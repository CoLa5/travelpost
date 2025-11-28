"""iCloud downloader."""

import argparse
import concurrent.futures
import datetime
import json
import logging
import os
import pathlib
import sys
import threading

import click
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudException
from pyicloud.services.photos import PhotoAlbum
from pyicloud.services.photos import PhotoAsset

logger = logging.getLogger(__name__)


class Checkpoint:
    def __init__(
        self,
        path: pathlib.Path | str,
        filename: str = "checkpoint.json",
    ) -> None:
        self._lock = threading.Lock()

        self._path = pathlib.Path(path)
        self._path.mkdir(exist_ok=True, parents=True)
        self._checkpoint = self._path / filename
        self._records = {}
        self._load()

    def _load(self):
        if self._checkpoint.exists():
            with self._lock, open(self._checkpoint, encoding="utf-8") as f:
                self._records.update(json.load(f))

    def add(self, version: str, photo_id: str, path: pathlib.Path) -> None:
        with self._lock:
            self._records.setdefault(version, {})[photo_id] = str(path)

    def get(self, version: str, photo_id: str) -> pathlib.Path | None:
        with self._lock:
            file_path = self._records.get(version, {}).get(photo_id)
        if file_path is None:
            return None
        return pathlib.Path(file_path)

    def save(self):
        if len(self._records) != 0:
            with (
                self._lock,
                open(self._checkpoint, mode="w", encoding="utf-8") as f,
            ):
                json.dump(self._records, f, indent=2)


class ProgressBar:
    WIDTH: int = 40
    _i = -1
    _clock = "|/-\\"

    @classmethod
    def print(cls, progress: float) -> None:
        if logger.level != logging.DEBUG:
            cls._i = (cls._i + 1) % len(cls._clock)
            filled = int(progress * cls.WIDTH)
            pbar = (
                "█" * filled
                + cls._clock[cls._i]
                + "-" * (cls.WIDTH - filled - 1)
            )
            percent = progress * 100

            sys.stdout.write(f"\r[{pbar:s}] {percent:.1f}%")
            sys.stdout.flush()

    @staticmethod
    def reset() -> None:
        sys.stdout.write("\r")
        sys.stdout.flush()


class ICloudDownloader:
    def __init__(
        self,
        email: str | None = None,
        password: str | None = None,
        max_workers: int | None = 4,
        path: pathlib.Path | str = "data/iCloud",
    ):
        self._max_workers = max_workers
        self._stop_event = threading.Event()

        self._api = None
        self._album_names = None
        self._verify_credentials(email, password)
        self._authenticate()

        self._path = pathlib.Path(path)
        self._path.mkdir(exist_ok=True, parents=True)
        self._checkpoint = Checkpoint(self._path)

    def _verify_credentials(
        self,
        email: str | None,
        password: str | None,
    ) -> tuple[str, str]:
        try:
            email = (
                email
                or os.environ.get("ICLOUD_EMAIL")
                or click.prompt(
                    "Please enter your iCloud e-mail",
                    type=str,
                )
            )
            password = (
                password
                or os.environ.get("ICLOUD_PASSWORD")
                or click.prompt(
                    "Please enter your iCloud password",
                    hide_input=True,
                    type=str,
                )
            )
        except click.exceptions.Abort:
            click.echo("\nAborted.")
            sys.exit(1)

        try:
            self._api = PyiCloudService(email, password)
        except PyiCloudException as e:
            click.echo(f"Error: {e.args[0]!s:s}")
            sys.exit(1)

    def _authenticate(self) -> None:
        if self._api.requires_2fa:
            click.echo("Two-factor authentication required ...")
            code = click.prompt(
                "Please enter the code you received on one of your approved "
                "devices",
                type=str,
            )
            result = self._api.validate_2fa_code(code)
            if not result:
                click.echo("Failed to verify security code.")
                sys.exit(1)

            if not self._api.is_trusted_session:
                click.echo("Session is not trusted, requesting trust ...")
                result = self._api.trust_session()
                if not result:
                    click.echo(
                        "Failed to request trust, you will likely be prompted "
                        "for the code again in the coming weeks."
                    )

        elif self._api.requires_2sa:
            click.echo(
                "Two-step authentication required. Your trusted devices are:"
            )

            devices = self._api.trusted_devices
            for i, device in enumerate(devices):
                phone_number = device.get("phoneNumber")
                device_name = device.get("deviceName")
                if device_name and phone_number:
                    label = f"{device_name:s} ({phone_number:s})"
                elif device_name:
                    label = device_name
                elif phone_number:
                    label = f"SMS to {phone_number:s}"
                else:
                    label = "unknown device"
                click.echo(f"  {i:d}: {label:s}")

            device = click.prompt(
                "Which device would you like to use?",
                default=0,
                type=int,
            )
            device = devices[device]
            if not self._api.send_verification_code(device):
                click.echo("Failed to send verification code.")
                sys.exit(1)

            code = click.prompt("Please enter validation code", type=str)
            if not self._api.validate_verification_code(device, code):
                click.echo("Failed to verify verification code")
                sys.exit(1)

        click.echo("Authentificated successfully.")

    def _download_photo(
        self,
        photo: PhotoAsset,
        version: str = "original",
    ) -> tuple[str, pathlib.Path]:
        created = photo.created.strftime("%Y-%m-%d")
        if created == "1970-01-01":
            created = "no-date"

        folder = self._path / created
        folder.mkdir(exist_ok=True)
        stem, ext = str(photo.versions[version]["filename"]).split(".")
        match version:
            case "original":
                pass
            case "original_video":
                stem += "_HEVC"
            case _:
                stem += f"_{version.upper():s}"
        filename = f"{stem:s}.{ext:s}"
        target = folder / filename

        with open(target, mode="wb") as f:
            f.write(photo.download(version=version))

        return photo.id, target

    @property
    def photo_album_names(self) -> set[str]:
        if self._album_names is None:
            self._album_names = {a.name for a in self._api.photos.albums}
        return self._album_names

    def _get_photo_album(self, album: str) -> PhotoAlbum:
        photo_album = (
            (self._api.photos.all if album == "all" else None)  # all
            or self._api.photos.albums.get(album)  # smart album
            or self._api.photos.albums.find(album)  # normal album
        )
        if photo_album is None:
            msg = (
                f"invalid album {album!r:s} "
                f"('{"', '".join(self.photo_album_names):s}' exist)"
            )
            raise ValueError(msg)
        return photo_album

    def get_asset_versions(self, album: str, index: int) -> set[str]:
        photo_album = self._get_photo_album(album)
        photo: PhotoAsset = photo_album.photo(index)
        return set(photo.versions.keys())

    def download_asset(
        self,
        album: str,
        index: int,
        version: str = "original",
    ) -> pathlib.Path:
        photo_album = self._get_photo_album(album)
        photo: PhotoAsset = photo_album.photo(index)
        photo_id, path = self._download_photo(photo, version=version)
        self._checkpoint.add(version, photo_id, path)
        return path

    def sync(
        self,
        album: str = "all",
        start_date: datetime.datetime | None = None,
        end_date: datetime.datetime | None = None,
    ) -> None:
        if start_date is not None:
            if start_date.tzinfo is None:
                msg = "missing timezone for 'start_date'"
                raise ValueError(msg)
            start_date = start_date.astimezone(datetime.UTC)

        if end_date is not None:
            if end_date.tzinfo is None:
                msg = "missing timezone for 'end_date'"
                raise ValueError(msg)
            end_date = end_date.astimezone(datetime.UTC)

        logger.info("Download photos and videos ...")
        photo_album = self._get_photo_album(album)
        total = len(photo_album)
        logger.info("%d photos/videos in photo album %r", total, album)

        def download_filtered(photo: PhotoAsset, progress: float) -> None:
            if self._stop_event.is_set():
                return

            # Live photo has versions "original" and "original_video",
            # edited photo has version "adjusted".
            for version in photo.versions:
                if (
                    version not in ("original", "original_video", "adjusted")
                    or (start_date is not None and photo.created <= start_date)
                    or (end_date is not None and end_date <= photo.created)
                ):
                    continue

                path = self._checkpoint.get(version, photo.id)
                downloaded = path.exists() if path else False
                if downloaded:
                    continue

                photo_id, path = self._download_photo(photo, version=version)
                self._checkpoint.add(version, photo_id, path)
            ProgressBar.print(progress)

        photo_iter = (
            iter(photo_album.photo(i) for i in range(total))
            if album == "all"
            else iter(photo_album)
        )

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._max_workers
        ) as pool:
            done: set[concurrent.futures.Future] = set()
            futures: set[concurrent.futures.Future] = set()

            try:
                for i, p in enumerate(photo_iter):
                    if self._stop_event.is_set():
                        break

                    while len(futures) >= pool._max_workers:  # pylint: disable=W0212
                        done, futures = concurrent.futures.wait(
                            futures,
                            return_when=concurrent.futures.FIRST_COMPLETED,
                        )

                    for d in done:
                        d.result()
                    futures.add(pool.submit(download_filtered, p, i / total))

                concurrent.futures.wait(futures)
            except Exception as e:
                logger.error("%s: %s", type(e).__name__, str(e))
                self._stop_event.set()
            except KeyboardInterrupt:
                self._stop_event.set()

            if self._stop_event.is_set():
                for f in futures:
                    f.cancel()
                concurrent.futures.wait(futures)
                msg = "Aborted"
            else:
                msg = f"Downloaded {total:d} photos and videos."

            self._checkpoint.save()
            ProgressBar.reset()
            logger.info(msg)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--email",
        type=str,
        required=False,
        help=("iCloud e-mail",),
    )
    parser.add_argument(
        "--password",
        type=str,
        required=False,
        help=("iCloud password",),
    )
    parser.add_argument(
        "--download-folder",
        type=str,
        required=False,
        help=("Download folder (defaults to './data/icloud')",),
    )
    parser.add_argument(
        "--album",
        type=str,
        required=False,
        help=("Photo album",),
    )
    parser.add_argument(
        "--from",
        dest="start_date",
        type=datetime.datetime.fromisoformat,
        required=False,
        help=(
            "From as start datetime with timezone (e.g. "
            "'2025-01-02T03:04:05+02:00')",
        ),
    )
    parser.add_argument(
        "--till",
        dest="end_date",
        type=datetime.datetime.fromisoformat,
        required=False,
        help=(
            "Till as end datetime with timezone (e.g. "
            "'2025-01-03T04:05:06+02:00')",
        ),
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(levelname)s:%(asctime)s:%(filename)s: %(message)s",
        level=getattr(logging, args.log_level.upper()),
    )

    ICloudDownloader(
        email=args.email,
        password=args.password,
        path=args.download_folder or "data/iCloud",
    ).sync(
        album=args.album or "all",
        start_date=args.start_date,
        end_date=args.end_date,
    )


if __name__ == "__main__":
    main()

"""iCloud downloader."""

import concurrent.futures
import datetime
import json
import os
import pathlib
import sys
import threading

import click
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudException
from pyicloud.services.photos import PhotoAlbum
from pyicloud.services.photos import PhotoAsset


class ICloudDownloader:
    def __init__(
        self,
        email: str | None = None,
        password: str | None = None,
        max_workers: int | None = 4,
        path: pathlib.Path | str = "data/iCloud",
    ):
        self._lock = threading.Lock()
        self._max_workers = max_workers
        self._stop_event = threading.Event()

        self._api = None
        self._retries = 0
        self._verify_credentials(email, password)
        self._authenticate()

        self._path = pathlib.Path(path)
        self._path.mkdir(exist_ok=True, parents=True)
        self._records = {}
        self._checkpoint = self._path / "checkpoint.json"
        self._load_checkpoint()

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

    def _load_checkpoint(self):
        if self._checkpoint.exists():
            with self._lock, open(self._checkpoint, encoding="utf-8") as f:
                self._records = json.load(f)

    def _save_checkpoint(self):
        with (
            self._lock,
            open(self._checkpoint, mode="w", encoding="utf-8") as f,
        ):
            json.dump(self._records, f, indent=2)

    @staticmethod
    def _progress_bar(progress: float, width: int = 40):
        filled = int(progress * width)
        pbar = "█" * filled + "-" * (width - filled)
        percent = progress * 100

        sys.stdout.write(f"\r[{pbar:s}] {percent:.1f}%")
        sys.stdout.flush()

    def _download_photo(
        self,
        photo: PhotoAsset,
        version: str = "original",
    ) -> tuple[str, str]:
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

        if target.exists():
            return None

        with open(target, mode="wb") as f:
            f.write(photo.download(version=version))

        return photo.id, str(target)

    def get_asset_versions(self, album: str, index: int) -> set[str]:
        album: PhotoAlbum = (
            self._api.photos.all
            if album == "all"
            else self._api.photos.albums[album]
        )
        photo: PhotoAsset = album.photo(index)
        return set(photo.versions.keys())

    def download_asset(
        self,
        album: str,
        index: int,
        version: str = "original",
    ) -> tuple[str, str]:
        album: PhotoAlbum = (
            self._api.photos.all
            if album == "all"
            else self._api.photos.albums[album]
        )
        photo: PhotoAsset = album.photo(index)
        if version not in photo.versions:
            msg = (
                f"invalid photo version {version!r:s} "
                f"(existing '{"', '".join(photo.versions.keys()):s}')"
            )
            raise ValueError(msg)
        return self._download_photo(photo, version=version)

    def sync(
        self,
        album: str | None = None,
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

        click.echo("Download photos and videos ...")
        album: PhotoAlbum = (
            self._api.photos.albums[album]
            if album is not None
            else self._api.photos.all
        )
        total = len(album)
        click.echo(f"{total:d} photos and videos in iCloud")

        def download_filtered(i: int) -> None:
            if self._stop_event.is_set():
                return

            photo: PhotoAsset = album.photo(i)

            # NOTE: Live photo has versions "original" and "original_video"
            #       Edited photo has version "adjusted"
            for version in photo.versions:
                if version not in ("original", "original_video", "adjusted"):
                    continue

                with self._lock:
                    file_path = self._records.get(version, {}).get(photo.id)
                downloaded = (
                    pathlib.Path(file_path).exists() if file_path else False
                )
                if (
                    not downloaded
                    and (start_date is None or start_date <= photo.created)
                    and (end_date is None or photo.created <= end_date)
                ):
                    photo_id, file_path = self._download_photo(
                        photo, version=version
                    )
                    with self._lock:
                        self._records.setdefault(version, {})[photo_id] = (
                            file_path
                        )

            self._progress_bar(i / total)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._max_workers
        ) as pool:
            futures: set[concurrent.futures.Future] = set()
            try:
                for i in range(total):
                    if self._stop_event.is_set():
                        break

                    while len(futures) >= pool._max_workers:  # pylint: disable=W0212
                        _, futures = concurrent.futures.wait(
                            futures,
                            return_when=concurrent.futures.FIRST_COMPLETED,
                        )

                    futures.add(pool.submit(download_filtered, i))

                concurrent.futures.wait(futures)
            except KeyboardInterrupt:
                self._stop_event.set()
                for f in futures:
                    f.cancel()
                concurrent.futures.wait(futures)
                self._save_checkpoint()

                click.echo(
                    f"\nAborted - downloaded {i + 1:d} of {total:d} photos and "
                    f"videos."
                )
            else:
                click.echo(f"\nDownloaded {total:d} photos and videos.")


if __name__ == "__main__":
    ICloudDownloader().sync()

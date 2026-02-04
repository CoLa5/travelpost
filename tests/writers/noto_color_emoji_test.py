"""Apple Color Emoji Test."""

import pathlib

import pytest

from travelpost.writers.pdf.libs import noto_color_emoji

TEST_EMOJI: int = 0x1F600


def test_EMOJI() -> None:
    assert len(noto_color_emoji.EMOJI) >= 2
    for i in range(4):
        assert chr(TEST_EMOJI + i) in noto_color_emoji.EMOJI
        assert isinstance(
            noto_color_emoji.EMOJI[chr(TEST_EMOJI + i)], pathlib.Path
        )


@pytest.mark.parametrize(
    "em_code",
    [chr(TEST_EMOJI + i) for i in range(4)],
)
def test_emoji_svg_path(em_code: str) -> None:
    p = noto_color_emoji.emoji_svg_path(em_code)
    assert isinstance(p, pathlib.Path)
    assert p == p.resolve()
    assert p.is_file()
    assert p.exists()


@pytest.mark.parametrize(
    "em_code",
    ["🇩🇪", "🇪🇸"],
)
def test_emoji_svg_flag_path(em_code: str) -> None:
    p = noto_color_emoji.emoji_svg_path(em_code)
    assert isinstance(p, pathlib.Path)
    assert p == p.resolve()
    assert p.is_file()
    assert p.exists()


@pytest.mark.parametrize(
    "em_code",
    ["xy"],
)
def test_emoji_svg_path_error(em_code: str) -> None:
    with pytest.raises(KeyError) as excinfo:
        noto_color_emoji.emoji_svg_path(em_code)
    assert f"{em_code!r:s}" in str(excinfo.value)


@pytest.mark.parametrize(
    ["text", "em_codes", "font_size"],
    [
        (
            "text example "
            + " ".join(chr(TEST_EMOJI + i) for i in range(4))
            + " end",
            [chr(TEST_EMOJI + i) for i in range(4)],
            12,
        )
    ],
)
def test_replace_emoji(text: str, em_codes: list[str], font_size: int) -> None:
    new_text = noto_color_emoji.replace_emoji(text, font_size=font_size)
    for em_code in em_codes:
        p = noto_color_emoji.emoji_svg_path(em_code)
        assert em_code not in new_text
        assert (
            f'<svg height="{font_size!s:s}" src="{p!s:s}" '
            f'valign="text-bottom" />'
        ) in new_text

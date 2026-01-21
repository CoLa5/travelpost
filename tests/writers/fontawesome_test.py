"""Font Awesome Icon Test."""

import pathlib
import string

import pytest

from tests.writers import DATA_PATH
import travelpost.writers.pdf.libs.fontawesome as fa


@pytest.fixture(scope="module", autouse=True)
def setup_fa_icons() -> int:
    try:
        # Local setup
        fa.setup_icons()
    except ValueError:
        # Remote setup
        fa.setup_icons(fa_path=DATA_PATH / "fontawesome")
    assert len(fa.FA_ICONS) > 0
    return len(fa.FA_ICONS)


def test_FA_ICONS() -> None:
    assert len(fa.FA_ICONS) > 5


def test_FA_STYLES() -> None:
    assert len(fa.FA_STYLES) == 3
    assert fa.FA_STYLES == ("brands", "regular", "solid")


@pytest.mark.parametrize(
    ["label", "style"],
    [
        ("house", "solid"),
        ("bell", "regular"),
        ("python", "brands"),
    ],
)
def test_fa_icon(label: str, style: str) -> None:
    icon = fa.fa_icon(label)
    assert isinstance(icon, fa.FAIcon)

    assert icon.label == string.capwords(label.replace("-", " "))
    assert isinstance(icon.aliases, dict)
    assert isinstance(icon.changes, tuple)
    assert all(isinstance(c, str) for c in icon.changes)

    assert isinstance(icon.ligatures, tuple)
    assert isinstance(icon.search, dict)

    assert isinstance(icon.styles, tuple)
    assert style in icon.styles

    assert isinstance(icon.unicode, str)

    assert isinstance(icon.voted, bool)

    assert isinstance(icon.svg, dict)
    assert len(icon.svg) == 0

    assert isinstance(icon.svg_paths, dict)
    assert style in icon.svg_paths
    assert isinstance(icon.svg_paths[style], pathlib.Path)
    assert icon.svg_paths[style] == icon.svg_paths[style].resolve()
    assert icon.svg_paths[style].is_file()
    assert icon.svg_paths[style].exists()

    assert isinstance(icon.free, tuple)
    assert style in icon.free


@pytest.mark.parametrize("label", ["headphones"])
def test_fa_icon_alias(label: str) -> None:
    icon = fa.fa_icon(label)

    assert isinstance(icon, fa.FAIcon)
    assert icon.label == string.capwords(label.replace("-", " "))

    assert isinstance(icon.aliases, dict)
    assert "names" in icon.aliases

    aliases = icon.aliases["names"]
    assert len(aliases) > 0

    for alias in aliases:
        al_icon = fa.fa_icon(alias)
        assert al_icon.label == alias.replace("-", " ").title()

        assert isinstance(al_icon.aliases, dict)
        assert "names" in al_icon.aliases
        assert label in al_icon.aliases["names"]
        assert alias not in al_icon.aliases["names"]

        assert al_icon.changes == icon.changes
        assert al_icon.ligatures == icon.ligatures
        assert al_icon.search == icon.search
        assert al_icon.styles == icon.styles
        assert al_icon.unicode == icon.unicode
        assert al_icon.voted == icon.voted
        assert al_icon.svg == icon.svg

        assert isinstance(al_icon.svg_paths, dict)
        for style in al_icon.styles:
            assert style in al_icon.svg_paths
            assert isinstance(al_icon.svg_paths[style], pathlib.Path)
            assert (
                al_icon.svg_paths[style] == al_icon.svg_paths[style].resolve()
            )
            assert al_icon.svg_paths[style].is_file()
            assert al_icon.svg_paths[style].exists()
            assert al_icon.svg_paths[style] != icon.svg_paths[style]

        assert al_icon.free == icon.free


def test_fa_icon_all(subtests: pytest.Subtests, setup_fa_icons: int) -> None:
    assert setup_fa_icons > 0
    assert len(fa.FA_ICONS) == setup_fa_icons

    for i in range(setup_fa_icons):
        label = fa.FA_ICONS[i]
        with subtests.test("FA icon", label=label, i=i):
            icon = fa.fa_icon(label)
            assert isinstance(icon, fa.FAIcon)

            assert icon.label == string.capwords(label.replace("-", " "))
            assert isinstance(icon.aliases, dict)
            assert isinstance(icon.changes, tuple)
            assert all(isinstance(c, str) for c in icon.changes)

            assert isinstance(icon.ligatures, tuple)
            assert isinstance(icon.search, dict)

            assert isinstance(icon.styles, tuple)
            assert len(icon.styles) > 0
            for style in icon.styles:
                assert style in fa.FA_STYLES

            assert isinstance(icon.unicode, str)

            assert isinstance(icon.voted, bool)

            assert isinstance(icon.svg, dict)
            assert len(icon.svg) == 0

            assert isinstance(icon.svg_paths, dict)
            assert len(icon.svg_paths) > 0
            for style in icon.svg_paths:
                assert style in icon.styles
                assert style in fa.FA_STYLES
                assert isinstance(icon.svg_paths[style], pathlib.Path)
                assert icon.svg_paths[style] == icon.svg_paths[style].resolve()
                assert icon.svg_paths[style].is_file()
                assert icon.svg_paths[style].exists()

            assert isinstance(icon.free, tuple)
            assert len(icon.free) > 0

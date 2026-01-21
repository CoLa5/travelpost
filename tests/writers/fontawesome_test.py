"""Font Awesome Icon Test."""

import pathlib
import string

import pytest

from travelpost.writers.pdf.libs.fontawesome import FAIcon
from travelpost.writers.pdf.libs.fontawesome import FA_ICONS
from travelpost.writers.pdf.libs.fontawesome import fa_icon


@pytest.mark.parametrize(
    ["label", "style"],
    [
        ("house", "solid"),
        ("bell", "regular"),
        ("python", "brands"),
    ],
)
def test_fa_icon(label: str, style: str) -> None:
    icon = fa_icon(label)
    assert isinstance(icon, FAIcon)

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
    icon = fa_icon(label)

    assert isinstance(icon, FAIcon)
    assert icon.label == string.capwords(label.replace("-", " "))

    assert isinstance(icon.aliases, dict)
    assert "names" in icon.aliases

    aliases = icon.aliases["names"]
    assert len(aliases) > 0

    for alias in aliases:
        al_icon = fa_icon(alias)
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


@pytest.mark.parametrize(
    "label",
    FA_ICONS,
)
def test_fa_icon_all(label: str) -> None:
    icon = fa_icon(label)
    assert isinstance(icon, FAIcon)

    assert icon.label == string.capwords(label.replace("-", " "))
    assert isinstance(icon.aliases, dict)
    assert isinstance(icon.changes, tuple)
    assert all(isinstance(c, str) for c in icon.changes)

    assert isinstance(icon.ligatures, tuple)
    assert isinstance(icon.search, dict)

    assert isinstance(icon.styles, tuple)
    assert len(icon.styles) > 0

    assert isinstance(icon.unicode, str)

    assert isinstance(icon.voted, bool)

    assert isinstance(icon.svg, dict)
    assert len(icon.svg) == 0

    assert isinstance(icon.svg_paths, dict)
    assert len(icon.svg_paths) > 0
    for style in icon.svg_paths:
        assert isinstance(icon.svg_paths[style], pathlib.Path)
        assert icon.svg_paths[style] == icon.svg_paths[style].resolve()
        assert icon.svg_paths[style].is_file()
        assert icon.svg_paths[style].exists()

    assert isinstance(icon.free, tuple)
    assert len(icon.free) > 0

"""Folium Patch."""

import pathlib

import folium

_DIR: pathlib.Path = pathlib.Path(__file__).parent


def patch(map: type[folium.Map]) -> type[folium.Map]:
    for file in (_DIR / "css").glob("*.css"):
        map.default_css.append((file.stem, file.as_uri()))
    for file in (_DIR / "js").glob("*.js"):
        map.default_js.append((file.stem, file.as_uri()))
    return map

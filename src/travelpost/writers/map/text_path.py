"""Text Path."""

from collections.abc import Sequence
from typing import Any

import folium
from folium.template import Template
from folium.utilities import parse_options


class TextPath(folium.PolyLine):
    """Text Path (Polyline with text)."""

    _template = Template(
        """
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.polyline(
                {{ this.locations|tojson }},
                {{ this.options|tojson }}
            ).addTo({{this._parent.get_name()}});
        {% endmacro %}
        """
    )

    def __init__(
        self,
        locations: Sequence[tuple[float, float]],
        text: str,
        popup: str | folium.Popup | None = None,
        tooltip: str | folium.Tooltip | None = None,
        **kwargs: Any,
    ) -> None:
        text_options = {k: v for k, v in kwargs.items() if k.startswith("text")}
        if "color" not in kwargs:
            kwargs["color"] = "#fff"

        super().__init__(locations, popup=popup, tooltip=tooltip, **kwargs)

        self.options["text"] = text
        if "text_anchor" in text_options:
            self.options["textAnchor"] = text_options.pop("text_anchor")
        if "text_outline_stroke" in text_options:
            self.options["outlineStroke"] = text_options.pop(
                "text_outline_stroke"
            )
        if "text_start_offset" in text_options:
            self.options["textStartOffset"] = text_options.pop(
                "text_start_offset"
            )
        if text_options:
            self.options["textStyle"] = parse_options(**text_options)

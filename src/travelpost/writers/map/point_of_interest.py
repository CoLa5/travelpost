"""Point of Interest."""

from typing import Any

import folium
from folium.template import Template
from folium.utilities import parse_options
from folium.utilities import validate_location


class PointOfInterestMarker(folium.MacroElement):
    """Point of Interest Marker.
    (Marker with FontAwesome-Icon & permanent header/trailer-tooltip).
    """

    _template = Template(
        """
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.Travel.pointOfInterest(
                {{ this.location|tojson }},
                {{ this.symbol|tojson }},
                {{ this.text.replace('\n', '<br>')|tojson }},
                {{ this.options|tojson }}
            ).addTo({{this._parent.get_name()}});
        {% endmacro %}
        """
    )

    def __init__(
        self,
        location: tuple[float, float],
        symbol: str,
        text: str | None = None,
        icon_options: dict[str, Any] | None = None,
        text_options: dict[str, Any] | None = None,
        outline_stroke: str | None = None,
    ) -> None:
        super().__init__()
        self._name = "PointOfInterest"
        self.location = validate_location(location)
        self.symbol = symbol
        self.text = text or ""

        self.options = {
            "iconOptions": parse_options(**(icon_options or {})),
            "textOptions": parse_options(**(text_options or {})),
        }
        if outline_stroke is not None:
            self.options["outlineStroke"] = str(outline_stroke)

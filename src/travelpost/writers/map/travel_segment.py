"""Travel Segment."""

from collections.abc import Sequence
from typing import Any

import folium
from folium.template import Template
from folium.utilities import camelize


class TravelSegment(folium.PolyLine):
    """Travel Segment (Polyline with transport icon)."""

    _template = Template(
        """
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.Travel.segment(
                {{ this.locations|tojson }},
                "{{ this.transport|lower }}",
                {{ this.options|tojson }}
            ).addTo({{this._parent.get_name()}});
        {% endmacro %}
        """
    )

    def __init__(
        self,
        locations: Sequence[tuple[float, float]],
        transport: str,
        popup: str | folium.Popup | None = None,
        tooltip: str | folium.Tooltip | None = None,
        **kwargs: Any,
    ) -> None:
        icon_options = kwargs.pop("icon_options", {})
        super().__init__(locations, popup=popup, tooltip=tooltip, **kwargs)
        self._name = "TravelSegment"
        self.options["iconOptions"] = {
            camelize(key): value for key, value in icon_options.items()
        }
        self.options["transportMarkerZIndexOffset"] = kwargs.pop(
            "transport_marker_z_index_offset", 0
        )
        self.transport = transport

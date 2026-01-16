"""Tile Loading Control."""

import folium
from folium.template import Template
from folium.utilities import remove_empty


class TileLoadingControl(folium.MacroElement):
    """Tile Loading Control (fires 'TILES LOADED')."""

    _template = Template(
        """
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.Travel.tileLoadingControl(
                {{ this.options|tojson }}
            ).addTo({{this._parent.get_name()}});
        {% endmacro %}
        """
    )

    def __init__(
        self,
        position: str | None = None,
    ) -> None:
        super().__init__()
        self._name = "TileLoadingControl"
        self.options = remove_empty(position=position)

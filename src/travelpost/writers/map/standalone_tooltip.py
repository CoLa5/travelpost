"""Standalone Tooltip."""

from collections.abc import Sequence

import folium
from folium.template import Template
from folium.utilities import TypeJsonValue
from folium.utilities import remove_empty
from folium.utilities import validate_location


class StandaloneTooltip(folium.MacroElement):
    """
    Create a standaone tooltip that shows text.

    Parameters
    ----------
    text: str
        String to display as a tooltip on the object. If the argument is of a
        different type it will be converted to str.
    style: str, default None.
        HTML inline style properties like font and colors. Will be applied to
        a div with the text in it.
    sticky: bool, default True
        Whether the tooltip should follow the mouse.
    **kwargs
        These values will map directly to the Leaflet Options. More info
        available here: https://leafletjs.com/reference.html#tooltip

    """

    _template = Template(
        """
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.tooltip(
                {{ this.location|tojson }},
                {{ this.options|tojavascript }}
            ).addTo({{ this._parent.get_name() }});
        {% endmacro %}
        """
    )

    def __init__(
        self,
        location: Sequence[float],
        text: str,
        **kwargs: TypeJsonValue,
    ):
        super().__init__()
        self._name = "Tooltip"
        self.location = validate_location(location)
        kwargs.update({"content": str(text)})
        self.options = remove_empty(**kwargs)

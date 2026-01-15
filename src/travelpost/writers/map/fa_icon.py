"""Font Awesome Icon."""

import folium
from folium.template import Template
from folium.utilities import remove_empty


class FAIcon(folium.MacroElement):
    """Font Awesome Icon."""

    _template = Template(
        """
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.Travel.faIcon({{ this.options|tojavascript }});
        {% endmacro %}
        """  # noqa: E501
    )

    def __init__(
        self,
        icon: str,
        icon_class_name: str | None = None,
        icon_shape: str = "circle",
        icon_size: int = 32,
        icon_style: str = "solid",
        background_color: str = "#3388ff",
        border_color: str = "white",
        border_width: int = 2,
        border_style: str = "solid",
        class_name: str | None = None,
        color: str = "white",
        font_size: int = 18,
    ) -> None:
        super().__init__()
        self._name = "FAIcon"
        self.options = remove_empty(
            icon=icon,
            icon_class_name=icon_class_name,
            icon_shape=icon_shape,
            icon_size=icon_size,
            icon_style=icon_style,
            background_color=background_color,
            border_color=border_color,
            border_width=border_width,
            border_style=border_style,
            class_name=class_name,
            color=color,
            font_size=font_size,
        )

"""Post Icon."""

import folium
from folium.template import Template
from folium.utilities import remove_empty


class PostIcon(folium.MacroElement):
    """Post Icon."""

    _template = Template(
        """
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.Travel.postIcon({{ this.options|tojavascript }});
        {% endmacro %}
        """  # noqa: E501
    )

    def __init__(
        self,
        img_url: str | None,
        icon_shape: str = "circle",
        icon_size: int = 32,
        empty_size: int = 16,
        background_color: str = "#3388ff",
        border_color: str = "white",
        border_width: int = 2,
        border_style: str = "solid",
        class_name: str | None = None,
    ) -> None:
        super().__init__()
        self._name = "PostIcon"
        self.options = remove_empty(
            img_url=img_url,
            icon_shape=icon_shape,
            icon_size=icon_size,
            empty_size=empty_size,
            background_color=background_color,
            border_color=border_color,
            border_width=border_width,
            border_style=border_style,
            class_name=class_name,
        )

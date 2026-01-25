"""SVG Point Adder."""

import pathlib

import lxml.etree

from travelpost.writers.pdf.libs.country_shapes.interface import Projection
from travelpost.writers.pdf.libs.country_shapes.interface import ViewBox
from travelpost.writers.pdf.libs.country_shapes.type_defs import Coo


class SVGEditor:
    """Adds a point on top of a country shape-SVG."""

    def __init__(self, svg_path: str | pathlib.Path) -> None:
        self._svg_path = pathlib.Path(svg_path)
        self._tree = lxml.etree.parse(self._svg_path)
        self._root = self._tree.getroot()
        self._nsmap = self._root.nsmap
        self._g = self._get_first_group()
        self._viewbox = self._get_viewbox()
        self._proj = self._get_projection()
        self._width, self._height = self._get_width_height()

    def _get_first_group(self) -> lxml.etree.Element:
        ns = {"svg": self._nsmap.get(None)} if None in self._nsmap else {}
        xpath_expr = ".//svg:g" if ns else ".//g"
        elem = self._root.xpath(xpath_expr, namespaces=ns if ns else None)
        if elem:
            return elem[0]
        msg = "No <g>...</g> found."
        raise RuntimeError(msg)

    def _get_projection(self) -> Projection:
        elem = self._root.xpath("./@desc")
        if not elem:
            msg = "no <svg desc='...'> found."
            raise RuntimeError(msg)
        return Projection.from_str(elem[0])

    def _get_width_height(self) -> tuple[float, float]:
        elem = self._root.xpath("./@width")
        if not elem:
            msg = "no <svg width='...'> found."
            raise RuntimeError(msg)
        width = float(elem[0])

        elem = self._root.xpath("./@height")
        if not elem:
            msg = "no <svg height='...'> found."
            raise RuntimeError(msg)
        height = float(elem[0])
        return width, height

    def _get_viewbox(self) -> ViewBox:
        elem = self._root.xpath("./@viewBox")
        if not elem:
            msg = "no <svg viewBox='...'> found."
            raise RuntimeError(msg)
        values = tuple(float(x) for x in elem[0].strip().split())
        if len(values) != 4:
            msg = f"invalid viewbox format: {elem[0]!r:s}"
            raise ValueError(msg)
        return ViewBox(
            **dict(
                zip(("min_x", "min_y", "width", "height"), values, strict=True)
            )
        )

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    @property
    def padding(self) -> float:
        return self._proj.pad

    @property
    def projection(self) -> Projection:
        return self._proj

    @property
    def viewbox(self) -> ViewBox:
        return self._viewbox

    @property
    def inner_viewbox(self) -> ViewBox:
        return ViewBox(
            min_x=self.viewbox.min_x + self.projection.pad,
            min_y=self.viewbox.min_y + self.projection.pad,
            width=self.viewbox.width - 2 * self.projection.pad,
            height=self.viewbox.height - 2 * self.projection.pad,
        )

    def change_style(
        self,
        fill_color: str | None = None,
        opacity: float | None = None,
        stroke_color: str | None = None,
        stroke_width: float | None = None,
    ) -> None:
        if fill_color is not None:
            self._g.attrib["fill"] = fill_color
        if opacity is not None:
            self._g.attrib["opacity"] = f"{opacity:.2f}"
        if stroke_color is not None:
            self._g.attrib["stroke"] = stroke_color
        if stroke_width is not None:
            self._g.attrib["stroke-width"] = f"{stroke_width:f}"

    def _svg_coordinates(self, lon_lat: Coo) -> Coo:
        xy = self.projection.project_lonlat(lon_lat)
        if not self.inner_viewbox.contains(xy):
            msg = "point is outside of inner viewbox of country shape"
            raise ValueError(msg)
        return xy

    def add_point(
        self,
        lon_lat: Coo,
        decimals: int = 3,
        radius: int = 16,
        fill_color: str = "#FF0000",
        opacity_steps: tuple[float] = [0.5, 0.5, 1.0],
    ) -> None:
        cx, cy = self._svg_coordinates(lon_lat)

        vb_scale_x = self._viewbox.width / self._width
        vb_scale_y = self._viewbox.height / self._height
        scale = max(vb_scale_x, vb_scale_y)

        inner_radius = radius / 2
        for i, opacity in enumerate(opacity_steps):
            r = radius - (radius - inner_radius) / (len(opacity_steps) - 1) * i
            rs = r * scale
            circle = lxml.etree.Element(
                "circle",
                {
                    "cx": f"{cx:.{decimals:d}f}",
                    "cy": f"{cy:.{decimals:d}f}",
                    "r": f"{rs:.{decimals:d}f}",
                    "fill": fill_color,
                    "fill-opacity": str(opacity).rstrip("0").rstrip("."),
                },
            )
            self._g.append(circle)

    def export(self, out: str | pathlib.Path) -> None:
        svg_str = self.to_svg()
        with open(out, mode="w", encoding="utf-8") as f:
            f.write(svg_str)

    def to_svg(self) -> str:
        return lxml.etree.tostring(self._root, encoding="unicode")


if __name__ == "__main__":
    ed = SVGEditor("de.svg")
    ed.change_style(fill_color="#808080", stroke_color="#DAA520")
    ed.add_point((8.417682623270723, 55.05805669734443), fill_color="#DAA520")
    with open("de_p.svg", mode="w", encoding="utf-8") as f:
        f.write(ed.to_svg())

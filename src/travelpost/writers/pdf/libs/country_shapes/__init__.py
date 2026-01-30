"""Country Shapes."""

from travelpost.writers.pdf.libs.country_shapes.interface import CountryShape
from travelpost.writers.pdf.libs.country_shapes.interface import Projection
from travelpost.writers.pdf.libs.country_shapes.interface import ViewBox
from travelpost.writers.pdf.libs.country_shapes.svg_editor import SVGEditor
from travelpost.writers.pdf.libs.country_shapes.svg_getter import COUNTRY_CODES
from travelpost.writers.pdf.libs.country_shapes.svg_getter import (
    setup_country_shapes,
)
from travelpost.writers.pdf.libs.country_shapes.svg_getter import shape_by_code
from travelpost.writers.pdf.libs.country_shapes.svg_getter import shape_by_name

__all__ = (
    "COUNTRY_CODES",
    "CountryShape",
    "Projection",
    "SVGEditor",
    "ViewBox",
    "setup_country_shapes",
    "shape_by_code",
    "shape_by_name",
)

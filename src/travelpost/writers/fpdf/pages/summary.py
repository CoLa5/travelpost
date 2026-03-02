"""Summary."""

from collections.abc import Iterator, Sequence
import contextlib
import pathlib
from typing import TYPE_CHECKING

import fpdf
from fpdf.image_parsing import preload_image
import fpdf.svg

from travelpost.writers.fpdf.env import SHOW_BOUNDARY
from travelpost.writers.fpdf.lib import DeviceColor
from travelpost.writers.fpdf.lib import Style
from travelpost.writers.fpdf.lib import Stylesheet
from travelpost.writers.fpdf.lib import font_awesome as fa
from travelpost.writers.fpdf.lib import use_style
from travelpost.writers.fpdf.lib.drawing import convert_style_attrib
from travelpost.writers.fpdf.lib.str_utils import alt_to_str
from travelpost.writers.fpdf.lib.str_utils import flag_unicode
from travelpost.writers.fpdf.lib.str_utils import travel_period_str
from travelpost.writers.fpdf.pages.abc import PageABC
from travelpost.writers.fpdf.styles import rem
from travelpost.writers.fpdf.styles import styles as glob_styles


class Summary(PageABC):
    """Summary."""

    peak_diagram_path: pathlib.Path = (
        pathlib.Path(__file__).parent.resolve() / "src" / "peak_diagram.svg"
    )
    peak_offset: float = 60
    peak_positions: tuple[tuple[int, int, int], ...] = (
        (1030, 30 - 28, -1),
        (1438, 119 - 28, +1),
        (442, 380 - 28, -1),
    )  # x, y, dir
    styles: Stylesheet = Stylesheet(
        glob_styles["h1"],
        Style(
            "summary_h2",
            parent=glob_styles["h2"],
            align=fpdf.Align.C,
            color="goldenrod",
        ),
        Style(
            "summary_dates",
            parent=glob_styles["body"],
            align=fpdf.Align.C,
        ),
        Style(
            "summary_desc",
            parent=glob_styles["body"],
            align=fpdf.Align.C,
        ),
        Style(
            "summary_flags",
            parent=glob_styles["default"],
            font_family="twitter-emoji",
            font_size_pt=24,
            align=fpdf.Align.C,
        ),
        Style(
            name="summary_stats_icon",
            parent=glob_styles["default"],
            font_family=fa.font_family,
            font_style=fa.font_styles["solid"],
            align=fpdf.Align.C,
            border_radius=0.999 * rem,
            color="white",
            fill_color="primary",
            padding=0.5 * rem,
        ),
        Style(
            name="summary_stats_main",
            parent=glob_styles["default"],
            font_size_pt=1.5 * rem,
            leading=1.2,
            align=fpdf.Align.C,
            padding=(0.25 * rem, 0),
        ),
        Style(
            name="summary_stats_footer",
            parent=glob_styles["default"],
            font_style="B",
            align=fpdf.Align.C,
            color="primary",
            padding=(0, 0.25 * rem, 0.5 * rem),
            text_transform="uppercase",
        ),
        Style(
            name="summary_peak_diagram",
            parent=glob_styles["default"],
            align=fpdf.Align.C,
            # Drawing
            stroke_cap_style=fpdf.enums.StrokeCapStyle.ROUND,
            stroke_color="black",
            stroke_join_style=fpdf.enums.StrokeJoinStyle.ROUND,
            stroke_width=1.0,
        ),
        Style(
            name="summary_peak_name",
            parent=glob_styles["body"],
            align=fpdf.Align.C,
            margin=(0, 0.667 * rem),
            padding=(0, 0.667 * rem),
        ),
        Style(
            name="summary_peak_altitude",
            parent=glob_styles["body"],
            align=fpdf.Align.C,
            margin=(0, 0.667 * rem),
            padding=(0, 0.667 * rem),
        ),
        Style(
            name="summary_peak_icon",
            parent=glob_styles["default"],
            font_family=fa.font_family,
            font_style=fa.font_styles["solid"],
            align=fpdf.Align.C,
            border_radius=0.999 * rem,
            color="white",
            fill_color="primary",
            padding=0.5 * rem,
            text_transform="uppercase",
        ),
    )

    def __init__(
        self,
        pdf: fpdf.FPDF,
        country_codes: Sequence[str] | None = None,
        description: str | None = None,
        peaks: dict[str, float] | None = None,
        photo_count: int | None = None,
        post_count: int | None = None,
        total_distance: float | None = None,
    ) -> None:
        super().__init__(pdf, "Summary")
        self.country_codes = country_codes or []
        self.description = description
        self.peaks = peaks
        if self.peaks is not None:
            self.peaks = dict(
                sorted(
                    self.peaks.items(), key=lambda item: item[1], reverse=True
                )
            )
        self.photo_count = photo_count
        self.post_count = post_count
        self.total_distance = total_distance

    def render(self) -> None:
        self.add_to_outline()
        self.render_title()
        self.render_description()
        self.render_dates()
        self.render_flags()
        self.render_stats()
        self.render_peaks()

    def render_title(self) -> None:
        if self.title is None:
            return

        with use_style(self.pdf, self.styles["h1"]) as pdf:
            pdf.cell(self.title, border=SHOW_BOUNDARY, new_y=fpdf.YPos.NEXT)

    def render_dates(self) -> None:
        if hasattr(self.pdf, "start_date") and hasattr(self.pdf, "end_date"):
            text = travel_period_str(
                self.pdf.start_date,
                self.pdf.end_date,
                show_day=True,
                short_year=True,
            )
            title = "Dates"

            with use_style(self.pdf, self.styles["summary_h2"]) as pdf:
                pdf.cell(title, border=SHOW_BOUNDARY, new_y=fpdf.YPos.NEXT)
            with use_style(self.pdf, self.styles["summary_dates"]) as pdf:
                pdf.cell(text, border=SHOW_BOUNDARY, new_y=fpdf.YPos.NEXT)

    def render_description(self) -> None:
        if self.description is None:
            return

        text = self.description
        title = "Description"

        with use_style(self.pdf, self.styles["summary_h2"]) as pdf:
            pdf.cell(title, border=SHOW_BOUNDARY, new_y=fpdf.YPos.NEXT)
        with use_style(self.pdf, self.styles["summary_desc"]) as pdf:
            pdf.multi_cell(
                text,
                border=SHOW_BOUNDARY,
                new_y=fpdf.YPos.NEXT,
                w=self.pdf.epw * 2 / 3,
            )

    def render_flags(self) -> None:
        if not self.country_codes:
            return

        text = " ".join(flag_unicode(c) for c in self.country_codes)
        title = "Collected Flags"

        with use_style(self.pdf, self.styles["summary_h2"]) as pdf:
            pdf.cell(title, border=SHOW_BOUNDARY, new_y=fpdf.YPos.NEXT)
        with use_style(self.pdf, self.styles["summary_flags"]) as pdf:
            pdf.cell(text, border=SHOW_BOUNDARY, new_y=fpdf.YPos.NEXT)

    def render_peaks(self) -> None:
        if not self.peaks:
            return

        # Title
        title = "Highest Peaks"
        with use_style(self.pdf, self.styles["summary_h2"]) as pdf:
            pdf.cell(title, border=SHOW_BOUNDARY, new_y=fpdf.YPos.NEXT)

        scale = self._render_peak_diagram()
        self._render_peak_labels(scale)

    def _render_peak_diagram(self) -> float:
        self.pdf.y += self.styles["summary_peak_name"].line_height
        h = self.pdf.h - self.pdf.y - self.pdf.b_margin
        w = self.pdf.epw
        svg_name = self.peak_diagram_path.resolve().as_posix()
        svg_name, svg, info = preload_image(self.pdf.image_cache, svg_name)
        if TYPE_CHECKING:
            svg: fpdf.svg.SVGObject

        svg_w, svg_h = info.width, info.height
        scale = min(w / svg_w, h / svg_h)
        svg_w *= scale
        svg_h *= scale

        convert_style_attrib(
            svg.base_group,
            stroke_width=self.styles["summary_peak_diagram"].stroke_width
            / scale,
        )

        self.pdf.set_x_by_align(
            self.styles["summary_peak_diagram"].align, svg_w
        )
        self.pdf._vector_image(
            svg_name,
            svg,
            info,
            x=self.pdf.x,
            y=self.pdf.y,
            w=svg_w,
            h=svg_h,
        )
        return scale

    def _render_peak_labels(self, scale: float) -> None:
        peaks = []
        style = self.styles["summary_peak_name"]
        with self.pdf.use_font_face(style.font_face):
            for name, alt in self.peaks.items():
                name = style.text_transform.transform(name)
                alt_text = alt_to_str(alt, decimals=0)
                w_text = max(
                    self.pdf.get_cell_width(s) for s in (name, alt_text)
                )
                peaks.append((name, alt_text, w_text))

        x = self.pdf.x
        y = self.pdf.y
        n_peaks = len(self.peaks)
        for i, (x_peak, y_peak, dir_), (name, alt_text, w_text) in zip(
            range(1, n_peaks + 1),
            self.peak_positions[:n_peaks],
            peaks,
            strict=True,
        ):
            x_peak = x + scale * x_peak
            y_peak = y + scale * y_peak
            style = self.styles["summary_peak_name"]
            w_line = style.padding.left + w_text + style.padding.right
            dx_icon = style.margin.left + w_line + style.margin.right

            if dir_ == -1:
                style = self.styles["summary_peak_icon"]
                with use_style(self.pdf, style) as pdf:
                    # NOTE: Some icons are wider than high.
                    #       Fix font_size so that max width = font size
                    icon_str = fa.get_icon(str(i), "solid")
                    icon_w = self.pdf.get_cell_width(icon_str)
                    font_size_pt = self.pdf.font_size_pt
                    if icon_w > font_size_pt:
                        self.pdf.set_font_size(font_size_pt**2 / icon_w)
                    icon_w = font_size_pt
                    self.pdf.set_xy(
                        x_peak
                        - dx_icon
                        - style.padding.left
                        - icon_w
                        - style.padding.right,
                        y_peak - icon_w / 2 - style.padding.top,
                    )
                    pdf.cell(
                        icon_str,
                        border=SHOW_BOUNDARY,
                        center=False,
                        w=icon_w,
                    )

                style = self.styles["summary_peak_diagram"]
                stroke_width = style.stroke_width
                with self.pdf.local_context(
                    draw_color=style.stroke_color,
                    line_width=stroke_width,
                    stroke_cap_style=style.stroke_cap_style,
                    stroke_join_style=style.stroke_join_style,
                    stroke_opacity=style.stroke_color.a
                    if isinstance(style.stroke_color, DeviceColor.__value__)
                    else None,
                ):
                    style = self.styles["summary_peak_name"]
                    self.pdf.line(
                        x_peak - style.margin.right - w_line,
                        y_peak,
                        x_peak - style.margin.right,
                        y_peak,
                    )

                style = self.styles["summary_peak_name"]
                with use_style(self.pdf, style) as pdf:
                    self.pdf.set_xy(
                        x_peak - style.margin.right - w_line,
                        y_peak - style.line_height,
                    )
                    pdf.cell(
                        name,
                        border=SHOW_BOUNDARY,
                        center=False,
                        w=w_text,
                    )

                style = self.styles["summary_peak_altitude"]
                with use_style(self.pdf, style) as pdf:
                    self.pdf.set_xy(
                        x_peak - style.margin.right - w_line, y_peak
                    )
                    pdf.cell(
                        alt_text,
                        border=SHOW_BOUNDARY,
                        center=False,
                        w=w_text,
                    )
            else:
                style = self.styles["summary_peak_diagram"]
                stroke_width = style.stroke_width
                with self.pdf.local_context(
                    draw_color=style.stroke_color,
                    line_width=stroke_width,
                    stroke_cap_style=style.stroke_cap_style,
                    stroke_join_style=style.stroke_join_style,
                    stroke_opacity=style.stroke_color.a
                    if isinstance(style.stroke_color, DeviceColor.__value__)
                    else None,
                ):
                    style = self.styles["summary_peak_name"]
                    self.pdf.line(
                        x_peak + style.margin.left,
                        y_peak,
                        x_peak + style.margin.left + w_line,
                        y_peak,
                    )

                style = self.styles["summary_peak_name"]
                with use_style(self.pdf, style) as pdf:
                    self.pdf.set_xy(
                        x_peak + style.margin.left,
                        y_peak - style.line_height,
                    )
                    pdf.cell(
                        name,
                        border=SHOW_BOUNDARY,
                        center=False,
                        w=w_text,
                    )

                style = self.styles["summary_peak_altitude"]
                with use_style(self.pdf, style) as pdf:
                    self.pdf.set_xy(x_peak + style.margin.left, y_peak)
                    pdf.cell(
                        alt_text,
                        border=SHOW_BOUNDARY,
                        center=False,
                        w=w_text,
                    )

                style = self.styles["summary_peak_icon"]
                with use_style(self.pdf, style) as pdf:
                    # NOTE: Some icons are wider than high.
                    #       Fix font_size so that max width = font size
                    icon_str = fa.get_icon(str(i), "solid")
                    icon_w = self.pdf.get_cell_width(icon_str)
                    font_size_pt = self.pdf.font_size_pt
                    if icon_w > font_size_pt:
                        self.pdf.set_font_size(font_size_pt**2 / icon_w)
                    icon_w = font_size_pt
                    self.pdf.set_xy(
                        x_peak + dx_icon,
                        y_peak - icon_w / 2 - style.padding.top,
                    )
                    pdf.cell(
                        icon_str,
                        border=SHOW_BOUNDARY,
                        center=False,
                        w=icon_w,
                    )

    @contextlib.contextmanager
    def reset_pdf_margins(self) -> Iterator[None]:
        t_margin = self.pdf.t_margin
        r_margin = self.pdf.r_margin
        b_margin = self.pdf.b_margin
        l_margin = self.pdf.l_margin
        try:
            yield
        finally:
            self.pdf.set_margins(l_margin, t_margin, r_margin)
            self.pdf.set_auto_page_break(self.pdf.auto_page_break, b_margin)

    def render_stats(self) -> None:
        # Collect stats
        stats = []
        if self.total_distance is not None:
            n = int(round(self.total_distance, 0))
            stats.append(
                (
                    "arrows-left-right",
                    str(n),
                    "Kilometer" + ("s" if n > 1 else ""),
                )
            )
        if hasattr(self.pdf, "start_date") and hasattr(self.pdf, "end_date"):
            n = (self.pdf.end_date - self.pdf.start_date).days + 1
            stats.append(
                ("calendar_days", str(n), "Day" + ("s" if n > 1 else ""))
            )
        if self.country_codes is not None:
            n = len(self.country_codes)
            stats.append(("flag", str(n), "Countr" + ("ies" if n > 1 else "y")))
        if self.post_count is not None:
            n = self.post_count
            stats.append(
                ("location-dot", str(n), "Post" + ("s" if n > 1 else ""))
            )
        if self.photo_count is not None:
            n = self.photo_count
            stats.append(
                ("camera-retro", str(n), "Photo" + ("s" if n > 1 else ""))
            )
        if not stats:
            return

        # Title
        title = "Stats"
        with use_style(self.pdf, self.styles["summary_h2"]) as pdf:
            pdf.cell(title, border=SHOW_BOUNDARY, new_y=fpdf.YPos.NEXT)

        # Calc stat column widths
        style = self.styles["summary_stats_footer"]
        with self.pdf.use_font_face(style.font_face):
            w = max(
                self.pdf.get_cell_width(style.text_transform.transform(footer))
                for _, _, footer in stats
            )
            cw = w + style.padding.left + style.padding.right
        cw = min(cw, self.pdf.epw / len(stats))
        total_w = len(stats) * cw

        # Draw stat columns
        with self.reset_pdf_margins():
            y = self.pdf.y
            lr_margin = (self.pdf.w - total_w) / 2
            for i, (icon, main, footer) in enumerate(stats):
                self.pdf.set_left_margin(lr_margin + i * cw)
                self.pdf.set_right_margin(self.pdf.w - self.pdf.l_margin - cw)
                self.pdf.set_y(y)

                with use_style(
                    self.pdf, self.styles["summary_stats_icon"]
                ) as pdf:
                    # NOTE: Some icons are wider than high.
                    #       Fix font_size so that max width = font size
                    icon_str = fa.get_icon(icon, "solid")
                    icon_w = self.pdf.get_cell_width(icon_str)
                    font_size_pt = self.pdf.font_size_pt
                    if icon_w > font_size_pt:
                        self.pdf.set_font_size(font_size_pt**2 / icon_w)
                    pdf.cell(
                        icon_str,
                        border=SHOW_BOUNDARY,
                        w=font_size_pt,
                        new_y=fpdf.YPos.NEXT,
                    )

                with use_style(
                    self.pdf, self.styles["summary_stats_main"]
                ) as pdf:
                    pdf.cell(
                        main,
                        border=SHOW_BOUNDARY,
                        w=w,
                        new_y=fpdf.YPos.NEXT,
                    )

                with use_style(
                    self.pdf, self.styles["summary_stats_footer"]
                ) as pdf:
                    pdf.cell(
                        footer,
                        border=SHOW_BOUNDARY,
                        w=w,
                        new_y=fpdf.YPos.NEXT,
                    )

                if SHOW_BOUNDARY:
                    self.pdf.rect(self.pdf.l_margin, y, cw, self.pdf.y - y)

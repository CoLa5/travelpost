"""Utils."""

import datetime as dt


def decimal_coo_to_dms(value: float, is_lat: bool, decimals: int = 0) -> str:
    if is_lat:
        direction = "N" if value >= 0 else "S"
    else:
        direction = "E" if value >= 0 else "W"

    value = abs(value)
    deg = int(value)
    min_full = (value - deg) * 60
    min_ = int(min_full)
    sec = (min_full - min_) * 60

    sec = round(sec, decimals)
    if sec == 60.0:
        sec = 0.0
        min_ += 1
    if min_ == 60:
        min_ = 0
        deg += 1

    return f"{deg:d}° {min_:02d}' {sec:02.{decimals}f}\" {direction:s}"  # ′″


def travel_period_str(
    start_date: dt.date,
    end_date: dt.date,
    *,
    show_day: bool = False,
    short_month: bool = False,
    short_year: bool = False,
) -> str:
    fmt_m = "%b " if short_month else "%B "
    fmt_y = "'%y" if short_year else "%Y"
    if start_date.year == end_date.year and start_date.month == end_date.month:
        text = f"{start_date.day:d} - {end_date.day:d} " if show_day else ""
        text += start_date.strftime(f"{fmt_m:s} {fmt_y:s}")
    else:
        text = f"{start_date.day:d} " if show_day else ""
        text += start_date.strftime(
            f"{fmt_m:s} {fmt_y:s}"
            if start_date.year != end_date.year
            else fmt_m
        )
        text += " - "
        text += f"{end_date.day:d} " if show_day else ""
        text += end_date.strftime(f"{fmt_m:s} {fmt_y:s}")
    if short_month:
        text = text.upper()
    return text

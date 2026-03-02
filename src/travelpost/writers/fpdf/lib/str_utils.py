"""Utils."""

import datetime as dt

SPACE: str = "\u202f"


def _decimal_coo_to_dms(value: float, is_lat: bool, decimals: int = 0) -> str:
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

    return (
        f"{deg:d}°{SPACE:s}"
        f"{min_:02d}’{SPACE:s}"
        f"{sec:02.{decimals:d}f}″{SPACE:s}"
        f"{direction:s}"
    )  # ′″


def lat_to_dms(lat: float, decimals: int = 0) -> str:
    return _decimal_coo_to_dms(lat, True, decimals=decimals)


def lon_to_dms(lon: float, decimals: int = 0) -> str:
    return _decimal_coo_to_dms(lon, False, decimals=decimals)


def alt_to_str(alt: float, decimals: int = 0) -> str:
    alt = round(alt * 10**decimals) / 10**decimals
    alt_symbol = "\u25b2" if alt >= 0.0 else "\u25bc"
    return f"{alt_symbol:s}{SPACE:s}{alt:,.{decimals:d}f}{SPACE:s}m"


def flag_unicode(country_code: str) -> str:
    country_code = country_code.upper()
    if len(country_code) != 2 or not country_code.isalpha():
        msg = (
            f"country code must be 2 letters (ISO-3166-1 alpha-2), not "
            f"{country_code!r:s}"
        )
        raise ValueError(msg)
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in country_code)


def travel_period_str(
    start_date: dt.date,
    end_date: dt.date,
    *,
    show_day: bool = False,
    short_month: bool = False,
    short_year: bool = False,
) -> str:
    fmt_m = "%b " if short_month else "%B "
    fmt_y = "’%y" if short_year else "%Y"
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
        text += "– "
        text += f"{end_date.day:d} " if show_day else ""
        text += end_date.strftime(f"{fmt_m:s} {fmt_y:s}")
    if short_month:
        text = text.upper()
    return text

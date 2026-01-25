"""Types."""

type Lon = float
"""Longitude."""

type Lat = float
"""Latitude."""

type Coo = tuple[Lon, Lat]
"""Coordinate `(longitude, latitude)`."""

type CooBounds = tuple[Lon, Lat, Lon, Lat]
"""Coordinate bounds `(lon_min, lat_min, lon_max, lat_max)`."""

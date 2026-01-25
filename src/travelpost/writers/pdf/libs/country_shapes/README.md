# README

Dowload country shapes from
[Natural Earth Data](https://www.naturalearthdata.com/downloads/), e.g.
[1:10m Cultural Vector - Admin 0 - Countries](https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip),
unpack the package and create the icons by calling:

```shell
$ python -m .\src\travelpost\writers\pdf\libs\country_shapes\creator \
--export-all \
--height=600 \
--padding=16 \
--oversampling=4 \
--shp-path=./ne_10m_admin_0_countries.shp
```

**Attention**:

- Set the `--shp-path` to the directory that comprises the
  `ne_10m_admin_0_countries.shp` of natural earth data.
- If you want to set later points on the country shape, make the padding as tall
  as the point radius to guarantee no cut-off at the viewbox-limits.

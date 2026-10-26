"""The GHSL R2023A tiles (JRC open data, CC BY 4.0): 100 m cells on a Mollweide grid (ESRI:54009), cut into 1000 km squares
R<row>_C<col> counted from the upper left. A tile serves every city that lies on it, so the tiles stay shared under raw/ghsl/;
a reader takes only the tiles that cover its city's area (one, or two to four for an area across a tile edge).
  S  GHS-BUILT-S, built-up surface, m² a cell (pipeline/overture_ghsl.py dates buildings by it)
  V  GHS-BUILT-V, built-up volume, m³ a cell (pipeline/ghsl_change.py)"""
import os, urllib.request

EPOCHS = [1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025, 2030]
URL = ('https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_{k}_GLOBE_R2023A/GHS_BUILT_{k}_E{y}_GLOBE_R2023A_54009_100/V1-0/tiles/'
       'GHS_BUILT_{k}_E{y}_GLOBE_R2023A_54009_100_V1_0_{tile}.zip')


def tiles(box):
    """the tiles that cover the box (west, south, east, north in degrees; a city's box is far smaller than a tile)"""
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 'ESRI:54009', always_xy=True)
    out = set()
    for lon in (box[0], box[2]):
        for lat in (box[1], box[3]):
            x, y = tr.transform(lon, lat)
            out.add(f'R{int((9000000 - y) // 1000000) + 1}_C{int((x + 18041000) // 1000000) + 1}')
    return sorted(out)


def _path(raw, kind, year, tile):
    return os.path.join(raw, 'ghsl', os.path.basename(URL.format(k=kind, y=year, tile=tile)))


def paths(raw, kind, year, box):
    """the downloaded tiles of this kind and epoch that cover the box; stops if one is missing"""
    ps = [_path(raw, kind, year, t) for t in tiles(box)]
    missing = [os.path.basename(p) for p in ps if not os.path.exists(p)]
    if missing: raise SystemExit(f'ghsl: {", ".join(missing)} not in {raw}/ghsl: download the tiles that cover the city first (docs/DATA.md)')
    return ps


def tif(z):
    """rasterio's path to the GeoTIFF inside a tile's zip"""
    return f'zip://{z}!' + os.path.basename(z)[:-4] + '.tif'


def fetch(raw, kind, box):
    """download the epoch tiles of this kind that cover the box (a zip with a GeoTIFF each); a tile already here is kept"""
    os.makedirs(os.path.join(raw, 'ghsl'), exist_ok=True)
    for y in EPOCHS:
        for t in tiles(box):
            url = URL.format(k=kind, y=y, tile=t); dst = _path(raw, kind, y, t)
            if os.path.exists(dst): continue
            print('fetching', url); urllib.request.urlretrieve(url, dst + '.part'); os.replace(dst + '.part', dst)
    return os.path.join(raw, 'ghsl')

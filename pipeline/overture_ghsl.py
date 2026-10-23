"""Global fallback adapter: Overture Maps building footprints (+ height) with a first-appearance epoch from the GHSL
built-up surface series (GHS-BUILT-S R2023A, 1975-2030 every 5 years, 100 m). Years are estimates at 100 m / 5-year precision
and the film must say so (docs/DATA.md).

  python -I pipeline/overture_ghsl.py fetch <west> <south> <east> <north> [--release 2026-09-23.1]
      (releases: curl 'https://overturemaps-us-west-2.s3.amazonaws.com/?prefix=release/&delimiter=/'; the scan is heavy: run it alone, niced)
      -> raw/overture/buildings_<hash>.geojson  (DuckDB + httpfs + spatial over the public S3 release; needs network)
  python -I pipeline/overture_ghsl.py ghsl <west> <south> <east> <north>
      -> raw/ghsl/GHS_BUILT_S_E<year>_... tiles (one per epoch) from the JRC open-data server
raw/ is this machine's raw root (pipeline/local.py). load(raw, frame) yields (polygon_utm, height_m, year_or_None, how, function) like cmab.load(), for prep.py."""
import glob, hashlib, json, os, sys, urllib.request
from shapely.geometry import shape
from shapely.validation import make_valid

EPOCHS = [1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025, 2030]
GHSL_BASE = 'https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_S_GLOBE_R2023A/GHS_BUILT_S_E{y}_GLOBE_R2023A_54009_100/V1-0/tiles/GHS_BUILT_S_E{y}_GLOBE_R2023A_54009_100_V1_0_{tile}.zip'


def _key(box): return hashlib.sha1(json.dumps([round(v, 4) for v in box]).encode()).hexdigest()[:10]


def fetch(raw, box, release='2026-09-23.1'):
    """Overture buildings in the box -> GeoJSON (WGS84). Uses DuckDB's httpfs + spatial extensions."""
    w, s, e, n = box
    out_dir = os.path.join(raw, 'overture'); os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f'buildings_{_key(box)}.geojson')
    if os.path.exists(out): return out
    if not os.path.exists(out + '.tmp.json'):   # (a scan already done is not run again: it takes minutes over the network)
        _scan(out, box, release)
    rows = json.load(open(out + '.tmp.json'))
    geo = lambda g: json.loads(g) if isinstance(g, str) else g   # (newer DuckDB writes the JSON column as an object)
    fc = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {k: r[k] for k in ('id', 'height', 'num_floors', 'class', 'subtype')}, 'geometry': geo(r['geometry'])} for r in rows]}
    json.dump(fc, open(out, 'w')); os.remove(out + '.tmp.json')
    print(f'overture: {len(rows)} buildings -> {out}')
    return out


def _scan(out, box, release):
    """the DuckDB scan of the public release (httpfs + spatial) into out.tmp.json"""
    import duckdb
    w, s, e, n = box
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2'; SET memory_limit='3GB'; SET threads=2;")
    q = f"""
      COPY (
        SELECT id, height, num_floors, class, subtype, ST_AsGeoJSON(geometry) AS geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=buildings/type=building/*', filename=true, hive_partitioning=1)
        WHERE bbox.xmin >= {w} AND bbox.xmax <= {e} AND bbox.ymin >= {s} AND bbox.ymax <= {n}
      ) TO '{out}.tmp.json' (FORMAT JSON, ARRAY true)"""
    con.execute(q)


def _mollweide_tile(lon, lat):
    """GHSL R2023A 100 m tiles are 1000 km squares on a Mollweide (ESRI:54009) grid: R<row>_C<col>, origin at the upper-left."""
    from pyproj import Transformer
    x, y = Transformer.from_crs(4326, 'ESRI:54009', always_xy=True).transform(lon, lat)
    col = int((x + 18041000) // 1000000) + 1; row = int((9000000 - y) // 1000000) + 1
    return f'R{row}_C{col}'


def ghsl(raw, box):
    """download the GHS-BUILT-S epoch tiles that cover the box (zip with a GeoTIFF each)"""
    w, s, e, n = box
    tiles = sorted({_mollweide_tile(lon, lat) for lon in (w, e) for lat in (s, n)})
    out_dir = os.path.join(raw, 'ghsl'); os.makedirs(out_dir, exist_ok=True)
    for y in EPOCHS:
        for tile in tiles:
            url = GHSL_BASE.format(y=y, tile=tile); dst = os.path.join(out_dir, os.path.basename(url))
            if os.path.exists(dst): continue
            print('fetching', url); urllib.request.urlretrieve(url, dst + '.part'); os.replace(dst + '.part', dst)
    return out_dir


def first_epoch(raw, lonlats, threshold=1500):
    """for each (lon, lat): the first epoch whose built-up surface in the 100 m cell is >= threshold m² (of 10,000), else None"""
    import numpy as np, rasterio
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 'ESRI:54009', always_xy=True)
    xs, ys = tr.transform([p[0] for p in lonlats], [p[1] for p in lonlats])
    years = [None] * len(lonlats)
    for y in EPOCHS:
        for z in sorted(glob.glob(os.path.join(raw, 'ghsl', f'GHS_BUILT_S_E{y}_*.zip'))):
            with rasterio.open(f'zip://{z}!' + os.path.basename(z)[:-4] + '.tif') as ds:   # (the tile's GeoTIFF inside the zip)
                vals = np.array([v[0] for v in ds.sample(zip(xs, ys))])
            for i, v in enumerate(vals):
                if years[i] is None and v >= threshold: years[i] = y
    return years


def load(raw, frame, simplify_m=1.0, min_area=15.0, threshold=1500):
    gj = sorted(glob.glob(os.path.join(raw, 'overture', '*.geojson')))
    if not gj: sys.exit('no Overture file under raw/overture: run pipeline/overture_ghsl.py fetch first')
    feats = json.load(open(gj[-1]))['features']
    polys, cents = [], []
    for f in feats:
        try:
            g = shape(f['geometry'])
            if g.geom_type == 'MultiPolygon': g = max(g.geoms, key=lambda q: q.area)
            if g.geom_type != 'Polygon': continue
            from shapely.ops import transform as sh_transform
            p = sh_transform(lambda x, y, z=None: frame.to_utm.transform(x, y), g)
            if not p.is_valid: p = make_valid(p)
            if p.geom_type != 'Polygon': continue
            if simplify_m: p = p.simplify(simplify_m, preserve_topology=True)
            if p.is_empty or p.area < min_area: continue
            c = p.centroid
            if not frame.inside(c.x, c.y): continue
            pr = f['properties']; h = pr.get('height') or (pr.get('num_floors') or 0) * 3.2 or 9.0
            polys.append((p, float(h), pr.get('class') or '')); cents.append(frame.ground_wgs(c.x, c.y))
        except Exception:   # noqa: BLE001
            continue
    years = first_epoch(raw, cents, threshold) if cents else []
    for (p, h, cls), y in zip(polys, years):
        yield p, h, y, ('epoch' if y else 'unknown'), cls


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import local   # this machine's raw root
    cmd, raw = sys.argv[1], local.raw(); box = tuple(float(v) for v in sys.argv[2:6])
    if cmd == 'fetch':
        rel = sys.argv[sys.argv.index('--release') + 1] if '--release' in sys.argv else '2026-09-23.1'
        fetch(raw, box, rel)
    elif cmd == 'ghsl':
        ghsl(raw, box)
    else:
        sys.exit('usage: overture_ghsl.py fetch|ghsl <w> <s> <e> <n>')

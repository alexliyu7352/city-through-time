"""Global fallback adapter: Overture Maps building footprints (+ height) with a first-appearance epoch from the GHSL
built-up surface series (GHS-BUILT-S R2023A, 1975-2030 every 5 years, 100 m). Years are estimates at 100 m / 5-year precision
and the film must say so (docs/DATA.md).

  python -I pipeline/overture_ghsl.py fetch <city_dir> [--release 2026-09-23.1]
      (releases: curl 'https://overturemaps-us-west-2.s3.amazonaws.com/?prefix=release/&delimiter=/'; the scan is heavy: run it alone, niced)
      -> <the city's raw folder>/overture/buildings_<hash of the box>.geojson  (the box is city.yaml's; the city's raw folder:
         pipeline/layout.py raw; DuckDB + httpfs + spatial over the public S3 release; needs network)
  python -I pipeline/overture_ghsl.py ghsl <city_dir>
      -> raw/ghsl/GHS_BUILT_S_E<year>_... the tiles that cover the box (pipeline/ghsl.py; shared by the cities on them)
raw/ is this machine's raw root (pipeline/local.py). load(city, frame) yields (polygon_utm, height_m, year_or_None, how, function) like cmab.load(), for prep.py."""
import hashlib, json, os, sys
from shapely.geometry import shape
from shapely.validation import make_valid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ghsl, layout, local

EPOCHS = ghsl.EPOCHS


def _key(box): return hashlib.sha1(json.dumps([round(v, 4) for v in box]).encode()).hexdigest()[:10]


def _cached(city, box):
    """the city's Overture file for this box (a new box needs a new fetch: the old box's file is never read)"""
    return layout.raw(city, 'overture', f'buildings_{_key(box)}.geojson')


def fetch(city, release='2026-09-23.1'):
    """Overture buildings in the city's box -> GeoJSON (WGS84). Uses DuckDB's httpfs + spatial extensions."""
    box = layout.box(city)
    out = _cached(city, box); os.makedirs(os.path.dirname(out), exist_ok=True)
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
    """the DuckDB scan of the public release (httpfs + spatial) into out.tmp.json: written under another name and renamed only
    when the scan has finished, so an interrupted scan leaves nothing a later fetch would take for a finished one"""
    import duckdb
    w, s, e, n = box
    part = out + '.scan.json'
    if os.path.exists(part): os.remove(part)   # (what an interrupted scan left)
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2'; SET memory_limit='3GB'; SET threads=2;")
    q = f"""
      COPY (
        SELECT id, height, num_floors, class, subtype, ST_AsGeoJSON(geometry) AS geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=buildings/type=building/*', filename=true, hive_partitioning=1)
        WHERE bbox.xmin >= {w} AND bbox.xmax <= {e} AND bbox.ymin >= {s} AND bbox.ymax <= {n}
      ) TO '{part}' (FORMAT JSON, ARRAY true)"""
    con.execute(q); con.close()
    os.replace(part, out + '.tmp.json')


def first_epoch(raw, lonlats, box, threshold=1500):
    """for each (lon, lat) inside the box: the first epoch whose built-up surface in the 100 m cell is >= threshold m² (of 10,000),
    else None; read from the GHSL tiles that cover the box"""
    import numpy as np, rasterio
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 'ESRI:54009', always_xy=True)
    xs, ys = tr.transform([p[0] for p in lonlats], [p[1] for p in lonlats])
    years = [None] * len(lonlats)
    for y in EPOCHS:
        for z in ghsl.paths(raw, 'S', y, box):
            with rasterio.open(ghsl.tif(z)) as ds:
                vals = np.array([v[0] for v in ds.sample(zip(xs, ys))]); nodata = ds.nodata
            for i, v in enumerate(vals):   # (a point off this tile, or a cell without data, reads nodata: 65535, above any threshold)
                if years[i] is None and v != nodata and v >= threshold: years[i] = y
    return years


def load(city, frame, simplify_m=1.0, min_area=15.0, threshold=1500):
    cached = _cached(city, frame.box)
    if not os.path.exists(cached): sys.exit(f'no Overture file for the box of {city}: run pipeline/overture_ghsl.py fetch {city} first')
    feats = json.load(open(cached))['features']
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
    years = first_epoch(local.raw(), cents, frame.box, threshold) if cents else []
    for (p, h, cls), y in zip(polys, years):
        yield p, h, y, ('epoch' if y else 'unknown'), cls


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] not in ('fetch', 'ghsl'): sys.exit('usage: overture_ghsl.py fetch|ghsl <city_dir> [--release <name>]')
    cmd, city = sys.argv[1], sys.argv[2]
    if cmd == 'fetch':
        rel = sys.argv[sys.argv.index('--release') + 1] if '--release' in sys.argv else '2026-09-23.1'
        fetch(city, rel)
    else:
        ghsl.fetch(local.raw(), 'S', layout.box(city))

"""CMAB adapter (China Multi-Attribute Building dataset, Tsinghua; figshare 27992417, per-province zips of shapefiles).
Yields buildings inside a Frame as (rings_ground_m, height_m, year_or_None, function) from every CMAB shapefile whose
bbox touches the box. Coordinates in the release are Web Mercator (EPSG:3857); the .prj is checked.
Age in CMAB is the first year the building's centroid appears in the GAIA impervious-surface series (1985-2018):
'1987' means 'already there in the 1987 observation', 'AF2018' means first seen after 2018, 'NaN' unknown."""
import glob, os, sys
import shapefile
from shapely.geometry import Polygon
from shapely.validation import make_valid


def shapefiles(root):
    return sorted(glob.glob(os.path.join(root, '**', '*.shp'), recursive=True))


def parse_age(a):
    a = (a or '').strip()
    if a.isdigit(): return int(a), 'seen'
    if a.upper().startswith('AF') and a[2:].isdigit(): return int(a[2:]) + 1, 'after'
    return None, 'unknown'


def load(root, frame, simplify_m=1.0, min_area=15.0):
    bx0, by0 = frame.x0, frame.y0; bx1, by1 = frame.x1, frame.y1
    n_files = 0
    for shp in shapefiles(root):
        prj = open(shp[:-4] + '.prj', encoding='utf-8', errors='ignore').read() if os.path.exists(shp[:-4] + '.prj') else ''
        if 'Mercator' not in prj and '3857' not in prj:
            sys.exit(f'{shp}: expected Web Mercator .prj, got: {prj[:80]}')
        r = shapefile.Reader(shp)
        x0, y0 = frame.merc_to_utm.transform(r.bbox[0], r.bbox[1]); x1, y1 = frame.merc_to_utm.transform(r.bbox[2], r.bbox[3])
        if x1 < bx0 or x0 > bx1 or y1 < by0 or y0 > by1: continue
        n_files += 1
        fields = [f[0] for f in r.fields[1:]]
        for sr in r.iterShapeRecords(fields=['Height', 'Function', 'Age']):
            rec = sr.record; h = rec['Height']
            if h is None or not (h == h) or h < 2.0: continue
            s = sr.shape
            if s.shapeType not in (5, 15, 25): continue   # polygon types
            parts = list(s.parts) + [len(s.points)]
            rings = []
            for i in range(len(parts) - 1):
                pts = s.points[parts[i]:parts[i + 1]]
                xs, ys = frame.merc_to_utm.transform([p[0] for p in pts], [p[1] for p in pts])
                rings.append(list(zip(xs, ys)))
            if not rings: continue
            # shapefile parts: outer rings clockwise, holes counter-clockwise; keep the first ring as outer, rest as holes
            try:
                poly = Polygon(rings[0], rings[1:])
                if not poly.is_valid: poly = make_valid(poly)
                if poly.geom_type == 'MultiPolygon': poly = max(poly.geoms, key=lambda g: g.area)
                if poly.geom_type != 'Polygon': continue
                if simplify_m: poly = poly.simplify(simplify_m, preserve_topology=True)
            except Exception:   # noqa: BLE001
                continue
            if poly.is_empty or poly.area < min_area: continue
            c = poly.centroid
            if not frame.inside(c.x, c.y): continue
            year, how = parse_age(rec['Age'])
            yield poly, float(h), year, how, rec['Function']
    if n_files == 0:
        sys.exit(f'no CMAB shapefile under {root} touches the box')

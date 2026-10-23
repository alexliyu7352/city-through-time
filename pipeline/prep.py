"""city.yaml -> data/model.json (the white model), data/water.png (water inlay mask), data/lines.json (roads, rail,
schematic lines in model units), data/stats.json (every number the film shows).
usage: python -I pipeline/prep.py <city_dir>      (reads <city_dir>/city.yaml; raw data under city.yaml's raw: paths)
Model frame: x east, z south, y up; 1 unit = 1 model metre; scale 1:N means 1 model metre = N ground metres."""
import json, os, sys, math, collections
import yaml
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, Point, mapping
from shapely.ops import unary_union, transform as sh_transform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import Frame, ring_area
import cmab, local

D = os.path.abspath(sys.argv[1])
C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'))
F = Frame(tuple(C['box']), 1.0 / C['scale'])
import layout as LAYOUT
LAYOUT.ensure(D)
RAW = C.get('raw', {})   # raw.cmab: the CMAB province folder, relative to this machine's raw root (pipeline/local.py)

# ------------------------------------------------------------------ terrain (optional): ground height per point, in model units
TER = None
tpath = LAYOUT.data(D, 'terrain.png')
if os.path.exists(tpath) and C.get('terrain', {}).get('enabled', True):
    import terrainio
    timg, tj = terrainio.load(D)   # metres above the box minimum
    TEX = float(C.get('terrain', {}).get('exaggeration', 3.0))
    def ground(x, y):
        """ground metres -> model units of relief (already exaggerated) at a ground point (bilinear, like the engine)"""
        u, v = F.uv(x, y); return terrainio.bilinear(timg, u, v) * F.scale * TEX
    TER = {'min_m': tj['min_m'], 'max_m': tj['max_m'], 'exaggeration': TEX, 'size': tj['size']}
    print(f'terrain: {tj["min_m"]}–{tj["max_m"]} m, exaggeration x{TEX}')
else:
    def ground(x, y): return 0.0

# ------------------------------------------------------------------ buildings (heights exaggerated like the terrain so the massing reads at 1:10000)
BEX = float(C.get('buildings', {}).get('exaggeration', C.get('terrain', {}).get('exaggeration', 3.0)))   # today's buildings; the plate has its own factor
bands = C['bands']   # [{lo, hi, zh, en}], years; lo inclusive, hi exclusive; buildings with no year go to band -1
def band_of(y):
    if y is None: return -1
    for i, b in enumerate(bands):
        if b['lo'] <= y < b['hi']: return i
    return -1

B, P = [], []
src = C['buildings']['source']
stat = collections.Counter(); area_by_band = collections.defaultdict(float); n_by_band = collections.Counter(); h_by_band = collections.defaultdict(list)
if src == 'cmab':
    it = cmab.load(local.raw(RAW['cmab']), F, simplify_m=C['buildings'].get('simplify_m', 1.0), min_area=C['buildings'].get('min_area_m2', 15))
elif src == 'overture_ghsl':
    import overture_ghsl
    it = overture_ghsl.load(local.raw(), F, simplify_m=C['buildings'].get('simplify_m', 1.0), min_area=C['buildings'].get('min_area_m2', 15), threshold=C['buildings'].get('ghsl_threshold', 1500))
else:
    sys.exit(f'unknown buildings.source {src}')
tallest = []
for poly, h, year, how, func in it:
    bi = len(B)
    b = band_of(year)
    B.append([year if year is not None else 0, round(h, 1)])
    rings = [[F.model(x, y) for x, y in poly.exterior.coords[:-1]]] + [[F.model(x, y) for x, y in r.coords[:-1]] for r in poly.interiors]
    c = poly.centroid
    P.append([bi, round(h * F.scale * BEX, 6), rings, round(ground(c.x, c.y), 6)])
    stat[how] += 1; n_by_band[b] += 1; area_by_band[b] += poly.area; h_by_band[b].append(h)
    tallest.append((h, bi, c.x, c.y, year))
# where the primary source has no buildings at all (CMAB leaves out villages and parts of the new towns: the northern plateau stood
# empty), Overture's footprints fill in (OSM + Shi et al. 2023 East Asian buildings, CC BY 4.0), dated by GHSL's built-up surface:
# a footprint comes in only when no primary building stands within fill_gap_m (no doubles where both sources map a town)
if C['buildings'].get('fill') == 'overture_ghsl':
    import overture_ghsl
    gap = float(C['buildings'].get('fill_gap_m', 100)); occ = set()
    for _, _, cx_, cy_, _ in tallest: occ.add((int(cx_ // gap), int(cy_ // gap)))
    n_fill = 0
    for poly, h, year, how, func in overture_ghsl.load(local.raw(), F, simplify_m=C['buildings'].get('simplify_m', 1.0), min_area=C['buildings'].get('min_area_m2', 15), threshold=C['buildings'].get('ghsl_threshold', 1500)):
        c = poly.centroid; k = (int(c.x // gap), int(c.y // gap))
        if any((k[0] + dx, k[1] + dy) in occ for dx in (-1, 0, 1) for dy in (-1, 0, 1)): continue
        bi = len(B); b = band_of(year)
        B.append([year if year is not None else 0, round(h, 1)])
        rings = [[F.model(x, y) for x, y in poly.exterior.coords[:-1]]] + [[F.model(x, y) for x, y in r.coords[:-1]] for r in poly.interiors]
        P.append([bi, round(h * F.scale * BEX, 6), rings, round(ground(c.x, c.y), 6)])
        stat['fill'] += 1; n_by_band[b] += 1; area_by_band[b] += poly.area; h_by_band[b].append(h); n_fill += 1
        tallest.append((h, bi, c.x, c.y, year))
    print(f'fill: {n_fill} Overture buildings where {src} has none within {gap:.0f} m')
tallest.sort(reverse=True)
print(f'buildings: {len(B)}  age: {dict(stat)}')

# ------------------------------------------------------------------ OSM: water mask, line features, landmarks
def osm_file(theme):
    """the cached Overpass answer for this city's box (pipeline/osm.py names caches by query hash, one per box)"""
    import osm
    f = osm.cache_path(local.raw(), tuple(C['box']), theme)
    if not os.path.exists(f): print(f'warning: no OSM {theme} cache for this box; run pipeline/osm.py with the box first'); return None
    return f

def osm_elements(theme):
    f = osm_file(theme)
    if not f: print(f'warning: no OSM {theme} file; skipping'); return []
    return json.load(open(f, encoding='utf-8'))['elements']

def el_polys(el):
    """closed ways and multipolygon relations -> list of shapely polygons in ground metres"""
    out = []
    if el['type'] == 'way' and el.get('geometry') and el['geometry'][0] == el['geometry'][-1]:
        pts = [F.to_utm.transform(p['lon'], p['lat']) for p in el['geometry']]
        if len(pts) >= 4: out.append(Polygon(pts))
    elif el['type'] == 'relation':
        outers, inners = [], []
        for m in el.get('members', []):
            if m.get('type') != 'way' or not m.get('geometry'): continue
            pts = [F.to_utm.transform(p['lon'], p['lat']) for p in m['geometry']]
            (outers if m.get('role') != 'inner' else inners).append(LineString(pts))
        from shapely.ops import polygonize, linemerge
        try:
            ol = list(polygonize(unary_union(linemerge(outers)))) if outers else []
            il = list(polygonize(unary_union(linemerge(inners)))) if inners else []
            for o in ol:
                for i in il:
                    if o.contains(i): o = o.difference(i)
                out.append(o)
        except Exception:   # noqa: BLE001
            pass
    return [p.buffer(0) for p in out if not p.is_empty]

def el_line(el):
    if el['type'] == 'way' and el.get('geometry'):
        return LineString([F.to_utm.transform(p['lon'], p['lat']) for p in el['geometry']])
    return None

MW = 4096; MH = round(MW * F.size[1] / F.size[0])
water = Image.new('L', (MW, MH), 0); dw = ImageDraw.Draw(water)
PX = lambda ring: [(F.uv(x, y)[0] * MW, F.uv(x, y)[1] * MH) for x, y in ring]
n_water = 0
for el in osm_elements('water'):
    tags = el.get('tags', {})
    if tags.get('waterway') in ('river', 'canal') and not (el['type'] == 'way' and el['geometry'][0] == el['geometry'][-1]):
        ln = el_line(el)
        if ln is not None and tags.get('waterway') == 'river':
            wmin = 60 if 'name' in tags else 25
            for g in getattr(ln.buffer(wmin / 2), 'geoms', [ln.buffer(wmin / 2)]):
                dw.polygon(PX(g.exterior.coords), fill=255); n_water += 1
        continue
    for p in el_polys(el):
        if p.area < 2000: continue
        dw.polygon(PX(p.exterior.coords), fill=255)
        for i in p.interiors: dw.polygon(PX(i.coords), fill=0)
        n_water += 1
water.filter(ImageFilter.GaussianBlur(1.0)).save(LAYOUT.data(D, 'water.png'))
print('water features drawn:', n_water)

lines = {'roads': [], 'rail': [], 'subway': [], 'rivers': []}
for el in osm_elements('water'):
    tags = el.get('tags', {})
    if tags.get('waterway') == 'river' and el['type'] == 'way' and el.get('geometry') and el['geometry'][0] != el['geometry'][-1]:
        ln = el_line(el)
        if ln is not None: lines['rivers'].append({'name': tags.get('name'), 'pts': [F.model(x, y) for x, y in ln.coords], 'tags': {'name': tags.get('name', '')}})
for el in osm_elements('roads'):
    ln = el_line(el)
    if ln is not None: lines['roads'].append({'cls': el['tags'].get('highway'), 'name': el['tags'].get('name'), 'pts': [F.model(x, y) for x, y in ln.coords]})
for el in osm_elements('rail'):
    ln = el_line(el)
    if ln is None: continue
    key = 'subway' if el['tags'].get('railway') in ('subway', 'light_rail') else 'rail'
    lines[key].append({'name': el['tags'].get('name'), 'pts': [F.model(x, y) for x, y in ln.coords], 'tags': {k: v for k, v in el['tags'].items() if k in ('railway', 'name', 'usage', 'service', 'start_date', 'opening_date')}})
for k, v in lines.items(): print(k, len(v), 'ways')

# landmarks named in city.yaml: lon/lat -> model position (+ the nearest building's roof for a pin anchor)
marks = {}
for m in C.get('landmarks', []):
    x, y = F.to_utm.transform(m['lon'], m['lat'])
    mx, mz = F.model(x, y)
    near = None
    if m.get('snap_to_building', True) and P:
        # nearest building centroid within 150 m
        best = None
        for h, bi, cx, cy, year in tallest:
            d = math.hypot(cx - x, cy - y)
            if d < 150 and (best is None or d < best[0]): best = (d, bi, h, year)
        if best: near = {'bi': best[1], 'h': best[2], 'year': best[3]}
    marks[m['id']] = {'pos': [mx, mz, ((near['h'] * F.scale * BEX) if near else 0.0) + ground(x, y)], 'lon': m['lon'], 'lat': m['lat'], 'inside': F.inside(x, y), 'near': near, 'g': round(ground(x, y), 6), **{k: v for k, v in m.items() if k not in ('id', 'lon', 'lat')}}

# ------------------------------------------------------------------ write
# earthworks (tomb mounds etc.) as truncated pyramids: real monuments, dimensions from the sources in FACTS.md
mounds = []
def osm_named(name):
    d = local.raw('osm')
    fs = sorted(f for f in os.listdir(d) if f.startswith('historic_')) if os.path.isdir(d) else []
    if not fs: return None
    for e in json.load(open(os.path.join(d, fs[-1]), encoding='utf-8'))['elements']:
        if e.get('tags', {}).get('name') == name and e['type'] == 'way' and e.get('geometry'):
            return [F.to_utm.transform(p['lon'], p['lat']) for p in e['geometry']]
    return None
for m in C.get('mounds', []):
    if 'osm' in m:   # base = the mapped outline's minimum rotated rectangle; centre and rotation from it
        pts = osm_named(m['osm']); assert pts, f'mound {m["id"]}: OSM way {m["osm"]!r} not in the historic cache'
        rect = Polygon(pts).minimum_rotated_rectangle; rc = list(rect.exterior.coords)[:4]
        e0 = math.hypot(rc[1][0] - rc[0][0], rc[1][1] - rc[0][1]); e1 = math.hypot(rc[2][0] - rc[1][0], rc[2][1] - rc[1][1])
        x, y = rect.centroid.x, rect.centroid.y; rot = math.atan2(rc[1][1] - rc[0][1], rc[1][0] - rc[0][0])
        m = {**m, 'lon': F.ground_wgs(x, y)[0], 'lat': F.ground_wgs(x, y)[1], 'base_m': [e0, e1], 'top_m': [e0 * m.get('top_ratio', .5), e1 * m.get('top_ratio', .5)]}
    else:
        x, y = F.to_utm.transform(m['lon'], m['lat']); rot = math.radians(m.get('rot_deg', 0))
    def ring(w, d):
        out = []
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            dx, dy = sx * w / 2, sy * d / 2
            out.append(F.model(x + dx * math.cos(rot) - dy * math.sin(rot), y + dx * math.sin(rot) + dy * math.cos(rot)))
        return out
    bw, bd = (m['base_m'], m['base_m']) if isinstance(m['base_m'], (int, float)) else m['base_m']
    tw, td = (m['top_m'], m['top_m']) if isinstance(m['top_m'], (int, float)) else m['top_m']
    g0 = ground(x, y)
    mounds.append({'id': m['id'], 'base': ring(bw, bd), 'top': ring(tw, td), 'h': round(m['h_m'] * F.scale * BEX, 6), 'h_m': m['h_m'], 'year': m['year'], 'g': round(g0, 6)})
    marks[m['id']] = {'pos': F.model(x, y) + [round(m['h_m'] * F.scale * BEX + g0, 6)], 'lon': m['lon'], 'lat': m['lat'], 'inside': F.inside(x, y), 'mound': True, **{k: v for k, v in m.items() if k not in ('id', 'lon', 'lat')}}
print('mounds:', len(mounds))

model = {'scale': F.scale, 'epsg': F.epsg, 'box': C['box'], 'crop_utm': [F.x0, F.x1, F.y0, F.y1], 'size': [round(v, 5) for v in F.size],
         'bands': [[b['lo'], b['hi']] for b in bands], 'b': B, 'p': P, 'decks': [], 'mounds': mounds, 'terrain': TER, 'bex': BEX}
json.dump(model, open(LAYOUT.data(D, 'model.json'), 'w'), separators=(',', ':'))
json.dump(lines, open(LAYOUT.data(D, 'lines.json'), 'w'), separators=(',', ':'))
tot_area = sum(area_by_band.values())
stats = {
    'buildings': len(B), 'age_how': dict(stat), 'scale': C['scale'], 'size_m': [round(v, 3) for v in F.size],
    'box_km': [round((F.x1 - F.x0) / 1000, 1), round((F.y1 - F.y0) / 1000, 1)], 'centre_wgs': [round(v, 5) for v in F.ground_wgs(F.cx, F.cy)],
    'bands': [{'lo': b['lo'], 'hi': b['hi'], 'zh': b.get('zh'), 'en': b.get('en'), 'n': n_by_band[i], 'area_share': round(area_by_band[i] / tot_area, 4) if tot_area else 0,
               'mean_h': round(sum(h_by_band[i]) / len(h_by_band[i]), 1) if h_by_band[i] else 0, 'over_h': {str(t): sum(1 for h in h_by_band[i] if h >= t) for t in (50, 100)}} for i, b in enumerate(bands)],
    'no_year': {'n': n_by_band[-1], 'area_share': round(area_by_band[-1] / tot_area, 4) if tot_area else 0},
    'tallest': [{'bi': bi, 'h': round(h, 1), 'year': y, 'pos': F.model(cx, cy) + [round(h * F.scale * BEX + ground(cx, cy), 6)], 'wgs': [round(v, 5) for v in F.ground_wgs(cx, cy)]} for h, bi, cx, cy, y in tallest[:10]],
    'marks': marks,
}
json.dump(stats, open(LAYOUT.data(D, 'stats.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: stats[k] for k in ('buildings', 'age_how', 'size_m', 'box_km', 'centre_wgs', 'no_year')}, ensure_ascii=False))
for b in stats['bands']: print(b)
print('tallest', [(t['h'], t['year']) for t in stats['tallest'][:5]])

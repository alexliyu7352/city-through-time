"""The Wei as it ran before it moved north (film.water_then): research/wei_courses.geojson, from research/wei_courses.md.

Each state is today's Wei (its OSM centreline, smoothed over 1.5 km) moved south by the distance the sources give, the move
growing from nothing at the old county town's east (where the old lines in 桑廣書 2005 圖1 meet today's river) to its full size
from 108.83 E east; a band of the river's width round that line is its water (as wide as today's, 300 m, where the two
meet, to the period's width where the move is full). Its stretch, where today's water gives way, runs
from the old line (or 500 m south of today's centreline, where the old line is closer, but never south of the old
river's own bank: a tributary cut there flows into it) to 1 km north of it. The Ming–Qing town stands on the north bank: in its states the river
passes south of its south wall (the gazetteer's 縣城圖), so the line moves a little south there and today's wide weir pool goes.
usage: uv run python -I cities/xianyang/research/wei_courses.py
"""
import json, os, sys
import numpy as np
import yaml
from shapely.geometry import LineString, Point, Polygon, mapping
from shapely.ops import linemerge, unary_union

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, '..', '..', 'pipeline'))
import layout, osm, osmgeo
from geo import Frame

C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8')); F = Frame(tuple(C['box']), 1.0 / C['scale'])
U = F.to_utm.transform; W = lambda x, y: F.to_wgs.transform(x, y)
els = json.load(open(osm.cache_path(layout.raw(D), F.area, 'water'), encoding='utf-8'))['elements']

# today's centreline: the ways named 渭河, joined, as northing by easting (the river runs west-south-west to east-north-east)
wei = linemerge([LineString([U(p['lon'], p['lat']) for p in e['geometry']]) for e in els
                 if e['type'] == 'way' and e.get('tags', {}).get('waterway') == 'river' and e['tags'].get('name') == '渭河'])
pts = sorted(c for g in getattr(wei, 'geoms', [wei]) for c in g.coords)
X0, X1 = U(C['box'][0], C['box'][1])[0] - 2000, U(C['box'][2], C['box'][3])[0] + 2000
E = np.arange(X0, X1, 50.0)
y_raw = np.interp(E, [p[0] for p in pts], [p[1] for p in pts])
k = int(1500 / 50) | 1; y_today = np.convolve(np.pad(y_raw, k // 2, mode='edge'), np.ones(k) / k, mode='valid')   # (smoothed over 1.5 km)
lon_of = lambda e, y: W(e, y)[0]
LON = np.array([lon_of(e, y) for e, y in zip(E, y_today)])

# the anchors the film already stands on: the Qin 橫橋 (34.3531-34.3610 at 108.8583 E) and the Han bridge outside 廚城門
# (34.3440-34.3560 at 108.870 E, piles excavated): each reaches dry land at both ends. A course moved 3780 m south of today's
# fits the first; the second wants the river some 600 m further south, so the course bends there (a bump round 108.871 E)
ss = lambda a, b, x: np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))
ramp = ss(108.755, 108.835, LON)   # (the old lines leave today's river east of 杜郵, where the Tang town's ferry is on today's water, 圖1)
ANCIENT = (3780 + 620 * np.exp(-((LON - 108.871) / .005) ** 2 / 2)) * ramp
# the county town (Ming-Qing) stands on the north bank and its south gate on the river (縣城圖): in its states the river's
# north bank runs 70 m off the south wall along the town (today's river turns north-east into its east corner), its boats at
# the gate on the water, and it bends back into today's course east of the town
ming = Polygon([U(*p) for p in next(n for n in C['film']['nodes'] if n['id'] == 'ming')['city']['walls'][0]['ring']])
TOWNW = 350.0
y_town = np.full(len(E), ming.bounds[1] - 70 - TOWNW / 2)
w_town = ss(108.700, 108.709, LON) * (1 - ss(108.737, 108.750, LON))
STATES = {   # id: (centre, northing along the river; width, metres, along it; stretch from, to (lon); basis)
    'wei_ancient': (y_today - ANCIENT, 350 + 250 * ramp, (108.690, 109.0), 'Qin to Tang: 3780 m south of today\'s centreline (the Qin 橫橋), 4400 m at the Han bridge outside '
                    '廚城門; 桑廣書 2005 表1: 4100 m at the Qin end (the stretch\'s mean), 3400 m in 636 (Tang, drawn with this course: the map holds three states, and '
                    'the Tang shots are at 杜郵, where the two meet today\'s river); width 600 m (枯水 300-500 m, 洪水 500-1000 m; 中渭橋 525 m by 水經注)'),
    'wei_1661': ((y_today - 2000 * ramp) * (1 - w_town) + y_town * w_town, 350 + 250 * ramp, (108.690, 109.0),
                 '順治 (1644-61): 2000 m south of the 1979 course (桑廣書 2005 表1), from 杜郵 east as in 圖1; past the county town 70 m off its south wall '
                 '(乾隆《咸陽縣志》縣城圖: the Wei along the south wall, the ferry at the south gate); width 600 m, 350 m by the town'),
    'wei_1936': (y_today * (1 - w_town) + y_town * w_town, np.full(len(E), TOWNW), (108.690, 108.760),
                 'the 1930s: today\'s course, but past the county town 70 m off its south wall (縣城圖), 350 m wide: today\'s wide water there is the 2000s 咸陽湖 weir pool'),
}
def band(xs, ys, ws):   # a river of varying width round a line
    dx, dy = np.gradient(xs), np.gradient(ys); n = np.hypot(dx, dy); nx, ny = -dy / n, dx / n
    return Polygon(list(zip(xs + nx * ws / 2, ys + ny * ws / 2)) + list(zip(xs - nx * ws / 2, ys - ny * ws / 2))[::-1]).buffer(0)
# what stands on the river in the film, by the state it shows in: a bridge reaches land at both ends over water, boats float
ON_WATER = {'wei_ancient': [('橫橋', (108.8583, 34.3531), (108.8583, 34.3610)), ('廚城門 bridge', (108.8700, 34.3440), (108.8702, 34.3560)),
                            ('杜郵 boats', (108.7466, 34.3424), (108.7482, 34.3415))],
            'wei_1661': [('town boats', (108.7246, 34.3308), (108.7254, 34.3288))], 'wei_1936': [('town boats', (108.7246, 34.3308), (108.7254, 34.3288))]}
feats = []
for sid, (yc, width, (la_, lb_), basis) in STATES.items():
    wide = (LON >= la_ - .005) & (LON <= lb_ + .005)   # (the water a little past the stretch, in today's river where the two meet)
    water = band(E[wide], yc[wide], width[wide])
    sel = (LON >= la_) & (LON <= lb_)
    north = list(zip(E[sel], y_today[sel] + 1000)); south = list(zip(E[sel], np.maximum(np.minimum(yc, y_today - 500), yc - width / 2 + 30)[sel]))   # (today's whole channel, but within the old river: a tributary cut there flows into it)
    stretch = Polygon(north + south[::-1])
    parts = [('water', water), ('stretch', stretch)]
    if sid == 'wei_ancient':   # two ponds of today under the Qin city (OSM relation 16934768, a 1 ha lake at the palace, and way 1472979241,
        # 0.8 ha, unnamed): nothing puts them there then
        pond = [q for e in els if (e['type'], e['id']) in (('relation', 16934768), ('way', 1472979241)) for q in osmgeo.polys(e, U)]
        parts += [('stretch', g_.buffer(25)) for g_ in pond]
    for kind, g in parts:
        ll = Polygon([tuple(round(v, 6) for v in W(x, y)) for x, y in g.simplify(3).exterior.coords])   # (to 3 m: the band is drawn at 7 m a texel)
        feats.append({'type': 'Feature', 'geometry': mapping(ll), 'properties': {'kind': kind, 'state': sid, 'basis': basis}})
    wet = lambda ll: water.contains(Point(U(*ll)))
    for nm, a_, b_ in ON_WATER[sid]:
        mid = ((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2)
        ok = (not wet(a_) and not wet(b_) and wet(mid)) if 'bridge' in nm or nm == '橫橋' else (wet(a_) or wet(b_)) and wet(mid)
        print(f'  {sid}: {nm} {"ok" if ok else "NOT on the water as it should be"} (ends {wet(a_)}, {wet(b_)}, middle {wet(mid)})')
    if sid != 'wei_ancient': print(f'  {sid}: the river {water.distance(ming):.0f} m off the town wall')
    move = y_today - yc; at = lambda lon: f'{lon}: {np.interp(lon, LON, move):.0f} m'
    print(f'{sid}: moved {", ".join(at(lo) for lo in (108.70, 108.72, 108.75, 108.78, 108.83, 108.86, 108.87, 108.90))}; water {water.area / 1e6:.1f} km², stretch {stretch.area / 1e6:.1f} km²')
out = os.path.join(D, 'research', 'wei_courses.geojson')
json.dump({'type': 'FeatureCollection', 'features': feats}, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
print('->', os.path.relpath(out, D))

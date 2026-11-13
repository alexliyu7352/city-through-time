"""A city's green space and its finer streets, from OpenStreetMap, for the colour film's maquette (engine/mini.js: its base lays
the green in a model's flat green and the streets as fine lines in the plaster): data/green.png, the green areas as a mask the
size of water.png (parks, gardens, grass, woods, recreation grounds; the water drawn over them cleared), and data/streets.json,
the streets below the arterials (secondary to residential) as polylines in model x z with their class. Reads the cached
Overpass answers (pipeline/osm.py <city> green streets) and writes only these two files; prep.py's own files stay as they are.
usage: python -I pipeline/greens.py <city_dir>"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yaml
from PIL import ImageFilter
import layout as LAYOUT, osm, osmgeo
from geo import Frame

if len(sys.argv) < 2: sys.exit(__doc__)
D = sys.argv[1]; C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'))
F = Frame(tuple(C['box']), 1.0 / C['scale']); RAW = LAYOUT.raw(D)
MW = 4096; MH = round(MW * F.size[1] / F.size[0])

def els(theme):
    f = osm.cache_path(RAW, F.area, theme)
    if not os.path.exists(f): print(f'no OSM {theme} answer for this area (pipeline/osm.py {D} {theme}): its file not written'); return None
    return json.load(open(f, encoding='utf-8'))['elements']

# green: every closed way and multipolygon from 400 m² (a pocket lawn smaller than that is no model's green), the water over it cleared
E = els('green')
G = [p for el in E or [] for p in osmgeo.polys(el, F.to_utm.transform) if p.area >= 400]
img = osmgeo.mask(G, F, (MW, MH))
W_ = osmgeo.water(RAW, F.area, F.to_utm.transform)
if W_:
    from PIL import ImageChops
    img = ImageChops.subtract(img, osmgeo.mask(W_, F, (MW, MH)))
if E is not None:
    img.filter(ImageFilter.GaussianBlur(1.0)).save(LAYOUT.data(D, 'green.png'))
    print(f'green: {len(G)} areas -> {LAYOUT.data(D, "green.png")}')

# streets: the ways' polylines in model x z, clipped to the area round the plate (as lines.json's roads)
S = []; E = els('streets')
for el in E or []:
    if el['type'] != 'way' or not el.get('geometry'): continue
    pts = [F.model(*F.to_utm.transform(p['lon'], p['lat'])) for p in el['geometry']]
    S.append({'cls': el.get('tags', {}).get('highway'), 'pts': [[round(x, 5), round(z, 5)] for x, z in pts]})
if E is not None:
    json.dump({'streets': S}, open(LAYOUT.data(D, 'streets.json'), 'w'), separators=(',', ':'))
    print(f'streets: {len(S)} ways -> {LAYOUT.data(D, "streets.json")}')

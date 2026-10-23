"""Sentinel-2 true-colour mosaic of a city box, for the "today, from above" plate texture.
usage: python -I pipeline/satellite.py <city_dir> [--from 2025-04-01 --to 2025-10-31 --cloud 5]
Finds the least-cloudy L2A scenes per MGRS tile through Earth Search (STAC, no login), reads only the box window from each
TCI cloud-optimised GeoTIFF on AWS, reprojects to the city's UTM frame at 10 m, mosaics and writes data/satellite.png
(+ data/satellite.json with scene ids, dates, cloud cover). Licence: Copernicus Sentinel data, free to use with attribution
("Contains modified Copernicus Sentinel data [year]")."""
import json, os, sys, urllib.request
import numpy as np, yaml
import rasterio
from rasterio.warp import reproject, Resampling
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import Frame

D = os.path.abspath(sys.argv[1])
C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'))
args = sys.argv[2:]
opt = lambda k, d: args[args.index(k) + 1] if k in args else d
T0, T1, CLOUD = opt('--from', '2025-04-01'), opt('--to', '2025-10-31'), float(opt('--cloud', '5'))
F = Frame(tuple(C['box']), 1.0 / C['scale'])
w, s, e, n = C['box']

q = {'collections': ['sentinel-2-l2a'], 'bbox': [w, s, e, n], 'datetime': f'{T0}T00:00:00Z/{T1}T23:59:59Z',
     'query': {'eo:cloud_cover': {'lt': CLOUD}}, 'limit': 100}
req = urllib.request.Request('https://earth-search.aws.element84.com/v1/search', data=json.dumps(q).encode(), headers={'Content-Type': 'application/json'})
feats = json.loads(urllib.request.urlopen(req, timeout=120).read())['features']
if not feats: sys.exit('no Sentinel-2 scene matched; widen the dates or the cloud limit')
# one scene per tile: the least cloudy; prefer the date shared by most tiles so the mosaic has one season
by_tile = {}
for f in feats:
    t = f['properties'].get('grid:code'); c = f['properties'].get('eo:cloud_cover', 100)
    if t not in by_tile or c < by_tile[t]['properties']['eo:cloud_cover']: by_tile[t] = f
dates = {}
for f in feats: dates.setdefault(f['properties']['datetime'][:10], set()).add(f['properties']['grid:code'])
best_date = max(dates, key=lambda d: (len(dates[d]), d))
for f in feats:
    if f['properties']['datetime'][:10] == best_date: by_tile[f['properties']['grid:code']] = f
print('tiles:', {t: (f['id'], round(f['properties']['eo:cloud_cover'], 2)) for t, f in by_tile.items()})

RES = 10.0
W = int(round((F.x1 - F.x0) / RES)); H = int(round((F.y1 - F.y0) / RES))
dst_transform = rasterio.transform.from_origin(F.x0, F.y1, RES, RES)
mosaic = np.zeros((3, H, W), np.uint8); filled = np.zeros((H, W), bool)
os.environ.setdefault('AWS_NO_SIGN_REQUEST', 'YES')
for t, f in by_tile.items():
    href = f['assets']['visual']['href']
    with rasterio.open(href) as src:
        # the box in the scene's CRS
        from rasterio.warp import transform_bounds
        b = transform_bounds('EPSG:4326', src.crs, w, s, e, n)
        win = src.window(*b).round_offsets().round_lengths()
        win = win.intersection(rasterio.windows.Window(0, 0, src.width, src.height))
        if win.width <= 0 or win.height <= 0: continue
        data = src.read(window=win)
        win_tr = src.window_transform(win)
    out = np.zeros((3, H, W), np.uint8)
    reproject(data, out, src_transform=win_tr, src_crs=src.crs, dst_transform=dst_transform, dst_crs=f'EPSG:{F.epsg}', resampling=Resampling.bilinear)
    has = out.max(0) > 0
    put = has & ~filled
    mosaic[:, put] = out[:, put]; filled |= put
    print(f'{t}: {f["id"]} window {int(win.width)}x{int(win.height)} -> filled {filled.mean() * 100:.1f}%')
img = Image.fromarray(np.moveaxis(mosaic, 0, -1), 'RGB')
os.makedirs(os.path.join(D, 'build', 'data'), exist_ok=True)   # (pipeline/layout.py)
img.save(os.path.join(D, 'build', 'data', 'satellite.png'))
json.dump({'scenes': {t: {'id': f['id'], 'date': f['properties']['datetime'][:10], 'cloud': f['properties']['eo:cloud_cover']} for t, f in by_tile.items()},
           'res_m': RES, 'size': [W, H], 'credit': f'Contains modified Copernicus Sentinel data {best_date[:4]}'}, open(os.path.join(D, 'build', 'data', 'satellite.json'), 'w'), indent=1)
print('wrote data/satellite.png', W, 'x', H, 'filled', f'{filled.mean() * 100:.1f}%')

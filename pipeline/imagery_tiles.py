"""Higher-resolution imagery for the finale's satellite plate: Esri World Imagery tiles (Web Mercator, z15 ~ 4 m at 34 N)
mosaicked and reprojected onto the plate's UTM frame -> data/satellite_hr.jpg (+ satellite_hr.json).
NOT open data: Esri's terms; for internal pipeline tests only. CREDITS must say so; replace with Sentinel-2 (pipeline/satellite.py)
or licensed imagery before anything is published.
usage: python -I pipeline/imagery_tiles.py cities/<slug> [--z 15] [--res 4]"""
import io, json, math, os, sys, time, urllib.request
import numpy as np, yaml
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import Frame
import local

D = sys.argv[1]; Z = int(sys.argv[sys.argv.index('--z') + 1]) if '--z' in sys.argv else 15
RES = float(sys.argv[sys.argv.index('--res') + 1]) if '--res' in sys.argv else 4.0
C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'))
F = Frame(tuple(C['box']), 1.0 / C['scale'])
URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
CACHE = local.raw('tiles', f'esri_z{Z}')
os.makedirs(CACHE, exist_ok=True)
n = 2 ** Z
def tx(lon): return (lon + 180) / 360 * n
def ty(lat): r = math.radians(lat); return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * n
w, s, e, nn = C['box']; m = .01
X0, X1 = int(tx(w - m)), int(tx(e + m)); Y0, Y1 = int(ty(nn + m)), int(ty(s - m))
print(f'tiles x {X0}..{X1}, y {Y0}..{Y1}: {(X1 - X0 + 1) * (Y1 - Y0 + 1)}')
mosaic = np.zeros(((Y1 - Y0 + 1) * 256, (X1 - X0 + 1) * 256, 3), np.uint8)
got = 0
for y in range(Y0, Y1 + 1):
    for x in range(X0, X1 + 1):
        f = os.path.join(CACHE, f'{y}_{x}.jpg')
        if not os.path.exists(f):
            for k in range(4):
                try:
                    req = urllib.request.Request(URL.format(z=Z, y=y, x=x), headers={'User-Agent': 'city-through-time/0.1 (internal test render)'})
                    data = urllib.request.urlopen(req, timeout=30).read(); open(f, 'wb').write(data); break
                except Exception as ex:
                    time.sleep(2 * (k + 1))
            time.sleep(.05)
        if os.path.exists(f):
            mosaic[(y - Y0) * 256:(y - Y0 + 1) * 256, (x - X0) * 256:(x - X0 + 1) * 256] = np.asarray(Image.open(f).convert('RGB')); got += 1
print('tiles', got)
# reproject: for each output pixel (UTM) -> lon/lat -> mosaic pixel (bilinear)
W = int(round((F.x1 - F.x0) / RES)); H = int(round((F.y1 - F.y0) / RES))
out = np.zeros((H, W, 3), np.uint8)
xs = F.x0 + (np.arange(W) + .5) * RES
for r0 in range(0, H, 256):
    r1 = min(H, r0 + 256); ys = F.y1 - (np.arange(r0, r1) + .5) * RES
    XX, YY = np.meshgrid(xs, ys)
    lon, lat = F.to_wgs.transform(XX, YY)
    px = ((np.asarray(lon) + 180) / 360 * n - X0) * 256 - .5
    lr = np.radians(np.asarray(lat)); py = ((1 - np.log(np.tan(lr) + 1 / np.cos(lr)) / np.pi) / 2 * n - Y0) * 256 - .5
    i0 = np.clip(np.floor(px).astype(int), 0, mosaic.shape[1] - 2); j0 = np.clip(np.floor(py).astype(int), 0, mosaic.shape[0] - 2)
    fu = np.clip(px - i0, 0, 1)[..., None]; fv = np.clip(py - j0, 0, 1)[..., None]
    a = mosaic[j0, i0] * (1 - fu) + mosaic[j0, i0 + 1] * fu; b = mosaic[j0 + 1, i0] * (1 - fu) + mosaic[j0 + 1, i0 + 1] * fu
    out[r0:r1] = (a * (1 - fv) + b * fv).round().clip(0, 255).astype(np.uint8)
Image.fromarray(out).save(os.path.join(D, 'build', 'data', 'satellite_hr.jpg'), quality=86)   # (pipeline/layout.py)
json.dump({'credit': 'Imagery: Esri, Maxar, Earthstar Geographics (Esri World Imagery) — internal test only, not for publication', 'z': Z, 'res_m': RES, 'size': [W, H]},
          open(os.path.join(D, 'build', 'data', 'satellite_hr.json'), 'w'), indent=1)
print('wrote data/satellite_hr.jpg', W, 'x', H)

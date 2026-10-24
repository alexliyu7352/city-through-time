"""The entry page's earth (index.html, site/globe.js): land as a white massing model, the way the films build a city.
usage: python -I tools/portal_land.py      (run again only to change the look; site/land.bin is committed)
Points spread evenly over the sphere (a Fibonacci lattice) and kept where Natural Earth's 1:50m land is (Antarctica left out:
it would only weigh the bottom of the globe). Each point carries two numbers the page turns into a block's height: the ground's
height (ETOPO1, NOAA, read at a quarter degree) and how many people live near it (Natural Earth's 1:10m populated places), so
mountain ranges stand up and the big cities rise like a city's towers do in the films, and glow on the night side.
All three sources are public domain; they are downloaded once into this machine's raw folder (local/config.json).

site/land.bin, little-endian: uint32 count, then per point int16 lat x100, int16 lon x100, uint8 ground (0-255 over 0-6000 m,
square-root scaled), uint8 people (0-255, log scaled). The points are shuffled, so any first part of the file is an even sample
of the whole earth (a phone draws fewer of them)."""
import json, math, os, struct, sys, urllib.request
import numpy as np
import shapely
from shapely.geometry import shape
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline'))
import local

N = 240000                # lattice points over the whole sphere (about 29 % fall on land)
REACH_KM = 140.0          # a place lifts the land within this distance
NE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
ETOPO = 'https://coastwatch.pfeg.noaa.gov/erddap/griddap/etopo180.csv?altitude%5B(-60):15:(90)%5D%5B(-180):15:(180)%5D'   # 0.25 degree
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site', 'land.bin')


def fetch(name, url):
    d = local.raw('naturalearth'); os.makedirs(d, exist_ok=True); f = os.path.join(d, name)
    if not os.path.exists(f): print('downloading', name); urllib.request.urlretrieve(url, f)
    return f


def ground():
    """ETOPO1 heights on a 0.25 degree grid from -60 to 90 latitude: (lats, lons, metres)"""
    rows = open(fetch('etopo1_q.csv', ETOPO), encoding='utf-8').read().splitlines()[2:]
    a = np.array([r.split(',') for r in rows], float)
    lats, lons = np.unique(a[:, 0]), np.unique(a[:, 1])
    return lats, lons, a[:, 2].reshape(len(lats), len(lons))


def main():
    land = shapely.unary_union([shape(f['geometry']) for f in json.load(open(fetch('ne_50m_land.geojson', NE + 'ne_50m_land.geojson'), encoding='utf-8'))['features']])
    i = np.arange(N); y = 1 - 2 * (i + .5) / N
    lat = np.degrees(np.arcsin(y)); lon = np.degrees((i * math.pi * (3 - math.sqrt(5))) % (2 * math.pi)) - 180
    keep = (lat >= -60) & shapely.contains_xy(land, lon, lat)
    lat, lon = lat[keep], lon[keep]
    # the ground: bilinear on the quarter-degree grid
    gl, gn, gz = ground()
    fy = np.interp(lat, gl, np.arange(len(gl))); fx = np.interp(lon, gn, np.arange(len(gn)))
    y0, x0 = np.floor(fy).astype(int), np.floor(fx).astype(int); y1, x1 = np.minimum(y0 + 1, len(gl) - 1), np.minimum(x0 + 1, len(gn) - 1)
    ty, tx = fy - y0, fx - x0
    z = (gz[y0, x0] * (1 - tx) + gz[y0, x1] * tx) * (1 - ty) + (gz[y1, x0] * (1 - tx) + gz[y1, x1] * tx) * ty
    g = np.clip(np.sqrt(np.clip(z, 0, 6000) / 6000) * 255, 0, 255)
    # the people: places within REACH_KM, weighted by their population and falling off with distance
    pl = [f['properties'] for f in json.load(open(fetch('ne_10m_populated_places_simple.geojson', NE + 'ne_10m_populated_places_simple.geojson'), encoding='utf-8'))['features']]
    P = np.radians(np.array([(p['latitude'], p['longitude']) for p in pl])); pop = np.clip(np.array([p['pop_max'] or 0 for p in pl], float), 0, None)   # (-99: unknown)
    la, lo = np.radians(lat), np.radians(lon); people = np.zeros(len(lat))
    for k in range(0, len(lat), 4000):   # (in slices: points x places)
        a, b = la[k:k + 4000, None], lo[k:k + 4000, None]
        d = 6371 * np.arccos(np.clip(np.sin(a) * np.sin(P[None, :, 0]) + np.cos(a) * np.cos(P[None, :, 0]) * np.cos(P[None, :, 1] - b), -1, 1))
        w = np.clip(1 - d / REACH_KM, 0, None) ** 2
        people[k:k + 4000] = (w * pop[None, :]).sum(1)
    p = np.log10(1 + people); p = np.clip(p / np.percentile(p[p > 0], 99.7), 0, 1) * 255
    order = np.random.default_rng(1).permutation(len(lat))   # (any first part is an even sample)
    rec = np.zeros(len(lat), dtype=[('lat', '<i2'), ('lon', '<i2'), ('g', 'u1'), ('p', 'u1')])
    rec['lat'], rec['lon'], rec['g'], rec['p'] = np.round(lat * 100)[order], np.round(lon * 100)[order], np.round(g)[order], np.round(p)[order]
    with open(OUT, 'wb') as f: f.write(struct.pack('<I', len(rec))); f.write(rec.tobytes())
    print(f'land: {len(rec)} points, {os.path.getsize(OUT) / 1e3:.0f} kB -> site/land.bin; ground max {z.max():.0f} m; people > 0 at {(people > 0).mean() * 100:.0f} %')


if __name__ == '__main__':
    main()

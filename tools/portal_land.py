"""The entry page's earth (index.html, site/land.json): land as a white massing model, the way the films build a city.
usage: python -I tools/portal_land.py      (run again only to change the look; the output is committed)
Points spread evenly over the sphere (a Fibonacci lattice) and kept where Natural Earth's 1:110m land is; each gets a height that
grows with the population living near it (Natural Earth's 1:50m populated places), so the world's big cities stand up like a
city's towers do in the films. Natural Earth is public domain (naturalearthdata.com); the two files are downloaded once into this
machine's raw folder (local/config.json)."""
import json, math, os, sys, urllib.request
import numpy as np
from shapely.geometry import shape, Point
from shapely.prepared import prep
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline'))
import local

N = 52000                 # lattice points over the whole sphere (about 29 % fall on land)
REACH_KM = 350.0          # a place lifts the land within this distance
SRC = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site', 'land.json')


def fetch(name):
    d = local.raw('naturalearth'); os.makedirs(d, exist_ok=True); f = os.path.join(d, name)
    if not os.path.exists(f): urllib.request.urlretrieve(SRC + name, f)
    return json.load(open(f, encoding='utf-8'))


def main():
    land = prep(shape({'type': 'GeometryCollection', 'geometries': [g['geometry'] for g in fetch('ne_110m_land.geojson')['features']]}).buffer(0))
    places = [(p['properties']['latitude'], p['properties']['longitude'], p['properties']['pop_max'] or 0) for p in fetch('ne_50m_populated_places_simple.geojson')['features']]
    P = np.radians(np.array([(a, b) for a, b, _ in places])); pop = np.array([c for *_, c in places], float)
    pts = []
    for i in range(N):   # Fibonacci lattice
        y = 1 - 2 * (i + .5) / N; lat = math.degrees(math.asin(y)); lon = math.degrees((i * math.pi * (3 - math.sqrt(5))) % (2 * math.pi)) - 180
        if lat < -60 or not land.contains(Point(lon, lat)): continue   # (no Antarctica: it would only weigh the bottom of the globe)
        la, lo = math.radians(lat), math.radians(lon)
        d = 6371 * np.arccos(np.clip(np.sin(la) * np.sin(P[:, 0]) + np.cos(la) * np.cos(P[:, 0]) * np.cos(P[:, 1] - lo), -1, 1))
        near = d < REACH_KM
        pts.append([lat, lon, float((pop[near] * (1 - d[near] / REACH_KM) ** 2).sum())])
    lift = np.log10(1 + np.array([p[2] for p in pts]))
    lift = np.clip(lift / np.percentile(lift, 99.5), 0, 1)
    out = {'source': 'Natural Earth (public domain): 1:110m land, 1:50m populated places; tools/portal_land.py',
           'points': [[round(a, 2), round(b, 2), round(float(h), 2)] for (a, b, _), h in zip(pts, lift)]}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), separators=(',', ':'))
    print(f'land: {len(pts)} points, {os.path.getsize(OUT) / 1e3:.0f} kB -> site/land.json')


if __name__ == '__main__':
    main()

"""OpenStreetMap features for a city box, through Overpass, cached by query hash in the city's own raw folder
(<raw root>/cities/<slug>/osm/, pipeline/layout.py raw).
usage: python -I pipeline/osm.py <city_dir> [themes...]      (the box is city.yaml's)
Themes: water (areas + rivers), roads (motorway..primary), rail (rail, light rail, subway), historic (historic=*, sites).
Overpass is slow and sometimes down: each theme is one request with a long timeout; a cached answer is never re-fetched."""
import sys, os, json, hashlib, time, urllib.request, urllib.error

ENDPOINTS = ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter', 'https://overpass.private.coffee/api/interpreter']
UA = 'city-through-time/0.1 (data film pipeline; one request per theme, cached)'

THEMES = {
    'water': '''(
  way["natural"="water"]({bbox}); relation["natural"="water"]({bbox});
  way["waterway"="riverbank"]({bbox}); relation["waterway"="riverbank"]({bbox});
  way["landuse"="reservoir"]({bbox}); relation["landuse"="reservoir"]({bbox});
  way["waterway"~"^(river|canal)$"]({bbox});
);''',
    'roads': '''(
  way["highway"~"^(motorway|trunk|primary)$"]({bbox});
  way["highway"~"^(motorway|trunk|primary)_link$"]({bbox});
);''',
    'rail': '''(
  way["railway"~"^(rail|light_rail|subway|monorail)$"]({bbox});
);''',
    'historic': '''(
  nwr["historic"]({bbox});
  nwr["site_type"]({bbox});
  nwr["boundary"="protected_area"]["protect_class"="22"]({bbox});
  nwr["heritage"]({bbox});
);''',
    'places': '''(
  node["place"~"^(city|town|suburb|village|quarter)$"]({bbox});
);''',
    'aeroway': '''(
  way["aeroway"~"^(aerodrome|runway|terminal)$"]({bbox}); relation["aeroway"="aerodrome"]({bbox});
);''',
}


def query(box, theme, timeout=300):
    w, s, e, n = box
    bbox = f'{s},{w},{n},{e}'
    body = THEMES[theme].replace('{bbox}', bbox)
    return f'[out:json][timeout:{timeout}];\n{body}\nout body geom;'


def cache_path(city_raw, box, theme, timeout=300):
    """where the answer for this box and theme is cached in the city's raw folder (the file name carries the query hash, so
    each box has its own)"""
    h = hashlib.sha1(query(box, theme, timeout).encode()).hexdigest()[:12]
    return os.path.join(city_raw, 'osm', f'{theme}_{h}.json')


def fetch(city_raw, box, theme, timeout=300):
    ql = query(box, theme, timeout)
    os.makedirs(os.path.join(city_raw, 'osm'), exist_ok=True)
    out = cache_path(city_raw, box, theme, timeout)
    if os.path.exists(out):
        return out
    last = None
    for attempt in range(4):
        for ep in ENDPOINTS:
            try:
                req = urllib.request.Request(ep, data=ql.encode(), headers={'User-Agent': UA})
                t0 = time.time()
                data = urllib.request.urlopen(req, timeout=timeout + 60).read()
                j = json.loads(data)
                if 'elements' not in j:
                    raise ValueError('no elements')
                tmp = out + '.tmp'
                open(tmp, 'wb').write(data); os.replace(tmp, out)
                print(f'{theme}: {len(j["elements"])} elements from {ep} in {time.time() - t0:.0f}s -> {out}')
                return out
            except Exception as e:   # noqa: BLE001  (any failure: try the next mirror)
                last = f'{ep}: {e}'
                print(f'{theme}: {last}', file=sys.stderr)
        time.sleep(20 * (attempt + 1))
    sys.exit(f'{theme}: all Overpass mirrors failed ({last})')


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import layout   # the city's raw folder and box
    if len(sys.argv) < 2: sys.exit(__doc__)
    city = sys.argv[1]; box = layout.box(city); themes = sys.argv[2:] or list(THEMES)
    for t in themes:
        fetch(layout.raw(city), box, t)

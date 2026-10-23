"""Named geometry from the pipeline's OpenStreetMap cache (all themes under raw/osm)."""
import json, os

def elements(raw_dir):
    d = os.path.join(raw_dir or '', 'osm'); out = []
    for f in (sorted(os.listdir(d)) if os.path.isdir(d) else []):
        if f.endswith('.json'): out += json.load(open(os.path.join(d, f), encoding='utf-8'))['elements']
    return out

def rings(els, name):
    """closed ways / multipolygon outers named `name` -> list of [(lon, lat), ...]"""
    out = []
    for e in els:
        if e.get('tags', {}).get('name') != name: continue
        if e['type'] == 'way' and e.get('geometry'): out.append([(p['lon'], p['lat']) for p in e['geometry']])
        elif e['type'] == 'relation':
            for m in e.get('members', []):
                if m.get('role') != 'inner' and m.get('geometry'): out.append([(p['lon'], p['lat']) for p in m['geometry']])
    return out

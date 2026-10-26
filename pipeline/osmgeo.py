"""Named geometry from a city's cached OpenStreetMap answers (pipeline/osm.py, in the city's raw folder)."""
import json, os

def elements(city_raw, area):
    """the elements of the city's cached answers for its area, every theme (themes in name order)"""
    import osm
    out = []
    for theme in sorted(osm.THEMES):
        f = osm.cache_path(city_raw, area, theme)
        if os.path.exists(f): out += json.load(open(f, encoding='utf-8'))['elements']
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

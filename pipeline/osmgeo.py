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

def polys(el, to_utm):
    """a closed way or a multipolygon relation -> shapely polygons in ground metres (its inner rings as holes)"""
    from shapely.geometry import LineString, Polygon
    from shapely.ops import linemerge, polygonize, unary_union
    out = []
    if el['type'] == 'way' and el.get('geometry') and el['geometry'][0] == el['geometry'][-1]:
        pts = [to_utm(p['lon'], p['lat']) for p in el['geometry']]
        if len(pts) >= 4: out.append(Polygon(pts))
    elif el['type'] == 'relation':
        outers, inners = [], []
        for m in el.get('members', []):
            if m.get('type') != 'way' or not m.get('geometry'): continue
            pts = [to_utm(p['lon'], p['lat']) for p in m['geometry']]
            (outers if m.get('role') != 'inner' else inners).append(LineString(pts))
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

def water(city_raw, area, to_utm):
    """the water the film draws (pipeline/prep.py, data/water.png), in drawing order, as shapely polygons in ground metres: every
    closed water way and multipolygon of the city's OSM water answer from 2000 m² (its islands as holes), named or not, and each
    river's centreline as a band 60 m wide (25 m when it has no name). Whatever keeps houses off the water reads this, so a house
    is never laid on water the film shows (a river mapped as an unnamed multipolygon, as many are, included)."""
    import osm
    from shapely.geometry import LineString, Polygon
    f = osm.cache_path(city_raw, area, 'water')
    if not os.path.exists(f): return []
    out = []
    for el in json.load(open(f, encoding='utf-8'))['elements']:
        tags = el.get('tags', {})
        if tags.get('waterway') in ('river', 'canal') and not (el['type'] == 'way' and el['geometry'][0] == el['geometry'][-1]):
            if tags.get('waterway') == 'river' and el['type'] == 'way' and el.get('geometry'):
                band = LineString([to_utm(p['lon'], p['lat']) for p in el['geometry']]).buffer((60 if 'name' in tags else 25) / 2)
                out += [Polygon(g.exterior) for g in getattr(band, 'geoms', [band])]   # (drawn by its outline)
            continue
        out += [p for p in polys(el, to_utm) if p.area >= 2000]
    return out

def mask(polys, F, size, img=None):
    """polygons (ground metres) drawn into a water mask of `size` (pipeline/prep.py: data/water.png): each outline filled, its
    holes cleared, in order; into `img` (an 'L' image) when given. Unblurred: the caller blurs it as the file it writes"""
    from PIL import Image, ImageDraw
    MW, MH = size; img = img or Image.new('L', (MW, MH), 0); dw = ImageDraw.Draw(img)
    PX = lambda ring: [(F.uv(x, y)[0] * MW, F.uv(x, y)[1] * MH) for x, y in ring]
    for p in polys:
        dw.polygon(PX(p.exterior.coords), fill=255)
        for i in p.interiors: dw.polygon(PX(i.coords), fill=0)
    return img

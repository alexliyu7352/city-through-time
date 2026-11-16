"""How well today's building heights follow real storeys (docs/DATA.md "Correcting building heights"): for any city with a
prepared model, against the OSM buildings that carry building:levels (the building_heights cache, pipeline/osm.py).
    python -I tools/heightcheck.py cities/<slug> [--areas <areas.yaml>]
Each OSM building with a whole storey count, its centroid on the plate, is matched to the prepared footprint it overlaps best
(intersection over union at least 0.5). The storeys table compares the model's height with storeys x 3.2 m per band (3 or fewer,
4-6, 7-12, more than 12): median, quartiles, mean absolute error, and the rank correlation over all, at each stage of the height
layers (pipeline/heights.py; the sidecar build/data/building_heights.json keeps each layer's before and after):
  primary          the adapter's own heights
  after dataset    after height_correction
  final (drawn)    every layer, with a split or replaced outline's own height where the appearance sidecar draws one
  final, not OSM   the final heights of the rows whose height OSM did not set: once the supplement applies OSM storeys, the
                   rows it set agree with their own storeys by construction and say nothing about the rest
A rank correlation under 0.3 before the OSM layer is a WARNING: the heights barely follow the storeys, and the city reads flat
whatever the supplement fixes. Also: explicit OSM heights against the model, the tallest buildings with the layer that set them,
each layer's counts, and with --areas (the format of footprints.py review: areas: [{id, ll: [lon, lat], radius_m}]) each
area's median height at each stage. Printed, and written to build/logs/heightcheck.txt. Reads only; changes nothing."""
import argparse, io, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pipeline'))
import numpy as np
from shapely.affinity import affine_transform
from shapely.geometry import Polygon, Point
from shapely.strtree import STRtree

BANDS = ((1, 3, '<=3'), (4, 6, '4-6'), (7, 12, '7-12'), (13, 400, '>12'))
FLOOR = 3.2
WARN = .3


def model_polygons(M, F):
    inv = [1 / M['scale'], 0, 0, -1 / M['scale'], F.cx, F.cy]   # Frame.model inverted: model x east, z south, about the centre
    return lambda rings: affine_transform(Polygon(rings[0], rings[1:]), inv)


def stages(M, H):
    """{stage: heights by bi}: undo the layers from the last back (each keeps its own before)"""
    final = np.array([b[1] for b in M['b']], float); out = {}; h = final.copy()
    L = H.get('layers')
    if L is None and H.get('changes'): L = {'osm': {'bi': [c['bi'] for c in H['changes']], 'before': [c['primary_height_m'] for c in H['changes']]}}
    L = L or {}
    for name in ('zones', 'osm', 'dataset'):
        if name == 'dataset' and 'dataset' in L: out['after dataset'] = h.copy()
        if name in L: h[np.asarray(L[name]['bi'], int)] = L[name]['before']
    out['primary'] = h
    order = ['primary'] + (['after dataset'] if 'after dataset' in out else [])
    osm_set = np.zeros(len(final), bool)
    if 'osm' in L: osm_set[np.asarray(L['osm']['bi'], int)] = True
    if 'zones' in L: osm_set[np.asarray(L['zones']['bi'], int)] = False
    return {k: out[k] for k in order}, final, osm_set, L


def sample(city, F):
    import heights, layout, osm, osmgeo
    path = osm.cache_path(layout.raw(city), F.area, 'building_heights')
    if not os.path.isfile(path): raise SystemExit(f'heightcheck: no OSM building_heights cache; run pipeline/osm.py {city} building_heights')
    rows = []
    for e in json.load(open(path, encoding='utf-8'))['elements']:
        t = e.get('tags', {})
        if not t.get('building') or t['building'] in ('no', 'construction', 'proposed', 'demolished', 'ruins'): continue
        if t.get('building:part', 'no') != 'no': continue
        lv = heights.levels(t); hm = heights.metres(t.get('height'))
        if lv is None and hm is None: continue
        for p in osmgeo.polys(e, F.to_utm.transform):
            if p.geom_type == 'Polygon' and p.is_valid and p.area > 0 and F.inside(p.centroid.x, p.centroid.y):
                rows.append({'id': f'{e["type"]}/{e["id"]}', 'levels': lv, 'height': hm, 'poly': p})
    return rows


def best(p, tree, P):
    hit = None
    for i in tree.query(p, predicate='intersects'):
        i = int(i); a = P[i].intersection(p).area
        if a > 0 and (hit is None or a / (P[i].area + p.area - a) > hit[0]): hit = (a / (P[i].area + p.area - a), i)
    return hit


def table(say, title, L, h):
    from scipy.stats import spearmanr
    L = np.asarray(L, float); h = np.asarray(h, float)
    if len(L) < 3: say(f'{title}: n={len(L)}, too few'); return None
    say(f'{title}: n={len(L)}')
    for lo, hi, lab in BANDS:
        m = (L >= lo) & (L <= hi)
        if m.any():
            say(f'  {lab:>5}: n {m.sum():5d}  storeys x {FLOOR} {np.median(L[m]) * FLOOR:5.1f}  model median {np.median(h[m]):5.1f}  '
                f'IQR {np.percentile(h[m], 25):5.1f}-{np.percentile(h[m], 75):5.1f}  mean err {np.mean(h[m] - L[m] * FLOOR):+6.1f}  '
                f'MAE {np.mean(np.abs(h[m] - L[m] * FLOOR)):5.1f}')
    rho = float(spearmanr(L, h)[0])
    say(f'    all: mean err {np.mean(h - L * FLOOR):+.1f}  MAE {np.mean(np.abs(h - L * FLOOR)):.1f} m  rank correlation {rho:.2f}')
    return rho


def wmedian(v, w):
    o = np.argsort(v); v, w = np.asarray(v)[o], np.asarray(w)[o]; c = np.cumsum(w)
    return float(v[np.searchsorted(c, c[-1] / 2)])


def main():
    import yaml, layout
    from geo import Frame
    from scipy.stats import spearmanr
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('city'); ap.add_argument('--areas'); A = ap.parse_args()
    city = A.city.rstrip('/'); C = yaml.safe_load(open(os.path.join(city, 'city.yaml'), encoding='utf-8'))
    M = json.load(open(layout.data(city, 'model.json'))); F = Frame(M['box'], M['scale'])
    hp = layout.data(city, 'building_heights.json'); H = json.load(open(hp)) if os.path.isfile(hp) else {}
    S, final, osm_set, L = stages(M, H)
    poly = model_polygons(M, F)
    P = [poly(p[2]) for p in M['p']]; PB = [p[0] for p in M['p']]; tree = STRtree(P)
    drawn = {}   # p index -> [(child polygon, its height)] where the appearance sidecar replaces the outline
    tp = layout.data(city, 'today_footprints.json')
    if os.path.isfile(tp):
        T = json.load(open(tp))
        if T.get('enabled'): drawn = {r['pi']: [(poly(c['rings']), c['height_m'], c['height_source']['source'].startswith('OSM'))
                                                for c in r['children']] for r in T['replacements']}
    added = H.get('fill_gaps', {}).get('counts', {}).get('added', 0)   # OSM gap fill: appended after the primary, OSM heights
    gaps = set(range(len(M['b']) - added, len(M['b']))) if added and 'osm' in L else set()
    osm_set[list(gaps)] = True
    out = io.StringIO()
    def say(s=''): print(s); out.write(s + '\n')
    rows = sample(city, F); matched = []
    for r in rows:
        b = best(r['poly'], tree, P)
        if b and b[0] >= .5:
            i = b[1]; h = final[PB[i]]; own = bool(osm_set[PB[i]])
            if i in drawn: _, h, own = max(drawn[i], key=lambda c: c[0].intersection(r['poly']).area); own = own or bool(osm_set[PB[i]])
            matched.append({**r, 'pi': i, 'bi': PB[i], 'drawn': h, 'osm': own})
    lv = [m for m in matched if m['levels']]
    say(f'heightcheck {os.path.basename(os.path.abspath(city))}: {len(rows)} OSM buildings with storeys or height on the plate, '
        f'{len(matched)} matched (IoU >= 0.5), {len(lv)} with storeys')
    rho = {}
    for name, h in S.items(): rho[name] = table(say, f'\n{name}', [m['levels'] for m in lv], [h[m['bi']] for m in lv])
    table(say, '\nfinal (drawn)', [m['levels'] for m in lv], [m['drawn'] for m in lv])
    ind = [m for m in lv if not m['osm']]
    if 'osm' in L: table(say, '\nfinal, not OSM', [m['levels'] for m in ind], [m['drawn'] for m in ind])
    pre = list(S)[-1]
    if rho.get(pre) is not None and rho[pre] < WARN:
        say(f'\nWARNING: rank correlation {rho[pre]:.2f} under {WARN} at "{pre}": heights barely follow storeys; '
            f'see docs/DATA.md "Correcting building heights"')
    ex = [m for m in matched if m['height']]
    if len(ex) >= 3:
        say(f'\nexplicit OSM heights: n={len(ex)}')
        for name, h in [*S.items(), ('final (drawn)', None)]:
            v = np.array([m['drawn'] if h is None else h[m['bi']] for m in ex]); t = np.array([m['height'] for m in ex])
            say(f'  {name:>14}: MAE {np.mean(np.abs(v - t)):5.1f}  median abs err {np.median(np.abs(v - t)):5.1f}  rank correlation {spearmanr(t, v)[0]:.2f}')
    say('\ntallest (final):')
    changed = {c['bi']: c for c in H.get('changes', [])}
    setter = {bi: 'osm gap fill' for bi in gaps}
    for name in ('dataset', 'osm', 'zones'):
        for bi in (L.get(name) or {}).get('bi', []): setter[bi] = name
    where = {bi: i for i, bi in enumerate(PB)}
    for bi in np.argsort(-final)[:15]:
        bi = int(bi); c = P[where[bi]].centroid
        lon, lat = F.ground_wgs(c.x, c.y); src = setter.get(bi, 'primary')
        tag = f' {changed[bi]["id"]} {changed[bi].get("name") or ""}'.rstrip() if bi in changed else ''
        say(f'  {final[bi]:6.1f} m  bi {bi:7d}  {lat:.5f},{lon:.5f}  {src}{tag}')
    say('\nlayers:')
    for name in ('dataset', 'osm', 'zones'):
        if name in L and 'counts' in L[name]: say(f'  {name}: {json.dumps(L[name]["counts"])}')
    if 'layers' not in H and H.get('counts'): say(f'  osm: {json.dumps(H["counts"])}')
    if H.get('fill_gaps'): say(f'  osm gap fill: {json.dumps(H["fill_gaps"]["counts"])}')
    if not H.get('counts') and not L: say('  none: the primary adapter\'s heights as they are')
    if A.areas:
        say('\nareas (buildings with their centroid inside; median / area-weighted median, m):')
        cen = np.array([[p.centroid.x, p.centroid.y] for p in P]); area = np.array([p.area for p in P])
        for a in yaml.safe_load(open(A.areas, encoding='utf-8'))['areas']:
            x, y = F.to_utm.transform(*a['ll']); idx = np.where(np.hypot(cen[:, 0] - x, cen[:, 1] - y) <= a['radius_m'])[0]
            if not len(idx): say(f'  {a["id"]}: no buildings'); continue
            bis = [PB[i] for i in idx]
            parts = [f'{name} {np.median(h[bis]):.1f} / {wmedian(h[bis], area[idx]):.1f}' for name, h in [*S.items(), ('final', final)]]
            say(f'  {a["id"]} ({len(idx)} buildings, {a["radius_m"]} m): ' + ';  '.join(parts))
    os.makedirs(layout.logs(city), exist_ok=True)
    open(layout.logs(city, 'heightcheck.txt'), 'w', encoding='utf-8').write(out.getvalue())


if __name__ == '__main__':
    main()

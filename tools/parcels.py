"""Whole-building lots for a quarter, laid along its own streets (docs/MODEL.md "Lay out blocks from an old map"): from where houses
stood (the built-up ground of a source map) less what was not houses (landmark sites, gardens, water), and the streets traced on
it, it cuts the ground into blocks, splits a large block by a bent access lane along its long side, then fills each block with
whole courtyard houses (the largest that fit, turned to the nearest street) and rows of shop-houses along the street fronts, each
lot's front to its street. It writes them as a trace (pipeline/citygen.py traced: a `block` feature per lot or row, with its
typ, lot and bearing; a `street` per lane) and a report: a file to look at and approve before it is built, not a city laid anew
on every compile (a change here would move every house of an approved quarter). The geometry is every city's; which types, how
large, how many storeys is the city's own research, given in the spec.
usage: python -I tools/parcels.py cities/<slug> <parcels.yaml>
parcels.yaml:
  id: velabrum                                  # the prefix of every id written
  era: <node id>                                # its landmarks keep their ground (citygen.landmark_site), traced ones too
  domain: [[lon, lat], ..] | research/<f>.geojson   # where houses stood: rings, or a file's polygons (kind: coverage, if it says)
  reserve: [[[lon, lat], ..], .., research/<f>.geojson]   # what stood instead: gardens, open ground, precincts (rings or files)
  water: {osm: <name>, buffer_m: 12}            # optional: a river kept clear
  streets: [research/<trace>.geojson, ..]        # its street features (w_m); and/or inline [{pts: [[lon, lat], ..], w_m}]; none: the era's
  (the era's walls and the shop rows of its streets with shops keep their ground, as citygen keeps it)
  blocks: {max_m2: 10000, min_width_m: 43, lane_m: 4.2, bend_m: 10}
  court: {typ: <house type>, min_m: 13, max_m: 34, min_m2: 240}     # whole courtyard houses (leave out for none)
  front: {typ: <house type>, unit_m: 11, min_unit_m: 6, depth_m: [8, 20], min_m2: 55}   # rows along the street fronts
  basis: "<what the lots rest on>"              # written on every lot (provenance), with its role
  out: research/<id>_parcels.geojson            # default; the report beside it (<id>_parcels_report.json)
Extracted from the trial city of Rome's approved quarters (fit_lot, fit_frontage_run, housing_lots; block_frame's split)."""
import copy, json, math, os, sys
import shapely
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, mapping, shape
from shapely.ops import polygonize, split, unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import citygen, landmarks
from geo import Frame


def pieces(g, kind='Polygon'):
    return [] if g.is_empty else [p for p in (g.geoms if hasattr(g, 'geoms') else [g]) if p.geom_type == kind]


def street_bearing(point, roads):
    line = min(roads, key=lambda r: r.distance(point)); segs = [LineString(s) for s in zip(line.coords, list(line.coords)[1:])]
    (a, b) = min(segs, key=lambda s: s.distance(point)).coords
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def long_axis(poly):
    q = list(poly.minimum_rotated_rectangle.exterior.coords)
    return max((math.dist(a, b), math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))) for a, b in zip(q, q[1:]))[1] % 180


def fit_lot(poly, roads, lo_m, hi_m):
    """the largest whole lot (a rectangle, at three proportions) inside poly, turned to the nearest street: (shape, bearing, w, d)"""
    best = None
    for c in (poly.representative_point(), poly.centroid, Point(shapely.maximum_inscribed_circle(poly, tolerance=.15).coords[0])):
        if not poly.contains(c): continue
        ang = street_bearing(c, roads); loc = affinity.rotate(poly, -ang, origin=c)
        for ratio in (.8, 1.2, 1.65):
            lo, hi = 0.0, min(hi_m, hi_m * ratio)
            for _ in range(14):   # (halving: the widest that still fits)
                w = (lo + hi) / 2; d = w / ratio
                if loc.covers(shapely.box(c.x - w / 2, c.y - d / 2, c.x + w / 2, c.y + d / 2)): lo = w
                else: hi = w
            w, d = lo, lo / ratio
            if min(w, d) < lo_m: continue
            r = shapely.box(c.x - w / 2, c.y - d / 2, c.x + w / 2, c.y + d / 2)
            if best is None or r.area > best[0].area: best = (affinity.rotate(r, ang, origin=c), ang, w, d)
    return best


def fit_run(block, remaining, roads, unit_m, min_unit_m, depths):
    """the longest row of shop-houses along one street front of the block: a common front and back line, N units: (shape, bearing, w, d, N)"""
    ring = list(shapely.orient_polygons(block).exterior.coords); best = None
    for a, b in zip(ring, ring[1:]):
        L = math.dist(a, b)
        if L < 2 * min_unit_m: continue
        mid = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); street, sw = min(roads, key=lambda r: r[0].distance(mid))
        if street.distance(mid) > .05: continue   # (this edge is not on a street: the blocks are cut along the streets' lines)
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])); loc = affinity.rotate(remaining, -ang, origin=a)
        front = a[1] + sw / 2 + .75   # (behind the street's own width)
        for depth in range(int(depths[1]), int(depths[0]) - 1, -1):
            spans = [(a[0] + .02, a[0] + L - .02)]
            for f in (0, .25, .5, .75, 1):   # (the row's ground clear at its front, back and between)
                y = front + depth * f; cut = loc.intersection(LineString([(a[0], y), (a[0] + L, y)]))
                av = [(g.bounds[0], g.bounds[2]) for g in pieces(cut, 'LineString')]
                spans = [(max(x0, p), min(x1, q)) for x0, x1 in spans for p, q in av if min(x1, q) - max(x0, p) >= 2 * min_unit_m]
                if not spans: break
            for x0, x1 in spans:
                r = shapely.box(x0 + .02, front, x1 - .02, front + depth)
                if not loc.covers(r): continue
                span = x1 - x0 - .04; n = max(2, round(span / unit_m)); w = span / n
                if w < min_unit_m: continue
                g = affinity.rotate(r, ang, origin=a)
                if best is None or g.area > best[0].area: best = (g, ang, w, float(depth), n)
    return best


def blocks_of(domain, roads, max_m2, min_width_m, lane_m, bend_m):
    """the domain cut by its streets into blocks; a block over max_m2 and wider than min_width_m split by a bent lane across its
    long side (at varied places, so no two read alike), until none is: (blocks, lanes)"""
    net = unary_union([domain.boundary] + [g.intersection(domain) for g, _ in roads if g.intersects(domain)])
    todo = sorted([p for p in polygonize(net) if domain.covers(p.representative_point()) and p.area > 100], key=lambda g: (-g.area, g.centroid.y, g.centroid.x))
    out, lanes = [], []
    while todo:
        p = todo.pop(); ang = long_axis(p); loc = affinity.rotate(p, -ang, origin=p.centroid); x0, y0, x1, y1 = loc.bounds
        if p.area <= max_m2 or min(x1 - x0, y1 - y0) < min_width_m: out.append(p); continue
        k = len(lanes) + 1; x = x0 + (x1 - x0) * (.43, .57, .48, .38, .61)[k % 5]; bend = min(bend_m, (x1 - x0) * .09) * (1 if k % 2 else -1)
        line = affinity.rotate(LineString([(x, y0 - 5), (x + bend, y0 + (y1 - y0) * .46), (x - bend * .3, y1 + 5)]), ang, origin=p.centroid)
        kids = [q for q in pieces(split(p, line)) if q.area > 1]
        if len(kids) < 2: out.append(p); continue
        for seg in pieces(line.intersection(p), 'LineString'):
            if seg.length >= 8: lanes.append(seg); roads.append((seg, lane_m))
        todo.extend(kids)
    return sorted(out, key=lambda g: (g.centroid.y, g.centroid.x)), lanes


def lots_of(block, roads, court, front):
    """whole courtyard houses first, the largest that fit, then rows along the street fronts, then single fronts in what is left;
    each lot's front to its nearest street: [(shape, bearing, w, d, units, form)], the ground left between them"""
    road_area = unary_union([g.buffer(w / 2 + .6, cap_style=2) for g, w in roads if g.distance(block) <= 70])
    usable = block.difference(road_area); remaining = usable; out = []
    lines = [g for g, _ in roads if g.distance(block) <= 70] or [g for g, _ in roads]
    near = [(g, w) for g, w in roads if g.distance(block) <= 70] or roads
    forms = ([('court', court)] if court else []) + ([('front', front)] if front else [])
    for form, P in forms:
        while True:
            run = fit_run(block, remaining, near, P['unit_m'], P['min_unit_m'], P['depth_m']) if form == 'front' else None
            if run: lot, ang, w, d, n = run
            else:
                lo, hi = (P['min_m'], P['max_m']) if form == 'court' else (P['min_unit_m'], P['depth_m'][1])
                tries = [t for t in (fit_lot(g, lines, lo, hi) for g in pieces(remaining) if g.area >= P['min_m2']) if t and t[0].area >= P['min_m2']]
                if not tries: break
                lot, ang, w, d = max(tries, key=lambda t: t[0].area); n = 1
            c = lot.centroid; a = math.radians(ang)
            fr, bk = Point(c.x + math.sin(a) * d / 2, c.y - math.cos(a) * d / 2), Point(c.x - math.sin(a) * d / 2, c.y + math.cos(a) * d / 2)
            if min(g.distance(fr) for g in lines) > min(g.distance(bk) for g in lines): ang += 180   # (its front to the street)
            out.append((lot, ang % 360, w, d, n, form))
            remaining = remaining.difference(lot.buffer(.65) if form == 'court' else lot)
    return out, usable, remaining


def main():
    import yaml
    if len(sys.argv) != 3: sys.exit(__doc__)
    D = os.path.abspath(sys.argv[1]); S = yaml.safe_load(open(sys.argv[2], encoding='utf-8'))
    C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8')); F = Frame(tuple(C['box']), 1.0 / C['scale'])
    utm = lambda g: shapely.transform(g, lambda q: [F.to_utm.transform(*p) for p in q])
    wgs = lambda g: shapely.transform(g, lambda q: [[round(v, 7) for v in F.to_wgs.transform(*p)] for p in q])
    def shapes(v, kinds=None):   # rings or files of polygons -> UTM polygons
        out = []
        for it in (v if isinstance(v, list) and v and not isinstance(v[0][0], (int, float)) else [v]) if v else []:
            if isinstance(it, str):
                for f in json.load(open(os.path.join(D, it), encoding='utf-8'))['features']:
                    if f['geometry']['type'] in ('Polygon', 'MultiPolygon') and (not kinds or f['properties'].get('kind') in kinds + (None,)): out.append(utm(shape(f['geometry'])))
            else: out.append(Polygon([F.to_utm.transform(*p) for p in it]))
        return out
    pid = S['id']; nodes = {n['id']: n for n in C['film']['nodes']}
    cs = (nodes.get(S.get('era')) or {}).get('city') or {}
    cs = landmarks.templated(citygen.with_trace(copy.deepcopy(cs), F, D), landmarks.library(C, D), f'parcels {pid}')
    sites = [g for L in cs.get('landmarks') or [] for g in citygen.landmark_site(L, F, cs.get('theta_deg', 0))[4]]   # (each landmark's own ground)
    # the ground citygen keeps for the era's walls (a band along them) and for the shop rows of its streets with shops
    walls = [Polygon([F.to_utm.transform(*p) for p in w['ring']]).exterior.buffer(w.get('t_m', 10) * 1.2 + 10) for w in cs.get('walls') or [] if 'ring' in w]
    shops = [LineString([F.to_utm.transform(*p) for p in st['pts']]).buffer(st.get('w_m', 14) / 2 + st.get('shop_depth', 14) + .5, cap_style=2) for st in cs.get('streets') or [] if st.get('shops')]
    reserve = shapes(S.get('reserve')) + sites + walls + shops
    if S.get('water'):
        import layout, osmgeo
        W = S['water']; rings = osmgeo.rings(osmgeo.elements(layout.raw(D), F.area), W['osm'])
        reserve.append(unary_union([Polygon([F.to_utm.transform(*p) for p in r]) for r in rings if len(r) > 3 and r[0] == r[-1]]).buffer(W.get('buffer_m', 12)))
    domain = shapely.make_valid(unary_union(shapes(S['domain'], ('coverage',))).difference(unary_union(reserve) if reserve else Polygon()))
    roads = []
    for it in S.get('streets') or [{'pts': st['pts'], 'w_m': st.get('w_m', 14)} for st in cs.get('streets') or []]:   # (none given: the era's own)
        if isinstance(it, str):
            for f in json.load(open(os.path.join(D, it), encoding='utf-8'))['features']:
                pr = f['properties']; m = pr.get('model') if isinstance(pr.get('model'), dict) else pr
                if pr.get('kind') == 'street' and f['geometry']['type'] == 'LineString': roads.append((utm(shape(f['geometry'])), float(m.get('w_m', 8))))
        else: roads.append((LineString([F.to_utm.transform(*p) for p in it['pts']]), float(it.get('w_m', 8))))
    if not roads: sys.exit('parcels: no streets: a quarter is laid along its streets (streets: a trace file, or inline)')
    B = {'max_m2': 10000, 'min_width_m': 43, 'lane_m': 4.2, 'bend_m': 10, **(S.get('blocks') or {})}
    blocks, lanes = blocks_of(domain, roads, B['max_m2'], B['min_width_m'], B['lane_m'], B['bend_m'])
    court = {'min_m': 13, 'max_m': 34, 'min_m2': 240, **S['court']} if S.get('court') else None
    front = {'unit_m': 11, 'min_unit_m': 6, 'depth_m': [8, 20], 'min_m2': 55, **S['front']} if S.get('front') else None
    feats, report = [], {'id': pid, 'domain_m2': round(domain.area), 'blocks': [], 'lanes': len(lanes)}
    for i, seg in enumerate(lanes, 1):
        feats.append({'type': 'Feature', 'geometry': mapping(wgs(seg)), 'properties': {'id': f'{pid}_lane_{i:03d}', 'kind': 'street', 'w_m': B['lane_m'],
                      'provenance': {'role': 'access lane splitting a large block (its place and bends estimated)', 'basis': S.get('basis', '')}}})
    for bi, blk in enumerate(blocks, 1):
        lots, usable, left = lots_of(blk, roads, court, front)
        for li, (g, ang, w, d, n, form) in enumerate(lots, 1):
            P = court if form == 'court' else front
            role = 'a whole courtyard house, the largest that fits here, turned to its street' if form == 'court' else (f'a row of {n} shop-houses on one street front' if n > 1 else 'a single shop-house on a street front')
            feats.append({'type': 'Feature', 'geometry': mapping(wgs(g)), 'properties': {'id': f'{pid}_b{bi:03d}_{li:02d}', 'kind': 'block', 'typ': P['typ'],
                          'lot': [round(w, 2), round(d, 2)], 'theta_deg': round(ang, 2), 'empty': 0,
                          'provenance': {'role': role, 'parent_block': f'{pid}_b{bi:03d}', 'buildings': n, 'basis': S.get('basis', '')}}})
        r_ = max([shapely.maximum_inscribed_circle(p, tolerance=.2).length for p in pieces(left) if p.area > 10] or [0])
        report['blocks'].append({'id': f'{pid}_b{bi:03d}', 'usable_m2': round(usable.area), 'built_m2': round(sum(x[0].area for x in lots)),
                                 'houses': sum(x[4] for x in lots), 'widest_ground_left_m': round(r_, 1)})
    sizes = {(round(f['properties']['lot'][0]), round(f['properties']['lot'][1])) for f in feats if f['properties']['kind'] == 'block'}
    report.update(houses=sum(b['houses'] for b in report['blocks']), lot_sizes=len(sizes), bearings=len({round(f['properties']['theta_deg'] / 5) for f in feats if f['properties']['kind'] == 'block'}),
                  built_share=round(sum(b['built_m2'] for b in report['blocks']) / max(1, sum(b['usable_m2'] for b in report['blocks'])), 3))
    out = os.path.join(D, S.get('out') or f'research/{pid}_parcels.geojson')
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(report, open(os.path.splitext(out)[0] + '_report.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"parcels: {len(blocks)} blocks, {report['lanes']} lanes, {report['houses']} houses on {len(feats) - len(lanes)} lots "
          f"({report['lot_sizes']} sizes, {report['bearings']} bearings; {report['built_share']:.0%} of the usable ground built) -> {os.path.relpath(out, ROOT)}")


if __name__ == '__main__':
    main()

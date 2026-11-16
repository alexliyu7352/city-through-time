"""Level the ground under the landmarks on a slope (docs/MODEL.md "Landmarks of any region"). Their builders cut into the hill and
filled below, or built a terrace, to stand them on level ground; on the plate the hill ran on under them, so the slope crossed
their walls (sunk on one side, standing out on the other) or they stood on a platform taller than themselves. The film is not
the land as it was, metre by metre, any more than its buildings are: what it needs is a building standing square on ground that
looks right. So the relief is levelled once, for the whole film, before anything is built on it: the plate, the period cities,
today's buildings and every check read it as they read any terrain, and nothing moves while the film plays.
Each landmark on a slope gets a pad: its rectangle and PAD_M round, level half-way between the highest and the lowest ground
under it (as much cut as fill), the hill coming back to its own height over a margin round it (the plate's mesh is about 36 m:
the edge is a slope, never a wall). Pads that overlap, in any period (a church and its forecourt, the same ground built on again,
a square laid over an older forecourt), are one: one level for all of them. A pad of less than MIN_M cut or fill is left to the
landmark's own foundation (site: raised or cut); a landmark of parts (site: parts) steps down the hill part by part, an arcade
(kind: arches) follows the ground, one in the river stands on its bed. Where two pads lie near but apart, the ground between them
is a slope, and what stands on it is seated as anything on a slope is. The ground is level from the start of the film, before
the landmark that needs it is built.
A period city can declare a pad of its own (city.pads: a region, or the landmarks that share one ground): it is levelled whatever
its cut or fill, at half-way between the highest and the lowest ground of what it declares, and over every cell of the plate's mesh
that ground touches (and the relief's texels those cells' corners read), so the plate as the engine draws it is flat under all of
it, never leaning to a corner out on its bank: the ground a quarter's doors and its streets share, on a plain whose relief the
threshold above leaves to each building's own foundation. Overlapping a pad of a landmark, it is one with it. Declared pads take the
ground as declared: no share of water or site keeps one out.
compile levels the relief on every run (grade()): terrain16.png and terrain.png are rewritten, the relief as prepared kept beside
them (*_ungraded) and levelled from each time; today's buildings over a pad are seated on it again in model.json (the seats as
prepared kept as model_ungraded.json). terrain.json (graded) and model.json (graded) mark files compile wrote, so one written
again by terrain.py or prep.py is taken as the new relief or seats as prepared. terrain_true16.png keeps the land as measured.
usage: uv run python -I pipeline/grade.py cities/<slug>      (the pads compile will lay, with their levels: nothing is written)"""
import copy, json, math, os, shutil, sys
import numpy as np
import yaml
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import citygen, landmarks, terrainio
import layout as LAYOUT
from geo import Frame

PAD_M = 10.0      # level ground round the landmarks' rectangles (their walls never stand at the edge of the cut)
MARGIN_M, RAMP = 45.0, 8.0   # the hill comes back over this much round the pad (a little more than the plate's mesh cell), or over RAMP times
# the cut or fill where that is wider (a deep cut's bank as steep as a shallow one's: a house beside the pad stands on a slope, not a cliff)
WET = .1          # a landmark whose rectangle is this share water (data/water.png) stands in or over the river (a bridge, a mill, a quay): its ground is the river's, never levelled
MIN_M = 1.5       # less cut or fill than this is left to the landmark's own foundation (site: cut lets it in half-way): levelling it changes nothing a viewer sees, only what stands round it
REACH_M = 100.0   # how far beyond a pad's margin the plate can change (a mesh cell, ~36 m, and a relief texel round it): today's buildings within it are seated again
DEEP_M = 15.0     # cut or fill deeper than this (metres as measured) is listed: a building that steps down the hill (site: parts), or one standing where the hill is too steep for it


def frame(C):
    return Frame(tuple(C['box']), 1.0 / C['scale'], near=[b for b in [((C.get('terrain') or {}).get('context') or {}).get('box')] if b])


def pads(C, F, D, joined=False):
    """a pad for each landmark on a slope: [{'landmarks': ['<node>/<id>'], 'poly': UTM polygon (its rectangle, PAD_M round)}].
    joined: the nodes' cities already hold their traced features (compile joins them first: citygen.traced)"""
    from shapely.geometry import Point, Polygon
    lib, out = landmarks.library(C, D), []
    wm = np.asarray(Image.open(LAYOUT.data(D, 'water.png')).convert('L')) if os.path.exists(LAYOUT.data(D, 'water.png')) else None
    def wet(poly):   # its share of water, sampled every few metres
        if wm is None: return 0.0
        x0, y0, x1, y1 = poly.bounds; X, Y = np.meshgrid(np.linspace(x0, x1, 12), np.linspace(y0, y1, 12)); X, Y = X.ravel(), Y.ravel()
        k = [(a, b) for a, b in zip(X, Y) if poly.contains(Point(a, b))]
        if not k: return 0.0
        hh, ww = wm.shape; u = [(a - F.x0) / (F.x1 - F.x0) for a, _ in k]; v = [(F.y1 - b) / (F.y1 - F.y0) for _, b in k]
        return float(np.mean([wm[min(hh - 1, max(0, int(vv * (hh - 1)))), min(ww - 1, max(0, int(uu * (ww - 1))))] > 127 for uu, vv in zip(u, v)]))
    for node in C['film']['nodes']:
        if not node.get('city'): continue
        lab = f'node {node["id"]}'
        cs = copy.deepcopy(node['city']); cs = landmarks.checked(landmarks.templated(cs if joined else citygen.with_trace(cs, F, D), lib, lab), lab)
        for li, L in enumerate(cs.get('landmarks') or []):
            if not isinstance(L, dict) or L.get('kind') not in landmarks.KINDS or L.get('site') == 'parts': continue   # (parts step down the hill, each on its own ground)
            if L['kind'] == 'arches': continue   # (arches span: a bridge over the river, an aqueduct along the ground)
            x, y, th, L2, _ = citygen.landmark_site(L, F, cs.get('theta_deg', 0))
            x0, y0, x1, y1 = landmarks.bounds(L2); P = citygen.Builder.frame(x, y, th)
            rect = Polygon([P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)])
            if wet(rect) >= WET: continue
            out.append({'landmarks': [f'{node["id"]}/{L2.get("id") or L2.get("name") or li}'], 'poly': rect.buffer(PAD_M), 'rect': rect, 'site': L2.get('site')})
    return out


def declared(C, F, D, shape, joined=False):
    """the pads the period cities declare (city.pads, docs/MODEL.md "Landmarks of any region"), each levelled whatever its cut or
    fill: {id, region} (a region as grounds write it: a ring of lon, lat, or rings) or {id, landmarks: [ids of the city's landmarks]}
    (their rectangles PAD_M round, the hull of them all: one ground, the lanes between them on it). shape: the relief's (rows,
    columns). -> [{'landmarks', 'declared': ['<node>/<id>'], 'area': the ground declared, 'poly': what is levelled for it to lie
    flat on the plate's mesh (flat())}] (UTM). joined: as pads()"""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    lib, out = None, []
    for node in C['film']['nodes']:
        city = node.get('city')
        if not city or not city.get('pads'): continue
        lab, cs = f'node {node["id"]}', None
        for i, d in enumerate(city['pads']):
            pid = d.get('id') or f'pad{i}'; name = f'{node["id"]}/{pid}'; d.get('basis')   # (basis: why this ground is level; read, not used)
            if ('region' in d) == ('landmarks' in d):
                raise SystemExit(f'grade: {lab}: pads[{i}] ({pid}): give the ground it levels as region: [[lon, lat], ..] or as landmarks: [<ids>], one of them (docs/MODEL.md)')
            if 'region' in d:
                if isinstance(d['region'], str): raise SystemExit(f'grade: {lab}: pads[{i}] ({pid}): region: a ring of [lon, lat] (or rings), not a name')
                area, who = citygen.region_utm(F, d['region']), [name]
            else:
                if cs is None:
                    lib = lib or landmarks.library(C, D)
                    cs = copy.deepcopy(city); cs = landmarks.checked(landmarks.templated(cs if joined else citygen.with_trace(cs, F, D), lib, lab), lab)
                by = {}
                for li, L in enumerate(cs.get('landmarks') or []):
                    if isinstance(L, dict): by.setdefault(L.get('id') or L.get('name') or li, L)
                miss = [k for k in d['landmarks'] if k not in by]
                if miss: raise SystemExit(f'grade: {lab}: pads[{i}] ({pid}): no landmark {", ".join(map(str, miss))} in this city (its landmarks\' id)')
                rects = []
                for k in d['landmarks']:
                    x, y, th, L2, polys = citygen.landmark_site(by[k], F, cs.get('theta_deg', 0))
                    if by[k].get('kind') in landmarks.KINDS:
                        x0, y0, x1, y1 = landmarks.bounds(L2); P = citygen.Builder.frame(x, y, th)
                        rects.append(Polygon([P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)]))
                    else: rects.append(unary_union(polys))   # (the generator's own kinds: the ground it keeps clear)
                area, who = unary_union([r.buffer(PAD_M) for r in rects]).convex_hull, [f'{node["id"]}/{k}' for k in d['landmarks']]
            if area.is_empty or area.area <= 0: raise SystemExit(f'grade: {lab}: pads[{i}] ({pid}): its ground is empty')
            out.append({'landmarks': who, 'declared': [name], 'area': area, 'poly': flat(area, F, shape)})
    return out


def flat(area, F, shape):
    """the ground to level so that the plate as the engine draws it (terrainio.plate_mesh: a mesh of flat triangles through the
    relief) is flat over all of area (UTM): every cell of the mesh it touches, and round them the relief's texels the cells'
    corners read (bilinear: a texel each way; the cells and the texels are both square to the frame, so a square round them)"""
    import shapely
    PW, PD = F.size; nx = terrainio.NX; nz = int(math.floor(nx * PD / PW + .5)); cw, cd = (PW + .1) / nx / F.scale, (PD + .1) / nz / F.scale
    ox, oy = F.cx - (PW + .1) / 2 / F.scale, F.cy + (PD + .1) / 2 / F.scale   # (the mesh's north-west corner, UTM: model z runs south)
    x0, y0, x1, y1 = area.bounds
    I, J = np.meshgrid(np.arange(max(0, int((x0 - ox) // cw)), min(nx - 1, int((x1 - ox) // cw)) + 1),
                       np.arange(max(0, int((oy - y1) // cd)), min(nz - 1, int((oy - y0) // cd)) + 1))
    cells = shapely.box(ox + I.ravel() * cw, oy - (J.ravel() + 1) * cd, ox + (I.ravel() + 1) * cw, oy - J.ravel() * cd)
    cells = cells[shapely.intersects(cells, area)]
    h, w = shape; tx, ty = (F.x1 - F.x0) / (w - 1), (F.y1 - F.y0) / (h - 1)
    return shapely.union_all(np.append(cells, area)).buffer(max(tx, ty), join_style='mitre')


def _sample(poly, ground):   # the ground under poly every ~8 m (its centre when it is smaller)
    import shapely
    x0, y0, x1, y1 = poly.bounds; n_ = max(4, int(max(x1 - x0, y1 - y0) / 8))
    X, Y = np.meshgrid(np.linspace(x0, x1, n_), np.linspace(y0, y1, n_)); ins = shapely.contains_xy(poly, X, Y)
    return np.array([ground(a, b) for a, b in zip(X[ins], Y[ins])] or [ground(poly.centroid.x, poly.centroid.y)])


def measure(PD, ground):
    """each pad's level from the ground as the plate draws it (ground(x, y): metres above the terrain's minimum at a UTM point):
    height_m (that level), cut_m, fill_m, margin_m; the pads under MIN_M of cut and fill are left out, but for a declared one
    (declared()): its level from the ground it declares, its cut and fill over all that is levelled for it"""
    out = []
    for p in PD:
        poly = p['poly']; g = _sample(p['area'] if p.get('declared') else poly, ground)
        H = float(g.max() + g.min()) / 2
        if p.get('declared'): g = np.append(g, _sample(poly, ground))
        cut, fill = float(g.max()) - H, H - float(g.min())
        if max(cut, fill) < MIN_M and not p.get('declared'): continue
        out.append({**p, 'height_m': H, 'cut_m': round(cut, 1), 'fill_m': round(fill, 1), 'margin_m': max(MARGIN_M, RAMP * max(cut, fill)), 'area_m2': round(poly.area)})
    return out


def blocks(PD, ground, DP=()):
    """the pads levelled: those that need it (measure) and the declared ones DP (declared()), the ones overlapping joined into one
    (any period: one ground under all of them), measured again as one (declared, if one of them is). A landmark that needs none of
    its own but overlaps one pad stands on it (the pad takes it in): beside it, it would stand on the pad's bank, steeper than the
    hill; one between two pads stays on its own ground"""
    from shapely.ops import unary_union
    rows = measure(PD, ground) + measure(DP, ground); up = list(range(len(rows))); need = {l for p in rows for l in p['landmarks']}
    def top(i):
        while up[i] != i: i = up[i]
        return i
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            if rows[i]['poly'].intersects(rows[j]['poly']): up[top(i)] = top(j)
    groups = {}
    for i in range(len(rows)): groups.setdefault(top(i), []).append(rows[i])
    joined = [unary_union([q['poly'] for q in g]) for g in groups.values()]
    for p in PD:
        if p['landmarks'][0] in need: continue
        hit = [k for k, u in enumerate(joined) if u.intersects(p['poly'])]
        if len(hit) == 1: list(groups.values())[hit[0]].append(p)
    def one(g):
        p = {'landmarks': sorted(sum((q['landmarks'] for q in g), [])), 'poly': unary_union([q['poly'] for q in g])}
        if any(q.get('declared') for q in g):   # (its level from the ground declared and the landmarks' pads with it)
            p.update(landmarks=sorted(set(p['landmarks'])), declared=sorted(sum((q.get('declared', []) for q in g), [])),   # (a landmark it names may have a pad of its own too)
                     area=unary_union([q['area'] if q.get('declared') else q['poly'] for q in g]))
        return p
    out = measure([one(g) for g in groups.values()], ground)
    out.sort(key=lambda p: p['landmarks'])
    return out


def level(arr, rows, F):
    """the relief (metres above the minimum, rows north first) levelled under the pads rows: level inside each, the hill back over
    its margin (smoothstep). Where two margins meet, the pad nearer (the larger share) is laid last, over the other"""
    import shapely
    h, w = arr.shape; bw, bl, sw, sl = (np.zeros_like(arr) for _ in range(4))   # (each texel's two pads with the largest shares: share, level)
    for p in rows:
        poly, mg = p['poly'], p['margin_m']; bx0, by0, bx1, by1 = poly.buffer(mg).bounds
        i0, i1 = max(0, int((bx0 - F.x0) / (F.x1 - F.x0) * (w - 1))), min(w - 1, int(math.ceil((bx1 - F.x0) / (F.x1 - F.x0) * (w - 1))))
        j0, j1 = max(0, int((F.y1 - by1) / (F.y1 - F.y0) * (h - 1))), min(h - 1, int(math.ceil((F.y1 - by0) / (F.y1 - F.y0) * (h - 1))))
        if i1 < i0 or j1 < j0: continue
        I, J = np.meshgrid(np.arange(i0, i1 + 1), np.arange(j0, j1 + 1))
        TX, TY = F.x0 + I / (w - 1) * (F.x1 - F.x0), F.y1 - J / (h - 1) * (F.y1 - F.y0)   # (the texels as terrainio.bilinear reads them)
        d = shapely.distance(poly.boundary, shapely.points(TX, TY)) * np.where(shapely.contains_xy(poly, TX, TY), -1, 1)
        s = np.clip(d / mg, 0, 1); k = np.where(d <= 0, 1.0, 1 - s * s * (3 - 2 * s)).astype(arr.dtype)
        win = np.s_[j0:j1 + 1, i0:i1 + 1]; B, BL, S2, SL = bw[win], bl[win], sw[win], sl[win]; H = p['height_m']
        up = k > B; second = ~up & (k > S2)
        S2[:] = np.where(up, B, np.where(second, k, S2)); SL[:] = np.where(up, BL, np.where(second, H, SL))
        B[:] = np.where(up, k, B); BL[:] = np.where(up, H, BL)
    out = arr + sw * (sl - arr)
    return out + bw * (bl - out)


def zone(rows):
    """the ground the pads rows level and their banks (UTM, prepared), or None: citygen lets nothing into it (Builder.graded)"""
    import shapely
    if not rows: return None
    z = shapely.union_all([p['poly'].buffer(p['margin_m']) for p in rows]); shapely.prepare(z)
    return z


def reseat(M, PL0, PL1, rows, F, tex):
    """today's buildings (model.json, as prep seated them on the plate PL0) over the pads rows seated again on the levelled plate
    PL1 as prep seats them (prep.py seat: the base on the lowest ground under the footprint, the height above the ground at its
    centre kept) -> how many"""
    import shapely
    S = F.scale; zone = shapely.union_all([shapely.Polygon([F.model(*q) for q in p['poly'].buffer(p['margin_m'] + REACH_M).exterior.coords]) for p in rows])
    shapely.prepare(zone); n = 0
    for e in M['p']:
        hh, rings, base = e[1], e[2], e[3]
        if len(rings[0]) < 3: continue
        r0 = shapely.Polygon(rings[0])
        if not zone.intersects(r0): continue
        c = r0.centroid; c = (c.x, c.y)
        h0 = hh - (PL0(*c) * S * tex - base)   # (its height above the ground at its centre, the foundation prep added taken off)
        mid = PL1(*c) * S * tex; b1 = min(mid, PL1.lowest(rings[0]) * S * tex)
        e[1], e[3] = round(h0 + mid - b1, 6), round(b1, 6); n += 1
    return n


def grade(C, F, D, arr0, tj, tex):
    """level the relief for the film (compile, after the traced features are joined): arr0 the relief as prepared (terrainio.load
    ungraded), tj its terrain.json. Rewrites the terrain files and today's seats (see the module's doc), or puts back those as
    prepared where nothing needs levelling -> (the relief levelled, tj, the pads)"""
    data = lambda n: LAYOUT.data(D, n)
    keep = {n: data(n.replace('.', '_ungraded.', 1)) for n in ('terrain16.png', 'terrain.png', 'model.json')}
    PL0 = terrainio.plate_mesh(arr0, *F.size)
    ground = lambda x, y: PL0(*F.model(x, y))
    rows = blocks(pads(C, F, D, joined=True), ground, declared(C, F, D, arr0.shape, joined=True))
    Mp = data('model.json'); M = json.load(open(Mp, encoding='utf-8')) if os.path.exists(Mp) else None
    t_graded, m_graded = 'graded' in tj, bool(M and M.get('graded'))
    if not rows:   # (nothing to level: the relief and the seats as prepared, put back where a run before levelled them)
        if t_graded:
            for n in ('terrain16.png', 'terrain.png'):
                if os.path.exists(keep[n]): shutil.move(keep[n], data(n))
            tj.pop('graded'); json.dump(tj, open(data('terrain.json'), 'w'), indent=1)
        if m_graded and os.path.exists(keep['model.json']): shutil.move(keep['model.json'], Mp)
        return arr0, tj, rows
    if not t_graded:   # (the files as terrain.py wrote them: kept as the relief as prepared)
        for n in ('terrain16.png', 'terrain.png'):
            if os.path.exists(data(n)): shutil.copy2(data(n), keep[n])
    span = tj['max_m'] - tj['min_m']; arr = level(arr0, rows, F)
    terrainio.write16(D, arr, 0.0, span)
    Image.fromarray((arr / max(1e-6, span) * 255).clip(0, 255).astype(np.uint8)).save(data('terrain.png'))
    tj['graded'] = {'pads': [{'landmarks': p['landmarks'], 'height_m': round(p['height_m'] + tj['min_m'], 2), 'cut_m': p['cut_m'], 'fill_m': p['fill_m'], 'area_m2': p['area_m2'],
                              **({'declared': p['declared']} if p.get('declared') else {})} for p in rows]}
    json.dump(tj, open(data('terrain.json'), 'w'), indent=1)
    if M is not None:
        if m_graded: M = json.load(open(keep['model.json'], encoding='utf-8'))
        else: shutil.copy2(Mp, keep['model.json'])   # (as prep.py wrote it: the seats as prepared)
        reseat(M, PL0, terrainio.plate_mesh(arr, *F.size), rows, F, tex); M['graded'] = True
        json.dump(M, open(Mp, 'w'), separators=(',', ':'))
    return arr, tj, rows


def main():
    D = os.path.abspath(sys.argv[1])
    C = yaml.load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'), Loader=getattr(yaml, 'CSafeLoader', yaml.SafeLoader))
    F = frame(C)
    arr, tj = terrainio.load(D, ungraded=True)
    if arr is None: sys.exit('grade: no terrain (pipeline/terrain.py first)')
    PL = terrainio.plate_mesh(arr, *F.size)
    PD, DP = pads(C, F, D), declared(C, F, D, arr.shape)
    rows = blocks(PD, lambda x, y: PL(*F.model(x, y)), DP)
    print(f'grade: {len(rows)} pad(s) for {sum(len(p["landmarks"]) for p in rows)} landmarks ({len(PD)} on a slope; the rest under {MIN_M:g} m left to their own foundations)'
          + (f'; {len(DP)} declared' if DP else ''))
    for p in sorted(rows, key=lambda p: -max(p['cut_m'], p['fill_m'])):
        deep = max(p['cut_m'], p['fill_m']) > DEEP_M
        print(f'  {", ".join(p["landmarks"])}: {p["area_m2"]:,} m2 at {p["height_m"] + tj["min_m"]:.1f} m, cut {p["cut_m"]:g} m, fill {p["fill_m"]:g} m'
              + (f'  (declared: {", ".join(p["declared"])})' if p.get('declared') else '')
              + (f'  DEEP (over {DEEP_M:g} m: does it step down the hill, site: parts, as the sources say? or stand where the hill is too steep for it?)' if deep else ''))


if __name__ == '__main__':
    main()

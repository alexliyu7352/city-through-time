"""An early Christian or Romanesque basilica (Old St Peter's, the Lateran, St Paul's outside the walls, Sant'Apollinare in
Classe, a Romanesque church ...) as a detailed model: the film's long halls and apses drawn as the building's outside.
  a long hall with aisles   the tall nave with its clerestory windows over the aisles, each aisle stepping down under its own
                            lean-to roof, windows in the outer walls; the entrance front with a door into the nave and each
                            aisle, a string course over them and windows above
  a hall without aisles     (a transept, a single-naved church) its walls with a row of windows high up, its gable ends
  a half dome or a dome     (an apse) its drum, and its roof: a cone of tiles or a dome
Gabled and lean-to roofs of Roman tiles (rows of cover tiles over the pans, ridge tiles), a plinth and an eaves cornice on every
wall, raking cornices up the gables. Openings are real: their sides and a back a wall's depth in, dark (seen into). The inside
(the colonnades between nave and aisles, the trusses) is not built: no viewpoint sees it.
Each part of a `parts` landmark keeps its own objects. Long halls in a line (the same width, height and aisles, end to end: one
nave cut in segments for the film's story) are built as one hall and cut where the segments meet, so the windows, cornices and
tile rows run on across the cut and a gable stands only at the true ends. Objects, for each part id:
  <id>             its walls and their mouldings
  <id>_roof        its roofs
  <id>_openings    the dark of its doors and windows (none when it has none)
Every size the landmark does not give is an estimate, a default here, and the part it shapes says so on the page. An opening
another part covers (a transept's windows behind the aisles, behind the apse) is not drawn."""
import math

import bmesh
from mathutils import Matrix, Vector

import kit

DEFAULT = {
    'parts': [],                 # the landmark's parts as the film has them (from_landmark): long halls, domes
    'bay_m': 4.5,                # the windows' rhythm along a wall (the landmark's bay_m)
    'aisle_pitch_deg': 14.0,     # estimate: the aisles' lean-to roofs (Roman tile roofs: low pitches)
    'aisle_step_m': 1.6,         # estimate: how far an inner aisle's wall stands above the roof of the aisle outside it (0, with
                                 # a lower aisle pitch: nearly one slope over all the aisles, as the film's generator draws them)
    'clerestory_min_m': 5.0,     # the least nave wall kept above the aisles' roofs (pitch and step shrink to keep it)
    'roof_t_m': .3,              # a roof's thickness at its edges
    'wall_m': 1.2,               # estimate: the walls' depth at the openings
    'window_share': .5,          # estimate: a window's width as a share of its bay
    'tile_m': .6,                # estimate: the spacing of the rows of cover tiles (imbrices) down a roof
    'doors': True,               # the entrance front: the front end of the hall with aisles, a door into the nave and each aisle
    'door_m': [3.4, 5.2],        # estimate: the nave's door, width and height (the aisles' are .7 of it)
    'front_windows': 3,          # estimate: windows in the nave's front above the doors
    'plinth_m': .62,             # estimate: the base course's height
    'cornice_m': .8,             # estimate: the eaves cornice's height (the step walls' about half)
    'apse_seg': 48,              # facets round a whole drum (a half drum half as many)
}


def from_landmark(L):
    """the film's landmark (kind parts, or a long hall or a dome alone) as this spec: its parts, and the bay of its first hall"""
    parts = [dict(q) for q in L['parts']] if L.get('kind') == 'parts' else [{**L, 'id': L.get('id') or 'hall', 'at': [0.0, 0.0], 'theta_deg': 0.0}]
    out = {'parts': [q for q in parts if q.get('kind') in ('long_hall', 'dome')]}
    for q in out['parts']:
        if q.get('repeat'): raise SystemExit(f'basilica: part {q.get("id")}: repeat is not drawn by this kind')
        if not q.get('id'): raise SystemExit('basilica: every part needs an id (its objects are named by it)')
    halls = [q for q in out['parts'] if q['kind'] == 'long_hall']
    if halls and halls[0].get('bay_m'): out['bay_m'] = float(halls[0]['bay_m'])
    return out


# ---- for the kit: walls with openings, mouldings along a line, tiled roof slopes, free-standing columns

def wall_frame(o, along, out):
    """the Matrix of a wall's frame (x along it, y out of its face, z up) with its origin at o"""
    return Matrix(((along[0], out[0], 0, o[0]), (along[1], out[1], 0, o[1]), (0, 0, 1, o[2] if len(o) > 2 else 0.0), (0, 0, 0, 1)))


def _face(bm, vs, mat):
    """a face on the vertices vs (a vertex repeated next to itself dropped), or None where there is none to make"""
    out = []
    for v in vs:
        if not out or out[-1] is not v: out.append(v)
    if len(out) > 2 and out[0] is out[-1]: out.pop()
    if len(out) < 3: return None
    try:
        f = bm.faces.new(out); f.material_index = mat; return f
    except ValueError: return None


def opening(u, w, sill, head, kind='round', through=False, frame=None, reveal=True):
    """an opening in a wall: centred at u along it, w wide, from its sill up to the top of its head; round-headed or rectangular;
    through: a passage (its sides in the wall's stone, nothing behind), else a window or door seen into (its sides and back dark);
    frame: the stone round it on the face ('window': a sill and an arched band; 'door': jambs and a lintel; None);
    reveal False: the same opening in the wall's other face (its sides are built with the first)"""
    return {'u': u, 'w': w, 'sill': sill, 'head': head, 'kind': kind, 'through': through, 'frame': frame, 'reveal': reveal}


def _arch_angles(seg):
    return sorted(set([math.pi * i / seg for i in range(seg + 1)] + [math.pi / 4, 3 * math.pi / 4]))


def wall_face(bm, M, z0, top, ops=(), t=1.0, bo=None, mat=0, rev=1, seg=12):
    """a wall's face in its frame M (x along it, y out of it, z up), from z0 up to `top`: straight pieces [(u0, z0, u1, z1), ...]
    end to end along it (a gable; an aisle's sloping end; a step where one piece ends lower than the next begins), with
    openings (opening(); one above another too: a door and a window over it) t deep: their sides, sill, head and back in bo
    (default bm), material rev, or for a passage in bm. The face is cut in upright strips at every opening's side and every
    bend of its top, each strip in the wall between the openings in it; faces meeting on an upright line share its vertices
    (no T-junction: no hairline crack along an opening's edge)"""
    bo = bm if bo is None else bo
    cache, lines = {}, {}

    def V(u, z):
        k = (round(u, 4), round(z, 4))
        if k not in cache: cache[k] = bm.verts.new(M @ Vector((u, 0.0, z)))
        return cache[k]

    def mark(u, *zs): lines.setdefault(round(u, 4), set()).update(round(z, 4) for z in zs)

    def piece(u):
        for p in top:
            if p[0] - 1e-6 <= u <= p[2] + 1e-6: return p
        return top[0] if u < top[0][0] else top[-1]

    def ztop(u, p): return p[1] + (p[3] - p[1]) * (u - p[0]) / (p[2] - p[0]) if p[2] - p[0] > 1e-9 else max(p[1], p[3])

    ops = sorted(ops, key=lambda o: (o['u'], o['sill']))
    u_lo, u_hi = top[0][0], top[-1][2]
    brk = {round(p[0], 4) for p in top} | {round(p[2], 4) for p in top}
    for o in ops: brk |= {round(o['u'] - o['w'] / 2, 4), round(o['u'] + o['w'] / 2, 4)}
    us = sorted(b for b in brk if u_lo - 1e-6 <= b <= u_hi + 1e-6)
    spans = [(a, b) for a, b in zip(us, us[1:]) if b - a > 1e-5]

    # each opening's head: its arch's points (the angles include those whose ray meets the head line at a strip's side), the
    # spandrels' outer points on the box round it, and the points on its head line
    geo = {}
    for o in ops:
        a = o['w'] / 2; ul, ur = o['u'] - a, o['u'] + a; sill, head = o['sill'], o['head']
        mark(ul, sill, head); mark(ur, sill, head)
        if o['kind'] == 'round':
            sp = head - a
            angs = set(_arch_angles(seg)) | {math.atan2(a, b - o['u']) for b in us if ul + 1e-4 < b < ur - 1e-4}
            angs = sorted(angs)
            inner = [(o['u'] + a * math.cos(q), sp + a * math.sin(q)) for q in angs]
            outer = [(ur, sp + a * math.tan(q)) if q <= math.pi / 4 + 1e-9 else (ul, sp + a * math.tan(math.pi - q)) if q >= 3 * math.pi / 4 - 1e-9
                     else (o['u'] + a / math.tan(q), head) for q in angs]
            for u, z in outer:
                if abs(u - ur) < 1e-6 or abs(u - ul) < 1e-6: mark(u, z)
            mark(ul, sp); mark(ur, sp)
            geo[id(o)] = (angs, inner, outer, [p for p in outer if abs(p[1] - head) < 1e-6])
        else:
            geo[id(o)] = (None, None, None, [(ul, head), (ur, head)])

    def gaps(ua, ub):
        """the wall in the strip ua..ub between the openings in it: [(bottom z, the opening below or None, top z at ua, at ub)]"""
        p = piece((ua + ub) / 2); za, zb = ztop(ua, p), ztop(ub, p)
        boxes = sorted((o for o in ops if o['u'] - o['w'] / 2 - 1e-4 <= ua and ub <= o['u'] + o['w'] / 2 + 1e-4), key=lambda o: o['sill'])
        out, z, below = [], z0, None
        for o in boxes:
            out.append((z, below, o['sill'], o['sill'])); z, below = o['head'], o
        out.append((z, below, za, zb))
        return [g for g in out if max(g[2], g[3]) > g[0] + 1e-4]

    for ua, ub in spans:
        for zb_, below, ta, tb in gaps(ua, ub): mark(ua, zb_, ta); mark(ub, zb_, tb)

    def side(u, lo, hi, down=False):
        zs = sorted(z for z in lines.get(round(u, 4), ()) if lo + 1e-4 < z < hi - 1e-4)
        return [V(u, z) for z in (reversed(zs) if down else zs)]

    for o in ops:   # the spandrels round a round head
        angs, inner, outer, _ = geo[id(o)]
        if inner:
            for i in range(len(inner) - 1): _face(bm, [V(*inner[i]), V(*inner[i + 1]), V(*outer[i + 1]), V(*outer[i])], mat)
    for ua, ub in spans:   # the wall between the openings, strip by strip
        for zb_, below, ta, tb in gaps(ua, ub):
            bottom = [q for q in geo[id(below)][3] if ua - 1e-6 <= q[0] <= ub + 1e-6] if below else []
            for u in (ua, ub):   # (a strip narrower than the opening under it: its corners on that opening's head line)
                if not any(abs(q[0] - u) < 1e-4 for q in bottom): bottom.append((u, zb_))
            bottom.sort(key=lambda q: q[0])
            _face(bm, [V(*q) for q in bottom] + side(ub, zb_, tb) + [V(ub, tb), V(ua, ta)] + side(ua, zb_, ta, True), mat)
    for o in ops:   # the openings' sides, sill, head and back
        if not o.get('reveal', True): continue   # (an opening's other face: its sides are built with the first)
        a = o['w'] / 2; ul, ur = o['u'] - a, o['u'] + a; sill, head = o['sill'], o['head']
        m_ = mat if o['through'] else rev; B = bm if o['through'] else bo
        W = lambda u, y, z: B.verts.new(M @ Vector((u, y, z)))
        if o['kind'] == 'round':
            sp = head - a; arc = [(o['u'] + a * math.cos(q), sp + a * math.sin(q)) for q in geo[id(o)][0]]   # (the spandrels' angles)
        else:
            sp = head; arc = [(ur, head), (ul, head)]
        for x in (ul, ur): _face(B, [W(x, 0, sill), W(x, -t, sill), W(x, -t, sp), W(x, 0, sp)], m_)
        if sill > z0 + 1e-4 or not o['through']: _face(B, [W(ul, 0, sill), W(ur, 0, sill), W(ur, -t, sill), W(ul, -t, sill)], m_)
        for (u1, z1), (u2, z2) in zip(arc, arc[1:]): _face(B, [W(u1, 0, z1), W(u2, 0, z2), W(u2, -t, z2), W(u1, -t, z1)], m_)
        if not o['through']: _face(B, [W(ul, -t, sill), W(ur, -t, sill)] + [W(u, -t, z) for u, z in arc], m_)


def opening_frame(bm, M, o, band=.32, out=.12):
    """the stone round an opening on the wall's face: a window's sill and an arched band round its head, standing out from the
    face (a round-headed window: the band down its sides too); a door's jambs and lintel"""
    a = o['w'] / 2; u = o['u']
    # (the stone stands from the face, y 0: sunk into it, its faces would lie on the dark sides of the opening and flicker)
    if o['frame'] == 'window':
        kit.box(bm, u - a - band * .6, u + a + band * .6, 0.0, out * 1.6, o['sill'] - .2, o['sill'], xf=M)
        if o['kind'] == 'round':
            sp = o['head'] - a
            kit.arch_band(bm, a, sp, [(0, 0), (0, out), (band, out), (band, 0)], xf=M @ Matrix.Translation((u, 0, 0)))
            for sx in (-1, 1): kit.box(bm, min(sx * a, sx * (a + band)) + u, max(sx * a, sx * (a + band)) + u, 0.0, out, o['sill'], sp, xf=M)
    elif o['frame'] == 'door':
        b = band * 1.4
        for sx in (-1, 1): kit.box(bm, u + min(sx * a, sx * (a + b)), u + max(sx * a, sx * (a + b)), 0.0, out * 1.3, 0, o['head'], xf=M)
        kit.box(bm, u - a - b - .15, u + a + b + .15, 0.0, out * 2, o['head'], o['head'] + b * 1.6, xf=M)


def strip(bm, M, a, b, prof, m0=0.0, m1=0.0, caps=True, mat=0):
    """a moulding along a straight line on a wall's face (its frame M: x along, y out, z up) from a = (u, z) to b = (u, z): the
    profile [(out, dz), ...] (out of the face, up from the line) carried along it; its ends cut square, or mitred to turn a
    corner (m0, m1: 1 an outside corner, the moulding reaching round it by its own projection)"""
    d = 1.0 if b[0] >= a[0] else -1.0
    rings = [[bm.verts.new(M @ Vector((a[0] - d * m0 * o, o, a[1] + dz))) for o, dz in prof],
             [bm.verts.new(M @ Vector((b[0] + d * m1 * o, o, b[1] + dz))) for o, dz in prof]]
    for k in range(len(prof) - 1): _face(bm, [rings[0][k], rings[1][k], rings[1][k + 1], rings[0][k + 1]], mat)
    if caps:
        _face(bm, rings[0], mat); _face(bm, list(reversed(rings[1])), mat)


def plinth_prof(h):
    """a base course h high (out, z): a plain block, a splayed top, a fillet"""
    k = h / .62
    return [(0, 0), (.22 * k, 0), (.22 * k, .45 * k), (.12 * k, .55 * k), (.12 * k, .62 * k), (0, .62 * k)]


def cornice_prof(c):
    """an eaves cornice c high under a roof's soffit (dz from the wall's top): brick courses each standing out over the one below"""
    k = c / .8; g = .3 * k
    return [(0, -g - c), (.1 * k, -g - c), (.1 * k, -g - .78 * c), (.22 * k, -g - .72 * c), (.22 * k, -g - .45 * c), (.38 * k, -g - .38 * c),
            (.38 * k, -g), (0, -g)]


def ridge_row(bm, M, x, z, y0, y1, r, seg=7, mat=0):
    """ridge tiles: a half round of radius r along the frame's y from y0 to y1, sitting on the line (x, z), its ends closed"""
    ring = lambda y: [bm.verts.new(M @ Vector((x + r * math.cos(math.pi * i / seg), y, z - .3 * r + r * math.sin(math.pi * i / seg)))) for i in range(seg + 1)]
    a, b = ring(y0), ring(y1)
    for i in range(seg):
        f = _face(bm, [a[i], b[i], b[i + 1], a[i + 1]], mat)
        if f: f.smooth = True
    _face(bm, a, mat); _face(bm, list(reversed(b)), mat)


def tiles_bump(q, amp):
    """the rise of a Roman tile roof's surface over its flat line, q in rows (0 between two rows, .5 on a row of cover tiles):
    a smooth swell (the pans flat, the cover tiles round over them), its slope continuous and shaded smooth: rows of hard-edged
    half rounds, a pixel or two wide seen from afar, shimmer in bands across a roof"""
    return amp * (.5 - .5 * math.cos(math.tau * q)) ** 2


def slope_roof(bm, lo, hi, t, tile=.6, M=None, low_face=True, high_face=False, end_faces=True, mat=0, cover=None, amp=.07, k=6):
    """a roof slope in a frame M (x across it, y along its eaves, z up): a slab t thick (its underside t below its top), its low
    edge lo = (x, z, y0, y1) and its high edge hi = (x, z, y0, y1) on its top surface (the two edges' y ranges may differ: a slope
    ending in a valley or a hip). Its top in rows of cover tiles every `tile` along it, down the slope (tile 0: plain), k steps
    across a row; its top and edges in material cover (the tiles: kit.roof's index), its underside in mat"""
    cover = mat if cover is None else cover
    M = M or Matrix.Identity(4)
    (xl, zl, a0, a1), (xh, zh, b0, b1) = lo, hi
    P = lambda s, y, dz=0.0: M @ Vector((xl + (xh - xl) * s, y, zl + (zh - zl) * s + dz))
    y_min, y_max = min(a0, b0), max(a1, b1)

    def span(y):   # the stretch of the slope (0 at the low edge, 1 at the high) at y, between its two ends
        s0, s1 = 0.0, 1.0
        for e0, e1, lower in ((a0, b0, True), (a1, b1, False)):
            de = e1 - e0
            if abs(de) < 1e-9: continue
            q = (y - e0) / de
            if (lower and de > 0) or (not lower and de < 0): s1 = min(s1, q)
            else: s0 = max(s0, q)
        return max(0.0, s0), min(1.0, s1)

    ys = [y_min, y_max]
    if tile > 0:
        n = int((y_max - y_min) / tile); y_s = y_min + (y_max - y_min - n * tile) / 2
        ys += [y_s + i * tile / k for i in range(n * k + 1)]
        bump = lambda y: tiles_bump((y - y_s) / tile, amp) if y_s <= y <= y_s + n * tile else 0.0
    else: bump = lambda y: 0.0
    for e in (a0, a1, b0, b1): ys.append(e)
    ys = sorted(set(round(y, 5) for y in ys if y_min - 1e-9 <= y <= y_max + 1e-9))
    rows = []
    for y in ys:
        s0, s1 = span(y)
        if s1 < s0: s0 = s1 = (s0 + s1) / 2
        dz = bump(y); rows.append((bm.verts.new(P(s0, y, dz)), bm.verts.new(P(s1, y, dz)), bm.verts.new(P(s0, y, -t)), bm.verts.new(P(s1, y, -t))))
    for (l0, h0, lb0, hb0), (l1, h1, lb1, hb1) in zip(rows, rows[1:]):
        f = _face(bm, [l0, l1, h1, h0], cover)
        if f: f.smooth = True
        _face(bm, [lb0, hb0, hb1, lb1], mat)   # the underside
        if low_face: _face(bm, [l0, lb0, lb1, l1], cover)
        if high_face: _face(bm, [h0, h1, hb1, hb0], cover)
    if end_faces:
        for l, h, lb, hb in (rows[0], rows[-1]): _face(bm, [l, h, hb, lb], cover)


def free_column(bm, x, y, z0, z1, r, seg=12, M=None, mat=0):
    """a free-standing column from z0 to the top of its capital z1, radius r at its foot, tapering a tenth: a square plinth, a
    base of two tori, the shaft, a bell capital of two rows of leaves curling out under a square abacus"""
    M = (M or Matrix.Identity(4)) @ Matrix.Translation((x, y, 0))
    kit.box(bm, -1.4 * r, 1.4 * r, -1.4 * r, 1.4 * r, z0, z0 + .5 * r, mat=mat, xf=M)
    rt = .9 * r; cap0 = z1 - 2.6 * r
    kit.lathe(bm, [(1.3 * r, z0 + .5 * r), (1.38 * r, z0 + .75 * r), (1.25 * r, z0 + r), (1.1 * r, z0 + 1.05 * r), (1.15 * r, z0 + 1.25 * r),
                   (1.05 * r, z0 + 1.45 * r), (r, z0 + 1.6 * r)], seg=seg, mat=mat, xf=M)
    kit.lathe(bm, [(r, z0 + 1.6 * r), (rt, cap0)], seg=seg, mat=mat, xf=M)
    kit.lathe(bm, [(rt, cap0), (rt * 1.08, cap0 + .12 * r), (rt, cap0 + .25 * r), (rt * 1.22, cap0 + .95 * r), (rt * 1.08, cap0 + 1.05 * r),
                   (rt * 1.45, cap0 + 1.8 * r), (rt * 1.3, cap0 + 1.9 * r), (r * 1.45, z1 - .4 * r)], seg=seg, mat=mat, xf=M)
    kit.box(bm, -1.55 * r, 1.55 * r, -1.55 * r, 1.55 * r, z1 - .4 * r, z1, mat=mat, xf=M)


def cut(bm, y0=None, y1=None):
    """a copy of bm with what lies before y0 and beyond y1 cut away (a hall built whole, cut into its segments)"""
    b = bm.copy()
    for y, keep_above in ((y0, True), (y1, False)):
        if y is None: continue
        geom = b.verts[:] + b.edges[:] + b.faces[:]
        bmesh.ops.bisect_plane(b, geom=geom, dist=1e-5, plane_co=(0, y, 0), plane_no=(0, 1, 0), clear_inner=keep_above, clear_outer=not keep_above)
    return b


# ---- the building

def part_frame(p):
    ax, ay = p.get('at') or (0.0, 0.0)
    return Matrix.Translation((float(ax), float(ay), float(p.get('z_m') or 0))) @ Matrix.Rotation(math.radians(float(p.get('theta_deg') or 0)), 4, 'Z')


class Section:
    """a long hall's cross-section, x across from its axis: X[k] its walls (X[0] the nave's, X[n] the outermost aisle's), e[k]
    each wall's top (the underside of the roof over it there), r[k] aisle k's roof underside where it meets the wall inside it;
    the nave's pitch tn and the aisles' ta (shrunk with the steps where the nave would keep too little wall for its windows)"""

    def __init__(self, p, S):
        ai = p.get('aisles') or {}
        self.w, self.h, self.d = float(p['w_m']), float(p['h_m']), float(p['d_m'])
        self.n = n = int(ai.get('n') or 0) if ai else 0
        self.aw = aw = float(ai.get('w_m') or 0) if n else 0.0
        self.X = [(self.w - 2 * n * aw) / 2 + k * aw for k in range(n + 1)]
        if self.X[0] < .5: raise SystemExit(f'basilica: {p.get("id")}: its aisles leave no nave')
        R = p.get('roof') or {}
        self.tn = math.tan(math.radians(R.get('pitch_deg') or 25.0))
        self.o = R.get('overhang_m') if R.get('overhang_m') is not None else .6
        self.tr = tr = S['roof_t_m']
        self.ta = math.tan(math.radians(S['aisle_pitch_deg'])); step = S['aisle_step_m']
        e = [self.h] + [0.0] * n; r = [0.0] * (n + 1)
        if n:
            eo = float(ai['h_m']); need = n * (aw * self.ta + tr) + (n - 1) * step
            room = self.h - S['clerestory_min_m'] - eo
            k = max(0.0, min(1.0, room / need)) if need > 0 else 1.0
            self.ta *= k; step *= k
            e[n] = eo
            for j in range(n, 0, -1):
                r[j] = e[j] + aw * self.ta
                if j > 1: e[j - 1] = r[j] + tr + step
        self.e, self.r = e, r

    def top(self, x):
        """the top of the hall over x (its roofs' top surface)"""
        ax = abs(x); X = self.X
        if ax <= X[0]: return self.h + (X[0] - ax) * self.tn + self.tr
        for j in range(1, self.n + 1):
            if ax <= X[j] + 1e-6: return self.e[j] + (X[j] - ax) * self.ta + self.tr
        return 0.0

    def outline(self):
        """an end wall's top: pieces (u0, z0, u1, z1) across it, along the underside of its roofs"""
        X, e, r = self.X, self.e, self.r; n = self.n; pcs = []
        for j in range(n, 0, -1): pcs.append((-X[j], e[j], -X[j - 1], r[j]))
        pcs += [(-X[0], self.h, 0.0, self.h + X[0] * self.tn), (0.0, self.h + X[0] * self.tn, X[0], self.h)]
        for j in range(1, n + 1): pcs.append((X[j - 1], r[j], X[j], e[j]))
        return pcs


class Solid:
    """a part's volume, for the test whether a wall's opening is behind it"""

    def __init__(self, p, S):
        self.id, self.p = p['id'], p; self.Mi = part_frame(p).inverted()
        self.sec = Section(p, S) if p['kind'] == 'long_hall' else None

    def top_at(self, x, y):
        q = self.Mi @ Vector((x, y, 0)); p = self.p
        if self.sec:
            if abs(q.x) <= self.sec.w / 2 + 1e-3 and abs(q.y) <= self.sec.d / 2 + 1e-3: return self.sec.top(q.x)
            return None
        r = float(p['d_m']) / 2; rho = math.hypot(q.x, q.y); sw = math.radians(float(p.get('sweep_deg') or 360))
        a = math.atan2(q.y, q.x); off = abs(((a - math.pi / 2) + math.pi) % math.tau - math.pi)   # (a sweep is centred on the part's back, +y)
        if rho <= r + 1e-3 and (sw >= math.tau - 1e-6 or off <= sw / 2 + 1e-6):
            rise = float((p.get('dome') or {}).get('rise_m') or r)
            return float(p.get('drum_h_m') or 0) + rise * (1 - rho / r)
        return None


def hidden(M, o, z, others, out=.4):
    """an opening of a wall (its frame M, whole frame) behind another part: either jamb or its middle, a little out from the face"""
    a = o['w'] / 2
    for du in (-a - .3, 0.0, a + .3):
        q = M @ Vector((o['u'] + du, out, 0))
        for s in others:
            tz = s.top_at(q.x, q.y)
            if tz is not None and tz > z: return True
    return False


ROOF = 2   # (the material index of a roof's covering in _mats)


def _mats(): return [kit.stone(), kit.dark(), kit.roof()]


def build_run(segs, S, solids, entrance):
    """long halls end to end along one axis: built as one, then cut into its segments' objects"""
    p0 = segs[0]; sec = Section(p0, S); th = math.radians(float(p0.get('theta_deg') or 0))
    Mr = part_frame(p0); yd = Vector((-math.sin(th), math.cos(th)))
    spans = []
    for p in segs:
        off = (Vector((float(p['at'][0]), float(p['at'][1]))) - Vector((float(p0['at'][0]), float(p0['at'][1])))).dot(yd)
        spans.append((off - float(p['d_m']) / 2, off + float(p['d_m']) / 2))
    y0, y1 = spans[0][0], spans[-1][1]
    ids = {p['id'] for p in segs}; others = [s for s in solids if s.id not in ids]
    X, e, r, n, h, tn, o, tr = sec.X, sec.e, sec.r, sec.n, sec.h, sec.tn, sec.o, sec.tr
    bay = S['bay_m']; t = S['wall_m']; cm = S['cornice_m']; verge = o * .6
    bw, br, bo = bmesh.new(), bmesh.new(), bmesh.new()

    def win_w(sill, head, wmax): return min(wmax, max(0.0, (head - sill) / 1.6))

    def place(Mw, ops):   # the openings kept: big enough, and not behind another part (Mr @ Mw: the wall in the whole's frame)
        return [q for q in ops if q['w'] > .5 and q['head'] - q['sill'] > 1.0 and not hidden(Mr @ Mw, q, q['sill'], others)]

    # ---- the long walls, side by side: the nave's (the clerestory), each aisle's step, the outer aisle's
    nb = max(1, round((y1 - y0) / bay)); bl = (y1 - y0) / nb
    for s in (-1, 1):
        for j in range(n + 1):
            zb = 0.0 if j == n else r[j + 1] - .4; zt = e[j]
            Mw = wall_frame((s * X[j], 0, 0), (0, 1, 0), (s, 0, 0))
            c = cm if (j == 0 or j == n) else cm * .55
            if j == 0 and n: sill, head = r[1] + tr + .6, zt - .3 * c - c - .4
            elif j == 0: sill, head = .55 * h, min(.88 * h, zt - .3 * c - c - .4)
            elif j == n: sill, head = .5 * zt, min(.85 * zt, zt - .3 * c - c - .4)
            else: sill, head = r[j + 1] + tr + .4, zt - .3 * c - c - .2
            ww = win_w(sill, head, S['window_share'] * bl)
            ops = []
            if head - sill >= 1.5 and ww > .5:
                fr = 'window' if (j == 0 or j == n) else None
                ops = [opening(y0 + (i + .5) * bl, ww, sill, head, frame=fr) for i in range(nb)]
            ops = place(Mw, ops)
            wall_face(bw, Mw, zb, [(y0, zt, y1, zt)], ops, t, bo)
            for q in ops:
                if q['frame']: opening_frame(bw, Mw, q)
            strip(bw, Mw, (y0, zt), (y1, zt), cornice_prof(c), 1, 1)
            if j == n: strip(bw, Mw, (y0, 0), (y1, 0), plinth_prof(S['plinth_m']), 1, 1)

    # ---- the ends: the entrance front (doors, a string course, windows), the other end plain; a hall without aisles: windows
    outline = sec.outline()
    for end, yy, out in (('front', y0, -1), ('back', y1, 1)):
        Mw = wall_frame((0, yy, 0), (1, 0, 0), (0, out, 0))
        ent = end == 'front' and entrance
        ops = []
        if ent:
            dw, dh = S['door_m']
            ops.append(opening(0.0, dw, 0.0, dh, 'rect', frame='door'))
            for j in range(1, n + 1):
                for sx in (-1, 1): ops.append(opening(sx * (X[j - 1] + sec.aw / 2), dw * .7, 0.0, dh * .7, 'rect', frame='door'))
            nf = int(S['front_windows'])
            if nf:
                sill, head = max(.5 * h, dh + 2.5), .82 * h; ww = min(2 * X[0] / (2 * nf + 1) * .9, (head - sill) / 2.5)
                ops += [opening(-X[0] + (i + .5) * 2 * X[0] / nf, ww, sill, head, frame='window') for i in range(nf)]
            for j in range(1, n + 1):
                sill, head = max(.5 * e[j], dh + 2.5), min(.82 * e[j], e[j] - .3 * cm - cm - .4)
                ww = min(sec.aw * .2, (head - sill) / 2)
                if head - sill > 1.5:
                    for sx in (-1, 1): ops.append(opening(sx * (X[j - 1] + sec.aw / 2), ww, sill, head, frame='window'))
        elif not n:
            nw = max(1, round(2 * X[0] / (bay * 1.5))); nw += 1 - nw % 2
            sill, head = .55 * h, min(.88 * h, h - .3 * cm - cm - .4); ww = win_w(sill, head, S['window_share'] * bay)
            ops = [opening(-X[0] + (i + .5) * 2 * X[0] / nw, ww, sill, head, frame='window') for i in range(nw)]
        ops = place(Mw, ops)
        wall_face(bw, Mw, 0.0, outline, ops, t, bo)
        for q in ops: opening_frame(bw, Mw, q)
        for u0, z0, u1, z1 in outline:   # raking cornices up the gable and the aisles' slopes
            if abs(z1 - z0) > 1e-3: strip(bw, Mw, (u0, z0), (u1, z1), [(0, -.04), (.26, -.04), (.26, -.3), (.12, -.4), (0, -.46)])
        strip(bw, Mw, (-X[0], h), (X[0], h), cornice_prof(cm), 1, 1)   # (the gable's foot: a pediment)
        doors = sorted((q['u'] - q['w'] / 2 - .7, q['u'] + q['w'] / 2 + .7) for q in ops if q['sill'] <= 1e-6)
        stops = [-X[n]] + [v for d_ in doors for v in d_] + [X[n]]   # (the plinth runs between the doors)
        for k in range(0, len(stops) - 1, 2):
            if stops[k + 1] - stops[k] > .2: strip(bw, Mw, (stops[k], 0), (stops[k + 1], 0), plinth_prof(S['plinth_m']), 1 if k == 0 else 0, 1 if k + 2 == len(stops) else 0)
        if ent:
            sc = S['door_m'][1] + 1.0
            strip(bw, Mw, (-X[n], sc), (X[n], sc), [(0, 0), (.16, 0), (.16, .22), (.08, .3), (0, .32)], 1, 1)

    # ---- the roofs: the nave's gable, each aisle's lean-to against the wall inside it; tiles, ridge tiles, flashing
    tile = S['tile_m']; ya, yb = y0 - verge, y1 + verge
    zr = h + X[0] * tn + tr
    for s in (-1, 1):
        slope_roof(br, (s * (X[0] + o), h - o * tn + tr, ya, yb), (0.0, zr, ya, yb), tr, tile, cover=ROOF)
    ridge_row(br, Matrix.Identity(4), 0.0, zr, ya, yb, .24, mat=ROOF)
    for j in range(1, n + 1):
        for s in (-1, 1):
            slope_roof(br, (s * (X[j] + o), e[j] - o * sec.ta + tr, ya, yb), (s * X[j - 1], r[j] + tr, ya, yb), tr, tile, cover=ROOF)
            ridge_row(br, Matrix.Identity(4), s * X[j - 1], r[j] + tr, ya, yb, .16, mat=ROOF)

    # ---- cut into the segments
    objs = []
    for (sa, sb), p in zip(spans, segs):
        c0 = None if p is segs[0] else sa; c1 = None if p is segs[-1] else sb
        for suffix, bm_ in (('', bw), ('_roof', br), ('_openings', bo)):
            b = cut(bm_, c0, c1)
            if not b.faces: b.free(); continue
            bmesh.ops.transform(b, matrix=Mr, verts=b.verts)
            objs.append(kit.obj(p['id'] + suffix, b, _mats()))
    for b in (bw, br, bo): b.free()
    return objs


def build_dome(p, S):
    """a dome on its drum, or a part of one (sweep_deg, centred on its back: an apse against the wall in front of it)"""
    M = part_frame(p); r = float(p['d_m']) / 2; h = float(p.get('drum_h_m') or 0); dm = p.get('dome') or {}
    sw = math.radians(float(p.get('sweep_deg') or 360)); whole = sw >= math.tau - 1e-6
    a0, a1 = (0.0, math.tau) if whole else (math.pi / 2 - sw / 2, math.pi / 2 + sw / 2)
    seg = max(8, int(S['apse_seg'] * (a1 - a0) / math.tau))
    rise = float(dm.get('rise_m') or r); shape = dm.get('shape') or 'hemisphere'
    tr = S['roof_t_m']; o = .6; cm = S['cornice_m']; tile = S['tile_m']
    bw, br = bmesh.new(), bmesh.new()
    turn = dict(seg=seg, a0=a0, a1=a1, xf=M)
    if h > 0:
        kit.lathe(bw, [(r, 0.0), (r, h)], **turn)
        kit.lathe(bw, [(r + q, z) for q, z in plinth_prof(S['plinth_m'])], **turn)
        kit.lathe(bw, [(r + q, h + z) for q, z in cornice_prof(cm)], **turn)
    tn = rise / r
    if shape == 'cone':
        R = r + o; ze = h - o * tn + tr; zr_ = rise + o * tn   # (the top surface: from the eaves' ring R up to the apex)
        kit.lathe(br, [(R, h - o * tn), (R, ze)], mat=ROOF, **turn)   # (its eaves' edge)
        kit.lathe(br, [(0.0, h + rise), (R, h - o * tn)], **turn)   # (its underside)
        # its top in rows of cover tiles up the cone, as a roof slope's (tiles_bump), their swell fading as they close in
        nrow = max(3, int((a1 - a0) * R / tile)); K = 6; nr = 10
        ring = [[br.verts.new(M @ Vector((R * (1 - i / nr) * math.cos(a), R * (1 - i / nr) * math.sin(a),
                                          ze + zr_ * i / nr + tiles_bump(j / K, .07) * (1 - i / nr))))
                 for i in range(nr + 1)] for j, a in enumerate(a0 + (a1 - a0) * q / (nrow * K) for q in range(nrow * K + 1))]
        for j in range(len(ring) - 1):
            for i in range(nr):
                f = _face(br, [ring[j][i], ring[j + 1][i], ring[j + 1][i + 1], ring[j][i + 1]], ROOF)
                if f: f.smooth = True
    else:   # a dome: its shell and its eaves' edge
        R = r + o * .3
        kit.lathe(br, [(R, h)] + [(R * math.cos(math.pi / 2 * i / 12), h + tr + rise * math.sin(math.pi / 2 * i / 12)) for i in range(13)], mat=ROOF, **turn)
    if not whole:   # the flat back against the wall in front of it: the roof's section closed
        Q = lambda x, z: br.verts.new(M @ Vector((x, 0.0, z)))
        if shape == 'cone':
            _face(br, [Q(-(r + o), h - o * tn), Q(r + o, h - o * tn), Q(r + o, h - o * tn + tr), Q(0.0, h + rise + tr), Q(-(r + o), h - o * tn + tr)], 0)
        else:
            R = r + o * .3
            _face(br, [Q(-R, h), Q(R, h)] + [Q(R * math.cos(math.pi * i / 24), h + tr + rise * math.sin(math.pi * i / 24)) for i in range(25)], 0)
    objs = []
    if bw.faces: objs.append(kit.obj(p['id'], bw, _mats()))
    else: bw.free()
    objs.append(kit.obj(p['id'] + '_roof', br, _mats()))
    return objs


def runs_of(halls):
    """long halls end to end along one axis (the same turn, width, height and aisles, centres on one line, ends touching)"""
    def key(p): return (round(float(p.get('theta_deg') or 0) % 360, 3), float(p['w_m']), float(p['h_m']), str(p.get('aisles')), str(p.get('roof')))
    out = []
    for p in halls:
        th = math.radians(float(p.get('theta_deg') or 0)); yd = Vector((-math.sin(th), math.cos(th))); xd = Vector((math.cos(th), math.sin(th)))
        for run in out:
            q = run[0]
            if key(q) != key(p): continue
            dv = Vector((float(p['at'][0]) - float(q['at'][0]), float(p['at'][1]) - float(q['at'][1])))
            if abs(dv.dot(xd)) > .05: continue
            ends = [(dv.dot(yd) - float(p['d_m']) / 2, dv.dot(yd) + float(p['d_m']) / 2)]
            spans = [((Vector((float(z['at'][0]) - float(q['at'][0]), float(z['at'][1]) - float(q['at'][1]))).dot(yd)) - float(z['d_m']) / 2,
                      (Vector((float(z['at'][0]) - float(q['at'][0]), float(z['at'][1]) - float(q['at'][1]))).dot(yd)) + float(z['d_m']) / 2) for z in run]
            if any(abs(ends[0][0] - b) < .05 or abs(ends[0][1] - a) < .05 for a, b in spans):
                run.append(p); break
        else: out.append([p])
    for run in out:   # front to back along the run
        q = run[0]; th = math.radians(float(q.get('theta_deg') or 0)); yd = Vector((-math.sin(th), math.cos(th)))
        run.sort(key=lambda z: Vector((float(z['at'][0]), float(z['at'][1]))).dot(yd))
    return out


def build(s):
    S = {**DEFAULT, **(s or {})}
    parts = S['parts']
    if not parts: raise SystemExit('basilica: no parts (a landmark: --landmark, or spec parts)')
    solids = [Solid(p, S) for p in parts]
    halls = [p for p in parts if p['kind'] == 'long_hall']
    runs = runs_of(halls)
    aisled = [rn for rn in runs if (rn[0].get('aisles') or {}).get('n')]
    ent = (aisled or runs)[0] if S['doors'] and runs else None
    objs = []
    for rn in runs: objs += build_run(rn, S, solids, rn is ent)
    for p in parts:
        if p['kind'] == 'dome': objs += build_dome(p, S)
    return objs

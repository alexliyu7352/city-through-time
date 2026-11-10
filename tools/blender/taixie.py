"""A terrace palace (台榭, 高台建筑) of the Warring States and Qin as a detailed model: a platform of rammed earth with battered
faces, rooms let into its sides, a covered walk round its foot and a pebble apron outside the walk; on its top an open terrace with
low walls at its edge, an upper tier with single-storey halls round a court and a two-storey main hall in the middle; and, when the
landmark has a twin (mirror_m), the twin across a gap, the two joined by a covered gallery on piers (飞阁).

The layout and the heights are the film's (pipeline/citygen.py Builder.taixie, after Yang Hongxun's reconstruction of palace No. 1
at Qin Xianyang): every hall, room, walk, stair and the gallery where the generator puts them, their eaves and ridges at its
heights, all as shares of the platform (DEFAULT). What the film's massing leaves out is built the way the period built, every
size an estimate where no source gives it:
  - timber posts on stone bases, a beam along their heads (阑额), a bearing block on each post (栌斗) with a short arm and two
    small blocks (一斗二升: the simple bracket of Warring States and Han pictures and models, no later tiers of brackets), or a
    block and a bolster (替木) under a low eave; a purlin along them;
  - roofs straight in section, without upturned corners: hipped (庑殿), hip-and-gable (歇山), gable (悬山) and lean-to; boarded
    and tiled, rows of round tiles (筒瓦) down every slope with a round eave tile (瓦当) at the foot of each row, rafters under
    the eaves, plain ridges with plain ends, hips, verges with their bargeboards;
  - walls of earth with wall posts (壁柱) in them, doors and windows that are openings, dark behind, framed in timber; windows
    barred (直棂);
  - the stair in steps (treads of hollow brick), its foot solid, its upper flight carried over the walk on a beam and posts;
    the walk's raised floor and the pebble apron (散水) outside it, edged with square bricks.

Objects (each one part of a museum page; a twin's halves are prefixed west_ and east_, a single terrace centre_):
  <half>_platform     the rammed-earth platform
  <half>_rooms        the rooms' doors in its faces (niches dark behind, timber frames, thresholds)
  <half>_walk         the walk round its foot: floor, apron, posts, beams, brackets, ties into the platform, rafters
  <half>_terrace      the top: the upper tier and its steps, the low walls at the edge with their copings
  <half>_halls        the halls round the court (a U: a north range and two side ranges): walls, doors, windows, wall posts, brackets
  <half>_main         the main hall: the lower storey (the room, its side rooms, the walk in front), the upper storey
  <half>_stair        the stair up the south face
  <half>_roof_walk, <half>_roof_halls, <half>_roof_main    the roofs
  gallery, gallery_roof    the gallery between the twins: deck, beams, piers, posts, railings, brackets; its roof
The east half is the west half mirrored: a landmark with mirror_m has two matching halves (Xianyang No. 1: the west half dug,
the east half mirrored from it).
Materials: stone (the model's white), dark (an opening seen into), sand (rammed earth: the film's earth tone), roof (the tiles,
ridges and copings: shaded as the film's roofs; the boards' underside, rafters and bargeboards stay white)."""
import math

import bmesh
from mathutils import Matrix, Vector

import kit

STONE, DARK, EARTH, ROOF = 0, 1, 2, 3   # (ROOF: a roof's covering, tiles and ridges: the page shades it as the film's roofs)

DEFAULT = {
    # the film's landmark (from_landmark): one half's platform at its foot (w x d, metres) and height, the gap to its twin (0: a
    # single terrace), the rooms let into its south and north faces, the main hall's roof
    'w_m': 60.0, 'd_m': 45.0, 'h_m': 6.0, 'mirror_m': 0.0, 'rooms': [5, 2], 'roof_main': 'xieshan',
    # ---- the layout as the film's generator draws it (citygen Builder.taixie): shares of the platform and metres
    'top': [.96, .95],               # the platform's top as a share of its foot (its faces battered)
    'room_door': [3.2, 3.6, .2],     # a room's door at most this wide and high, its head .2 + high over the ground (and .8 w / n * .4, .6 h)
    'walk': {'body': [.985, .975], 'depth': 5.2, 'h': 4.4, 'h_share': .72, 'rise': 1.1, 'bay': 4.2},   # the walk: its inner line, depth, eave, roof's rise, bays
    'upper': {'w': .9, 'd': .6, 'y': .17, 'h': .6},                    # the upper tier: share of w, of d, its middle north of the centre (share of d), height
    'parapet': {'side_x': .47, 'side_y': -.2, 'side_len': .5, 'front_y': -.46, 'front_len': .94, 't': .5, 'h': 1.1},   # the low walls at the top's edge
    'halls': {'d': 9.0, 'h': 4.6, 'side_cut': 13.0, 'side_dy': -2.0},  # the ranges round the court: depth, height to the ridge, the side ranges' length (ud less this) and middle
    'main': {'w': .48, 'w_max': 26.0, 'd': .55, 'd_max': 17.0, 'dy': -1.0, 'h1': 5.6, 'eave1': 2.4,
             'k2': .78, 'z2': 6.2, 'h2': 4.0, 'rise': 3.8, 'eave2': 2.0},   # the main hall: its lower body (shares of the tier), the first floor's eave, the upper storey, its roof
    'stair': {'x': -.3, 'w': 5.0},   # the stair up the south face: its middle (share of w, toward the far side from the twin), width
    'gallery': {'w': 6.5, 'post_h': 3.4, 'rise': 2.2, 'eave': 1.0, 'pier': [3.0, 5.0], 'pier_x': .22, 'bay': 4.5},
    # ---- estimates (what neither the film nor a source gives: the period's building, Qin and Han finds, Yang Hongxun's drawings)
    'main_room_m': None,             # the main hall's room inside its walk ([w, d] metres; None: .52 x .81 of the lower body)
    'main_doors': [2, 0],            # doors in the room's south and north walls
    'floor_h': .3,                   # the walk's floor over the ground
    'sill': .15,                     # a door's threshold over its floor
    'apron': {'w': 1.0, 'brick': .36},   # the pebble apron outside the walk, the square bricks along its edge
    'riser': .2,                     # a step's rise (treads of hollow brick)
    'post_r': {'walk': .22, 'main': .3, 'gallery': .2, 'stair': .15},
    'tile': {'pitch': .5, 'r': .085, 'eave_r': .095},   # rows of round tiles: apart, the half round's radius, the eave tile's
    'rafter': {'pitch': .42, 'size': .12},
    'roof_t': .3,                    # boards and tiles: the roof's depth over its rafters
    'pent_pitch': .25,               # the main hall's first-floor eave, a lean-to round the upper storey
    'wall_t': {'hall': .6, 'main': .8, 'upper': .45},
}


def from_landmark(L):
    """the sizes the film's landmark gives (city.yaml, kind taixie: w_m, d_m, h_m, mirror_m, rooms, roof), as this spec's keys"""
    out = {}
    for k in ('w_m', 'd_m', 'h_m', 'mirror_m'):
        if L.get(k) is not None: out[k] = float(L[k])
    if L.get('rooms'): out['rooms'] = [int(x) for x in L['rooms']]
    if L.get('roof'): out['roof_main'] = 'xieshan' if L['roof'] == 'hip' else str(L['roof'])   # (the generator draws 'hip' as a hip-and-gable)
    return out


def spec_of(s):
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULT.items()}
    for k, v in (s or {}).items():
        out[k] = {**out[k], **v} if isinstance(out.get(k), dict) and isinstance(v, dict) else v
    return out


# ---- for the kit: faces, timbers, blocks, prisms on a plan, plan polygons

def face(bm, pts, mat=STONE, smooth=False):
    """a face through the 3D points in their order (welded to its neighbours later: kit.obj)"""
    try: f = bm.faces.new([bm.verts.new(p) for p in pts])
    except ValueError: return None
    f.material_index = mat; f.smooth = smooth
    return f


def beam(bm, p0, p1, w, h, mat=STONE, lift=0.0):
    """a timber (a ridge, a rail, a rafter) w wide and h deep along p0 -> p1 (3D), its section square to the line and upright as
    far as the line allows; lift raises the section along its upright (0: centred on the line)"""
    p0, p1 = Vector(p0), Vector(p1); t = p1 - p0
    if t.length < 1e-4: return
    t.normalize(); s = t.cross(Vector((0, 0, 1)))
    if s.length < 1e-6: s = Vector((1, 0, 0))
    s.normalize(); u = s.cross(t)
    c = [p + s * (i * w / 2) + u * (j * h / 2 + lift) for p in (p0, p1) for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): face(bm, [c[i] for i in q], mat)


def block(bm, cx, cy, z0, z1, a0, a1=None, ang=0.0, mat=STONE, b0=None, b1=None):
    """a block a0 x b0 at its foot and a1 x b1 at its head (a along the angle ang), centred on (cx, cy): a box, or a block tapering
    up (a post's base) or down (a bearing block)"""
    a1 = a0 if a1 is None else a1; b0 = a0 if b0 is None else b0; b1 = a1 if b1 is None else b1
    c, s = math.cos(ang), math.sin(ang)
    P = lambda x, y, z: (cx + x * c - y * s, cy + x * s + y * c, z)
    lo = [P(i * a0 / 2, j * b0 / 2, z0) for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    hi = [P(i * a1 / 2, j * b1 / 2, z1) for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    face(bm, lo[::-1], mat); face(bm, hi, mat)
    for k in range(4): face(bm, [lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]], mat)


def prism(bm, poly, z0, z1, mat=STONE):
    """an upright prism on a plan polygon [(x, y), ...] from z0 to z1"""
    lo = [(x, y, z0) for x, y in poly]; hi = [(x, y, z1) for x, y in poly]; n = len(poly)
    face(bm, hi, mat); face(bm, lo[::-1], mat)
    for k in range(n): face(bm, [lo[k], lo[(k + 1) % n], hi[(k + 1) % n], hi[k]], mat)


def section(bm, prof, a, b, mat=STONE):
    """a section [(q, z), ...] (q across) laid along the plan line a -> b: a coping, a stair's flight, a cheek wall. q is measured
    to the left of a -> b"""
    L = math.dist(a, b); ex, ey = (b[0] - a[0]) / L, (b[1] - a[1]) / L; lx, ly = -ey, ex
    A = [(a[0] + lx * q, a[1] + ly * q, z) for q, z in prof]; B = [(b[0] + lx * q, b[1] + ly * q, z) for q, z in prof]; n = len(prof)
    face(bm, A[::-1], mat); face(bm, B, mat)
    for k in range(n): face(bm, [A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]], mat)


def dedupe(poly, eps=1e-6):
    out = []
    for p in poly:
        if not out or math.dist(p, out[-1]) > eps: out.append(p)
    if len(out) > 1 and math.dist(out[0], out[-1]) <= eps: out.pop()
    return out


def clip(poly, a, b, c):
    """the part of a plan polygon where a x + b y >= c (one half-plane, Sutherland-Hodgman)"""
    out, n = [], len(poly)
    for i in range(n):
        P, Q = poly[i], poly[(i + 1) % n]
        fp, fq = a * P[0] + b * P[1] - c, a * Q[0] + b * Q[1] - c
        if fp >= 0: out.append(P)
        if (fp >= 0) != (fq >= 0):
            k = fp / (fp - fq); out.append((P[0] + (Q[0] - P[0]) * k, P[1] + (Q[1] - P[1]) * k))
    return dedupe(out)


def inside(poly, x, y):
    c, n = False, len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): c = not c
    return c


def cylinder_along(bm, c, axis, side, r, l0, l1, seg=8, mat=STONE, caps=(False, True), smooth=True):
    """a short drum round the axis through c (3D), from l0 to l1 along it; side: a vector square to the axis (the first point)"""
    axis = Vector(axis).normalized(); side = Vector(side).normalized(); up = axis.cross(side)
    ring = [side * (r * math.cos(math.tau * i / seg)) + up * (r * math.sin(math.tau * i / seg)) for i in range(seg)]
    A = [Vector(c) + axis * l0 + q for q in ring]; B = [Vector(c) + axis * l1 + q for q in ring]
    for i in range(seg): face(bm, [A[i], A[(i + 1) % seg], B[(i + 1) % seg], B[i]], mat, smooth)
    if caps[0]: face(bm, A[::-1], mat)
    if caps[1]: face(bm, B, mat)


# ---- for the kit: roofs as planes. A roof is a few panels, each a plan polygon on one plane rising from its eave line; the
# panels meet on hips, ridges and valleys. A panel draws as a slab of boards and tiles (its depth t under its top), rows of
# round tiles down it, rafters under its eave; the lines where panels meet get their ridges

class Panel:
    """one plane of a roof: a plan polygon, its eave line (a point e0 on it and n, the unit plan normal up the slope), the height E
    of the tiles' top at the eave line and the pitch p (rise per metre); t: boards and tiles, the underside t below the top"""

    def __init__(self, poly, e0, n, E, p, t):
        self.poly = dedupe([(float(x), float(y)) for x, y in poly]); self.e0 = (float(e0[0]), float(e0[1]))
        k = math.hypot(*n); self.n = (n[0] / k, n[1] / k); self.u = (self.n[1], -self.n[0]); self.E, self.p, self.t = E, p, t

    def v(self, x, y): return (x - self.e0[0]) * self.n[0] + (y - self.e0[1]) * self.n[1]
    def w(self, x, y): return (x - self.e0[0]) * self.u[0] + (y - self.e0[1]) * self.u[1]
    def z(self, x, y): return self.E + self.p * self.v(x, y)
    def top(self, x, y): return Vector((x, y, self.z(x, y)))
    def at(self, w, v): return (self.e0[0] + w * self.u[0] + v * self.n[0], self.e0[1] + w * self.u[1] + v * self.n[1])

    def span(self, w):
        """the stretch [v0, v1] up the slope of the line at w (along the eave) that lies on the panel, or None"""
        ox, oy = self.at(w, 0.0); nx, ny = self.n; vs = []; m = len(self.poly)
        for i in range(m):
            (x1, y1), (x2, y2) = self.poly[i], self.poly[(i + 1) % m]
            ex, ey = x2 - x1, y2 - y1; den = nx * ey - ny * ex
            if abs(den) < 1e-12: continue
            dx, dy = x1 - ox, y1 - oy
            v, s = (dx * ey - dy * ex) / den, (dx * ny - dy * nx) / den
            if -1e-9 <= s <= 1 + 1e-9: vs.append(v)
        return (min(vs), max(vs)) if len(vs) >= 2 and max(vs) - min(vs) > 1e-6 else None

    def eaves(self):
        """the polygon's edges on the eave line"""
        m = len(self.poly)
        return [(self.poly[i], self.poly[(i + 1) % m]) for i in range(m) if abs(self.v(*self.poly[i])) < 1e-6 and abs(self.v(*self.poly[(i + 1) % m])) < 1e-6]


def under(panels, x, y):
    """the underside of a roof (its panels) over a plan point: the boards' underside (rafters hang below it)"""
    for dx, dy in ((0, 0), (.03, 0), (-.03, 0), (0, .03), (0, -.03), (.03, .03), (-.03, -.03), (.03, -.03), (-.03, .03)):
        zs = [P.z(x + dx, y + dy) - P.t for P in panels if inside(P.poly, x + dx, y + dy)]
        if zs: return max(zs)
    raise ValueError(f'taixie: no roof over ({x:.2f}, {y:.2f})')


def under_any(panels, pts):
    """the underside over the first of the plan points a roof covers (one clear of its gaps)"""
    for x, y in pts:
        if any(inside(P.poly, x, y) for P in panels): return under(panels, x, y)
    raise ValueError(f'taixie: no roof over any of {pts}')


def slab(bm, P, mat=ROOF):
    """a panel's boards and tiles: its top and edges the roof's covering, its underside (the boards seen under the eave) white"""
    top = [P.top(x, y) for x, y in P.poly]; bot = [q - Vector((0, 0, P.t)) for q in top]; n = len(top)
    face(bm, top, mat); face(bm, bot[::-1], STONE)
    for k in range(n): face(bm, [bot[k], bot[(k + 1) % n], top[(k + 1) % n], top[k]], mat)


def tiles(bm, P, T):
    """rows of round tiles down a panel, T['pitch'] apart: each a half round laid on the boards from the eave (or a valley) up to
    the ridge, hip or wall, a round eave tile across its foot"""
    ws = [P.w(x, y) for x, y in P.poly]; sp, r, re = T['pitch'], T['r'], T['eave_r']
    N = Vector((-P.p * P.n[0], -P.p * P.n[1], 1)).normalized(); S3 = Vector((P.u[0], P.u[1], 0)); out = Vector((-P.n[0], -P.n[1], 0))
    seg = 5; ring = [S3 * (r * math.cos(math.pi * i / seg)) + N * (r * math.sin(math.pi * i / seg)) for i in range(seg + 1)]
    for k in range(math.ceil(min(ws) / sp - .5), math.floor(max(ws) / sp - .5) + 1):
        w = (k + .5) * sp; s_ = P.span(w)
        if not s_: continue
        v0, v1 = s_; eave = abs(v0) < 1e-4
        a, b = v0 + (0.0 if eave else .15), v1 - .15
        if b - a < .3: continue
        A, B = P.top(*P.at(w, a)), P.top(*P.at(w, b))
        ra, rb = [A + q for q in ring], [B + q for q in ring]
        for i in range(seg): face(bm, [ra[i], rb[i], rb[i + 1], ra[i + 1]], ROOF, smooth=True)
        face(bm, rb, ROOF)
        if eave: cylinder_along(bm, A, out, S3, re, -.02, .03, seg=10, mat=ROOF)   # the eave tile, across the row's foot, over the fascia
        else: face(bm, ra[::-1], ROOF)


def rafters(bm, P, R, depth=None):
    """rafters under a panel's eave, R['pitch'] apart, R['size'] square, from the eave up `depth` metres (to the wall line; None:
    as far as the panel goes), each stopping short of a hip"""
    sz = R['size']
    for a, b in P.eaves():
        w0, w1 = sorted((P.w(*a), P.w(*b)))
        n = max(1, int((w1 - w0) / R['pitch']))
        for i in range(n + 1):
            w = w0 + .1 + (w1 - w0 - .2) * i / n; s_ = P.span(w)
            if not s_: continue
            L = s_[1] - .15 if depth is None else min(depth, s_[1] - .15)
            if L < .3: continue
            A = P.top(*P.at(w, .03)) - Vector((0, 0, P.t)); B = P.top(*P.at(w, L)) - Vector((0, 0, P.t))
            beam(bm, A, B, sz, sz, lift=-sz / 2)


LINE = {'ridge': (.5, .6, .15), 'hip': (.34, .36, .1), 'verge': (.3, .32, .08), 'flash': (.36, .3, .06), 'base': (.3, .3, .08), 'valley': (.5, .08, .02)}


def lines(bm, ls):
    """the ridges, hips, verges and valleys along the lines where a roof's panels meet: (kind, a, b) with a, b on the tiles' top"""
    for kind, a, b in ls:
        w, h, below = LINE[kind]
        beam(bm, a, b, w, h, ROOF, lift=h / 2 - below)
        if kind == 'ridge':   # the round tiles along its top and its plain ends, a little higher
            a, b = Vector(a), Vector(b); t = (b - a); L = t.length; t.normalize()
            cylinder_along(bm, a + Vector((0, 0, h - below)), t, Vector((-t.y, t.x, 0)), .16, -.25, L + .25, seg=10, mat=ROOF, caps=(True, True))
            for e, sg in ((a, -1), (b, 1)): beam(bm, e + t * (sg * .2), e - t * (sg * .55), w + .1, h + .35, ROOF, lift=(h + .35) / 2 - below)


def draw_roof(bm, panels, ls, S, depth=None):
    for P in panels:
        slab(bm, P); tiles(bm, P, S['tile']); rafters(bm, P, S['rafter'], depth)
    lines(bm, ls)


def hip_roof(cx, cy, W, D, E, rise, t):
    """a hipped roof (庑殿) over the eave rectangle W x D (W along x, W >= D) round (cx, cy): its tiles' top at the eave E, the ridge
    rise over it"""
    hD = D / 2; p = rise / hD; hx = max(0.0, W / 2 - hD); X0, X1, Y0, Y1 = cx - W / 2, cx + W / 2, cy - hD, cy + hD; zr = E + rise
    P = [Panel([(X0, Y0), (X1, Y0), (cx + hx, cy), (cx - hx, cy)], (cx, Y0), (0, 1), E, p, t),
         Panel([(X1, Y1), (X0, Y1), (cx - hx, cy), (cx + hx, cy)], (cx, Y1), (0, -1), E, p, t),
         Panel([(X1, Y0), (X1, Y1), (cx + hx, cy)], (X1, cy), (-1, 0), E, p, t),
         Panel([(X0, Y1), (X0, Y0), (cx - hx, cy)], (X0, cy), (1, 0), E, p, t)]
    L = [('ridge', (cx - hx, cy, zr), (cx + hx, cy, zr))] if hx > .3 else []
    L += [('hip', (X, Y, E), (cx + (hx if X > cx else -hx), cy, zr)) for X in (X0, X1) for Y in (Y0, Y1)]
    return P, L, []


def xieshan_roof(cx, cy, W, D, E, rise, t, s=None):
    """a hip-and-gable roof (歇山) over the eave rectangle W x D (W along x) round (cx, cy): a hipped skirt to the gables, set s
    in from the ends (a quarter of D), a gable roof over them -> panels, lines, gables (x of the gable, its base y0, y1, base z,
    apex z, its outward sign)"""
    hD = D / 2; p = rise / hD; s = D / 4 if s is None else s; gx = W / 2 - s; zg, zr = E + p * s, E + rise
    X0, X1, Y0, Y1 = cx - W / 2, cx + W / 2, cy - hD, cy + hD
    P = [Panel([(X0, Y0), (X1, Y0), (cx + gx, Y0 + s), (cx + gx, cy), (cx - gx, cy), (cx - gx, Y0 + s)], (cx, Y0), (0, 1), E, p, t),
         Panel([(X1, Y1), (X0, Y1), (cx - gx, Y1 - s), (cx - gx, cy), (cx + gx, cy), (cx + gx, Y1 - s)], (cx, Y1), (0, -1), E, p, t),
         Panel([(X1, Y0), (X1, Y1), (cx + gx, Y1 - s), (cx + gx, Y0 + s)], (X1, cy), (-1, 0), E, p, t),
         Panel([(X0, Y1), (X0, Y0), (cx - gx, Y0 + s), (cx - gx, Y1 - s)], (X0, cy), (1, 0), E, p, t)]
    L = [('ridge', (cx - gx, cy, zr), (cx + gx, cy, zr))]
    for sg in (-1, 1):
        x_, X_ = cx + sg * gx, cx + sg * W / 2
        L += [('hip', (X_, Y0, E), (x_, Y0 + s, zg)), ('hip', (X_, Y1, E), (x_, Y1 - s, zg)),
              ('verge', (x_, Y0 + s, zg), (x_, cy, zr)), ('verge', (x_, Y1 - s, zg), (x_, cy, zr)), ('base', (x_, Y0 + s, zg), (x_, Y1 - s, zg))]
    G = [(cx + sg * gx, Y0 + s, Y1 - s, zg, zr, sg) for sg in (-1, 1)]
    return P, L, G


def gable_roof(cx, cy, W, D, E, rise, t):
    """a gable roof (悬山) W long (x) over the eave lines D apart, its ends overhanging the gables -> panels, lines"""
    hD = D / 2; p = rise / hD; X0, X1, Y0, Y1 = cx - W / 2, cx + W / 2, cy - hD, cy + hD
    P = [Panel([(X0, Y0), (X1, Y0), (X1, cy), (X0, cy)], (cx, Y0), (0, 1), E, p, t),
         Panel([(X1, Y1), (X0, Y1), (X0, cy), (X1, cy)], (cx, Y1), (0, -1), E, p, t)]
    return P, [('ridge', (X0 + .3, cy, E + rise), (X1 - .3, cy, E + rise))], []


def gables(bm, G, panels, t):
    """the gable boards (山花) under a hip-and-gable's gable ends, a little in, and the bargeboards along the verges"""
    for x_, y0, y1, zg, zr, sg in G:
        cy = (y0 + y1) / 2; xb = x_ - sg * .25
        tri = [(xb, y0, zg - .05), (xb, y1, zg - .05), (xb, cy, zr - t - .05)]
        for d in (0, .15): face(bm, [(q[0] - sg * d, q[1], q[2]) for q in (tri if sg > 0 else tri[::-1])])
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            face(bm, [a, b, (b[0] - sg * .15, b[1], b[2]), (a[0] - sg * .15, a[1], a[2])])
        for ye in (y0, y1):   # the bargeboard: on the verge's end face, hanging below it
            a, b = Vector((x_ + sg * .05, ye, zg)), Vector((x_ + sg * .05, cy, zr))
            beam(bm, a, b, .1, .55, lift=-.12)


def bargeboards(bm, x_, y0, y1, E, zr, sg):
    """a gable roof's bargeboards at its end x_ (the verge from each eave to the ridge)"""
    cy = (y0 + y1) / 2
    for ye in (y0, y1): beam(bm, (x_ + sg * .05, ye, E), (x_ + sg * .05, cy, zr), .1, .55, lift=-.12)


def ring_roof(outer, inner, E, p, t, gaps=()):
    """a lean-to all round a body (a walk's roof against its platform, a first-floor eave round an upper storey): the eave on the
    outer rectangle (X0, X1, Y0, Y1), rising to the inner one (x0, x1, y0, y1), hips from the outer corners; gaps (side 's', 'e',
    'n', 'w', from, to) along a side where it opens (a stair, a gallery through it) -> panels, lines (hips; flashings along the wall)"""
    X0, X1, Y0, Y1 = outer; x0, x1, y0, y1 = inner
    dS, dN, dW, dE = y0 - Y0, Y1 - y1, x0 - X0, X1 - x1
    HSW = (X0 + max(dS, dW), Y0 + max(dS, dW)); HSE = (X1 - max(dS, dE), Y0 + max(dS, dE))
    HNE = (X1 - max(dN, dE), Y1 - max(dN, dE)); HNW = (X0 + max(dN, dW), Y1 - max(dN, dW))
    side = {'s': ([(X0, Y0), (X1, Y0), HSE] + ([(x1, y0)] if dE > dS else []) + ([(x0, y0)] if dW > dS else []) + [HSW], (0, Y0), (0, 1)),
            'e': ([(X1, Y0), (X1, Y1), HNE] + ([(x1, y1)] if dN > dE else []) + ([(x1, y0)] if dS > dE else []) + [HSE], (X1, 0), (-1, 0)),
            'n': ([(X1, Y1), (X0, Y1), HNW] + ([(x0, y1)] if dW > dN else []) + ([(x1, y1)] if dE > dN else []) + [HNE], (0, Y1), (0, -1)),
            'w': ([(X0, Y1), (X0, Y0), HSW] + ([(x0, y0)] if dS > dW else []) + ([(x0, y1)] if dN > dW else []) + [HNW], (X0, 0), (1, 0))}
    panels = []
    for k, (poly, e0, n) in side.items():
        pieces = [poly]
        for sd, a, b in gaps:
            if sd != k: continue
            ax = 0 if k in 'sn' else 1; nxt = []
            for q in pieces:
                lo = clip(q, *((-1, 0) if ax == 0 else (0, -1)), -a); hi = clip(q, *((1, 0) if ax == 0 else (0, 1)), b)
                nxt += [r for r in (lo, hi) if len(r) >= 3]
            pieces = nxt
        panels += [Panel(q, e0, n, E, p, t) for q in pieces]
    on_inner = lambda q: (abs(q[0] - x0) < 1e-6 or abs(q[0] - x1) < 1e-6) and y0 - 1e-6 <= q[1] <= y1 + 1e-6 or (abs(q[1] - y0) < 1e-6 or abs(q[1] - y1) < 1e-6) and x0 - 1e-6 <= q[0] <= x1 + 1e-6
    L = []
    for C, H in (((X0, Y0), HSW), ((X1, Y0), HSE), ((X1, Y1), HNE), ((X0, Y1), HNW)):
        P_ = next(P for P in panels if any(math.dist(C, q) < 1e-6 for q in P.poly))
        hit = [q for P in panels for q in P.poly if math.dist(q, H) < 1e-6]
        if hit: L.append(('hip', P_.top(*C), P_.top(*H)))
    for P in panels:   # the flashing along the wall: the edges of each piece on the inner rectangle
        m = len(P.poly)
        for i in range(m):
            a, b = P.poly[i], P.poly[(i + 1) % m]
            if on_inner(a) and on_inner(b) and (abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6): L.append(('flash', P.top(*a), P.top(*b)))
    return panels, L, []


# ---- for the kit: timber framing

BRACKET = {'arm': .72, 'bolster': .4}   # a bracket's height: block, arm and small blocks (一斗二升); block and bolster (替木)


def bracket(bm, x, y, z0, ang, kind='arm', cross=False):
    """a bracket on a post's head at z0: a bearing block (栌斗), tapering down, then an arm along ang with a small block at
    each end (一斗二升), or a bolster (替木) along ang; cross: a second arm or bolster square to it (a corner post)"""
    c, s = math.cos(ang), math.sin(ang)
    if kind == 'arm':
        block(bm, x, y, z0, z0 + .18, .36, .5, ang); block(bm, x, y, z0 + .18, z0 + .32, .5, ang=ang)
        for a in ((ang,) + ((ang + math.pi / 2,) if cross else ())):
            ca, sa = math.cos(a), math.sin(a); z = z0 + .32
            prof = [(-.6, z), (.6, z), (.75, z + .12), (.75, z + .24), (-.75, z + .24), (-.75, z + .12)]   # the arm, its ends rounded off below
            A = (x - sa * .1, y + ca * .1); B = (x + sa * .1, y - ca * .1)
            pts = [[(p[0] + ca * q, p[1] + sa * q, zz) for q, zz in prof] for p in (A, B)]
            face(bm, pts[0][::-1]); face(bm, pts[1])
            for k in range(6): face(bm, [pts[0][k], pts[0][(k + 1) % 6], pts[1][(k + 1) % 6], pts[1][k]])
            for e in (-.6, .6): block(bm, x + ca * e, y + sa * e, z + .24, z + .4, .26, ang=a)
        return z0 + BRACKET['arm']
    block(bm, x, y, z0, z0 + .14, .32, .44, ang); block(bm, x, y, z0 + .14, z0 + .26, .44, ang=ang)
    for a in ((ang,) + ((ang + math.pi / 2,) if cross else ())):
        block(bm, x, y, z0 + .26, z0 + .4, 1.2, ang=a, b0=.2)
    return z0 + BRACKET['bolster']


def post(bm, x, y, z0, z1, r):
    """a round timber post on a stone base (柱础) from the floor z0 to its head z1"""
    block(bm, x, y, z0 - .05, z0 + .1, r * 3, r * 2.6); block(bm, x, y, z0 + .1, z0 + .16, r * 2.6, r * 2.3)
    kit.cylinder(bm, x, y, z0 + .16, z1, r, seg=12)


def framed_row(bm, pts, z_under, r, kind, floor, arch=True, cross_ends=False, done=None):
    """posts along a straight row (plan points, in order) carrying a purlin under a roof: z_under(x, y) the rafters' foot over a
    post (the roof's underside less its rafters); each post's head so its bracket and the purlin (.25) reach it; a beam along
    their heads (阑额). done: the posts already standing (a corner two rows share), not drawn again -> the posts' heads"""
    if len(pts) < 1: return []
    ang = math.atan2(pts[-1][1] - pts[0][1], pts[-1][0] - pts[0][0]) if len(pts) > 1 else 0.0
    heads = []; done = set() if done is None else done
    for i, (x, y) in enumerate(pts):
        zt = z_under(x, y) - .25 - BRACKET[kind]; key = (round(x, 3), round(y, 3))
        if key not in done:
            done.add(key); post(bm, x, y, floor, zt, r); bracket(bm, x, y, zt, ang, kind, cross=cross_ends and i in (0, len(pts) - 1))
        heads.append((x, y, zt))
    if len(pts) > 1:
        zt = min(h[2] for h in heads); a, b = pts[0], pts[-1]
        if arch: beam(bm, (a[0], a[1], zt - .16), (b[0], b[1], zt - .16), r * .9, .32)   # the beam along the heads
        zp = zt + BRACKET[kind] + .125; c, s = math.cos(ang), math.sin(ang)
        beam(bm, (a[0] - c * .5, a[1] - s * .5, zp), (b[0] + c * .5, b[1] + s * .5, zp), .25, .25)   # the purlin
    return heads


def spaced(a, b, bay, n_min=1, floor=False):
    """points from a to b (plan) at about `bay` apart (floor: at least `bay`, as the film's generator counts them), both ends included"""
    L = math.dist(a, b); n = max(n_min, int(L // bay) if floor else round(L / bay))
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]


# ---- for the kit: walls with openings

def wall(bm, a, b, out, z0, top, t, holes=(), pil=(), mat=STONE):
    """a wall of plastered earth along a -> b (the plan points of its outer face), out its outward plan normal, t thick (in), from
    z0 up to top(x, y) (the roof's underside over it), welded to the roof's slope. holes: (u0, u1, za, zb, kind) openings along it
    (u metres from a; 'door' or 'window'), each a niche dark at its back, framed in timber, a door with its threshold, a window
    barred (直棂); pil: wall posts (壁柱) at those u, a little proud of the face, to under its brackets -> the posts' heads [(x,
    y, z)] for their brackets, 'head' (u) giving each post's head height"""
    ax, ay = a; L = math.dist(a, b); ex, ey = (b[0] - ax) / L, (b[1] - ay) / L; ox, oy = out
    P = lambda u, k, z: (ax + ex * u - ox * k, ay + ey * u - oy * k, z)
    n = max(1, math.ceil(L / .25)); us = [L * i / n for i in range(n + 1)]
    zs = [top(*P(u, t / 2, 0)[:2]) + .05 for u in us]
    TU = [(us[0], zs[0])]   # (the top as a polyline: its kinks)
    for i in range(1, n):
        u0, z0_ = TU[-1]; z_ = z0_ + (zs[i + 1] - z0_) * (us[i] - u0) / (us[i + 1] - u0)
        if abs(z_ - zs[i]) > .004: TU.append((us[i], zs[i]))
    TU.append((us[-1], zs[-1]))
    tf = lambda u: next(z1 + (z2 - z1) * (u - u1) / max(1e-9, u2 - u1) for (u1, z1), (u2, z2) in zip(TU, TU[1:]) if min(u, L) <= u2 + 1e-9)
    fit = []   # (an opening that does not fit in the wall, or runs into another, is left out: a smaller building than the defaults')
    for hh in sorted(holes):
        if hh[0] >= .4 and hh[1] <= L - .4 and (not fit or hh[0] >= fit[-1][1] + .5): fit.append(hh)
    holes = fit
    ub = sorted(set([round(u, 6) for u, _ in TU] + [round(q, 6) for h in holes for q in h[:2]]))
    Z = sorted(set([z0] + [q for h in holes for q in h[2:4]]))
    if Z[-1] > min(z for _, z in TU) - .1: raise ValueError(f'taixie: an opening reaches the top of a wall ({Z[-1]:.2f} m, top {min(z for _, z in TU):.2f} m)')
    hole = lambda u0, u1, z1, z2: any(h[0] - 1e-6 <= u0 and u1 <= h[1] + 1e-6 and h[2] - 1e-6 <= z1 and z2 <= h[3] + 1e-6 for h in holes)
    for u0, u1 in zip(ub, ub[1:]):
        t0, t1 = tf(u0), tf(u1)
        for z1, z2 in zip(Z, Z[1:]):
            if not hole(u0, u1, z1, z2): face(bm, [P(u0, 0, z1), P(u1, 0, z1), P(u1, 0, z2), P(u0, 0, z2)], mat)
        face(bm, [P(u0, 0, Z[-1]), P(u1, 0, Z[-1]), P(u1, 0, t1), P(u0, 0, t0)], mat)
        face(bm, [P(u1, t, z0), P(u0, t, z0), P(u0, t, t0), P(u1, t, t1)], mat)
        face(bm, [P(u0, 0, t0), P(u1, 0, t1), P(u1, t, t1), P(u0, t, t0)], mat)
    for u, sg in ((0.0, 1), (L, -1)):
        side = [P(u, 0, z) for z in Z] + [P(u, 0, tf(u)), P(u, t, tf(u)), P(u, t, z0)]
        face(bm, side if sg < 0 else side[::-1], mat)
    wb = lambda u0, u1, k0, k1, z1, z2, m=STONE: [face(bm, [P(*q) for q in f_], m) for f_ in (
        ((u0, k0, z1), (u1, k0, z1), (u1, k0, z2), (u0, k0, z2)), ((u1, k1, z1), (u0, k1, z1), (u0, k1, z2), (u1, k1, z2)),
        ((u0, k1, z1), (u0, k0, z1), (u0, k0, z2), (u0, k1, z2)), ((u1, k0, z1), (u1, k1, z1), (u1, k1, z2), (u1, k0, z2)),
        ((u0, k0, z2), (u1, k0, z2), (u1, k1, z2), (u0, k1, z2)), ((u0, k1, z1), (u1, k1, z1), (u1, k0, z1), (u0, k0, z1)))]
    nd = min(t - .1, .4)
    for u0, u1, za, zb, kind in holes:   # the niche: its sides, head and sill dark, its back dark; the frame and the bars white
        for q in (((u0, 0, za), (u0, nd, za), (u0, nd, zb), (u0, 0, zb)), ((u1, nd, za), (u1, 0, za), (u1, 0, zb), (u1, nd, zb)),
                  ((u0, 0, zb), (u0, nd, zb), (u1, nd, zb), (u1, 0, zb)), ((u0, nd, za), (u0, 0, za), (u1, 0, za), (u1, nd, za)),
                  ((u0, nd, za), (u1, nd, za), (u1, nd, zb), (u0, nd, zb))):
            face(bm, [P(*p) for p in q], DARK)
        fw = .18
        wb(u0 - fw, u0, -.06, .05, za if kind == 'door' else za - fw, zb + fw); wb(u1, u1 + fw, -.06, .05, za if kind == 'door' else za - fw, zb + fw)
        wb(u0 - fw, u1 + fw, -.06, .05, zb, zb + fw)
        if kind == 'door': wb(u0, u1, -.06, .2, za, za + .12)
        else:
            wb(u0 - fw, u1 + fw, -.06, .05, za - fw, za)
            nb = max(2, round((u1 - u0) / .18))
            for i in range(1, nb): wb(u0 + (u1 - u0) * i / nb - .03, u0 + (u1 - u0) * i / nb + .03, nd * .4, nd * .4 + .06, za, zb)
    heads = []
    for u, zt in pil:
        if any(h[0] - .5 < u < h[1] + .5 for h in holes): continue
        wb(u - .18, u + .18, -.1, .05, z0, zt); heads.append(P(u, -.1, zt))
    return heads


# ---- the building

def half(S, gal):
    """one terrace, centred on the origin, its front (south) toward -y; gal: the gallery leaves its east face (+x) -> {name: bmesh}"""
    w, d, h = S['w_m'], S['d_m'], S['h_m']; T = S['roof_t']; RS = S['rafter']['size']
    B = {k: bmesh.new() for k in ('platform', 'rooms', 'walk', 'terrace', 'halls', 'main', 'stair', 'roof_walk', 'roof_halls', 'roof_main')}
    X0, Y0, X1, Y1 = w / 2, d / 2, w * S['top'][0] / 2, d * S['top'][1] / 2
    Xz = lambda z: X0 - (X0 - X1) * z / h; Yz = lambda z: Y0 - (Y0 - Y1) * z / h
    fh = S['floor_h']

    # ---- the platform, the rooms' doors in its south and north faces (as the film: their middles, widths and heads)
    rd_w, rd_h, rd_z = S['room_door']
    def doors(n):
        if n <= 0: return []
        dw = min(rd_w, w * .8 / n * .4)
        return [(-w * .4 + w * .8 * (i + .5) / n - dw / 2, -w * .4 + w * .8 * (i + .5) / n + dw / 2) for i in range(n)]
    DS, DN = doors(S['rooms'][0]), doors(S['rooms'][1] if len(S['rooms']) > 1 else 0)
    za, zb = fh + S['sill'], rd_z + min(rd_h, h * .6)
    Z = [0.0] + ([za, zb] if DS or DN else []) + [h]
    bmp = B['platform']
    for sg, D_ in ((-1, DS), (1, DN)):   # the south and north faces, in cells round the doors (no T-junctions: the rows share them)
        xs = sorted(set(q for dd in D_ for q in dd))
        for j, (z1, z2) in enumerate(zip(Z, Z[1:])):
            cols = [None] + xs + [None]
            for i, (xa, xb) in enumerate(zip(cols, cols[1:])):
                if j == 1 and any(abs(xa - a) < 1e-9 and abs(xb - b) < 1e-9 for a, b in D_ if xa is not None and xb is not None): continue
                xa1 = -Xz(z1) if xa is None else xa; xa2 = -Xz(z2) if xa is None else xa
                xb1 = Xz(z1) if xb is None else xb; xb2 = Xz(z2) if xb is None else xb
                q = [(xa1, sg * Yz(z1), z1), (xb1, sg * Yz(z1), z1), (xb2, sg * Yz(z2), z2), (xa2, sg * Yz(z2), z2)]
                face(bmp, q if sg < 0 else q[::-1], EARTH)
    for sg in (-1, 1):   # the east and west faces
        for z1, z2 in zip(Z, Z[1:]):
            q = [(sg * Xz(z1), Yz(z1), z1), (sg * Xz(z1), -Yz(z1), z1), (sg * Xz(z2), -Yz(z2), z2), (sg * Xz(z2), Yz(z2), z2)]
            face(bmp, q if sg < 0 else q[::-1], EARTH)
    top = [(-X1, -Y1, h)] + [(x, -Y1, h) for x in sorted(set(q for dd in DS for q in dd))] + [(X1, -Y1, h), (X1, Y1, h)] + \
          [(x, Y1, h) for x in sorted(set(q for dd in DN for q in dd), reverse=True)] + [(-X1, Y1, h)]
    face(bmp, top, EARTH)
    bmr = B['rooms']
    for sg, D_ in ((-1, DS), (1, DN)):   # each door a niche of even depth in the battered face, a timber frame in it leaning with it
        yf = lambda z, sg=sg: sg * Yz(z); yb = lambda z, sg=sg: sg * (Yz(z) - .6)
        for xa, xb in D_:
            for q, m in ((((xa, yf(za), za), (xa, yb(za), za), (xa, yb(zb), zb), (xa, yf(zb), zb)), EARTH), (((xb, yb(za), za), (xb, yf(za), za), (xb, yf(zb), zb), (xb, yb(zb), zb)), EARTH),
                         (((xa, yf(zb), zb), (xa, yb(zb), zb), (xb, yb(zb), zb), (xb, yf(zb), zb)), EARTH), (((xa, yb(za), za), (xa, yf(za), za), (xb, yf(za), za), (xb, yb(za), za)), EARTH),
                         (((xa, yb(za), za), (xb, yb(za), za), (xb, yb(zb), zb), (xa, yb(zb), zb)), DARK)):   # (the sides cut in the earth, the doorway dark)
                face(bmr, q if sg < 0 else q[::-1], m)
            fr = lambda x, z, k=.1, sg=sg: (x, yb(z) + sg * k, z)   # (a point k in front of the niche's back)
            for x in (xa + .14, xb - .14): beam(bmr, fr(x, za), fr(x, zb), .28, .12)
            beam(bmr, fr(xa, zb - .17), fr(xb, zb - .17), .12, .34)
            beam(bmr, fr(xa, za + .05, .45), fr(xb, za + .05, .45), .9, .1)   # the threshold
    # ---- the walk round the foot: floor, apron, posts on the film's lines, its lean-to roof from the film's eave to the face
    WK = S['walk']; bw, bd = w * WK['body'][0], d * WK['body'][1]; dep = WK['depth']; eh = min(WK['h'], h * WK['h_share'])
    XO, YO = bw / 2 + dep + .4, bd / 2 + dep + .4; XP, YP = bw / 2 + dep - .3, bd / 2 + dep - .3; XF, YF = bw / 2 + dep, bd / 2 + dep
    p_w = WK['rise'] / (dep + .8)
    zi = eh + p_w * (YO - Yz(eh + WK['rise']))
    xi, yi = Xz(zi) - .3, Yz(zi) - .3   # (the roof's high edge in the face)
    st = S['stair']; sx = w * st['x']; sw = st['w']; sgw = sw + 1.2
    G = S['gallery']; ggw = G['w'] + 1.2
    gaps = [('s', sx - sgw / 2, sx + sgw / 2)] + ([('e', -ggw / 2, ggw / 2)] if gal else [])
    panels, ls, _ = ring_roof((-XO, XO, -YO, YO), (-xi, xi, -yi, yi), eh, p_w, T * .85, gaps)
    for P_ in panels: P_.t = T * .85
    draw_roof(B['roof_walk'], panels, ls, S)
    bmw = B['walk']; zu = lambda x, y: under(panels, x, y) - RS
    prism(bmw, [(-XF, -YF), (XF, -YF), (XF, -Y0 + .25), (-XF, -Y0 + .25)], -.1, fh)   # the floor (into the platform's foot)
    prism(bmw, [(-XF, Y0 - .25), (XF, Y0 - .25), (XF, YF), (-XF, YF)], -.1, fh)
    for sg in (-1, 1): prism(bmw, [(sg * (X0 - .25), -Y0 + .25), (sg * XF, -Y0 + .25), (sg * XF, Y0 - .25), (sg * (X0 - .25), Y0 - .25)][::sg], -.1, fh)
    aw, br = S['apron']['w'], S['apron']['brick']; XA, YA = XF + aw, YF + aw
    for poly in ([(-XA, -YA), (XA, -YA), (XA, -YF), (-XA, -YF)], [(-XA, YF), (XA, YF), (XA, YA), (-XA, YA)],
                 [(-XA, -YF), (-XF, -YF), (-XF, YF), (-XA, YF)], [(XF, -YF), (XA, -YF), (XA, YF), (XF, YF)]):
        prism(bmw, poly, -.1, .12)   # the pebble apron
    for a, b in (((-XA, -YA), (XA, -YA)), ((XA, -YA), (XA, YA)), ((XA, YA), (-XA, YA)), ((-XA, YA), (-XA, -YA))):   # its edge of square bricks
        L = math.dist(a, b); n = max(1, int(L / (br + .02))); ex, ey = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        for i in range(n):
            c = (a[0] + ex * (i + .5) * L / n - ey * br / 2, a[1] + ey * (i + .5) * L / n + ex * br / 2)
            block(bmw, c[0], c[1], .05, .17, br, ang=math.atan2(ey, ex))
    # the posts: along each side between its corners and its gaps, on the film's line, as many as the film's bays
    rows = []
    for k, a, b in (('s', (-XP, -YP), (XP, -YP)), ('e', (XP, -YP), (XP, YP)), ('n', (XP, YP), (-XP, YP)), ('w', (-XP, YP), (-XP, -YP))):
        cuts = sorted([(lo, hi) for sd, lo, hi in gaps if sd == k])
        ax = 0 if k in 'sn' else 1; sgn = 1 if b[ax] > a[ax] else -1
        stops = [a[ax]]
        for lo, hi in (cuts if sgn > 0 else [(hi, lo) for lo, hi in cuts[::-1]]): stops += [lo, hi]
        stops.append(b[ax])
        for s0, s1 in zip(stops[::2], stops[1::2]):
            pa = (s0, a[1]) if ax == 0 else (a[0], s0); pb = (s1, a[1]) if ax == 0 else (a[0], s1)
            if abs(s1 - s0) > .5: rows.append((k, spaced(pa, pb, WK['bay'], floor=True)))
    seen, done = set(), set()
    for k, pts in rows:
        heads = framed_row(bmw, pts, zu, S['post_r']['walk'], 'bolster', fh, cross_ends=True, done=done)
        for (x, y, zt) in heads:   # a tie from each post's head into the platform (not at the corners)
            if (round(x, 3), round(y, 3)) in seen: continue
            seen.add((round(x, 3), round(y, 3)))
            if abs(abs(x) - XP) < 1e-6 and abs(abs(y) - YP) < 1e-6: continue
            zt_ = zt - .3
            if k in 'sn': beam(bmw, (x, y, zt_), (x, math.copysign(Yz(zt_) - .25, y), zt_), .2, .26)
            else: beam(bmw, (x, y, zt_), (math.copysign(Xz(zt_) - .25, x), y, zt_), .2, .26)
    for k in 'sewn':   # the wall plate along each face under the roof's high edge (open where the stair and the gallery pass)
        zp = None
        if k in 'sn':
            yy = math.copysign(Yz(zi - .7) - .05, -1 if k == 's' else 1); zp = under_any(panels, [(x_, yy) for x_ in (xi * .5, -xi * .5, 0.0)]) - RS - .02
            cuts = sorted([(lo, hi) for sd, lo, hi in gaps if sd == k]); stops = [-Xz(zp)] + [q for c_ in cuts for q in c_] + [Xz(zp)]
            for s0, s1 in zip(stops[::2], stops[1::2]): beam(bmw, (s0, yy, zp), (s1, yy, zp), .3, .26, lift=-.13)
        else:
            xx = math.copysign(Xz(zi - .7) - .05, 1 if k == 'e' else -1); zp = under_any(panels, [(xx, y_) for y_ in (yi * .5, -yi * .5, 0.0)]) - RS - .02
            cuts = sorted([(lo, hi) for sd, lo, hi in gaps if sd == k]); stops = [-Yz(zp)] + [q for c_ in cuts for q in c_] + [Yz(zp)]
            for s0, s1 in zip(stops[::2], stops[1::2]): beam(bmw, (xx, s0, zp), (xx, s1, zp), .3, .26, lift=-.13)

    # ---- the top: the upper tier and its steps, the low walls at the edge (open where the stair arrives and the gallery leaves)
    U = S['upper']; uw, ud, uy = w * U['w'], d * U['d'], d * U['y']; zf = h + U['h']
    bmt = B['terrace']
    kit.box(bmt, -uw / 2, uw / 2, uy - ud / 2, uy + ud / 2, h - .05, zf - .15)
    kit.box(bmt, -uw / 2 - .08, uw / 2 + .08, uy - ud / 2 - .08, uy + ud / 2 + .08, zf - .15, zf)   # its edge, a coping
    M = S['main']; mw, md = min(uw * M['w'], M['w_max']), min(ud * M['d'], M['d_max']); my = uy + M['dy']
    cw, cd = S['main_room_m'] or (mw * .52, md * .81)
    ns = max(1, round(U['h'] / .2)); sw_ = cw   # the steps up to the tier before the main hall
    for i in range(ns - 1):   # (the tier is the top step)
        kit.box(bmt, -sw_ / 2, sw_ / 2, uy - ud / 2 - .38 * (ns - 1 - i) - .08, uy - ud / 2, h - .05, h + U['h'] * (i + 1) / ns)
    PA = S['parapet']; pt, ph = PA['t'], PA['h']
    cop = [(-pt / 2 - .12, 0), (pt / 2 + .12, 0), (pt / 2 + .12, .1), (0, .26), (-pt / 2 - .12, .1)]
    def low_wall(a, b):   # a low wall of earth, plastered, and its tiled coping
        if math.dist(a, b) < .5: return
        L = math.dist(a, b); ex, ey = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        poly = [(a[0] - ey * pt / 2, a[1] + ex * pt / 2), (b[0] - ey * pt / 2, b[1] + ex * pt / 2), (b[0] + ey * pt / 2, b[1] - ex * pt / 2), (a[0] + ey * pt / 2, a[1] - ex * pt / 2)]
        prism(bmt, poly, h - .05, h + ph - .26)
        section(bmt, [(q, h + ph - .26 + z) for q, z in cop], (a[0] - ex * .1, a[1] - ey * .1), (b[0] + ex * .1, b[1] + ey * .1), ROOF)
    fy, fx = d * PA['front_y'], w * PA['front_len'] / 2
    for s0, s1 in ((-fx - pt / 2, sx - sw / 2 - .15), (sx + sw / 2 + .15, fx + pt / 2)): low_wall((s0, fy), (s1, fy))
    sxw = w * PA['side_x']; sy0, sy1 = fy - pt / 2, d * PA['side_y'] + d * PA['side_len'] / 2
    for sg in (-1, 1):
        if gal and sg > 0:
            for s0, s1 in ((sy0, min(sy1, -G['w'] / 2 - .3)), (G['w'] / 2 + .3, sy1)):
                if s1 > s0: low_wall((sg * sxw, s0), (sg * sxw, s1))
        else: low_wall((sg * sxw, sy0), (sg * sxw, sy1))

    # ---- the halls round the court: a north range and two side ranges (a U), single storey, one hip-and-gable roof whose side
    # ranges end in gables to the south and run into the north range's roof (valleys inside, hips outside)
    HL = S['halls']; hd, hh = HL['d'], HL['h']; hb, hr = hh * .56, hh * .44; oh = min(1.8, .1 * hd + .4)
    ny0, ny1 = uy + ud / 2 - hd, uy + ud / 2; sl = ud - HL['side_cut']; sy0_ = uy + HL['side_dy'] - sl / 2
    xo, xi_, yno, yni, ys = uw / 2 + oh, uw / 2 - hd - oh, ny1 + oh, ny0 - oh, sy0_ - oh
    hD = hd / 2 + oh; p_h = hr / hD; Eh = zf + hb; zr = Eh + hr; xr = xo - hD; yr = (yno + yni) / 2; s_h = (hd + 2 * oh) / 4
    hp = []; hl = [('ridge', (-xr, yr, zr), (xr, yr, zr))]; hg = []
    for sg in (-1, 1):
        f = lambda poly: [(sg * x, y) for x, y in poly][::sg]
        hp += [Panel(f([(-xo, ys), (-xo, yno), (-xr, yr), (-xr, ys + s_h), (-xo + s_h, ys + s_h)][::-1]), (sg * -xo, 0), (sg, 0), Eh, p_h, T),
               Panel(f([(-xi_, ys), (-xi_ - s_h, ys + s_h), (-xr, ys + s_h), (-xr, yr), (-xi_, yni)]), (sg * -xi_, 0), (-sg, 0), Eh, p_h, T),
               Panel(f([(-xo, ys), (-xi_, ys), (-xi_ - s_h, ys + s_h), (-xo + s_h, ys + s_h)]), (0, ys), (0, 1), Eh, p_h, T)]
        hl += [('ridge', (sg * xr, ys + s_h, zr), (sg * xr, yr, zr)), ('hip', (sg * xo, yno, Eh), (sg * xr, yr, zr)),
               ('valley', (sg * xi_, yni, Eh), (sg * xr, yr, zr)),
               ('hip', (sg * xo, ys, Eh), (sg * (xo - s_h), ys + s_h, Eh + p_h * s_h)), ('hip', (sg * xi_, ys, Eh), (sg * (xi_ + s_h), ys + s_h, Eh + p_h * s_h)),
               ('verge', (sg * (xo - s_h), ys + s_h, Eh + p_h * s_h), (sg * xr, ys + s_h, zr)), ('verge', (sg * (xi_ + s_h), ys + s_h, Eh + p_h * s_h), (sg * xr, ys + s_h, zr)),
               ('base', (sg * (xo - s_h), ys + s_h, Eh + p_h * s_h), (sg * (xi_ + s_h), ys + s_h, Eh + p_h * s_h))]
    hp += [Panel([(-xo, yno), (xo, yno), (xr, yr), (-xr, yr)], (0, yno), (0, -1), Eh, p_h, T),
           Panel([(-xi_, yni), (-xr, yr), (xr, yr), (xi_, yni)], (0, yni), (0, 1), Eh, p_h, T)]
    draw_roof(B['roof_halls'], hp, hl, S, depth=oh + .3)
    bmh = B['roof_halls']
    for sg in (-1, 1):   # the side ranges' gables to the south (the board turned to face y)
        yg = ys + s_h; zg = Eh + p_h * s_h; yb_ = yg + .25
        tri = [(sg * (xo - s_h), yb_, zg - .05), (sg * (xi_ + s_h), yb_, zg - .05), (sg * xr, yb_, zr - T - .05)]
        for dd in (0, .15): face(bmh, [(q[0], q[1] + dd, q[2]) for q in tri])
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])): face(bmh, [a, b, (b[0], b[1] + .15, b[2]), (a[0], a[1] + .15, a[2])])
        for xe in (sg * (xo - s_h), sg * (xi_ + s_h)): beam(bmh, (xe, yg - .05, zg), (sg * xr, yg - .05, zr), .1, .55, lift=-.12)
    zh = lambda x, y: under(hp, x, y)
    bmH = B['halls']; ht = S['wall_t']['hall']; hu = lambda x, y: zh(x, y) - RS - .2   # (the purlin's foot over a wall post)
    X_, Xi = uw / 2, uw / 2 - hd
    dz, wz = (zf, zf + min(2.2, hb - .35)), (zf + .9, zf + min(1.9, hb - .4))
    def openings(L, spec):   # openings along a wall: [(share along, width, kind)]
        return [(L * f_ - wd / 2, L * f_ + wd / 2, *(dz if k_ == 'door' else wz), k_) for f_, wd, k_ in spec]
    walls = []
    for sg in (-1, 1):
        f = lambda q: (sg * q[0], q[1])
        walls += [(f((-X_, sy0_)), f((-X_, ny1)), (-sg, 0), [(i / 3, 1.2, 'window') for i in (1, 2)]),                         # the side range's outer wall
                  (f((-Xi, ny0)), f((-Xi, sy0_)), (sg, 0), [(.25, 1.6, 'door'), (.5, 1.2, 'window'), (.75, 1.6, 'door')]),   # its court side
                  (f((-Xi, sy0_)), f((-X_, sy0_)), (0, -1), [(.5, 1.6, 'door')])]                                          # its south end
    walls += [((-X_, ny1), (X_, ny1), (0, 1), [(i / 8, 1.2, 'window') for i in range(1, 8)]),
              ((Xi, ny0), (-Xi, ny0), (0, -1), [(f_, 1.6, 'door') for f_ in ((Xi - (Xi - mw / 2) / 2 + Xi) / (2 * Xi), ((Xi - mw / 2) / 2) / (2 * Xi))] if Xi - mw / 2 > 2.6 else [])]   # (its doors either side of the main hall)
    for a, b, o_, op in walls:
        L = math.dist(a, b)
        holes = openings(L, op)
        pil = [(u, hu(a[0] + (b[0] - a[0]) * u / L + o_[0] * .1, a[1] + (b[1] - a[1]) * u / L + o_[1] * .1) - BRACKET['bolster']) for u in [L * i / max(1, round(L / 3.6)) for i in range(round(L / 3.6) + 1)][1:-1]]
        heads = wall(bmH, a, b, o_, zf, zh, ht, holes, pil)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for x, y, z in heads: bracket(bmH, x + o_[0] * .1, y + o_[1] * .1, z, ang, 'bolster')
        if heads:
            zp = heads[0][2] + BRACKET['bolster'] + .1
            beam(bmH, (a[0] + o_[0] * .2, a[1] + o_[1] * .2, zp), (b[0] + o_[0] * .2, b[1] + o_[1] * .2, zp), .2, .2)

    # ---- the main hall: its lower storey (the room and the side rooms east and west of it behind a walk of posts), the first
    # floor's eave (a lean-to round the upper storey), the upper storey and its roof
    bmm = B['main']; mt = S['wall_t']['main']; z1 = zf + M['h1']
    ux, uyh = mw * M['k2'] / 2, md * M['k2'] / 2; zu2 = zf + M['z2']; E2 = zu2 + M['h2']
    pent, pls, _ = ring_roof((-mw / 2 - M['eave1'], mw / 2 + M['eave1'], my - md / 2 - M['eave1'], my + md / 2 + M['eave1']),
                             (-ux + .2, ux - .2, my - uyh + .2, my + uyh - .2), z1 + .3, S['pent_pitch'], T)
    W2, D2 = 2 * ux + 2 * M['eave2'], 2 * uyh + 2 * M['eave2']
    build_roof = {'hip': hip_roof, 'gable': gable_roof}.get(S['roof_main'], xieshan_roof)
    up, uls, ug = build_roof(0.0, my, W2, D2, E2, M['rise'], T + .05)
    draw_roof(B['roof_main'], pent, pls, S); draw_roof(B['roof_main'], up, uls, S, depth=M['eave2'] + .3)
    gables(B['roof_main'], ug, up, T + .05)
    if S['roof_main'] == 'gable':
        for sg in (-1, 1): bargeboards(B['roof_main'], sg * W2 / 2, my - D2 / 2, my + D2 / 2, E2, E2 + M['rise'], sg)
    zp1 = lambda x, y: under(pent, x, y)
    yw = my - md / 2 + (md - cd) / 2   # the room's front wall (the walk before it)
    ys_ = my - md / 2 + .3
    framed_row(bmm, spaced((-mw / 2 + .3, ys_), (mw / 2 - .3, ys_), 3.2), lambda x, y: zp1(x, y) - RS, S['post_r']['main'], 'arm', zf, cross_ends=False)
    nd_s, nd_n = S['main_doors'][0], S['main_doors'][1] if len(S['main_doors']) > 1 else 0
    dh = min(3.6, M['h1'] - 1.2)
    side_w = (mw - cw) / 2
    lw = [((mw / 2, yw), (-mw / 2, yw), (0, -1),
           [(mw / 2 - (-cw / 2 + cw * (i + .5) / nd_s), 2.2, zf, zf + dh, 'door') for i in range(nd_s)] +
           ([(mw / 2 - xm, 1.6, zf + 1.8, zf + 3.0, 'window') for xm in (-(cw / 2 + side_w / 2), cw / 2 + side_w / 2)] if side_w > 2 else [])),
          ((-mw / 2, yw), (-mw / 2, my + md / 2), (-1, 0), [((my + md / 2 - yw) / 2, 1.6, zf + 1.8, zf + 3.0, 'window')]),
          ((mw / 2, my + md / 2), (mw / 2, yw), (1, 0), [((my + md / 2 - yw) / 2, 1.6, zf + 1.8, zf + 3.0, 'window')]),
          ((-mw / 2, my + md / 2), (mw / 2, my + md / 2), (0, 1), [(mw / 2 + (-cw / 2 + cw * (i + .5) / nd_n), 2.2, zf, zf + dh, 'door') for i in range(nd_n)])]
    for a, b, o_, op in lw:
        L = math.dist(a, b); holes = [(u - wd / 2, u + wd / 2, z_a, z_b, k_) for u, wd, z_a, z_b, k_ in op]
        n_ = max(1, round(L / 3.2)); us_ = [L * i / n_ for i in range(1, n_)]
        pil = [(u, zp1(a[0] + (b[0] - a[0]) * u / L + o_[0] * .25, a[1] + (b[1] - a[1]) * u / L + o_[1] * .25) - RS - .25 - BRACKET['arm']) for u in us_]
        heads = wall(bmm, a, b, o_, zf, zp1, mt, holes, pil)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for x, y, z in heads: bracket(bmm, x + o_[0] * .15, y + o_[1] * .15, z, ang, 'arm')
        if heads:
            zp = heads[0][2] + BRACKET['arm'] + .125
            beam(bmm, (a[0] + o_[0] * .25, a[1] + o_[1] * .25, zp), (b[0] + o_[0] * .25, b[1] + o_[1] * .25, zp), .25, .25)
    zr2 = lambda x, y: under(up, x, y)
    ut = S['wall_t']['upper']; wb_ = (zf + 7.6, zf + 8.8)   # the upper storey's windows (the film's dark band)
    for a, b, o_ in (((ux, my - uyh), (-ux, my - uyh), (0, -1)), ((-ux, my - uyh), (-ux, my + uyh), (-1, 0)),
                     ((-ux, my + uyh), (ux, my + uyh), (0, 1)), ((ux, my + uyh), (ux, my - uyh), (1, 0))):
        L = math.dist(a, b); n_ = max(2, round(L / 3.4)); us_ = [L * i / n_ for i in range(n_ + 1)]
        holes = [(L * (i + .5) / n_ - L / n_ * .3, L * (i + .5) / n_ + L / n_ * .3, *wb_, 'window') for i in range(n_)]
        pil = [(u, zr2(a[0] + (b[0] - a[0]) * u / L + o_[0] * .25, a[1] + (b[1] - a[1]) * u / L + o_[1] * .25) - RS - .25 - BRACKET['arm']) for u in us_[1:-1]]
        heads = wall(bmm, a, b, o_, zu2, zr2, ut, holes, pil)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for x, y, z in heads: bracket(bmm, x + o_[0] * .15, y + o_[1] * .15, z, ang, 'arm')
        zc = zr2(a[0] + o_[0] * .25, a[1] + o_[1] * .25) - RS - .25 - BRACKET['arm']   # the corner posts and their brackets
        block(bmm, a[0] + o_[0] * .02, a[1] + o_[1] * .02, zu2, zc, .5); bracket(bmm, a[0] + o_[0] * .1, a[1] + o_[1] * .1, zc, ang, 'arm', cross=True)
        zp = zc + BRACKET['arm'] + .125
        beam(bmm, (a[0] + o_[0] * .25, a[1] + o_[1] * .25, zp), (b[0] + o_[0] * .25, b[1] + o_[1] * .25, zp), .25, .25)

    # ---- the stair up the south face: its foot solid, its flight over the walk on a beam and two posts; cheeks and railings
    bms = B['stair']; run = d * .025 + 5.2 + h * 1.05; ny_ = max(3, round(h / S['riser'])); r_, g_ = h / ny_, run / ny_
    yfoot = -Y1 - run; qs = YF - Y1; qs = run - qs; tv = .75
    prof = [(0, -.1), (qs, -.1), (qs, h * qs / run - tv), (run, h - tv), (run, h)]
    for i in range(ny_ - 1, -1, -1): prof += [(i * g_, (i + 1) * r_), (i * g_, i * r_)]
    prof[-1] = (0, max(0.0, prof[-1][1]))
    if prof[-1][1] <= 0: prof.pop()
    PQ = lambda x, q, z: (x, yfoot + q, z)
    for xs_, sg in ((sx - sw / 2, 1), (sx + sw / 2, -1)):
        cap = [PQ(xs_, q, z) for q, z in prof]; face(bms, cap if sg > 0 else cap[::-1], EARTH)
    n_ = len(prof)
    for k in range(n_):
        (q1, z1_), (q2, z2_) = prof[k], prof[(k + 1) % n_]
        face(bms, [PQ(sx - sw / 2, q1, z1_), PQ(sx - sw / 2, q2, z2_), PQ(sx + sw / 2, q2, z2_), PQ(sx + sw / 2, q1, z1_)][::-1], EARTH)
    cprof = [(0, -.1), (qs, -.1), (qs, h * qs / run - tv), (run, h - tv), (run, h + .3), (0, r_ + .3)]
    for sg in (-1, 1):   # the cheeks, a little over the steps' noses
        x0_ = sx + sg * sw / 2; x1_ = x0_ + sg * .3
        A = [PQ(x0_, q, z) for q, z in cprof]; Bc = [PQ(x1_, q, z) for q, z in cprof]
        face(bms, A); face(bms, Bc[::-1])
        for k in range(6): face(bms, [A[k], Bc[k], Bc[(k + 1) % 6], A[(k + 1) % 6]])
        xr_ = x0_ + sg * .15; nr = max(3, round(run / 1.6))
        for i in range(nr + 1):
            q = run * i / nr; z_ = r_ + .3 + (h - r_) * q / run
            kit.box(bms, xr_ - .07, xr_ + .07, yfoot + q - .07, yfoot + q + .07, z_ - .05, z_ + .95)
        for zz in (.5, .95): beam(bms, PQ(xr_, 0, r_ + .3 + zz), PQ(xr_, run, h + .3 + zz), .1, .12)
    zsof = h * qs / run - tv   # the beam and posts carrying the flight over the walk
    zsb = h * (qs + .2) / run - tv
    beam(bms, PQ(sx - sw / 2 - .4, qs + .2, zsb - .2), PQ(sx + sw / 2 + .4, qs + .2, zsb - .2), .4, .4)
    for sg in (-1, 1): post(bms, sx + sg * (sw / 2 + .15), yfoot + qs + .2, fh, zsb - .4, S['post_r']['stair'] * 1.5)
    return B


def gallery(S):
    """the covered gallery between the twins (飞阁): its deck on two beams from one platform's top edge to the other's, the piers
    under it, posts on its deck with railings between, brackets and purlins, its gable roof -> (bmesh, roof bmesh)"""
    w, h, mir = S['w_m'], S['h_m'], S['mirror_m']; G = S['gallery']; gw = G['w']; T = S['roof_t']; RS = S['rafter']['size']
    bm, bmr = bmesh.new(), bmesh.new(); mats_x = w / 2 + mir / 2 - w * S['top'][0] / 2   # (the platforms' top edges, either side of the middle)
    kit.box(bm, -mats_x, mats_x, -gw / 2, gw / 2, h - .25, h)   # the deck
    for sg in (-1, 1): kit.box(bm, -mats_x - .8, mats_x + .8, sg * (gw / 2 - .35) - .25, sg * (gw / 2 - .35) + .25, h - .85, h - .25)   # its beams
    nj = max(2, round(2 * mats_x / 2.4))
    for i in range(1, nj): x = -mats_x + 2 * mats_x * i / nj; kit.box(bm, x - .12, x + .12, -gw / 2 + .1, gw / 2 - .1, h - .55, h - .25)
    pa, pb = G['pier']
    for sg in (-1, 1):   # the piers, rammed earth, a timber sill over each
        x = sg * mir * G['pier_x']
        block(bm, x, 0, -.1, h - 1.05, pa, pa - .3, b0=pb, b1=pb - .3, mat=EARTH)
        kit.box(bm, x - pa / 2 + .1, x + pa / 2 - .1, -gw / 2 + .1, gw / 2 - .1, h - 1.05, h - .85)
    Lr = mir + .04 * w - 2.0; n = max(3, int(Lr // G['bay'])); py = gw / 2 - .45
    W_, D_ = Lr + 2 * G['eave'] * .6, gw + 2 * G['eave']; E = h + G['post_h']
    panels, ls, _ = gable_roof(0.0, 0.0, W_, D_, E, G['rise'], T)
    draw_roof(bmr, panels, ls, S, depth=G['eave'] + .8)
    for sg in (-1, 1): bargeboards(bmr, sg * W_ / 2, -D_ / 2, D_ / 2, E, E + G['rise'], sg)
    zu = lambda x, y: under(panels, x, y) - RS
    for sg in (-1, 1):
        pts = [(-Lr / 2 + Lr * i / n, sg * py) for i in range(n + 1)]
        heads = framed_row(bm, pts, zu, S['post_r']['gallery'], 'arm', h)
        rh = (.15, .95)   # the railing between the posts: rails and bars (直棂)
        for z in rh: beam(bm, (pts[0][0], sg * py, h + z), (pts[-1][0], sg * py, h + z), .1, .1)
        for (x0, _), (x1, _) in zip(pts, pts[1:]):
            nb = max(2, round((x1 - x0) / .3))
            for i in range(1, nb): xb = x0 + (x1 - x0) * i / nb; kit.box(bm, xb - .03, xb + .03, sg * py - .03, sg * py + .03, h + .2, h + .9)
    for sg in (-1, 1):   # the trusses at the ends: a tie beam, a king post and the principal rafters under the roof
        x = sg * Lr / 2; zt = zu(x, py) - .25
        beam(bm, (x, -py - .3, zt), (x, py + .3, zt), .25, .3)
        zr = E + G['rise'] - T - RS
        kit.box(bm, x - .12, x + .12, -.12, .12, zt, zr)
        for s2 in (-1, 1): beam(bm, (x, s2 * (py + .3), zt + .1), (x, 0, zr), .22, .25, lift=-.12)
    return bm, bmr


def build(s):
    S = spec_of(s); mats = [kit.stone(), kit.dark(), kit.material('sand', (.78, .70, .55)), kit.roof()]
    objs = []
    if S['mirror_m'] > 0:
        cx = S['w_m'] / 2 + S['mirror_m'] / 2
        for name, bm in half(S, gal=True).items():
            if not bm.faces: bm.free(); continue
            bmesh.ops.translate(bm, vec=(-cx, 0, 0), verts=bm.verts)
            east = bm.copy(); bmesh.ops.scale(east, vec=(-1, 1, 1), verts=east.verts); bmesh.ops.reverse_faces(east, faces=east.faces)
            objs += [kit.obj('west_' + name, bm, mats), kit.obj('east_' + name, east, mats)]
        g, gr = gallery(S)
        objs += [kit.obj('gallery', g, mats), kit.obj('gallery_roof', gr, mats)]
    else:
        for name, bm in half(S, gal=False).items():
            if bm.faces: objs.append(kit.obj('centre_' + name, bm, mats))
            else: bm.free()
    return objs

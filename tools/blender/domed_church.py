"""A domed church on a cross plan (St Peter's in Rome, St Paul's in London, the Invalides in Paris ...) as a detailed model: its
blocks (nave, arms, crossing) dressed in a giant order of pilasters with its entablature and an attic, windows in their bays and
roofs; half-round apses; over the crossing a round base, the drum with its buttresses, paired columns and pedimented windows, the
ribbed dome with rows of dormers, the lantern with its paired columns, the ball and the cross; smaller domes on blocks of their
own; and the front: a wall in two storeys behind a giant order of columns and pilasters, its entablature, the pediment, the attic
with its windows and the balustrade, and in its bays doors, windows with balconies, niches and passages.

It is drawn from a `parts` landmark as the film has it (from_landmark): every block, apse, ring and column the film gives keeps
its place and size, read by the parts' ids (`roles`: which part is the drum, which the shell ...; an id with * is a pattern).
What the film does not give (mouldings, the order's members on the blocks, the openings, the dormers) is a default here: an
estimate after the building as it stands, and the part it shapes says so on the page. Objects (each taken by a page part's
labels): one per block, apse and smaller dome (the part's id); the crossing's pieces (the id of the part each draws: base, drum,
drum columns, drum cornice, shell, lantern, lantern columns, ball, cross); and the front's: <front> (the wall with its
openings, the plinth, the course between the storeys), <front>_pediment, the giant columns and the giant pilasters (the id of
their parts less the number: facade_giant_columns), <front>_entablature, <front>_openings (frames, pediments, balconies, the
loggia) and <front>_attic (with its balustrade).

Frames: the landmark's (x along the whole, y to its left, z up, metres, the plan centred on its place); build.py turns it."""
import fnmatch
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

import kit

STONE, DARK, ROOF = 0, 1, 2   # (materials: kit.stone, kit.dark, kit.roof: a roof's covering, shaded as the film's roofs)
UP = Vector((0.0, 0.0, 1.0))

ROLES = {   # which of the landmark's parts is which (ids; * a pattern)
    'base': 'attic', 'drum': 'drum', 'drum_columns': 'drum_columns*', 'drum_cornice': 'drum_cornice', 'shell': 'shell',
    'lantern': 'lantern', 'lantern_columns': 'lantern_columns*', 'ball': 'ball', 'cross': 'cross', 'cross_bar': 'cross_bar',
    'front': 'facade', 'front_forward': ['facade_central_projection', 'facade_*_end'], 'front_columns': 'facade_giant_columns*',
    'front_pilasters': 'facade_giant_pilasters*', 'front_pediment': 'facade_pediment',
    'front_entablature': ['facade_entablature', 'facade_main_cornice'], 'front_attic': 'facade_attic*', 'front_parapet': 'facade_parapet',
    'front_loggia': 'facade_loggia_balcony'}

DEFAULT = {
    # ---- the building (the film's New St Peter's, for a build without a landmark; with one, from_landmark gives these)
    'bodies': [   # blocks: centre, turn (degrees: its across axis from the whole's x), across, along, height; aisles beside a nave; roof
        {'id': 'western_body', 'at': [-18.0, 0.0], 'theta_deg': 90.0, 'w_m': 64.0, 'd_m': 112.0, 'h_m': 42.0, 'aisles': {'w_m': 15.0, 'h_m': 26.0}, 'roof': {'shape': 'flat'}},
        {'id': 'cross_arm', 'at': [-10.0, 0.0], 'theta_deg': 0.0, 'w_m': 42.0, 'd_m': 126.0, 'h_m': 42.0, 'roof': {'shape': 'gabled', 'pitch_deg': 18.0}},
        {'id': 'long_nave', 'at': [68.0, 0.0], 'theta_deg': 90.0, 'w_m': 76.0, 'd_m': 94.0, 'h_m': 42.0, 'aisles': {'w_m': 18.0, 'h_m': 26.0}, 'roof': {'shape': 'gabled', 'pitch_deg': 18.0}}],
    'apses': [{'id': 'western_apse', 'at': [-73.0, 0.0], 'theta_deg': 90.0, 'd_m': 42.0, 'h_m': 26.0, 'rise_m': 6.0, 'sweep_deg': 180.0}],
    'centre_m': [0.0, 0.0],   # the crossing's centre
    'base': {'id': 'attic', 'r_m': 25.0, 'z_m': 42.5, 'h_m': 12.5},
    'drum': {'id': 'drum', 'r_m': 25.0, 'r_in_m': 20.75, 'z_m': 55.0, 'h_m': 20.0},
    'drum_columns': {'id': 'drum_columns', 'r_m': 28.25, 'w_m': 1.2, 'angles_deg': sorted(i * 22.5 + s for i in range(16) for s in (-2.5, 2.5))},
    'drum_cornice': {'id': 'drum_cornice', 'r_m': 29.45, 'h_m': 2.0},
    'shell': {'id': 'shell', 'd_m': 46.5, 'rise_m': 35.0, 'shape': 'pointed', 'z_m': 75.0, 'ribs': {'n': 16, 'w_m': 1.4, 'h_m': .7}},
    'lantern': {'id': 'lantern', 'd_m': 8.0, 'z_m': 109.3, 'h_m': 12.719, 'rise_m': 5.451},
    'lantern_columns': {'id': 'lantern_columns', 'r_m': 4.5, 'w_m': .45, 'angles_deg': sorted(i * 45.0 + s for i in range(8) for s in (-8.0, 8.0))},
    'ball': {'id': 'ball', 'd_m': 2.5, 'z_m': 127.47},
    'cross': {'id': 'cross', 'z_m': 129.97, 'h_m': 3.33, 'w_m': .4, 'bar_m': [2.4, .4], 'bar_z_m': 132.07},
    'small_domes': [{'id': f'small_dome_{s}', 'at': [22.0, y], 'base': {'w_m': 23.0, 'd_m': 23.0, 'h_m': 42.0}, 'd_m': 20.0, 'drum_h_m': 4.0,
                     'shape': 'pointed', 'rise_m': 12.0, 'lantern': {'d_m': 3.5, 'h_m': 5.0}} for s, y in (('north', 37.0), ('south', -37.0))],
    'front': {   # in its own frame: u along it (its outside on the right), n outward, metres from the front part's centre
        'id': 'facade', 'at': [115.0, 0.0], 'u': [0.0, 1.0], 'n': [1.0, 0.0], 'length_m': 116.0, 'h_m': 32.0, 'back_m': -7.0, 'front_m': 7.0,
        'storey_m': 16.0,   # the lower storey's height (the film's tiers)
        'forward': [[-16.0, 16.0, 9.0], [34.8, 58.0, 9.0], [-58.0, -34.8, 9.0]],   # stretches standing forward: from, to, their face
        'columns': {'id': 'facade_giant_columns', 'n_m': 9.15, 'u_m': [-41.3, -28.2, -17.5, -5.7, 5.7, 17.5, 28.2, 41.3],
                    'stages': [[3.4, .95, 1.0], [2.77, 24.0, .92], [3.1, 1.93, 1.0], [3.7, .6, 1.0]]},   # base, shaft, capital, abacus: width, height, taper
        'pilasters': {'id': 'facade_giant_pilasters', 'u_m': [-56.1, -47.5, 47.5, 56.1], 'front_m': 11.0, 'w_m': [3.2, 2.5], 'z_m': [.95, 24.95, 27.48]},
        'entablature_m': [27.48, 32.7],
        'attic': {'z_m': 32.0, 'top_m': 45.5, 'n_m': [-9.0, 9.0], 'parapet_m': [44.0, 10.8]},
        'pediment': {'id': 'facade_pediment', 'w_m': 30.0, 'h_m': 7.5, 'z_m': 32.7, 'front_m': 11.0},
        'loggia': {'u_m': [-4.1, 4.1], 'z_m': [15.6, 16.0], 'front_m': 11.0}},

    # ---- what the film does not give: estimates after the building as it stands
    'order': {   # the giant order on the blocks (a lower block's scaled to its height over ref_m)
        'ref_m': 42.0,            # the wall height of the full order (the film's tallest block)
        'top_m': 27.48,           # the order's top (the front's columns, when the landmark gives them)
        'entablature_m': 32.7,    # the entablature's top (the front's cornice)
        'base_m': .95, 'capital_m': 2.53,   # the pilasters' base and capital (the front's columns')
        'bay_m': 9.0,             # between pilasters
        'plinth_m': 1.6,          # the base course
        'pilaster_m': [2.6, .5],  # width, projection
        'attic_m': [33.6, 40.6],  # the attic's pilaster strips: from, to (the crowning cornice above them, to the wall's top)
        'frame_m': [.42, .22],    # a window's frame: width, projection
        'depth_m': 1.2,           # an opening's depth (dark behind it)
        'windows': [              # in each bay: its zone, width, from, to, head (rect, arch), what crowns it (alt: triangle and segment by turns)
            {'zone': 'order', 'w': 3.0, 'z': [4.8, 13.0], 'top': 'alt'},
            {'zone': 'order', 'w': 2.6, 'z': [17.4, 22.6], 'top': 'cornice'},
            {'zone': 'attic', 'w': 2.6, 'z': [35.2, 38.8], 'top': None}]},
    'clerestory': {'drop_m': 3.0, 'strip_m': [1.8, .3], 'window_m': [2.8, 2.4, 3.6], 'cornice_m': 2.0},   # (drop: the aisle roof's rise at most, as the film's generator draws it; window: width, sill over the course, gap under the cornice)
    'base_foot_m': None,          # the crossing base's wall reaches down to (None: the lowest aisle roof)
    'drum_detail': {'podium_m': 2.6, 'buttress_m': [3.4, 2.4], 'window_m': [2.6, 59.2 - 55.0, 67.4 - 55.0], 'attic_m': 2.5},   # (window: width, from, to above the drum's foot)
    'dormers': [[7.0, 2.6, 4.0], [17.0, 2.0, 3.0], [25.0, 1.4, 2.0]],   # rows on the dome: height over its springing, width, height
    'front_detail': {
        'plinth_m': [1.0, .6], 'course_m': [-.4, .3, .5],   # the course between the storeys: from, to (round the storey's line), projection
        'bays': [   # the bays between the order's members from the centre outward (mirrored): the lower and the upper opening
            {'lower': 'portal_main', 'upper': 'loggia'}, {'lower': 'portal', 'upper': 'balcony'}, {'lower': 'portal', 'upper': 'balcony'},
            {'lower': 'niche', 'upper': 'niche_up'}, {}, {'lower': 'passage', 'upper': 'window'}],
        'openings': {   # width, from, to, spring of the arch (none: square), depth, what crowns it, a balcony, a niche (stone, not dark)
            'portal_main': {'w': 5.2, 'z': [0.0, 10.6], 'depth': 3.0, 'top': 'cornice', 'over': {'w': 3.4, 'z': [12.0, 14.6]}},
            'portal': {'w': 4.4, 'z': [0.0, 9.6], 'depth': 3.0, 'top': 'cornice', 'over': {'w': 3.0, 'z': [11.4, 14.0]}},
            'loggia': {'w': 6.0, 'z': [16.3, 25.6], 'spring': 22.6, 'depth': 4.0, 'balcony': 'loggia'},
            'balcony': {'w': 4.0, 'z': [16.5, 24.0], 'spring': 22.0, 'depth': 2.0, 'top': 'alt', 'balcony': 1.4},
            'niche': {'w': 2.6, 'z': [2.4, 8.4], 'spring': 7.1, 'depth': .9, 'top': 'seg', 'niche': True},
            'niche_up': {'w': 2.6, 'z': [17.0, 23.2], 'spring': 21.9, 'depth': .9, 'top': 'tri', 'niche': True, 'balcony': .9},
            'passage': {'w': 4.4, 'z': [0.0, 10.0], 'spring': 7.8, 'depth': 6.0},
            'window': {'w': 3.0, 'z': [17.0, 23.4], 'spring': 21.9, 'depth': 1.5, 'top': 'seg', 'balcony': .9}},
        'attic_window': {'w': 3.4, 'z': [37.4, 41.0], 'depth': 1.2},
        'attic_m': [32.7, 33.6, 42.8, 44.0],   # the attic's base course from, to; its crowning cornice from, to (the terrace behind the balustrade)
        'attic_pilaster_m': [2.8, .35], 'balustrade_m': [1.5, .44]},   # (balustrade: height, the balusters' spacing)
}


# ---- for the kit: helpers any kind with walls, openings, mouldings or round columns could use ------------------------

def finish(name, bm, mats):
    """kit.obj without recalc_face_normals: every helper here winds its faces outward itself (an open wall's face has no
    inside for recalc to find, and it turned whole walls inward, culled from outside)"""
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bad = [f for f in bm.faces if f.calc_area() < 1e-7]
    if bad: bmesh.ops.delete(bm, geom=bad, context='FACES')
    sharp = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(40)]
    if sharp: bmesh.ops.split_edges(bm, edges=sharp)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    return o


def face(bm, pts, mat=STONE, smooth=False):
    """a face through the points, counter-clockwise seen from its outside (repeated points dropped, a sliver skipped)"""
    q = []
    for p in pts:
        p = Vector(p)
        if not q or (p - q[-1]).length > 1e-5: q.append(p)
    while len(q) > 2 and (q[0] - q[-1]).length <= 1e-5: q.pop()
    if len(q) < 3: return None
    nrm = Vector()
    for i in range(len(q)): nrm += q[i].cross(q[(i + 1) % len(q)])
    if nrm.length < 1e-8: return None
    f = bm.faces.new([bm.verts.new(p) for p in q]); f.material_index = mat; f.smooth = smooth
    return f


def ccw(poly):
    """a 2D outline counter-clockwise"""
    a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))
    return list(poly) if a > 0 else list(reversed(poly))


class Flat:
    """a flat wall's face: p(u, n, z), u along it (its outside on the right), n outward, z up; o the point at u = 0"""
    step = None

    def __init__(self, o, d):
        self.o = Vector((o[0], o[1], 0.0)); self.d = Vector((d[0], d[1], 0.0)).normalized(); self.nv = Vector((self.d.y, -self.d.x, 0.0))

    def p(self, u, n, z): return self.o + self.d * u + self.nv * n + Vector((0, 0, z))
    def T(self, u): return self.d
    def N(self, u): return self.nv
    def at(self, u): return Flat(self.p(u, 0, 0), self.d)


class Round:
    """a round wall's face: u the length round it (counter-clockwise from the angle a0), n outward of its radius r round c"""
    step = 1.6

    def __init__(self, c, r, a0=0.0):
        self.c = Vector((c[0], c[1], 0.0)); self.r = r; self.a0 = a0

    def _t(self, u): return self.a0 + u / self.r
    def p(self, u, n, z): t = self._t(u); return self.c + Vector(((self.r + n) * math.cos(t), (self.r + n) * math.sin(t), z))
    def T(self, u): t = self._t(u); return Vector((-math.sin(t), math.cos(t), 0.0))
    def N(self, u): t = self._t(u); return Vector((math.cos(t), math.sin(t), 0.0))
    def at(self, u): return Flat(self.p(u, 0, 0), self.T(u))


def bay(W, u, z=0.0):
    """kit's bay frame on the wall at u (x along -u, y outward, z up): for kit.box, kit.column, kit.lathe"""
    T, N = W.T(u), W.N(u); p = W.p(u, 0, z)
    return Matrix(((-T.x, N.x, 0, p.x), (-T.y, N.y, 0, p.y), (0, 0, 1, p.z), (0, 0, 0, 1)))


def wbox(bm, W, ua, ub, n0, n1, z0, z1, mat=STONE):
    """a box on the wall from ua to ub, n0 to n1 out of its face, z0 to z1 (on a round wall: in the tangent plane at its middle)"""
    if ub - ua < 1e-4 or n1 - n0 < 1e-4 or z1 - z0 < 1e-4: return
    kit.box(bm, -(ub - ua) / 2, (ub - ua) / 2, n0, n1, z0, z1, mat, xf=bay(W, (ua + ub) / 2))


def wprism(bm, W, poly, n0, n1, mat=STONE):
    """a flat wall's outline poly [(u, z), ...] stood out of it from n0 to n1"""
    poly = ccw(poly); m = len(poly)
    face(bm, [W.p(u, n1, z) for u, z in poly], mat)
    face(bm, [W.p(u, n0, z) for u, z in reversed(poly)], mat)
    for i in range(m):
        (ua, za), (ub, zb) = poly[i], poly[(i + 1) % m]
        face(bm, [W.p(ua, n1, za), W.p(ua, n0, za), W.p(ub, n0, zb), W.p(ub, n1, zb)], mat)


def sweep_path(bm, pts, outs, ups, prof, closed=False, ring=False, caps=True, mat=STONE, smooth=False):
    """the profile prof [(o, h), ...] carried along the path: at each point P + out * o + up * h (outs and ups mitred by the
    caller). Its faces look outward when T x up = out (T the path's direction) and the profile runs counter-clockwise in
    (o, h): from its foot out round its face to its top. closed: the path is a loop; ring: the profile is a closed outline"""
    rings = [[P + O * o + U * h for o, h in prof] for P, O, U in zip(pts, outs, ups)]
    n, m = len(rings), len(prof)
    for i in range(n if closed else n - 1):
        a, b = rings[i], rings[(i + 1) % n]
        for k in range(m if ring else m - 1):
            k1 = (k + 1) % m
            face(bm, (a[k], b[k], b[k1], a[k1]), mat, smooth)
    if caps and not closed:
        face(bm, rings[0], mat); face(bm, list(reversed(rings[-1])), mat)


def plan_path(poly, closed=False, z=0.0):
    """a plan polyline [(x, y), ...] walked with its outside on the right -> (points, outs mitred: o out of every side, ups)"""
    P = [Vector((x, y, z)) for x, y in poly]; n = len(P)
    seg = [(P[(i + 1) % n] - P[i]).normalized() for i in range(n if closed else n - 1)]
    nrm = [Vector((d.y, -d.x, 0.0)) for d in seg]
    outs = []
    for i in range(n):
        a, b = (nrm[i - 1], nrm[i % len(nrm)]) if closed else (nrm[max(0, i - 1)], nrm[min(i, len(nrm) - 1)])
        m = a + b
        outs.append(m / m.dot(b) if m.length > 1e-6 else b.copy())
    return P, outs, [UP.copy() for _ in P]


def arc_path(c, r, a0, a1, n, closed=False, z=0.0):
    """points on a circle round c, counter-clockwise from a0 to a1 (radians) in n steps; outs radial (its outside on the right)"""
    ts = [a0 + (a1 - a0) * i / n for i in range(n if closed else n + 1)]
    P = [Vector((c[0] + r * math.cos(t), c[1] + r * math.sin(t), z)) for t in ts]
    return P, [Vector((math.cos(t), math.sin(t), 0.0)) for t in ts], [UP.copy() for _ in ts]


def wall_path(W, pts_uz, n=0.0):
    """a polyline [(u, z), ...] on a flat wall walked left to right (its 'up' above it): points, outs (the wall's outward), ups
    (in the wall's plane, mitred): for a pediment's raking cornice or an arch's archivolt"""
    P = [W.p(u, n, z) for u, z in pts_uz]; N = W.N(0)
    seg = [(b - a).normalized() for a, b in zip(P, P[1:])]
    nr = [N.cross(d) for d in seg]   # (N x T: up, in the wall's plane)
    ups = []
    for i in range(len(P)):
        a, b = nr[max(0, i - 1)], nr[min(i, len(nr) - 1)]; m = a + b
        ups.append(m / m.dot(b) if m.length > 1e-6 else b.copy())
    return P, [N.copy() for _ in P], ups


def surface(bm, W, u0, u1, z0, z1, holes=(), smooth=None):
    """a wall's face from u0 to u1 and z0 to z1 less its openings, and their reveals and backs: each hole a dict with ua, ub,
    za, zb (the box it takes: an arched one's to the arch's crown), spring (an arch: its sides rise to it, then a round head),
    depth, reveal (material) and back (material, or None: open behind). Built on one grid with the openings' edges, so the
    reveals meet the face without cracks; a round wall in facets W.step long at most, shaded smooth"""
    smooth = isinstance(W, Round) if smooth is None else smooth
    r4 = lambda v: round(v, 4)
    holes = [{**h, **{k: r4(h[k]) for k in ('ua', 'ub', 'za', 'zb', 'spring') if h.get(k) is not None}} for h in holes]   # (on the grid's own values)
    us, zs = {r4(u0), r4(u1)}, {r4(z0), r4(z1)}
    for h in holes:
        us |= {r4(h['ua']), r4(h['ub'])}; zs |= {r4(h['za']), r4(h['zb'])}
        if h.get('spring') is not None: zs.add(r4(h['spring'])); us.add(r4((h['ua'] + h['ub']) / 2))
    if W.step:
        m = max(1, math.ceil((u1 - u0) / W.step)); us |= {r4(u0 + (u1 - u0) * i / m) for i in range(m)}
    U = sorted(u for u in us if u0 - 1e-6 <= u <= u1 + 1e-6); Zs = sorted(z for z in zs if z0 - 1e-6 <= z <= z1 + 1e-6)
    for i in range(len(U) - 1):
        for j in range(len(Zs) - 1):
            cu, cz = (U[i] + U[i + 1]) / 2, (Zs[j] + Zs[j + 1]) / 2
            if any(h['ua'] < cu < h['ub'] and h['za'] < cz < h['zb'] for h in holes): continue
            face(bm, [W.p(U[i], 0, Zs[j]), W.p(U[i + 1], 0, Zs[j]), W.p(U[i + 1], 0, Zs[j + 1]), W.p(U[i], 0, Zs[j + 1])], STONE, smooth)
    for h in holes: _reveal(bm, W, h, U, Zs, smooth)


def _reveal(bm, W, h, U, Zs, smooth):
    ua, ub, za, zb, sp, D = h['ua'], h['ub'], h['za'], h['zb'], h.get('spring'), h['depth']
    rm, bk = h.get('reveal', DARK), h.get('back', DARK)
    pairs = lambda v: zip(v, v[1:])
    side = [z for z in Zs if za - 1e-5 <= z <= (sp if sp is not None else zb) + 1e-5]
    bot = [u for u in U if ua - 1e-5 <= u <= ub + 1e-5]
    p = W.p
    for z_, z__ in pairs(side):
        face(bm, [p(ua, 0, z_), p(ua, -D, z_), p(ua, -D, z__), p(ua, 0, z__)], rm)
        face(bm, [p(ub, 0, z_), p(ub, 0, z__), p(ub, -D, z__), p(ub, -D, z_)], rm)
    for u_, u__ in pairs(bot):
        face(bm, [p(u_, 0, za), p(u__, 0, za), p(u__, -D, za), p(u_, -D, za)], rm)
    if sp is None:
        for u_, u__ in pairs(bot): face(bm, [p(u_, 0, zb), p(u_, -D, zb), p(u__, -D, zb), p(u__, 0, zb)], rm)
        top = [(u, zb) for u in reversed(bot)]
    else:
        r, uc, seg = (ub - ua) / 2, (ua + ub) / 2, 16
        ang = lambda u, z: math.atan2(z - sp, u - uc)
        A = [(uc + r * math.cos(math.pi * i / seg), sp + r * math.sin(math.pi * i / seg)) for i in range(seg + 1)]
        B = [(ub, z) for z in Zs if sp - 1e-6 <= z <= zb + 1e-6] + [(u, zb) for u in reversed(bot)][1:-1] + [(ua, z) for z in reversed(Zs) if sp - 1e-6 <= z <= zb + 1e-6]
        ka = [math.pi * i / seg for i in range(seg + 1)]; kb = [ang(*q) for q in B]
        i = j = 0
        while i < len(A) - 1 or j < len(B) - 1:   # the spandrels: the arch zipped to the box's edge by angle round its centre
            if j < len(B) - 1 and (i == len(A) - 1 or kb[j + 1] <= ka[i + 1]):
                face(bm, [p(*_n(A[i])), p(*_n(B[j])), p(*_n(B[j + 1]))], STONE, smooth); j += 1
            else:
                face(bm, [p(*_n(A[i])), p(*_n(B[j])), p(*_n(A[i + 1]))], STONE, smooth); i += 1
        for a, b in pairs(A):   # the soffit
            face(bm, [p(a[0], 0, a[1]), p(b[0], 0, b[1]), p(b[0], -D, b[1]), p(a[0], -D, a[1])], rm)
        top = A[1:-1]
    if bk is not None:
        ring = [(u, za) for u in bot] + [(ub, z) for z in side[1:]] + top + [(ua, z) for z in reversed(side[1:])]
        face(bm, [p(u, -D, z) for u, z in ring], bk)


def _n(q): return (q[0], 0.0, q[1])


def round_column(bm, M, z0, rc, hb, hs, hc, ha, taper=.92, seg=16, aw=None, pw=None, mat=STONE):
    """a free-standing column, turned whole (M: its foot's frame): a square plinth and an Attic base (hb), the shaft (hs) tapering
    to taper with its astragal, a Corinthian capital (hc: a bell in two rows of leaves, scrolls at its corners) and the abacus
    (ha, aw square). kit.column is the half one, engaged in a wall"""
    pw = pw or rc * 2.5; aw = aw or rc * 2.7; rt = rc * taper; T = dict(seg=seg, xf=M, mat=mat)
    zp = z0 + hb * .32; b = hb - hb * .32
    kit.box(bm, -pw / 2, pw / 2, -pw / 2, pw / 2, z0, zp, mat, xf=M)
    kit.lathe(bm, [(pw / 2 * .92, zp), (rc * 1.24, zp + b * .2), (rc * 1.2, zp + b * .38), (rc * 1.06, zp + b * .44), (rc * 1.04, zp + b * .62),
                   (rc * 1.13, zp + b * .7), (rc * 1.09, zp + b * .86), (rc * 1.02, zp + b * .93), (rc, z0 + hb)], **T)
    z1 = z0 + hb + hs; a = max(.04, hc * .07)
    kit.lathe(bm, [(rc, z0 + hb), (rt, z1 - a), (rt * 1.08, z1 - a * .7), (rt * 1.08, z1 - a * .25), (rt, z1)], **T)
    kit.lathe(bm, [(rt, z1), (rt * 1.2, z1 + hc * .3), (rt * 1.04, z1 + hc * .37), (rt * 1.34, z1 + hc * .66), (rt * 1.12, z1 + hc * .73),
                   (aw / 2 * .96, z1 + hc)], **T)
    kit.box(bm, -aw / 2, aw / 2, -aw / 2, aw / 2, z1 + hc, z1 + hc + ha, mat, xf=M)
    s = aw * .36; d = aw * .1
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):   # the corner scrolls, under the abacus's corners
        kit.box(bm, sx * s - d, sx * s + d, sy * s - d, sy * s + d, z1 + hc * .7, z1 + hc, mat, xf=M)


def pilaster(bm, M, z0, z1, w, p, hb, hc, ext=0.0, mat=STONE):
    """a pilaster (M: kit's bay frame at its middle) from z0 to z1: a base (hb) and a Corinthian capital (hc: necking, two rows of
    leaves, scrolls, abacus) each wider and deeper than the shaft; ext: it runs that far past its +u side (round a corner)"""
    def B(dw, dp, za, zb):   # (+u is the frame's -x)
        kit.box(bm, -w / 2 - (ext + dp if ext else dw), w / 2 + dw, -.05, p + dp, za, zb, mat, xf=M)
    c0 = z1 - hc
    B(.1 * w, .14 * w, z0, z0 + hb * .45); B(.06 * w, .08 * w, z0 + hb * .45, z0 + hb)
    B(0, 0, z0 + hb, c0)
    B(.02 * w, .02 * w, c0, c0 + hc * .1); B(.06 * w, .07 * w, c0 + hc * .1, c0 + hc * .42); B(.1 * w, .12 * w, c0 + hc * .42, c0 + hc * .72)
    B(.15 * w, .16 * w, c0 + hc * .72, c0 + hc * .86); B(.2 * w, .2 * w, c0 + hc * .86, z1)


def baluster_run(bm, W, u0, u1, z0, h, n1, depth, space, piers=(), pw=.7, seg=6, mat=STONE):
    """a balustrade on the wall frame W from u0 to u1, standing at z0, h high, its front n1 out, depth deep: its plinth, turned
    balusters, the rail, and piers at the u's given"""
    nc = n1 - depth / 2
    wbox(bm, W, u0, u1, n1 - depth, n1, z0, z0 + .17 * h, mat)
    wbox(bm, W, u0, u1, n1 - depth - .04, n1 + .05, z0 + .84 * h, z0 + h, mat)
    for u in piers: wbox(bm, W, u - pw / 2, u + pw / 2, n1 - depth - .08, n1 + .08, z0, z0 + h + .06, mat)
    r = depth * .3; b0, H = z0 + .17 * h, .67 * h
    prof = [(r * .75, b0), (r * .75, b0 + .07 * H), (r * .5, b0 + .12 * H), (r * .98, b0 + .42 * H), (r * .42, b0 + .76 * H), (r * .78, b0 + .87 * H), (r * .78, b0 + H)]
    m = max(1, int((u1 - u0) / space))
    for i in range(m):
        u = u0 + (i + .5) * (u1 - u0) / m
        if any(abs(u - q) < pw / 2 + r for q in piers): continue
        kit.lathe(bm, prof, seg=seg, xf=bay(W, u) @ Matrix.Translation((0, nc, 0)), mat=mat)


def pointed(hw, rise, n=24, upto=None):
    """a dome's outer profile from its springing (hw, 0) toward its top, metres, as the film's generator draws a 'pointed' one
    (two arcs meeting on the axis) or, when it rises no more than its half width, a 'saucer' (a cap of a sphere); upto: stop
    where it narrows to that radius"""
    k = rise / hw
    if k <= 1:
        rho = (1 + k * k) / (2 * k) * hw; c = 0.0; zc = rise - rho   # (a sphere of radius rho centred on the axis, below)
        a0 = math.atan2(-zc, hw); a1 = math.pi / 2
        arc = lambda t: (rho * math.cos(t), zc + rho * math.sin(t))
    else:
        rho = (k * k + 1) / 2 * hw; c = hw - rho; zc = 0.0   # (two arcs of radius rho centred c off the axis)
        a0 = 0.0; a1 = math.acos(-c / rho)
        arc = lambda t: (c + rho * math.cos(t), rho * math.sin(t))
    if upto is not None:
        a1 = math.acos((upto - c) / rho) if k > 1 else math.acos(upto / rho)
    return [arc(a0 + (a1 - a0) * i / n) for i in range(n + 1)], (c, zc, rho)


# ---- profiles (o out of the face, z) ----------------------------------------------------------------------------------

def p_band(z, h, p):
    """a band: a course between storeys, a base course"""
    return [(0, z), (p, z), (p, z + h * .55), (p * .6, z + h * .75), (p * .6, z + h), (0, z + h)]


def p_crown(z, h, p):
    """a crowning cornice"""
    return [(0, z), (p * .22, z), (p * .22, z + h * .2), (p * .42, z + h * .3), (p * .42, z + h * .5), (p, z + h * .72), (p, z + h), (0, z + h)]


def p_plinth(h, p):
    return [(p, 0), (p, h * .75), (p * .85, h * .82), (p * .85, h * .89), (p * .65, h), (0, h)]


def p_entab(z, h, p, k=1.0):
    """an entablature h high from z: architrave, frieze, cornice; p the architrave's projection"""
    return kit.entablature([[p, h * .33], [p * .9, h * .29], [p + .9 * k * h / 5.22 * 1.2, h * .38]], z)


# ---- reading the landmark ---------------------------------------------------------------------------------------------

def _glob(parts, pat):
    pats = pat if isinstance(pat, list) else [pat]
    return [q for q in parts if any(fnmatch.fnmatch(str(q.get('id') or ''), p) for p in pats)]


def _stem(pat): return (pat[0] if isinstance(pat, list) else pat).rstrip('*').rstrip('_')


def _placed(q):
    """a part's copies (its repeat): [(x, y, turn)] in the whole's frame, as the film's generator places them"""
    th = math.radians(q.get('theta_deg') or 0); ax, ay = q.get('at') or [0.0, 0.0]; r = q.get('repeat') or {}
    if 'mirror' in r:
        m = r['mirror']; out = [(ax, ay, th)]
        if 'x' in m: out.append((-ax, ay, -th))
        if 'y' in m: out.append((ax, -ay, math.pi - th))
        if m == 'xy': out.append((-ax, -ay, math.pi + th))
        return out
    if 'ring' in r:
        n, R, a0 = r['ring']['n'], r['ring']['r_m'], math.radians(r['ring']['start_deg'])
        return [(R * math.cos(a0 + i / n * math.tau), R * math.sin(a0 + i / n * math.tau), th) for i in range(n)]
    if 'line' in r:
        dx, dy = r['line']['step_m']; return [(ax + i * dx, ay + i * dy, th) for i in range(r['line']['n'])]
    return [(ax, ay, th)]


def _height(q):
    """a part's height as the generator draws it (no exaggeration): its top over its foot"""
    k = q['kind']
    if k == 'long_hall':
        R = q['roof']; ai = q.get('aisles'); nw = q['w_m'] - (2 * ai['n'] * ai['w_m'] if ai else 0); h = q['h_m'] + (q.get('podium') or {}).get('h_m', 0)
        if R['shape'] == 'flat': return h + .5
        return h + nw / 2 * math.tan(math.radians(R.get('pitch_deg') or 22))
    if k == 'dome':
        dm = q['dome']; dw = dm.get('d_m') or q['d_m']; rise = dm.get('rise_m') or .5 * dw; ln = q.get('lantern') or {}
        return (q.get('base') or {}).get('h_m', 0) + q['drum_h_m'] + rise + (q.get('ribs') or {}).get('h_m', 0) + ln.get('h_m', 0) + q.get('finial_m', 0)
    if k == 'column':
        return (q.get('pedestal') or {}).get('h_m', 0) + (sum(s['h_m'] for s in q['stages']) if q.get('stages') else q['h_m'])
    if k == 'revolve': return max(p[1] for p in q['profile_m'])
    if k == 'prism': return q['h_m'] if 'plan_m' in q else max(p[1] for p in q['section_m'])
    return q.get('h_m', 0.0)


def _feet(parts):
    """each part's foot (metres over the ground), stacked as the generator stacks them (atop: on the top of an earlier part)"""
    feet, tops = [], []
    for q in parts:
        z = (tops[q['atop']] if q.get('atop') is not None else 0.0) + (q.get('z_m') or 0.0)
        feet.append(z); tops.append(z + _height(q))
    return feet


def _ring_cols(qs, feet, parts):
    """columns repeated round a ring (a drum's, a lantern's): their radius, width, angles (degrees), foot and height"""
    angs, r, w, z, h = [], None, None, None, None
    for q in qs:
        rg = (q.get('repeat') or {}).get('ring')
        if not rg: continue
        angs += [(rg['start_deg'] + 360.0 * i / rg['n']) % 360 for i in range(rg['n'])]
        r, w, z, h = rg['r_m'], q['w_m'], feet[parts.index(q)], q['h_m']
    return {'r_m': r, 'w_m': w, 'angles_deg': sorted(angs), 'z_m': z, 'h_m': h} if angs else None


def from_landmark(L):
    """the sizes the film's `parts` landmark gives (its blocks, apses, the crossing's rings and columns, the smaller domes, the
    front), as this spec's keys; a part the roles do not find leaves the default"""
    if isinstance(L, dict) and 'parts' not in L and isinstance(L.get('landmark'), dict): L = L['landmark']
    if not isinstance(L, dict) or L.get('kind') != 'parts': return {}
    P, R = L['parts'], ROLES; feet = _feet(P)
    out = {k: None for k in ('base', 'drum', 'drum_columns', 'drum_cornice', 'shell', 'lantern', 'lantern_columns', 'ball', 'cross', 'front')}
    one = lambda role: (_glob(P, R[role]) or [None])[0]
    roled = {id(q) for role in R for q in _glob(P, R[role])}
    bodies, apses, smalls = [], [], []
    for q in P:
        if id(q) in roled: continue
        if q['kind'] == 'long_hall':
            ai = q.get('aisles')
            bodies.append({'id': q['id'], 'at': list(q.get('at') or [0, 0]), 'theta_deg': q.get('theta_deg') or 0.0, 'w_m': q['w_m'], 'd_m': q['d_m'], 'h_m': q['h_m'],
                           'aisles': {'w_m': ai['n'] * ai['w_m'], 'h_m': ai['h_m']} if ai else None,
                           'roof': {'shape': q['roof']['shape'], 'pitch_deg': q['roof'].get('pitch_deg') or 22.0}})
        elif q['kind'] == 'dome' and (q.get('sweep_deg') or 360) < 360:
            apses.append({'id': q['id'], 'at': list(q.get('at') or [0, 0]), 'theta_deg': q.get('theta_deg') or 0.0, 'd_m': q['d_m'], 'h_m': q['drum_h_m'],
                          'rise_m': q['dome'].get('rise_m') or .25 * q['d_m'], 'sweep_deg': q['sweep_deg']})
        elif q['kind'] == 'dome' and q.get('base'):
            dm = q['dome']; ln = q.get('lantern') or {}
            smalls.append({'id': q['id'], 'at': list(q.get('at') or [0, 0]), 'base': q['base'], 'd_m': q['d_m'], 'drum_h_m': q['drum_h_m'],
                           'shape': dm['shape'], 'rise_m': dm.get('rise_m') or .74 * q['d_m'], 'lantern': {'d_m': ln.get('d_m', q['d_m'] * .18), 'h_m': ln.get('h_m', 0.0)} if ln else None})
    out.update(bodies=bodies, apses=apses, small_domes=smalls)
    q = one('base')
    if q: out['base'] = {'id': q['id'], 'r_m': q['w_m'] / 2, 'z_m': feet[P.index(q)], 'h_m': q['h_m']}; out['centre_m'] = list(q.get('at') or [0.0, 0.0])
    q = one('drum')
    if q:
        rs = [p[0] for p in q['profile_m']]
        out['drum'] = {'id': q['id'], 'r_m': max(rs), 'r_in_m': min(rs), 'z_m': feet[P.index(q)], 'h_m': max(p[1] for p in q['profile_m'])}
    qs = _glob(P, R['drum_columns'])
    if qs and _ring_cols(qs, feet, P): out['drum_columns'] = {'id': qs[0]['id'], **_ring_cols(qs, feet, P)}
    q = one('drum_cornice')
    if q: out['drum_cornice'] = {'id': q['id'], 'r_m': max(p[0] for p in q['profile_m']), 'h_m': max(p[1] for p in q['profile_m'])}
    q = one('shell')
    if q:
        dm = q['dome']
        out['shell'] = {'id': q['id'], 'd_m': dm.get('d_m') or q['d_m'], 'rise_m': dm.get('rise_m') or .74 * q['d_m'], 'shape': dm['shape'],
                        'z_m': feet[P.index(q)] + q.get('drum_h_m', 0.0), 'ribs': q.get('ribs')}
    q = one('lantern')
    if q: out['lantern'] = {'id': q['id'], 'd_m': q['d_m'], 'z_m': feet[P.index(q)], 'h_m': q['drum_h_m'], 'rise_m': q['dome'].get('rise_m') or q['d_m'] / 2}
    qs = _glob(P, R['lantern_columns'])
    if qs and _ring_cols(qs, feet, P): out['lantern_columns'] = {'id': qs[0]['id'], **_ring_cols(qs, feet, P)}
    q = one('ball')
    if q: out['ball'] = {'id': q['id'], 'd_m': 2 * max(p[0] for p in q['profile_m']), 'z_m': feet[P.index(q)]}
    q, b = one('cross'), one('cross_bar')
    if q:
        out['cross'] = {'id': q['id'], 'z_m': feet[P.index(q)], 'h_m': q.get('h_m') or 3.0, 'w_m': q.get('w_m') or .4}
        if b and b.get('plan_m'):
            xs = [p[0] for p in b['plan_m']]; ys = [p[1] for p in b['plan_m']]
            out['cross'].update({'bar_m': [max(xs) - min(xs), max(ys) - min(ys)], 'bar_z_m': feet[P.index(b)], 'bar_h_m': b['h_m']})
    q = one('front')
    if q: out['front'] = _front(q, P, feet)
    return out


def _front(q, P, feet):
    """the front in its own frame (u along it, its outside on the right; n outward from the whole's centre; from its part's centre)"""
    R = ROLES; th = math.radians(q.get('theta_deg') or 0.0); ax, ay = q.get('at') or [0.0, 0.0]
    ly = Vector((-math.sin(th), math.cos(th), 0))
    N = -ly if Vector((ax, ay, 0)).dot(ly) < 0 else ly; U = UP.cross(N)
    at = Vector((ax, ay, 0)); uv = lambda x, y: ((Vector((x, y, 0)) - at).dot(U), (Vector((x, y, 0)) - at).dot(N))
    F = {'id': q['id'], 'at': [ax, ay], 'u': [U.x, U.y], 'n': [N.x, N.y], 'length_m': q['length_m'], 'h_m': q['h_m'],
         'back_m': -q['depth_m'] / 2, 'front_m': q['depth_m'] / 2, 'storey_m': q['h_m'] / max(1, q.get('tiers') or 1)}
    fw = []
    for f in _glob(P, R['front_forward']):
        u, n = uv(*f['at']); fw.append([round(u - f['length_m'] / 2, 4), round(u + f['length_m'] / 2, 4), round(n + f['depth_m'] / 2, 4)])
    F['forward'] = sorted(fw)
    cs = _glob(P, R['front_columns'])
    if cs:
        us, ns = [], []
        for c in cs:
            for x, y, _ in _placed(c): u, n = uv(x, y); us.append(round(u, 4)); ns.append(n)
        st = cs[0].get('stages') or [{'w_m': cs[0]['w_m'], 'h_m': cs[0]['h_m']}]
        F['columns'] = {'id': _stem(R['front_columns']), 'n_m': sum(ns) / len(ns), 'u_m': sorted(us), 'stages': [[s['w_m'], s['h_m'], s.get('taper', 1.0)] for s in st]}
    ps = _glob(P, R['front_pilasters'])
    if ps and ps[0].get('section_m'):
        us, fr = [], []
        for c in ps:
            for x, y, _ in _placed(c): u, n = uv(x, y); us.append(round(u, 4)); fr.append(n + c['length_m'] / 2)
        sec = ps[0]['section_m']; xs = sorted({abs(p[0]) for p in sec}); zs = sorted({p[1] for p in sec})
        F['pilasters'] = {'id': _stem(R['front_pilasters']), 'u_m': sorted(us), 'front_m': max(fr), 'w_m': [2 * xs[-1], 2 * xs[0]], 'z_m': [zs[1], zs[-2], zs[-1]]}
    es = _glob(P, R['front_entablature'])
    if es:
        z0 = min(feet[P.index(e)] for e in es); z1 = max(feet[P.index(e)] + _height(e) for e in es)
        F['entablature_m'] = [z0, z1]
    at_ = _glob(P, R['front_attic'])
    if at_:
        ns = []
        for e in at_:
            n = uv(*e['at'])[1]; d = (max(abs(p[1]) for p in e['plan_m'])) if e.get('plan_m') else e.get('depth_m', 0) / 2
            ns += [n - d, n + d]
        F['attic'] = {'z_m': min(feet[P.index(e)] for e in at_), 'top_m': max(feet[P.index(e)] + _height(e) for e in at_), 'n_m': [min(ns), max(ns)]}
        pa = (_glob(P, R['front_parapet']) or [None])[0]
        if pa and pa.get('plan_m'): F['attic']['parapet_m'] = [feet[P.index(pa)], uv(*pa['at'])[1] + max(abs(p[1]) for p in pa['plan_m'])]
    pd = (_glob(P, R['front_pediment']) or [None])[0]
    if pd and pd.get('section_m'):
        xs = [p[0] for p in pd['section_m']]; F['pediment'] = {'id': pd['id'], 'w_m': max(xs) - min(xs), 'h_m': max(p[1] for p in pd['section_m']),
                                                               'z_m': feet[P.index(pd)], 'front_m': uv(*pd['at'])[1] + pd['length_m'] / 2}
    lg = (_glob(P, R['front_loggia']) or [None])[0]
    if lg and lg.get('plan_m'):
        u, n = uv(*lg['at']); xs = [p[0] for p in lg['plan_m']]
        F['loggia'] = {'u_m': [u + min(xs), u + max(xs)], 'z_m': [feet[P.index(lg)], feet[P.index(lg)] + lg['h_m']], 'front_m': n + max(abs(p[1]) for p in lg['plan_m'])}
    return F


def spec_of(s):
    s = s or {}; out = {**DEFAULT, **s}
    for k in ('order', 'clerestory', 'drum_detail'): out[k] = {**DEFAULT[k], **(s.get(k) or {})}
    out['front'] = {**DEFAULT['front'], **(s.get('front') or {})} if out.get('front') else None
    out['front_detail'] = {**DEFAULT['front_detail'], **(s.get('front_detail') or {})}
    return out


# ---- what stands where (an element is drawn only where it does not run into another block) ----------------------------

class Solids:
    def __init__(self): self.s = []

    def poly(self, own, pts, z0, z1): self.s.append(('p', own, [(p[0], p[1]) for p in pts], z0, z1))
    def disc(self, own, c, r, z0, z1, face=None, cap=0.0): self.s.append(('d', own, (c[0], c[1]), r, z0, z1, face, cap))   # (cap: a sphere's cap that high over z1)
    def gable(self, own, c, X, Y, hw, hd, z0, rise): self.s.append(('g', own, c, X, Y, hw, hd, z0, rise))

    def inside(self, p, own, e=.03):
        for s in self.s:
            if s[1] == own: continue
            if s[0] == 'p':
                _, _, pts, z0, z1 = s
                if not (z0 + e < p.z < z1 - e): continue
                if _in_poly(p.x, p.y, pts) and min(_seg_dist(p.x, p.y, a, b) for a, b in zip(pts, pts[1:] + pts[:1])) > e: return True
            elif s[0] == 'd':
                _, _, c, r, z0, z1, fc, cap = s
                dx, dy = p.x - c[0], p.y - c[1]; rho = math.hypot(dx, dy)
                if cap > 0 and rho < r:
                    R = (r * r + cap * cap) / (2 * cap); z1 = z1 + math.sqrt(max(0.0, R * R - rho * rho)) - (R - cap)
                if not (z0 + e < p.z < z1 - e): continue
                if rho < r - e and (fc is None or dx * fc[0] + dy * fc[1] > -e): return True
            else:
                _, _, c, X, Y, hw, hd, z0, rise = s
                d = Vector((p.x - c[0], p.y - c[1], 0)); a, b = abs(d.dot(X)), abs(d.dot(Y))
                if a < hw - e and b < hd - e and z0 - 1 < p.z < z0 + rise * (1 - a / hw) - e: return True
        return False

    def clear(self, pts, own): return not any(self.inside(p, own) for p in pts)


def _in_poly(x, y, pts):
    c = False
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0: c = not c
    return c


def _seg_dist(x, y, a, b):
    ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L))
    return math.hypot(x - ax - t * dx, y - ay - t * dy)


def _clear(solids, own, W, ua, ub, n, za, zb):
    return solids.clear([W.p(u, n, z) for u in (ua, (ua + ub) / 2, ub) for z in (za, (za + zb) / 2, zb)], own)


def _block_frame(B):
    th = math.radians(B['theta_deg']); X = Vector((math.cos(th), math.sin(th), 0)); Y = Vector((-math.sin(th), math.cos(th), 0))
    A = Vector((B['at'][0], B['at'][1], 0)); return A, X, Y, (lambda x, y: A + X * x + Y * y)


def solids_of(S):
    so = Solids()
    for B in S['bodies']:
        A, X, Y, P = _block_frame(B); w, d, h = B['w_m'], B['d_m'], B['h_m']; ai = B.get('aisles')
        nw = w - 2 * ai['w_m'] if ai else w
        so.poly(B['id'], [P(-nw / 2, -d / 2), P(nw / 2, -d / 2), P(nw / 2, d / 2), P(-nw / 2, d / 2)], -1, h + (.5 if B['roof']['shape'] == 'flat' else 0))
        if ai:
            for s in (-1, 1):
                x0, x1 = sorted((s * nw / 2, s * w / 2))
                so.poly(B['id'], [P(x0, -d / 2), P(x1, -d / 2), P(x1, d / 2), P(x0, d / 2)], -1, ai['h_m'] + min(S['clerestory']['drop_m'], (h - ai['h_m']) * .6))
        if B['roof']['shape'] != 'flat':
            so.gable(B['id'], A, X, Y, nw / 2 + .3, d / 2 + .3, h, nw / 2 * math.tan(math.radians(B['roof']['pitch_deg'])))
    for Ap in S['apses']:
        th = math.radians(Ap['theta_deg']); f = (-math.sin(th), math.cos(th))
        so.disc(Ap['id'], Ap['at'], Ap['d_m'] / 2 + .4, -1, Ap['h_m'], f, cap=Ap['rise_m'])
    c = S['centre_m']; Bs = S['base']
    if Bs: so.disc(Bs['id'], c, Bs['r_m'], _base_foot(S), Bs['z_m'] + Bs['h_m'])
    for D in S['small_domes']:
        b = D['base']; x, y = D['at']
        so.poly(D['id'], [(x - b['w_m'] / 2, y - b['d_m'] / 2), (x + b['w_m'] / 2, y - b['d_m'] / 2), (x + b['w_m'] / 2, y + b['d_m'] / 2), (x - b['w_m'] / 2, y + b['d_m'] / 2)], -1, b['h_m'])
        so.disc(D['id'], (x, y), D['d_m'] / 2 + .8, b['h_m'], b['h_m'] + D['drum_h_m'] + D['rise_m'])
    F = S['front']
    if F:
        q = _fq(F)
        so.poly(F['id'], [q(u, n) for u, n in _front_outline(F)], -1, F['h_m'])
        a = F['attic']; Lh = F['length_m'] / 2
        so.poly(F['id'], [q(-Lh, a['n_m'][0]), q(Lh, a['n_m'][0]), q(Lh, a['n_m'][1]), q(-Lh, a['n_m'][1])][::-1], a['z_m'], a['top_m'])
    return so


def _base_foot(S):
    if S.get('base_foot_m') is not None: return S['base_foot_m']
    hs = [B['aisles']['h_m'] for B in S['bodies'] if B.get('aisles')]
    return min(hs) if hs else S['base']['z_m']


# ---- the walls' dress: the giant order, its windows, the clerestory --------------------------------------------------

def windows_of(bm, W, uc, w, za, zb, k, O, top, spring=None):
    """a window's frame on the wall at uc (its opening from za to zb, w wide): the architrave round it, the sill, and what crowns
    it: a cornice, or a pediment (tri, seg) over a frieze and cornice; an arched one's archivolt. -> its top. On a flat wall the
    frame stands on its face (behind it, in the opening, it would share the reveals' planes); on a round one, in the tangent
    plane at uc, it reaches back into the curve and keeps a few centimetres clear of the opening's edges"""
    fw, fp = O['frame_m'][0] * k, O['frame_m'][1] * k; V = W.at(uc)
    rnd = isinstance(W, Round); e0 = -((w / 2 + fw + .3) ** 2 / (2 * W.r) + .03) if rnd else 0.0; g = .03 if rnd else 0.0
    ua, ub = -w / 2 - g, w / 2 + g
    wbox(bm, V, ua - fw - .12 * k, ub + fw + .12 * k, e0, fp + .14 * k, za - .3 * k, za - g)   # the sill
    if spring is None:
        wbox(bm, V, ua - fw, ua, e0, fp, za - g, zb + g); wbox(bm, V, ub, ub + fw, e0, fp, za - g, zb + g)
        wbox(bm, V, ua - fw, ub + fw, e0, fp, zb + g, zb + g + fw); z = zb + g + fw
    else:
        wbox(bm, V, ua - fw, ua, e0, fp, za - g, spring); wbox(bm, V, ub, ub + fw, e0, fp, za - g, spring)
        r = w / 2 + g; n = 14
        pts = [(r * math.cos(math.pi * (1 - i / n)), spring + r * math.sin(math.pi * (1 - i / n))) for i in range(n + 1)]
        P, O_, _ = wall_path(V, pts)
        ups = [(P[i] - V.p(0, 0, spring)).normalized() for i in range(len(P))]
        sweep_path(bm, P, O_, ups, [(e0, 0), (fp, 0), (fp, fw * .45), (fp * .7, fw * .6), (fp * .7, fw), (e0, fw)])
        wbox(bm, V, -.22 * k, .22 * k, max(e0, 0.0) + .01, fp + .1 * k, spring + r - .1 * k, spring + r + fw + .1 * k)   # the keystone
        z = spring + r + fw
    if top in ('cornice', 'tri', 'seg'):
        hw = w / 2 + g + fw
        wbox(bm, V, -hw, hw, e0, fp * .7, z, z + .35 * k)
        wbox(bm, V, -hw - .2 * k, hw + .2 * k, e0, fp + .2 * k, z + .35 * k, z + .62 * k); z += .62 * k
        if top in ('tri', 'seg'): z = pediment(bm, V, 0, hw + .2 * k, z, k * .9, fp + .2 * k, top)
    return z


def pediment(bm, W, uc, hw, z, k, p, kind='tri', rise=None, apex=None):
    """a pediment on the flat wall W over uc, hw half wide, from z: its tympanum and its raking (or curved) cornice, p out of the
    wall at the tympanum's face; apex: where the cornice's top reaches (a triangle's rise is then found for it) -> its top"""
    t = .5 * k   # the cornice's height across its slope
    prof = [(-.15 - p, 0), (p * .35, 0), (p * .35, t * .35), (p * .6, t * .5), (p * .6, t * .7), (p, t * .82), (p, t), (-.15 - p, t)]
    if kind == 'tri':
        rise = rise or (apex - z - t * 1.08 if apex else hw * .42)
        if apex:
            for _ in range(6): rise = apex - z - t * math.hypot(hw, rise) / hw
        wprism(bm, W, [(uc - hw, z), (uc + hw, z), (uc, z + rise)], -.15, 0.0)
        P, O, U = wall_path(W, [(uc - hw - t * .3, z - .02), (uc, z + rise), (uc + hw + t * .3, z - .02)], n=0.0)
        sweep_path(bm, P, O, U, [(o + p * 0, h) for o, h in prof])
        return z + rise + t * math.hypot(hw, rise) / hw
    rise = rise or hw * .3; R = (hw * hw + rise * rise) / (2 * rise); zc = z + rise - R; a = math.asin(hw / R); n = 12
    pts = [(uc + R * math.sin(-a + 2 * a * i / n), zc + R * math.cos(-a + 2 * a * i / n)) for i in range(n + 1)]
    poly = [(uc - hw, z), (uc + hw, z)] + list(reversed(pts[1:-1]))
    wprism(bm, W, poly, -.15, 0.0)
    P, O, _ = wall_path(W, pts)
    ups = [(P[i] - W.p(uc, 0, zc)).normalized() for i in range(len(P))]
    sweep_path(bm, P, O, ups, prof)
    return z + rise + t


def dress(bm, W, L, top, S, so, own, k=1.0, zones=('order', 'attic'), corner=True):
    """a wall's face from the ground to top (u 0..L) in the giant order scaled by k: its pilasters at the bays (and round the
    corner at its end), the windows of each bay with their frames, and the face itself with their openings"""
    O = S['order']; n = max(1, round(L / (O['bay_m'] * k))); bw = L / n
    pw, pp = O['pilaster_m'][0] * k, O['pilaster_m'][1] * k; zp0, zo = O['plinth_m'] * k, O['top_m'] * k
    za0, za1 = O['attic_m'][0] * k, O['attic_m'][1] * k
    holes = []
    for i in range(n + 1):
        u = min(max(i * bw, pw / 2), L - pw / 2); ext = pp if (corner and i == n) else 0.0
        if 'order' in zones and _clear(so, own, W, u - pw / 2 - .3 * k, u + pw / 2 + ext + .3 * k, pp + .5 * k, zp0 + .1, zo):
            pilaster(bm, bay(W, u), zp0, zo, pw, pp, O['base_m'] * k, O['capital_m'] * k, ext)
        if 'attic' in zones and top > za1 and _clear(so, own, W, u - pw / 2, u + pw / 2 + ext, .4 * k, za0 + .1, za1):
            M = bay(W, u); e = (lambda d: d + ext if ext else d)
            kit.box(bm, -pw / 2 - e(0), pw / 2, -.05, .3 * k, za0, za1 - .5 * k, xf=M)
            kit.box(bm, -pw / 2 - e(.1 * k) if ext else -pw / 2 - .1 * k, pw / 2 + .1 * k, -.05, .42 * k, za1 - .5 * k, za1, xf=M)
    fw = O['frame_m'][0] * k
    for i in range(n):
        uc = (i + .5) * bw
        for wd in O['windows']:
            if wd['zone'] not in zones or (wd['zone'] == 'attic' and top <= za1): continue
            w, za, zb = wd['w'] * k, wd['z'][0] * k, wd['z'][1] * k; tp = wd.get('top')
            if tp == 'alt': tp = ('tri', 'seg')[i % 2]
            if w + 2 * fw + .4 * k > bw - pw - .3 * k: continue
            ztop = zb + fw + (2.3 * k if tp in ('tri', 'seg') else .62 * k if tp else 0)
            if not _clear(so, own, W, uc - w / 2 - fw - .3 * k, uc + w / 2 + fw + .3 * k, O['frame_m'][1] * k + .3, za - .35 * k, ztop): continue
            holes.append({'ua': uc - w / 2, 'ub': uc + w / 2, 'za': za, 'zb': zb, 'depth': O['depth_m'] * max(k, .7)})
            windows_of(bm, W, uc, w, za, zb, k, O, tp)
    surface(bm, W, 0, L, 0, top, holes)


def order_mouldings(bm, pts, outs, ups, S, k, top, closed=True, attic=True):
    """the giant order's mouldings along a path: the plinth, the entablature, the attic's base course and its crowning cornice"""
    O = S['order']; zo, ze = O['top_m'] * k, O['entablature_m'] * k
    sm = isinstance(pts, list) and len(pts) > 8
    run = lambda prof: sweep_path(bm, pts, outs, ups, prof, closed=closed, smooth=sm)
    run(p_plinth(O['plinth_m'] * k, (O['pilaster_m'][1] + .4) * k))
    run(p_entab(zo, ze - zo, (O['pilaster_m'][1] + .14) * k, k))
    if attic and top > O['attic_m'][1] * k:
        run(p_band(ze, O['attic_m'][0] * k - ze, .42 * k))
        run(p_crown(O['attic_m'][1] * k, top - O['attic_m'][1] * k, 1.3 * k))


def clerestory(bm, W, L, zb, zt, S, so, own):
    """the wall of a nave over its aisles' roofs: a course over the roof, pilaster strips, round-headed windows, the cornice"""
    C, O = S['clerestory'], S['order']; zv = zb + min(C['drop_m'], (zt - zb) * .6); n = max(1, round(L / O['bay_m'])); bw = L / n
    sw, spp = C['strip_m']; zc = zt - C['cornice_m']; ww, sill, gap = C['window_m']
    for i in range(n + 1):
        u = min(max(i * bw, sw / 2), L - sw / 2)
        if _clear(so, own, W, u - sw / 2, u + sw / 2, spp + .3, zv + .7, zc):
            M = bay(W, u)
            kit.box(bm, -sw / 2, sw / 2, -.05, spp, zv + .7, zc - .5, xf=M)
            kit.box(bm, -sw / 2 - .12, sw / 2 + .12, -.05, spp + .12, zc - .5, zc, xf=M)
    holes = []
    for i in range(n):
        uc = (i + .5) * bw; za = zv + .7 + sill; sp = zc - gap - ww / 2
        if sp - za < 1.0 or not _clear(so, own, W, uc - ww / 2 - .6, uc + ww / 2 + .6, .5, za - .4, sp + ww / 2 + .6): continue
        holes.append({'ua': uc - ww / 2, 'ub': uc + ww / 2, 'za': za, 'zb': sp + ww / 2, 'spring': sp, 'depth': 1.0})
        windows_of(bm, W, uc, ww, za, sp + ww / 2, 1.0, O, None, spring=sp)
    surface(bm, W, 0, L, zb, zt, holes)
    return zv


# ---- the blocks and apses ---------------------------------------------------------------------------------------------

def block(B, S, so):
    """a block: its outer walls in the order (scaled to their height), a nave's clerestory over its aisles, the mouldings, roofs"""
    bm = bmesh.new(); own = B['id']; A, X, Y, P = _block_frame(B)
    w, d, h = B['w_m'], B['d_m'], B['h_m']; ai = B.get('aisles'); nw = w - 2 * ai['w_m'] if ai else w; ah = ai['h_m'] if ai else h
    k = ah / S['order']['ref_m']
    outer = [P(-w / 2, -d / 2), P(w / 2, -d / 2), P(w / 2, d / 2), P(-w / 2, d / 2)]
    for i in range(4):
        a, b = outer[i], outer[(i + 1) % 4]; dress(bm, Flat(a, b - a), (b - a).length, ah, S, so, own, k)
    order_mouldings(bm, *plan_path([(p.x, p.y) for p in outer], True), S, k, ah)
    if ai:
        nave = [P(-nw / 2, -d / 2), P(nw / 2, -d / 2), P(nw / 2, d / 2), P(-nw / 2, d / 2)]
        for i in range(4):
            a, b = nave[i], nave[(i + 1) % 4]; zv = clerestory(bm, Flat(a, b - a), (b - a).length, ah, h, S, so, own)
        pts, outs, ups = plan_path([(p.x, p.y) for p in nave], True)
        sweep_path(bm, pts, outs, ups, p_band(zv, .7, .35), closed=True)
        sweep_path(bm, pts, outs, ups, p_crown(h - S['clerestory']['cornice_m'], S['clerestory']['cornice_m'], 1.2), closed=True)
        dr = min(S['clerestory']['drop_m'], (h - ah) * .6)
        for s in (-1, 1):   # the aisles' lean-to roofs, from the outer cornice up to the nave's wall
            m = dr / ai['w_m']; ov = .3
            sec = ccw([(s * nw / 2, ah + dr), (s * (w / 2 + ov), ah - ov * m), (s * (w / 2 + ov), ah - ov * m - .35), (s * nw / 2, ah + dr - .35)])
            sweep_path(bm, [P(0, -d / 2), P(0, d / 2)], [X, X], [UP, UP], sec, ring=True, mat=ROOF)
    R = B['roof']
    if R['shape'] == 'flat':
        kit.box(bm, -nw / 2, nw / 2, -d / 2, d / 2, h, h + .5, ROOF, xf=Matrix(((X.x, Y.x, 0, A.x), (X.y, Y.y, 0, A.y), (0, 0, 1, 0), (0, 0, 0, 1))))
    else:
        t = math.tan(math.radians(R['pitch_deg'])); ov = .3; rid = h + nw / 2 * t; e = h - ov * t
        sec = [(-(nw / 2 + ov), e - .4), (nw / 2 + ov, e - .4), (nw / 2 + ov, e), (0, rid), (-(nw / 2 + ov), e)]
        sweep_path(bm, [P(0, -d / 2 - ov), P(0, d / 2 + ov)], [X, X], [UP, UP], sec, ring=True, mat=ROOF)
        for s in (-1, 1):   # the gable ends: the tympanum and its raking cornice
            a, b = (P(s * nw / 2, s * d / 2), P(-s * nw / 2, s * d / 2))
            V = Flat(a, b - a)
            if not so.clear([V.p(nw / 2, 1.0, h + 1.0)], own): continue
            wprism(bm, V, [(0, h), (nw, h), (nw / 2, rid - .45)], -1.0, 0.0)
            pp, oo, uu = wall_path(V, [(-.4, h - .25), (nw / 2, rid - .25), (nw + .4, h - .25)])
            sweep_path(bm, pp, oo, uu, [(-.15, 0), (.5, 0), (.5, .25), (.75, .4), (.75, .9), (-.15, .9)])
    return finish(own, bm, MATS)


def apse(Ap, S, so):
    """a half-round apse: its wall in the order (scaled), the mouldings round it, the half dome"""
    bm = bmesh.new(); own = Ap['id']; th = math.radians(Ap['theta_deg'])
    phi = math.atan2(math.cos(th), -math.sin(th)); sw = math.radians(Ap['sweep_deg']); r = Ap['d_m'] / 2; h = Ap['h_m']
    a0 = phi - sw / 2; W = Round(Ap['at'], r, a0); L = r * sw; k = h / S['order']['ref_m']
    dress(bm, W, L, h, S, so, own, k, corner=False)
    order_mouldings(bm, *arc_path(Ap['at'], r, a0, a0 + sw, max(16, int(L / 1.2))), S, k, h, closed=False)
    prof, _ = pointed(r + .3 * k, Ap['rise_m'], 16, upto=.05)
    prof = [(x, h + z) for x, z in prof]
    kit.lathe(bm, prof, seg=48, x=Ap['at'][0], y=Ap['at'][1], a0=a0, a1=a0 + sw, mat=ROOF)
    for a, rev in ((a0, False), (a0 + sw, True)):   # its cut ends, on the block's wall
        pts = [Vector((Ap['at'][0] + x * math.cos(a), Ap['at'][1] + x * math.sin(a), z)) for x, z in prof] + [Vector((Ap['at'][0], Ap['at'][1], h))]
        face(bm, pts if rev else list(reversed(pts)), ROOF)
    return finish(own, bm, MATS)


# ---- the crossing ------------------------------------------------------------------------------------------------------

def _clusters(angles):
    """columns' angles grouped where they stand close (pairs: the gaps inside a group are the short ones): their middles, degrees"""
    a = sorted(x % 360 for x in angles)
    if len(a) < 2: return a
    d = [(b - x) % 360 for x, b in zip(a, a[1:] + a[:1])]
    gap = (min(d) + max(d)) / 2 if max(d) > 1.5 * min(d) else 0.0
    groups = [[a[0]]]
    for x, dx in zip(a[1:], d):
        (groups[-1].append(x) if dx < gap else groups.append([x]))
    if len(groups) > 1 and d[-1] < gap: groups[0] = [x - 360 for x in groups.pop()] + groups[0]
    return [sum(g) / len(g) for g in groups]


def _pair_half(angles, r):
    """half the span between the centres of a pair of columns on a ring of radius r (0 when they stand singly)"""
    a = sorted(x % 360 for x in angles); d = [(b - x) % 360 for x, b in zip(a, a[1:] + a[:1])]
    return r * math.sin(math.radians(min(d) / 2)) if len(a) > 1 and max(d) > 1.5 * min(d) else 0.0


def crossing(S, so):
    c = S['centre_m']; Bs, Dr, Dc, Dk, Sh = S['base'], S['drum'], S['drum_columns'], S['drum_cornice'], S['shell']
    D = S['drum_detail']; cl = _clusters(Dc['angles_deg']); rd = Dr['r_m']; z0, z1 = Dr['z_m'], Dr['z_m'] + Dr['h_m']
    rc = Dc['w_m'] / 2; plinth = rc * 2.5; r_out = Dc['r_m'] + plinth / 2 + .3
    objs = []

    # the base under the drum: its wall down to the roofs, a course where it leaves the roof, strips under the buttresses,
    # framed panels between them, and a stepped cornice reaching out under the drum's columns
    bm = bmesh.new(); own = Bs['id']; rb = Bs['r_m']; zb0, zb1 = Bs['z_m'], Bs['z_m'] + Bs['h_m']; Wb = Round(c, rb, 0.0)
    zk = zb1 - 4.4
    surface(bm, Wb, 0, math.tau * rb, _base_foot(S), zb1)
    ring = arc_path(c, rb, 0, math.tau, 128, closed=True)
    sweep_path(bm, *ring, p_band(zb0, .9, .45), closed=True, smooth=True)
    dr = r_out - rb
    sweep_path(bm, *ring, [(0, zk), (.45, zk), (.45, zk + .55), (dr * .3, zk + .8), (dr * .3, zk + 1.45), (dr * .55, zk + 1.7), (dr * .55, zk + 2.35),
                           (dr * .8, zk + 2.6), (dr * .8, zk + 3.25), (dr, zk + 3.5), (dr, zb1), (0, zb1)], closed=True, smooth=True)
    zones = [(zb0 + .9, zk)]   # (and below the roofs' line, where the wall shows between the blocks: the same in a lower storey)
    if zb0 - _base_foot(S) - S['clerestory']['drop_m'] > 4: zones.append((_base_foot(S) + S['clerestory']['drop_m'] + .4, zb0))
    for z0_, z1_ in zones:
        for a in cl:
            u = rb * math.radians(a % 360)
            if _clear(so, own, Wb, u - 1.6, u + 1.6, .6, z0_ + .1, z1_):
                kit.box(bm, -1.5, 1.5, -.1, .4, z0_, z1_, xf=bay(Wb, u))
        for a0_, a1_ in zip(cl, cl[1:] + [cl[0] + 360]):
            u = rb * math.radians(((a0_ + a1_) / 2) % 360); hw = rb * math.radians(a1_ - a0_) / 2 - 2.6
            if hw > .6 and _clear(so, own, Wb, u - hw, u + hw, .4, z0_ + .7, z1_ - .6):
                V = Wb.at(u); zA, zB = z0_ + 1.0, z1_ - .9
                for ua, ub, za, zb in ((-hw, hw, zA, zA + .3), (-hw, hw, zB - .3, zB), (-hw, -hw + .3, zA + .3, zB - .3), (hw - .3, hw, zA + .3, zB - .3)):
                    wbox(bm, V, ua, ub, -.15, .18, za, zb)
    objs.append(finish(own, bm, MATS))

    # the drum: its wall with a window in every bay, the podium and the pedestals under the columns, the buttresses, the windows'
    # frames and pediments
    bm = bmesh.new(); own = Dr['id']; a_0 = math.radians(cl[0]); W = Round(c, rd, a_0); L = math.tau * rd
    zp = z0 + D['podium_m']; holes = []
    mids = [((a + b) / 2) for a, b in zip(cl, cl[1:] + [cl[0] + 360])]
    ww, wa, wb = D['window_m']
    for i, m in enumerate(mids):
        u = rd * math.radians(m - cl[0])
        holes.append({'ua': u - ww / 2, 'ub': u + ww / 2, 'za': z0 + wa, 'zb': z0 + wb, 'depth': 1.8})
        windows_of(bm, W, u, ww, z0 + wa, z0 + wb, 1.0, S['order'], ('tri', 'seg')[i % 2])
        wbox(bm, W.at(u), -ww / 2 - .3, ww / 2 + .3, -.15, .3, z0 + wa - 1.4, z0 + wa - .3)   # the apron under the sill
    surface(bm, W, 0, L, z0, z1, holes)
    sweep_path(bm, *arc_path(c, rd, 0, math.tau, 128, closed=True), [(1.0, z0), (1.0, z0 + .5), (.7, z0 + .7), (.7, zp - .5), (.95, zp - .35), (.95, zp), (0, zp)], closed=True, smooth=True)
    bw_, bd_ = D['buttress_m']; hw = _pair_half(Dc['angles_deg'], Dc['r_m']) + plinth / 2 + .3
    for a in cl:
        u = rd * math.radians(a - cl[0]); M = bay(W, u)
        kit.box(bm, -hw, hw, -.3, r_out - rd, z0, zp - .4, xf=M)
        kit.box(bm, -hw - .15, hw + .15, -.3, r_out - rd + .15, zp - .4, zp, xf=M)
        kit.box(bm, -bw_ / 2, bw_ / 2, -.3, bd_, zp, z1, xf=M)
    objs.append(finish(own, bm, MATS))

    # the columns, in pairs on the pedestals before the buttresses
    bm = bmesh.new(); hs = z1 - zp
    for a in Dc['angles_deg']:
        t = math.radians(a); M = Matrix.Translation((c[0] + Dc['r_m'] * math.cos(t), c[1] + Dc['r_m'] * math.sin(t), 0)) @ Matrix.Rotation(t, 4, 'Z')
        round_column(bm, M, zp, rc, rc * 1.1, hs - rc * 1.1 - rc * 2.4 - rc * .4, rc * 2.4, rc * .4, seg=14)
    objs.append(finish(Dc['id'], bm, MATS))

    # the cornice: the entablature round the drum, breaking forward over each pair; the drum's attic and its pedestals
    bm = bmesh.new(); h = Dk['h_m']
    ent = kit.entablature([[.3, h * .33], [.25, h * .27], [.95, h * .4]], z1)
    sweep_path(bm, *arc_path(c, rd, 0, math.tau, 128, closed=True), ent, closed=True, smooth=True)
    rf = Dk['r_m'] - .95
    for a in cl:
        t = math.radians(a); R_ = Vector((math.cos(t), math.sin(t), 0)); T_ = Vector((-math.sin(t), math.cos(t), 0)); C = Vector((c[0], c[1], 0))
        pts = [C + R_ * (rd - .4) - T_ * hw, C + R_ * rf - T_ * hw, C + R_ * rf + T_ * hw, C + R_ * (rd - .4) + T_ * hw]
        sweep_path(bm, *plan_path([(p.x, p.y) for p in pts]), kit.entablature([[.3, h * .33], [.25, h * .27], [.95, h * .4]], z1))
    za, zt_ = z1 + h, z1 + h + D['attic_m']
    shell_r = lambda z: _shell_r(Sh, z)
    ra = shell_r(za) + 1.4
    sweep_path(bm, *arc_path(c, ra, 0, math.tau, 128, closed=True), [(0, za - .1), (0, zt_ - .45), (.25, zt_ - .35), (.25, zt_), (shell_r(zt_) - ra - .1, zt_)], closed=True, smooth=True)
    Wa = Round(c, ra, 0.0)
    for a in cl:
        u = ra * math.radians(a); M = bay(Wa, u)
        kit.box(bm, -hw + .2, hw - .2, -.4, 1.0, za - .05, zt_ - .4, xf=M)   # (a pedestal over each pair, where its rib springs)
        kit.box(bm, -hw + .05, hw - .05, -.4, 1.15, zt_ - .4, zt_, xf=M)
    for a0_, a1_ in zip(cl, cl[1:] + [cl[0] + 360]):   # a sunk panel in the attic between the pedestals
        u = ra * math.radians((a0_ + a1_) / 2); hw2 = ra * math.radians(a1_ - a0_) / 2 - hw - .4; V = Wa.at(u)
        if hw2 > .4:
            for ua, ub, zA, zB in ((-hw2, hw2, za + .3, za + .5), (-hw2, hw2, zt_ - .8, zt_ - .6), (-hw2, -hw2 + .2, za + .5, zt_ - .8), (hw2 - .2, hw2, za + .5, zt_ - .8)):
                wbox(bm, V, ua, ub, -.15, .15, zA, zB)
    objs.append(finish(Dk['id'], bm, MATS))
    objs += dome(S, so, cl)
    return objs


def _shell_r(Sh, z):
    """the shell's outer radius at height z"""
    prof, _ = pointed(Sh['d_m'] / 2, Sh['rise_m'], 96)
    zz = z - Sh['z_m']
    for (r0, h0), (r1, h1) in zip(prof, prof[1:]):
        if h0 <= zz <= h1: return r0 + (r1 - r0) * (zz - h0) / max(1e-9, h1 - h0)
    return prof[0][0] if zz < 0 else 0.0


def dome(S, so, cl):
    """the shell with its ribs and dormers; the lantern (its collar, wall with arched windows, buttresses, entablature, attic and
    cupola); its columns; the ball; the cross"""
    c = S['centre_m']; C = Vector((c[0], c[1], 0)); Sh, Ln, Lc = S['shell'], S['lantern'], S['lantern_columns']
    hw_, rise, zs = Sh['d_m'] / 2, Sh['rise_m'], Sh['z_m']; objs = []
    rl = Ln['d_m'] / 2 if Ln else .6; collar = rl + .8
    bm = bmesh.new()
    prof, (cc, zc, rho) = pointed(hw_, rise, 40, upto=collar - .6)
    kit.lathe(bm, [(r, zs + z) for r, z in prof], seg=96, x=c[0], y=c[1], mat=ROOF)
    rb = Sh.get('ribs') or {'n': 16, 'w_m': 1.4, 'h_m': .7}
    za = S['drum']['z_m'] + S['drum']['h_m'] + S['drum_cornice']['h_m'] + S['drum_detail']['attic_m'] - .2
    ribs = cl if len(cl) == rb['n'] else [360.0 * i / rb['n'] for i in range(rb['n'])]
    w2, hp = rb['w_m'] / 2, rb['h_m']
    rprof = [(-.1, -w2), (hp * .62, -w2), (hp * .7, -w2 * .78), (hp, -w2 * .6), (hp, w2 * .6), (hp * .7, w2 * .78), (hp * .62, w2), (-.1, w2)]
    sel = [(r, z) for r, z in pointed(hw_, rise, 60, upto=collar - .3)[0] if zs + z >= za]
    for a in ribs:
        t = math.radians(a); R_ = Vector((math.cos(t), math.sin(t), 0)); T_ = Vector((-math.sin(t), math.cos(t), 0))
        pts, outs, ups = [], [], []
        for r, z in sel:
            if Sh['rise_m'] > hw_: nr = Vector((r - cc, z)).normalized()
            else: nr = Vector((r, z - zc)).normalized()
            pts.append(C + R_ * r + UP * (zs + z)); outs.append(R_ * nr.x + UP * nr.y); ups.append(-T_)
        sweep_path(bm, pts, outs, ups, rprof, mat=ROOF)
    for row, (dz, dw, dh) in enumerate(S['dormers']):   # the dormers, between the ribs
        z0 = zs + dz; z1 = z0 + dh; r0, r1 = _shell_r(Sh, z0), _shell_r(Sh, z1 + dh * .35)
        for i in range(len(ribs)):
            a = (ribs[i] + (ribs[(i + 1) % len(ribs)] + (360 if i == len(ribs) - 1 else 0))) / 2; t = math.radians(a)
            M = Matrix(((-(-math.sin(t)), math.cos(t), 0, c[0]), (-math.cos(t), math.sin(t), 0, c[1]), (0, 0, 1, 0), (0, 0, 0, 1)))
            rf = r0 + .35; rb_ = r1 - .6
            kit.box(bm, -dw / 2, dw / 2, rb_, rf, z0, z1, xf=M)
            kit.box(bm, -dw / 2 - .12, dw / 2 + .12, rb_, rf + .12, z0 - .25, z0, xf=M)   # its sill
            ow, oh = dw * .46, dh * .52; oz = z0 + dh * .22
            for x0, x1, zA, zB in ((-ow / 2 - .16, -ow / 2, oz, oz + oh), (ow / 2, ow / 2 + .16, oz, oz + oh), (-ow / 2 - .16, ow / 2 + .16, oz + oh, oz + oh + .16)):
                kit.box(bm, x0, x1, rb_, rf + .14, zA, zB, xf=M)
            kit.box(bm, -ow / 2, ow / 2, rb_, rf + .06, oz, oz + oh, DARK, xf=M)
            ph = dh * .35   # its pediment, a small gable running back into the shell
            sec = [(-dw / 2 - .15, 0), (dw / 2 + .15, 0), (0, ph)]
            Rv = Vector((math.cos(t), math.sin(t), 0)); Tv = Vector((-math.sin(t), math.cos(t), 0))
            sweep_path(bm, [C + Rv * (rf + .2) + UP * z1, C + Rv * rb_ + UP * z1], [Tv, Tv], [UP, UP], [(x, z) for x, z in sec], ring=True)
    objs.append(finish(Sh['id'], bm, MATS))

    if Ln:   # the lantern
        bm = bmesh.new(); zl = Ln['z_m']; zt = zl + Ln['h_m']; rw = rl * .9
        zcol = _shell_z(Sh, collar)
        kit.lathe(bm, [(collar, zcol - .4), (collar, zl - .9), (collar + .2, zl - .7), (collar + .2, zl - .3), (rl + .9, zl)], seg=48, x=c[0], y=c[1])
        zf = zl + .7
        kit.lathe(bm, [(rl + .9, zl), (rl + .9, zf), (rw, zf)], seg=48, x=c[0], y=c[1])
        lcl = _clusters(Lc['angles_deg']) if Lc else [45.0 * i for i in range(8)]
        rcl = Lc['w_m'] / 2 if Lc else .22; ze = zt - 3.0
        W = Round(c, rw, math.radians(lcl[0])); holes = []
        for a0_, a1_ in zip(lcl, lcl[1:] + [lcl[0] + 360]):
            u = rw * math.radians((a0_ + a1_) / 2 - lcl[0]); w_ = min(1.4, rw * math.radians(a1_ - a0_) - 1.9)
            holes.append({'ua': u - w_ / 2, 'ub': u + w_ / 2, 'za': zf + .8, 'zb': ze - 1.0, 'spring': ze - 1.0 - w_ / 2, 'depth': .7})
            V = W.at(u); wbox(bm, V, -w_ / 2 - .15, w_ / 2 + .15, -.1, .2, zf + .55, zf + .8)
        surface(bm, W, 0, math.tau * rw, zf, ze + .05, holes)
        hb = (_pair_half(Lc['angles_deg'], Lc['r_m']) + rcl + .2) if Lc else .8
        for a in lcl:
            u = rw * math.radians(a - lcl[0]); M = bay(W, u)
            kit.box(bm, -hb + .25, hb - .25, -.2, (Lc['r_m'] if Lc else rl + .5) - rw - rcl - .05, zf, ze, xf=M)
        ent = kit.entablature([[.18, .4], [.15, .35], [.55, .55]], ze)
        sweep_path(bm, *arc_path(c, rw, 0, math.tau, 64, closed=True), ent, closed=True, smooth=True)
        rr = (Lc['r_m'] if Lc else rl + .5) + rcl - .3
        for a in lcl:
            t = math.radians(a); R_ = Vector((math.cos(t), math.sin(t), 0)); T_ = Vector((-math.sin(t), math.cos(t), 0))
            pts = [C + R_ * (rw - .2) - T_ * hb, C + R_ * rr - T_ * hb, C + R_ * rr + T_ * hb, C + R_ * (rw - .2) + T_ * hb]
            sweep_path(bm, *plan_path([(p.x, p.y) for p in pts]), ent)
        zat = ze + 1.3
        kit.lathe(bm, [(rw, zat - .1), (rw, zt - .25), (rw + .12, zt - .15), (rw + .12, zt), (rl, zt)], seg=48, x=c[0], y=c[1])
        for a in lcl:   # pedestals over the pairs, on the attic
            t = math.radians(a); M = Matrix.Translation((c[0], c[1], 0)) @ Matrix.Rotation(t - math.pi / 2, 4, 'Z')
            kit.box(bm, -hb * .55, hb * .55, rw - .2, rw + .45, zat, zt - .1, xf=M)
        cup = [(rl * math.cos(math.pi / 2 * i / 16), zt + Ln['rise_m'] * math.sin(math.pi / 2 * i / 16)) for i in range(16)]
        cup = [(r, z) for r, z in cup if r > .5] + [(.5, zt + Ln['rise_m'] * .985)]
        kit.lathe(bm, cup, seg=40, x=c[0], y=c[1], mat=ROOF)
        for a in lcl:   # ribs on the cupola
            t = math.radians(a); R_ = Vector((math.cos(t), math.sin(t), 0)); T_ = Vector((-math.sin(t), math.cos(t), 0))
            pts, outs, ups = [], [], []
            for r, z in cup[:-1]:
                nr = Vector((r / rl, (z - zt) / Ln['rise_m'] * (rl / Ln['rise_m']))).normalized()
                pts.append(C + R_ * r + UP * z); outs.append(R_ * nr.x + UP * nr.y); ups.append(-T_)
            sweep_path(bm, pts, outs, ups, [(-.05, -.2), (.16, -.2), (.16, .2), (-.05, .2)], mat=ROOF)
        zb_ = S['ball']['z_m'] if S.get('ball') else zt + Ln['rise_m']
        kit.lathe(bm, [(.55, zb_ - .7), (.62, zb_ - .45), (.4, zb_ - .3), (.4, zb_ + .2), (0.05, zb_ + .3)], seg=24, x=c[0], y=c[1])   # the neck under the ball
        objs.append(finish(Ln['id'], bm, MATS))

        if Lc:
            bm = bmesh.new(); zc0, zc1 = zf, ze; hs = zc1 - zc0
            for a in Lc['angles_deg']:
                t = math.radians(a); M = Matrix.Translation((c[0] + Lc['r_m'] * math.cos(t), c[1] + Lc['r_m'] * math.sin(t), 0)) @ Matrix.Rotation(t, 4, 'Z')
                round_column(bm, M, zc0, rcl, rcl * 1.2, hs - rcl * 1.2 - rcl * 2.6 - .1, rcl * 2.6, .1, seg=10)
            objs.append(finish(Lc['id'], bm, MATS))

    Bl = S.get('ball')
    if Bl:
        bm = bmesh.new(); r = Bl['d_m'] / 2; zc_ = Bl['z_m'] + r
        kit.lathe(bm, [(max(.03, r * math.sin(math.pi * i / 16)), zc_ - r * math.cos(math.pi * i / 16)) for i in range(17)], seg=28, x=c[0], y=c[1])
        objs.append(finish(Bl['id'], bm, MATS))
    Cr = S.get('cross')
    if Cr:
        bm = bmesh.new(); w = Cr['w_m']; z0 = Cr['z_m'] - .25; M = Matrix.Translation((c[0], c[1], 0))
        kit.box(bm, -w / 2, w / 2, -w / 2, w / 2, z0, Cr['z_m'] + Cr['h_m'], xf=M)
        bl, bt = Cr.get('bar_m', [Cr['h_m'] * .72, w]); bz = Cr.get('bar_z_m', Cr['z_m'] + Cr['h_m'] * .63); bh = Cr.get('bar_h_m', w)
        kit.box(bm, -bt / 2, bt / 2, -bl / 2, bl / 2, bz, bz + bh, xf=M)
        for x, y, z in ((0, -bl / 2, bz + bh / 2), (0, bl / 2, bz + bh / 2), (0, 0, Cr['z_m'] + Cr['h_m'])):   # the knobs at its ends
            kit.box(bm, x - w * .7, x + w * .7, y - w * .7, y + w * .7, z - w * .7, z + w * .7, xf=M)
        objs.append(finish(Cr['id'], bm, MATS))
    return objs


def _shell_z(Sh, r):
    prof, _ = pointed(Sh['d_m'] / 2, Sh['rise_m'], 96)
    for (r0, h0), (r1, h1) in zip(prof, prof[1:]):
        if r1 <= r <= r0: return Sh['z_m'] + h0 + (h1 - h0) * (r0 - r) / max(1e-9, r0 - r1)
    return Sh['z_m'] + Sh['rise_m']


# ---- the smaller domes -------------------------------------------------------------------------------------------------

def small_dome(D, S, so):
    """a smaller dome: its block in the order, the drum with pilasters and windows, the ribbed dome, the lantern"""
    bm = bmesh.new(); own = D['id']; x, y = D['at']; b = D['base']; hb = b['h_m']
    pts = [Vector((x - b['w_m'] / 2, y - b['d_m'] / 2, 0)), Vector((x + b['w_m'] / 2, y - b['d_m'] / 2, 0)), Vector((x + b['w_m'] / 2, y + b['d_m'] / 2, 0)), Vector((x - b['w_m'] / 2, y + b['d_m'] / 2, 0))]
    k = hb / S['order']['ref_m']
    for i in range(4):
        a, c = pts[i], pts[(i + 1) % 4]; dress(bm, Flat(a, c - a), (c - a).length, hb, S, so, own, k)
    order_mouldings(bm, *plan_path([(p.x, p.y) for p in pts], True), S, k, hb)
    face(bm, [p + UP * hb for p in pts])   # its roof
    r = D['d_m'] / 2; z0 = hb; z1 = hb + D['drum_h_m']; W = Round((x, y), r, 0.0); n = 8; holes = []
    for i in range(n):
        u = math.tau * r * (i + .5) / n; ww = min(1.1, r * .12)
        holes.append({'ua': u - ww / 2, 'ub': u + ww / 2, 'za': z0 + .9, 'zb': z1 - 1.0, 'spring': z1 - 1.0 - ww / 2, 'depth': .5})
        windows_of(bm, W, u, ww, z0 + .9, z1 - 1.0, .45, S['order'], None, spring=z1 - 1.0 - ww / 2)
    surface(bm, W, 0, math.tau * r, z0, z1, holes)
    ring = arc_path((x, y), r, 0, math.tau, 64, closed=True)
    sweep_path(bm, *ring, p_band(z0, .55, .35), closed=True, smooth=True)
    sweep_path(bm, *ring, p_crown(z1 - .75, .75, .65), closed=True, smooth=True)
    for i in range(n):
        u = math.tau * r * i / n; M = bay(W, u)
        for dx in (-.55, .55):
            kit.box(bm, dx - .22, dx + .22, -.1, .22, z0 + .55, z1 - .75, xf=M)
    rl = D['lantern']['d_m'] / 2 if D.get('lantern') else .8
    prof, (cc, zc, rho) = pointed(r, D['rise_m'], 24, upto=rl + .15)
    kit.lathe(bm, [(rr, z1 + z) for rr, z in prof], seg=64, x=x, y=y, mat=ROOF)
    sel = pointed(r, D['rise_m'], 30, upto=rl + .3)[0]
    for i in range(n):   # its ribs
        t = math.tau * i / n; R_ = Vector((math.cos(t), math.sin(t), 0)); T_ = Vector((-math.sin(t), math.cos(t), 0))
        P_, O_, U_ = [], [], []
        for rr, z in sel:
            nr = Vector((rr - cc, z)).normalized() if D['rise_m'] > r else Vector((rr, z - zc)).normalized()
            P_.append(Vector((x, y, 0)) + R_ * rr + UP * (z1 + z)); O_.append(R_ * nr.x + UP * nr.y); U_.append(-T_)
        sweep_path(bm, P_, O_, U_, [(-.05, -.28), (.3, -.28), (.3, .28), (-.05, .28)], mat=ROOF)
    if D.get('lantern') and D['lantern']['h_m'] > 0:
        Lh = D['lantern']['h_m']; zl = z1 + D['rise_m'] - .02 * D['rise_m']; zt = zl + Lh * .7
        zcol = z1 + [z for rr, z in prof][-1] - .3
        kit.lathe(bm, [(rl + .35, zcol), (rl + .35, zl - .15), (rl + .2, zl)], seg=32, x=x, y=y)
        Wl = Round((x, y), rl, 0.0); hl = []
        for i in range(8):
            u = math.tau * rl * (i + .5) / 8; ww = min(.6, math.tau * rl / 8 - .5)
            hl.append({'ua': u - ww / 2, 'ub': u + ww / 2, 'za': zl + .5, 'zb': zt - .7, 'spring': zt - .7 - ww / 2, 'depth': .35})
        surface(bm, Wl, 0, math.tau * rl, zl, zt, hl)
        for i in range(8):
            kit.box(bm, -.16, .16, -.05, .2, zl + .2, zt - .45, xf=bay(Wl, math.tau * rl * i / 8))
        sweep_path(bm, *arc_path((x, y), rl, 0, math.tau, 32, closed=True), p_crown(zt - .45, .45, .3), closed=True, smooth=True)
        cup = [(rl * math.cos(math.pi / 2 * i / 12), zt + Lh * .3 * math.sin(math.pi / 2 * i / 12)) for i in range(12)] + [(.06, zt + Lh * .3)]
        kit.lathe(bm, cup, seg=24, x=x, y=y, mat=ROOF)
    return finish(own, bm, MATS)


# ---- the front ---------------------------------------------------------------------------------------------------------

def _fq(F):
    at, U, N = Vector((F['at'][0], F['at'][1], 0)), Vector((F['u'][0], F['u'][1], 0)), Vector((F['n'][0], F['n'][1], 0))
    return lambda u, n, z=0.0: at + U * u + N * n + UP * z


def _front_line(F):
    """the front's face along it: [(u, n), ...] from one end to the other, stepping out where it stands forward"""
    Lh = F['length_m'] / 2; nf = F['front_m']; cur = -Lh; segs = []
    for a, b, n in sorted(F.get('forward') or []):
        a, b = max(a, -Lh), min(b, Lh)
        if a > cur + 1e-6: segs.append((cur, a, nf))
        segs.append((a, b, n)); cur = b
    if cur < Lh - 1e-6: segs.append((cur, Lh, nf))
    pts = []
    for a, b, n in segs:
        for p in ((a, n), (b, n)):
            if not pts or (abs(pts[-1][0] - p[0]) > 1e-6 or abs(pts[-1][1] - p[1]) > 1e-6): pts.append(p)
    return pts, segs


def _front_outline(F):
    pts, _ = _front_line(F); Lh = F['length_m'] / 2
    return pts + [(Lh, F['back_m']), (-Lh, F['back_m'])]


def front(F, S, so):
    """the front: its wall in two storeys with the openings of each bay between the order's members, the giant columns and
    pilasters, the entablature, the pediment, the attic with its windows and balustrade"""
    FD = S['front_detail']; O = S['order']; q = _fq(F); own = F['id']; Lh = F['length_m'] / 2
    N = Vector((F['n'][0], F['n'][1], 0))
    line, segs = _front_line(F); outline = _front_outline(F); H = F['h_m']
    Wn = lambda a, b: Flat(q(*a), q(*b) - q(*a))
    ze0, ze1 = F['entablature_m']; ne = F['columns']['n_m'] + F['columns']['stages'][1][0] / 2 * F['columns']['stages'][1][2] if F.get('columns') else F['front_m'] + 1.4
    mem = []   # the order's members along it: (u, half width, kind)
    if F.get('columns'): mem += [(u, F['columns']['stages'][0][0] / 2, 'col') for u in F['columns']['u_m']]
    if F.get('pilasters'): mem += [(u, F['pilasters']['w_m'][0] / 2, 'pil') for u in F['pilasters']['u_m']]
    mem.sort()
    wall, opn, ent, att, cols, pils, ped = (bmesh.new() for _ in range(7))

    # the openings of each bay, on the stretch of the face where they fit best
    edges = [-Lh] + [x for u, hw, _ in mem for x in (u - hw, u + hw)] + [Lh]
    bays = [(a, b) for a, b in zip(edges[::2], edges[1::2]) if b - a > .5]
    c0 = min(range(len(bays)), key=lambda i: abs((bays[i][0] + bays[i][1]) / 2))
    ca, cb, cp = (F['storey_m'] + FD['course_m'][0], F['storey_m'] + FD['course_m'][1], FD['course_m'][2])
    holes = {i: [] for i in range(len(segs))}; gaps = []   # (gaps: where the plinth stops for a door)
    for bi, (ba, bb) in enumerate(bays):
        idx = abs(bi - c0); spec = FD['bays'][idx] if idx < len(FD['bays']) else {}
        for which in ('lower', 'upper'):
            kind = spec.get(which)
            if not kind: continue
            od = FD['openings'][kind]; fw = O['frame_m'][0]
            best = max(((max(a, ba), min(b, bb), si) for si, (a, b, n) in enumerate(segs)), key=lambda t: t[1] - t[0])
            sa, sb, si = best; w = min(od['w'], sb - sa - 2 * fw - .8)
            if w < .55 * od['w']: continue
            uc = (sa + sb) / 2; a, b, n = segs[si]; W = Wn((a, n), (b, n)); ul = uc - a
            sp = od.get('spring'); za, zb = od['z']; zb = sp + w / 2 if sp is not None else zb
            niche = od.get('niche'); h = {'ua': ul - w / 2, 'ub': ul + w / 2, 'za': za, 'zb': zb, 'depth': od['depth']}
            if sp is not None: h['spring'] = sp
            if niche: h.update(reveal=STONE, back=STONE)
            holes[si].append(h)
            tp = od.get('top'); tp = ('tri', 'seg')[(idx + (which == 'upper')) % 2] if tp == 'alt' else tp
            if kind.startswith('portal'):
                V = W.at(ul); hw = w / 2 + .5
                wbox(opn, V, -hw, -w / 2, 0.0, .32, za, zb); wbox(opn, V, w / 2, hw, 0.0, .32, za, zb); wbox(opn, V, -hw, hw, 0.0, .32, zb, zb + .5)
                wbox(opn, V, -hw, hw, 0.0, .22, zb + .5, zb + .95); wbox(opn, V, -hw - .3, hw + .3, 0.0, .6, zb + .95, zb + 1.3)
                for sx in (-1, 1): wbox(opn, V, sx * (hw + .05) - .2, sx * (hw + .05) + .2, 0.0, .55, zb + .2, zb + .95)   # its consoles
                gaps.append((uc - hw - .3, uc + hw + .3))
                ov = od.get('over')
                if ov:
                    ow = ov['w']; holes[si].append({'ua': ul - ow / 2, 'ub': ul + ow / 2, 'za': ov['z'][0], 'zb': ov['z'][1], 'depth': 1.2})
                    windows_of(opn, W, ul, ow, ov['z'][0], ov['z'][1], 1.0, O, None)
            else:
                windows_of(opn, W, ul, w, za, zb, 1.0, O, tp if tp else None, spring=sp)
                if sp is not None and not niche:
                    for sx in (-1, 1): wbox(opn, W.at(ul), min(sx * (w / 2 + O['frame_m'][0]), sx * (w / 2 + .9)), max(sx * (w / 2 + O['frame_m'][0]), sx * (w / 2 + .9)), 0.0, .4, sp - .45, sp)   # the imposts
                if za < FD['plinth_m'][0]: gaps.append((uc - w / 2 - O['frame_m'][0] - .15, uc + w / 2 + O['frame_m'][0] + .15))
            bal = od.get('balcony')
            if bal:
                if bal == 'loggia' and F.get('loggia'):
                    lg = F['loggia']; u0, u1 = lg['u_m']; z0, z1 = lg['z_m']; d = lg['front_m'] - n; z1 = max(z1, cb)
                else:
                    u0, u1 = uc - w / 2 - .9, uc + w / 2 + .9; d = bal; z0, z1 = ca, cb
                V = Wn((u0, n), (u1, n)); L_ = u1 - u0
                kit.box(opn, -L_ / 2, L_ / 2, 0.0, d, z0, z1, xf=bay(V, L_ / 2))
                kit.box(opn, -L_ / 2 + .25, L_ / 2 - .25, 0.0, d - .25, z0 - .35, z0, xf=bay(V, L_ / 2))
                Vf = Wn((u0 + .05, n + d - .05), (u1 - .05, n + d - .05))
                baluster_run(opn, Vf, 0, L_ - .1, z1, 1.1, 0.0, .32, .36, piers=(.25, L_ - .35))
                for s_, (pa, pb) in ((0, ((u0 + .05, n), (u0 + .05, n + d - .05))), (1, ((u1 - .05, n + d - .05), (u1 - .05, n)))):
                    Vs = Wn(pa, pb); ls = (q(*pb) - q(*pa)).length
                    baluster_run(opn, Vs, .1, ls - .1, z1, 1.1, 0.0, .32, .36)
    for si, (a, b, n) in enumerate(segs):
        surface(wall, Wn((a, n), (b, n)), 0, b - a, 0, H, holes[si])
    for (pa, pb) in zip(line, line[1:]):   # the returns where the face steps
        if abs(pa[0] - pb[0]) < 1e-6: surface(wall, Wn(pa, pb), 0, abs(pb[1] - pa[1]), 0, H)
    nb = F['back_m']
    for pa, pb in (((Lh, line[-1][1]), (Lh, nb)), ((Lh, nb), (-Lh, nb)), ((-Lh, nb), (-Lh, line[0][1]))):   # its ends and back
        W = Wn(pa, pb); L_ = (q(*pb) - q(*pa)).length
        dress(wall, W, L_, H, S, so, own, 1.0, zones=('order',))
    for piece in cut_loop(outline, gaps) or [outline]:
        sweep_path(wall, *plan_path([tuple(q(u, n)[:2]) for u, n in piece], closed=not gaps), p_plinth(*FD['plinth_m']), closed=not gaps)
    sweep_path(wall, *plan_path([tuple(q(u, n)[:2]) for u, n in line]), p_band(ca, cb - ca, cp))
    objs = [finish(own, wall, MATS)]

    # the giant columns and pilasters
    if F.get('columns'):
        st = F['columns']['stages']; (pw_, hb_, _), (ds, hs, tp_), (_, hc, _), (aw, ha, _) = st[0], st[1], st[2], st[3] if len(st) > 3 else (st[2][0] * 1.2, .5, 1)
        for u in F['columns']['u_m']:
            M = Matrix.Translation(q(u, F['columns']['n_m'])) @ Matrix.Rotation(math.atan2(N.y, N.x), 4, 'Z')
            round_column(cols, M, 0.0, ds / 2, hb_, hs, hc, ha, taper=tp_, seg=24, aw=aw, pw=pw_)
        objs.append(finish(F['columns']['id'], cols, MATS))
    if F.get('pilasters'):
        Pl = F['pilasters']; w0, w1 = Pl['w_m']; zb_, zc_, zt_ = Pl['z_m']
        for u in Pl['u_m']:
            n0 = max(nn for a, b, nn in segs if a - 1e-6 <= u <= b + 1e-6)
            V = Wn((u - 1, n0), (u + 1, n0)); p = Pl['front_m'] - n0
            pilaster(pils, bay(V, 1.0), 0.0, zt_, w1, p, zb_, zt_ - zc_)
        objs.append(finish(Pl['id'], pils, MATS))

    # the entablature: along the columns' line over the whole front, breaking forward over the pilasters; the ceiling behind it
    # where the wall stands back; round the ends and the back over the wall
    brk = sorted((u - F['pilasters']['w_m'][0] / 2 - .05, u + F['pilasters']['w_m'][0] / 2 + .05) for u in F['pilasters']['u_m']) if F.get('pilasters') else []
    nfp = F['pilasters']['front_m'] if F.get('pilasters') else ne
    fl = []; cur = -Lh
    for a, b in brk:
        a = -Lh if a - (-Lh) < 1.0 else a; b = Lh if Lh - b < 1.0 else b
        if a > cur + 1e-6: fl += [(cur, ne), (a, ne)]
        fl += [(a, nfp), (b, nfp)]; cur = b
    if cur < Lh - 1e-6: fl += [(cur, ne), (Lh, ne)]
    fl2 = [fl[0]]
    for p in fl[1:]:
        if abs(p[0] - fl2[-1][0]) > 1e-6 or abs(p[1] - fl2[-1][1]) > 1e-6: fl2.append(p)
    path = fl2 + [(Lh, nb), (-Lh, nb)]
    he = ze1 - ze0
    sweep_path(ent, *plan_path([tuple(q(u, n)[:2]) for u, n in path], True), kit.entablature([[.3, he * .3], [.24, he * .3], [1.0, he * .4]], ze0), closed=True)
    nmin = min(n for a, b, n in segs)
    Vf = Wn((-Lh + .1, nmin), (Lh - .1, nmin)); kit.box(ent, -(Lh - .1), Lh - .1, -.05, ne - nmin, ze0, ze1, xf=bay(Vf, Lh - .1))
    objs.append(finish(F['entablature_id'], ent, MATS))

    # the pediment over the middle, its raking cornice's top where the film puts the pediment's
    Pd = F.get('pediment')
    if Pd:
        A_ = F['attic']; Va = Wn((-Lh, A_['n_m'][1]), (Lh, A_['n_m'][1])); pn = ne - A_['n_m'][1]
        V2 = Flat(Va.p(0, pn, 0), Va.d)
        wprism(ped, Va, [(Lh - Pd['w_m'] / 2, Pd['z_m']), (Lh + Pd['w_m'] / 2, Pd['z_m']), (Lh, Pd['z_m'] + Pd['h_m'] - 1.0)], 0.0, pn)
        pediment(ped, V2, Lh, Pd['w_m'] / 2, Pd['z_m'], 2.4, .95, 'tri', apex=Pd['z_m'] + Pd['h_m'])
        objs.append(finish(Pd['id'], ped, MATS))

    # the attic: its wall with windows in the bays, pilaster strips over the order's members, its courses, the terrace, the
    # balustrade with piers over the members
    A_ = F['attic']; z0, (zba, zbb, zca, zcb) = A_['z_m'], FD['attic_m']; nA0, nA1 = A_['n_m']
    if A_.get('parapet_m'): zca, zcb = zca + A_['parapet_m'][0] - zcb, A_['parapet_m'][0]   # (the terrace behind the balustrade where the film puts the parapet's foot)
    Wf = Wn((-Lh, nA1), (Lh, nA1)); aw_ = FD['attic_window']; hl = []
    ped_top = lambda u: (Pd['z_m'] + Pd['h_m'] * max(0.0, 1 - abs(u) / (Pd['w_m'] / 2)) + 1.6) if Pd else 0
    for ba, bb in bays:
        uc = (ba + bb) / 2; w = min(aw_['w'], bb - ba - 1.4)
        if w < 1.5 or ped_top(uc - w / 2 - .5) > aw_['z'][0] - .3 or ped_top(uc + w / 2 + .5) > aw_['z'][0] - .3: continue
        hl.append({'ua': uc + Lh - w / 2, 'ub': uc + Lh + w / 2, 'za': aw_['z'][0], 'zb': aw_['z'][1], 'depth': aw_['depth']})
        windows_of(att, Wf, uc + Lh, w, aw_['z'][0], aw_['z'][1], 1.0, O, 'cornice' if abs(uc) > 30 else None)
    surface(att, Wf, 0, 2 * Lh, z0, zcb, hl)
    for pa, pb in (((Lh, nA1), (Lh, nA0)), ((Lh, nA0), (-Lh, nA0)), ((-Lh, nA0), (-Lh, nA1))):
        W = Wn(pa, pb); surface(att, W, 0, (q(*pb) - q(*pa)).length, z0, zcb)
    face(att, [q(-Lh, nA0, zcb), q(Lh, nA0, zcb), q(Lh, nA1, zcb), q(-Lh, nA1, zcb)])   # the terrace
    fb = F['back_m']
    if nA0 < fb - .05: face(att, [q(-Lh, nA0, z0), q(-Lh, fb, z0), q(Lh, fb, z0), q(Lh, nA0, z0)])   # (its underside where it overhangs the back)
    apw, app = FD['attic_pilaster_m']
    for u, hw, _ in mem:
        V = Wf.at(u + Lh)
        if ped_top(u) > zca - 1.0 and abs(u) < (Pd['w_m'] / 2 if Pd else 0): continue
        wbox(att, V, -apw / 2, apw / 2, -.1, app, zbb, zca - .45); wbox(att, V, -apw / 2 - .12, apw / 2 + .12, -.1, app + .12, zca - .45, zca)
    rr = [(-Lh, nA1), (Lh, nA1), (Lh, nA0), (-Lh, nA0)]
    if _area([tuple(q(u, n)[:2]) for u, n in rr]) < 0: rr = rr[::-1]
    ring = plan_path([tuple(q(u, n)[:2]) for u, n in rr], True)
    sweep_path(att, *ring, p_band(zba, zbb - zba, .45), closed=True)
    sweep_path(att, *ring, p_crown(zca, zcb - zca, 1.15), closed=True)
    bh, bs = FD['balustrade_m']; nfr = min(A_.get('parapet_m', [zcb, nA1 + 1.0])[1], nA1 + 1.0)
    if A_.get('top_m') and A_['top_m'] > zcb + .5: bh = A_['top_m'] - zcb   # (its top where the film's front ends)
    Vb = Wn((-Lh + .3, nfr), (Lh - .3, nfr))
    baluster_run(att, Vb, 0, 2 * Lh - .6, zcb, bh, 0.0, .55, bs, piers=[u + Lh - .3 for u, hw, _ in mem] + [.4, 2 * Lh - 1.0], pw=1.3, seg=6)
    for pa, pb in (((Lh - .3, nfr), (Lh - .3, nA0 + .3)), ((-Lh + .3, nA0 + .3), (-Lh + .3, nfr))):
        Vs = Wn(pa, pb); ls = (q(*pb) - q(*pa)).length
        baluster_run(att, Vs, .7, ls, zcb, bh, 0.0, .55, bs, piers=[ls - .4], pw=1.3, seg=6)
    objs.append(finish(F['attic_id'], att, MATS))
    objs.append(finish(F['openings_id'], opn, MATS))
    return objs


def cut_loop(loop, gaps):
    """a closed outline [(u, n), ...] cut where it runs along +u through the gaps [(u0, u1), ...] -> its open pieces"""
    pts, cut = [], []   # (cut[i]: the edge from pts[i] to the next is a gap)
    m = len(loop)
    for i in range(m):
        a, b = loop[i], loop[(i + 1) % m]; pts.append(a); cut.append(False)
        if abs(a[1] - b[1]) < 1e-6 and b[0] > a[0]:
            for g0, g1 in sorted(gaps):
                g0, g1 = max(g0, a[0]), min(g1, b[0])
                if g1 - g0 < 1e-6: continue
                if g0 > pts[-1][0] + 1e-6: pts.append((g0, a[1])); cut.append(False)
                cut[-1] = True; pts.append((g1, a[1])); cut.append(False)
    if not any(cut): return None
    k = cut.index(True); m = len(pts); pieces, cur = [], [pts[(k + 1) % m]]
    for j in range(1, m + 1):
        i = (k + 1 + j - 1) % m
        if cut[i]: pieces.append(cur); cur = [pts[(i + 1) % m]]
        else: cur.append(pts[(i + 1) % m])
    return [p for p in pieces if len(p) > 1]


def _area(poly): return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1])) / 2


# ---- the whole ---------------------------------------------------------------------------------------------------------

MATS = []


def build(s):
    S = spec_of(s)
    MATS[:] = [kit.stone(), kit.dark(), kit.roof()]
    so = solids_of(S); objs = []
    for B in S['bodies']: objs.append(block(B, S, so))
    for Ap in S['apses']: objs.append(apse(Ap, S, so))
    if all(S.get(k) for k in ('base', 'drum', 'drum_columns', 'drum_cornice', 'shell')): objs += crossing(S, so)
    else: print('build: domed_church: no crossing (the landmark has no base, drum, drum columns, cornice or shell by the roles)')
    for D in S['small_domes']: objs.append(small_dome(D, S, so))
    if S.get('front'):
        F = {**S['front']}; fid = F['id']
        F.setdefault('entablature_id', f'{fid}_entablature'); F.setdefault('attic_id', f'{fid}_attic'); F.setdefault('openings_id', f'{fid}_openings')
        objs += front(F, S, so)
    return objs

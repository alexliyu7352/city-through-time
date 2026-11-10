"""Colonnaded porticoes (the covered walks round a garden, a forum's or a sanctuary's stoas) as a detailed model, drawn from a `parts`
landmark as the film's generator lays it out (pipeline/landmarks.py: each part a row of columns, a wall, a floor, a block on the
columns with its roof). Each part keeps the film's footprint and heights and is drawn as what it stands for. Parts (objects):
  floor        the low prisms (h_m .5 or less, standing on nothing): the paved walk, and a stylobate course under each row of
               columns as wide as their plinths
  columns      each `column` part (round, its copies along its `repeat` line): free-standing columns with a base, a tapered shaft
               and a capital in the spec's order
  entablature  a `long_hall` standing on a row of columns (`atop`): its body is the entablature over the columns (architrave in
               fasciae, frieze, cornice out to the roof's eaves), the beams across the walk at each column and the ceiling
  walls        the tall prisms (the back walls), a plinth along both faces; carried up behind the entablature to the roof, a band
               on the walk's side at the columns' head; an `arches` part (a doorway through a wall) with its moulded frame
  roofs        that long_hall's roof, tiled: rows of cover tiles (imbrices) from the eaves to the ridge over the pan tiles, a
               ridge cap, antefixes along the eaves; gabled as the film has it (its pitch, overhang and ridge height), or a
               lean-to against the back wall (spec roof: lean_to: the film's pitch from the front eave, so its top stands higher
               than the film's ridge by about the gable's rise: kept at the film's ridge, it fell to a nearly flat roof)
Sizes: every footprint, height, column count, spacing and diameter, the roof's form, pitch and overhang come from the landmark;
what it does not give is a DEFAULT here, an estimate: the order, how the block on the columns divides into architrave, frieze
and cornice, the tiles, the mouldings. A part this module does not know stops the build (a hall among the porticoes: hall.py).

The helpers under "for the kit" are general (a free-standing column, a straight sweep, a tiled roof, a wall with openings, a
plan extruded); hall.py and theatre.py use them too."""
import math

import bmesh
from mathutils import Matrix, Vector

import kit

DEFAULT = {
    'parts': [],                 # the landmark's parts (from_landmark)
    'order': 'tuscan',           # the columns' order: tuscan, ionic or corinthian (an estimate: the sources name none)
    'column_seg': 10,            # facets round a column (its side is shaded smooth)
    'ent_split': [.4, .3, .3],   # the block on the columns as architrave, frieze and cornice (shares of its height)
    'roof': None,                # gabled or lean_to (None: the landmark's)
    'tile_m': .55,               # cover tiles: their spacing along the eaves, their half width and height
    'tile_r': [.09, .08],
    'eave_m': .12,               # the roof's edge over the cornice (the pan tiles' and the gutter's depth)
    'plinth_m': [.45, .05],      # a wall's plinth: height, projection
    'beam_m': [.3, .35],         # a ceiling beam across the walk at each column: width, depth
}


# ---- for the kit (general helpers: hall.py and theatre.py import them from here)

def frame(x, y, ang=0.0, z=0.0):
    """the Matrix of a frame at (x, y, z), its x axis turned ang radians counter-clockwise from east"""
    c, s = math.cos(ang), math.sin(ang)
    return Matrix(((c, -s, 0, x), (s, c, 0, y), (0, 0, 1, z), (0, 0, 0, 1)))


def axes(o, u, n, z=0.0):
    """the Matrix of a frame at o (x, y) whose x axis is u and y axis n (unit vectors in the plan, u x n = up)"""
    return Matrix(((u[0], n[0], 0, o[0]), (u[1], n[1], 0, o[1]), (0, 0, 1, z), (0, 0, 0, 1)))


def _faces(bm, quads, mat):
    for q in quads:
        try: f = bm.faces.new(q); f.material_index = mat
        except ValueError: pass


def extrude(bm, profile, p0, p1, out=(0, 1, 0), up=(0, 0, 1), mat=0, caps=True, xf=None, closed=False, mats=None):
    """a straight moulding: the profile [(o, v), ...] (o metres along out, v along up) carried from p0 to p1 (points of the frame
    xf), its consecutive points joined into faces (closed: the last to the first too); caps: its ends closed (the profile read as a
    closed outline); mats: a material for each of its faces in turn (else mat), the caps in mat"""
    M = xf or Matrix.Identity(4); out, up = Vector(out), Vector(up)
    rings = [[bm.verts.new(M @ (Vector(p) + out * o + up * v)) for o, v in profile] for p in (p0, p1)]
    n = len(profile)
    for k in range(n if closed else n - 1):
        _faces(bm, [(rings[0][k], rings[1][k], rings[1][(k + 1) % n], rings[0][(k + 1) % n])], mats[k] if mats else mat)
    if caps and len(profile) > 2:
        _faces(bm, [rings[0][::-1], rings[1]], mat)
    return rings


def prism_plan(bm, pts, z0, z1, mat=0, xf=None):
    """a plan [(x, y), ...] (any simple polygon, concave too) extruded from z0 to z1"""
    M = xf or Matrix.Identity(4)
    lo = [bm.verts.new(M @ Vector((x, y, z0))) for x, y in pts]; hi = [bm.verts.new(M @ Vector((x, y, z1))) for x, y in pts]
    n = len(pts)
    _faces(bm, [lo[::-1], hi] + [(lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]) for i in range(n)], mat)


def column_free(bm, order, rc, z0, z1, M, taper=.9, seg=10, plinth=None):
    """a free-standing column from z0 to the top of its capital z1, radius rc at its foot, tapering to rc * taper under its
    capital, every part sized by its diameter D (Vitruvius's modules): a Tuscan base and capital each half a diameter high; an
    Attic base under the Ionic capital (a third of a diameter, its volutes facing the frame's y) and the Corinthian (a bell of two
    rows of leaves, its corner scrolls, a diameter and a tenth). Plinth and abacus square; plinth: the plinth's half width (default
    1.3 rc). M places it (the frame's x along its row, y its front)"""
    D = 2 * rc; rt = rc * taper; p = plinth or rc * 1.3; full = dict(seg=seg, xf=M)
    if order == 'tuscan':
        kit.box(bm, -p, p, -p, p, z0, z0 + .25 * D, xf=M)
        kit.lathe(bm, [(rc * 1.2, z0 + .25 * D), (rc * 1.27, z0 + .33 * D), (rc * 1.2, z0 + .42 * D), (rc * 1.05, z0 + .45 * D), (rc, z0 + .5 * D)], **full)
        c0 = z1 - .5 * D
        kit.lathe(bm, [(rc, z0 + .5 * D), (rt, c0)], **full)
        kit.lathe(bm, [(rt, c0), (rt * 1.1, c0 + .03 * D), (rt, c0 + .07 * D), (rt, c0 + .17 * D), (rt * 1.05, c0 + .19 * D), (rc * 1.15, c0 + .33 * D)], **full)
        kit.box(bm, -rc * 1.2, rc * 1.2, -rc * 1.2, rc * 1.2, c0 + .33 * D, z1, xf=M)
        return
    b0 = z0 + D / 6
    kit.box(bm, -p, p, -p, p, z0, b0, xf=M)   # the Attic base: torus, scotia, torus
    kit.lathe(bm, [(rc * 1.25, b0), (rc * 1.3, b0 + .08 * D), (rc * 1.25, b0 + .15 * D), (rc * 1.1, b0 + .17 * D), (rc * 1.06, b0 + .23 * D),
                   (rc * 1.16, b0 + .26 * D), (rc * 1.18, b0 + .29 * D), (rc * 1.08, b0 + .33 * D), (rc, b0 + .36 * D)], **full)
    if order == 'ionic':
        c0 = z1 - .4 * D
        kit.lathe(bm, [(rc, b0 + .36 * D), (rt, c0)], **full)
        kit.lathe(bm, [(rt, c0), (rt * 1.1, c0 + .03 * D), (rt, c0 + .06 * D), (rt * 1.25, c0 + .2 * D)], **full)   # the astragal, the echinus
        kit.box(bm, -rc * 1.2, rc * 1.2, -rc * .95, rc * .95, c0 + .12 * D, z1 - .08 * D, xf=M)   # the cushion between the volutes
        for sx in (-1, 1):   # the volutes, their eyes front and back
            Mv = M @ Matrix.Translation((sx * rc * 1.2, 0, c0 + .14 * D)) @ Matrix.Rotation(math.pi / 2, 4, 'X')
            kit.cylinder(bm, 0, 0, -rc, rc, .2 * D, seg=10, xf=Mv)
            kit.cylinder(bm, 0, 0, -rc * 1.06, rc * 1.06, .07 * D, seg=6, xf=Mv)
        kit.box(bm, -rc * 1.3, rc * 1.3, -rc * 1.05, rc * 1.05, z1 - .08 * D, z1, xf=M)
        return
    c0 = z1 - 1.1 * D   # Corinthian
    kit.lathe(bm, [(rc, b0 + .36 * D), (rt, c0)], **full)
    kit.lathe(bm, [(rt, c0), (rt * 1.08, c0 + .03 * D), (rt, c0 + .06 * D), (rt * 1.3, c0 + .3 * D), (rt * 1.04, c0 + .36 * D),   # two rows of leaves curling out
                   (rt * 1.45, c0 + .62 * D), (rt * 1.14, c0 + .68 * D), (rc * 1.4, c0 + .92 * D)], **full)
    a = rc * 1.45
    kit.box(bm, -a, a, -a, a, c0 + .92 * D, z1, xf=M)   # the abacus
    for sx in (-1, 1):
        for sy in (-1, 1):   # the corner scrolls under the abacus
            kit.box(bm, sx * a - .1 * D * (1 + sx), sx * a + .1 * D * (1 - sx), sy * a - .1 * D * (1 + sy), sy * a + .1 * D * (1 - sy), c0 + .72 * D, c0 + .92 * D, xf=M)


def wall_openings(bm, x0, x1, t, z0, z1, holes, mat=0, reveal=None, xf=None):
    """a wall from x0 to x1 along the frame's x, t thick (its front at y=0, its back at y=-t), from z0 to z1, with rectangular
    openings holes [(xa, xb, za, zb), ...] through it, their sides, sills and heads in reveal (mat when None): the wall's faces cut
    on the grid of the openings' edges"""
    M = xf or Matrix.Identity(4); rv = mat if reveal is None else reveal
    V = lambda x, y, z: bm.verts.new(M @ Vector((x, y, z)))
    xs = sorted({x0, x1} | {h[0] for h in holes} | {h[1] for h in holes}); zs = sorted({z0, z1} | {h[2] for h in holes} | {h[3] for h in holes})
    inside = lambda x, z: any(h[0] < x < h[1] and h[2] < z < h[3] for h in holes)
    q = []
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            if inside((xs[i] + xs[i + 1]) / 2, (zs[j] + zs[j + 1]) / 2): continue
            for y in (0.0, -t):
                q.append((V(xs[i], y, zs[j]), V(xs[i + 1], y, zs[j]), V(xs[i + 1], y, zs[j + 1]), V(xs[i], y, zs[j + 1])))
    q += [(V(x0, 0, z1), V(x1, 0, z1), V(x1, -t, z1), V(x0, -t, z1)), (V(x0, 0, z0), V(x0, -t, z0), V(x0, -t, z1), V(x0, 0, z1)),
          (V(x1, 0, z0), V(x1, 0, z1), V(x1, -t, z1), V(x1, -t, z0))]
    _faces(bm, q, mat)
    r = []
    for xa, xb, za, zb in holes:
        r += [(V(x, 0, za), V(x, -t, za), V(x, -t, zb), V(x, 0, zb)) for x in (xa, xb)]
        r += [(V(xa, 0, z), V(xb, 0, z), V(xb, -t, z), V(xa, -t, z)) for z in ((za,) if za > z0 + 1e-6 else ()) + (zb,)]
    _faces(bm, r, rv)


def door_frame(bm, xa, xb, za, zb, w=.4, p=.08, cornice=(.3, .25), xf=None):
    """the moulded frame round an opening on a wall's face (y=0, the frame's y out of it): jambs and lintel w wide standing out p,
    and a cornice over it (its height, its projection)"""
    M = xf or Matrix.Identity(4)
    for x in (xa - w, xb):   # (from the wall's face: a frame sunk into it showed a flickering line along the reveal)
        kit.box(bm, x, x + w, 0, p, za, zb + w, xf=M)
    kit.box(bm, xa, xb, 0, p, zb, zb + w, xf=M)
    if cornice:
        ch, cp = cornice
        extrude(bm, [(0, 0), (p + cp * .4, 0), (p + cp * .6, ch * .45), (p + cp, ch * .7), (p + cp, ch), (0, ch)], (xa - w - cp, 0, zb + w), (xb + w + cp, 0, zb + w), xf=M)


def tiles(bm, M, x0, x1, a, b, step, r=(.09, .08), antefix=True, mat=0):
    """cover tiles (imbrices) on a roof's slope in the frame M: the slope from the eave line (y, z) a to the ridge line b, the rows
    along x from x0 to x1 every step: each a half-hexagon ridge r[0] wide, r[1] high, closed at the eave by an antefix"""
    a, b = Vector((0, *a)), Vector((0, *b)); dn = (b - a).normalized(); nrm = Vector((0, -dn.z, dn.y)) if dn.y < 0 else Vector((0, dn.z, -dn.y))
    if nrm.z < 0: nrm = -nrm
    n = max(1, int((x1 - x0) / step))
    for i in range(n):
        x = x0 + (x1 - x0) * (i + .5) / n
        sec = [Vector((x + r[0] * math.cos(f), 0, 0)) + nrm * (r[1] * math.sin(f)) for f in (0, math.pi / 3, 2 * math.pi / 3, math.pi)]
        lo = [bm.verts.new(M @ (a + s)) for s in sec]; hi = [bm.verts.new(M @ (b + s)) for s in sec]
        _faces(bm, [(lo[k], lo[k + 1], hi[k + 1], hi[k]) for k in range(3)] + [lo], mat)
        if antefix:   # an upright palmette at the eave, closing the row
            e = a + Vector((x, 0, 0)); h = r[0] * 2.2; q = r[0] * 1.15
            _faces(bm, [[bm.verts.new(M @ (e + Vector(v))) for v in ((-q * .7, 0, 0), (q * .7, 0, 0), (q, 0, h * .55), (q * .55, 0, h * .9), (0, 0, h), (-q * .55, 0, h * .9), (-q, 0, h * .55))]], mat)


def roof_gable(bm, M, x0, x1, half, z0, e, z_ridge, step=.55, r=(.09, .08), cap=.14, cover=0):
    """a tiled gabled roof in the frame M: its ridge along x from x0 to x1 at z_ridge (the ridge cap's top), its eaves at y = +-half,
    their edge e over z0 (its underside, a flat ceiling): the solid, the cover tiles on both slopes, the ridge cap. cover: the
    covering's material (slopes, eaves' edges, tiles, ridge, antefixes); the underside and the gable ends in material 0"""
    zr = z_ridge - cap * .8
    extrude(bm, [(-half, z0), (half, z0), (half, z0 + e), (0, zr), (-half, z0 + e)], (x0, 0, 0), (x1, 0, 0), out=(0, 1, 0), xf=M,
            closed=True, mats=[0, cover, cover, cover, cover])
    for s in (-1, 1):
        tiles(bm, M, x0, x1, (s * half, z0 + e), (0, zr), step, r, mat=cover)
    extrude(bm, [(cap * math.cos(f), cap * .8 * math.sin(f)) for f in (0, math.pi / 3, 2 * math.pi / 3, math.pi)], (x0, 0, zr), (x1, 0, zr), xf=M, mat=cover)


def roof_lean(bm, M, x0, x1, y_low, y_high, z0, e, z_top, step=.55, r=(.09, .08), cover=0):
    """a tiled lean-to roof in the frame M: one slope from its eave at y_low (its edge e over z0) up to y_high at z_top, along x
    from x0 to x1; its underside flat at z0. cover: the covering's material (slope, edges, tiles); underside and ends in 0"""
    extrude(bm, [(y_high, z0), (y_low, z0), (y_low, z0 + e), (y_high, z_top)], (x0, 0, 0), (x1, 0, 0), out=(0, 1, 0), xf=M,
            closed=True, mats=[0, cover, cover, cover])
    tiles(bm, M, x0, x1, (y_low, z0 + e), (y_high, z_top), step, r, mat=cover)


def ring(bm, pts, profile, closed=True, mat=0, xf=None):
    """a profile [(out, up), ...] swept along a polyline pts [(x, y), ...] (counter-clockwise round what it faces away from:
    out is to the right of the way), mitred at its corners; closed: round to the first point again, else its two ends capped"""
    M = xf or Matrix.Identity(4); n = len(pts)
    def nrm(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]; k = math.hypot(dx, dy); return (dy / k, -dx / k)
    rings = []
    for i in range(n):
        if closed or 0 < i < n - 1:
            na, nb = nrm(pts[i - 1], pts[i]), nrm(pts[i], pts[(i + 1) % n]); k = 1 + na[0] * nb[0] + na[1] * nb[1]
            m = ((na[0] + nb[0]) / k, (na[1] + nb[1]) / k)
        else: m = nrm(pts[0], pts[1]) if i == 0 else nrm(pts[-2], pts[-1])
        rings.append([bm.verts.new(M @ Vector((pts[i][0] + m[0] * o, pts[i][1] + m[1] * o, z))) for o, z in profile])
    for i in range(n if closed else n - 1):
        r0, r1 = rings[i], rings[(i + 1) % n]
        _faces(bm, [(r0[k], r1[k], r1[k + 1], r0[k + 1]) for k in range(len(profile) - 1)], mat)
    if not closed: _faces(bm, [rings[0][::-1], rings[-1]], mat)



# ---- the parts of a `parts` landmark

def instances(q):
    """a part's copies in the whole's frame: [(x, y, turn radians)] (pipeline/landmarks.py placed)"""
    th = math.radians(q.get('theta_deg') or 0); ax, ay = q.get('at') or [0.0, 0.0]; r = q.get('repeat') or {}
    if 'line' in r:
        dx, dy = r['line']['step_m']; return [(ax + i * dx, ay + i * dy, th) for i in range(r['line']['n'])]
    if 'corners' in r:
        w, d = r['corners']; return [(sx * w / 2, sy * d / 2, th) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    if 'ring' in r:
        n, R, a0 = r['ring']['n'], r['ring']['r_m'], math.radians(r['ring'].get('start_deg', 0))
        return [(R * math.cos(a0 + i / n * math.tau), R * math.sin(a0 + i / n * math.tau), th + a0 + i / n * math.tau - math.pi / 2) for i in range(n)]
    if 'mirror' in r:
        m = r['mirror']; out = [(ax, ay, th)]
        if 'x' in m: out.append((-ax, ay, -th))
        if 'y' in m: out.append((ax, -ay, math.pi - th))
        if m == 'xy': out.append((-ax, -ay, math.pi + th))
        return out
    return [(ax, ay, th)]


def to_whole(px, py, th, x, y):
    c, s = math.cos(th), math.sin(th); return (px + x * c - y * s, py + x * s + y * c)


def to_local(px, py, th, x, y):
    c, s = math.cos(th), math.sin(th); dx, dy = x - px, y - py; return (dx * c + dy * s, -dx * s + dy * c)


def levels(parts):
    """each part's foot and top (metres): on the ground (its z_m) or on the top of the part it stands on (atop)"""
    foot, top = [], []
    for q in parts:
        z = (q.get('z_m') or 0.0) + (top[q['atop']] if q.get('atop') is not None else 0.0)
        h = q.get('h_m') or 0.0
        if q['kind'] == 'column' and q.get('pedestal'): h += q['pedestal']['h_m']
        foot.append(z); top.append(z + h)
    return foot, top


def classify(parts, skip=()):
    """each part's role: floor, wall, columns, doorway or cap (a long_hall on columns); a part of another kind stops the build"""
    out = {}
    for i, q in enumerate(parts):
        if i in skip: continue
        k = q['kind']
        if k == 'column' and (q.get('section') or 'round') == 'round': out[i] = 'columns'
        elif k == 'prism' and 'plan_m' in q: out[i] = 'floor' if q['h_m'] <= .5 and q.get('atop') is None else 'wall'
        elif k == 'arches': out[i] = 'doorway'
        elif k == 'long_hall' and q.get('atop') is not None and parts[q['atop']]['kind'] == 'column': out[i] = 'cap'
        else: raise SystemExit(f'portico: part {i} ({k}{", atop " + str(q.get("atop")) if q.get("atop") is not None else ""}): not a portico\'s '
                               '(round columns, walls and floors as prisms, a doorway as arches, a long_hall on columns: its entablature and roof)')
    return out


def cap_frame(parts, i, foot, S):
    """a long_hall on columns: its rectangle and where its columns stand -> dict (the frame M of its run: x along it from one end,
    y out of its front through the columns' axis line, z up; its length; the columns' line, radius, taper; the depth behind)"""
    q = parts[i]; px, py = q.get('at') or [0.0, 0.0]; th = math.radians(q.get('theta_deg') or 0); w, d = q['w_m'], q['d_m']
    cq = parts[q['atop']]; cols = [to_local(px, py, th, x, y) for x, y, _ in instances(cq)]
    mx = sum(x for x, _ in cols) / len(cols); sf = 1 if mx > 0 else -1; xc = abs(mx)
    if abs(xc - w / 2) > 2.0: raise SystemExit(f'portico: part {i}: its columns stand {xc:.2f} m from its middle, not along a long side ({w / 2:.2f})')
    u, n = (0, -sf), (sf, 0)   # (x along the run, y out of the front: u x n = up)
    o = (sf * xc, sf * d / 2)
    L = axes(o, u, n)
    M = frame(px, py, th) @ L
    ys = sorted(-sf * y + d / 2 for _, y in cols)   # the columns along the run (x of M)
    return {'M': M, 'local': frame(px, py, th), 'sf': sf, 'xc': xc, 'w': w, 'd': d, 'z_b': foot[i], 'h': q['h_m'], 'cols': ys,
            'rc': cq['w_m'] / 2, 'taper': cq.get('taper', 1.0) or 1.0, 'col': q['atop'], 'roof': q.get('roof') or {}}


def back_depth(parts, cls, c, foot):
    """the thickness of the wall at a cap's back (a wall or doorway under its back half), 1 m when none"""
    best = None
    for j, r in cls.items():
        if r not in ('wall', 'doorway'): continue
        q = parts[j]
        for x, y, th in instances(q):
            if r == 'wall': pts = [to_whole(x, y, th, *p) for p in q['plan_m']]
            else: pts = [to_whole(x, y, th, sx * q['length_m'] / 2, sy * q['depth_m'] / 2) for sx in (-1, 1) for sy in (-1, 1)]
            Mi = c['M'].inverted(); loc = [Mi @ Vector((a, b, 0)) for a, b in pts]   # (in the run's frame: y from the columns' axis out)
            back = -(c['xc'] + c['w'] / 2)
            if all(back - .05 <= v.y <= -(c['xc']) and -.5 <= v.x <= c['d'] + .5 for v in loc):
                t = max(v.y for v in loc) - back
                best = t if best is None else max(best, t)
    return best if best is not None else 1.0


def build_parts(S, skip=()):
    """the portico's objects from the spec's parts (skip: parts another module draws): floor, columns, entablature, walls, roofs"""
    parts = S['parts']; cls = classify(parts, skip); foot, top = levels(parts)
    stone = kit.stone(); mats = [stone, kit.dark(), kit.roof()]   # (material 2: a roof's covering, shaded as the film's roofs)
    caps = {i: cap_frame(parts, i, foot, S) for i, r in cls.items() if r == 'cap'}
    under = {c['col']: c for c in caps.values()}   # (a row of columns -> the cap on it)
    fl, co, en, wa, ro = (bmesh.new() for _ in range(5))
    sa = .03   # (the stylobate course: this much over the floor, the columns' feet on it)

    for i, r in cls.items():
        q = parts[i]
        if r == 'floor':
            for x, y, th in instances(q):
                prism_plan(fl, [to_whole(x, y, th, *p) for p in q['plan_m']], foot[i], foot[i] + q['h_m'])
        elif r == 'wall':
            ph, pp = S['plinth_m']
            for x, y, th in instances(q):
                pts = q['plan_m']
                prism_plan(wa, [to_whole(x, y, th, *p) for p in pts], foot[i], top[i])
                if len(pts) == 4:   # a straight wall: a plinth along both its long faces
                    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
                    M = frame(x, y, th)
                    if x1 - x0 >= y1 - y0: kit.box(wa, x0 - pp, x1 + pp, y0 - pp, y1 + pp, foot[i], foot[i] + ph, xf=M)   # (round its ends too: no face in the plane of the wall's end)
                    else: kit.box(wa, x0 - pp, x1 + pp, y0 - pp, y1 + pp, foot[i], foot[i] + ph, xf=M)
        elif r == 'doorway':
            for x, y, th in instances(q):
                doorway(wa, q, foot[i], frame(x, y, th))
        elif r == 'columns':
            c = under.get(i); rc = q['w_m'] / 2; tp = q.get('taper', 1.0) or 1.0
            z0 = foot[i] + (sa if c else 0.0); z1 = top[i]
            for x, y, th in instances(q):
                column_free(co, S['order'], rc, z0, z1, frame(x, y, th), taper=tp, seg=S['column_seg'])
            if c:   # the stylobate course under the row, as wide as the plinths, from the ground (past the floor's edge)
                p = rc * 1.3 + .06; xs = c['cols']; g = foot[q['atop']] if q.get('atop') is not None else foot[i]
                kit.box(fl, xs[0] - p, xs[-1] + p, -p, p, g, foot[i] + sa, xf=c['M'])

    for i, c in caps.items():
        cap(en, wa, ro, parts, cls, c, foot, S)

    out = []
    for name, bm in (('floor', fl), ('columns', co), ('entablature', en), ('walls', wa), ('roofs', ro)):
        if len(bm.faces): out.append(kit.obj(name, bm, mats))
        else: bm.free()
    return out


def doorway(bm, q, z0, M):
    """an `arches` part as a wall with its openings (flat-headed: rectangular; round: arched), a moulded frame round each on both
    faces; M: its frame (x along it, y through it)"""
    Lm, h, dep, n = q['length_m'], q['h_m'], q['depth_m'], q.get('bays') or 1
    bay = Lm / n; span = bay * q['opening']; vs = h / (q.get('tiers') or 1) * q['spring']
    Mf = M @ Matrix.Translation((0, dep / 2, 0))   # (its front face at y = 0 of this frame)
    if q.get('arch', 'flat') == 'flat':
        holes = [(-Lm / 2 + (k + .5) * bay - span / 2, -Lm / 2 + (k + .5) * bay + span / 2, z0, z0 + vs) for k in range(n)]
        wall_openings(bm, -Lm / 2, Lm / 2, dep, z0, z0 + h, holes, xf=Mf)
        for xa, xb, za, zb in holes:
            w = min(.4, max(.15, (bay - span) / 4)); top_ok = zb + w + .3 < z0 + h
            door_frame(bm, xa, xb, za, zb, w=w, cornice=(.3, .2) if top_ok else None, xf=Mf)
            door_frame(bm, -xb, -xa, za, zb, w=w, cornice=(.3, .2) if top_ok else None, xf=M @ Matrix.Translation((0, -dep / 2, 0)) @ Matrix.Rotation(math.pi, 4, 'Z'))
    else:
        for k in range(n):
            kit.arch_panel(bm, bay, h, dep, span, vs, z0=z0, xf=Mf @ Matrix.Translation((-Lm / 2 + (k + .5) * bay, 0, 0)))


def cap(en, wa, ro, parts, cls, c, foot, S):
    """a long_hall on columns: the entablature over them, the beams and ceiling of the walk, the back wall carried up, the roof"""
    M, d, w, xc, zb, h = c['M'], c['d'], c['w'], c['xc'], c['z_b'], c['h']; z0 = zb + h
    rt = c['rc'] * c['taper']; R = c['roof']; o = R.get('overhang_m', .2) if R.get('overhang_m') is not None else .2
    yc = w / 2 + o - xc   # (the eaves' line, out from the columns' axis: the cornice reaches it)
    sa, sf_, sc = S['ent_split']; tot = sa + sf_ + sc; ha, hf, hc = h * sa / tot, h * sf_ / tot, h * sc / tot
    pa = .08; off = rt - pa * .6
    ent = kit.entablature([[pa, ha], [.06, hf], [yc - off, hc]], zb)
    sec = [(-rt, zb)] + [(p + off, z) for p, z in ent] + [(-rt, z0)]
    extrude(en, sec, (0, 0, 0), (d, 0, 0), xf=M, closed=True)   # (closed: its face on the walk's side)
    wt = back_depth(parts, cls, c, foot); yb_out = -(xc + w / 2); yb_in = yb_out + wt
    bw, bd = S['beam_m']
    for x in c['cols']:   # the beams across the walk, from the architrave to the back wall
        kit.box(en, x - bw / 2, x + bw / 2, yb_in, -rt, z0 - bd, z0, xf=M)
    kit.box(wa, 0, d, yb_out, yb_in, zb, z0, xf=M)   # the back wall behind the entablature
    kit.box(wa, 0, d, yb_in, yb_in + .06, zb, zb + ha, xf=M)   # (its band on the walk's side, the architrave's line)
    shape = S['roof'] or R.get('shape', 'gabled'); pitch = math.radians(R.get('pitch_deg') or 15.0); e = S['eave_m']
    ridge = z0 + w / 2 * math.tan(pitch)   # (the film's ridge: its gable over the block's top)
    xo = o * .6   # (the roof past the block's ends, as the film's)
    Mr = M @ Matrix.Translation((0, -xc, 0))   # (the roof's frame: y across from the block's middle line)
    if shape == 'lean_to':
        roof_lean(ro, Mr, -xo, d + xo, w / 2 + o, -(w / 2 + o), z0, e, z0 + e + (w + 2 * o) * math.tan(pitch), S['tile_m'], S['tile_r'], cover=2)
    else:
        roof_gable(ro, Mr, -xo, d + xo, w / 2 + o, z0, e, ridge, S['tile_m'], S['tile_r'], cover=2)


def from_landmark(L):
    """the landmark's parts (pipeline/landmarks.py FIELDS: column, prism, arches, long_hall) as this spec's"""
    if L.get('kind') != 'parts': raise SystemExit(f'portico: a parts landmark, not {L.get("kind")}')
    return {'parts': L['parts']}


def build(s):
    S = {**DEFAULT, **(s or {})}
    return build_parts(S)

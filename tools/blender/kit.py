"""Geometry for landmark models made in Blender (docs/MUSEUM.md "Detailed models"): run inside Blender (bpy), never imported by
the pipeline. Units are metres, Blender's axes: x east, y north, z up; a building's plan is centred on the origin and turned by
the landmark's theta_deg afterwards (build.py), as the film's generator turns it.

A building is a few named objects, one per part a museum page can say is sourced or estimated (amphitheatre.py: facade_arcades,
orders, attic, cavea, ...), each built from meshes made here: bays placed round a plan curve, profiles swept along it, steps,
columns; the classical orders (column, entablature) for any building that has them. Two materials: stone (the model's white)
and dark (an opening seen into, as the film's dark parts). A helper two kinds need belongs here, not copied into each."""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector


# ---- the scene and materials

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, rgb, rough=.85):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*rgb, 1.0); b.inputs['Roughness'].default_value = rough
    return m


def stone(): return material('stone', (.86, .84, .80))
def dark(): return material('dark', (.06, .06, .07), .95)


def obj(name, bm, mats):
    """a bmesh as an object of its own (its faces' material_index into mats), normals made consistent; the edges where faces meet
    at more than 40 degrees split, so a turned profile is smooth round its axis and keeps its steps (a base's torus, an abacus's
    edge) sharp: shaded smooth across them, a step showed as a soft gradient"""
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    sharp = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(40)]
    if sharp: bmesh.ops.split_edges(bm, edges=sharp)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    return o


# ---- a plan curve: an ellipse, walked at equal steps along it

class Oval:
    """the ellipse x = a cos t, y = b sin t; points at equal distances along it, and its outward normal; offset(d): a point d
    inside it along the normal (the true parallel curve: an amphitheatre's rings are parallel, not smaller ellipses)"""

    def __init__(self, a, b, n=20000):
        self.a, self.b = a, b
        ts = [math.tau * i / n for i in range(n + 1)]
        L = [0.0]
        for t0, t1 in zip(ts, ts[1:]): L.append(L[-1] + math.dist(self.xy(t0), self.xy(t1)))
        self.ts, self.L, self.length = ts, L, L[-1]

    def xy(self, t): return (self.a * math.cos(t), self.b * math.sin(t))

    def normal(self, t):
        nx, ny = self.b * math.cos(t), self.a * math.sin(t); k = math.hypot(nx, ny); return (nx / k, ny / k)

    def t_at(self, s):
        """the parameter at arc length s (0..length)"""
        s %= self.length; lo, hi = 0, len(self.L) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if self.L[m] <= s: lo = m
            else: hi = m
        f = (s - self.L[lo]) / max(1e-12, self.L[hi] - self.L[lo]); return self.ts[lo] + f * (self.ts[hi] - self.ts[lo])

    def frame(self, s, d=0.0):
        """at arc length s, d metres inside: the point, the tangent (direction of travel) and the outward normal"""
        t = self.t_at(s); nx, ny = self.normal(t); x, y = self.xy(t)
        return Vector((x - d * nx, y - d * ny, 0)), Vector((ny, -nx, 0)), Vector((nx, ny, 0))   # (tangent x normal = up: a right-handed bay frame)


# ---- sweeps: a profile carried round the curve

def sweep(bm, oval, profile, n, mat=0, d0=0.0, closed=True):
    """a ring: the profile [(out, z), ...] (out: metres outward of the curve offset d0 inward) at n equal steps round it,
    consecutive profile points joined into faces"""
    rings = []
    for i in range(n):
        p, _, nr = oval.frame(oval.length * i / n, d0)
        rings.append([bm.verts.new(p + nr * o + Vector((0, 0, z))) for o, z in profile])
    for i in range(n if closed else n - 1):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for k in range(len(profile) - 1):
            f = bm.faces.new((r0[k], r1[k], r1[k + 1], r0[k + 1])); f.material_index = mat
    return rings


# ---- a bay: a wall panel with an arched opening, in its own frame (x along the wall, y outward, z up)

def arch_panel(bm, w, h, t, ow, spring, z0=0.0, seg=12, mat=0, xf=None):
    """a panel w wide, h high, t thick (front at y=0, back at y=-t), from z0; an opening ow wide whose sides rise to spring, then
    a round arch (radius ow/2). Built face by face (no booleans): piers, the spandrels between the arch and the panel's edges,
    the soffit and jambs. xf: a Matrix placing the bay"""
    r = ow / 2; cz = z0 + spring; top = z0 + h
    M = xf or Matrix.Identity(4)
    V = lambda x, y, z: bm.verts.new(M @ Vector((x, y, z)))
    angs = sorted(set([math.pi * i / seg for i in range(seg + 1)] + [math.atan2(top - cz, w / 2), math.pi - math.atan2(top - cz, w / 2)]))

    def edge(a):   # where the ray from the arch centre at angle a meets the panel's edge (sides above the spring, or its top)
        c, s = math.cos(a), math.sin(a); ks = []
        if abs(c) > 1e-9: ks.append((w / 2) / abs(c))
        if s > 1e-9: ks.append((top - cz) / s)
        k = min(ks); return (k * c, cz + k * s)

    faces = []
    for y in (0.0, -t):
        inner = [V(r * math.cos(a), y, cz + r * math.sin(a)) for a in angs]
        outer = [V(*(lambda p: (p[0], y, p[1]))(edge(a))) for a in angs]
        for i in range(len(angs) - 1): faces.append((inner[i], inner[i + 1], outer[i + 1], outer[i]))
        # piers: from the floor to the spring, either side of the opening
        for sx in (-1, 1):
            a, b = sx * w / 2, sx * r
            q = [V(a, y, z0), V(b, y, z0), V(b, y, cz), V(a, y, cz)]; faces.append(tuple(q))
        if y == 0.0: front_in = inner
        else: back_in = inner
    for i in range(len(angs) - 1): faces.append((front_in[i], back_in[i], back_in[i + 1], front_in[i + 1]))   # the soffit
    for sx in (-1, 1):   # the jambs
        faces.append((V(sx * r, 0, z0), V(sx * r, -t, z0), V(sx * r, -t, cz), V(sx * r, 0, cz)))
    faces.append((V(-w / 2, 0, top), V(w / 2, 0, top), V(w / 2, -t, top), V(-w / 2, -t, top)))   # its top
    for q in faces:
        try: f = bm.faces.new(q); f.material_index = mat
        except ValueError: pass


def box(bm, x0, x1, y0, y1, z0, z1, mat=0, xf=None):
    M = xf or Matrix.Identity(4)
    v = [bm.verts.new(M @ Vector(p)) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        f = bm.faces.new([v[i] for i in q]); f.material_index = mat


def cylinder(bm, x, y, z0, z1, r0, r1=None, seg=16, mat=0, xf=None, caps=True):
    """an upright drum or a taper (r0 at its foot, r1 at its head), centred on (x, y) in the bay's frame; its side shaded smooth
    (a round shaft, not a prism of seg faces), its caps flat"""
    M = xf or Matrix.Identity(4); r1 = r0 if r1 is None else r1
    lo = [bm.verts.new(M @ Vector((x + r0 * math.cos(math.tau * i / seg), y + r0 * math.sin(math.tau * i / seg), z0))) for i in range(seg)]
    hi = [bm.verts.new(M @ Vector((x + r1 * math.cos(math.tau * i / seg), y + r1 * math.sin(math.tau * i / seg), z1))) for i in range(seg)]
    for i in range(seg):
        f = bm.faces.new((lo[i], lo[(i + 1) % seg], hi[(i + 1) % seg], hi[i])); f.material_index = mat; f.smooth = True
    if caps:
        f = bm.faces.new(list(reversed(lo))); f.material_index = mat
        f = bm.faces.new(hi); f.material_index = mat


def bay_frame(oval, s, d=0.0, z=0.0):
    """the Matrix that puts a bay (x along the wall, y outward, z up) at arc length s, d inside the curve"""
    p, tg, nr = oval.frame(s, d)
    return Matrix(((tg.x, nr.x, 0, p.x), (tg.y, nr.y, 0, p.y), (0, 0, 1, z), (0, 0, 0, 1)))


def rect_panel(bm, w, h, t, ow=0.0, oz0=0.0, oz1=0.0, z0=0.0, mat=0, xf=None, reveal=None):
    """a panel w wide, h high, t thick (front at y=0, back at y=-t), from z0, in a bay's frame; with ow > 0 a rectangular opening
    ow wide from oz0 to oz1 (heights above z0), its sides, sill and head as faces through the wall (a window seen in depth), in
    the material reveal (mat if None: dark, a small opening reads as one from any side, its sides lit white did not)"""
    M = xf or Matrix.Identity(4); top = z0 + h
    V = lambda x, y, z: bm.verts.new(M @ Vector((x, y, z)))
    quads = []
    for y in (0.0, -t):
        if ow > 0:
            a, b, za, zb = ow / 2, w / 2, z0 + oz0, z0 + oz1
            quads += [((-b, y, z0), (-a, y, z0), (-a, y, top), (-b, y, top)), ((a, y, z0), (b, y, z0), (b, y, top), (a, y, top)),
                      ((-a, y, z0), (a, y, z0), (a, y, za), (-a, y, za)), ((-a, y, zb), (a, y, zb), (a, y, top), (-a, y, top))]
        else:
            quads.append(((-w / 2, y, z0), (w / 2, y, z0), (w / 2, y, top), (-w / 2, y, top)))
    quads.append(((-w / 2, 0, top), (w / 2, 0, top), (w / 2, -t, top), (-w / 2, -t, top)))
    rev = []
    if ow > 0:
        a, za, zb = ow / 2, z0 + oz0, z0 + oz1
        rev += [((sx * a, 0, za), (sx * a, -t, za), (sx * a, -t, zb), (sx * a, 0, zb)) for sx in (-1, 1)]
        rev += [((-a, 0, z), (a, 0, z), (a, -t, z), (-a, -t, z)) for z in (za, zb)]
    for qs, m in ((quads, mat), (rev, mat if reveal is None else reveal)):
        for q in qs:
            f = bm.faces.new([V(*p) for p in q]); f.material_index = m


def lathe(bm, profile, seg=16, x=0.0, y=0.0, a0=0.0, a1=math.tau, mat=0, xf=None):
    """a profile [(r, z), ...] turned round the upright line through (x, y) of a bay's frame, from angle a0 to a1 (a whole turn,
    or a half from 0 to pi: an engaged column's front, y >= 0, the rest in the wall); shaded smooth round the turn"""
    M = xf or Matrix.Identity(4); whole = abs(a1 - a0 - math.tau) < 1e-9; n = seg if whole else seg + 1
    rings = [[bm.verts.new(M @ Vector((x + r * math.cos(a), y + r * math.sin(a), z))) for r, z in profile]
             for a in (a0 + (a1 - a0) * i / seg for i in range(n))]
    for i in range(seg):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for k in range(len(profile) - 1):
            if profile[k] == profile[k + 1]: continue
            f = bm.faces.new((r0[k], r1[k], r1[k + 1], r0[k + 1])); f.material_index = mat; f.smooth = True


def arch_band(bm, r, cz, profile, seg=12, mat=0, xf=None):
    """a moulding round a round arch of radius r springing at cz (a bay's frame, the wall's face at y=0): the profile
    [(dr, out), ...] (dr metres beyond the arch's edge, out metres in front of the face) carried round the half circle"""
    M = xf or Matrix.Identity(4)
    rings = [[bm.verts.new(M @ Vector(((r + dr) * math.cos(a), out, cz + (r + dr) * math.sin(a)))) for dr, out in profile]
             for a in (math.pi * i / seg for i in range(seg + 1))]
    for i in range(seg):
        for k in range(len(profile) - 1):
            f = bm.faces.new((rings[i][k], rings[i + 1][k], rings[i + 1][k + 1], rings[i][k + 1])); f.material_index = mat
    for ring in (rings[0], rings[-1]):   # (its ends closed: they stand on the impost)
        if len(profile) > 2:
            f = bm.faces.new(ring); f.material_index = mat


# ---- the classical orders (any building with columns, pilasters and entablatures)

def column(bm, order, rc, z0, z1, M):
    """an engaged half-column from z0 to the top of its capital z1 (radius rc at its foot, tapering a twelfth), its front half
    turned (the rest is in the wall): a Tuscan base and capital, an Attic base under Ionic (volutes) and Corinthian (a bell of
    two rows of leaves) capitals; plinth and abacus square"""
    half = dict(seg=8, a0=0.0, a1=math.pi, xf=M); rt = rc * .92
    if order == 'tuscan':
        box(bm, -rc * 1.3, rc * 1.3, -.05, rc * 1.3, z0, z0 + .2, xf=M)
        lathe(bm, [(rc * 1.22, z0 + .2), (rc * 1.28, z0 + .27), (rc * 1.22, z0 + .36), (rc * 1.06, z0 + .4), (rc, z0 + .45)], **half)
        cap0 = z1 - .55
        lathe(bm, [(rc, z0 + .45), (rt, cap0)], **half)
        lathe(bm, [(rt, cap0), (rt * 1.08, cap0 + .04), (rt, cap0 + .09), (rt, cap0 + .22), (rt * 1.05, cap0 + .25), (rc * 1.22, cap0 + .37)], **half)
        box(bm, -rc * 1.32, rc * 1.32, -.05, rc * 1.32, z1 - .18, z1, xf=M)
        return
    box(bm, -rc * 1.35, rc * 1.35, -.05, rc * 1.35, z0, z0 + .16, xf=M)   # the Attic base: torus, scotia, torus
    lathe(bm, [(rc * 1.28, z0 + .16), (rc * 1.34, z0 + .22), (rc * 1.28, z0 + .29), (rc * 1.12, z0 + .31), (rc * 1.1, z0 + .37),
                   (rc * 1.18, z0 + .4), (rc * 1.12, z0 + .46), (rc * 1.03, z0 + .48), (rc, z0 + .52)], **half)
    if order == 'ionic':
        cap0 = z1 - .45
        lathe(bm, [(rc, z0 + .52), (rt, cap0)], **half)
        lathe(bm, [(rt, cap0), (rt * 1.07, cap0 + .04), (rt, cap0 + .08), (rt * 1.25, cap0 + .22)], **half)   # the astragal, the echinus
        box(bm, -rc * 1.15, rc * 1.15, -.05, rc * .95, cap0 + .14, z1 - .1, xf=M)   # the cushion between the volutes
        for sx in (-1, 1):   # the volutes, their eyes facing out
            Mv = M @ Matrix.Translation((sx * rc * 1.15, 0, cap0 + .14)) @ Matrix.Rotation(math.pi / 2, 4, 'X')
            cylinder(bm, 0, 0, -rc * 1.0, 0, .2, seg=12, xf=Mv)
            cylinder(bm, 0, 0, -rc * 1.05, -rc * 1.0, .09, seg=10, xf=Mv)
        box(bm, -rc * 1.4, rc * 1.4, -.05, rc * 1.25, z1 - .1, z1, xf=M)
        return
    cap0 = z1 - 1.15   # Corinthian
    lathe(bm, [(rc, z0 + .52), (rt, cap0)], **half)
    lathe(bm, [(rt, cap0), (rt * 1.07, cap0 + .04), (rt, cap0 + .08), (rt * 1.3, cap0 + .3), (rt * 1.02, cap0 + .36),   # two rows of leaves curling out
                   (rt * 1.5, cap0 + .68), (rt * 1.15, cap0 + .74), (rc * 1.42, cap0 + .97)], seg=12, a0=0.0, a1=math.pi, xf=M)
    box(bm, -rc * 1.55, rc * 1.55, -.05, rc * 1.45, z1 - .18, z1, xf=M)   # the abacus
    box(bm, -rc * .3, rc * .3, -.05, rc * 1.55, z1 - .16, z1 - .02, xf=M)   # the flower on its face
    for sx in (-1, 1):   # the corner scrolls under the abacus
        box(bm, sx * rc * 1.15 - .12, sx * rc * 1.15 + .12, rc * .9, rc * 1.4, z1 - .42, z1 - .18, xf=M)


def entablature(ent, z):
    """the profile (out, z) of an entablature from z: [architrave, frieze, cornice] as [projection, height]; the architrave in three
    fasciae, the frieze plain, the cornice in a bed moulding, the corona and the crowning moulding"""
    (pa, ha), (pf, hf), (pc, hc) = ent
    p = [(0, z), (pa * .6, z), (pa * .6, z + ha * .3), (pa * .78, z + ha * .33), (pa * .78, z + ha * .62), (pa * .92, z + ha * .66),
         (pa * .92, z + ha * .88), (pa, z + ha * .92), (pa, z + ha)]
    z += ha; p += [(pf, z), (pf, z + hf)]; z += hf
    p += [(pf + (pc - pf) * .25, z + hc * .12), (pf + (pc - pf) * .25, z + hc * .25), (pf + (pc - pf) * .5, z + hc * .3),
          (pc * .9, z + hc * .45), (pc * .9, z + hc * .7), (pc, z + hc * .85), (pc, z + hc), (0, z + hc)]
    return p

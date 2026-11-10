"""Geometry for landmark models made in Blender (docs/MUSEUM.md "Detailed models"): run inside Blender (bpy), never imported by
the pipeline. Units are metres, Blender's axes: x east, y north, z up; a building's plan is centred on the origin and turned by
the landmark's theta_deg afterwards (build.py), as the film's generator turns it.

A building is a few named objects, one per part a museum page can say is sourced or estimated (amphitheatre.py: facade_arcades,
orders, attic, cavea, ...), each built from meshes made here: bays placed round a plan curve, profiles swept along it, steps,
columns. Two materials: stone (the model's white) and dark (an opening seen into, as the film's dark parts)."""
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
    """a bmesh as an object of its own (its faces' material_index into mats), normals made consistent"""
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
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

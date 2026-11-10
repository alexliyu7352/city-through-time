"""A Roman amphitheatre (the Colosseum, Verona, Nimes, Pula ...) as a detailed model: its outer wall in arcaded storeys with their
orders, the attic, the corridor behind the arcades and the second ring of arches, the seating in bands down to the podium and the
arena. Every size comes from the spec (a landmark's sizes and a museum page's notes); what the spec does not give is an estimate
written here as a default, and the part it belongs to says so on the page. Parts (objects):
  facade_arcades   the outer wall's arched bays, storey by storey, and the second ring of arches behind the corridor
  orders           half-columns, their bases and capitals, pedestals, entablatures, the parapets in the upper arches
  attic            the solid top storey: its wall, pilasters, windows, corbels and crowning cornice
  cavea            the seating bands, the walls between them, their openings (vomitoria), the colonnade at the top
  podium           the wall round the arena and its terrace
  arena            the floor
"""
import math

import bmesh
from mathutils import Matrix, Vector

import kit

DEFAULT = {
    'outer_m': [189.0, 156.0],   # the plan's axes
    'ring_m': 55.0,              # from the outer wall to the arena's edge (the arena: outer less twice this)
    'bays': 80,
    'base_m': .6,                # the steps round its foot
    'wall_m': 2.4,               # the outer wall's depth
    'corridor_m': 4.5,           # the corridor behind the arcades
    'inner_wall_m': 2.0,         # the second ring of arches
    'storeys': [                 # each arcaded storey: its height, the arch's width and the height of its sides, its order
        {'h': 10.5, 'arch_w': 4.2, 'spring': 4.95, 'order': 'tuscan', 'pedestal': 0.0},
        {'h': 11.85, 'arch_w': 4.2, 'spring': 4.9, 'order': 'ionic', 'pedestal': 1.6},
        {'h': 11.6, 'arch_w': 4.2, 'spring': 4.9, 'order': 'corinthian', 'pedestal': 1.6}],
    'attic_to_m': 48.0,          # the top of the attic (the building's height)
    'column_r': .5,              # an engaged half-column's radius
    'entablature': [[.35, .7], [.25, .6], [.85, .4]],   # architrave, frieze, cornice: [projection, height] metres
    'terrace_m': 40.0,           # the top of the seating: the terrace behind the attic
    'bands': [                   # seating bands from the top down: rows, each row's rise and run; then the wall below the band
        {'rows': 10, 'rise': .55, 'run': .8, 'drop': 2.0, 'walk': 1.5},
        {'rows': 24, 'rise': .62, 'run': .78, 'drop': 1.6, 'walk': 1.3},
        {'rows': 4, 'rise': .45, 'run': 1.4, 'drop': 0.0, 'walk': 0.0}],
    'podium_m': 4.0,             # the arena wall's height
    'vomitoria': 64,             # openings in each wall between bands
    'portico': {'columns': 160, 'h': 7.0, 'r': .35},   # the colonnade round the top of the seating (an estimate where none survives)
}


def from_landmark(L):
    """the sizes the film's landmark gives (city.yaml, kind ring: outer_m, inner_m, h_m, bays, arena_wall_m), as this spec's keys"""
    out = {}
    if L.get('outer_m'): out['outer_m'] = [float(x) for x in L['outer_m']]
    if L.get('outer_m') and L.get('inner_m'): out['ring_m'] = (float(L['outer_m'][0]) - float(L['inner_m'][0])) / 2   # (the rings are parallel: the long and the short axis give the same)
    if L.get('h_m'): out['attic_to_m'] = float(L['h_m'])
    if L.get('bays'): out['bays'] = int(L['bays'])
    if L.get('arena_wall_m'): out['podium_m'] = float(L['arena_wall_m'])
    return out


def spec_of(s):
    out = {**DEFAULT, **(s or {})}
    out['storeys'] = s.get('storeys', DEFAULT['storeys']) if s else DEFAULT['storeys']
    return out


def build(s):
    S = spec_of(s); a, b = S['outer_m'][0] / 2, S['outer_m'][1] / 2
    ov = kit.Oval(a, b); N = S['bays']; bw = ov.length / N; z0 = S['base_m']; T = S['wall_m']
    stone, dark = kit.stone(), kit.dark(); mats = [stone, dark]
    d_in = T + S['corridor_m']          # the second ring's face
    objs = []

    # ---- the outer wall's arcades and the second ring
    bm = bmesh.new(); zs = []; z = z0
    for st in S['storeys']:
        zs.append(z)
        for i in range(N):
            M = kit.bay_frame(ov, (i + .5) * bw)
            kit.arch_panel(bm, bw, st['h'], T, st['arch_w'], st['spring'] + st.get('pedestal', 0), z0=z, xf=M)
            Mi = kit.bay_frame(ov, (i + .5) * bw, d_in)
            kit.arch_panel(bm, (ov.length - math.tau * d_in) / N, st['h'], S['inner_wall_m'], st['arch_w'] * .9, st['spring'] + st.get('pedestal', 0), z0=z, xf=Mi)   # (a parallel curve d inside is 2 pi d shorter)
        z += st['h']
    attic0 = z
    # floors between the rings at each storey above the ground, and the dark mass behind the second ring (seen through two arches)
    for zf in zs[1:] + [attic0]:
        kit.sweep(bm, ov, [(-0.0, zf), (-d_in, zf)], 4 * N, d0=0.0)
    kit.sweep(bm, ov, [(0, z0), (0, S['terrace_m'])], 4 * N, mat=1, d0=d_in + S['inner_wall_m'] + 1.5)
    objs.append(kit.obj('facade_arcades', bm, mats))

    # ---- the orders
    bm = bmesh.new(); rc = S['column_r']; ent = S['entablature']; eh = sum(h for _, h in ent)
    for k, st in enumerate(S['storeys']):
        zb, zt = zs[k], zs[k] + st['h']; ped = st.get('pedestal', 0)
        if ped:   # the pedestal course the columns stand on, and the parapet across each arch
            kit.sweep(bm, ov, [(0, zb), (.55, zb), (.55, zb + ped), (0, zb + ped)], 4 * N)
        col0, col1 = zb + ped, zt - eh
        for i in range(N):
            M = kit.bay_frame(ov, i * bw)
            kit.cylinder(bm, 0, 0, col0 + .35, col1 - .45, rc, seg=14, xf=M, caps=False)
            kit.cylinder(bm, 0, 0, col0, col0 + .35, rc * 1.3, seg=14, xf=M)   # base
            if st['order'] == 'tuscan':
                kit.cylinder(bm, 0, 0, col1 - .45, col1 - .2, rc, rc * 1.25, seg=14, xf=M)
                kit.box(bm, -rc * 1.35, rc * 1.35, -rc * 1.35, rc * 1.35, col1 - .2, col1, xf=M)
            elif st['order'] == 'ionic':
                kit.box(bm, -rc * 1.3, rc * 1.3, -rc * 1.1, rc * 1.1, col1 - .45, col1 - .1, xf=M)
                for sx in (-1, 1): kit.cylinder(bm, sx * rc * 1.25, rc * .9, col1 - .45, col1 - .12, .17, seg=10, xf=M)   # volutes
                kit.box(bm, -rc * 1.4, rc * 1.4, -rc * 1.4, rc * 1.4, col1 - .1, col1, xf=M)
            else:   # corinthian: a flaring bell under the abacus
                kit.cylinder(bm, 0, 0, col1 - 1.1, col1 - .15, rc, rc * 1.45, seg=14, xf=M)
                kit.box(bm, -rc * 1.55, rc * 1.55, -rc * 1.55, rc * 1.55, col1 - .15, col1, xf=M)
            if ped:
                Mc = kit.bay_frame(ov, (i + .5) * bw)
                kit.box(bm, -st['arch_w'] / 2, st['arch_w'] / 2, -T * .7, -T * .3, zb, zb + ped + 1.0, xf=Mc)   # the parapet
        prof, o, zz = [(0, zt - eh)], 0, zt - eh   # the entablature: architrave, frieze, cornice, stepped out
        for proj, h in ent: prof += [(proj, zz), (proj, zz + h)]; zz += h
        prof.append((0, zz)); kit.sweep(bm, ov, prof, 4 * N)
    kit.sweep(bm, ov, [(1.6, 0), (1.6, z0 / 2), (.8, z0 / 2), (.8, z0), (0, z0)], 4 * N)   # the steps round its foot
    objs.append(kit.obj('orders', bm, mats))

    # ---- the attic
    bm = bmesh.new(); top = S['attic_to_m']
    kit.sweep(bm, ov, [(0, attic0), (0, top - .9), (.6, top - .9), (.6, top - .35), (.9, top - .35), (.9, top), (-T, top), (-T, attic0)], 4 * N)
    for i in range(N):
        M = kit.bay_frame(ov, i * bw)
        kit.box(bm, -.55, .55, -.05, .28, attic0 + .6, top - 1.2, xf=M)   # pilaster
        Mc = kit.bay_frame(ov, (i + .5) * bw)
        if i % 2 == 0: kit.box(bm, -.75, .75, -.25, .03, attic0 + 4.2, attic0 + 6.0, mat=1, xf=Mc)   # window
        for k in (-1, 0, 1): kit.box(bm, k * bw / 3 - .25, k * bw / 3 + .25, -.05, .45, top - 3.4, top - 2.9, xf=Mc)   # corbels
    objs.append(kit.obj('attic', bm, mats))

    # ---- the seating, from the terrace down to the podium
    bm = bmesh.new(); d = d_in + S['inner_wall_m'] + 1.0; zt = S['terrace_m']
    prof = [(-T, zt), (-d, zt)]; walls = []
    for bd in S['bands']:
        for r in range(bd['rows']):
            zt -= bd['rise']; prof += [(-d, zt)]; d += bd['run']; prof += [(-d, zt)]
        if bd['drop']:
            d += bd['walk']; prof += [(-d, zt)]; walls.append((d, zt - bd['drop'], zt)); zt -= bd['drop']; prof += [(-d, zt)]
    pod_top, ring = S['podium_m'] + .9, S['ring_m']
    prof += [(-d, pod_top), (-(ring - .6), pod_top)]
    kit.sweep(bm, ov, prof, 4 * N)
    nv = S['vomitoria']
    for dw, za, zb_ in walls:   # openings in the walls between bands
        for i in range(nv):
            M = kit.bay_frame(ov, (i + .5) * ov.length / nv, dw)
            kit.box(bm, -.9, .9, -.02, .5, za + .05, min(zb_, za + 2.1), mat=1, xf=M)
    pc = S['portico']   # the colonnade on the terrace and its roof
    dpc = d_in + S['inner_wall_m'] + .6
    for i in range(pc['columns']):
        M = kit.bay_frame(ov, (i + .5) * ov.length / pc['columns'], dpc)
        kit.cylinder(bm, 0, 0, S['terrace_m'], S['terrace_m'] + pc['h'], pc['r'], seg=10, xf=M)
    kit.sweep(bm, ov, [(-T, S['terrace_m'] + pc['h']), (-(dpc + .6), S['terrace_m'] + pc['h']), (-(dpc + .6), S['terrace_m'] + pc['h'] + .5), (-T, S['terrace_m'] + pc['h'] + .5)], 4 * N)
    objs.append(kit.obj('cavea', bm, mats))

    # ---- the podium and the arena
    bm = bmesh.new()
    kit.sweep(bm, ov, [(-(ring - .6), pod_top), (-(ring - .6), pod_top + .9), (-ring, pod_top + .9), (-ring, 0)], 4 * N)
    objs.append(kit.obj('podium', bm, mats))
    bm = bmesh.new(); vs = []
    for i in range(4 * N):
        p, _, _ = ov.frame(ov.length * i / (4 * N), ring); vs.append(bm.verts.new(p + Vector((0, 0, .02))))
    bm.faces.new(vs)
    objs.append(kit.obj('arena', bm, [kit.material('sand', (.78, .70, .55))]))
    return objs

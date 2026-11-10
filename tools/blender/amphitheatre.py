"""A Roman amphitheatre (the Colosseum, Verona, Nimes, Pula ...) as a detailed model: its outer wall in arcaded storeys with their
orders, the attic, the corridor behind the arcades and the second ring of arches, the seating in bands down to the podium and the
arena. Every size comes from the spec (a landmark's sizes and a museum page's notes); what the spec does not give is an estimate
written here as a default, and the part it belongs to says so on the page. Parts (objects):
  facade_arcades   the outer wall's arched bays, storey by storey, their archivolts and imposts, the vaulted corridor behind
                   them and the second ring of arches
  orders           half-columns with their bases and capitals (Tuscan, Ionic, Corinthian), pedestals, entablatures (architrave
                   in fasciae, frieze, cornice), the parapets in the upper arches
  attic            the solid top storey: its wall, windows in every other bay, pilasters with base and capital, corbels, the
                   crowning cornice and the sockets through it for the awning's masts
  cavea            the seating bands, the stairs dividing them into wedges, the walls between them and their openings
                   (vomitoria), the colonnade at the top
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
    'stairs': 64,                # stairways down each band (dividing it into wedges), between its openings
    'archivolt_m': [.45, .2],    # the moulding round each outer arch: its width and how far it stands out
    'impost_m': [.35, .18],      # the moulding the arch springs from: its height and how far it stands out
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


def column(bm, order, rc, z0, z1, M):
    """an engaged half-column from z0 to the top of its capital z1 (radius rc at its foot, tapering a twelfth), its front half
    turned (the rest is in the wall): a Tuscan base and capital, an Attic base under Ionic (volutes) and Corinthian (a bell of
    two rows of leaves) capitals; plinth and abacus square"""
    half = dict(seg=8, a0=0.0, a1=math.pi, xf=M); rt = rc * .92
    if order == 'tuscan':
        kit.box(bm, -rc * 1.3, rc * 1.3, -.05, rc * 1.3, z0, z0 + .2, xf=M)
        kit.lathe(bm, [(rc * 1.22, z0 + .2), (rc * 1.28, z0 + .27), (rc * 1.22, z0 + .36), (rc * 1.06, z0 + .4), (rc, z0 + .45)], **half)
        cap0 = z1 - .55
        kit.lathe(bm, [(rc, z0 + .45), (rt, cap0)], **half)
        kit.lathe(bm, [(rt, cap0), (rt * 1.08, cap0 + .04), (rt, cap0 + .09), (rt, cap0 + .22), (rt * 1.05, cap0 + .25), (rc * 1.22, cap0 + .37)], **half)
        kit.box(bm, -rc * 1.32, rc * 1.32, -.05, rc * 1.32, z1 - .18, z1, xf=M)
        return
    kit.box(bm, -rc * 1.35, rc * 1.35, -.05, rc * 1.35, z0, z0 + .16, xf=M)   # the Attic base: torus, scotia, torus
    kit.lathe(bm, [(rc * 1.28, z0 + .16), (rc * 1.34, z0 + .22), (rc * 1.28, z0 + .29), (rc * 1.12, z0 + .31), (rc * 1.1, z0 + .37),
                   (rc * 1.18, z0 + .4), (rc * 1.12, z0 + .46), (rc * 1.03, z0 + .48), (rc, z0 + .52)], **half)
    if order == 'ionic':
        cap0 = z1 - .45
        kit.lathe(bm, [(rc, z0 + .52), (rt, cap0)], **half)
        kit.lathe(bm, [(rt, cap0), (rt * 1.07, cap0 + .04), (rt, cap0 + .08), (rt * 1.25, cap0 + .22)], **half)   # the astragal, the echinus
        kit.box(bm, -rc * 1.15, rc * 1.15, -.05, rc * .95, cap0 + .14, z1 - .1, xf=M)   # the cushion between the volutes
        for sx in (-1, 1):   # the volutes, their eyes facing out
            Mv = M @ Matrix.Translation((sx * rc * 1.15, 0, cap0 + .14)) @ Matrix.Rotation(math.pi / 2, 4, 'X')
            kit.cylinder(bm, 0, 0, -rc * 1.0, 0, .2, seg=12, xf=Mv)
            kit.cylinder(bm, 0, 0, -rc * 1.05, -rc * 1.0, .09, seg=10, xf=Mv)
        kit.box(bm, -rc * 1.4, rc * 1.4, -.05, rc * 1.25, z1 - .1, z1, xf=M)
        return
    cap0 = z1 - 1.15   # Corinthian
    kit.lathe(bm, [(rc, z0 + .52), (rt, cap0)], **half)
    kit.lathe(bm, [(rt, cap0), (rt * 1.07, cap0 + .04), (rt, cap0 + .08), (rt * 1.3, cap0 + .3), (rt * 1.02, cap0 + .36),   # two rows of leaves curling out
                   (rt * 1.5, cap0 + .68), (rt * 1.15, cap0 + .74), (rc * 1.42, cap0 + .97)], seg=12, a0=0.0, a1=math.pi, xf=M)
    kit.box(bm, -rc * 1.55, rc * 1.55, -.05, rc * 1.45, z1 - .18, z1, xf=M)   # the abacus
    kit.box(bm, -rc * .3, rc * .3, -.05, rc * 1.55, z1 - .16, z1 - .02, xf=M)   # the flower on its face
    for sx in (-1, 1):   # the corner scrolls under the abacus
        kit.box(bm, sx * rc * 1.15 - .12, sx * rc * 1.15 + .12, rc * .9, rc * 1.4, z1 - .42, z1 - .18, xf=M)


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


def build(s):
    S = spec_of(s); a, b = S['outer_m'][0] / 2, S['outer_m'][1] / 2
    ov = kit.Oval(a, b); N = S['bays']; bw = ov.length / N; z0 = S['base_m']; T = S['wall_m']
    stone, dark = kit.stone(), kit.dark(); mats = [stone, dark]
    d_in = T + S['corridor_m']          # the second ring's face
    objs = []

    # ---- the outer wall's arcades and the second ring
    bm = bmesh.new(); zs = []; z = z0
    av_w, av_p = S['archivolt_m']; im_h, im_p = S['impost_m']; cw = S['corridor_m'] / 2
    av = [(0, 0), (0, av_p * .6), (av_w * .35, av_p * .6), (av_w * .35, av_p), (av_w, av_p), (av_w, 0)]   # (two bands, the outer standing out more)
    for st in S['storeys']:
        zs.append(z); spring = st['spring'] + st.get('pedestal', 0); r = st['arch_w'] / 2
        for i in range(N):
            M = kit.bay_frame(ov, (i + .5) * bw)
            kit.arch_panel(bm, bw, st['h'], T, st['arch_w'], spring, z0=z, xf=M)
            kit.arch_band(bm, r, z + spring, av, xf=M)
            for sx in (-1, 1):   # the impost across each pier, from the arch to the half-column
                kit.box(bm, min(sx * r, sx * bw / 2), max(sx * r, sx * bw / 2), 0, im_p, z + spring - im_h, z + spring, xf=M)
            Mi = kit.bay_frame(ov, (i + .5) * bw, d_in)
            kit.arch_panel(bm, (ov.length - math.tau * d_in) / N, st['h'], S['inner_wall_m'], st['arch_w'] * .9, spring, z0=z, xf=Mi)   # (a parallel curve d inside is 2 pi d shorter)
        # the corridor's barrel vault, its crown under the floor above (seen through the arches: not a flat ceiling)
        zv = z + st['h'] - .6 - cw
        kit.sweep(bm, ov, [(-(T + cw) + cw * math.cos(math.pi * k / 10), zv + cw * math.sin(math.pi * k / 10)) for k in range(11)], 4 * N)
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
            kit.sweep(bm, ov, [(0, zb), (.55, zb), (.55, zb + .15), (.62, zb + .22), (.55, zb + .3), (.55, zb + ped - .2), (.66, zb + ped - .1), (.66, zb + ped), (0, zb + ped)], 4 * N)
        col0, col1 = zb + ped, zt - eh
        for i in range(N):
            M = kit.bay_frame(ov, i * bw)
            column(bm, st['order'], rc, col0, col1, M)
            if ped:
                Mc = kit.bay_frame(ov, (i + .5) * bw)
                kit.box(bm, -st['arch_w'] / 2, st['arch_w'] / 2, -T * .7, -T * .3, zb, zb + ped + 1.0, xf=Mc)   # the parapet
                kit.box(bm, -st['arch_w'] / 2, st['arch_w'] / 2, -T * .7 - .08, -T * .3 + .08, zb + ped + 1.0, zb + ped + 1.15, xf=Mc)   # its coping
        kit.sweep(bm, ov, entablature(ent, zt - eh), 4 * N)
    kit.sweep(bm, ov, [(1.6, 0), (1.6, z0 / 2), (.8, z0 / 2), (.8, z0), (0, z0)], 4 * N)   # the steps round its foot
    objs.append(kit.obj('orders', bm, mats))

    # ---- the attic
    bm = bmesh.new(); top = S['attic_to_m']; wtop = top - .9; ph = .3
    kit.sweep(bm, ov, [(0, wtop), (.25, wtop), (.25, wtop + .12), (.45, wtop + .2), (.6, wtop + .35), (.6, top - .35), (.75, top - .3), (.9, top - .2), (.9, top), (-T, top), (-T, wtop)], 4 * N)   # the crowning cornice
    kit.sweep(bm, ov, [(0, attic0), (.35, attic0), (.35, attic0 + .25), (.2, attic0 + .4), (0, attic0 + .4)], 4 * N)   # the plinth course
    for i in range(N):
        Mc = kit.bay_frame(ov, (i + .5) * bw)
        if i % 2 == 0:   # a window through the wall, dark behind
            kit.rect_panel(bm, bw, wtop - attic0, T, 1.5, 4.2, 6.0, z0=attic0, xf=Mc, reveal=1)
            kit.box(bm, -.85, .85, -T - .12, -T - .04, attic0 + 4.1, attic0 + 6.1, mat=1, xf=Mc)
        else:
            kit.rect_panel(bm, bw, wtop - attic0, T, z0=attic0, xf=Mc)
        for k in (-1, 0, 1):   # the corbels for the masts, and the sockets through the cornice above them
            x = k * bw / 3
            kit.box(bm, x - .25, x + .25, -.05, .42, top - 3.4, top - 3.1, xf=Mc)
            kit.box(bm, x - .22, x + .22, -.05, .28, top - 3.1, top - 2.9, xf=Mc)
            kit.box(bm, x - .2, x + .2, .2, .6, top - .015, top + .005, mat=1, xf=Mc)
        M = kit.bay_frame(ov, i * bw)   # the pilaster: base, shaft, capital
        kit.box(bm, -.68, .68, -.05, ph + .1, attic0 + .4, attic0 + .75, xf=M)
        kit.box(bm, -.55, .55, -.05, ph, attic0 + .75, top - 1.6, xf=M)
        kit.box(bm, -.62, .62, -.05, ph + .05, top - 1.6, top - 1.45, xf=M)
        kit.box(bm, -.72, .72, -.05, ph + .12, top - 1.45, top - 1.2, xf=M)
    objs.append(kit.obj('attic', bm, mats))

    # ---- the seating, from the terrace down to the podium
    bm = bmesh.new(); d = d_in + S['inner_wall_m'] + 1.0; zt = S['terrace_m']
    prof = [(-T, zt), (-d, zt)]; walls = []; ns = S['stairs']
    for bd in S['bands']:
        for r in range(bd['rows']):
            zt -= bd['rise']; prof += [(-d, zt)]
            for i in range(ns):   # a stair's half-step on each row's tread, by the row above: the stairs between the openings
                M = kit.bay_frame(ov, i * ov.length / ns, d)
                kit.box(bm, -.6, .6, -bd['run'] / 2, 0, zt, zt + bd['rise'] / 2, xf=M)
            d += bd['run']; prof += [(-d, zt)]
        if bd['drop']:
            d += bd['walk']; prof += [(-d, zt)]; walls.append((d, zt - bd['drop'], zt)); zt -= bd['drop']; prof += [(-d, zt)]
    pod_top, ring = S['podium_m'] + .9, S['ring_m']
    prof += [(-d, pod_top), (-(ring - .6), pod_top)]
    kit.sweep(bm, ov, prof, 4 * N)
    nv = S['vomitoria']
    for dw, za, zb_ in walls:   # openings in the walls between bands
        for i in range(nv):
            M = kit.bay_frame(ov, (i + .5) * ov.length / nv, dw)
            kit.box(bm, -.9, .9, -.04, 0, za + .05, min(zb_ - .25, za + 2.1), mat=1, xf=M)   # (a dark panel on the wall's face, short of its top: an opening, not a block)
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

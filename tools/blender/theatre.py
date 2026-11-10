"""A Roman theatre (Pompey's, Marcellus's, Orange, Aspendos ...) as a detailed model: a half ring of seating round the orchestra,
closed by the stage building, as the film's generator draws a `ring` landmark with plan: half (pipeline/landmarks.py _ring): the
cavea on the frame's +y, its outer wall a half circle, the stage building a straight block across the open side (on -y, 1 m
behind the orchestra's diameter). Its massing is the generator's: the outer wall's height, the seating falling in bands from the
top walk to the podium round the orchestra, the stage block's width, depth and height. Parts (objects):
  facade_arcades   the curved outer wall's arched bays, storey by storey, their archivolts and imposts, the vaulted corridor
                   behind them and the second ring of arches, dark behind; the walls closing the half ring's two ends
  orders           engaged half-columns with bases and capitals (Tuscan below, Ionic above, as at the Theatre of Marcellus),
                   the pedestals and parapets of the upper storey, the entablatures, the steps round the foot
  attic            the closed top storey: its wall, windows in every other bay (dark behind), pilasters, the crowning cornice
  cavea            the seating in bands of rows, each band below the top with its walk (praecinctio) under the wall of the band
                   above, the stairs dividing the bands into wedges (more in the upper ones), dark openings (vomitoria) in the
                   walls between bands, the podium wall round the orchestra
  orchestra        the orchestra's floor, out to the stage
  stage            the stage building: its block, the wings at both ends (versurae) with their doors onto the stage, the stage
                   (pulpitum) with its moulded front, the roof over the stage, string courses, pilasters and the cornice round
                   its outer faces
  scaenae_frons    the stage's back wall: a straight front (the stage before the curved recesses of later rebuildings) with its
                   three doors (the royal door in the middle, a guest door each side: dark beyond), and before it storeys of
                   columns on a podium and pedestals, each under its entablature
  temple           a temple on the theatre's axis at the top of the seating, facing the stage over it (the Temple of Venus
                   Victrix at Pompey's theatre: its place is attested, its form is not: here a small prostyle temple, its front
                   of columns under a pediment, an estimate), on a substructure carried down outside the curved wall
Sizes from the landmark (from_landmark): the outer diameter, the orchestra's, the height, the bays, the podium wall, the number of
arcaded storeys, the stage's depth and height. Everything else is a DEFAULT here, an estimate from the type: the storeys' heights
and orders, the attic, the arches, the seating's rows and stairs, the stage's division, the frons's storeys and doors, the temple.
Not built (they need sources): statues (in the frons and the porticoes), the awning and its masts, paintings, inscriptions."""
import math

import bmesh
from mathutils import Matrix, Vector

import kit
import portico as po

DEFAULT = {
    'outer_m': 150.0,            # the outer wall's diameter (the landmark's)
    'orchestra_m': 44.0,         # the orchestra's diameter (the landmark's inner_m)
    'h_m': 36.0,                 # the outer wall's height (the landmark's)
    'bays': 48,                  # arches round the half ring (the landmark's)
    'podium_m': 3.0,             # the wall round the orchestra (the landmark's arena_wall_m)
    'sweep_deg': 180.0,          # how much of a circle the seating takes (the landmark's)
    'arcades': 2,                # storeys of arches under the attic (the landmark's storeys)
    'stage': {'d_m': 14.0, 'h_m': 36.0},   # the stage block's depth and height (the landmark's)
    'base_m': .6,                # the steps round the foot
    'wall_m': 2.4,               # the outer wall's depth
    'corridor_m': 4.5,           # the corridor behind the arcades
    'inner_wall_m': 2.0,         # the second ring of arches
    'storeys': [                 # the arcaded storeys from the ground: height, arch's width (share of a bay), its sides' height, order
        {'h': 12.0, 'arch': .62, 'spring': 6.6, 'order': 'tuscan', 'pedestal': 0.0},
        {'h': 11.4, 'arch': .62, 'spring': 5.2, 'order': 'ionic', 'pedestal': 1.5},
        {'h': 11.4, 'arch': .62, 'spring': 5.2, 'order': 'corinthian', 'pedestal': 1.5}],
    'attic_m': 12.0,             # the closed storey on top (the storeys and the attic are scaled to the height together)
    'column_r': .55,             # an engaged half-column's radius
    'entablature': [[.3, .6], [.22, .5], [.75, .45]],   # architrave, frieze, cornice: [projection, height] metres
    'archivolt_m': [.4, .18],    # the moulding round each arch: its width and how far it stands out
    'impost_m': [.3, .15],       # the moulding the arch springs from: its height and how far it stands out
    'window_m': [1.5, 4.5, 7.3], # the attic's windows: width, sill and head over its foot
    'parapet_m': 1.0,            # the top walk this far under the outer wall's top (its parapet)
    'walk_m': 1.2,               # the walk at the head of each band below the top
    'row_m': .75,                # a row of seats' depth
    'bands': None,               # bands of seats (None: the generator's, the seating's depth over 12 m, 2 to 5)
    'divisions': [12, 12, 12, 6],   # wedges in each band from the top (its stairs between them); the last repeats
    'seat_steps': 96,            # facets of the seating round the half ring
    'stage_parts': {             # the stage building (estimates from the type: Vitruvius 5.6, Orange, Aspendos)
        'scaena_m': 6.0,         # its block behind the frons wall
        'frons_wall_m': 1.5,     # the frons wall's thickness
        'pulpitum_m': 1.5,       # the stage's height (Vitruvius: at most five feet)
        'versura_m': 12.0,       # the wings at both ends, as deep as the block
        'roof_m': [34.5, 1.0],   # the roof over the stage: its underside, its fall toward the front
        'strings': [9.0],        # string courses round the outer faces
        'pilaster_m': 6.0,       # pilasters on the back face, this far apart, from the first string course up
    },
    'frons': {
        'out_m': 1.6,            # the columns this far in front of the wall
        'bay_m': 5.0,            # their spacing
        'storeys': [             # podium or pedestal under the columns, the columns' height and radius, the entablature's height, the order
            {'podium': 2.4, 'h': 9.0, 'r': .45, 'ent': 1.5, 'order': 'corinthian'},
            {'podium': 1.2, 'h': 8.0, 'r': .4, 'ent': 1.3, 'order': 'corinthian'},
            {'podium': 1.1, 'h': 7.0, 'r': .35, 'ent': 1.2, 'order': 'corinthian'}],
        'doors': [[0.0, 4.5, 8.0], [-18.0, 3.5, 7.0], [18.0, 3.5, 7.0]],   # x, width, height over the stage
    },
    'temple': {                  # None: no temple
        'w_m': 12.0, 'd_m': 12.0,    # its front's width, its depth (its front step to the back wall)
        'into_m': 3.0,           # its front this far into the top rows of seats (the rest projects outside the curved wall)
        'columns': 4, 'col_h': 7.5, 'col_r': .42, 'order': 'corinthian', 'ent_m': 1.4, 'pitch_deg': 15.0,
        'pronaos_m': 3.5,        # the porch between the columns and the cella's door
    },
    'column_seg': 12,
}


# ---- for the kit (an open arc of a sweep; a profile's section closing a half ring's end)

def arc_sweep(bm, ov, profile, s0, s1, n, mat=0, d0=0.0):
    """a profile [(out, z), ...] carried along the plan curve ov from arc length s0 to s1 in n steps (an open stretch of
    kit.sweep: its ends left open)"""
    rings = []
    for i in range(n + 1):
        p, _, nr = ov.frame(s0 + (s1 - s0) * i / n, d0)
        rings.append([bm.verts.new(p + nr * o + Vector((0, 0, z))) for o, z in profile])
    for i in range(n):
        po._faces(bm, [(rings[i][k], rings[i + 1][k], rings[i + 1][k + 1], rings[i][k + 1]) for k in range(len(profile) - 1)], mat)
    return rings


def section_slab(bm, poly, t, away, thick, mat=0):
    """a slab thick metres along away (a plan vector) whose face is the section poly [(r, z), ...] on the radius at angle t"""
    c, s = math.cos(t), math.sin(t); a = Vector((away[0], away[1], 0)).normalized() * thick
    f0 = [bm.verts.new(Vector((r * c, r * s, z))) for r, z in poly]; f1 = [bm.verts.new(v.co + a) for v in f0]
    n = len(poly)
    po._faces(bm, [f0[::-1], f1] + [(f0[i], f0[(i + 1) % n], f1[(i + 1) % n], f1[i]) for i in range(n)], mat)


# ---- the theatre

def from_landmark(L):
    """the sizes the film's landmark gives (city.yaml, kind ring, plan half: outer_m, inner_m, h_m, bays, arena_wall_m, storeys,
    sweep_deg, stage) as this spec's keys"""
    if L.get('kind') != 'ring' or L.get('plan') != 'half': raise SystemExit('theatre: a ring landmark with plan: half')
    out = {}
    if L.get('outer_m'): out['outer_m'] = float(L['outer_m'][0])
    if L.get('inner_m'): out['orchestra_m'] = float(L['inner_m'][0])
    if L.get('h_m'): out['h_m'] = float(L['h_m'])
    if L.get('bays'): out['bays'] = int(L['bays'])
    if L.get('arena_wall_m') is not None: out['podium_m'] = float(L['arena_wall_m'])
    if L.get('sweep_deg'): out['sweep_deg'] = float(L['sweep_deg'])
    if L.get('storeys'): out['arcades'] = int(L['storeys'])
    if L.get('stage'): out['stage'] = {k: float(v) for k, v in L['stage'].items() if v is not None}
    return out


def spec_of(s):
    S = {**DEFAULT, **(s or {})}
    for k in ('stage_parts', 'frons'): S[k] = {**DEFAULT[k], **((s or {}).get(k) or {})}
    if S.get('temple') is not None: S['temple'] = {**DEFAULT['temple'], **((s or {}).get('temple') or {})}
    st = [dict(x) for x in S['storeys'][:S['arcades']]]
    k = (S['h_m'] - S['base_m']) / (sum(x['h'] for x in st) + S['attic_m'])   # (the storeys and the attic to the wall's height)
    for x in st: x['h'] *= k; x['spring'] *= k; x['pedestal'] = x.get('pedestal', 0) * k
    S['storeys'], S['attic'] = st, S['attic_m'] * k
    return S


def seating(S):
    """the cavea's section as the generator draws it (pipeline/landmarks.py _ring sec): from the top walk at the outer wall down
    to the podium round the orchestra -> (points [(r, z)] from the outer wall's inner face inward to the orchestra's floor; the
    bands [(r, z of its first riser, rows, run, rise, its divisions)]; the walls between bands [(r, z foot, z top, division of
    the band below)])"""
    R, ri, h = S['outer_m'] / 2, S['orchestra_m'] / 2, S['h_m']; band = R - ri
    rim = min(3.0, band * .08); k = S['bands'] or max(2, min(5, round(band / 12)))
    aw = min(S['podium_m'], h * .5); r0 = R - rim; dz = .25 * (h - aw) / k
    ztop = h - S['parapet_m']; dv = S['divisions'] + [S['divisions'][-1]] * k
    pts = [(R - S['wall_m'], ztop), (r0, ztop)]; bands, walls = [], []
    ra, za = r0, ztop
    for j in range(1, k + 1):
        rj, yj = r0 + (ri - r0) * j / k, h + (aw - h) * j / k
        if j > 1: ra -= S['walk_m']; pts.append((ra, za))
        zb = yj + dz if j < k else aw
        n = max(1, round((ra - rj) / S['row_m'])); run = (ra - rj) / n; rise = (za - zb) / n
        for i in range(n): pts += [(ra - i * run, za - (i + 1) * rise), (ra - (i + 1) * run, za - (i + 1) * rise)]
        bands.append((ra, za, n, run, rise, dv[j - 1]))
        if j < k: pts.append((rj, yj)); walls.append((rj, yj, yj + dz, dv[j])); ra, za = rj, yj
    pts.append((ri, 0.0))
    return pts, bands, walls


def z_at(pts, r):
    """the seating's height at radius r"""
    for (r0, z0), (r1, z1) in zip(pts, pts[1:]):
        if min(r0, r1) <= r <= max(r0, r1) and r0 != r1: return min(z0, z1)
    return 0.0


def build(s):
    S = spec_of(s); R = S['outer_m'] / 2; h = S['h_m']; N = S['bays']; T = S['wall_m']; z0 = S['base_m']
    ov = kit.Oval(R, R); sw = math.radians(S['sweep_deg']); t0, t1 = math.pi / 2 - sw / 2, math.pi / 2 + sw / 2
    s0, s1 = R * t0, R * t1; bw = (s1 - s0) / N; n4 = 4 * N
    stone, dark = kit.stone(), kit.dark(); mats = [stone, dark, kit.roof()]   # (material 2: a roof's covering)
    d_in = T + S['corridor_m']; d_dark = d_in + S['inner_wall_m'] + 1.5
    pts, bands, walls = seating(S); ri = S['orchestra_m'] / 2
    objs = []

    # ---- the outer wall's arcades, the corridor, the second ring, dark behind; the walls closing the ends
    bm = bmesh.new(); zs = []; z = z0
    av_w, av_p = S['archivolt_m']; im_h, im_p = S['impost_m']; cw = S['corridor_m'] / 2
    av = [(0, 0), (0, av_p * .6), (av_w * .35, av_p * .6), (av_w * .35, av_p), (av_w, av_p), (av_w, 0)]
    for st in S['storeys']:
        zs.append(z); spring = st['spring'] + st['pedestal']; aw_ = st['arch'] * bw; r = aw_ / 2
        for i in range(N):
            M = kit.bay_frame(ov, s0 + (i + .5) * bw)
            kit.arch_panel(bm, bw, st['h'], T, aw_, spring, z0=z, xf=M)
            kit.arch_band(bm, r, z + spring, av, xf=M)
            for sx in (-1, 1):
                kit.box(bm, min(sx * r, sx * bw / 2), max(sx * r, sx * bw / 2), 0, im_p, z + spring - im_h, z + spring, xf=M)
            Mi = kit.bay_frame(ov, s0 + (i + .5) * bw, d_in)
            kit.arch_panel(bm, (t1 - t0) * (R - d_in) / N, st['h'], S['inner_wall_m'], aw_ * .9, spring, z0=z, xf=Mi)
        zv = z + st['h'] - .6 - cw   # (the corridor's barrel vault, its crown under the floor above)
        arc_sweep(bm, ov, [(-(T + cw) + cw * math.cos(math.pi * k / 10), zv + cw * math.sin(math.pi * k / 10)) for k in range(11)], s0, s1, n4)
        z += st['h']
    attic0 = z
    for zf in [z0] + zs[1:] + [attic0]:   # floors between the rings (a little under the walls' tops: no two faces in one plane)
        arc_sweep(bm, ov, [(0.0, zf - (.02 if zf > z0 else 0)), (-d_dark, zf - (.02 if zf > z0 else 0))], s0, s1, n4)
    zd = z_at(pts, R - d_dark) - .5
    arc_sweep(bm, ov, [(0, z0), (0, zd)], s0, s1, n4, mat=1, d0=d_dark)
    end = [(R + 1.0, 0.0), (R + 1.0, h), (R - T, h)] + pts
    for t, away in ((t0, (math.sin(t0), -math.cos(t0))), (t1, (-math.sin(t1), math.cos(t1)))):
        section_slab(bm, end, t, away, .4)
    objs.append(kit.obj('facade_arcades', bm, mats))

    # ---- the orders
    bm = bmesh.new(); rc = S['column_r']; ent = S['entablature']; eh = sum(x for _, x in ent)
    for k, st in enumerate(S['storeys']):
        zb, zt = zs[k], zs[k] + st['h']; ped = st['pedestal']
        if ped:   # the pedestal course the columns stand on, a parapet across each arch
            arc_sweep(bm, ov, [(0, zb), (.55, zb), (.55, zb + .15), (.62, zb + .22), (.55, zb + .3), (.55, zb + ped - .2), (.66, zb + ped - .1), (.66, zb + ped), (0, zb + ped)], s0, s1, n4)
        for i in range(1, N):
            kit.column(bm, st['order'], rc, zb + ped, zt - eh, kit.bay_frame(ov, s0 + i * bw))
        if ped:
            aw_ = st['arch'] * bw
            for i in range(N):
                Mc = kit.bay_frame(ov, s0 + (i + .5) * bw)
                kit.box(bm, -aw_ / 2, aw_ / 2, -.35, 0, zb, zb + ped, xf=Mc)
                kit.box(bm, -aw_ / 2, aw_ / 2, -.42, .06, zb + ped, zb + ped + .12, xf=Mc)
        arc_sweep(bm, ov, kit.entablature(ent, zt - eh), s0, s1, n4)
    arc_sweep(bm, ov, [(1.0, 0), (1.0, z0 / 2), (.5, z0 / 2), (.5, z0), (0, z0)], s0, s1, n4)   # the steps round the foot
    objs.append(kit.obj('orders', bm, mats))

    # ---- the attic
    bm = bmesh.new(); wtop = h - .9; ph = .3; wx, wsill, whead = S['window_m']
    arc_sweep(bm, ov, [(0, wtop), (.25, wtop), (.25, wtop + .12), (.45, wtop + .2), (.6, wtop + .35), (.6, h - .35), (.75, h - .3), (.9, h - .2), (.9, h), (-T, h), (-T, wtop)], s0, s1, n4)
    arc_sweep(bm, ov, [(0, attic0), (.35, attic0), (.35, attic0 + .25), (.2, attic0 + .4), (0, attic0 + .4)], s0, s1, n4)
    for i in range(N):
        Mc = kit.bay_frame(ov, s0 + (i + .5) * bw)
        if i % 2 == 0:   # a window through the wall, dark behind
            kit.rect_panel(bm, bw, wtop - attic0, T, wx, wsill, whead, z0=attic0, xf=Mc, reveal=1)
            kit.box(bm, -wx / 2 - .35, wx / 2 + .35, -T - .12, -T - .04, attic0 + wsill - .1, attic0 + whead + .1, mat=1, xf=Mc)
        else:
            kit.rect_panel(bm, bw, wtop - attic0, T, z0=attic0, xf=Mc)
    for i in range(1, N):   # the pilasters: base, shaft, capital
        M = kit.bay_frame(ov, s0 + i * bw)
        kit.box(bm, -.62, .62, -.05, ph + .1, attic0 + .4, attic0 + .75, xf=M)
        kit.box(bm, -.5, .5, -.05, ph, attic0 + .75, h - 1.6, xf=M)
        kit.box(bm, -.57, .57, -.05, ph + .05, h - 1.6, h - 1.45, xf=M)
        kit.box(bm, -.66, .66, -.05, ph + .12, h - 1.45, h - 1.2, xf=M)
    objs.append(kit.obj('attic', bm, mats))

    # ---- the seating
    bm = bmesh.new()
    arc_sweep(bm, ov, [(r - R, z) for r, z in pts], s0, s1, S['seat_steps'])
    for ra, za, n, run, rise, dv in bands:   # the stairs: a half step on each row's tread, by the row above
        for k in range(1, dv):
            sk = s0 + (s1 - s0) * k / dv
            for i in range(n):
                M = kit.bay_frame(ov, sk, R - (ra - i * run)); zt = za - (i + 1) * rise
                kit.box(bm, -.6, .6, -run / 2, 0, zt, zt + rise / 2, xf=M)
    for rw, za, zb, dv in walls:   # the openings in the walls between bands, in the wedges of the band below
        for k in range(dv):
            M = kit.bay_frame(ov, s0 + (s1 - s0) * (k + .5) / dv, R - rw)
            kit.box(bm, -.8, .8, -.04, 0, za + .05, min(zb - .25, za + 2.0), mat=1, xf=M)
    objs.append(kit.obj('cavea', bm, mats))

    # ---- the orchestra, out to the stage's front
    st = S['stage']; yf = -1.0; D = st['d_m']; H = st.get('h_m') or h
    bm = bmesh.new()
    arc = [(ri * math.cos(t0 + (t1 - t0) * i / 48), ri * math.sin(t0 + (t1 - t0) * i / 48)) for i in range(49)]
    po.prism_plan(bm, arc + [(arc[-1][0], yf), (arc[0][0], yf)], 0.0, .05)
    objs.append(kit.obj('orchestra', bm, mats))

    objs += stage(S, R, yf, D, H, mats)
    if S.get('temple'): objs.append(temple(S, R, h, pts, mats))
    return objs


def stage(S, R, yf, D, H, mats):
    """the stage building: its block and wings, the stage, its roof, the frons wall with its doors and columns"""
    P, F = S['stage_parts'], S['frons']; W = 2 * R * (1.0 if S['sweep_deg'] <= 180 else .8); hw = W / 2
    yb = yf - D; yw = yb + P['scaena_m']; tf = P['frons_wall_m']; vw = P['versura_m']; xi = hw - vw; zp = P['pulpitum_m']
    out = []
    # the block behind the frons wall and the wings at both ends, as one plan
    bm = bmesh.new()
    U = [(-hw, yb), (hw, yb), (hw, yf), (xi, yf), (xi, yw - tf), (-xi, yw - tf), (-xi, yf), (-hw, yf)]
    po.prism_plan(bm, U, 0.0, H)
    run = [(-xi, yf), (-hw, yf), (-hw, yb), (hw, yb), (hw, yf), (xi, yf)]   # (the outer faces, counter-clockwise: out to the right)
    po.ring(bm, run, [(0, 0), (.25, 0), (.25, .5), (.18, .62), (.18, .9), (.1, 1.0), (0, 1.05)], closed=False)   # the plinth
    for zs in P['strings']:
        po.ring(bm, run, [(0, zs - .35), (.12, zs - .35), (.12, zs - .1), (.28, zs), (.28, zs + .12), (0, zs + .12)], closed=False)
    po.ring(bm, run, kit.entablature([[.12, .4], [.08, .35], [.75, .45]], H - 1.2), closed=False)   # the crowning cornice
    z1 = P['strings'][0] + .12 if P['strings'] else 1.05; n = max(1, round(W / P['pilaster_m']))
    for i in range(1, n):   # pilasters on the back face, between the string courses
        x = -hw + W * i / n
        kit.box(bm, x - .45, x + .45, yb - .25, yb + .05, z1, H - 1.2)
    for sx in (-1, 1):   # the wings' doors onto the stage
        x = sx * xi; y0, y1 = yw + 1.5, yf - 2.0
        kit.box(bm, min(x, x - sx * .04), max(x, x - sx * .04), y0, y1, zp, zp + 6.0, mat=1)
        kit.box(bm, min(x, x - sx * .25), max(x, x - sx * .25), y0 - .35, y0, zp, zp + 6.35)
        kit.box(bm, min(x, x - sx * .25), max(x, x - sx * .25), y1, y1 + .35, zp, zp + 6.35)
        kit.box(bm, min(x, x - sx * .25), max(x, x - sx * .25), y0 - .35, y1 + .35, zp + 6.0, zp + 6.35)
    # the stage: its floor and moulded front; the roof over it, falling toward the cavea
    e = .2
    kit.box(bm, -xi, xi, yw, yf, 0.0, zp)   # (between the wings exactly: run into them, its front lay in the plane of theirs)
    po.extrude(bm, [(0, zp - .25), (.12, zp - .25), (.12, zp - .12), (.22, zp - .05), (.22, zp + .04), (0, zp + .04)], (-xi, yf, 0), (xi, yf, 0))
    po.extrude(bm, [(0, 0), (.25, 0), (.25, .3), (.12, .4), (0, .4)], (-xi, yf, 0), (xi, yf, 0))
    rz, fall = P['roof_m']
    po.roof_lean(bm, Matrix.Identity(4), -xi, xi, yf, yw - .3, rz, H - fall - rz, H - .15, .66, (.12, .1), cover=2)
    out.append(kit.obj('stage', bm, mats))

    # the frons: its wall and doors, the columns on their podium and pedestals, the entablatures
    bm = bmesh.new(); Mf = po.frame(0, yw)   # (x along it, y out of its face toward the cavea)
    doors = [(x - w / 2, x + w / 2, zp, zp + dh) for x, w, dh in F['doors']]
    po.wall_openings(bm, -xi - e, xi + e, tf, zp, H, doors, reveal=1, xf=Mf)
    for xa, xb, za, zb in doors:
        po._faces(bm, [[bm.verts.new(Mf @ Vector(v)) for v in ((xa - .3, -tf + .3, za), (xb + .3, -tf + .3, za), (xb + .3, -tf + .3, zb + .3), (xa - .3, -tf + .3, zb + .3))]], 1)   # (dark beyond)
        po.door_frame(bm, xa, xb, za, zb, w=.5, p=.12, cornice=(.5, .4), xf=Mf)
    out_ = F['out_m']; z = zp; spans = sorted((xa - .9, xb + .9) for xa, xb, _, _ in doors)
    xs = [x for x in (-xi + F['bay_m'] / 2 + k * F['bay_m'] for k in range(int(2 * xi / F['bay_m']) + 1)) if abs(x) < xi - .5]
    seg = S['column_seg']
    for k, fs in enumerate(F['storeys']):
        r = fs['r']; rt = r * .9; pod = fs['podium']; deep = out_ + r * 1.3 + .3
        cols = [x for x in xs if all(not (a - r * 1.3 < x < b + r * 1.3) for a, b in spans)] if k == 0 else xs
        if k == 0:   # the podium on the stage, broken at the doors
            edges = [-xi - e] + [v for a, b in spans for v in (a, b)] + [xi + e]
            for a, b in zip(edges[::2], edges[1::2]):
                if b - a < .5: continue
                kit.box(bm, a, b, 0, deep, z, z + pod, xf=Mf)
                po.extrude(bm, [(0, z), (deep + .15, z), (deep + .15, z + .25), (deep + .05, z + .35), (0, z + .35)], (a, 0, 0), (b, 0, 0), xf=Mf)
                po.extrude(bm, [(0, z + pod - .3), (deep + .05, z + pod - .3), (deep + .2, z + pod - .1), (deep + .2, z + pod), (0, z + pod)], (a, 0, 0), (b, 0, 0), xf=Mf)
        else:   # a pedestal course on the entablature below
            po.extrude(bm, [(0, z), (deep, z), (deep, z + pod - .15), (deep + .12, z + pod - .05), (deep + .12, z + pod), (0, z + pod)], (-xi - e, 0, 0), (xi + e, 0, 0), xf=Mf)
        zc = z + pod; zt = zc + fs['h']
        for x in cols:
            po.column_free(bm, fs['order'], r, zc, zt, Mf @ Matrix.Translation((x, out_, 0)), taper=.9, seg=seg)
        eh = fs['ent']; pa = .1; off = out_ + rt - pa * .6
        prof = [(p + off, zz) for p, zz in kit.entablature([[pa, eh * .4], [.08, eh * .3], [.55, eh * .3]], zt)]
        po.extrude(bm, [(0, zt)] + prof + [(0, zt + eh)], (-xi - e, 0, 0), (xi + e, 0, 0), xf=Mf)
        z = zt + eh
    out.append(kit.obj('scaenae_frons', bm, mats))
    return out


def temple(S, R, h, pts, mats):
    """a small prostyle temple on the axis at the top of the seating, facing the stage over it: its floor the outer wall's top,
    reached from the seats by a flight of steps; its back carried outside the curved wall on a projection that continues the
    facade's storeys (the steps at its foot, the pedestal course, the entablatures, the attic's plinth and cornice, pilasters)"""
    Tp = S['temple']; w, d = Tp['w_m'], Tp['d_m']; hw = w / 2; zf = h
    yfront = pts[1][0] - Tp['into_m']   # (its front: into the top rows of seats)
    yback = yfront + d
    bm = bmesh.new()
    yin = math.sqrt(max(0.0, R * R - hw * hw)) - .5   # (inside the curved wall's face at its sides)
    if yback > yin + .5:
        po.prism_plan(bm, [(-hw, yin), (hw, yin), (hw, yback), (-hw, yback)], 0.0, zf)
        run = [(hw, yin + .3), (hw, yback), (-hw, yback), (-hw, yin + .3)]
        z0 = S['base_m']; ent = S['entablature']; eh = sum(x for _, x in ent)
        po.ring(bm, run, [(1.0, 0), (1.0, z0 / 2), (.5, z0 / 2), (.5, z0), (0, z0)], closed=False)
        zz = z0
        piers = [(hw - .45, hw + .3, yback - .45, yback + .3), (-hw - .3, -hw + .45, yback - .45, yback + .3), (-.45, .45, yback - .1, yback + .3)]   # (pilasters: the two back corners, the back's middle)
        for st in S['storeys']:
            ped = st['pedestal']
            if ped: po.ring(bm, run, [(0, zz), (.55, zz), (.55, zz + .15), (.62, zz + .22), (.55, zz + .3), (.55, zz + ped - .2), (.66, zz + ped - .1), (.66, zz + ped), (0, zz + ped)], closed=False)
            for x0_, x1_, y0_, y1_ in piers:
                kit.box(bm, x0_, x1_, y0_, y1_, zz + ped, zz + st['h'] - eh)
            zz += st['h']; po.ring(bm, run, kit.entablature(ent, zz - eh), closed=False)
        po.ring(bm, run, [(0, zz), (.35, zz), (.35, zz + .25), (.2, zz + .4), (0, zz + .4)], closed=False)
        wtop = zf - .9
        po.ring(bm, run, [(0, wtop), (.25, wtop), (.25, wtop + .12), (.45, wtop + .2), (.6, wtop + .35), (.6, zf - .35), (.75, zf - .3), (.9, zf - .2), (.9, zf), (0, zf)], closed=False)
    # the floor reaching over the top walk and the top rows, the steps up to it from the seats (as many as reach them)
    po.prism_plan(bm, [(-hw, yfront), (hw, yfront), (hw, yin + .1), (-hw, yin + .1)], zf - 3.0, zf)
    run_, n = .38, 1
    for _ in range(4):
        n = max(1, math.ceil((zf - z_at(pts, yfront - n * run_)) / .3))
    zb = z_at(pts, yfront - n * run_); rise = (zf - zb) / n; yb0 = yfront - n * run_
    prof = [(yfront, zb - 1.5), (yb0, zb - 1.5)]
    for k in range(n): prof += [(yb0 + k * run_, zb + (k + 1) * rise), (yb0 + (k + 1) * run_, zb + (k + 1) * rise)]
    po.extrude(bm, prof, (-hw + .4, 0, 0), (hw - .4, 0, 0))
    # the temple: a step, the front columns, the cella with its door, the entablature round it, the roof and pediments
    st0 = zf + .3
    kit.box(bm, -hw, hw, yfront, yback, zf, st0)
    rc = Tp['col_r']; rt = rc * .9; nc = Tp['columns']; yc = yfront + .3 + rc * 1.3 + .1; zt = st0 + Tp['col_h']
    for i in range(nc):
        x = -(hw - .3 - rc * 1.3 - .1) + (2 * (hw - .3 - rc * 1.3 - .1)) * i / (nc - 1)
        po.column_free(bm, Tp['order'], rc, st0, zt, po.frame(x, yc), seg=S['column_seg'])
    yd = yc + Tp['pronaos_m']; wt = .9
    po.prism_plan(bm, [(-hw + .3, yd), (-hw + .3 + wt, yd), (-hw + .3 + wt, yback - .3 - wt), (hw - .3 - wt, yback - .3 - wt), (hw - .3 - wt, yd), (hw - .3, yd), (hw - .3, yback - .3), (-hw + .3, yback - .3)], st0, zt)
    Md = po.frame(0, yd) @ Matrix.Rotation(math.pi, 4, 'Z')   # (the cella's front wall, its face toward the stage)
    dw, dh = 2.6, 5.2
    po.wall_openings(bm, -(hw - .3 - wt), hw - .3 - wt, wt, st0, zt, [(-dw / 2, dw / 2, st0, st0 + dh)], reveal=1, xf=Md)
    po._faces(bm, [[bm.verts.new(Md @ Vector(v)) for v in ((-dw, -wt - .6, st0), (dw, -wt - .6, st0), (dw, -wt - .6, st0 + dh + .5), (-dw, -wt - .6, st0 + dh + .5))]], 1)
    po.door_frame(bm, -dw / 2, dw / 2, st0, st0 + dh, w=.3, p=.08, cornice=(.3, .2), xf=Md)
    eh = Tp['ent_m']; ye = yc - rt
    po.prism_plan(bm, [(-hw + .3, ye), (hw - .3, ye), (hw - .3, yback - .3), (-hw + .3, yback - .3)], zt, zt + eh)
    ent = kit.entablature([[.1, eh * .4], [.06, eh * .3], [.5, eh * .3]], zt)
    po.ring(bm, [(-hw + .3, ye), (hw - .3, ye), (hw - .3, yback - .3), (-hw + .3, yback - .3)], ent)
    zc = zt + eh; o = .3; half = hw - .3 + o; ridge = zc + (hw - .3) * math.tan(math.radians(Tp['pitch_deg']))
    Mr = po.frame(0, 0, math.pi / 2); x0, x1 = ye - .2, yback - .3 + .2
    po.roof_gable(bm, Mr, x0, x1, half, zc, .12, ridge, cover=2)
    zr = ridge - .14 * .8
    for x, sx in ((x0, -1), (x1, 1)):
        for s in (-1, 1):
            p0, p1 = Vector((x, s * half, zc + .12)), Vector((x, 0, zr)); up = Vector((0, s * (zr - zc - .12), half)).normalized()
            po.extrude(bm, [(-.15, -.45), (.1, -.45), (.1, -.3), (.25, -.15), (.3, -.08), (.3, .06), (-.15, .06)], p0, p1, out=(sx, 0, 0), up=up, xf=Mr)
    return kit.obj('temple', bm, mats)

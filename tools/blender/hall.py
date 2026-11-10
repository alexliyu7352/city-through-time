"""A Roman hall standing among porticoes (a curia, a basilica's or a temple's hall set in a colonnaded court) as a detailed model,
drawn from a `parts` landmark as the film's generator lays it out: the hall is a tall prism of walls (its plan: the walls, open
where its front is), an `arches` part across its front (the doorway) and a `long_hall` on the walls (the block under the roof,
and the roof); every other part is a portico's (portico.py: columns, their entablature and roofs, back walls, the floor).
Parts (objects): the portico's (floor, columns, entablature, walls, roofs), and
  hall_walls   the hall's walls as the film has them, a moulded plinth round their foot (broken at the door)
  hall_front   its front wall: the doorway the landmark gives, with a moulded frame and a cornice over it, and the windows above it
               (a DEFAULT, an estimate: the senate house type, the Curia Julia, has three tall windows over its door; the
               landmark gives the door alone), their reveals dark and a dark wall behind them inside (an empty hall seen in shade)
  hall_roof    the block on the walls as an entablature round the hall (architrave band, frieze, cornice), the gabled roof as the
               film has it (pitch, overhang, ridge height), tiled, its gables as pediments with raking cornices
Sizes from the landmark: the hall's footprint, its walls' plan and height, the door, the block's height, the roof's form, pitch
and overhang. Estimates (DEFAULT): the windows, the mouldings' profiles, the tiles."""
import math

import bmesh
from mathutils import Matrix, Vector

import kit
import portico as po

DEFAULT = {**po.DEFAULT,
    'windows': 3,                     # windows over the door in the front wall (0: none)
    'window_m': [2.4, 8.2, 12.0],     # a window's width, its sill and head over the floor
    'window_gap_m': 7.0,              # from one window's middle to the next
    'plinth': [[0, 0], [.18, 0], [.18, .2], [.12, .32], [.12, .62], [.06, .7], [0, .75]],   # the plinth round the walls' foot (out, up)
    'crown': [[.12, .45], [.08, .45], [.7, .55]],   # the entablature round the hall's top: architrave band, frieze, cornice [projection, height]
    'raking_m': [.35, .5],            # the pediments' raking cornice: how far it stands out of the gable, its depth
    'dark_in_m': 1.0,                 # the dark wall inside, this far behind the front wall
}


def find_hall(parts):
    """the hall's parts by what they are: the long_hall on a tall prism (its roof), that prism (its walls), an arches part on the
    same footing inside the roof's rectangle (its front) -> (roof, walls, front) indices"""
    for i, q in enumerate(parts):
        if q['kind'] != 'long_hall' or q.get('atop') is None: continue
        w = parts[q['atop']]
        if w['kind'] != 'prism' or 'plan_m' not in w or w['h_m'] <= .5: continue
        px, py = q.get('at') or [0.0, 0.0]; th = math.radians(q.get('theta_deg') or 0)
        for j, a in enumerate(parts):
            if a['kind'] != 'arches' or a.get('atop') != w.get('atop'): continue
            lx, ly = po.to_local(px, py, th, *(a.get('at') or [0.0, 0.0]))
            if abs(lx) <= q['w_m'] / 2 + .1 and abs(ly) <= q['d_m'] / 2 + .1: return i, q['atop'], j
    raise SystemExit('hall: no hall among the parts (a long_hall on a tall prism of walls, an arches part across its front)')


def build(s):
    S = {**DEFAULT, **(s or {})}; parts = S['parts']
    ir, iw, ia = find_hall(parts); foot, top = po.levels(parts)
    objs = po.build_parts(S, skip={ir, iw, ia})
    stone, dark = kit.stone(), kit.dark(); mats = [stone, dark, kit.roof()]   # (material 2: the roof's covering)
    R, W, A = parts[ir], parts[iw], parts[ia]
    px, py = R.get('at') or [0.0, 0.0]; th = math.radians(R.get('theta_deg') or 0); Ml = po.frame(px, py, th)
    w, d = R['w_m'], R['d_m']; z0, zw = foot[iw], top[iw]; zc = zw + R['h_m']
    ax, ay = po.to_local(px, py, th, *(A.get('at') or [0.0, 0.0])); sfr = -1 if ay < 0 else 1   # (the front: the side its doorway is on)
    Mh = Ml @ (Matrix.Identity(4) if sfr < 0 else Matrix.Rotation(math.pi, 4, 'Z'))   # (the hall's frame: its front toward -y)
    if sfr > 0: ax, ay = -ax, -ay

    # ---- the walls as the film has them, the plinth round their foot
    bm = bmesh.new()
    for x, y, t in po.instances(W):
        po.prism_plan(bm, [po.to_whole(x, y, t, *p) for p in W['plan_m']], z0, zw)
    dep, Lm = A['depth_m'], A['length_m']; n = A.get('bays') or 1; bay = Lm / n; span = bay * A['opening']; vs = A['h_m'] / (A.get('tiers') or 1) * A['spring']
    doors = [(ax - Lm / 2 + (k + .5) * bay - span / 2, ax - Lm / 2 + (k + .5) * bay + span / 2) for k in range(n)]
    fw = min(.5, max(.2, (bay - span) / 4))   # (the door frame's width)
    yf = ay - dep / 2   # (the front wall's face)
    pl = [tuple(p) for p in S['plinth']]; lo = [(o, z0 + z) for o, z in pl]
    run = [(doors[-1][1] + fw, yf), (w / 2, yf), (w / 2, d / 2), (-w / 2, d / 2), (-w / 2, yf), (doors[0][0] - fw, yf)]
    po.ring(bm, run, lo, closed=False, xf=Mh)
    for (xa, xb), (xc, xd) in zip(doors, doors[1:]):   # (between two doors)
        po.ring(bm, [(xb + fw, yf), (xc - fw, yf)], lo, closed=False, xf=Mh)
    objs.append(kit.obj('hall_walls', bm, mats))

    # ---- the front: the doorway, the windows over it, a dark wall inside
    bm = bmesh.new(); Mf = Mh @ Matrix.Translation((0, yf, 0)) @ Matrix.Rotation(math.pi, 4, 'Z')   # (its face at y = 0, y out of it: toward the garden)
    holes = [(-xb, -xa, z0, z0 + vs) for xa, xb in doors]
    ww, ws, wh = S['window_m']; nw = S['windows']
    wins = [(-(k - (nw - 1) / 2) * S['window_gap_m'] - ww / 2, -(k - (nw - 1) / 2) * S['window_gap_m'] + ww / 2, z0 + ws, z0 + wh) for k in range(nw)]
    Mi = Mh.inverted(); xs = sorted(v.x for v in (Mi @ Vector((*po.to_whole(x, y, t, *p), 0)) for x, y, t in po.instances(W) for p in W['plan_m']) if abs(v.y - yf) < .05)
    x1, x2 = (xs[1], xs[2]) if len(xs) == 4 else (ax - Lm / 2, ax + Lm / 2)   # (the walls' opening at the front: the front wall fills it, its ends in the planes of the side walls' ends flickered)
    po.wall_openings(bm, -x2, -x1, dep, z0, zw, holes + wins, reveal=1, xf=Mf)
    for xa, xb, za, zb in holes:
        po.door_frame(bm, xa, xb, za, zb, w=fw, p=.1, cornice=(.45, .35), xf=Mf)
    for xa, xb, za, zb in wins:
        po.door_frame(bm, xa, xb, za, zb, w=.3, p=.08, cornice=None, xf=Mf)
        kit.box(bm, xa - .4, xb + .4, 0, .2, za - .25, za, xf=Mf)   # (its sill)
    di = S['dark_in_m']; xi = w / 2 - dep - .05
    po._faces(bm, [[bm.verts.new(Mf @ Vector(v)) for v in ((-xi, -dep - di, z0), (xi, -dep - di, z0), (xi, -dep - di, zw), (-xi, -dep - di, zw))]], 1)
    objs.append(kit.obj('hall_front', bm, mats))

    # ---- the block on the walls (an entablature round the hall), the roof, the pediments
    bm = bmesh.new()
    po.prism_plan(bm, [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)], zw, zc, xf=Ml)
    ch = sum(h for _, h in S['crown']); ent = kit.entablature(S['crown'], zc - ch)
    po.ring(bm, [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)], ent, xf=Ml)
    Ro = R.get('roof') or {}; o = Ro.get('overhang_m', .3) if Ro.get('overhang_m') is not None else .3
    pitch = math.radians(Ro.get('pitch_deg') or 15.0); ridge = zc + w / 2 * math.tan(pitch); e = S['eave_m']
    Mr = Ml @ po.frame(0, 0, math.pi / 2)   # (the ridge along the hall's depth, its y)
    x0, x1, half = -d / 2 - .6 * o, d / 2 + .6 * o, w / 2 + o
    po.roof_gable(bm, Mr, x0, x1, half, zc, e, ridge, S['tile_m'], S['tile_r'], cover=2)
    zr = ridge - .14 * .8; ro_, rd = S['raking_m']
    for x, sx in ((x0, -1), (x1, 1)):   # the raking cornices up both gables
        for s in (-1, 1):
            p0, p1 = Vector((x, s * half, zc + e)), Vector((x, 0, zr)); up = Vector((0, s * (zr - zc - e), half)).normalized()
            prof = [(-.15, -rd), (ro_ * .3, -rd), (ro_ * .3, -rd * .7), (ro_ * .8, -rd * .4), (ro_, -rd * .2), (ro_, .06), (-.15, .06)]
            po.extrude(bm, prof, p0, p1, out=(sx, 0, 0), up=up, xf=Mr)
    objs.append(kit.obj('hall_roof', bm, mats))
    return objs


def from_landmark(L):
    if L.get('kind') != 'parts': raise SystemExit(f'hall: a parts landmark, not {L.get("kind")}')
    return {'parts': L['parts']}

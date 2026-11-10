"""A colonnaded forecourt (the atrium before an early Christian basilica: Old St Peter's, San Clemente, the Lateran; a
quadriporticus before a church or a mosque's court) as a detailed model: covered walks round an open court, each a row of
columns on the court's side carrying a beam, a lean-to roof of Roman tiles falling to the court, and on the outer side a wall
with a plinth and a cornice under the roof's edge; the entrance front's wall with its gate; the walks' floors a step above the
paved court. A walk may lean on a building behind it instead of a wall of its own (a basilica's front: its narthex).
The film draws the walks as `arches` parts of a `parts` landmark (each a wall of openings, `length_m` x `depth_m`, `h_m` high);
from_landmark reads the court from them: its outer edge (the walks' outline), which sides have a walk, their depth, height and
bays. Objects:
  walls        the outer walls: plinth, face, cornice; the gate and its frame
  colonnades   the columns (base, shaft, capital) and the beams they carry
  roofs        the walks' roofs: slabs, rows of cover tiles, the capping along their high edge
  floors       the walks' floors and the court's paving
Every size the landmark does not give is an estimate, a default here, and the part it shapes says so on the page."""
import math

import bmesh
from mathutils import Matrix, Vector

import kit
from basilica import ROOF, opening, wall_face, strip, slope_roof, ridge_row, free_column, plinth_prof, cornice_prof, _face

SIDES = ('front', 'right', 'back', 'left')   # (front: the court's -y side, the entrance; back: +y, toward the building it serves)

DEFAULT = {
    'outer_m': [-30.0, 30.0, -30.0, 30.0],   # the court's outer edge: x0, x1, y0, y1 (from_landmark: the walks' outline)
    'walks': list(SIDES),        # the sides with a covered walk
    'walls': None,               # the walks with an outer wall of their own (None: all); one without leans on a building behind
    'extend_m': {},              # {side: metres}: that side's outer edge moved out (to meet the building behind it)
    'h_m': 6.0,                  # the walks' height: the top of their roofs at the outer wall
    'depth_m': 3.5,              # a walk's depth, from the outer face to the court
    'bays': 12,                  # bays of each colonnade (or {side: bays})
    'gate': 'front',             # the side whose wall has the entrance gate (its colonnade gets a bay in front of it)
    'centre_bay': ['back'],      # other sides whose colonnade has a bay at its middle (a door behind it: a basilica's)
    'pitch_deg': 20.0,           # estimate: the walks' roofs, falling to the court
    'overhang_m': .6,            # estimate: the roofs' eaves over the court
    'roof_t_m': .25,
    'wall_m': .8,                # estimate: the outer walls' thickness
    'column_r': .26,             # estimate: a column's radius at its foot
    'beam_m': [.6, .55],         # estimate: the beam on the columns, its width and height
    'step_m': .3,                # estimate: the walks' floors above the court
    'gate_m': [3.6, 4.7],        # estimate: the gate's width and the top of its arch
    'tile_m': .6,                # estimate: the spacing of the rows of cover tiles
    'paved': True,               # the court paved (a slab over it)
}


def from_landmark(L):
    """the court from the film's walks (arches parts, mirrored where repeat says so): its outer edge, its sides, the walks' depth,
    height and bays per side"""
    qs = L['parts'] if L.get('kind') == 'parts' else [{**L, 'at': [0.0, 0.0]}]
    boxes, out = [], {'bays': {}}
    for q in qs:
        if q.get('kind') != 'arches' or not q.get('length_m'): continue
        ax, ay = q.get('at') or (0.0, 0.0); th = float(q.get('theta_deg') or 0); cps = [(ax, ay, th)]
        m = (q.get('repeat') or {}).get('mirror') or ''
        if 'x' in m: cps.append((-ax, ay, -th))
        if 'y' in m: cps.append((ax, -ay, 180 - th))
        for x, y, t in cps:
            along_x = abs(math.cos(math.radians(t))) > .7; hl, hd = float(q['length_m']) / 2, float(q['depth_m']) / 2
            hw, hh = (hl, hd) if along_x else (hd, hl)
            side = ('front' if y < 0 else 'back') if along_x else ('left' if x < 0 else 'right')
            boxes.append((x - hw, x + hw, y - hh, y + hh)); out['bays'][side] = int(q.get('bays') or 12)
            out['h_m'] = max(out.get('h_m', 0.0), float(q['h_m'])); out['depth_m'] = float(q['depth_m'])
            if q.get('arch') and q['arch'] != 'flat': print(f'atrium: {side}: its {q["arch"]} arches drawn as columns under a beam (this kind draws trabeated walks)')
    if not boxes: return {}
    out['outer_m'] = [min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), max(b[3] for b in boxes)]
    out['walks'] = [s for s in SIDES if s in out['bays']]
    return out


def side_geo(side, X0, X1, Y0, Y1):
    """a side's frame: the middle of its outer edge, its outward and along directions, its length, the sides at its two ends
    (v = -L/2, +L/2)"""
    return {'front': (Vector(((X0 + X1) / 2, Y0)), Vector((0, -1)), Vector((1, 0)), X1 - X0, ('left', 'right')),
            'back': (Vector(((X0 + X1) / 2, Y1)), Vector((0, 1)), Vector((1, 0)), X1 - X0, ('left', 'right')),
            'left': (Vector((X0, (Y0 + Y1) / 2)), Vector((-1, 0)), Vector((0, 1)), Y1 - Y0, ('front', 'back')),
            'right': (Vector((X1, (Y0 + Y1) / 2)), Vector((1, 0)), Vector((0, 1)), Y1 - Y0, ('front', 'back'))}[side]


def build(s):
    S = {**DEFAULT, **(s or {})}
    X0, X1, Y0, Y1 = S['outer_m']; ex = S['extend_m'] or {}
    X0 -= ex.get('left', 0); X1 += ex.get('right', 0); Y0 -= ex.get('front', 0); Y1 += ex.get('back', 0)
    walks = [w for w in SIDES if w in S['walks']]; walled = set(walks if S['walls'] is None else S['walls'])
    H, D, tw, tr = S['h_m'], S['depth_m'], S['wall_m'], S['roof_t_m']; tn = math.tan(math.radians(S['pitch_deg'])); o = S['overhang_m']
    w_hi = .15   # (the roofs' high edge: this far beyond the outer face)
    zt = lambda w: H - (w_hi - w) * tn            # a roof's top surface at w (outward from the outer edge, metres; inward negative)
    zu = lambda w: zt(w) - tr                     # its underside
    ax = D - .4                                   # the colonnade's axis, this far in from the outer edge
    rc = S['column_r']; bw_, bh_ = S['beam_m']; st = S['step_m']
    mats = [kit.stone(), kit.dark(), kit.roof()]   # (ROOF: the roofs' covering)
    bw, bc, br, bf = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()
    cols = {}

    for side in walks:
        c, out, along, L, (end0, end1) = side_geo(side, X0, X1, Y0, Y1)
        nb0, nb1 = end0 in walks, end1 in walks
        P = lambda v, w: c + along * v + out * w
        Mr = Matrix(((out.x, along.x, 0, c.x), (out.y, along.y, 0, c.y), (0, 0, 1, 0), (0, 0, 0, 1)))   # (x outward, y along, z up)

        # ---- the roof: its two ends meet the walks beside it in valleys (45 degrees), else stop square at the outer edge
        def ends(w): return (-L / 2 - w if nb0 else -L / 2, L / 2 + w if nb1 else L / 2)
        wl = -(D + o); a0, a1 = ends(wl); b0, b1 = ends(w_hi)
        slope_roof(br, (wl, zt(wl), a0, a1), (w_hi, zt(w_hi), b0, b1), tr, S['tile_m'], M=Mr, high_face=True, cover=ROOF)
        ridge_row(br, Mr, w_hi - .12, zt(w_hi), b0, b1, .14, mat=ROOF)

        # ---- the colonnade: columns from corner to corner on its axis, the beam over them
        va = -L / 2 + ax if nb0 else -L / 2 + .6; vb = L / 2 - ax if nb1 else L / 2 - .6
        bays = S['bays'].get(side, 12) if isinstance(S['bays'], dict) else int(S['bays'])
        bays = bays or max(1, round((vb - va) / 5.0))
        if side == S['gate'] or side in (S['centre_bay'] or []): bays += 1 - bays % 2   # (a bay, not a column, in the middle)
        ztop = zu(-ax + bw_ / 2) - .02   # (the beam's top under the sloping underside, inside the slab where it rises)
        z1 = ztop - bh_
        for i in range(bays + 1):
            p = P(va + (vb - va) * i / bays, -ax); cols[(round(p.x, 3), round(p.y, 3))] = p
        q0, q1 = P(va - rc * 1.6, -ax), P(vb + rc * 1.6, -ax)
        Mb = Matrix(((along.x, out.x, 0, 0), (along.y, out.y, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
        lo, hi = (q0, q1) if (q1 - q0).dot(along) > 0 else (q1, q0)
        vv0, vv1 = lo.dot(along), hi.dot(along); ww = lo.dot(out)
        kit.box(bc, vv0, vv1, ww - bw_ / 2, ww + bw_ / 2, z1, ztop, xf=Mb)                       # the beam
        kit.box(bc, vv0, vv1, ww - bw_ / 2 - .1, ww - bw_ / 2 + .05, ztop - .2, ztop - .02, xf=Mb)  # its moulding toward the court

        # ---- the outer wall: its face, its inner face, its top under the roof; plinth and cornice outside; the gate
        if side in walled:
            u0 = -L / 2; u1 = L / 2
            i0 = -L / 2 + (tw if (nb0 and end0 in walled) else 0); i1 = L / 2 - (tw if (nb1 and end1 in walled) else 0)
            Mo = Matrix(((along.x, out.x, 0, c.x), (along.y, out.y, 0, c.y), (0, 0, 1, 0), (0, 0, 0, 1)))
            ci = c - out * tw
            Mi = Matrix(((along.x, -out.x, 0, ci.x), (along.y, -out.y, 0, ci.y), (0, 0, 1, 0), (0, 0, 0, 1)))
            ops, opi = [], []
            if side == S['gate']:
                gw, gh = S['gate_m']
                ops = [opening(0.0, gw, 0.0, gh, 'round', through=True)]
                opi = [opening(0.0, gw, 0.0, gh, 'round', through=True, reveal=False)]   # (its inner face)
            wall_face(bw, Mo, 0.0, [(u0, zu(0), u1, zu(0))], ops, tw)
            wall_face(bw, Mi, 0.0, [(i0, zu(-tw), i1, zu(-tw))], opi, tw)
            V = lambda v, w, z: bw.verts.new(Vector((*(c + along * v + out * w), z)))
            _face(bw, [V(u0, 0, zu(0)), V(u1, 0, zu(0)), V(i1, -tw, zu(-tw)), V(i0, -tw, zu(-tw))], 0)   # its top
            for v_, vi, nb in ((u0, i0, nb0 and (end0 in walled)), (u1, i1, nb1 and (end1 in walled))):
                if not nb: _face(bw, [V(v_, 0, 0), V(v_, 0, zu(0)), V(vi, -tw, zu(-tw)), V(vi, -tw, 0)], 0)   # an end standing free
            cm = .45; g = .3 * cm / .8   # (the cornice under the roof's edge: its top at the underside, cornice_prof's gap taken up)
            strip(bw, Mo, (u0, zu(0) + g), (u1, zu(0) + g), cornice_prof(cm), 1 if nb0 and end0 in walled else 0, 1 if nb1 and end1 in walled else 0)
            gaps = sorted((q['u'] - q['w'] / 2 - .9, q['u'] + q['w'] / 2 + .9) for q in ops)
            stops = [u0] + [x for g in gaps for x in g] + [u1]
            for k in range(0, len(stops) - 1, 2):
                strip(bw, Mo, (stops[k], 0), (stops[k + 1], 0), plinth_prof(.5), 1 if (k == 0 and nb0 and end0 in walled) else 0,
                      1 if (k + 2 == len(stops) and nb1 and end1 in walled) else 0)
            for q in ops:   # the gate's frame: an arched band, the impost it springs from, a pilaster each side
                a = q['w'] / 2; sp = q['head'] - a
                kit.arch_band(bw, a, sp, [(0, 0), (0, .14), (.42, .14), (.42, 0)], xf=Mo)
                for sx in (-1, 1):
                    kit.box(bw, min(sx * a, sx * (a + .42)), max(sx * a, sx * (a + .42)), 0.0, .16, sp - .3, sp, xf=Mo)
                    kit.box(bw, sx * (a + .9) - .4, sx * (a + .9) + .4, 0.0, .26, .5, zu(0) - cm, xf=Mo)
                    kit.box(bw, sx * (a + .9) - .5, sx * (a + .9) + .5, 0.0, .34, .0, .62, xf=Mo)

    # ---- the columns, once at each corner; the floors and the court
    for p in cols.values(): free_column(bc, p.x, p.y, st, z1, rc)
    ins = {sd: (D + .05 if sd in walks else 0.0) for sd in SIDES}   # (each floor reaches past the colonnade's axis to its step)
    if 'front' in walks: kit.box(bf, X0, X1, Y0, Y0 + ins['front'], 0, st)
    if 'back' in walks: kit.box(bf, X0, X1, Y1 - ins['back'], Y1, 0, st)
    for sd, xa, xb in (('left', X0, X0 + ins['left']), ('right', X1 - ins['right'], X1)):
        if sd in walks: kit.box(bf, xa, xb, Y0 + ins['front'], Y1 - ins['back'], 0, st)
    if S['paved']: kit.box(bf, X0 + ins['left'], X1 - ins['right'], Y0 + ins['front'], Y1 - ins['back'], 0, .1)
    return [kit.obj('walls', bw, mats), kit.obj('colonnades', bc, mats), kit.obj('roofs', br, mats), kit.obj('floors', bf, mats)]

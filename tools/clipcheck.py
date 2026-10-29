"""Clipping check (穿模): geometry that passes through other geometry in the era cities and against today's city.
usage: python -I tools/clipcheck.py cities/<slug> [--max 0]      exit 1 if any check finds more than --max cases

Checks, per era city (data/era_<id>.json, primitives from pipeline/citygen.py):
  houses_vs_walls     ordinary house bodies (part 0) overlapping the city wall, a landmark or the moat
  houses_vs_streets   house bodies standing on a main street or lane (paving, part 7)
  trees_in_houses     a tree trunk inside a house, landmark or earthwork body (at any height: a hall on a podium too), or
                      standing below the top of the platform it is on (a court's on a hillside); a court or an arena is open
  landmarks_overlap   two different landmark bodies overlapping (beyond touching)
  walls_through       a wall (a thin long piece) right across a hall or a house (its whole width), in the same court too;
                      a wall running part way into the gate house it ends at is as built
  streets_short       the end of a street (a road 10 m wide or more) that meets no other road within 20 m and points at a
                      landmark, earthwork or wall 20-150 m ahead without reaching it (an avenue stopping short of the palace
                      it leads to)
  today_vs_era        today's buildings that stay up (outside the era's hide mask) but overlap the era city
  floating            primitives whose base sits above the plate's surface and not on a lot's platform (the plate is sampled
                      like the engine does)
  terrain_cut         bodies the plate rises through: under the footprint the ground climbs more than half the body's height
                      above the ground the body stands on (a long wall or a big hall on a slope)
  cross_era           bodies of a city that overlap bodies of another city standing at the same time (the empire over Qin)
  paving_under        paving (roads, lanes, yards) the plate rises through by more than 0.3 m: a road comes out in dashes
  tall_foundation     houses and halls whose foundation on screen is over 30% of the building's height, counted only when
                      they are more than a tenth of the era's buildings: then the plate's exaggeration is too high for this
                      ground (a slope's fall shows times the exaggeration, the building times its own); the line says the
                      highest exaggeration that would pass. Plinths (citygen PLINTH: a body's base on a slope) are not bodies here.
Checks on today's buildings (data/model.json):
  today floating      buildings whose base stands more than 1 m (times the plate's exaggeration) above the lowest plate point
                      under the footprint: prep.py seats each one on that point, so a count here means the model was prepared
                      on another terrain (terrain.py run again, prep.py not) or seated another way
Footprints are the primitives' rotated rectangles in model units; overlaps under 2 m2 (rounding at shared edges) are ignored.
"""
import json, math, os, sys
import numpy as np
from PIL import Image
import shapely
from shapely.geometry import Polygon
from shapely.strtree import STRtree
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline'))
from citygen import footprint, plan, solid_plan

FAB, LMK, WALL, BRIDGE, TREE, WATER, DARK, PAVE, ROOF, LROOF, EARTH, PLINTH = range(12)
STREET_M, SHORT_M, STREET_W = 150.0, 20.0, 10.0   # how far a road's end looks for what it leads to; a gap under SHORT_M is near enough; roads this wide or wider (metres)
SKIRT = 3.0       # metres every body reaches below grade (citygen Builder.skirt)
FOUND_MAX = .3    # a foundation on screen over this share of its building's height is tall (tall_foundation)


SOLID = (0, 2, 5, 6)   # the record types that are bodies (box, frustum, solid of revolution, prism; not a roof, a trunk, a cone)


def rect(p, shrink=0.0):
    return plan(p, -shrink)   # (citygen.plan: a record's plan as a geometry; shrunk, a plan with a narrow neck may part in two)


def main():
    city = sys.argv[1]; mx = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 0
    D = os.path.join(city, 'build', 'data'); FILM = json.load(open(os.path.join(city, 'build', 'film.json'))); M = json.load(open(os.path.join(D, 'model.json')))   # (pipeline/layout.py)
    S = M['scale']; m2 = (1 / S) ** -2   # model units^2 per m^2
    min_area = 2.0 * m2
    PW, PD = M['size']
    import terrainio
    timg, tj = terrainio.load(city)
    tex = M['terrain'].get('exaggeration', 3) if M.get('terrain') else 3
    plate_ = terrainio.plate_mesh(timg, PW, PD) if timg is not None else None
    def plate_y(x, z):   # the plate as the engine draws it: its mesh (terrainio.plate_mesh), flat between the mesh's corners
        return 0.0 if plate_ is None else plate_(x, z) * S * tex
    # today's buildings as footprints
    today = [Polygon(r[2][0]) for r in M['p'] if len(r[2][0]) >= 3]
    today_ctr = np.array([[p.centroid.x, p.centroid.y] for p in today]) if today else np.zeros((0, 2))
    hide = [np.asarray(Image.open(os.path.join(D, f)).convert('RGBA')) for f in ('hide.png', 'hide2.png') if os.path.exists(os.path.join(D, f))]
    report, total, notes = {}, 0, {}
    fields = None   # the ground's two scales (terrain.py) at model points -> (landforms, fine relief) in metres
    ttrue, _ = terrainio.load(city, true=True)
    if ttrue is not None:
        large_ = terrainio.gauss(ttrue, float((tj.get('detail') or {}).get('below_m', 150.0)) / tj['res_m']); fine_ = ttrue - large_
        def fields(x, z):
            Hh, Ww = ttrue.shape; u = np.clip((x / PW + .5) * (Ww - 1), 0, Ww - 1.001); v = np.clip((z / PD + .5) * (Hh - 1), 0, Hh - 1.001)
            i0, j0 = u.astype(int), v.astype(int); fu, fv = u - i0, v - j0
            bl = lambda a: (a[j0, i0] * (1 - fu) + a[j0, i0 + 1] * fu) * (1 - fv) + (a[j0 + 1, i0] * (1 - fu) + a[j0 + 1, i0 + 1] * fu) * fv
            return bl(large_), bl(fine_)
    bodies_by_era = {}
    for e in FILM.get('eras', []):
        J_ = json.load(open(os.path.join(city, 'build', e['file']))); prims = J_['prims']
        # when each record stands: from its rise to the city's end, or to its loss (lose:): a part lost and what is built where it
        # stood never stand together, so they are not an overlap (within the city: from each record's own rise)
        lost_ = J_.get('lost') or [0] * len(prims); off_ = e.get('off') or 1e9
        span_ = {id(p): (e['on'] + p[10] * e['span'], e['losses'][k - 1]['gone'] if k else off_) for p, k in zip(prims, lost_)}
        both = lambda a, b: span_[id(a)][0] < span_[id(b)][1] and span_[id(b)][0] < span_[id(a)][1]
        ground = [p for p in prims if p[4] <= p[12] + 1e-9 and p[11] != PLINTH]   # primitives that start at (or below) grade, not plinths
        body = lambda parts: [p for p in ground if p[11] in parts and p[0] in SOLID]
        hp_, wp0_, sp_ = body((FAB,)), body((WALL, LMK, EARTH, WATER)), [p for p in body((PAVE,)) if p[5] > 12 * S or p[6] > 12 * S]
        houses = [rect(p, .3 * S) for p in hp_]
        hard = [rect(p, .3 * S) for p in wp0_]
        streets = [rect(p, .5 * S) for p in sp_]
        trunks = [p for p in prims if p[11] == TREE and p[0] == 3]
        lmp_ = body((LMK, EARTH))
        lm = [((p[15], p[16]) if len(p) > 16 else (p[1], p[2]), rect(p, .3 * S), p[11]) for p in lmp_]   # (the building it belongs to, its body, part)
        R = {}
        def overlaps(A, B, label, PA=None, PB=None):   # (PA, PB: the records, when only those standing together count)
            if not A or not B: R[label] = 0; return
            tree = STRtree(B); n = 0; ex = []
            for i, a in enumerate(A):
                for j in tree.query(a, predicate='intersects'):
                    if PA is not None and not both(PA[i], PB[j]): continue
                    if a.intersection(B[j]).area > min_area: n += 1; ex.append([round(a.centroid.x, 4), round(a.centroid.y, 4)]); break
            R[label] = n; R[label + '_at'] = ex[:5]
        overlaps(houses, hard, 'houses_vs_walls', hp_, wp0_)
        overlaps(houses, streets, 'houses_vs_streets', hp_, sp_)
        # a trunk inside a body: the ground it stands on below the body's top (along the body's slope), inside where the body
        # stands (a hall on a podium starts above grade, so every body counts, at any height; a tree on top of a terrace stands
        # at its top and is not inside it; a court or an arena is open: solid_plan). A platform counts too: a tree in a court on
        # a hillside stands on it, and one standing on the slope inside it shows only its crown
        bp = [p for p in prims if p[11] in (FAB, LMK, EARTH, PLINTH) and p[0] in SOLID]
        bodies = [solid_plan(p, -.1 * S) for p in bp]
        top = lambda q, x, z: q[4] + q[7] + q[13] * (x - q[1]) + q[14] * (z - q[2])
        if trunks and bodies:
            tree = STRtree(bodies); n = 0; ex = []
            for p in trunks:
                pt = shapely.Point(p[1], p[2])
                if any(bodies[j].contains(pt) and p[12] < top(bp[j], p[1], p[2]) - .5 * S and both(p, bp[j]) for j in tree.query(pt)): n += 1; ex.append([round(p[1], 4), round(p[2], 4)])
            R['trees_in_houses'] = n; R['trees_in_houses_at'] = ex[:5]
        # bodies of different landmarks (each primitive carries the centre of the building it belongs to: parts of one big
        # court may touch inside it, two buildings may not)
        if lm:
            polys = [q for _, q, _ in lm]; owner = [o for o, _, _ in lm]; part_ = [k for _, _, k in lm]; tree = STRtree(polys); n = 0; ex_lm = []
            for i, q in enumerate(polys):
                for j in tree.query(q, predicate='intersects'):
                    if j <= i or owner[j] == owner[i] or not both(lmp_[i], lmp_[j]): continue
                    if part_[i] == EARTH and part_[j] == EARTH: continue   # rammed-earth tiers of one platform abut by design
                    small, big = (q, polys[j]) if q.area < polys[j].area else (polys[j], q)
                    if small.area < .1 * big.area: continue   # an appendage (a stair, a porch) against a much bigger body
                    if q.intersection(polys[j]).area > min_area * 4:
                        n += 1; c_ = q.intersection(polys[j]).centroid; ex_lm.append([round(c_.x, 4), round(c_.y, 4)])
            R['landmarks_overlap'] = n; R['landmarks_overlap_at'] = ex_lm[:40]
        # a wall through a building: a thin long piece (a court's or a city's wall, citygen strip) across a hall or a house body,
        # in the same court too (parts of one court are let touch in landmarks_overlap, so a wall through its own side hall passed)
        # (across: the wall covers the building's whole width along its line; a wall running into a gate house or a corner hall
        # it ends at goes in part way, as built)
        wp_ = [p for p in body((LMK, WALL)) if min(p[5], p[6]) <= 2.5 * S and max(p[5], p[6]) > 8 * S]
        bp_ = [p for p in body((LMK, FAB)) if min(p[5], p[6]) > 2.5 * S]
        n = 0; ex = []
        if wp_ and bp_:
            br_ = [rect(p, .3 * S) for p in bp_]; btree = STRtree(br_)
            for p in wp_:
                a = rect(p, .3 * S); ang = p[3] + (0 if p[5] >= p[6] else math.pi / 2); ux, uz = math.cos(ang), math.sin(ang)
                span = lambda g: (lambda v: max(v) - min(v))([x * ux + z * uz for x, z in g.exterior.coords]) if not g.is_empty and g.geom_type == 'Polygon' else 0.0
                for j in btree.query(a, predicate='intersects'):
                    if not both(p, bp_[j]): continue
                    q = a.intersection(br_[j])
                    if q.area > min_area and span(q) >= .9 * span(br_[j]): n += 1; c_ = q.centroid; ex.append([round(c_.x, 4), round(c_.y, 4)]); break
        R['walls_through'] = n; R['walls_through_at'] = ex[:10]
        # a street that stops short: one end of a road (paving marked a road, field 8) that meets no other road and points at a
        # landmark, an earthwork or a wall within street_m, without reaching it (an avenue that ends 80 m before the palace it
        # leads to reads as a broken road). Two pieces of one street meet end to end, so an end inside another road piece is a
        # junction, not an end
        roads = [p for p in prims if p[0] == 0 and p[11] == PAVE and len(p) > 8 and p[8] == 1 and p[6] >= STREET_W * S]   # (a lane may stop inside its block)
        if roads:
            rr = [rect(p, -.5 * S) for p in roads]; rtree = STRtree(rr)
            goal = [rect(p) for p in prims if p[0] in SOLID and p[11] in (LMK, EARTH, WALL) and p[7] > 1.5 * S * tex]
            gtree = STRtree(goal) if goal else None; n = 0; ex = []
            for i, p in enumerate(roads):
                c_, s_ = math.cos(p[3]), math.sin(p[3])
                for k in (-1, 1):
                    E = shapely.Point(p[1] + k * p[5] / 2 * c_, p[2] + k * p[5] / 2 * s_)
                    if any(j != i and rr[j].distance(E) < SHORT_M * S for j in rtree.query(E.buffer(SHORT_M * S))): continue   # a junction, the next piece, or a lane stopping at a street
                    if gtree is None: continue
                    ray = shapely.LineString([(E.x + k * c_ * 3 * S, E.y + k * s_ * 3 * S), (E.x + k * c_ * STREET_M * S, E.y + k * s_ * STREET_M * S)])
                    if any(goal[j].contains(E) or goal[j].distance(E) < SHORT_M * S for j in gtree.query(E.buffer(SHORT_M * S))): continue   # it reaches it, or near enough (a lane stopping at the path inside a wall)
                    hits = [goal[j].intersection(ray) for j in gtree.query(ray) if goal[j].intersects(ray)]
                    if hits:
                        dist = min(E.distance(h) for h in hits) / S; n += 1; ex.append([round(E.x, 4), round(E.y, 4), round(dist), round(p[6] / S)])
            R['streets_short'] = n; R['streets_short_at'] = ex[:10]
        # today's buildings that stay up next to (or through) the era city
        if today and e.get('hide') is not None and hide:
            img = np.asarray(Image.open(os.path.join(D, f"hide_{e['id']}.png")).convert('L')) if e.get('occupy') else hide[e['hide'] // 4][..., e['hide'] % 4]; Hh, Ww = img.shape   # (a shared channel: the city's own mask)
            u = np.clip(((today_ctr[:, 0] / PW + .5) * Ww).astype(int), 0, Ww - 1); v = np.clip(((today_ctr[:, 1] / PD + .5) * Hh).astype(int), 0, Hh - 1)
            up = [today[k] for k in np.nonzero(img[v, u] < 5)[0]]
            era_all = [rect(p) for p in ground if p[11] not in (PAVE, WATER, TREE)]
            overlaps(up, era_all, 'today_vs_era')
        # floating: base above the plate by more than 1 m (exaggerated)
        fl = [p for p in ground if p[12] - plate_y(p[1], p[2]) > 1.0 * S * tex and p[4] > plate_y(p[1], p[2]) + 1e-6]
        plat = [q for q in prims if q[11] == PLINTH and q[0] == 0]   # a lot's platform (citygen lot_site): what stands on it is not floating
        if fl and plat:
            prs = [rect(q).buffer(2 * S) for q in plat]; ptree = STRtree(prs)   # (a wall on the lot's edge stands half on it)
            top = lambda q, x, z: q[4] + q[7] + (q[13] if len(q) > 13 else 0) * (x - q[1]) + (q[14] if len(q) > 14 else 0) * (z - q[2])   # (a platform on a sloping lot is sheared)
            fl = [p for p in fl if not any(prs[j].contains(shapely.Point(p[1], p[2])) and top(plat[j], p[1], p[2]) >= p[4] - .5 * S * tex for j in ptree.query(shapely.Point(p[1], p[2])))]
        R['floating'] = len(fl); R['floating_at'] = [[round(p[1], 4), round(p[2], 4)] for p in fl[:5]]
        cut = []
        for p in ground:
            if p[11] in (TREE, WATER, PAVE) or p[0] not in SOLID: continue
            hb = p[4] + p[7] - p[12]                                   # body height above its own ground
            if hb <= 0: continue
            P = rect(p); xs, zs = P.exterior.xy; k_ = len(xs) - 1
            pts = list(zip(xs[:k_], zs[:k_])) + [((xs[i] + xs[i + 1]) / 2, (zs[i] + zs[i + 1]) / 2) for i in range(k_)]
            gx, gz = (p[13], p[14]) if len(p) > 14 else (0.0, 0.0)   # a piece laid along a slope: its ground is a plane
            rise_ = max(plate_y(x, z) - (gx * (x - p[1]) + gz * (z - p[2])) for x, z in pts) - p[12]
            if rise_ > max(.5 * hb, 1.0 * S * tex): cut.append(p)
        R['terrain_cut'] = len(cut); R['terrain_cut_at'] = [[round(p[1], 4), round(p[2], 4)] for p in cut[:5]]
        pu = []
        for p in prims:   # the top of each paving piece (a plane when laid along a slope) against the plate, corners, edge middles, centre
            if p[11] != PAVE or p[0] != 0: continue
            P = rect(p); xs, zs = P.exterior.xy; gx, gz = (p[13], p[14]) if len(p) > 14 else (0.0, 0.0)
            pts = list(zip(xs[:4], zs[:4])) + [((xs[i] + xs[i + 1]) / 2, (zs[i] + zs[i + 1]) / 2) for i in range(4)] + [(p[1], p[2])]
            if max(plate_y(x, z) - (p[4] + p[7] + gx * (x - p[1]) + gz * (z - p[2])) for x, z in pts) > .3 * S * tex: pu.append(p)
        R['paving_under'] = len(pu); R['paving_under_at'] = [[round(p[1], 4), round(p[2], 4)] for p in pu[:5]]
        # tall_foundation: each house or hall body's foundation (below its base, less the skirt every body has) against its
        # building's height (the top of its group); for the suggestion, the same body's fall at another exaggeration from the
        # ground's two scales (terrain.py: landforms x EX, fine relief x1) at its corners, edge middles and centre
        top = {}
        for p in prims: k_ = (p[15], p[16]) if len(p) > 16 else (p[1], p[2]); top[k_] = max(top.get(k_, -1e9), p[4] + p[7])
        fb = [p for p in ground if p[0] == 0 and p[11] in (FAB, LMK) and p[8] != 1 and not (p[13] or p[14]) and min(p[5], p[6]) >= 2 * S]
        fr = np.array([[max(0.0, p[12] - p[4] - SKIRT * S * tex), top[(p[15], p[16]) if len(p) > 16 else (p[1], p[2])] - p[12]] for p in fb]).reshape(-1, 2)
        fr = fr[fr[:, 1] > 0]; ratio = fr[:, 0] / fr[:, 1] if len(fr) else np.zeros(0)
        p90 = float(np.percentile(ratio, 90)) if len(ratio) else 0.0
        R['tall_foundation'] = int((ratio > FOUND_MAX).sum()) if p90 > FOUND_MAX else 0
        sug = None
        if fields is not None and len(fb):
            fb_ = [p for p in fb if (top[(p[15], p[16]) if len(p) > 16 else (p[1], p[2])] - p[12]) > 0]
            pts = np.array([[c for c in zip(*rect(p).exterior.xy)][:4] for p in fb_])   # (n, 4, 2): corners
            pts = np.concatenate([pts, (pts + np.roll(pts, -1, axis=1)) / 2, pts.mean(axis=1, keepdims=True)], axis=1)
            la, fi = fields(pts[..., 0], pts[..., 1])
            fall = lambda ex: (la * ex + fi).max(axis=1) - (la * ex + fi).min(axis=1)
            now = fall(tex) + .1   # (+ 0.1 m: a body the nine points find flat keeps its ratio)
            ok = [ex for ex in np.arange(1.0, 10.01, .5) if np.percentile(ratio * (fall(ex) + .1) / now, 90) <= FOUND_MAX]
            sug = max(ok) if ok else 1.0
        notes[e['id']] = f'foundations: top tenth {p90:.0%} of the height' + (f', within {FOUND_MAX:.0%} up to x{sug:g}' if sug else '')
        xb_ = body((FAB, LMK, WALL, EARTH))
        bodies_by_era[e['id']] = (e, [rect(p, .3 * S) for p in xb_], [span_[id(p)][1] for p in xb_])   # (each body until its city's end or its loss)
        for oid, (oe, ob, oend) in bodies_by_era.items():
            if oid == e['id'] or not ob: continue
            if not (oe['on'] < (e.get('off') or 1e9) and e['on'] < (oe.get('off') or 1e9)): continue
            tree = STRtree(ob); n = 0
            for a, aend in zip(bodies_by_era[e['id']][1], bodies_by_era[e['id']][2]):
                if any(oe['on'] < aend and e['on'] < oend[j] and a.intersection(ob[j]).area > min_area for j in tree.query(a, predicate='intersects')): n += 1
            R['cross_era'] = R.get('cross_era', 0) + n
        report[e['id']] = R
        bad = sum(v for k, v in R.items() if isinstance(v, int))
        total += bad
        print(f"{e['id']:10s} " + '  '.join(f"{k} {v}" for k, v in R.items() if isinstance(v, int)) + f"  ({notes[e['id']]})")
    if plate_ is not None:   # today's buildings on the plate (prep.py seat)
        fl = [r for r in M['p'] if len(r[2][0]) >= 3 and r[3] - plate_.lowest(r[2][0]) * S * tex > 1.0 * S * tex]
        report['today'] = {'floating': len(fl), 'floating_at': [[round(sum(p[0] for p in r[2][0]) / len(r[2][0]), 4), round(sum(p[1] for p in r[2][0]) / len(r[2][0]), 4)] for r in fl[:5]]}
        total += len(fl)
        print(f"{'today':10s} floating {len(fl)}")
    json.dump(report, open(os.path.join(city, 'build', 'logs', 'clipcheck.json'), 'w'), indent=1)
    print('clipcheck:', 'ok' if total <= mx else f'{total} cases (see build/logs/clipcheck.json)')
    sys.exit(0 if total <= mx else 1)


if __name__ == '__main__':
    main()

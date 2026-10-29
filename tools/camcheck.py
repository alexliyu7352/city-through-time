"""Camera check: the camera must never be inside or under anything, and nothing solid may stand between it and what it looks at.
usage: python -I tools/camcheck.py cities/<slug> [--max 0]      (run tools/camcheck.mjs first: it writes build/logs/cam.json)

For every camera sample (out/cam.json, the film's real camera with drift and near plane):
  below_ground  the camera is closer to the plate than 2 near planes
  inside        the camera is inside (or within 1.5 near planes of) a building of today or a period city that stands at that time
  blocked       a solid that stands at that time cuts the sight line between 4 % and 88 % of the way to the target
  spin          two camera keys more than 120 degrees of azimuth apart (the camera whips round)
  offscreen     a period city changes where the viewer cannot see it: while its buildings rise, fewer than 60 % of the
                rising ones are in the frame (or a full-screen clip covers it). Change only on screen (docs/STAGING.md).
  ring_unseen   a node's colour ring starts where the camera does not look (its origin out of frame for its first 1.5 s)
Today's buildings count only where the era hide masks have not stepped them aside (the engine's hideK at the centroid);
period cities only while standing (risen, not yet taken back). Flagged samples are merged into intervals: out/camcheck.json.
"""
import json, math, os, sys
import numpy as np
import shapely
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline'))
from citygen import footprint

FAB, LMK, WALL, BRIDGE, TREE, WATER, DARK, PAVE, ROOF, LROOF, EARTH, PLINTH = range(12)


def ss(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def seg(t, a, b): return 0.0 if b == a else min(1.0, max(0.0, (t - a) / (b - a)))
def sstep(e0, e1, x): return ss((x - e0) / (e1 - e0)) if e1 != e0 else float(x >= e1)


def main():
    city = sys.argv[1]; mx = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 0
    D = os.path.join(city, 'build', 'data'); FILM = json.load(open(os.path.join(city, 'build', 'film.json'))); M = json.load(open(os.path.join(D, 'model.json')))   # (pipeline/layout.py)
    CAM = json.load(open(os.path.join(city, 'build', 'logs', 'cam.json')))['rows']
    S = M['scale']; PW, PD = M['size']
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline'))
    import terrainio
    timg, _ = terrainio.load(city); tex = M['terrain'].get('exaggeration', 3) if M.get('terrain') else 3
    plate_y = lambda x, z: 0.0 if timg is None else terrainio.bilinear(timg, x / PW + .5, z / PD + .5) * S * tex
    # today's buildings: footprint, base, top, hide mask values at the centroid (8 channels)
    tp, tb, tt, tc = [], [], [], []
    for r in M['p']:
        ring = r[2][0]
        if len(ring) < 3: continue
        tp.append(ring); tb.append(r[3] if len(r) > 3 else 0.0); tt.append((r[3] if len(r) > 3 else 0.0) + r[1])
    today = np.array([shapely.Polygon(r) for r in tp]); tb = np.array(tb); tt = np.array(tt)
    ctr = shapely.get_coordinates(shapely.centroid(today))
    hide = [np.asarray(Image.open(os.path.join(D, f)).convert('RGBA')).astype(np.float32) / 255 for f in ('hide.png', 'hide2.png')]
    Hh, Hw = hide[0].shape[:2]
    u = np.clip(((ctr[:, 0] / PW + .5) * Hw).astype(int), 0, Hw - 1); v = np.clip(((ctr[:, 1] / PD + .5) * Hh).astype(int), 0, Hh - 1)
    hm = np.concatenate([hide[0][v, u], hide[1][v, u]], axis=1)          # n x 8
    ttree = shapely.STRtree(today)
    eras = []
    for e in FILM.get('eras', []):
        J_ = json.load(open(os.path.join(city, 'build', e['file']))); lost_ = J_.get('lost') or [0] * len(J_['prims'])
        keep_ = [(p, k) for p, k in zip(J_['prims'], lost_) if p[11] not in (WATER, PAVE)]
        prims = [p for p, _ in keep_]
        own = None   # a city sharing its channel with others apart in time has its own mask (compile era channels)
        if e.get('occupy'): own = np.asarray(Image.open(os.path.join(D, f"hide_{e['id']}.png")).convert('L')).astype(np.float32)[v, u] / 255
        polys, base, top = [], [], []
        start = np.array([e['on'] + p[10] * e['span'] for p in prims]); bc = np.array([[p[15], p[16]] if len(p) > 16 else [p[1], p[2]] for p in prims])
        for p in prims:
            polys.append(footprint(p))
            tilt = max(abs(p[13] * (x - p[1]) + p[14] * (z - p[2])) for x, z in polys[-1]) if len(p) > 14 else 0.0   # a piece laid along a slope rises and falls by this much at its corners
            base.append(p[4] - tilt); top.append(p[4] + p[7] + tilt)
        g = np.array([shapely.Polygon(q) for q in polys])   # (footprints of any number of corners: citygen.footprint)
        eras.append({'e': e, 'g': g, 'tree': shapely.STRtree(g), 'base': np.array(base), 'top': np.array(top), 'start': start, 'bc': bc, 'gy': np.array([p[12] for p in prims]),
                     'lost': np.array([k for _, k in keep_]), 'own': own})

    nodes = FILM.get('nodes', [])
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline'))
    from stagecraft import curve_at   # the same sampled curves the engine reads (compile writes them)
    def fall_state(e, t):   # the taking-back ring, half a sink-time back (a building is half gone there): (radius, centre, contracting) or None
        FR = e.get('fallR')
        if not FR or t - .5 * e.get('fallDur', 1.4) < FR['curve'][0][0]: return None
        return (curve_at(FR['curve'], t - .5 * e.get('fallDur', 1.4)), FR['o'], FR['mode'] == 'in')
    def taken(xz, st):
        R, c, inm = st; d = np.hypot(xz[:, 0] - c[0], xz[:, 1] - c[1]); return d > R if inm else d < R
    def era_standing(E, idx, t):
        e = E['e']; ok = E['start'][idx] + .5 * e['grow'] <= t
        st = fall_state(e, t)
        if st is not None: ok &= ~taken(E['bc'][idx], st)
        for j, q in enumerate(e.get('losses') or [], 1):   # a part lost while the rest stands (compile lose:), with its own ring
            if t - .5 * e.get('fallDur', 1.4) < q['curve'][0][0]: continue
            ok &= ~((E['lost'][idx] == j) & taken(E['bc'][idx], (curve_at(q['curve'], t - .5 * e.get('fallDur', 1.4)), q['o'], q['mode'] == 'in')))
        return ok
    def today_standing(idx, t):
        """the engine's hideK at the building's centroid: stepped aside just before the era building beside it rises, back
        where the era is taken back"""
        k = np.zeros(len(idx), bool)
        for E in eras:
            e = E['e']
            if e.get('hide') is None or t < e['on']: continue
            tn = (t - e['on']) / e['span']; g = e['grow'] / e['span']
            m = (E['own'][idx] if E['own'] is not None else hm[idx, e['hide']]); r = (m - .04) / .96
            hk = (m >= .02) & (tn >= r - .3 * g)
            st = fall_state(e, t)
            if st is not None: hk &= ~taken(ctr[idx], st)
            k |= hk
        return ~k

    # what the camera sees: in front, inside the frame (16:9, vertical fov), not under a full-screen clip
    FULL = [(f['on'] + f['fin'], f['on'] + f['dur'] - f['fout']) for f in FILM.get('footage', []) if (f.get('mode') or 'full') == 'full']
    def in_frame(row, X, Y, Z):
        p_ = np.array(row[1:4]); g_ = np.array(row[4:7]); fov = math.radians(row[9] if len(row) > 9 else 30)
        f_ = g_ - p_; f_ /= np.linalg.norm(f_); r_ = np.cross(f_, [0, 1, 0]); r_ /= np.linalg.norm(r_); u_ = np.cross(r_, f_)
        V = np.stack([X - p_[0], Y - p_[1], Z - p_[2]], 1); z = V @ f_; th = math.tan(fov / 2)
        with np.errstate(divide='ignore', invalid='ignore'):
            ok = (z > 1e-6) & (np.abs((V @ r_) / (z * th * 16 / 9)) <= 1) & (np.abs((V @ u_) / (z * th)) <= 1)
        if any(a <= row[0] <= b for a, b in FULL): ok[:] = False
        return ok
    rows = np.array([r[:10] if len(r) >= 10 else r + [30] for r in CAM])
    T0, DT = rows[0][0], rows[1][0] - rows[0][0]; T1 = rows[-1][0]   # cam.json may cover only a stretch (--from/--to)
    row_at = lambda t: rows[min(len(rows) - 1, max(0, int(round((t - T0) / DT))))]
    offs = []
    for E in eras:   # change only on screen: the buildings rising at each moment must be (mostly) in view
        e = E['e']; t = max(e['on'], T0); _, first = np.unique(E['bc'].round(7), axis=0, return_index=True)
        st0, bc0, gy0 = E['start'][first], E['bc'][first], E['gy'][first]
        while t <= min(e['on'] + e['span'] + e['grow'], T1):
            rising = (st0 <= t) & (t <= st0 + e['grow'])
            row = row_at(t)
            for F_ in e.get('fronts', []):   # a ring that has left the frame speeds up out there (演出文法 9a): what rises beyond the frame is not counted
                if F_['mode'] == 'ring' and F_['curve'][0][0] <= t <= F_['curve'][-1][0] + e['grow']:
                    o = F_['o']; p_ = np.array(row[1:4]); z_ = np.linalg.norm(p_ - np.array([o[0], row[5], o[1]])); vr = z_ * math.tan(math.radians(row[9]) / 2)
                    rising &= np.hypot(bc0[:, 0] - o[0], bc0[:, 1] - o[1]) <= vr
            if rising.sum() >= 3:
                fr = float(in_frame(row, bc0[rising, 0], gy0[rising], bc0[rising, 1]).mean())
                if fr < .6: offs.append((f"offscreen:{e['id']}", t, round(fr, 2)))
            t += .1
    for i, n in enumerate(nodes):   # a node's colour ring must start in view
        rg = n.get('ring')
        if i == 0 or not n.get('tint') or not rg or not (T0 <= rg['t0'] <= T1): continue
        seen = False; t = rg['t0']
        while t <= rg['t0'] + 1.5:
            row = row_at(t)
            if in_frame(row, np.array([rg['o'][0]]), np.array([row[5]]), np.array([rg['o'][1]]))[0]: seen = True; break
            t += .1
        if not seen: offs.append((f"ring_unseen:{n['id']}", rg['t0'], 0.0))

    # spins: camera keys are interpolated value by value, so 0 -> 357 degrees turns the whole way round: write -3
    pd_ = (FILM.get('prologue') or {}).get('dur', 0)   # (the prologue is cut like a trailer, and closes on black)
    spins = [(t0, t1, a[3], b[3]) for (t0, a), (t1, b) in zip(FILM['camera'][:-1], FILM['camera'][1:]) if abs(b[3] - a[3]) > 120 and t1 > pd_ + .6]
    for t0, t1, a0, a1 in spins: print(f'spin                   {t0:7.2f}-{t1:7.2f}s  azimuth {a0} -> {a1}')
    NS = 40; flags = []
    for row in CAM:
        t, px, py, pz, gx, gy, gz, near, d = row[:9]
        mrg = max(near * 1.5, .0002)
        bad = []
        if py - plate_y(px, pz) < max(2 * near, .0003): bad.append(('below_ground', py - plate_y(px, pz)))
        # solids standing at t: today (not stepped aside) and period cities between rise and sink
        sets = []
        sets.append(('today', ttree, today, tb, tt, today_standing))
        for E in eras:
            e = E['e']
            if t >= e['on'] and not (e.get('off') is not None and t > e['off'] + e['sink'] + 5): sets.append((e['id'], E['tree'], E['g'], E['base'], E['top'], lambda idx, t_, E=E: era_standing(E, idx, t_)))
        cam_pt = shapely.Point(px, pz)
        ks = np.linspace(.04, .88, NS)
        seg_pts = shapely.points(np.c_[px + (gx - px) * ks, pz + (gz - pz) * ks]); seg_y = py + (gy - py) * ks
        for name, tree, geoms, base, top, standing in sets:
            # inside: the camera within mrg of a footprint, between its base and top (+ margin)
            hit = tree.query(cam_pt, predicate='dwithin', distance=mrg)
            if len(hit):
                ok = (base[hit] - mrg < py) & (py < top[hit] + mrg)
                if standing is not None and ok.any(): ok[ok] = standing(hit[ok], t)
                if ok.any(): bad.append(('inside', name))
            # blocked: sight-line samples inside a footprint below its top
            pi, gi = tree.query(seg_pts, predicate="intersects")
            if len(pi):
                ok = (seg_y[pi] < top[gi]) & (seg_y[pi] > base[gi] - mrg)
                if standing is not None and ok.any(): ok[ok] = standing(gi[ok], t)
                if ok.any(): bad.append(('blocked', name, round(float(len(set(pi[ok]))) / NS, 2)))
        if bad: flags.append((t, bad))
    # merge into intervals per (kind, what)
    iv = {}
    for key, t, fr in offs:
        L = iv.setdefault(key, [])
        if L and t - L[-1][1] <= .25: L[-1][1] = t; L[-1][2] = min(L[-1][2], fr)
        else: L.append([t, t, fr])
    for t, bad in flags:
        for b in bad:
            key = b[0] + (':' + b[1] if b[0] != 'below_ground' else '')
            val = b[2] if b[0] == 'blocked' else 1.0
            L = iv.setdefault(key, [])
            if L and t - L[-1][1] <= .15: L[-1][1] = t; L[-1][2] = max(L[-1][2], val)
            else: L.append([t, t, val])
    out = {k: [[round(a, 2), round(b, 2), round(w, 2)] for a, b, w in v] for k, v in iv.items()}
    json.dump(out, open(os.path.join(city, 'build', 'logs', 'camcheck.json'), 'w'), indent=1)
    n = 0
    for k, v in sorted(out.items()):
        for a, b, w in v:
            if k.startswith('blocked') and w < .08: continue   # a corner grazing the sight line for a sample or two
            if k.startswith('offscreen') and b - a < .35: continue   # a moment, not a scene
            n += 1; print(f'{k:22s} {a:7.2f}-{b:7.2f}s' + (f'  blocks {w:.0%} of the sight line' if k.startswith('blocked') else f'  {w:.0%} of the rising buildings in view' if k.startswith('offscreen') else ''))
    n += len(spins)
    print('camcheck:', 'ok' if n <= mx else f'{n} intervals (see out/camcheck.json)')
    sys.exit(0 if n <= mx else 1)


if __name__ == '__main__':
    main()

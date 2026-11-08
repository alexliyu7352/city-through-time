"""Camera check: the camera must never be inside or under anything, and nothing solid may stand between it and what it looks at.
usage: python -I tools/camcheck.py cities/<slug> [--max 0] [--cam file] [--out file] [--json file]
  (run tools/camcheck.mjs first: it writes build/logs/cam.json, or its --out, read here with --cam)
  --out   the intervals (default build/logs/camcheck.json)
  --json  each stretch's result on its own: [{from, to, ok, lines, intervals}] (tools/rangecheck.py)

For every camera sample (out/cam.json, the film's real camera with drift and near plane):
  below_ground  the camera is closer to the plate than 2 near planes
  inside        the camera is inside (or within 1.5 near planes of) a building of today or a period city that stands at that time
  blocked       a solid that stands at that time cuts the sight line between 4 % and 88 % of the way to the target
  spin          two camera keys more than 120 degrees of azimuth apart: listed, not counted (compile unwraps the azimuth and stops on
                a turn too fast to follow, its jump check); look that a big turn is meant
  offscreen     a period city changes where the viewer cannot see it: while its buildings rise, fewer than 60 % of the
                rising ones are in the frame (or a full-screen clip covers it). Change only on screen (docs/STAGING.md).
  ring_unseen   a node's colour ring starts where the camera does not look (its origin out of frame for its first 1.5 s)
Today's buildings count at the height the engine gives them at that moment: sunk after the lamp to rise.ghost, taken back by a
reset ring, rising with the year counter (or when the camera first sees them, data/grow_t.json), stepped aside by the era hide
masks (hideK at the centre) and sunk by a living moment (its sink); a water_then stage is not followed (it only takes buildings
away, so the check errs on the side of a flag). Period cities only while standing (risen, not yet taken back). Flagged samples are merged into intervals: out/camcheck.json.
A dump of several stretches (tools/camcheck.mjs --from/--to more than once) is checked stretch by stretch, each as if dumped alone,
and only the period cities that stand or rise in one of them are built (the setup is most of the time a short stretch takes).
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
    city = sys.argv[1]; arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    mx = int(arg('--max', 0)); outf = arg('--out', os.path.join(city, 'build', 'logs', 'camcheck.json')); jsonf = arg('--json')
    D = os.path.join(city, 'build', 'data'); FILM = json.load(open(os.path.join(city, 'build', 'film.json'))); M = json.load(open(os.path.join(D, 'model.json')))   # (pipeline/layout.py)
    CJ = json.load(open(arg('--cam', os.path.join(city, 'build', 'logs', 'cam.json')))); CAM = CJ['rows']
    parts, i = [], 0   # each stretch's rows (a dump before ranges were written: one stretch)
    for _, _, n in CJ.get('ranges') or [[None, None, len(CAM)]]: parts.append(CAM[i:i + n]); i += n
    def meets(a, b): return any(max(a, P[0][0]) <= min(b, P[-1][0]) for P in parts if P)   # (closed: a sample at either end counts)
    S = M['scale']; PW, PD = M['size']
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline'))
    import terrainio
    timg, _ = terrainio.load(city); tex = M['terrain'].get('exaggeration', 3) if M.get('terrain') else 3
    plate_y = lambda x, z: 0.0 if timg is None else terrainio.bilinear(timg, x / PW + .5, z / PD + .5) * S * tex
    # today's buildings: footprint, base, top, hide mask values at the centroid (8 channels)
    tp, tb, tt, tpi = [], [], [], []
    for i, r in enumerate(M['p']):
        ring = r[2][0]
        if len(ring) < 3: continue
        tp.append(ring); tb.append(r[3] if len(r) > 3 else 0.0); tt.append((r[3] if len(r) > 3 else 0.0) + r[1]); tpi.append(i)
    today = np.array([shapely.Polygon(r) for r in tp]); tb = np.array(tb); tt = np.array(tt)
    ctr = np.array([np.mean(r, axis=0)[:2] for r in tp])   # (the engine's aCtr: the mean of the outline's points)
    hide = [np.asarray(Image.open(os.path.join(D, f)).convert('RGBA')).astype(np.float32) / 255 for f in ('hide.png', 'hide2.png', 'hide3.png') if f != 'hide3.png' or os.path.exists(os.path.join(D, f))]   # (hide3: film.eraSlots 12)
    Hh, Hw = hide[0].shape[:2]
    u = np.clip(((ctr[:, 0] / PW + .5) * Hw).astype(int), 0, Hw - 1); v = np.clip(((ctr[:, 1] / PD + .5) * Hh).astype(int), 0, Hh - 1)
    hm = np.concatenate([h_[v, u] for h_ in hide], axis=1)          # n x 8 (or 12)
    ttree = shapely.STRtree(today)
    eras = []
    for e in FILM.get('eras', []):
        own = None   # a city sharing its channel with others apart in time has its own mask (compile era channels)
        if e.get('occupy'): own = np.asarray(Image.open(os.path.join(D, f"hide_{e['id']}.png")).convert('L')).astype(np.float32)[v, u] / 255
        # its solids only where some stretch has it standing (the sets below) or rising (offscreen); today's city steps aside for every one
        if not (meets(e['on'], math.inf if e.get('off') is None else e['off'] + e['sink'] + 5) or meets(e['on'], e['on'] + e['span'] + e['grow'])):
            eras.append({'e': e, 'own': own}); continue
        J_ = json.load(open(os.path.join(city, 'build', e['file']))); lost_ = J_.get('lost') or [0] * len(J_['prims'])
        keep_ = [(p, k) for p, k in zip(J_['prims'], lost_) if p[11] not in (WATER, PAVE)]
        prims = [p for p, _ in keep_]
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
    # today's height (the engine's rise, studio.js RISE): up "today", sunk after the lamp to rise.ghost, a reset ring takes back
    # what came after its year, then each building rises when the counter reaches its year or the camera first sees it
    G, R_, LT = FILM.get('grow') or {}, FILM.get('rise') or {}, FILM['light']; CH = FILM.get('change') or {}
    early = dict(map(tuple, CH.get('early') or [])); renew = {r[0]: r[1:] for r in CH.get('renew') or []}
    gt_ = dict(map(tuple, json.load(open(os.path.join(city, 'build', G['tfile']))))) if G.get('tfile') else {}
    ty = np.array([early.get(i, M['b'][M['p'][i][0]][0]) for i in tpi], float)
    hf0, hfA, hfB = np.array([renew.get(i, (1, 0, 0)) for i in tpi], float).T
    YLg = G.get('yl') or []
    def t_of_year(y):   # (the engine's tOfYear)
        for (t0_, y0_), (t1_, y1_) in zip(YLg, YLg[1:]):
            if y1_ >= y: return t0_ if y0_ >= y else t0_ + (t1_ - t0_) * (y - y0_) / max(y1_ - y0_, 1e-4)
        return 1e6
    ton = np.array([gt_.get(i) or t_of_year(y - .5) for i, y in zip(tpi, ty)]) if len(YLg) > 1 else None
    YLn = FILM.get('yearline') or [[0, 0]]; year_at = lambda t: float(np.interp(t, [a for a, _ in YLn], [b for _, b in YLn]))
    vss = lambda x: (lambda c: c * c * (3 - 2 * c))(np.clip(x, 0, 1))
    reset = next((n for n in nodes if n.get('reset') is not None), None)
    def live_sink(t):   # a living moment sinks today's city by its sink (the engine's liveAt k)
        for L in FILM.get('living') or []:
            a0, o1 = L['on'] - L['arrive'], L['on'] + L['reveal'] + L['hold'] + L['out']
            if a0 <= t <= o1 + L['back']: return (ss(seg(t, a0 + L['arrive'] * .3, L['on'])) if t < L['on'] else 1.0 if t <= o1 else 1 - ss(seg(t, o1, o1 + L['back']))) * L.get('sink', 1)
        return 0.0
    def today_rise(idx, t):
        """how far up each of today's buildings stands at t (0: down): the engine's rise, times hideK at its centre"""
        Y = year_at(t); y_ = ty[idx]
        hf = np.where(hf0[idx] < .999, hf0[idx] + (1 - hf0[idx]) * vss((Y - hfA[idx]) / np.maximum(hfB[idx] - hfA[idx], 1e-6)), 1.0)
        by = np.where(y_ > 0, vss((t - ton[idx]) / 1.8) if ton is not None else vss((Y - y_ + .5) / 3), vss((Y - 1985) / 3))   # (studio.js uGrowDur 1.8 s)
        keep = np.full(len(idx), float(R_.get('ghost', .05)))
        if reset is not None and t >= (reset['ring']['t0'] if reset.get('ring') else reset['t0']):
            rg = reset['ring']; Rr = curve_at(rg['curve'], t) if t < rg['curve'][-1][0] else 99
            inR = vss((Rr - np.hypot(ctr[idx, 0] - rg['o'][0], ctr[idx, 1] - rg['o'][1]) + .02) / .06)
            keep *= np.where(y_ > reset['reset'], 1 - inR, 1 + (hf - 1) * inR)
        sink0 = R_.get('sinkAt', LT['lamp'])
        up = max(1 - ss(seg(t, sink0, sink0 + R_.get('sinkDur', 2.0))), ss(seg(t, LT.get('lights', math.inf) - .2, LT.get('lights', math.inf) + 1.2)))
        ry = np.maximum(np.maximum(up, (ss(seg(t, G['on'] - .5, G['on'] + .5)) if G else 0) * by * hf), keep)
        ry = ry * today_standing(idx, t) * (1 - live_sink(t))
        return np.where(ry < .002, 0.0, ry)
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
    # spins: a big turn between two keys, listed to look at (compile has unwrapped the azimuth; a turn too fast to follow is its jump)
    pd_ = (FILM.get('prologue') or {}).get('dur', 0)   # (the prologue is cut like a trailer, and closes on black)
    spins = [(t0, t1, a[3], b[3]) for (t0, a), (t1, b) in zip(FILM['camera'][:-1], FILM['camera'][1:]) if abs(b[3] - a[3]) > 120 and t1 > pd_ + .6]
    spin_lines = [f'spin                   {t0:7.2f}-{t1:7.2f}s  azimuth {a0} -> {a1}' for t0, t1, a0, a1 in spins]   # (the whole film's: every stretch counts them)
    def check(CAM):   # one stretch's rows -> (intervals, the lines it prints, how many count)
        if not CAM: return {}, ['camcheck: no camera samples in this stretch'], mx + 1
        rows = np.array([r[:10] if len(r) >= 10 else r + [30] for r in CAM])
        T0, DT = rows[0][0], rows[1][0] - rows[0][0] if len(rows) > 1 else CJ['step']; T1 = rows[-1][0]   # cam.json may cover only a stretch (--from/--to)
        row_at = lambda t: rows[min(len(rows) - 1, max(0, int(round((t - T0) / DT))))]
        offs = []
        for E in eras:   # change only on screen: the buildings rising at each moment must be (mostly) in view
            e = E['e']; t = max(e['on'], T0)
            if t > min(e['on'] + e['span'] + e['grow'], T1): continue   # (not rising in this stretch)
            if 'first' not in E: E['first'] = np.unique(E['bc'].round(7), axis=0, return_index=True)[1]   # (once for every stretch)
            first = E['first']; st0, bc0, gy0 = E['start'][first], E['bc'][first], E['gy'][first]
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

        NS = 40; flags = []
        for row in CAM:
            t, px, py, pz, gx, gy, gz, near, d = row[:9]
            mrg = max(near * 1.5, .0002)
            bad = []
            if py - plate_y(px, pz) < max(2 * near, .0003): bad.append(('below_ground', py - plate_y(px, pz)))
            # solids standing at t: today (not stepped aside) and period cities between rise and sink
            sets = []
            sets.append(('today', ttree, today, tb, tt, today_rise))
            for E in eras:
                e = E['e']
                if t >= e['on'] and not (e.get('off') is not None and t > e['off'] + e['sink'] + 5): sets.append((e['id'], E['tree'], E['g'], E['base'], E['top'], lambda idx, t_, E=E: era_standing(E, idx, t_).astype(float)))
            cam_pt = shapely.Point(px, pz)
            ks = np.linspace(.04, .88, NS)
            seg_pts = shapely.points(np.c_[px + (gx - px) * ks, pz + (gz - pz) * ks]); seg_y = py + (gy - py) * ks
            for name, tree, geoms, base, top, rise in sets:   # (rise: how far up each one stands at t, 0 down .. 1 its full height)
                # inside: the camera within mrg of a footprint, between its base and top (+ margin)
                hit = tree.query(cam_pt, predicate='dwithin', distance=mrg)
                if len(hit):
                    ok = (base[hit] - mrg < py) & (py < top[hit] + mrg)
                    if ok.any(): h_ = hit[ok]; k_ = rise(h_, t); ok[ok] = (k_ > 0) & (py < base[h_] + (top[h_] - base[h_]) * k_ + mrg)
                    if ok.any(): bad.append(('inside', name))
                # blocked: sight-line samples inside a footprint below its top
                pi, gi = tree.query(seg_pts, predicate="intersects")
                if len(pi):
                    ok = (seg_y[pi] < top[gi]) & (seg_y[pi] > base[gi] - mrg)
                    if ok.any(): g_ = gi[ok]; k_ = rise(g_, t); ok[ok] = (k_ > 0) & (seg_y[pi[ok]] < base[g_] + (top[g_] - base[g_]) * k_)
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
        lines = list(spin_lines); n = 0
        for k, v in sorted(out.items()):
            for a, b, w in v:
                if k.startswith('blocked') and w < .08: continue   # a corner grazing the sight line for a sample or two
                if k.startswith('offscreen') and b - a < .35: continue   # a moment, not a scene
                n += 1; lines.append(f'{k:22s} {a:7.2f}-{b:7.2f}s' + (f'  blocks {w:.0%} of the sight line' if k.startswith('blocked') else f'  {w:.0%} of the rising buildings in view' if k.startswith('offscreen') else ''))
        return out, lines + ['camcheck: ' + ('ok' if n <= mx else f'{n} intervals (see out/camcheck.json)')], n
    res = [check(P) for P in parts]
    for P, (_, lines, _) in zip(parts, res):
        if len(parts) > 1: print(f"camcheck {P[0][0]:g}-{P[-1][0]:g} s:" if P else 'camcheck: an empty stretch:')
        print('\n'.join(lines))
    allout = {}   # (the stretches apart in time: their intervals side by side)
    for out, _, _ in res:
        for k, v in out.items(): allout.setdefault(k, []).extend(v)
    json.dump(allout, open(outf, 'w'), indent=1)
    if jsonf: json.dump([{'from': P[0][0] if P else None, 'to': P[-1][0] if P else None, 'ok': n <= mx, 'lines': lines, 'intervals': out} for P, (out, lines, n) in zip(parts, res)], open(jsonf, 'w'), indent=1)
    sys.exit(0 if all(n <= mx for _, _, n in res) else 1)


if __name__ == '__main__':
    main()

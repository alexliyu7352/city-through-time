"""Where a revision changed the film (docs/CHECKS.md "Acceptance and reporting"): two versions' build/film.json compared, the camera
every half second, each line (by id), each panel, tag, route, drawn line and spot (by id), each era's fronts, losses and today_from,
the light the film data sets (the grown city's grow.dim, today's city's dim keys and the night keys every half second; era_look,
night_look and shade for the whole film: a light changed for one stretch can drown another's subject), and the
stretches that differ printed, each with what changed there and the tools/rangecheck.py command that compares it with the previous
version line by line. A stretch whose picture and lines only moved together (a station before it grew or shrank) is listed apart:
its lines still meet the same picture, so it needs no comparison unless its timing was the point.
usage: python -I tools/filmdiff.py <previous: city_slug | city folder> <this: city_slug | city folder>"""
import bisect, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEP = 0.5     # camera sampled this often
EPS = 1e-3     # a camera value closer than this is the same
JOIN = 2.0     # changes closer than this make one stretch
PAD = 1.0      # each stretch compared with this much either side
TIMES = ('on', 'off', 't0', 't1', 'gone')
NAME = {'lines': 'drawn-line', 'footage': 'panel', 'pins': 'tag', 'routes': 'route', 'readouts': 'readout', 'spots': 'spot', 'fronts': 'front', 'losses': 'loss', 'today': 'today_from'}
LOOKS = ('era_look', 'night_look', 'shade')   # the film's light settings with no time of their own: for the whole film


def load(c):
    D = os.path.abspath(c) if '/' in c else os.path.join(ROOT, 'cities', c)
    return json.load(open(os.path.join(D, 'build', 'film.json'), encoding='utf-8')), c


def cam(f, t): return keys_at(f['camera'], t)


def keys_at(ks, t):   # [[t, [v, ..]], ..] at t, straight between keys
    i = bisect.bisect_right([k[0] for k in ks], t) - 1
    if i < 0 or i >= len(ks) - 1: return ks[max(i, 0)][1]
    (t0, v0), (t1, v1) = ks[i], ks[i + 1]; u = (t - t0) / (t1 - t0) if t1 > t0 else 0
    return [x + (y - x) * u for x, y in zip(v0, v1)]


def same_cam(f, g, t, d=0.0): return max(abs(x - y) for x, y in zip(cam(f, t), cam(g, t - d))) < EPS


def light(f, t):   # the grown city's light (grow.dim: one key or keys, each easing from the last), today's city dimmed (dim keys), night
    D = (f.get('grow') or {}).get('dim'); v = 1.0
    for k in (D if isinstance(D, list) else [D] if D else []):
        u = min(1.0, max(0.0, (t - k['t']) / k.get('dur', .8))); v += (k['to'] - v) * u * u * (3 - 2 * u)
    return [v] + [keys_at(f[k], t)[0] if f.get(k) else 0.0 for k in ('dim', 'night')]


def same_light(f, g, t, d=0.0): return max(abs(x - y) for x, y in zip(light(f, t), light(g, t - d))) < EPS


def moved(x, d):   # x with its times taken back by d: equal to the previous version's item when only the time moved
    x = dict(x)
    for k in TIMES:
        if isinstance(x.get(k), (int, float)): x[k] = round(x[k] - d, 2)
    if isinstance(x.get('a'), list) and len(x['a']) == 2: x['a'] = [round(v - d, 2) for v in x['a']]
    if isinstance(x.get('curve'), list): x['curve'] = [[round(p[0] - d, 2), *p[1:]] for p in x['curve']]
    return json.dumps(x, sort_keys=True)


def span(kind, x):
    if kind == 'footage': return x['on'], x['on'] + x.get('dur', 0)
    if kind in ('routes', 'lines'): return x['on'], x.get('off') or x['on']
    if kind == 'fronts': return tuple(x['a'])
    if kind == 'losses': c = x.get('curve') or [[x['gone']]]; return c[0][0], x['gone']
    return x['t0'], x['t1']


def items(f):   # (kind, key) -> item, every timed thing on screen
    out = {}
    for kind in ('footage', 'pins', 'routes', 'lines', 'readouts', 'spots'):
        for i, x in enumerate(f.get(kind) or []): out[(kind, x.get('id') or f'#{i}')] = x
    for e in f.get('eras') or []:
        if e.get('todayFrom') is not None: out[('today', e['id'])] = {'t0': e['todayFrom'], 't1': e.get('off') or f['dur']}   # (today's city no longer dims for it)
        for x in e.get('fronts') or []: out.setdefault(('fronts', f"{e['id']} {x['a'][0]:.2f}"), x)
        for x in e.get('losses') or []: out[('losses', f"{e['id']} {x['id']}")] = x
    return out


def main():
    if len(sys.argv) != 3: sys.exit(__doc__.split('usage: ')[1])
    (P, pname), (N, nname) = load(sys.argv[1]), load(sys.argv[2])
    pc = {c['id']: c for c in P['cues']}; both = sorted((c['t0'], c['t0'] - pc[c['id']]['t0']) for c in N['cues'] if c['id'] in pc)
    def shift(t):   # how far the film moved here: the nearest line both versions have
        i = bisect.bisect_left(both, (t,)); near = [both[j] for j in (i - 1, i) if 0 <= j < len(both)]
        return round(min(near, key=lambda b: abs(b[0] - t))[1], 2) if near else 0.0
    changed, slid = [], []   # (a, b, what)
    t, end = 0.0, max(N['dur'], P['dur'])
    while t <= end:
        if not same_cam(N, P, t): (slid if (d := shift(t)) and same_cam(N, P, t, d) else changed).append((t, t, 'camera'))
        if not same_light(N, P, t): (slid if (d := shift(t)) and same_light(N, P, t, d) else changed).append((t, t, 'light'))
        t = round(t + STEP, 2)
    for k in LOOKS:
        if json.dumps(P.get(k), sort_keys=True) != json.dumps(N.get(k), sort_keys=True): changed.append((0.0, N['dur'], f'light {k} (whole film)'))
    for c in N['cues']:
        o = pc.get(c['id'])
        if o is None: changed.append((c['t0'], c['t1'], f"line {c['id']} (new)")); continue
        if (o.get('a'), o.get('b')) != (c.get('a'), c.get('b')): changed.append((c['t0'], c['t1'], f"line {c['id']} (words)"))
        elif abs(o['t0'] - c['t0']) > .02 or abs(o['t1'] - c['t1']) > .02:
            d = round(c['t0'] - o['t0'], 2); still = all(same_cam(N, P, s, d) for s in (c['t0'], (c['t0'] + c['t1']) / 2, c['t1']))
            (slid if still and abs((c['t1'] - o['t1']) - d) <= .02 else changed).append((c['t0'], c['t1'], f"line {c['id']}"))
    ids = {c['id'] for c in N['cues']}
    for c in P['cues']:
        if c['id'] not in ids: changed.append((c['t0'], c['t1'], f"line {c['id']} (gone; previous version's time)"))
    I, J = items(P), items(N); matched = set()   # a front keyed by its start: one that moved is gone under its old key and new under its new one
    for k, x in J.items():
        o = I.get(k); a, b = span(k[0], x)
        if o is not None and json.dumps(o, sort_keys=True) == json.dumps(x, sort_keys=True): continue
        d = shift(a)
        if o is not None and d and moved(x, d) == moved(o, 0): slid.append((a, b, f'{NAME[k[0]]} {k[1]}')); continue
        twin = next((kk for kk, oo in I.items() if o is None and d and kk[0] == k[0] == 'fronts' and kk not in J and kk not in matched
                     and kk[1].split()[0] == k[1].split()[0] and moved(x, d) == moved(oo, 0)), None)
        if twin: matched.add(twin); slid.append((a, b, f'{NAME[k[0]]} {k[1]}')); continue
        changed.append((a, b, f"{NAME[k[0]]} {k[1]}{' (new)' if o is None else ''}"))
    for k, o in I.items():
        if k not in J and k not in matched: a, b = span(k[0], o); changed.append((a, b, f"{NAME[k[0]]} {k[1]} (gone; previous version's time)"))
    def merged(xs):
        out = []
        for a, b, w in sorted(xs):
            if out and a - out[-1][1] <= JOIN: out[-1][1] = max(out[-1][1], b); out[-1][2].append(w)
            else: out.append([a, b, [w]])
        return out
    def said(ws):   # the camera once, the rest by kind, a long list cut short
        ws = list(dict.fromkeys(ws)); kinds = {}
        for w in ws: kinds.setdefault(w.split(' ')[0], []).append(w.split(' ', 1)[1] if ' ' in w else '')
        return '; '.join(k if k in ('camera', 'light') and not any(v) else f"{k} {', '.join(q for q in v[:4] if q)}{f' (+{len(v) - 4})' if len(v) > 4 else ''}" for k, v in kinds.items())
    ch, sl = merged(changed), merged(slid)
    print(f'filmdiff: {pname} -> {nname}: {len(ch)} stretch(es) changed, {len(sl)} only moved in time')
    for a, b, ws in ch: print(f'  {a:8.2f}-{b:8.2f}  {said(ws)}')
    if sl: print('only moved (lines and picture together; compare if the timing was the point):')
    for a, b, ws in sl: print(f'  {a:8.2f}-{b:8.2f}  moved {shift(a):+.2f} s: {said(ws)}')
    if ch: print('compare each changed stretch with the previous version, line by line:')
    for a, b, _ in ch: print(f'  uv run python -I tools/rangecheck.py {nname} --from {max(0, a - PAD):.2f} --to {min(N["dur"], b + PAD):.2f} --against {pname}')


if __name__ == '__main__':
    main()

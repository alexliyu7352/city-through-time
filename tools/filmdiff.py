"""Where a revision changed the film (docs/CHECKS.md "Acceptance and reporting"): two versions' build/film.json compared, the camera
every half second, each line (by id), each panel, tag, route, drawn line and spot (by id), each era's fronts, losses and today_from,
the light the film data sets (the grown city's grow.dim, today's city's dim keys and the night keys every half second; era_look,
night_look and shade for the whole film: a light changed for one stretch can drown another's subject), and the
stretches that differ printed, each with what changed there, and one tools/rangecheck.py command that compares them all with the
previous version line by line (one command: the film is loaded once for every stretch). Each time is compared with the film's shift
at that time (the nearest line both versions have), so a part that only moved with its lines did not change; a long item (a
chapter's readout) that changed is placed where it differs. A stretch whose picture and lines only moved together (a station before
it grew or shrank) is listed apart: its lines still meet the same picture, so it needs no comparison unless its timing was the point.
Then the lines the camera now shows from much farther than before (at the line's closest moment, over FARTHER times the distance): what
was seen close is often what read better (a wall raised, a street lived in), so look at those lines first in the line sheets.
usage: python -I tools/filmdiff.py <previous: city_slug | city folder> <this: city_slug | city folder> [--json out.json]
  --json  the changed stretches (padded as rangecheck takes them) and the farther lines, for tools/round.py"""
import bisect, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEP = 0.5     # camera sampled this often
EPS = 1e-3     # a camera value closer than this is the same
JOIN = 2.0     # changes closer than this make one stretch
PAD = 1.0      # each stretch compared with this much either side
FARTHER = 2.0  # a line whose camera is this many times farther away than before at its closest is listed
WHOLE = 60.0   # an item on screen this long or shorter that changed is compared whole (a tag's reading time is judged whole); a longer
               # one (a chapter's readout, a drawn line) only where it differs, so one note does not mark a whole chapter
TIMES = ('on', 'off', 't0', 't1', 'gone', 't', 'a', 'burn', 'flash')   # times at any depth: a number or a list of them ([a, b]) under these keys; a curve's points start with one
TOL = .011     # two times this close are the same (kept to the cent, some to the ms: rounded apart, they can differ by one)
NAME = {'lines': 'drawn-line', 'footage': 'panel', 'pins': 'tag', 'routes': 'route', 'arrows': 'arrow', 'readouts': 'readout', 'spots': 'spot', 'fronts': 'front', 'losses': 'loss', 'today': 'today_from'}
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


def num(v): return isinstance(v, (int, float)) and not isinstance(v, bool)
def own(x): return [t for k, v in x.items() if k in TIMES for t in (v if isinstance(v, list) else [v]) if num(t)] if isinstance(x, dict) else []


def diff(x, o, sh, at, k=None):
    """where x (this version) differs from o (the previous) once each time of x is taken back by the film's shift at that time
    (sh(t)): [(a, b), ..] in this version's seconds, [] when x only moved. A time that differs is placed at its own seconds; any
    other difference at the part holding it that has times of its own (a readout's note, not the whole readout), else at `at`"""
    if isinstance(x, dict) and isinstance(o, dict):
        if k is not None and own(x): at = (min(own(x)), max(own(x)))
        return [w for q in sorted(x.keys() | o.keys()) for w in (diff(x[q], o[q], sh, at, q) if q in x and q in o else [at])]
    if k in TIMES and num(x) and num(o): return [] if abs(x - sh(x) - o) <= TOL else [(min(x, o + sh(x)), max(x, o + sh(x)))]
    if not (isinstance(x, list) and isinstance(o, list)): return [] if x == o else [at]
    if k == 'curve':   # [[t, value..], ..]: each point at its time
        if len(x) != len(o): return [(min(x[0][0], o[0][0] + sh(x[0][0])), max(x[-1][0], o[-1][0] + sh(x[-1][0])))] if x and o else [at]
        same = lambda p, q: len(p) == len(q) and all(math.isclose(u, v, rel_tol=1e-3) for u, v in zip(p[1:], q[1:]))   # (a ring's radius recomputed off frame: a thousandth is no change)
        return [w for p, q in zip(x, o) for w in diff(p[0], q[0], sh, at, 't') + ([] if same(p, q) else [(p[0], p[0])])]
    if len(x) == len(o): return [w for p, q in zip(x, o) for w in diff(p, q, sh, at, k)]
    if not all(isinstance(v, dict) for v in x + o): return [at]
    left, out = list(o), []   # parts added or taken away (a readout's notes): each one without a twin, at its own time
    for p in x:
        q = next((q for q in left if not diff(p, q, sh, at, k)), None)
        if q is None: out.append((min(own(p)), max(own(p))) if own(p) else at)
        else: left.remove(q)
    return out + [(min(own(q)) + sh(min(own(q))), max(own(q)) + sh(max(own(q)))) if own(q) else at for q in left]


def span(kind, x):
    if kind == 'footage': return x['on'], x['on'] + x.get('dur', 0)
    if kind in ('routes', 'arrows', 'lines'): return x['on'], x.get('off') or x['on']
    if kind == 'fronts': return tuple(x['a'])
    if kind == 'losses': c = x.get('curve') or [[x['gone']]]; return c[0][0], x['gone']
    return x['t0'], x['t1']


def items(f):   # (kind, key) -> item, every timed thing on screen
    out = {}
    for kind in ('footage', 'pins', 'routes', 'arrows', 'lines', 'readouts', 'spots'):
        for i, x in enumerate(f.get(kind) or []): out[(kind, x.get('id') or f'#{i}')] = x
    for e in f.get('eras') or []:
        if e.get('todayFrom') is not None: out[('today', e['id'])] = {'t0': e['todayFrom'], 't1': e.get('off') or f['dur']}   # (today's city no longer dims for it)
        for x in e.get('fronts') or []: out.setdefault(('fronts', f"{e['id']} {x['a'][0]:.2f}"), x)
        for x in e.get('losses') or []: out[('losses', f"{e['id']} {x['id']}")] = x
    return out


def main():
    args = sys.argv[1:]; out_json = None
    if '--json' in args: i = args.index('--json'); out_json = args[i + 1]; del args[i:i + 2]
    if len(args) != 2: sys.exit(__doc__.split('usage: ')[1])
    (P, pname), (N, nname) = load(args[0]), load(args[1])
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
        o = I.get(k); a, b = span(k[0], x); name = f'{NAME[k[0]]} {k[1]}'
        if o is not None and json.dumps(o, sort_keys=True) == json.dumps(x, sort_keys=True): continue
        if o is None and k[0] == 'fronts':
            twin = next((kk for kk, oo in I.items() if kk[0] == 'fronts' and kk not in J and kk not in matched and kk[1].split()[0] == k[1].split()[0]
                         and not diff(x, oo, shift, (a, b))), None)
            if twin: matched.add(twin); slid.append((a, b, name)); continue
        if o is None: changed.append((a, b, name + ' (new)')); continue
        w = diff(x, o, shift, (a, b))
        if w: changed += [(p, q, name) for p, q in w + ([(a, b)] if b - a <= WHOLE else [])]
        else: slid += [(p, q, name) for p, q in diff(x, o, lambda t: 0.0, (a, b))]   # (where it moved; none: the same to the cent)
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
    # the camera's distance (a key's sixth value) at the line's closest moment, this version against the last
    near_ = lambda f, a, b: min(cam(f, a + (b - a) * k / 6)[5] for k in range(7))
    far = []
    for c in N['cues']:
        o = pc.get(c['id'])
        if o is None or c.get('node') is None: continue   # (the prologue is cut like a trailer)
        dn, do = near_(N, c['t0'], c['t1']), near_(P, o['t0'], o['t1'])
        if do > 0 and dn / do > FARTHER: far.append((c['id'], c['t0'], do, dn))
    if far:
        print(f'lines the camera now shows from over {FARTHER:g}x farther than before (at their closest): what was seen close often read better, look at these first:')
        for id_, t_, do, dn in far: print(f'  {id_:10s} {t_:8.2f} s  distance {do:.3f} -> {dn:.3f}')
    spans = [[round(max(0, a - PAD), 2), round(min(N['dur'], b + PAD), 2)] for a, b, _ in ch]
    if ch: print('compare the changed stretches with the previous version, line by line, all in one command:')
    if ch: print(f'  uv run python -I tools/rangecheck.py {nname} ' + ' '.join(f'--from {a:.2f} --to {b:.2f}' for a, b in spans) + f' --against {pname}')
    if out_json: json.dump({'previous': pname, 'this': nname, 'stretches': spans, 'what': [said(ws) for _, _, ws in ch],
                            'farther': [{'line': i_, 't': t_, 'before': round(do, 4), 'now': round(dn, 4)} for i_, t_, do, dn in far]}, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()

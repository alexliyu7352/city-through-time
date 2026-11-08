"""Where a revision changed the film (docs/CHECKS.md "Acceptance and reporting"): two versions' build/film.json compared, the camera
every half second, each line (by id), every timed thing on screen by id (panels, tags, routes, arrows, drawn lines, spots, readouts,
living moments, marks, stations with their chapter titles and rings, epochs, labels, props, ranges, sections), the timed settings
(the lamps' times, the prologue, the grown city, the timeline bar, the end card), each period city's own times (its rise, its fall),
its fronts, losses and today_from, the year counter every half second, the light the film data sets (the grown city's grow.dim,
today's city's dim keys and the night keys every half second; era_look and shade for the whole film, night_look where the night is
on: a light changed for one stretch can drown another's subject), and the stretches that differ printed, each with what changed
there, and one tools/rangecheck.py command that compares them all with the previous version line by line (one command: the film is
loaded once for every stretch). Each time is compared with the film's shift at that time (the nearest line both versions have), so a
part that only moved with its lines did not change; a long item (a chapter's readout) that changed is placed where it differs. A
stretch whose picture and lines only moved together (a station before it grew or shrank) is listed apart: its lines still meet the
same picture, so it needs no comparison unless its timing was the point.
Then the lines the camera now shows from much farther than before (at the line's closest moment, over FARTHER times the distance): what
was seen close is often what read better (a wall raised, a street lived in), so look at those lines first in the line sheets.
Then what it cannot place in time: the period cities whose model changed (buildings, ground, water, boundary, colour: on screen for as
long as the city stands, so look at them with tools/eraview.mjs in both versions, then in the film where it shows them), and any other
part of film.json that changed (a whole-film setting, or a kind this tool does not know yet: teach it here rather than skip it).
usage: python -I tools/filmdiff.py <previous: city_slug | city folder> <this: city_slug | city folder> [--json out.json]
  --json  the changed stretches (padded as rangecheck takes them), the farther lines, the changed models and the rest, for tools/round.py"""
import bisect, filecmp, json, math, os, sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEP = 0.5     # camera sampled this often
EPS = 1e-3     # a camera value closer than this is the same
JOIN = 2.0     # changes closer than this make one stretch
PAD = 1.0      # each stretch compared with this much either side
FARTHER = 2.0  # a line whose camera is this many times farther away than before at its closest is listed
WHOLE = 60.0   # an item on screen this long or shorter that changed is compared whole (a tag's reading time is judged whole); a longer
               # one (a chapter's readout, a drawn line) only where it differs, so one note does not mark a whole chapter
TIMES = ('on', 'off', 't0', 't1', 'gone', 't', 'a', 'burn', 'flash', 'arrive', 'dimAt', 'keep', 'tOut', 'up', 'hit', 'lamp', 'lights', 'lightsOut', 'darks')   # times at any depth: a number or a list of them ([a, b], [[a, b], ..]) under these keys; a curve's points start with one (a key that holds a length in one kind, a living moment's arrive, is made a time first: items())
TOL = .011     # two times this close are the same (kept to the cent, some to the ms: rounded apart, they can differ by one)
NAME = {'lines': 'drawn-line', 'footage': 'panel', 'pins': 'tag', 'routes': 'route', 'arrows': 'arrow', 'readouts': 'readout', 'spots': 'spot', 'fronts': 'front', 'losses': 'loss', 'today': 'today_from',
        'living': 'living-moment', 'marks': 'mark', 'nodes': 'station', 'epochs': 'epoch', 'labels': 'label', 'props': 'prop', 'pick': 'pick', 'ranges': 'range', 'sections': 'section',
        'decals': 'decal', 'ev': 'event', 'eras': 'city', 'light': 'lamps', 'prologue': 'prologue', 'grow': 'grown-city', 'bar': 'timeline-bar', 'end': 'end-card'}
LOOKS = ('era_look', 'night_look', 'shade')   # the film's light settings with no time of their own: for the whole film (night_look: where the night is on)
KINDS = ('footage', 'pins', 'routes', 'arrows', 'lines', 'readouts', 'spots', 'living', 'marks', 'nodes', 'epochs', 'labels', 'props', 'pick', 'ranges', 'sections', 'decals', 'ev')   # the film's timed lists, each item by its id
ONE = ('light', 'prologue', 'grow', 'bar', 'end')   # timed settings, one of each
SEEN = ('camera', 'dim', 'night', 'yearline', 'cues', 'eras', 'dur') + LOOKS   # compared on their own: sampled, line by line, each period city (its times as an item, what it is made of in model())
PACKED = ('voice', 'music', 'basinMap', 'basinSlots', 'eraSlots', 'groundMap', 'groundSlots', 'keepMaps')   # heard, or how the build is packed: seen through what is compared
ASIDE_S = 4.0  # a building of today stepping aside or coming back (the engine: over a city's grow, today_from over 3 s): seen in this time
LENGTHS = ('arrive', 'reveal', 'hold', 'out', 'back')   # a living moment's: the camera arrives (before its on), the picture reveals, holds, goes out, the camera goes back


def load(c):
    D = os.path.abspath(c) if '/' in c else os.path.join(ROOT, 'cities', c)
    F = json.load(open(os.path.join(D, 'build', 'film.json'), encoding='utf-8'))
    F['yearline'] = [[t, [y]] for t, y in F.get('yearline') or []]   # (as camera keys, for keys_at)
    return F, c, D


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


def night_on(F):   # [(a, b)] where the film's night is above 0 (film.night keys, held before the first and after the last): night_look acts there only
    ks = F.get('night') or []; out = [(0.0, ks[0][0])] if ks and ks[0][1][0] > 0 else []
    out += [(a, b) for (a, va), (b, vb) in zip(ks, ks[1:]) if va[0] > 0 or vb[0] > 0]
    return out + ([(ks[-1][0], F['dur'])] if ks and ks[-1][1][0] > 0 else [])


def same_light(f, g, t, d=0.0): return max(abs(x - y) for x, y in zip(light(f, t), light(g, t - d))) < EPS


def year(f, t): return round(keys_at(f['yearline'], t)[0]) if f['yearline'] else None   # the year the counter shows (straight between keys, main.js yearAt)
def same_year(f, g, t, d=0.0): return year(f, t) == year(g, t - d)


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


def span(kind, x, dur):
    if kind == 'footage': return x['on'], x['on'] + x.get('dur', 0)
    if kind in ('routes', 'arrows', 'lines'): return x['on'], x.get('off') or x['on']
    if kind == 'fronts': return tuple(x['a'])
    if kind == 'losses': c = x.get('curve') or [[x['gone']]]; return c[0][0], x['gone']
    if kind == 'prologue': return 0.0, x['dur']
    if kind == 'grow': return x['on'], dur
    if kind == 'end': return x['t'], dur
    ts = own(x); return (min(ts), max(ts)) if ts else (0.0, dur)   # (its own times; none: the whole film)


def items(f):   # (kind, key) -> item, every timed thing on screen
    out = {}
    for kind in KINDS:
        for i, x in enumerate(f.get(kind) or []):
            if kind == 'living':   # its lengths as the times each ends at, so a moment that only moved with its lines did not change
                ts = [x['on'] - x['arrive'], x['on']]
                for k in LENGTHS[1:]: ts.append(ts[-1] + x[k])
                x = {**{k: v for k, v in x.items() if k not in LENGTHS}, 'a': [round(t, 3) for t in ts]}
            if kind == 'nodes': x = {k: v for k, v in x.items() if k != 'wave'}   # (where its colour wave starts: seen as its ring, compared there)
            out[(kind, x.get('id') or f'#{i}')] = x
    for kind in ONE:
        x = f.get(kind)
        if x and kind == 'grow' and x.get('yl'): x = {**x, 'yl': [{'t': t, 'year': y} for t, y in x['yl']]}   # (its years by time: the times shift, the years do not)
        if x and kind == 'bar': x = {**x, 'from': None, 'to': None, 'a': [x.get('from'), x.get('to')]}   # (the bar runs from the lamp to the lights: times)
        if x: out[(kind, '')] = x
    for e in f.get('eras') or []:
        ts = [e['on'], e['on'] + e.get('span', 0), e['on'] + e.get('rise', 0)]   # the city rises from its on over its span, the last part risen at its rise
        if e.get('off') is not None: ts += [e['off'], e['off'] + e.get('sink', 0)] + ([e['off'] - .6 * e['burn']] if e.get('burn') else [])   # it goes at its off (a burn before)
        out[('eras', e['id'])] = {'a': [round(t, 3) for t in ts], **{k: e[k] for k in ('up', 'fallR') if k in e}}   # (its slot and when it holds it are packing: left out)
        if e.get('todayFrom') is not None: out[('today', e['id'])] = {'t0': e['todayFrom'], 't1': e.get('off') or f['dur']}   # (today's city no longer dims for it)
        for x in e.get('fronts') or []: out.setdefault(('fronts', f"{e['id']} {x['a'][0]:.2f}"), x)
        for x in e.get('losses') or []: out[('losses', f"{e['id']} {x['id']}")] = x
    return out


def model(P, N, pd, nd, shift):
    """what the period cities are made of rather than when: [(city, on, off, what changed)], and [(a, b, name)] where a building or a
    basin of a city whose model did not change now rises at another time (each rises at the city's on + its rank × the city's span:
    a city re-timed re-ranks them all, so they are compared as times, shift taken back, not as the model)"""
    pe = {e['id']: e for e in P.get('eras') or []}; atlas = {}; notes, rises = [], []
    def crop(F, D, e):   # a city's ground (film.groundMap: one atlas of every city's ground, each its crop), its slots as the city's own
        if D not in atlas: atlas[D] = np.asarray(Image.open(os.path.join(D, 'build', F['groundMap']['file'])))
        ax, ay, nx, nz = e['ground']['a']; c = atlas[D][ay:ay + nz, ax:ax + nx].copy()
        own = np.zeros(256, np.uint8)   # (B: the slot that times a texel's ground + 1, numbered over the whole film: grounds added before it renumber it)
        for i, b in enumerate(e.get('basins') or []): own[b['k'] + 1] = i + 1
        c[..., 2] = own[c[..., 2]]; return c
    def ground_same(o, e):
        g, h = o.get('ground'), e.get('ground')
        if not g or not h: return not g and not h
        return g['m'] == h['m'] and g['a'][2:] == h['a'][2:] and np.array_equal(crop(P, pd, o), crop(N, nd, e))
    def risen(o, e, ro, rn, name):   # ranks of the same parts in both versions -> where their rise differs
        to, tn = o['on'] + np.array(ro) * o.get('span', 0), e['on'] + np.array(rn) * e.get('span', 0)
        u, inv = np.unique(tn.round(2), return_inverse=True); sh = np.array([shift(t) for t in u])[inv]
        bad = np.abs(tn - sh - to) > TOL; rises.extend((x, y, name) for x, y in zip(np.minimum(tn, to + sh)[bad].tolist(), np.maximum(tn, to + sh)[bad].tolist()))
    water = lambda e: [{k: v for k, v in b.items() if k not in ('k', 'rank')} for b in e.get('basins') or []]   # (k: its slot in the water map, packing; rank: when it fills)
    for e in N.get('eras') or []:
        o = pe.get(e['id'])
        if o is None: continue   # (a new city: its times are listed as new above)
        what = []; fo, fn = os.path.join(pd, 'build', o['file']), os.path.join(nd, 'build', e['file'])
        if not filecmp.cmp(fo, fn, shallow=False):
            A, B = json.load(open(fo, encoding='utf-8')), json.load(open(fn, encoding='utf-8')); pa, pb = A['prims'], B['prims']
            if A.get('lost') != B.get('lost') or len(pa) != len(pb) or any(p[:10] != q[:10] or p[11:] != q[11:] for p, q in zip(pa, pb)): what.append('buildings')
            else: risen(o, e, [p[10] for p in pa], [q[10] for q in pb], f"city {e['id']} (buildings rising)")
            del A, B, pa, pb
        if not ground_same(o, e): what.append('ground')
        if water(o) != water(e): what.append('water')
        elif o.get('basins'): risen(o, e, [b['rank'] for b in o['basins']], [b['rank'] for b in e['basins']], f"city {e['id']} (water filling)")
        if o.get('boundary') != e.get('boundary'): what.append('boundary')
        if any(o.get(k) != e.get(k) for k in ('col', 'tint', 'edgeD', 'sinkStyle')): what.append('colour')
        if what: notes.append((e['id'], e['on'], e.get('off'), what))
    return notes, rises


def aside(P, N, pd, nd, shift):
    """[(a, b, name)] where today's buildings step aside for a period city, or come back round what of it still stands, at
    another time than before: each building read at its centre (the engine's aCtr) in the city's hide map and, with today_from,
    its keep map (compile hide_layer, keep_layer). A hide region given a time, a court, a landmark kept clear: they change those
    maps and nothing else. A building that stepped aside in both versions differs between its two times; one that steps aside
    (or stays clear after today_from) in one version only differs from then for as long as the city stands: listed where it
    changes, for ASIDE_S s (it steps aside, or comes back, there; what follows holds it)"""
    out = []; dd = lambda D: os.path.join(D, 'build', 'data')
    mp, mn = os.path.join(dd(pd), 'model.json'), os.path.join(dd(nd), 'model.json')
    if not (os.path.exists(mp) and os.path.exists(mn)): return out
    if not filecmp.cmp(mp, mn, shallow=False): return [(0.0, N['dur'], "today's-city (its buildings changed: where they step aside not compared)")]
    rings = [r[2][0] for r in json.load(open(mn, encoding='utf-8'))['p']]; ok = np.array([len(r) >= 3 for r in rings])
    ctr = np.array([np.mean(r, axis=0)[:2] if len(r) >= 3 else (0.0, 0.0) for r in rings], float)
    PW, PD = json.load(open(mn, encoding='utf-8'))['size']; maps = {}
    def read(D, f):
        if (D, f) not in maps:
            p_ = os.path.join(dd(D), f)
            maps[(D, f)] = np.asarray(Image.open(p_).convert('RGBA')).astype(np.float32) / 255 if os.path.exists(p_) else None
        return maps[(D, f)]
    def at(D, e, base, own):   # the city's channel at every building's centre (a shared channel: the city's own map)
        img = read(D, f"{own}_{e['id']}.png") if e.get('occupy') else read(D, (base, f'{base}2', f'{base}3')[e['hide'] // 4] + '.png')
        if img is None: return None
        H_, W_ = img.shape[:2]; u = np.clip(((ctr[:, 0] / PW + .5) * W_).astype(int), 0, W_ - 1); v = np.clip(((ctr[:, 1] / PD + .5) * H_).astype(int), 0, H_ - 1)
        return img[v, u, 0] if e.get('occupy') else img[v, u, e['hide'] % 4]
    pe = {e['id']: e for e in P.get('eras') or []}
    for e in N.get('eras') or []:
        o = pe.get(e['id'])
        if o is None or e.get('hide') is None or o.get('hide') is None: continue
        hn, ho = at(nd, e, 'hide', 'hide'), at(pd, o, 'hide', 'hide')
        if hn is None or ho is None: continue
        end = lambda f, x: min([t for t in (x.get('todayFrom'), x.get('off')) if num(t)] or [f['dur']])
        tn = np.where((hn >= .02) & ok, e['on'] + (hn - .04) / .96 * e.get('span', 0), np.nan)
        to = np.where((ho >= .02) & ok, o['on'] + (ho - .04) / .96 * o.get('span', 0), np.nan)
        q = 1 / 255 / .96 * max(e.get('span', 0), o.get('span', 0)) + TOL   # (a rank kept to one step of the map's 8 bits)
        u, inv = np.unique(np.nan_to_num(tn, nan=-1).round(1), return_inverse=True); sh = np.array([shift(t) for t in u])[inv]
        both = ~np.isnan(tn) & ~np.isnan(to); bad = both & (np.abs(tn - sh - to) > q)
        name = f"city {e['id']} (today's buildings stepping aside)"
        out += [(float(min(a, b + s)), float(max(a, b + s)), name) for a, b, s in zip(tn[bad], to[bad], sh[bad])]   # (plain floats: the --json report)
        for t_, ws in ((tn[~np.isnan(tn) & np.isnan(to) & ok], 'now'), (to[np.isnan(tn) & ~np.isnan(to) & ok], 'before')):
            for t in np.unique(t_.round(1)):
                t = float(t) + (shift(float(t)) if ws == 'before' else 0.0); out.append((t, min(t + ASIDE_S, end(N, e)), f"{name[:-1]}, {ws} only)"))
        if num(e.get('todayFrom')) and num(o.get('todayFrom')):
            kn, ko = at(nd, e, 'keep', 'keep'), at(pd, o, 'keep', 'keep')
            if kn is not None and ko is not None and ((kn >= .02) != (ko >= .02))[ok].any():
                t = float(e['todayFrom']); out.append((t, t + ASIDE_S, f"city {e['id']} (today's buildings coming back round what still stands)"))
    return out


def main():
    args = sys.argv[1:]; out_json = None
    if '--json' in args: i = args.index('--json'); out_json = args[i + 1]; del args[i:i + 2]
    if len(args) != 2: sys.exit(__doc__.split('usage: ')[1])
    (P, pname, pd), (N, nname, nd) = load(args[0]), load(args[1])
    pc = {c['id']: c for c in P['cues']}; both = sorted((c['t0'], c['t0'] - pc[c['id']]['t0']) for c in N['cues'] if c['id'] in pc)
    def shift(t):   # how far the film moved here: the nearest line both versions have
        i = bisect.bisect_left(both, (t,)); near = [both[j] for j in (i - 1, i) if 0 <= j < len(both)]
        return round(min(near, key=lambda b: abs(b[0] - t))[1], 2) if near else 0.0
    changed, slid = [], []   # (a, b, what)
    t, end = 0.0, max(N['dur'], P['dur'])
    while t <= end:
        if not same_cam(N, P, t): (slid if (d := shift(t)) and same_cam(N, P, t, d) else changed).append((t, t, 'camera'))
        if not same_light(N, P, t): (slid if (d := shift(t)) and same_light(N, P, t, d) else changed).append((t, t, 'light'))
        if not same_year(N, P, t): (slid if (d := shift(t)) and same_year(N, P, t, d) else changed).append((t, t, 'year'))
        t = round(t + STEP, 2)
    for k in LOOKS:
        if json.dumps(P.get(k), sort_keys=True) == json.dumps(N.get(k), sort_keys=True): continue
        if k == 'night_look': changed += [(a, b, 'light night_look') for a, b in night_on(N)] + [(a, b, "light night_look (previous version's time)") for a, b in night_on(P)]
        else: changed.append((0.0, N['dur'], f'light {k} (whole film)'))
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
        o = I.get(k); a, b = span(k[0], x, N['dur']); name = f'{NAME[k[0]]} {k[1]}'.strip()
        if o is not None and json.dumps(o, sort_keys=True) == json.dumps(x, sort_keys=True): continue
        if o is None and k[0] == 'fronts':
            twin = next((kk for kk, oo in I.items() if kk[0] == 'fronts' and kk not in J and kk not in matched and kk[1].split()[0] == k[1].split()[0]
                         and not diff(x, oo, shift, (a, b))), None)
            if twin: matched.add(twin); slid.append((a, b, name)); continue
        if o is None: changed.append((a, b, name + ' (new)')); continue
        if k[0] == 'prologue':   # its scene keys: its own times, each with the film's time whose city it shows (that one moves with the film)
            sc, so = x.get('scene') or [], o.get('scene') or []
            if {**x, 'scene': 0} != {**o, 'scene': 0} or len(sc) != len(so) or any(p[0] != q[0] or abs(p[1] - shift(p[1]) - q[1]) > TOL for p, q in zip(sc, so)): changed.append((a, b, name))
            continue
        w = diff(x, o, shift, (a, b))
        if w: changed += [(p, q, name) for p, q in w + ([(a, b)] if b - a <= WHOLE else [])]
        else: slid += [(p, q, name) for p, q in diff(x, o, lambda t: 0.0, (a, b))]   # (where it moved; none: the same to the cent)
    for k, o in I.items():
        if k not in J and k not in matched: a, b = span(k[0], o, P['dur']); changed.append((a, b, f"{NAME[k[0]]} {k[1]} (gone; previous version's time)".replace('  ', ' ')))
    def merged(xs):
        out = []
        for a, b, w in sorted(xs):
            if out and a - out[-1][1] <= JOIN: out[-1][1] = max(out[-1][1], b); out[-1][2].append(w)
            else: out.append([a, b, [w]])
        return out
    def said(ws):   # the camera once, the rest by kind, a long list cut short
        ws = list(dict.fromkeys(ws)); kinds = {}
        for w in ws: kinds.setdefault(w.split(' ')[0], []).append(w.split(' ', 1)[1] if ' ' in w else '')
        return '; '.join(k if not any(v) else f"{k} {', '.join(q for q in v[:4] if q)}{f' (+{len(v) - 4})' if len(v) > 4 else ''}" for k, v in kinds.items())
    M, rises = model(P, N, pd, nd, shift); changed += rises + aside(P, N, pd, nd, shift)
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
    if M:
        print('the model changed (on screen for as long as the city stands: look at each city from every side in both versions, then in the film where it shows it):')
        for id_, on, off, what in M: print(f"  {id_:28s} {on:8.2f}-{(off if off is not None else N['dur']):8.2f}  {', '.join(what)}")
        print(f"  node tools/eraview.mjs {nname} --eras {','.join(m[0] for m in M)}   and the same with {pname}")
    known = set(KINDS + ONE + SEEN + PACKED)
    rest = [k for k in sorted(P.keys() | N.keys()) if k not in known and json.dumps(P.get(k), sort_keys=True) != json.dumps(N.get(k), sort_keys=True)]
    if rest: print(f"changed and placed nowhere (a whole-film setting, or a kind filmdiff does not know yet): {', '.join(rest)}")
    spans = [[round(max(0, a - PAD), 2), round(min(N['dur'], b + PAD), 2)] for a, b, _ in ch]
    if ch: print('compare the changed stretches with the previous version, line by line, all in one command:')
    if ch: print(f'  uv run python -I tools/rangecheck.py {nname} ' + ' '.join(f'--from {a:.2f} --to {b:.2f}' for a, b in spans) + f' --against {pname}')
    if out_json: json.dump({'previous': pname, 'this': nname, 'stretches': spans, 'what': [said(ws) for _, _, ws in ch],
                            'farther': [{'line': i_, 't': t_, 'before': round(do, 4), 'now': round(dn, 4)} for i_, t_, do, dn in far],
                            'model': [{'city': id_, 'on': on, 'off': off, 'what': what} for id_, on, off, what in M], 'rest': rest}, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()

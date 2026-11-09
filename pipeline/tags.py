"""Tag layout (docs/STAGING.md 9h): every tag on the map (pins and place names) is a dot, a pole straight up and a small box on
the pole. Compile picks each tag's pole length and box side once per stretch of time it shows, so that tags shown together do
not cover each other and keep clear of the subtitles, the readout, the locator and the timeline; the engine (overlay.js tag)
draws what is chosen. Screen sizes follow overlay.js TAG (name 27 px, second line 21 px, pad 14, boxes 42 / 68 high). A tag
whose anchor sits too high for a box above it hangs below it (a negative length). Obstacles at a moment (an arrow's or route's
name, a picture card and its caption) are kept clear as the fixed furniture is; a tag the city lays out itself (fixed) is only
kept clear of."""
import math, re

W, H = 1920, 1080
SUBTOP = H - 145
TOP = 140   # the timeline and the one identity line above it (overlay.js LTOP)
UI = [(0, SUBTOP - 10, W, H), (60, 380, 820, 880), (1500, 660, 1840, 945), (0, 0, W, TOP)]   # subtitles, readout, locator, timeline and identity
LENS = (70, 110, 150, 190, 240, 300, 360)   # the pole's length up to the box
DOWN = (-90, -140)                         # hanging below the anchor, where no box fits above
HIT, POLE, FURN, UNDRAWN = 12, 2, 12, 1e5   # costs: a box over a box, a pole under a box, a box over furniture, a moment the tag cannot be drawn
CJK = re.compile(r'[　-鿿豈-﫿]')


def text_w(s, px, ls=0.0):
    """estimated width of a line in the overlay's fonts"""
    if not s: return 0.0
    return sum(px if CJK.match(ch) else .56 * px for ch in s) + ls * len(s)


def box_of(sx, sy, L, left, w, h):
    """the box, the pole and the pole's drawn length for a tag anchored at (sx, sy): as overlay.js tag() places them (L < 0:
    hanging below); a pole under 24 px is not drawn"""
    if L >= 0:
        top = max(min(sy - L - h, SUBTOP - 14 - h), TOP); pole, n = (sx - 2, top, sx + 2, sy), sy - top - h
    else:
        top = min(max(sy - L, TOP), SUBTOP - 14 - h); pole, n = (sx - 2, sy, sx + 2, top + h), top - sy
    x0 = sx - w if left else sx
    return (x0, top, x0 + w, top + h), pole, n


def overlap(a, b):
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(0.0, min(a[3], b[3]) - max(a[1], b[1]))


def layout(tags, project, step=.25, obstacles=None):
    """tags: [{'id', 'pos': (x, y, z) model, 'spans': [(t0, t1), ...], 'visible': fn(t) -> bool, 'text', 'sub', 'fixed': (L, left)
    or None}] in priority order; project(t, X) -> (ndc x, ndc y, depth) or None; obstacles(t) -> screen boxes to keep clear at t.
    Returns {id: [[t0, t1, L, left], ...]} (one choice per span)."""
    placed = {}   # time slot -> boxes of the tags already laid out
    slot = lambda t: int(round(t / step))
    furn = {}
    def furniture(t):
        k = slot(t)
        if k not in furn: furn[k] = UI + (list(obstacles(k * step)) if obstacles else [])
        return furn[k]
    out = {}
    for tg in tags:
        w = max(text_w(tg['text'], 27, 1), text_w(tg.get('sub'), 21, .3)) + 28; h = 68 if tg.get('sub') else 42
        for t0, t1 in tg['spans']:
            samples = []
            t = t0
            while t <= t1 + 1e-6:
                q = project(t, tg['pos']) if tg['visible'](t) else None
                if q is not None and -1.2 < q[0] < 1.2 and -1.2 < q[1] < 1.2: samples.append((t, (q[0] * .5 + .5) * W, (1 - (q[1] * .5 + .5)) * H))
                t += step
            if not samples: continue
            if tg.get('fixed'):   # laid out by the city: kept as written, the others keep clear of it
                L, left = tg['fixed']; left = bool(left)
            else:
                best = None
                for L in LENS + DOWN:
                    for left in (False, True):
                        cost = 0.0
                        for t, sx, sy in samples:
                            box, pole, n = box_of(sx, sy, L, left, w, h)
                            others = placed.get(slot(t), ())
                            cost += HIT * sum(overlap(box, b) for b in others) + POLE * sum(overlap(pole, b) for b in others)
                            cost += FURN * sum(overlap(box, u) for u in furniture(t))
                            cost += 2 * (max(0, 40 - box[0]) + max(0, box[2] - (W - 40))) * h
                            cost += (160 * abs(L - 170) / 40 if L > 0 else 900) + (90 if left else 0) + (UNDRAWN if n < 24 else 0)
                        if best is None or cost < best[0]: best = (cost, L, left)
                _, L, left = best
            out.setdefault(tg['id'], []).append([round(t0, 2), round(t1, 2), L, left])
            for t, sx, sy in samples: placed.setdefault(slot(t), []).append(box_of(sx, sy, L, left, w, h)[0])
    return out

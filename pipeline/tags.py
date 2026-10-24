"""Tag layout (docs/STAGING.md 9h): every tag on the map (pins and place names) is a dot, a pole straight up and a small box on
the pole. Compile picks each tag's pole length and box side once per stretch of time it shows, so that tags shown together do
not cover each other and keep clear of the subtitles, the readout, the locator and the timeline; the engine (overlay.js tag)
draws what is chosen. Screen sizes follow overlay.js TAG (name 20 px, second line 14 px)."""
import math, re

W, H = 1920, 1080
SUBTOP = H - 145
UI = [(0, SUBTOP - 10, W, H), (60, 400, 640, 800), (1500, 680, 1840, 945), (0, 0, W, 125)]   # subtitles, readout, locator, timeline
LENS = (110, 150, 190, 240, 300)
CJK = re.compile(r'[　-鿿豈-﫿]')


def text_w(s, px, ls=0.0):
    """estimated width of a line in the overlay's fonts"""
    if not s: return 0.0
    return sum(px if CJK.match(ch) else .56 * px for ch in s) + ls * len(s)


def box_of(sx, sy, L, left, w, h):
    """the box and the pole for a tag anchored at (sx, sy): as overlay.js tag() places them"""
    top = min(sy - L - h, SUBTOP - 14 - h); top = max(top, 128)
    x0 = sx - w if left else sx
    return (x0, top, x0 + w, top + h), (sx - 2, top, sx + 2, sy)


def overlap(a, b):
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(0.0, min(a[3], b[3]) - max(a[1], b[1]))


def layout(tags, project, step=.25):
    """tags: [{'id', 'pos': (x, y, z) model, 'spans': [(t0, t1), ...], 'visible': fn(t) -> bool, 'text', 'sub'}] in priority
    order; project(t, X) -> (ndc x, ndc y, depth) or None. Returns {id: [[t0, t1, L, left], ...]} (one choice per span)."""
    placed = {}   # time slot -> boxes of the tags already laid out
    slot = lambda t: int(round(t / step))
    out = {}
    for tg in tags:
        w = max(text_w(tg['text'], 20, 1), text_w(tg.get('sub'), 14, .3)) + 22; h = 50 if tg.get('sub') else 32
        for t0, t1 in tg['spans']:
            samples = []
            t = t0
            while t <= t1 + 1e-6:
                q = project(t, tg['pos']) if tg['visible'](t) else None
                if q is not None and -1.2 < q[0] < 1.2 and -1.2 < q[1] < 1.2: samples.append((t, (q[0] * .5 + .5) * W, (1 - (q[1] * .5 + .5)) * H))
                t += step
            if not samples: continue
            best = None
            for L in LENS:
                for left in (False, True):
                    cost = 0.0
                    for t, sx, sy in samples:
                        box, pole = box_of(sx, sy, L, left, w, h)
                        others = placed.get(slot(t), ())
                        cost += 4 * sum(overlap(box, b) for b in others) + sum(overlap(pole, b) for b in others)
                        cost += 2 * sum(overlap(box, u) for u in UI)
                        cost += 2 * (max(0, 40 - box[0]) + max(0, box[2] - (W - 40))) * h
                        cost += 160 * abs(L - 170) / 40 + (90 if left else 0)
                    if best is None or cost < best[0]: best = (cost, L, left)
            _, L, left = best
            out.setdefault(tg['id'], []).append([round(t0, 2), round(t1, 2), L, left])
            for t, sx, sy in samples: placed.setdefault(slot(t), []).append(box_of(sx, sy, L, left, w, h)[0])
    return out

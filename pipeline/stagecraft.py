"""Stagecraft: when and how a change is shown (docs/STAGING.md). Everything here is computed once, in compile, and written
into film.json as times and sampled curves; the engine and tools/camcheck.py only interpolate them (one source of truth).

  camera     the film's camera from its compiled keys (the engine's track(), without the hand-held drift)
  settle     the first moment the camera holds a place in view long enough for a change to be watched there
  mode       how a change is lit: an expanding ring (a large area), a line sweeping across (a staged sweep) or a band of
             light scanning across a small area inside its outline (a village, a quarter)
  curves     ring radius over time, paced on screen: slow while the ring is inside the frame, faster once it is out of it

Model frame: x east, z south, y up; camera keys [tx, ty, tz, az, el, d, fov] as compile writes them."""
import math

ASPECT = 16 / 9


# ------------------------------------------------------------------ the engine's interpolation (core/lib.js monotone, track)
def monotone(keys):
    """Fritsch-Carlson monotone cubic through [(t, v), ...], exactly as core/lib.js"""
    n = len(keys); xs = [k[0] for k in keys]; ys = [k[1] for k in keys]
    if n == 1: return lambda t: ys[0]
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [0.0] * n; m[0] = d[0]; m[n - 1] = d[n - 2]
    for i in range(1, n - 1): m[i] = 0.0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2
    for i in range(n - 1):
        if d[i] == 0: m[i] = m[i + 1] = 0.0; continue
        a, b = m[i] / d[i], m[i + 1] / d[i]; s = a * a + b * b
        if s > 9: k = 3 / math.sqrt(s); m[i] = k * a * d[i]; m[i + 1] = k * b * d[i]
    def f(t):
        if t <= xs[0]: return ys[0]
        if t >= xs[-1]: return ys[-1]
        i = 0
        while t > xs[i + 1]: i += 1
        h = xs[i + 1] - xs[i]; u = (t - xs[i]) / h; u2 = u * u; u3 = u2 * u
        return (2 * u3 - 3 * u2 + 1) * ys[i] + (u3 - 2 * u2 + u) * h * m[i] + (-2 * u3 + 3 * u2) * ys[i + 1] + (u3 - u2) * h * m[i + 1]
    return f


class Camera:
    """the compiled camera: at(t) -> (position, target, fov degrees); keys [[t, [tx, ty, tz, az, el, d, fov]], ...]"""
    def __init__(self, keys, fov=30):
        dim = max(len(k[1]) for k in keys)
        keys = [[t, list(v) + [fov] * (dim - len(v))] for t, v in keys]
        self.fs = [monotone([(t, v[j]) for t, v in keys]) for j in range(dim)]

    def state(self, t):
        """the interpolated key at t: [tx, ty, tz, az, el, d, fov]"""
        return [f(t) for f in self.fs][:7]

    def at(self, t):
        tx, ty, tz, az, el, d, fov = [f(t) for f in self.fs][:7]
        a, e = math.radians(az), math.radians(el)
        p = (tx + d * math.sin(a) * math.cos(e), ty + d * math.sin(e), tz + d * math.cos(a) * math.cos(e))
        return p, (tx, ty, tz), fov, d

    def project(self, t, X):
        """model point -> (ndc x, ndc y, depth) or None behind the camera; ndc in -1..1 across the 16:9 frame"""
        p, g, fov, _ = self.at(t)
        f = [g[i] - p[i] for i in range(3)]; L = math.sqrt(sum(v * v for v in f)) or 1e-9; f = [v / L for v in f]
        r = [f[1] * 0 - f[2] * 1, f[2] * 0 - f[0] * 0, f[0] * 1 - f[1] * 0]   # f x up(0,1,0)
        rl = math.sqrt(sum(v * v for v in r)) or 1e-9; r = [v / rl for v in r]
        u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
        V = [X[i] - p[i] for i in range(3)]; z = sum(V[i] * f[i] for i in range(3))
        if z <= 1e-6: return None
        th = math.tan(math.radians(fov) / 2)
        return (sum(V[i] * r[i] for i in range(3)) / (z * th * ASPECT), sum(V[i] * u[i] for i in range(3)) / (z * th), z)

    def view_radius(self, t, X):
        """half the frame's width (model units) at the depth of X: how far a ring can grow and still be on screen"""
        q = self.project(t, X); _, _, fov, _ = self.at(t)
        if q is None: return 0.0
        return q[2] * math.tan(math.radians(fov) / 2) * ASPECT


# ------------------------------------------------------------------ when the viewer can watch a place
def holding(cam, centre, radius, t, step=.1, frame=.6, qmin=.12, dmove=.15, dpush=.5, tmove=.10, hidden=None):
    """the camera holds a place at t: `centre` (model xyz) inside the central `frame` of the picture, the place at least `qmin`
    of the frame tall (radius / half-height), the target still (moving under `tmove` of the distance per second). The camera
    may still be pushing in (distance shrinking up to `dpush` per second: the place only grows on screen) but not pulling
    out faster than `dmove`. hidden(t): the picture is covered (a full-screen clip), so nothing is held."""
    if hidden and hidden(t): return False
    q = cam.project(t, centre)
    if q is None or abs(q[0]) > frame or abs(q[1]) > frame: return False
    _, _, fov, _ = cam.at(t)
    if radius / (q[2] * math.tan(math.radians(fov) / 2)) < qmin: return False
    _, g0, _, d0 = cam.at(t); _, g1, _, d1 = cam.at(t + step)
    if (d1 - d0) / step > dmove * d0 or (d0 - d1) / step > dpush * d0: return False
    if math.dist(g0, g1) / step > tmove * d0: return False
    return True


def settle(cam, centre, radius, t_from, t_to, need=2.0, step=.1, **kw):
    """the first t in [t_from, t_to - need] from which the camera holds the place (holding) for `need` seconds; None when
    there is no such moment"""
    ok = lambda t: holding(cam, centre, radius, t, step, **kw)
    n = int(round(need / step)); t = t_from; run = 0; start = None
    while t <= t_to + 1e-9:
        if ok(t):
            if run == 0: start = t
            run += 1
            if run > n: return round(start, 3)
        else: run = 0
        t += step
    return None


def settle_report(cam, centre, radius, t, step=.1):
    """why the camera does or does not hold a place at t (for compile's error message)"""
    q = cam.project(t, centre)
    if q is None: return f'{t:7.2f}s  behind the camera'
    _, g0, fov, d0 = cam.at(t); _, g1, _, d1 = cam.at(t + step)
    return (f'{t:7.2f}s  frame x {q[0]:+.2f} y {q[1]:+.2f}  size {radius / (q[2] * math.tan(math.radians(fov) / 2)):.2f}  '
            f'dist {(d1 - d0) / step / d0:+.2f}/s  target {math.dist(g0, g1) / step / d0:.2f}/s  {"holds" if holding(cam, centre, radius, t, step) else "-"}')


def size_on_screen(cam, t, centre, radius):
    """the place's diameter as a fraction of the frame's height at t (0 behind the camera)"""
    q = cam.project(t, centre)
    if q is None: return 0.0
    _, _, fov, _ = cam.at(t)
    return radius / (q[2] * math.tan(math.radians(fov) / 2))


# ------------------------------------------------------------------ how a change is lit
def choose_mode(cam, t, centre, extent_m, scale, ring_m=1000.0, ring_q=.35):
    """'ring' for a large area (over `ring_m` metres, or over `ring_q` of the frame's half-width on screen), else 'scan'"""
    if extent_m >= ring_m: return 'ring'
    vr = cam.view_radius(t, centre)
    return 'ring' if vr > 0 and extent_m * scale / vr >= ring_q else 'scan'


def stage_duration(cam, t, centre, length_model, dur, min_dur, frames_per_s=1 / 3, ahead=1.5):
    """at least `min_dur`, and slow enough that the front crosses no more than `frames_per_s` of the frame's width per second,
    measured on the tightest view of the next `ahead` seconds (the camera may still be pushing in)"""
    vs = [cam.view_radius(t + k * .5, centre) for k in range(int(ahead / .5) + 1)]
    vs = [v for v in vs if v > 0]
    if not vs: return max(dur, min_dur)
    return max(dur, min_dur, (length_model / (2 * min(vs))) / frames_per_s)


# ------------------------------------------------------------------ ring curves, paced on screen
def ring_curve(t0, r_view, r_max, t_view=2.8, t_out=1.6, step=.1):
    """an expanding ring: inside the frame (to r_view) it takes t_view seconds, a quick start easing off; beyond the frame it
    accelerates to r_max in t_out seconds. [[t, R], ...]"""
    out = []
    r_view = min(r_view, r_max)
    n1 = max(2, int(round(t_view / step)))
    for i in range(n1 + 1):
        u = i / n1; out.append([round(t0 + u * t_view, 3), round(r_view * (.35 * u + .65 * (1 - (1 - u) ** 2)), 6)])
    if r_max > r_view * 1.01:
        n2 = max(2, int(round(t_out / step)))
        for i in range(1, n2 + 1):
            u = i / n2; out.append([round(t0 + t_view + u * t_out, 3), round(r_view + (r_max - r_view) * u * u, 6)])
    return out


def contract_curve(t0, r_max, r_view, dur, t_out=1.2, step=.1):
    """a contracting ring (a city taken back from its edge): from r_max sweeping into the frame (t_out, easing in), then on
    screen to 0 at a pace the eye can follow, easing out as it reaches the centre. [[t, R], ...]"""
    out = []; t_out = min(t_out, .35 * dur) if r_max > r_view * 1.05 else 0.0
    if t_out > 0:
        n = max(2, int(round(t_out / step)))
        for i in range(n): u = i / n; out.append([round(t0 + u * t_out, 3), round(r_max - (r_max - r_view) * u * u, 6)])
    rest = dur - t_out; n = max(2, int(round(rest / step))); r0 = min(r_view, r_max)
    for i in range(n + 1): u = i / n; out.append([round(t0 + t_out + u * rest, 3), round(r0 * (1 - u) ** 1.15, 6)])
    return out


def sweep_curve(t0, r0, r1, dur, step=.1):
    """a ring going from r0 to r1 (in or out) over dur seconds, easing in and out: a part of a city taken back while the rest
    stands (lose:), the ring stopping where the last of that part is. [[t, R], ...]"""
    n = max(2, int(round(dur / step)))
    return [[round(t0 + i / n * dur, 3), round(r0 + (r1 - r0) * (lambda u: u * u * (3 - 2 * u))(i / n), 6)] for i in range(n + 1)]


def ring_exit(cam, t, o, y, r_cap):
    """how far a ring round o (model x, z; ground height y) must grow to have left the frame at t: the farthest point of the
    ground the frame's edge sees (a ray above the horizon: r_cap, the plate's far corner)"""
    p, g, fov, _ = cam.at(t)
    f = [g[i] - p[i] for i in range(3)]; L = math.sqrt(sum(v * v for v in f)) or 1e-9; f = [v / L for v in f]
    r = [-f[2], 0.0, f[0]]; rl = math.hypot(r[0], r[2]) or 1e-9; r = [v / rl for v in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    th = math.tan(math.radians(fov) / 2); far = 0.0
    for k in range(16):   # round the frame's edge
        a = 2 * math.pi * k / 16; sx, sy = max(-1, min(1, 1.5 * math.cos(a))), max(-1, min(1, 1.5 * math.sin(a)))
        d = [f[i] + r[i] * sx * th * ASPECT + u[i] * sy * th for i in range(3)]
        if d[1] >= -1e-6: return r_cap
        s_ = (y - p[1]) / d[1]; far = max(far, math.hypot(p[0] + d[0] * s_ - o[0], p[2] + d[2] * s_ - o[1]))
    return min(far * 1.05, r_cap)


def curve_at(c, t):
    """linear interpolation in a sampled curve (clamped at both ends)"""
    if t <= c[0][0]: return c[0][1]
    if t >= c[-1][0]: return c[-1][1]
    lo, hi = 0, len(c) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if c[mid][0] <= t: lo = mid
        else: hi = mid
    (a, ra), (b, rb) = c[lo], c[hi]
    return ra + (rb - ra) * (t - a) / ((b - a) or 1e-9)


# ------------------------------------------------------------------ camera moves the algorithm adds
def move_time(v0, v1, speed=.35, t_min=1.8, t_max=9.0):
    """seconds a move between two camera keys [tx, ty, tz, az, el, d, fov] takes when nothing on screen should travel faster
    than `speed` frames a second: the target's travel (frame widths at the mean distance), the zoom (doublings), the turn and
    the tilt"""
    x0, y0, z0, a0, e0, d0 = v0[:6]; x1, y1, z1, a1, e1, d1 = v1[:6]
    fov = v0[6] if len(v0) > 6 else 30
    dm = math.sqrt(d0 * d1); wide = 2 * dm * math.tan(math.radians(fov) / 2) * ASPECT
    frames = math.dist((x0, y0, z0), (x1, y1, z1)) / wide + abs(math.log(d1 / d0)) / math.log(2) * .5 + abs(a1 - a0) / 120 + abs(e1 - e0) / 60
    return max(t_min, min(t_max, frames / speed))


def look_view(centre, radius, az, el=34.0, fov=30.0, size=.55):
    """a key that frames a place (centre model xyz, radius) at `size` of the frame's height"""
    d = radius / (size * math.tan(math.radians(fov) / 2))
    return [centre[0], centre[1], centre[2], az, el, d, fov]


def unwrap(az, ref):
    """az moved by whole turns to within 180 degrees of ref (a camera never spins the long way round)"""
    return az + 360 * round((ref - az) / 360)


# ------------------------------------------------------------------ framing: what a single camera key keeps in the picture
def view_of(v):
    """a camera standing still on one key [tx, ty, tz, az, el, d, fov]"""
    return Camera([[0.0, list(v)]], v[6] if len(v) > 6 else 30)


def in_frame(v, pts, mx=.9, my=.85):
    """every point (model xyz) inside the frame of key v, `mx`/`my` of the half-width/half-height"""
    cam = view_of(v)
    for X in pts:
        q = cam.project(0.0, X)
        if q is None or abs(q[0]) > mx or abs(q[1]) > my: return False
    return True


def circle(o, r, y, n=36):
    """points on a ring of radius r round o (model x, z) at height y"""
    return [(o[0] + r * math.cos(2 * math.pi * i / n), y, o[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def fit_radius(v, o, y, mx=.9, my=.85, r_hi=20.0):
    """the largest ring round o (model x, z, at height y) that key v shows whole"""
    lo, hi = 0.0, r_hi
    for _ in range(40):
        mid = (lo + hi) / 2
        if in_frame(v, circle(o, mid, y), mx, my): lo = mid
        else: hi = mid
    return lo


def fit_distance(v, pts, mx=.9, my=.85, d_lo=.01, d_hi=20.0):
    """the nearest distance at which key v (its target, azimuth, elevation and lens kept) shows every point: v with that d"""
    w = list(v)
    if in_frame(w[:5] + [d_lo] + w[6:], pts, mx, my): return w[:5] + [d_lo] + w[6:]
    lo, hi = math.log(d_lo), math.log(d_hi)
    for _ in range(40):
        mid = (lo + hi) / 2
        if in_frame(w[:5] + [math.exp(mid)] + w[6:], pts, mx, my): hi = mid
        else: lo = mid
    return w[:5] + [math.exp(hi)] + w[6:]

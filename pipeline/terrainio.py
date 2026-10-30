"""One way to read the terrain everywhere (prep, compile, citygen, clipcheck) so buildings and the engine's plate agree.
data/terrain16.png: 16-bit relief in two channels (R = high byte, G = low byte) over terrain.json min..max; data/terrain.png is
the 8-bit fallback. Sampling is bilinear, like the engine's ground(); the plate itself is a mesh through it (plate_mesh)."""
import json, math, os
import numpy as np
from PIL import Image


def load(D, true=False):
    """-> (metres above the box minimum as float32 HxW, terrain.json dict) or (None, None). The field the plate is drawn from
    (its fine relief scaled down so it shows at its true height: terrain.py), or with true=True the relief as measured
    (terrain_true16.png, for what quotes metres; an older build without it: the plate's)"""
    tj_p = os.path.join(D, 'build', 'data', 'terrain.json')   # (pipeline/layout.py)
    if not os.path.exists(tj_p): return None, None
    tj = json.load(open(tj_p)); span = tj['max_m'] - tj['min_m']
    p16 = os.path.join(D, 'build', 'data', 'terrain16.png')
    if true and os.path.exists(os.path.join(D, 'build', 'data', 'terrain_true16.png')): p16 = os.path.join(D, 'build', 'data', 'terrain_true16.png')
    if os.path.exists(p16):
        a = np.asarray(Image.open(p16).convert('RGB')).astype(np.float32)
        return (a[..., 0] * 256 + a[..., 1]) / 65535.0 * span, tj
    return np.asarray(Image.open(os.path.join(D, 'build', 'data', 'terrain.png')).convert('L')).astype(np.float32) / 255.0 * span, tj


def load_context(D):
    """the land beyond the plate (terrain.py, terrain.context) -> (metres above the plate's minimum as float32 HxW, context.json
    dict) or (None, None); row 0 at the north, the grid spans context.json rect_model"""
    cj_p = os.path.join(D, 'build', 'data', 'context.json'); tj_p = os.path.join(D, 'build', 'data', 'terrain.json')
    if not (os.path.exists(cj_p) and os.path.exists(tj_p)): return None, None
    cj = json.load(open(cj_p)); ref = json.load(open(tj_p))['min_m']
    a = np.asarray(Image.open(os.path.join(D, 'build', 'data', 'context16.png')).convert('RGB')).astype(np.float32)
    return (a[..., 0] * 256 + a[..., 1]) / 65535.0 * (cj['max_m'] - cj['min_m']) + cj['min_m'] - ref, cj


def gauss(a, sigma):
    """a gaussian blur of sigma cells along both axes (terrain.py splits the relief in two scales by it)"""
    r = int(3 * sigma + 1); x = np.arange(-r, r + 1); k = np.exp(-x * x / (2.0 * sigma * sigma)); k /= k.sum()
    for ax in (0, 1):
        p_ = np.pad(a, [(r, r) if i == ax else (0, 0) for i in range(2)], mode='edge')
        a = np.apply_along_axis(lambda v: np.convolve(v, k, mode='valid'), ax, p_)
    return a.astype(np.float32)


def bilinear(arr, u, v):
    """sample arr at plate uv (0..1, v down), the same way the engine does"""
    h, w = arr.shape
    x = min(max(u, 0.0), 1.0) * (w - 1); y = min(max(v, 0.0), 1.0) * (h - 1)
    i0 = min(w - 2, int(x)); j0 = min(h - 2, int(y)); fu = x - i0; fv = y - j0
    a = arr[j0, i0] * (1 - fu) + arr[j0, i0 + 1] * fu; b = arr[j0 + 1, i0] * (1 - fu) + arr[j0 + 1, i0 + 1] * fu
    return float(a * (1 - fv) + b * fv)


NX = 640   # the plate mesh's cells across (studio.js plateGeometry)


def plate_mesh(arr, PW, PD, nx=NX):
    """the plate as the engine draws it (studio.js plateGeometry): an nx-cell mesh over the PW x PD plate (model units) through
    the heightfield, two flat triangles a cell (THREE.PlaneGeometry: the diagonal from a cell's south-west corner to its
    north-east one). Where the ground dips between the mesh's corners the plate stands above the sampled ground: anything thin
    is laid on this. Returns f(x, z) (model x east, z south) -> arr's units."""
    nz = int(math.floor(nx * PD / PW + .5)); h, w = arr.shape
    xs = np.clip(-(PW + .1) / 2 + np.arange(nx + 1) * (PW + .1) / nx, -PW / 2, PW / 2)
    zs = np.clip(-(PD + .1) / 2 + np.arange(nz + 1) * (PD + .1) / nz, -PD / 2, PD / 2)
    X = np.clip(xs / PW + .5, 0, 1) * (w - 1); Y = np.clip(zs / PD + .5, 0, 1) * (h - 1)
    i0 = np.minimum(w - 2, X.astype(int)); j0 = np.minimum(h - 2, Y.astype(int)); fu = (X - i0)[None, :]; fv = (Y - j0)[:, None]
    A, B = arr[j0[:, None], i0[None, :]], arr[j0[:, None], i0[None, :] + 1]
    C, D = arr[j0[:, None] + 1, i0[None, :]], arr[j0[:, None] + 1, i0[None, :] + 1]
    V = (A * (1 - fu) + B * fu) * (1 - fv) + (C * (1 - fu) + D * fu) * fv   # vertex heights [row (south), column (east)]
    def f(x, z):
        gx = (x + (PW + .1) / 2) / (PW + .1) * nx; gz = (z + (PD + .1) / 2) / (PD + .1) * nz
        ix = min(nx - 1, max(0, int(gx))); iz = min(nz - 1, max(0, int(gz))); a, b = gx - ix, gz - iz
        h00, h10, h01, h11 = V[iz, ix], V[iz, ix + 1], V[iz + 1, ix], V[iz + 1, ix + 1]
        if a + b <= 1: return float(h00 + (h10 - h00) * a + (h01 - h00) * b)
        return float(h11 + (h01 - h11) * (1 - a) + (h10 - h11) * (1 - b))
    cw, cd = (PW + .1) / nx, (PD + .1) / nz   # a mesh cell, model units

    def many(x, z):   # f over arrays of points
        gx = (x + (PW + .1) / 2) / (PW + .1) * nx; gz = (z + (PD + .1) / 2) / (PD + .1) * nz
        ix = np.clip(gx.astype(int), 0, nx - 1); iz = np.clip(gz.astype(int), 0, nz - 1); a, b = gx - ix, gz - iz
        h00, h10, h01, h11 = V[iz, ix], V[iz, ix + 1], V[iz + 1, ix], V[iz + 1, ix + 1]
        return np.where(a + b <= 1, h00 + (h10 - h00) * a + (h01 - h00) * b, h11 + (h01 - h11) * (1 - a) + (h10 - h11) * (1 - b))

    def lowest(ring):
        """the lowest point of the plate under a footprint (a ring of model x, z points). Each mesh triangle is flat, so it lies
        at a corner of the ring, a mesh corner inside the ring, or where a ring edge crosses a mesh line (the edges are walked a
        quarter cell at a time, which finds it to within a few centimetres)"""
        r = np.asarray(ring, float); pts = [r]
        for p, q in zip(r, np.roll(r, -1, axis=0)):
            n = int(max(abs(q[0] - p[0]) / cw, abs(q[1] - p[1]) / cd) * 4)
            if n: pts.append(p + (q - p) * (np.arange(1, n + 1) / (n + 1))[:, None])
        pts = np.vstack(pts); lo = float(many(pts[:, 0], pts[:, 1]).min())
        (x0, z0), (x1, z1) = r.min(axis=0), r.max(axis=0)
        ix = np.arange(max(0, math.ceil((x0 + (PW + .1) / 2) / cw)), min(nx, math.floor((x1 + (PW + .1) / 2) / cw)) + 1)
        iz = np.arange(max(0, math.ceil((z0 + (PD + .1) / 2) / cd)), min(nz, math.floor((z1 + (PD + .1) / 2) / cd)) + 1)
        if len(ix) and len(iz):
            import shapely
            gx_, gz_ = np.meshgrid(-(PW + .1) / 2 + ix * cw, -(PD + .1) / 2 + iz * cd)
            inside = shapely.contains_xy(shapely.Polygon(r), gx_, gz_)
            if inside.any(): lo = min(lo, float(V[np.ix_(iz, ix)][inside].min()))
        return lo
    f.lowest = lowest
    return f


def write16(D, out_m, lo, hi, name='terrain16.png'):
    """write the 16-bit relief (metres) as R/G"""
    q = np.round((out_m - lo) / max(1e-6, hi - lo) * 65535).clip(0, 65535).astype(np.uint32)
    rgb = np.zeros((*q.shape, 3), np.uint8); rgb[..., 0] = (q >> 8).astype(np.uint8); rgb[..., 1] = (q & 255).astype(np.uint8)
    Image.fromarray(rgb, 'RGB').save(os.path.join(D, 'build', 'data', name))

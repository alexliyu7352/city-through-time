"""The optics of one frame, measured: what makes a picture read as a model on a table or as a map (the colour film, film.look
kind mini; a still of ours or a reference frame alike). By horizontal bands of the frame, from its top:
  detail  the band's finest detail against all its detail (the energy a 1 px blur takes over what a 16 px one takes), as a share
          of the frame's sharpest band: 1 is in focus, under .5 visibly soft. The sharp band is where it is .5 or more.
          It is relative and depends a little on what the band shows (dense far houses read sharper than a near field).
  blur    with --edge: the defocus itself, sigma of a Gaussian in px of a 1080 picture (a rendered edge in focus measures about
          .5-.8; an edge's 10-90 % width is 2.56 sigma), from the profile across a drawn edge fitted by a blurred step: draw
          edges that run through the depth (a coast, a wall, a road's edge, a row of roofs) and every band they cross gets a value
  S, V    the mean saturation and value (HSV, 0-1) of the band, and of its greens alone (Sg, Vg: hue 60-170 degrees, grass
          and woods; the same material near and far, so aerial perspective shows as Sg and Vg falling toward the top)
With --cam (the camera the page reports, main.js window.CAMAT: position, target, vertical fov), the flat ground each band shows:
  z/s     its distance along the view over the focus distance (the target's): the depth range the lens has to work on
  size    how big a thing there is against the same thing at the target (s/z): the near-to-far size ratio of the frame
  house   with --scale (model units per metre): the pixels of a house --house metres wide (default 10) at that band
usage: python -I tools/lenscheck.py <image> [--mask x0,y0,x1,y1 ...] [--edge x0,y0,x1,y1[,x2,y2 ...] ...] [--bands 12]
       [--cam px,py,pz,tx,ty,tz,fov] [--scale k] [--house m] [--json out.json]
--mask: rectangles left out, in pixels of the image (an overlay's text, a logo, the sky); a band mostly masked reports nothing."""
import argparse, json, math, sys
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.optimize import curve_fit
from scipy.special import erf


def detail(g, keep, a, b):
    """the band's finest detail against all its detail: the energy the picture loses to a 1 px blur over what it loses to a 16 px
    one (falls as the band blurs; a flat band has none)"""
    k = keep[a:b]
    if k.mean() < .25: return None
    d1 = (g[a:b] - ndimage.gaussian_filter(g, 1.0)[a:b])[k]; d16 = (g[a:b] - ndimage.gaussian_filter(g, 16.0)[a:b])[k]
    e = float((d16 * d16).mean())
    return float((d1 * d1).mean()) / e if e > 1e-7 else None


def step(x, a, b, x0, sg): return a + b * .5 * (1 + erf((x - x0) / (math.sqrt(2) * max(abs(sg), .05))))


def edge_blur(g, pts, every=12, half=24):
    """the blur along a drawn edge (a polyline that follows a step of light): every `every` px along it, the profile across it
    fitted by a blurred step (erf); (y, sigma in px of this picture, the step's contrast) where the step is clear"""
    out = []; P = np.array(pts, float).reshape(-1, 2)
    for p0, p1 in zip(P[:-1], P[1:]):
        L = np.linalg.norm(p1 - p0); t = (p1 - p0) / L; n = np.array([-t[1], t[0]])
        for u in np.arange(every / 2, L, every):
            c = p0 + t * u; x = np.arange(-half, half + .01, .25); q = c[None, :] + x[:, None] * n[None, :]
            prof = ndimage.map_coordinates(g, [q[:, 1], q[:, 0]], order=1)
            i = int(np.argmax(np.abs(np.gradient(prof))))
            try: (a, b, x0, sg), _ = curve_fit(step, x, prof, p0=[prof[0], prof[-1] - prof[0], x[i], 1.0], maxfev=4000)
            except Exception: continue
            res = float(np.sqrt(np.mean((step(x, a, b, x0, sg) - prof) ** 2)))
            if abs(b) > .06 and abs(x0) < half - 4 and res < .2 * abs(b) and abs(sg) < half / 2.5:   # (a clear, single step)
                out.append((float(c[1]), abs(float(sg)), abs(float(b))))
    return out


def ground(cam, H, rows):
    """for each image row (through the frame's middle): the distance along the view to the flat ground at the target's height,
    over the target's; None where the row looks above the horizon"""
    px, py, pz, tx, ty, tz, fov = cam
    p = np.array([px, py, pz]); f = np.array([tx, ty, tz]) - p; s = float(np.linalg.norm(f)); f /= s
    r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f); th = math.tan(math.radians(fov) / 2); out = []
    for y in rows:
        d = f + (1 - 2 * (y + .5) / H) * th * u   # (not normalised: its component along f is 1, so k is the depth along the view)
        out.append((ty - py) / d[1] / s if d[1] < -1e-9 else None)
    return out, s, th


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('image'); ap.add_argument('--mask', action='append', default=[]); ap.add_argument('--edge', action='append', default=[])
    ap.add_argument('--bands', type=int, default=12); ap.add_argument('--cam'); ap.add_argument('--scale', type=float)
    ap.add_argument('--house', type=float, default=10.0); ap.add_argument('--json')
    A = ap.parse_args()
    im = Image.open(A.image).convert('RGB'); W, H = im.size; k1080 = 1080 / H
    rgb = np.asarray(im, dtype=np.float32) / 255
    g = rgb @ np.array([.2126, .7152, .0722], dtype=np.float32)
    hsv = np.asarray(im.convert('HSV'), dtype=np.float32) / 255
    keep = np.ones((H, W), bool)
    for m in A.mask:
        x0, y0, x1, y1 = (int(float(v)) for v in m.split(',')); keep[max(y0, 0):y1, max(x0, 0):x1] = False
    green = keep & (hsv[..., 0] * 360 > 60) & (hsv[..., 0] * 360 < 170) & (hsv[..., 1] > .15)
    edges = np.linspace(0, H, A.bands + 1).astype(int); pairs = list(zip(edges[:-1], edges[1:]))
    det = [detail(g, keep, a, b) for a, b in pairs]; dmax = max((d for d in det if d is not None), default=None)
    fits = [e for spec in A.edge for e in edge_blur(g, [float(v) for v in spec.split(',')])]
    cam = [float(v) for v in A.cam.split(',')] if A.cam else None
    zs, s, th = ground(cam, H, [(a + b) // 2 for a, b in pairs]) if cam else ([None] * len(pairs), None, None)
    rows = []
    for i, (a, b) in enumerate(pairs):
        r = {'y0': int(a), 'y1': int(b)}; kp = keep[a:b]
        if det[i] is not None and dmax: r['detail'] = round(det[i] / dmax, 2)
        fb = [sg for y, sg, _ in fits if a <= y < b]
        if fb: r['blur'] = round(float(np.median(fb)) * k1080, 2); r['n'] = len(fb)
        if kp.mean() > .25:
            h = hsv[a:b][kp]; r['S'] = round(float(h[:, 1].mean()), 3); r['V'] = round(float(h[:, 2].mean()), 3)
            gg = green[a:b]
            if gg.sum() > 500: hg = hsv[a:b][gg]; r['Sg'] = round(float(hg[:, 1].mean()), 3); r['Vg'] = round(float(hg[:, 2].mean()), 3)
        if zs[i] is not None:
            r['z/s'] = round(zs[i], 3); r['size'] = round(1 / zs[i], 3)
            if A.scale: r['house'] = round(A.house * A.scale / (2 * zs[i] * s * th) * H, 1)
        rows.append(r)
    dd = [r for r in rows if 'detail' in r]
    out = {'image': A.image, 'size': [W, H], 'bands': rows, 'sharp_share': round(sum(r['y1'] - r['y0'] for r in dd if r['detail'] >= .5) / max(sum(r['y1'] - r['y0'] for r in dd), 1), 3) if dd else None}
    cols = [('detail', 6), ('blur', 5), ('n', 4), ('S', 5), ('V', 5), ('Sg', 5), ('Vg', 5)] + ([('z/s', 6), ('size', 5)] if cam else []) + ([('house', 6)] if cam and A.scale else [])
    print(A.image); print(f"{'rows':>11} " + ' '.join(f'{k:>{w}}' for k, w in cols))
    for r in rows: print(f"{r['y0']:>5}-{r['y1']:<5} " + ' '.join(f"{r[k]:>{w}}" if k in r else ' ' * (w - 1) + '-' for k, w in cols))
    print(f"sharp band (detail >= .5): {out['sharp_share']} of the measured height")
    if A.json: json.dump(out, open(A.json, 'w'), indent=1)


if __name__ == '__main__':
    sys.exit(main())

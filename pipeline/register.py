"""Old maps and plans into the model's coordinates (docs/MODEL.md "Lay out blocks from an old map"). A source picture is registered
(a GeoTIFF that carries its own registration, control points read off it, or a scale and one known point); points read off it in
pixels become lon/lat; a traced feature file becomes the GeoJSON `city.trace` reads; an outline traced on it becomes a landmark of
the classes; any GeoJSON can be drawn back over the picture to compare by eye. Every city laid from an old map, an excavation
plan or a figure in a paper needs these steps, and done by hand they went wrong: a picture whose y runs down fitted as if it ran
up (mirrored), metres per degree taken as 111,320 everywhere, a raster in a projected CRS read as if it were lon/lat.
Everything is fitted and measured in the city's own UTM (geo.Frame), the metres citygen builds in.

usage: python -I pipeline/register.py trace <city folder> <trace.yaml> [--out research/<name>.geojson] [--overlay <picture>.png]
       python -I pipeline/register.py selftest      (each way of registering against a known answer, a mirrored picture caught)
trace.yaml:
  source: research/maps/plan.tif                       # a GeoTIFF; or a picture and control points read off it:
  # source: {image: research/maps/fig.png, controls: [{id, pixel: [x, y], lonlat: [lon, lat]}, ..], method: similarity}
  #   method: similarity (two points or more: scale, turn, shift), affine (three or more: it may also shear), the image's y down
  # source: {image: ..., origin: {pixel: [x, y], lonlat: [lon, lat]}, m_per_px: 0.5, north_deg: 0}   # a plan with a scale bar;
  #   north_deg: how far its north arrow turns from straight up, clockwise
  features:                                            # one per traced shape, in the picture's pixels
    - { id: north_wall, kind: wall, pixels: [[x, y], ..], h_m: 8, provenance: {basis: "..."} }
  kind: wall / block (polygons), street (a line), landmark (a point, or a polygon: citygen takes its centre, size and bearing);
  every other key is that entry's (lot, typ, w_m, type, ...); provenance: {..} rides along and the model ignores it.
It writes the GeoJSON (each feature keeps its source pixels under provenance), prints the registration (metres per pixel; for
control points each one's residual and its error when left out of the fit) and, with --overlay, draws the features over the
picture."""
import json, math, os, sys

import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon, shape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import Frame

LINE_KINDS = {'street', 'lane'}


class Source:
    """a registered picture: pixels (x right, y down) <-> the city's UTM metres <-> lon/lat"""

    def __init__(self, F, to_utm, to_px, report):
        self.F, self._utm, self._px, self.report = F, to_utm, to_px, report

    def utm(self, px): return tuple(float(v) for v in self._utm(np.asarray(px, float)))
    def lonlat(self, px): return self.F.to_wgs.transform(*self.utm(px))
    def pixel(self, lonlat): return tuple(float(v) for v in self._px(np.asarray(self.F.to_utm.transform(*lonlat), float)))

    @classmethod
    def geotiff(cls, F, path):
        """a picture that carries its registration (a GeoTIFF, any CRS)"""
        import rasterio
        with rasterio.open(path) as ds: A, crs = ds.transform, ds.crs
        fwd, back = Transformer.from_crs(crs, F.epsg, always_xy=True), Transformer.from_crs(F.epsg, crs, always_xy=True)
        return cls(F, lambda p: np.array(fwd.transform(*(A * tuple(p)))), lambda u: np.array(~A * back.transform(*u)),
                   {'method': 'geotiff', 'crs': str(crs), 'm_per_px': round(_m_per_px(F, fwd, A), 4)})

    @classmethod
    def scaled(cls, F, pixel, lonlat, m_per_px, north_deg=0.0):
        """a plan with a scale bar and one point known on the ground; north_deg: its north arrow's turn from straight up, clockwise"""
        o = np.array(F.to_utm.transform(*lonlat)); p0 = np.asarray(pixel, float); t = math.radians(north_deg)
        R = m_per_px * np.array([[math.cos(t), math.sin(t)], [math.sin(t), -math.cos(t)]])   # (y down on the picture, north up on the ground)
        return cls(F, lambda p: o + R @ (p - p0), lambda u: p0 + np.linalg.solve(R, u - o), {'method': 'scale', 'm_per_px': m_per_px, 'north_deg': north_deg})

    @classmethod
    def controls(cls, F, anchors, method='similarity'):
        """fitted to control points [{id, pixel, lonlat}]: similarity (scale, turn, shift; two or more) or affine (three or more)"""
        need = {'similarity': 2, 'affine': 3}[method]
        if len(anchors) < need: raise SystemExit(f'register: a {method} fit needs {need} control points or more, not {len(anchors)}')
        c = np.mean([F.to_utm.transform(*a['lonlat']) for a in anchors], axis=0)   # (fitted about their centre: small numbers)
        T, Ti, A = _fit(F, anchors, method, c)
        if np.linalg.det(A) > 0:   # (a picture's y runs down; the ground's north up: a true fit turns one into the other mirrored)
            raise SystemExit('register: the control points give a mirrored picture: check that each pixel is [x across, y down] and pairs with its own lon/lat')
        res = {a['id']: round(float(np.linalg.norm(T(np.asarray(a['pixel'], float)) - F.to_utm.transform(*a['lonlat']))), 2) for a in anchors}
        loo = {}
        if len(anchors) > need:   # each point left out of the fit: how far the others put it (the honest error)
            for a in anchors:
                T_, _, _ = _fit(F, [b for b in anchors if b is not a], method, c)
                loo[a['id']] = round(float(np.linalg.norm(T_(np.asarray(a['pixel'], float)) - F.to_utm.transform(*a['lonlat']))), 2)
        d = T(np.array([1.0, 0.0])) - T(np.array([0.0, 0.0]))
        return cls(F, T, Ti, {'method': method, 'm_per_px': round(float(np.hypot(*d)), 4), 'residual_m': res, 'left_out_error_m': loo})


def _fit(F, anchors, method, c):
    P = np.array([a['pixel'] for a in anchors], float); U = np.array([F.to_utm.transform(*a['lonlat']) for a in anchors]) - c
    if method == 'similarity':   # E = a x + b y + tx, N = b x - a y + ty: a turn and a scale, the picture's y down made north up
        M = np.vstack([np.column_stack([P[:, 0], P[:, 1], np.ones(len(P)), np.zeros(len(P))]), np.column_stack([-P[:, 1], P[:, 0], np.zeros(len(P)), np.ones(len(P))])])
        a, b, tx, ty = np.linalg.lstsq(M, np.concatenate([U[:, 0], U[:, 1]]), rcond=None)[0]
        A = np.array([[a, b], [b, -a]]); t = np.array([tx, ty])
    else:
        X = np.column_stack([P, np.ones(len(P))]); sol = np.linalg.lstsq(X, U, rcond=None)[0]
        A = sol[:2].T; t = sol[2]
    return (lambda p: c + A @ p + t), (lambda u: np.linalg.solve(A, np.asarray(u) - c - t)), A


def _m_per_px(F, fwd, A):
    x, y = A.c, A.f   # (the picture's corner)
    a, b = np.array(fwd.transform(x, y)), np.array(fwd.transform(x + A.a, y + A.d))
    return float(np.hypot(*(b - a)))


def source(F, spec, base):
    """a Source from trace.yaml's source: a path to a GeoTIFF, or {image, controls, method} or {image, origin, m_per_px, north_deg}"""
    if isinstance(spec, str): return Source.geotiff(F, os.path.join(base, spec))
    if 'controls' in spec: return Source.controls(F, spec['controls'], spec.get('method', 'similarity'))
    if 'm_per_px' in spec: return Source.scaled(F, spec['origin']['pixel'], spec['origin']['lonlat'], spec['m_per_px'], spec.get('north_deg', 0.0))
    raise SystemExit('register: source is a GeoTIFF path, {image, controls: [..]} or {image, origin, m_per_px}')


def local(F, anchor, theta_deg):
    """a landmark's own frame (citygen Builder.frame: x along theta, y to its left), metres: (to_local(lonlat), to_lonlat(xy))"""
    x0, y0 = F.to_utm.transform(*anchor); c, s = math.cos(math.radians(theta_deg)), math.sin(math.radians(theta_deg))
    def to_local(ll):
        x, y = F.to_utm.transform(*ll); return ((x - x0) * c + (y - y0) * s, -(x - x0) * s + (y - y0) * c)
    def to_lonlat(p): return F.to_wgs.transform(x0 + p[0] * c - p[1] * s, y0 + p[0] * s + p[1] * c)
    return to_local, to_lonlat


def outline_landmark(F, ring, h_m, edge=(0, 1), holes=(), z_m=0.0):
    """an outline traced on a source (lon/lat ring, holes) as a prism of the classes: anchored at its centre, turned to the edge
    between two of its points (its front), the plan in its own metres"""
    U = [F.to_utm.transform(*p) for p in ring]; P = Polygon(U, [[F.to_utm.transform(*p) for p in h] for h in holes])
    anchor = F.to_wgs.transform(P.centroid.x, P.centroid.y); (ax, ay), (bx, by) = U[edge[0]], U[edge[1]]
    theta = math.degrees(math.atan2(by - ay, bx - ax)); to_local, _ = local(F, anchor, theta)
    r = lambda pts: [[round(v, 3) for v in to_local(p)] for p in pts]
    return {'kind': 'prism', 'lon': round(anchor[0], 7), 'lat': round(anchor[1], 7), 'theta_deg': round(theta, 3), 'plan_m': r(ring),
            **({'holes_m': [r(h) for h in holes]} if holes else {}), 'h_m': h_m, **({'z_m': z_m} if z_m else {})}


def fit_circle(F, lonlats):
    """a rim read off a source (an arena, a round temple): its centre (lon/lat), diameter and how far the points sit off it (m)"""
    U = np.array([F.to_utm.transform(*p) for p in lonlats]); o = U.mean(axis=0); q = U - o
    cx, cy, k = np.linalg.lstsq(np.c_[2 * q[:, 0], 2 * q[:, 1], np.ones(len(q))], (q * q).sum(axis=1), rcond=None)[0]
    r = math.sqrt(k + cx * cx + cy * cy); c = o + [cx, cy]
    return {'centre': F.to_wgs.transform(*c), 'diameter_m': round(2 * r, 2), 'rms_m': round(float(np.sqrt(np.mean((np.linalg.norm(U - c, axis=1) - r) ** 2))), 2)}


def trace(src, features):
    """traced features (pixels) as the GeoJSON city.trace reads: lines for streets and lanes, a point for a landmark of one pixel,
    else a polygon; each keeps its pixels under provenance; ids unique and every shape valid, or it stops naming the feature"""
    out, seen = [], set()
    for f in features:
        f = dict(f); px = f.pop('pixels'); fid = f.get('id')
        if fid in seen: raise SystemExit(f'register: two features are {fid!r}')
        seen.add(fid)
        ll = [[round(v, 7) for v in src.lonlat(p)] for p in px]
        if f.get('kind') in LINE_KINDS: g = {'type': 'LineString', 'coordinates': ll}
        elif len(ll) == 1: g = {'type': 'Point', 'coordinates': ll[0]}
        else: g = {'type': 'Polygon', 'coordinates': [ll + [ll[0]]]}
        if not shape(g).is_valid: raise SystemExit(f'register: {fid}: the traced shape crosses itself (check the order of its pixels)')
        f['provenance'] = {**(f.get('provenance') or {}), 'source_pixels': px}
        out.append({'type': 'Feature', 'properties': f, 'geometry': g})
    return {'type': 'FeatureCollection', 'features': out}


COLOURS = {'wall': (255, 214, 10), 'street': (0, 190, 255), 'lane': (255, 60, 190), 'block': (255, 140, 0), 'landmark': (80, 230, 120)}


def overlay(image, src, geojson, out):
    """the features drawn back over the picture (any source), each with its id: to compare the trace with what it was traced from"""
    from PIL import Image, ImageDraw
    im = Image.open(image).convert('RGBA'); lay = Image.new('RGBA', im.size); d = ImageDraw.Draw(lay)
    for f in geojson['features']:
        g, pr = f['geometry'], f['properties']; col = COLOURS.get(pr.get('kind'), (255, 255, 255)) + (230,)
        pts = [src.pixel(p) for p in ([g['coordinates']] if g['type'] == 'Point' else g['coordinates'] if g['type'] == 'LineString' else g['coordinates'][0])]
        if g['type'] == 'Point': x, y = pts[0]; d.ellipse((x - 5, y - 5, x + 5, y + 5), outline=col, width=2)
        else: d.line(pts + ([pts[0]] if g['type'] == 'Polygon' else []), fill=col, width=3)
        if pr.get('id'): d.text((pts[0][0] + 6, pts[0][1] + 4), str(pr['id']), fill=col)
    Image.alpha_composite(im, lay).convert('RGB').save(out); return out


def selftest():
    """each way of registering against a picture whose answer is known: a GeoTIFF (lon/lat and a projected CRS), control points
    (similarity, affine), a scaled plan; pixel -> lon/lat -> pixel; a traced file read back by citygen; a mirrored fit refused"""
    import tempfile, rasterio, citygen
    from rasterio.transform import from_origin
    F = Frame((108.69, 34.31, 108.75, 34.36), 1e-4); o = F.to_utm.transform(108.72, 34.335); ok = []
    truth = lambda p: (o[0] + 0.8 * (p[0] * math.cos(.3) + p[1] * math.sin(.3)), o[1] + 0.8 * (p[0] * math.sin(.3) - p[1] * math.cos(.3)))   # y down, turned .3 rad, 0.8 m a pixel
    pts = [(10, 20), (900, 40), (500, 700), (60, 650), (420, 330)]
    anchors = [{'id': f'a{i}', 'pixel': list(p), 'lonlat': list(F.to_wgs.transform(*truth(p)))} for i, p in enumerate(pts)]
    for m in ('similarity', 'affine'):
        S = Source.controls(F, anchors, m); e = max(math.dist(S.utm(p), truth(p)) for p in [(300, 300), (800, 600)])
        back = max(math.dist(S.pixel(S.lonlat(p)), p) for p in pts)
        ok.append((f'controls {m}: off {e:.4f} m, round trip {back:.2e} px, {S.report["m_per_px"]} m/px', e < .01 and back < 1e-6 and abs(S.report['m_per_px'] - .8) < 1e-3))
    flip = [{**a, 'pixel': [a['pixel'][0], 1000 - a['pixel'][1]]} for a in anchors]   # the same points on a picture flipped top to bottom
    S = Source.controls(F, flip, 'similarity'); ok.append((f'mirrored picture shows in the similarity fit: worst residual {max(S.report["residual_m"].values()):.0f} m', max(S.report['residual_m'].values()) > 50))
    try: Source.controls(F, flip, 'affine'); ok.append(('mirrored picture refused by the affine fit', False))
    except SystemExit: ok.append(('mirrored picture refused by the affine fit', True))
    S = Source.scaled(F, (100, 100), F.to_wgs.transform(*o), 0.5, 90)   # north to the right: down is east
    e = S.utm((100, 300)); ok.append((f'scaled plan, north arrow 90: 200 px down is {e[0] - o[0]:.2f} m east', abs(e[0] - o[0] - 100) < 1e-6 and abs(e[1] - o[1]) < 1e-6))
    with tempfile.TemporaryDirectory() as d:
        for crs, x0, y0, step in ((4326, 108.70, 34.35, 1e-5), (3857, *Transformer.from_crs(4326, 3857, always_xy=True).transform(108.70, 34.35), 1.0)):
            f = os.path.join(d, f'{crs}.tif')
            with rasterio.open(f, 'w', driver='GTiff', width=50, height=40, count=1, dtype='uint8', crs=f'EPSG:{crs}', transform=from_origin(x0, y0, step, step)) as w: w.write(np.zeros((1, 40, 50), 'uint8'))
            S = Source.geotiff(F, f); ll = S.lonlat((10, 20)); want = Transformer.from_crs(crs, 4326, always_xy=True).transform(x0 + 10 * step, y0 - 20 * step)
            ok.append((f'geotiff EPSG:{crs}: off {math.dist(F.to_utm.transform(*ll), F.to_utm.transform(*want)):.2e} m', math.dist(F.to_utm.transform(*ll), F.to_utm.transform(*want)) < 1e-3 and math.dist(S.pixel(ll), (10, 20)) < 1e-6))
        S = Source.controls(F, anchors, 'similarity')
        fc = trace(S, [{'id': 'w', 'kind': 'wall', 'pixels': [[0, 0], [200, 0], [200, 200], [0, 200]], 'h_m': 8},
                       {'id': 's', 'kind': 'street', 'pixels': [[0, 300], [400, 300]], 'w_m': 12},
                       {'id': 'b', 'kind': 'block', 'pixels': [[300, 0], [500, 0], [500, 120], [300, 120]], 'lot': [18, 26], 'provenance': {'basis': 'a test'}},
                       {'id': 't', 'kind': 'landmark', 'pixels': [[600, 600]], 'type': 'hall', 'w_m': 20, 'd_m': 12, 'h_m': 8}])
        json.dump(fc, open(os.path.join(d, 't.geojson'), 'w'))
        got = citygen.traced({'trace': 't.geojson'}, F, d)
        ok.append(('traced file read by citygen, provenance left out', [len(got[k]) for k in ('walls', 'streets', 'fabric', 'landmarks')] == [1, 1, 1, 1] and 'provenance' not in got['fabric'][0] and got['fabric'][0]['lot'] == [18, 26]))
    ring = [F.to_wgs.transform(o[0] + x, o[1] + y) for x, y in ((0, 0), (40, 0), (40, 20), (0, 20))]
    L = outline_landmark(F, ring, 10); xs = [p[0] for p in L['plan_m']]; ys = [p[1] for p in L['plan_m']]
    ok.append((f'outline as a prism: {max(xs) - min(xs):.2f} x {max(ys) - min(ys):.2f} m, theta {L["theta_deg"]}', abs(max(xs) - min(xs) - 40) < .01 and abs(max(ys) - min(ys) - 20) < .01 and abs(L['theta_deg']) < .01))
    c = fit_circle(F, [F.to_wgs.transform(o[0] + 65 * math.cos(a), o[1] + 65 * math.sin(a)) for a in np.linspace(0, 3, 9)])
    ok.append((f'circle: diameter {c["diameter_m"]} m, rms {c["rms_m"]}', abs(c['diameter_m'] - 130) < .05))
    for msg, good in ok: print(('ok    ' if good else 'FAIL  ') + msg)
    if not all(g for _, g in ok): raise SystemExit('register: selftest failed')


def main():
    import argparse, yaml
    if sys.argv[1:2] == ['selftest']: return selftest()
    ap = argparse.ArgumentParser(description='old maps and plans into lon/lat (pipeline/register.py docstring)')
    ap.add_argument('what', choices=['trace']); ap.add_argument('city'); ap.add_argument('spec'); ap.add_argument('--out'); ap.add_argument('--overlay')
    a = ap.parse_args()
    D = os.path.abspath(a.city); C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'))
    F = Frame(tuple(C['box']), 1.0 / C['scale']); S = yaml.safe_load(open(a.spec, encoding='utf-8'))
    src = source(F, S['source'], D)
    print('register: ' + json.dumps(src.report, ensure_ascii=False))
    fc = trace(src, S['features'])
    out = a.out or os.path.splitext(a.spec)[0] + '.geojson'
    json.dump(fc, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'register: {len(fc["features"])} features -> {out}')
    if a.overlay:
        img = S['source'] if isinstance(S['source'], str) else S['source']['image']
        print('register: overlay -> ' + overlay(os.path.join(D, img), src, fc, a.overlay))


if __name__ == '__main__':
    main()

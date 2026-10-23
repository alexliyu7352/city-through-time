"""Graphics projected on the plate (decals): an emblem drawn as glowing strokes, a star map tied to places on the model, a
schematic plan (walls, palaces) from a period map, and the closing annual-rings diagram. Each renders to an RGBA PNG whose
`uv` rectangle (in plate uv, 0..1) the engine maps onto the plate; alpha is the light, colour is the projector's hue.
Every decal is explicitly schematic: the film labels it 示意."""
import json, math, os
import local
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops


def _glow(im, radius, strength=1.0):
    """additive bloom of an RGBA layer: the image plus blurred copies (only the alpha of thin strokes blooms visibly)"""
    base = im.convert('RGBA')
    out = base.copy()
    for r, s in ((radius * .5, .55 * strength), (radius, .35 * strength), (radius * 2.5, .18 * strength)):
        b = base.filter(ImageFilter.GaussianBlur(r))
        b = Image.fromarray((np.asarray(b).astype(np.float32) * s).clip(0, 255).astype(np.uint8), 'RGBA')
        out = ImageChops.add(out, b)
    return out


def _uv_rect(F, centre_lonlat, size_m):
    """plate uv rectangle of a square `size_m` metres wide centred on a lon/lat"""
    x, y = F.to_utm.transform(*centre_lonlat); u, v = F.uv(x, y)
    w = size_m / (F.x1 - F.x0); h = size_m / (F.y1 - F.y0)
    return [u - w / 2, v - h / 2, u + w / 2, v + h / 2]


def emblem(dc, F, ST, C, out):
    """a glowing emblem: either an SVG-like list of strokes (circles, polylines in a -1..1 square) or a PNG mask"""
    S = dc.get('px', 1024); im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = tuple(int(dc.get('col', '#ffd27a').lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    P = lambda x, y: ((x + 1) / 2 * S, (y + 1) / 2 * S)
    for st in dc.get('strokes', []):
        w = int(st.get('w', 2) / 100 * S)
        if st['kind'] == 'circle':
            r = st['r'] / 2 * S; cx, cy = P(*st.get('c', (0, 0)))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col + (255,), width=max(1, w))
        elif st['kind'] == 'disc':
            r = st['r'] / 2 * S; cx, cy = P(*st.get('c', (0, 0)))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (int(255 * st.get('a', .35)),))
        elif st['kind'] == 'polyline':
            d.line([P(*p) for p in st['pts']], fill=col + (255,), width=max(1, w), joint='curve')
        elif st['kind'] == 'polygon':
            d.polygon([P(*p) for p in st['pts']], outline=col + (255,), fill=col + (int(255 * st.get('a', 0)),), width=max(1, w))
        elif st['kind'] == 'rays':   # n rays around a centre between radii r0..r1, rotated
            cx, cy = P(*st.get('c', (0, 0))); n_ = st['n']; r0, r1 = st['r0'] / 2 * S, st['r1'] / 2 * S
            for k in range(n_):
                a = 2 * math.pi * k / n_ + math.radians(st.get('rot', 0)); a2 = a + math.radians(st.get('sweep', 0))
                d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a2), cy + r1 * math.sin(a2))], fill=col + (255,), width=max(1, w))
    if dc.get('image'):
        m = Image.open(os.path.join(os.path.dirname(out), '..', dc['image'])).convert('L').resize((S, S))
        layer = Image.new('RGBA', (S, S), col + (0,)); layer.putalpha(m); im = ImageChops.add(im, layer)
    im = _glow(im, S * dc.get('glow_px', .02), dc.get('glow', 1.0))
    im.save(out)
    return {'uv': _uv_rect(F, dc['centre'], dc['size_m'])}


def starmap(dc, F, ST, C, out):
    """stars and constellation lines positioned on the plate (lon/lat per star), a faint star field around them"""
    MW = dc.get('px', 2048); MH = round(MW * F.size[1] / F.size[0])
    im = Image.new('RGBA', (MW, MH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = tuple(int(dc.get('col', '#cfe9ff').lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    rng = np.random.default_rng(dc.get('seed', 3))
    for _ in range(dc.get('field', 900)):   # a background of faint stars
        x, y = rng.random() * MW, rng.random() * MH; r = rng.random() * 1.6 + .4
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (int(70 + 120 * rng.random()),))
    pt = {}
    for s in dc['stars']:
        x, y = F.to_utm.transform(s['lon'], s['lat']); u, v = F.uv(x, y); p = (u * MW, v * MH); pt[s['id']] = p
        r = s.get('r', 7)
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col + (255,))
    for a, b in dc.get('links', []):
        d.line([pt[a], pt[b]], fill=col + (200,), width=dc.get('w', 3))
    for ln in dc.get('curves', []):   # a polyline of lon/lat points (e.g. the river as the Milky Way)
        d.line([(F.uv(*F.to_utm.transform(lon, lat))[0] * MW, F.uv(*F.to_utm.transform(lon, lat))[1] * MH) for lon, lat in ln['pts']], fill=col + (150,), width=ln.get('w', 10), joint='curve')
    im = _glow(im, 9, dc.get('glow', 1.0))
    im.save(out)
    return {'uv': [0, 0, 1, 1]}


def plan(dc, F, ST, C, out):
    """a schematic plan from a period map: walls as glowing outlines, courts as faint fills, gates as gaps (lon/lat polygons)"""
    MW = dc.get('px', 2048); MH = round(MW * F.size[1] / F.size[0])
    im = Image.new('RGBA', (MW, MH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = tuple(int(dc.get('col', '#ffa13d').lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    P = lambda ring: [(F.uv(*F.to_utm.transform(lon, lat))[0] * MW, F.uv(*F.to_utm.transform(lon, lat))[1] * MH) for lon, lat in ring]
    for sh in dc.get('shapes', []):
        if sh['kind'] == 'wall':
            if 'pts' in sh: pts = P(sh['pts'])
            else:
                import osmgeo
                pts = P(osmgeo.rings(osmgeo.elements(local.raw()), sh['osm'])[0])
            d.line(pts + ([pts[0]] if sh.get('closed', True) else []), fill=col + (255,), width=sh.get('w', 6), joint='curve')
        elif sh['kind'] == 'fill': d.polygon(P(sh['pts']), fill=col + (int(255 * sh.get('a', .25)),))
        elif sh['kind'] == 'line': d.line(P(sh['pts']), fill=col + (int(255 * sh.get('a', .8)),), width=sh.get('w', 3))
        elif sh['kind'] == 'dot':
            x, y = P([sh['pt']])[0]; r = sh.get('r', 6); d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
    im = _glow(im, 7, dc.get('glow', 1.0))
    im.save(out)
    return {'uv': [0, 0, 1, 1]}


def rings(dc, F, ST, C, out):
    """the annual-rings diagram: fine concentric lines around a centre, the plate coloured by period regions (polygons or the
    building bands' convex hulls), like the cut face of a tree"""
    from shapely.geometry import Polygon, MultiPoint, Point
    MW = dc.get('px', 2048); MH = round(MW * F.size[1] / F.size[0])
    cx_m, cy_m = F.to_utm.transform(*dc['centre'])
    xs = F.x0 + (np.arange(MW) + .5) / MW * (F.x1 - F.x0); ys = F.y1 - (np.arange(MH) + .5) / MH * (F.y1 - F.y0)
    X, Y = np.meshgrid(xs, ys); R = np.hypot(X - cx_m, Y - cy_m)
    period = dc.get('period_m', 180)
    line = (0.5 + 0.5 * np.cos(2 * np.pi * R / period)) ** 8        # thin bright lines every `period` metres
    wobble = np.sin(X / 900) * 40 + np.cos(Y / 1300) * 40
    line2 = (0.5 + 0.5 * np.cos(2 * np.pi * (R + wobble) / period)) ** 8
    lines = np.maximum(line, line2 * .7)
    rgba = np.zeros((MH, MW, 4), np.float32)
    regions = []   # (polygon in ground metres, colour)
    for rg in dc.get('regions', []):
        col = tuple(int(rg['col'].lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
        if 'polygon' in rg: poly = Polygon([F.to_utm.transform(lon, lat) for lon, lat in rg['polygon']])
        elif 'osm_polygon' in rg:
            import osmgeo
            poly = Polygon([F.to_utm.transform(lon, lat) for lon, lat in osmgeo.rings(osmgeo.elements(local.raw()), rg['osm_polygon'])[0]])
        elif 'band_hull' in rg:   # the convex hull of all buildings up to this band (from model.json)
            M = json.load(open(os.path.join(os.path.dirname(out), 'model.json')))
            lo = C['bands'][rg['band_hull']]['hi']
            pts = [p[2][0][0] for p in M['p'] if 0 < M['b'][p[0]][0] < lo]
            S = F.scale
            poly = MultiPoint([(F.cx + x / S, F.cy - z / S) for x, z in pts]).convex_hull.buffer(rg.get('buffer_m', 300))
        else: poly = Point(cx_m, cy_m).buffer(rg['radius_m'])
        regions.append((poly, col, rg.get('a', .55)))
    # rasterise regions (last on top) with PIL for speed
    reg = Image.new('RGBA', (MW, MH), (0, 0, 0, 0)); dr = ImageDraw.Draw(reg)
    for poly, col, a in regions:
        geoms = getattr(poly, 'geoms', [poly])
        for g in geoms:
            dr.polygon([((x - F.x0) / (F.x1 - F.x0) * MW, (F.y1 - y) / (F.y1 - F.y0) * MH) for x, y in g.exterior.coords], fill=col + (int(255 * a),))
    reg = reg.filter(ImageFilter.GaussianBlur(dc.get('soft_px', 4)))
    reg_a = np.asarray(reg).astype(np.float32)
    rgba[..., :3] = reg_a[..., :3]; rgba[..., 3] = reg_a[..., 3]
    # the lines: white where no region, the region's colour brightened inside
    lw = (lines * 255 * dc.get('line_gain', .8))
    rgba[..., :3] = np.maximum(rgba[..., :3], lw[..., None] * np.where(reg_a[..., 3:4] > 10, reg_a[..., :3] / 255 * .6 + .4, 1.0))
    rgba[..., 3] = np.maximum(rgba[..., 3], lw * .9)
    im = Image.fromarray(rgba.clip(0, 255).astype(np.uint8), 'RGBA')
    im.save(out)
    return {'uv': [0, 0, 1, 1]}


def image(dc, F, ST, C, out):
    """a scanned map or drawing projected on the plate: ink becomes light (alpha = darkness), tinted; centre lon/lat, width in metres,
    rotation in degrees (clockwise), optional crop box [x0, y0, x1, y1] in source pixels"""
    im = Image.open(os.path.join(os.path.dirname(out), '..', dc['file'])).convert('L')
    if dc.get('crop'): im = im.crop(tuple(dc['crop']))
    if dc.get('rot'): im = im.rotate(-dc['rot'], expand=True, fillcolor=255)
    S = dc.get('px', 1600); im = im.resize((S, max(1, round(S * im.height / im.width))))
    a = np.asarray(im).astype(np.float32) / 255.0
    ink = (1 - a); lo, hi = np.percentile(ink, dc.get('black_pct', 55)), np.percentile(ink, 99.5)
    alpha = ((ink - lo) / max(1e-6, hi - lo)).clip(0, 1) ** dc.get('gamma', .9)
    col = tuple(int(dc.get('col', '#ffe3b0').lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    rgba = np.zeros((*alpha.shape, 4), np.uint8); rgba[..., 0] = col[0]; rgba[..., 1] = col[1]; rgba[..., 2] = col[2]; rgba[..., 3] = (alpha * 255).astype(np.uint8)
    out_im = Image.fromarray(rgba, 'RGBA')
    if dc.get('vignette', True):   # soft edges so the sheet sits on the plate like a projection
        yy, xx = np.mgrid[0:out_im.height, 0:out_im.width]; vx = np.minimum(xx, out_im.width - xx) / (out_im.width * .08); vy = np.minimum(yy, out_im.height - yy) / (out_im.height * .08)
        v = np.clip(np.minimum(vx, vy), 0, 1); rgba[..., 3] = (rgba[..., 3] * v).astype(np.uint8); out_im = Image.fromarray(rgba, 'RGBA')
    out_im = _glow(out_im, 4, dc.get('glow', .6))
    out_im.save(out)
    x, y = F.to_utm.transform(*dc['centre']); u, v = F.uv(x, y)
    w = dc['width_m'] / (F.x1 - F.x0); h = w * (out_im.height / out_im.width) * ((F.x1 - F.x0) / (F.y1 - F.y0))
    return {'uv': [u - w / 2, v - h / 2, u + w / 2, v + h / 2]}


def footprints(dc, F, ST, C, out):
    """every period city's footprint on today's plate, each in its era colour: where the city stood, age by age"""
    MW = dc.get('px', 2048); MH = round(MW * F.size[1] / F.size[0])
    im = Image.new('RGBA', (MW, MH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    P = lambda ring: [(F.uv(*F.to_utm.transform(lon, lat))[0] * MW, F.uv(*F.to_utm.transform(lon, lat))[1] * MH) for lon, lat in ring]
    for era in dc['eras']:
        col = tuple(int(era['col'].lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
        if era.get('mask') is not None:   # the era city's real footprint (its hide mask): a faint fill and a glowing outline
            m = era['mask'].point(lambda v: 255 if v > 0 else 0).resize((MW, MH), Image.BILINEAR).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2)).point(lambda v: 255 if v > 90 else 0)
            edge = Image.fromarray(np.clip(np.asarray(m, np.int16) - np.asarray(m.filter(ImageFilter.MinFilter(5)), np.int16), 0, 255).astype(np.uint8))
            fill_a = m.point(lambda v: int(v * dc.get('fill', .16)))
            layer = Image.new('RGBA', (MW, MH), col + (0,)); layer.putalpha(Image.fromarray(np.maximum(np.asarray(fill_a), np.asarray(edge))))
            im = Image.alpha_composite(im, layer); d = ImageDraw.Draw(im)
            continue
        if era.get('uv_rings'):   # the era city's outline (pipeline/compile.py era_boundary): a faint fill, a fine glowing line
            for ring in era['uv_rings']:
                pts = [(u * MW, v * MH) for u, v in ring]
                d.polygon(pts, fill=col + (int(255 * dc.get('fill', .16)),)); d.line(pts + [pts[0]], fill=col + (255,), width=dc.get('w', 4), joint='curve')
            continue
        for ring in era['rings']:
            pts = P(ring)
            d.polygon(pts, fill=col + (int(255 * dc.get('fill', .16)),))
            d.line(pts + [pts[0]], fill=col + (255,), width=dc.get('w', 4), joint='curve')
    im = _glow(im, 6, dc.get('glow', .8))
    im.save(out)
    return {'uv': [0, 0, 1, 1]}


KINDS = {'emblem': emblem, 'starmap': starmap, 'plan': plan, 'rings': rings, 'image': image, 'footprints': footprints}


def render(dc, F, ST, C, out):
    return KINDS[dc['kind']](dc, F, ST, C, out)

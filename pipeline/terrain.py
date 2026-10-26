"""Real relief under the white model: Copernicus GLO-30 DEM (30 m) under the plate, through Earth Search (STAC, no login),
reprojected to the city's UTM frame and written as data/terrain16.png (16-bit, see terrainio; data/terrain.png is the 8-bit
fallback: 0 = box minimum, 255 = box maximum) with data/terrain.json (min/max/percentiles). The engine displaces the plate by
this field with a vertical exaggeration from city.yaml (terrain.exaggeration, default 3), and prep.py lifts each building's base
to the sampled ground height. Today's buildings are first taken out of the surface model (terrain.bare). Relief finer than terrain.detail.below_m (default 150 m) is written so that it shows at
terrain.detail.exaggeration (default 1: true height); data/terrain_true16.png keeps the relief as measured.
With terrain.context: { box: [w, s, e, n], res_m: 150, exaggeration_far: 2.5, blend_km: 6 } it also writes the land beyond the plate (data/context16.png and
data/context.json): relief only, for a mountain or a river a story needs that lies off the plate (the engine draws it in the
plate's colour with a fixed side light on its sunward slopes (shade), fading to the dark at its edges, in the nodes that ask for
it; compile lets pins stand on it). res_m fine enough for ridges (60 m for a mountain 40 km off; 150 m smoothed it into dunes). Its exaggeration is
the plate's at the plate's edge, easing to exaggeration_far blend_km out (a mountain at the plate's x6 is a wall).
usage: python -I pipeline/terrain.py <city_dir>
Licence: Copernicus DEM GLO-30, free for any use with attribution ("produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014
and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved")."""
import json, os, sys, urllib.request
import numpy as np, yaml
import rasterio
from rasterio.warp import reproject, Resampling, transform_bounds
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import Frame, lonlat_box

D = os.path.abspath(sys.argv[1])
C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'))
F = Frame(tuple(C['box']), 1.0 / C['scale'])
os.environ.setdefault('AWS_NO_SIGN_REQUEST', 'YES')


def dem(x0, x1, y0, y1, res):
    """Copernicus GLO-30 resampled to the city's UTM frame on the rectangle x0..x1, y0..y1 (metres) at res metres a cell, row 0
    at the north -> (metres above sea level as float32 HxW, the scene ids). It reads the lon/lat box around the rectangle, not a
    box from city.yaml: the rectangle stands outside the box it was cut from along half of each edge"""
    w, s, e, n = lonlat_box(F.to_wgs, x0, y0, x1, y1)
    q = {'collections': ['cop-dem-glo-30'], 'bbox': [w, s, e, n], 'limit': 40}
    req = urllib.request.Request('https://earth-search.aws.element84.com/v1/search', data=json.dumps(q).encode(), headers={'Content-Type': 'application/json'})
    feats = json.loads(urllib.request.urlopen(req, timeout=120).read())['features']
    if not feats: sys.exit(f'no Copernicus DEM tile matched {[w, s, e, n]}')
    W = int(round((x1 - x0) / res)); H = int(round((y1 - y0) / res))
    dst_transform = rasterio.transform.from_origin(x0, y1, res, res)
    out = np.full((H, W), np.nan, np.float32)
    for f in feats:
        href = f['assets']['data']['href'] if 'data' in f['assets'] else next(iter(f['assets'].values()))['href']
        with rasterio.open(href) as src:
            b = transform_bounds('EPSG:4326', src.crs, w, s, e, n)
            win = src.window(*b).round_offsets().round_lengths()
            win = rasterio.windows.Window(win.col_off - 2, win.row_off - 2, win.width + 4, win.height + 4)   # (two cells more each way, for the resampling at the edge)
            win = win.intersection(rasterio.windows.Window(0, 0, src.width, src.height))
            if win.width <= 0 or win.height <= 0: continue
            data = src.read(1, window=win).astype(np.float32); tr = src.window_transform(win); nod = src.nodata
        if nod is not None: data[data == nod] = np.nan
        tile = np.full((H, W), np.nan, np.float32)
        reproject(data, tile, src_transform=tr, src_crs=src.crs, dst_transform=dst_transform, dst_crs=f'EPSG:{F.epsg}', resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan)
        m = np.isnan(out) & ~np.isnan(tile); out[m] = tile[m]
        print(f['id'], 'filled', f'{(~np.isnan(out)).mean() * 100:.1f}%')
    if np.isnan(out).any():   # (a tile the catalogue does not have, such as open sea)
        print(f'WARNING: no DEM for {np.isnan(out).mean():.1%} of the rectangle (filled with its lowest height): find which tile is missing before going on')
        out = np.where(np.isnan(out), np.nanmin(out), out)
    return out, [f['id'] for f in feats]


RES = 30.0
out, scenes = dem(F.x0, F.x1, F.y0, F.y1, RES)
W, H = out.shape[1], out.shape[0]
os.makedirs(os.path.join(D, 'build', 'data'), exist_ok=True)   # (pipeline/layout.py)
import terrainio
# today's buildings out of the surface model, for the ground they stand on (what stands on the ground is
# not the ground). GLO-30 measures roofs: a town's blocks stood 2-4 m above its streets, so the period cities built over
# today's old town showed their foundations along every street (Tang, Ming) and their yard walls rose and fell (Qin's west).
# Every 30 m cell a footprint of the buildings source (and its fill) touches is dropped and filled from the open ground round
# it, streets, yards and fields, the nearest that has enough of it (subtracting the buildings' heights would leave pits and
# bumps: a cell mixes roof and street, and the heights are estimates). Tombs, terraces and banks are not buildings and stay.
# terrain.bare: false keeps the surface as measured
if (C.get('terrain') or {}).get('bare', True) is not False and C.get('buildings'):
    import rasterio.features, cmab, overture_ghsl, local
    BC = C['buildings']
    def _feet():
        kw = dict(simplify_m=BC.get('simplify_m', 1.0), min_area=BC.get('min_area_m2', 15))
        if BC.get('source') == 'cmab': yield from (q for q, *_ in cmab.load(local.raw(C['raw']['cmab']), F, **kw))
        if 'overture_ghsl' in (BC.get('source'), BC.get('fill')): yield from (q for q, *_ in overture_ghsl.load(D, F, threshold=BC.get('ghsl_threshold', 1500), **kw))
    roofs = rasterio.features.rasterize(((q, 1) for q in _feet()), out_shape=out.shape, transform=rasterio.transform.from_origin(F.x0, F.y1, RES, RES), all_touched=True, dtype='uint8').astype(bool)
    open_ = (~roofs).astype(np.float32); z_ = np.where(roofs, 0.0, out).astype(np.float32); todo = roofs.copy()
    for s_ in (1, 2, 4, 8, 16, 32):   # (cells of blur: the open ground within about 2.5 sigma)
        den = terrainio.gauss(open_, s_); ok = todo & (den > .05)
        if ok.any(): out[ok] = terrainio.gauss(z_, s_)[ok] / den[ok]; todo &= ~ok
    print(f"bare ground: {roofs.mean():.0%} of the plate under today's buildings, filled from the ground round them" + (f' ({todo.mean():.1%} kept as measured)' if todo.any() else ''))
lo, hi = float(out.min()), float(out.max())
def _binomial(a):   # a 5-tap binomial blur (~1 px sigma) along both axes: the DEM's 30 m noise reads as steps up close
    k = np.array([1, 4, 6, 4, 1], np.float32) / 16
    for ax in (0, 1):
        p_ = np.pad(a, [(2, 2) if i == ax else (0, 0) for i in range(2)], mode='edge')
        a = sum(k[i] * np.take(p_, range(i, i + a.shape[ax]), axis=ax) for i in range(5))
    return a
smooth = _binomial(out.astype(np.float32))
# the plate's relief in two scales (else the old cities stand on a jumble). Landforms broader than
# terrain.detail.below_m (a terrace, a valley side, a tableland's edge) take the film's exaggeration; what is smaller (in this
# surface model mostly today's roofs and trees, field banks, cuttings: at x6 a 4 m bump stood 24 m high under a 5 m Han house)
# is drawn at terrain.detail.exaggeration (default 1, its true height). Everything that stands on the plate reads this field
# (terrainio). The true relief is kept as terrain_true16.png for what quotes metres (a terrain section's profile).
TC = C.get('terrain') or {}; EX = float(TC.get('exaggeration', 3.0)); DT = {'below_m': 150.0, 'exaggeration': 1.0, **(TC.get('detail') or {})}
large = terrainio.gauss(smooth, float(DT['below_m']) / RES)
shown = large + (smooth - large) * (float(DT['exaggeration']) / EX)
# how high the exaggeration can go before the period cities' houses stand on foundations as tall as themselves (e.g.
# the 北阪 at x6 stretched every house; a mountain city would at x3). Over each period city's extent (citygen.extent),
# a reference house 12 m across and 6 m high (times the city's exaggeration) on the ground as the plate shows it (the landforms
# x EX, the fine relief x1): the top tenth of its foundations should stay within 30% of its height. tools/clipcheck.py measures
# the same on the built cities (tall_foundation)
SUG = {}
if any(n.get('city') for n in C['film']['nodes']):
    import citygen, osmgeo, shapely, layout
    OSM_ = osmgeo.elements(layout.raw(D), F.area); fine_ = smooth - large
    gl, gf = np.hypot(*np.gradient(large, RES)), np.hypot(*np.gradient(fine_, RES))
    Hh, Ww = smooth.shape; jj, ii = np.meshgrid(np.arange(Ww), np.arange(Hh))
    px_, py_ = F.x0 + jj / (Ww - 1) * (F.x1 - F.x0), F.y1 - ii / (Hh - 1) * (F.y1 - F.y0)
    for n in C['film']['nodes']:
        if not n.get('city'): continue
        m_ = shapely.contains_xy(citygen.extent(citygen.with_trace(n['city'], F, D), F, lambda nm: osmgeo.rings(OSM_, nm)), px_, py_)
        if m_.sum() < 4: continue
        top = lambda ex: float(np.percentile((gl[m_] * ex + gf[m_]) * 12.0 / (6.0 * float(n['city'].get('exaggeration', 2.0))), 90))
        ok = [float(ex) for ex in np.arange(1.0, 10.01, .5) if top(ex) <= .3]
        SUG[n['id']] = max(ok) if ok else 1.0
        print(f"foundations: {n['id']:10s} top tenth {top(EX):.0%} of a house at x{EX:g}; within 30% up to x{SUG[n['id']]:g}" + ('' if ok else ' (the fine relief alone is too much: roofs and trees in the surface model?)'))
    if SUG and EX > min(SUG.values()):
        print(f"WARNING: terrain.exaggeration x{EX:g} is higher than the x{min(SUG.values()):g} the steepest period city bears (docs/MODEL.md)")
terrainio.write16(D, shown, lo, hi)
terrainio.write16(D, smooth, lo, hi, name='terrain_true16.png')
Image.fromarray(((shown - lo) / max(1e-6, hi - lo) * 255).clip(0, 255).astype(np.uint8)).save(os.path.join(D, 'build', 'data', 'terrain.png'))   # (the 8-bit fallback)
pct = {str(p): round(float(np.percentile(out, p)), 1) for p in (1, 5, 25, 50, 75, 95, 99)}
json.dump({'min_m': round(lo, 1), 'max_m': round(hi, 1), 'res_m': RES, 'size': [W, H], 'percentiles': pct, 'scenes': scenes, 'detail': DT, 'exaggeration_max': SUG,
           'credit': 'Copernicus DEM GLO-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018, provided under COPERNICUS by the European Union and ESA'},
          open(os.path.join(D, 'build', 'data', 'terrain.json'), 'w'), indent=1)
print('terrain.png', W, 'x', H, 'min', round(lo, 1), 'max', round(hi, 1), 'pct', pct)

# the land beyond the plate (terrain.context): the context box's UTM rectangle in the city's frame, coarser, heights in metres
# (context.json keeps its own min/max; the engine and compile measure them from the plate's minimum, so both meet at the edge)
CX = (C.get('terrain') or {}).get('context')
if CX:
    cw, cs, ce, cn = CX['box']; cres = float(CX.get('res_m', 150))
    xs, ys = zip(*[F.to_utm.transform(lon, lat) for lon, lat in ((cw, cs), (ce, cs), (ce, cn), (cw, cn))])
    cx0, cx1, cy0, cy1 = min(xs), max(xs), min(ys), max(ys)
    cout, cscenes = dem(cx0, cx1, cy0, cy1, cres)
    clo, chi = float(cout.min()), float(cout.max())
    q = np.round((_binomial(cout) - clo) / max(1e-6, chi - clo) * 65535).clip(0, 65535).astype(np.uint32)
    rgb = np.zeros((*q.shape, 3), np.uint8); rgb[..., 0] = (q >> 8).astype(np.uint8); rgb[..., 1] = (q & 255).astype(np.uint8)
    Image.fromarray(rgb, 'RGB').save(os.path.join(D, 'build', 'data', 'context16.png'))
    (mx0, mz1), (mx1, mz0) = F.model(cx0, cy0), F.model(cx1, cy1)   # model x east, z south: the north edge has the smaller z
    json.dump({'min_m': round(clo, 1), 'max_m': round(chi, 1), 'res_m': cres, 'size': [cout.shape[1], cout.shape[0]], 'box': CX['box'],
               'rect_utm': [round(cx0, 1), round(cx1, 1), round(cy0, 1), round(cy1, 1)], 'rect_model': [mx0, mx1, mz0, mz1], 'scenes': cscenes},
              open(os.path.join(D, 'build', 'data', 'context.json'), 'w'), indent=1)
    print('context16.png', cout.shape[1], 'x', cout.shape[0], 'min', round(clo, 1), 'max', round(chi, 1), 'model rect', [mx0, mx1, mz0, mz1])

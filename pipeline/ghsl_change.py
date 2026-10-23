"""What changed where, 1975-2030: the GHSL built-up volume series (GHS-BUILT-V R2023A, 100 m cells, every 5 years, CC BY 4.0)
read against today's buildings (CMAB or Overture). Building datasets know only today's footprints and heights and, at best, when
a plot first became built-up; the volume series adds what they cannot know:
  taller   a cell whose volume kept growing after its buildings were already there: rebuilt or added to (平房 -> 高楼).
           Its buildings rise first low (f0 of today's height) and reach today's height over the epochs of that growth.
Demolition cannot be read: in R2023A the observed volume (1975-2020) never decreases in a cell (checked over Xianyang: no cell
loses volume between any two epochs), and no open dataset records buildings that are gone. The film can only say what grew.
Everything here is an estimate at 100 m x 5 years, labelled so on screen (docs/DATA.md).

  early    CMAB's first layer only says "already there in 1987". The volume series of the building's cell (1975, 1980, 1985,
           1990) dates it within 1975-1987: of the buildings of a cell, the share the cell's 1975 volume covers stood by 1975, the
           rest came in the order the volume grew (a deterministic hash orders the buildings of a cell). The film's modern
           growth starts in 1975, the first year with data (SKILL.md 演出文法 7).

  python -I pipeline/ghsl_change.py fetch <west> <south> <east> <north>     download the volume tiles (~220 MB a tile) to raw/ghsl/
                                                                          (raw/: this machine's raw root, pipeline/local.py)
  change(raw, frame, model) -> {'renew': [[i, f0, yA, yB], ...], 'early': [[i, year], ...], 'counts': [[year, new, taller], ...]}
"""
import glob, json, os, sys, urllib.request
import numpy as np

EPOCHS = [1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025, 2030]
URL = ('https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_V_GLOBE_R2023A/GHS_BUILT_V_E{y}_GLOBE_R2023A_54009_100/V1-0/tiles/'
       'GHS_BUILT_V_E{y}_GLOBE_R2023A_54009_100_V1_0_{tile}.zip')
LAST_OBSERVED = 2020   # the later epochs of R2023A are projections: change is read up to here
FIRST_LAYER = 1987     # CMAB's earliest layer ("already there in 1987"): dated within 1975..1987 from the cell's volume
VERSION = 2            # the cache's layout (bump when the output changes)


def _tile(lon, lat):
    from pyproj import Transformer
    x, y = Transformer.from_crs(4326, 'ESRI:54009', always_xy=True).transform(lon, lat)
    return f'R{int((9000000 - y) // 1000000) + 1}_C{int((x + 18041000) // 1000000) + 1}'


def fetch(raw, box):
    w, s, e, n = box
    out = os.path.join(raw, 'ghsl'); os.makedirs(out, exist_ok=True)
    for tile in sorted({_tile(lon, lat) for lon in (w, e) for lat in (s, n)}):
        for y in EPOCHS:
            url = URL.format(y=y, tile=tile); dst = os.path.join(out, os.path.basename(url))
            if os.path.exists(dst): continue
            print('fetching', url); urllib.request.urlretrieve(url, dst + '.part'); os.replace(dst + '.part', dst)
    return out


def cube(raw, box):
    """the volume cube over the box: (epochs, rows, cols) m3 per 100 m cell, with the Mollweide transform of the window"""
    import rasterio
    from rasterio.windows import from_bounds
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 'ESRI:54009', always_xy=True)
    w, s, e, n = box
    xs, ys = tr.transform([w, e, w, e], [s, s, n, n]); B = (min(xs) - 200, min(ys) - 200, max(xs) + 200, max(ys) + 200)
    V, T = [], None
    for y in EPOCHS:
        zs = sorted(glob.glob(os.path.join(raw, 'ghsl', f'GHS_BUILT_V_E{y}_*.zip')))
        if not zs: raise SystemExit(f'ghsl: no volume tile for {y} in {raw}/ghsl (python -I pipeline/ghsl_change.py fetch ...)')
        z = zs[0]
        with rasterio.open(f'zip://{z}!' + os.path.basename(z)[:-4] + '.tif') as ds:
            win = from_bounds(*B, ds.transform); a = ds.read(1, window=win).astype(np.float64); T = ds.window_transform(win)
        a[a > 4e9] = 0; V.append(a)
    return np.array(V), T


def change(raw, frame, model, cache=None, grow=1.5):
    """per building of today (model['p'], model['b']): renewal [i, f0, yA, yB] where its cell's volume grew `grow` times or more
    after the building was first there; yearly counts (cumulative)"""
    if cache and os.path.exists(cache):
        c_ = json.load(open(cache))
        if c_.get('version') == VERSION and c_.get('n') == len(model['p']): return c_   # (buildings added or removed: computed again)
    from pyproj import Transformer
    V, T = cube(raw, frame.box)
    to_moll = Transformer.from_crs(frame.epsg, 'ESRI:54009', always_xy=True)
    S = model['scale']; ei = {y: i for i, y in enumerate(EPOCHS)}; iL = ei[LAST_OBSERVED]
    def cell(xm, ym):   # Mollweide -> (row, col) or None
        c, r = ~T * (xm, ym); r, c = int(r), int(c)
        return (r, c) if 0 <= r < V.shape[1] and 0 <= c < V.shape[2] else None
    # today's buildings: centroid (UTM) -> cell; renewal where the cell grew after the building was there
    renew = []
    cx_ = [sum(p[0] for p in rec[2][0]) / len(rec[2][0]) for rec in model['p']]; cz_ = [sum(p[1] for p in rec[2][0]) / len(rec[2][0]) for rec in model['p']]
    ux = [x / S + frame.cx for x in cx_]; uy = [-z / S + frame.cy for z in cz_]
    mx, my = to_moll.transform(ux, uy)
    for i, (rec, a, b) in enumerate(zip(model['p'], mx, my)):
        rc = cell(a, b)
        if rc is None: continue
        yr = model['b'][rec[0]][0] or 1987
        ser = V[:iL + 1, rc[0], rc[1]]
        e0 = max(0, min(iL, ei.get(min(EPOCHS, key=lambda y: abs(y - max(yr, 1975))), 0)))
        v0, vL = ser[e0], ser[iL]
        if v0 <= 0 or vL < v0 * grow: continue
        d = np.diff(ser[e0:])   # the epochs of growth: from the first to the last with a third of the largest step
        if not len(d) or d.max() <= 0: continue
        big = np.nonzero(d >= d.max() / 3)[0]
        yA, yB = EPOCHS[e0 + big[0]], EPOCHS[e0 + big[-1] + 1]
        f0 = max(.15, min(.8, v0 / vL))
        renew.append([i, round(f0, 3), yA, yB])
    # the first layer dated from the cell's volume, 1975-1987
    early = []; i75, i80, i85, i90 = ei[1975], ei[1980], ei[1985], ei[1990]
    for i, (rec, a, b) in enumerate(zip(model['p'], mx, my)):
        yr = model['b'][rec[0]][0]
        if yr and yr > FIRST_LAYER: continue
        rc = cell(a, b)
        if rc is None: continue
        v75, v80, v85, v90 = (V[k, rc[0], rc[1]] for k in (i75, i80, i85, i90))
        vR = v85 + (v90 - v85) * (FIRST_LAYER - 1985) / 5
        if vR <= 0: continue
        f75, f80, f85 = min(1, v75 / vR), min(1, v80 / vR), min(1, v85 / vR)
        r = ((rec[0] * 2654435761) % 4294967296) / 4294967296   # the building's place among those of its cell
        if r < f75: y = 1975.0
        elif r < f80: y = 1975 + 5 * (r - f75) / max(f80 - f75, 1e-6)
        elif r < f85: y = 1980 + 5 * (r - f80) / max(f85 - f80, 1e-6)
        else: y = 1985 + (FIRST_LAYER - 1985) * (r - f85) / max(1 - f85, 1e-6)
        early.append([i, round(y, 2)])
    eff = {i: y for i, y in early}
    # yearly counts (cumulative from 1975): new buildings by their (estimated) first year, taller ones by the end of their growth
    years = list(range(1975, 2025)); counts = []
    by = [eff.get(i, model['b'][rec[0]][0]) for i, rec in enumerate(model['p'])]
    for Y in years:
        counts.append([Y, sum(1 for y in by if y and 1975 < y <= Y), sum(1 for q in renew if q[3] <= Y + 2.5)])
    out = {'version': VERSION, 'n': len(model['p']), 'renew': renew, 'early': early, 'counts': counts, 'note': 'GHS-BUILT-V R2023A, 100 m, 5-year epochs, estimate'}
    if cache: json.dump(out, open(cache, 'w'), separators=(',', ':'))
    return out


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import local   # this machine's raw root
    if len(sys.argv) >= 6 and sys.argv[1] == 'fetch': print(fetch(local.raw(), [float(v) for v in sys.argv[2:6]]))
    else: print(__doc__)

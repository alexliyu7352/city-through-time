"""3D-GloBFP (Che et al. 2024, Earth Syst. Sci. Data 16, 5357-5374): worldwide building footprints, each with a height estimated
from satellite data, CC BY 4.0. Published on figshare in ten parts by grid ID; each part holds one zip per grid cell, named
<grid id>_<west>_<south>_<east>_<north>_<regions>.zip (a name a part lists twice is kept as <figshare file id>_<name>; one shapefile in WGS84 with a `Height` field, metres). pipeline/heights.py
uses it to correct a primary adapter's heights building by building (`buildings.height_correction`, docs/DATA.md); its own
footprints are never drawn.

Shared data under the raw root (pipeline/local.py): <raw root>/globfp/index.json (the parts and their files as figshare lists
them: DOI, version, licence, md5) and the zips themselves, kept as downloaded (read in memory, never unzipped). prep never
fetches; the fetch is explicit and takes only the cells whose bounds in the file name meet the city's area (pipeline/layout.py).

  python -I pipeline/globfp.py fetch <city_dir>     the index (once) and the zips covering the city's area; a zip already here
                                                   whose md5 matches is kept
  python -I pipeline/globfp.py selftest
"""
import hashlib, io, json, os, re, sys, time, urllib.request, zipfile

PARTS = (28879733, 28881749, 28882700, 28889813, 28890593, 28891631, 28903454, 28903853, 28904453, 28906499)
API = 'https://api.figshare.com/v2/articles/'
NAME = '3D-GloBFP'
LICENCE = 'CC BY 4.0'
CITATION = ('Che, Y., Li, X., Liu, X., Wang, Y., Liao, W., Zheng, X., Zhang, X., Xu, X., Shi, Q., Zhu, J., Zhang, H., Yuan, H., '
            'Dai, Y. (2024). 3D-GloBFP: the first global three-dimensional building footprint dataset. '
            'Earth Syst. Sci. Data 16, 5357-5374. https://doi.org/10.5194/essd-16-5357-2024')
CREDIT = f'Building heights corrected with {NAME} (Che et al. 2024), {LICENCE}'
TILE = re.compile(r'(\d+)_(-?\d+(?:\.\d+)?)_(-?\d+(?:\.\d+)?)_(-?\d+(?:\.\d+)?)_(-?\d+(?:\.\d+)?)(?:_[^/]*)?\.zip')


def folder(raw): return os.path.join(raw, 'globfp')


def bounds(name):
    """a part's file name -> (grid id, (west, south, east, north)), or None for a file that is not a grid cell"""
    m = TILE.fullmatch(name)
    return (int(m[1]), tuple(float(m[k]) for k in range(2, 6))) if m else None


def covering(files, area):
    """the cells whose bounds meet the lon/lat area (west, south, east, north), by the bounds in their names"""
    w, s, e, n = area; out = []
    for f in files:
        b = bounds(f['name'])
        if b and b[1][0] < e and b[1][2] > w and b[1][1] < n and b[1][3] > s: out.append(f)
    return sorted(out, key=lambda f: f['name'])


def _get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'city-through-time pipeline'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r: return json.load(r)
        except OSError:
            if attempt == 3: raise
            time.sleep(5 * (attempt + 1))


def index(raw, refresh=False):
    """every part's files as figshare lists them, cached in <raw root>/globfp/index.json (a few hundred kB)"""
    path = os.path.join(folder(raw), 'index.json')
    if os.path.isfile(path) and not refresh: return json.load(open(path, encoding='utf-8'))
    parts = []
    for pid in PARTS:
        a = _get(API + str(pid)); files = []; page = 1
        while True:   # the files listing is paged: read until a short page
            got = _get(f'{API}{pid}/files?page={page}&page_size=500'); files += got
            if len(got) < 500: break
            page += 1
        twice = {n for n in (f['name'] for f in files) if sum(g['name'] == n for g in files) > 1}
        if twice: print(f'globfp: part {pid} lists {sorted(twice)} more than once: each kept under its figshare file id')
        parts.append({'id': pid, 'title': a['title'], 'doi': a['doi'], 'version': a.get('version'), 'url': a.get('url_public_html'),
                      'licence': a['license']['name'],
                      'files': [{'name': f['name'], 'file': f'{f["id"]}_{f["name"]}' if f['name'] in twice else f['name'],
                                 'size': f['size'], 'md5': f.get('computed_md5') or f.get('supplied_md5'),
                                 'url': f['download_url']} for f in files]})
        print(f'globfp: part {pid}: {len(files)} files, {a["license"]["name"]}')
    bad = [p['id'] for p in parts if p['licence'] != LICENCE]
    if bad: raise SystemExit(f'globfp: parts {bad} are no longer {LICENCE}; check the licence before using them')
    out = {'dataset': NAME, 'licence': LICENCE, 'citation': CITATION, 'listed': time.strftime('%Y-%m-%d'), 'parts': parts}
    os.makedirs(folder(raw), exist_ok=True)
    tmp = path + '.tmp'; json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False); os.replace(tmp, path)
    return out


def _files(idx):
    return [{**f, 'part': p['id'], 'doi': p['doi'], 'version': p['version']} for p in idx['parts'] for f in p['files']]


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 22), b''): h.update(chunk)
    return h.hexdigest()


def fetch(raw, area):
    """download the cells covering the area; a zip whose md5 matches figshare's is kept"""
    idx = index(raw); want = covering(_files(idx), area)
    if not want: raise SystemExit(f'globfp: no {NAME} cell covers {area}')
    for f in want:
        dst = os.path.join(folder(raw), f['file'])
        if os.path.isfile(dst) and md5(dst) == f['md5']: print('globfp: have', f['file']); continue
        print(f'globfp: fetching {f["name"]} ({f["size"] / 1e6:.0f} MB)', flush=True)
        urllib.request.urlretrieve(f['url'], dst + '.part')
        if md5(dst + '.part') != f['md5']: raise SystemExit(f'globfp: {f["name"]}: md5 does not match figshare\'s; not kept')
        os.replace(dst + '.part', dst)
    return want


def load(raw, frame):
    """the dataset's buildings over the frame's area -> (polygons in the frame's UTM metres, heights in metres, provenance).
    Stops when the index or a covering cell is missing (fetch first: no silent download in prep)."""
    import numpy as np, shapefile, shapely
    from shapely.geometry import shape
    path = os.path.join(folder(raw), 'index.json')
    if not os.path.isfile(path): raise SystemExit('heights: no 3D-GloBFP index; run pipeline/globfp.py fetch <city> first (docs/DATA.md)')
    want = covering(_files(json.load(open(path, encoding='utf-8'))), frame.area)
    missing = [f['file'] for f in want if not os.path.isfile(os.path.join(folder(raw), f['file']))]
    if not want or missing: raise SystemExit(f'heights: 3D-GloBFP cells missing ({", ".join(missing) or "none listed"}); run pipeline/globfp.py fetch <city>')
    geoms, heights = [], []; skipped = 0
    for f in want:
        z = zipfile.ZipFile(os.path.join(folder(raw), f['file']))
        member = {n[-3:].lower(): n for n in z.namelist() if n[-4:-3] == '.'}
        if 'WGS' not in z.read(member['prj']).decode('utf-8', 'ignore').upper():
            raise SystemExit(f'globfp: {f["name"]}: expected a WGS84 .prj')
        r = shapefile.Reader(**{k: io.BytesIO(z.read(member[k])) for k in ('shp', 'shx', 'dbf')})
        field = [x[0] for x in r.fields[1:]].index('Height')
        for sr in r.iterShapeRecords(bbox=frame.area):
            h = sr.record[field]
            if h is None or not h == h or not 0 < h < 1000 or sr.shape.shapeType not in (5, 15, 25): skipped += 1; continue
            geoms.append(shape(sr.shape.__geo_interface__)); heights.append(float(h))
    geoms = np.array(geoms, dtype=object)
    to_utm = lambda c: np.column_stack(frame.to_utm.transform(c[:, 0], c[:, 1]))
    geoms = shapely.make_valid(shapely.transform(geoms, to_utm))
    ok = ~shapely.is_empty(geoms) & (shapely.area(geoms) > 0)
    provenance = {'dataset': NAME, 'licence': LICENCE, 'citation': CITATION, 'credit': CREDIT,
                  'tiles': [{'name': f['name'], 'md5': f['md5'], 'doi': f['doi'], 'version': f['version']} for f in want],
                  'footprints': int(ok.sum()), 'skipped': skipped + int((~ok).sum())}
    return geoms[ok], np.asarray(heights)[ok], provenance


def selftest():
    import unittest
    class Tests(unittest.TestCase):
        def test_names_and_cover(self):
            self.assertEqual(bounds('2433_121.25_31.25_122.5_32.5_jiangsuCN_shanghaiCN.zip'), (2433, (121.25, 31.25, 122.5, 32.5)))
            self.assertEqual(bounds('2358_120.0_-30.0_130.0_-20.0_AS.zip')[1], (120.0, -30.0, 130.0, -20.0))
            self.assertIsNone(bounds('world_grid.zip')); self.assertIsNone(bounds('readme.txt'))
            files = [{'name': n} for n in ('2433_121.25_31.25_122.5_32.5_jiangsuCN_shanghaiCN.zip',
                                           '2435_121.25_30.0_122.5_31.25_shanghaiCN_zhejiangCN.zip',
                                           '2300_116.25_36.25_117.5_37.5_hebeiCN_shandongCN.zip', 'world_grid.zip')]
            self.assertEqual([f['name'][:4] for f in covering(files, (121.35, 31.11, 121.66, 31.43))], ['2433', '2435'])
            self.assertEqual([f['name'][:4] for f in covering(files, (121.35, 31.3, 121.66, 31.43))], ['2433'])
            self.assertEqual(covering(files, (0, 0, 1, 1)), [])
    result = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    if not result.wasSuccessful(): raise SystemExit(1)


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if sys.argv[1:] == ['selftest']: selftest()
    elif len(sys.argv) == 3 and sys.argv[1] == 'fetch':
        import layout, local
        fetch(local.raw(), layout.area(sys.argv[2]))
    else: raise SystemExit(__doc__)

"""Roof specimen sheet: today's city's roof kinds (engine/mini.js today.roofKinds, drawn with todayLight roofKinds on), each on a
few real buildings of the data beside the paintings it is made to match, one row a kind. A kind is judged here, building by
building at film distance and close, before it goes into the scene: a roof is a few pixels in a wide shot, so a scene alone hides
what a roof lacks.

usage: uv run python -I tools/roofsheet.py <city> --refs <refs.json> --out <dir> [--sheet <path prefix>] [--picks <picks.json>]
         [--from <name>=<tx,ty,tz,az,el,d,fov> ...] [--t 8] [--q '<page query>'] [--pic '<json>' | --pic @<file.json>]
         [--angle -30,40,30] [--film-d <d>] [--zoom 3.5] [--n 3] [--kinds 1,2,7] [--seed 7] [--no-mask] [--fresh-off] [--no-render | --picks-only]

  --refs    the paintings' catalogue of roofs, a JSON file (kept with the paintings, never in the city folder):
            { "cell": [560, 420], "kinds": { "<kind 1-12>": { "name": "<label>", "crops": [["<painting.jpg>", x0, y0, zoom], ...],
              "roof": ["#rrggbb", ...], "rim": [...], "plant": [...], "near": [[x, z], ...] } } }
            crops: each a cell of the painting from (x0, y0), cell / zoom pixels of it (the catalogue's own crops); roof, rim,
            plant: the colours sampled on the painting (its roof, its parapet's lit coping, its plant room's top); near (kind 12,
            the detailed models): the model positions of the landmarks to show
  --out     a folder outside the city's (the renders, picks.json, the measures); --sheet the sheet's path prefix (default
            <out>/sheet): <prefix>_1.jpg, _2.jpg, .. four kinds a page
  --picks   the specimens (default <out>/picks.json). Made when missing, from the buildings the --from frames show, then reused
            as it is, so every later sheet shows the same buildings; delete it to choose again
  --from    the frames the specimens come from (the paintings' districts; required to make picks.json): a still's camera each,
            in order of preference (a kind's specimens come from the first frames that show at least 4n of it)
  --q, --pic, --t   the page (render/still.mjs): its query without cam and pic, the still's picture keys (?pic=; their
            todayLight gets roofKinds on, and the mask's roofMap), the film's second
  --angle   the specimens' camera: azimuth, elevation, field of view (the paintings' oblique view: elevation 30-45)
  --film-d  film distance (model units; default the first --from camera's): the camera a film shot has, its frame cropped to
            the share of it a catalogue crop at --zoom covers of its painting (the painting's cell / zoom of its width)
  --kinds   only these kinds: their renders made again (the current scene's column reused as it is, --fresh-off to make it
            again) and their bands alone in <prefix>_k<kinds>.jpg; one kind's try takes about 90 s with --no-mask (no mask
            render: their measured swatches left out), a page load and three shots more with it. Without --kinds, every kind
  --no-render  lay out the sheet from the renders there; --picks-only: choose the specimens (picks.json) and stop

Per kind (rows): the painting's crops; per building (n, the kind's typical height and size, one with an irregular outline where
the kind has one, never one hidden behind a taller neighbour from the camera's side, 120 m apart): at film distance the current
scene (roof kinds off) and the new kind (on), and the new kind close; the swatches: the painting's sampled roof, rim and plant
room beside ours, measured on the lit close render (each pixel's part from a render of the same frame with todayLight roofMap
"parts": roofs red, parapets green, plant rooms blue, small units yellow, their sides darker). What a building shows is read
back from the page (window.__MINI.roofs): its caption gives the kind drawn, the kind given when another, height, footprint and
the share of its least rectangle it fills.

The pages: tools/roofsheet.mjs (one at a time; about 10 s a shot, four shots a building).
"""
import argparse, colorsys, json, math, os, subprocess, sys, tempfile, urllib.parse

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
W, H = 1920, 1080   # (the page's frame: render/page.mjs)
CELL = (400, 300)   # (a cell on the sheet, 4:3)
FONTS = [('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 3), (os.path.join(ROOT, 'fonts', 'NotoSansSC-VF.ttf'), 0)]
KIND_NAMES = {1: 'flat, own paint, plant room', 2: 'point tower, round caps', 3: 'slab, long plant room', 4: 'glass tower, warm white',
              5: 'large hall', 6: 'old grey flat', 7: 'grey tile, pitched', 8: 'lane houses', 9: 'pink hip', 10: 'ochre pitched',
              11: 'setbacks', 12: 'landmarks'}


def font(n):
    for p, i in FONTS:
        if os.path.exists(p): return ImageFont.truetype(p, n, index=i)
    return ImageFont.load_default()


def args_():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('city'); ap.add_argument('--refs', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--sheet'); ap.add_argument('--picks'); ap.add_argument('--from', dest='frm', action='append', default=[])
    ap.add_argument('--t', default='8'); ap.add_argument('--q', default='look=mini&clean'); ap.add_argument('--pic', default='{"material":"maquette"}')
    ap.add_argument('--angle', default='-30,40,30'); ap.add_argument('--film-d', type=float); ap.add_argument('--zoom', type=float, default=3.5)
    ap.add_argument('--n', type=int, default=3); ap.add_argument('--kinds'); ap.add_argument('--seed', default='7'); ap.add_argument('--no-render', action='store_true'); ap.add_argument('--picks-only', action='store_true')
    ap.add_argument('--no-mask', action='store_true'); ap.add_argument('--fresh-off', action='store_true')
    A = ap.parse_args()
    A.out = os.path.abspath(A.out); city_dir = os.path.realpath(os.path.join(ROOT, 'cities', A.city))
    if os.path.realpath(A.out).startswith(city_dir + os.sep): sys.exit('roofsheet: --out must lie outside the city folder')
    A.pic = json.loads(open(A.pic[1:], encoding='utf8').read() if A.pic.startswith('@') else A.pic)
    A.frm = [f.split('=', 1) for f in A.frm]
    A.az, A.el, A.fov = (float(v) for v in A.angle.split(','))
    A.sheet = A.sheet or os.path.join(A.out, 'sheet'); A.picks = A.picks or os.path.join(A.out, 'picks.json')
    return A


def node(cmd, A, job, tag):
    jf, of = os.path.join(A.out, f'{tag}_job.json'), os.path.join(A.out, f'{tag}.json')
    json.dump(job, open(jf, 'w')); r = subprocess.run(['node', 'tools/roofsheet.mjs', cmd, A.city, A.t, jf, of], cwd=ROOT)
    if r.returncode: sys.exit(f'roofsheet: tools/roofsheet.mjs {cmd} failed ({r.returncode})')
    return json.load(open(of))


def query(A, cam, **tl):
    """the page's query: --q, the camera, --pic with todayLight extras (roofKinds, roofMap)"""
    pic = dict(A.pic); pic['todayLight'] = {**pic.get('todayLight', {}), **tl}
    q = '&'.join(p for p in A.q.split('&') if p and not p.startswith(('cam=', 'pic=')))
    return f'{q}&cam={",".join(f"{v:.6g}" for v in cam)}&pic={urllib.parse.quote(json.dumps(pic, separators=(",", ":")))}'


# --- the specimens ----------------------------------------------------------------------------------------------------------
def pick(A, refs):
    if not A.frm: sys.exit('roofsheet: no picks.json yet: give --from frames to choose the specimens from')
    lf = os.path.join(A.out, 'list.json'); L = json.load(open(lf)) if os.path.exists(lf) else None
    if not L or L.get('from') != A.frm:   # (the frames' buildings, listed again only when the frames change)
        L = node('list', A, {'q': query(A, [0] * 7, roofKinds=1), 'seed': A.seed, 'cams': A.frm}, 'list'); L['from'] = A.frm; json.dump(L, open(lf, 'w'))
    sc, seen, allb = L['scale'], set(), []
    for fi, (name, bs) in enumerate(L['cams'].items()):
        for b in bs:
            key = (round(b['x'] / sc), round(b['z'] / sc))
            if key not in seen: seen.add(key); allb.append({**b, 'from': name, 'fi': fi})
    X = np.array([[b['x'], b['z'], b['y'], .5 * math.hypot(b['L'], b['W']) * sc] for b in allb]) if allb else np.zeros((0, 4))   # (every building drawn: what may hide one)
    one = {}   # (one building a record: a replacement footprint's pieces stand for their parent, the largest of them)
    for b in allb:
        if b['p'] not in one or b['a'] > one[b['p']]['a']: one[b['p']] = b
    allb = list(one.values())
    ux, uz, te = math.sin(math.radians(A.az)), math.cos(math.radians(A.az)), math.tan(math.radians(A.el))

    def hidden(b):   # a taller neighbour between it and the camera, over its roof's line of sight
        d = X[:, :2] - [b['x'], b['z']]; s = d @ [ux, uz]; t = np.abs(d @ [uz, -ux]); rb = .5 * math.hypot(b['L'], b['W']) * sc
        return bool(np.any((s > 1e-9) & (t < .8 * (rb + X[:, 3])) & (X[:, 2] - b['y'] > (s - X[:, 3]) * te)))
    kinds = sorted(int(k) for k in refs['kinds'] if not A.kinds or int(k) in {int(v) for v in A.kinds.split(',')})
    picks = {}
    for k in kinds:
        if k == 12:   # the detailed models: by the refs' positions
            P = []
            for nx, nz in refs['kinds']['12'].get('near', []):
                bx = min(L['landmarks'] or [[0] * 6], key=lambda b: math.hypot((b[0] + b[3]) / 2 - nx, (b[2] + b[5]) / 2 - nz))
                if not L['landmarks']: break
                P.append({'x': (bx[0] + bx[3]) / 2, 'z': (bx[2] + bx[5]) / 2, 'y': bx[4], 'y0': bx[1], 'k': 12, 'rk': 12, 'hm': round((bx[4] - bx[1]) / sc),
                          'L': round(max(bx[3] - bx[0], bx[5] - bx[2]) / sc), 'W': round(min(bx[3] - bx[0], bx[5] - bx[2]) / sc), 'a': 0, 'fill': 1, 'yr': 0, 'plan': ''})
            picks['12'] = P[:A.n]; continue
        whole = [b for b in allb if b['k'] == k and b['hm'] > 0 and b['a'] > 0]
        if not whole: picks[str(k)] = []; print(f'kind {k}: no building shows it in the --from frames'); continue
        for fi in range(len(L['cams'])):   # (the first frames that hold enough of it: the --from order is the preference)
            pool = [b for b in whole if b['fi'] <= fi]
            if len(pool) < 4 * A.n and fi < len(L['cams']) - 1: continue
            chosen, mh, ma = choose(pool, hidden, A.n, sc, fi == len(L['cams']) - 1)
            if len(chosen) >= A.n: break
        chosen.sort(key=lambda b: b['fill'], reverse=True)
        picks[str(k)] = chosen
        print(f'kind {k}: {len(pool)} in frame (of {len(whole)}), median {mh:.0f} m, {ma:.0f} m2; picked ' + ', '.join(f"{b['hm']:.0f} m {b['a']} m2 fill {b['fill']:.2f}" for b in chosen))
    out = {'scale': sc, 'angle': [A.az, A.el, A.fov], 'film_d': A.film_d, 'picks': picks}
    json.dump(out, open(A.picks, 'w'), ensure_ascii=False, indent=1); return out


def choose(pool, hidden, n, sc, last):
    """n of the pool at its typical height and size (its medians; within a quarter of its height and half of its area, or less
    near when no more frames are left), not hidden, 120 m apart, one with an irregular outline (filling under .75 of its least
    rectangle) where there is one, the rest regular (from .85)"""
    mh, ma = np.median([b['hm'] for b in pool]), np.median([b['a'] for b in pool])
    for b in pool: b['score'] = abs(math.log(b['hm'] / mh)) + .5 * abs(math.log(b['a'] / ma))
    clear = sorted((b for b in pool if not hidden(b) and (last or b['score'] <= .6)), key=lambda b: (b['score'], b['x'], b['z']))
    if last and len(clear) < n: clear += sorted((b for b in pool if b not in clear), key=lambda b: (b['score'], b['x']))
    chosen = []
    far = lambda b: all(math.hypot(b['x'] - c['x'], b['z'] - c['z']) > 120 * sc for c in chosen)
    irr = [b for b in clear if b['fill'] < .75]
    if irr: chosen.append(irr[0])
    for b in clear:
        if len(chosen) >= n: break
        if b not in chosen and (b['fill'] >= .85 or not irr) and far(b): chosen.append(b)
    for b in clear:
        if len(chosen) >= n: break
        if b not in chosen and far(b): chosen.append(b)
    return chosen, mh, ma


def cams(A, P, b):
    """a specimen's cameras: film distance (its top in the middle) and close (its roof and a storey or two of wall in the frame)"""
    sc, el = P['scale'], math.radians(A.el)
    y = b['y'] - .12 * (b['y'] - b['y0']) if b['k'] == 12 else b['y']   # (a landmark: its crown)
    ext = max(b['L'], 8.) * math.sin(el) + min(b['hm'], max(b['L'], 8.)) * math.cos(el)   # (its roof and about its width of wall, as seen)
    dc = max(35., ext / (.65 * 2 * math.tan(math.radians(A.fov) / 2))) * sc
    fd = A.film_d or P['film_d']
    return [b['x'], y, b['z'], A.az, A.el, fd, A.fov], [b['x'], y, b['z'], A.az, A.el, dc, A.fov], [[b['x'], y, b['z']]]


# --- measuring ----------------------------------------------------------------------------------------------------------------
def lab(c):
    c = np.asarray(c, float) / 255; c = np.where(c > .04045, ((c + .055) / 1.055) ** 2.4, c / 12.92)
    x, y, z = (np.array([[.4124, .3576, .1805], [.2126, .7152, .0722], [.0193, .1192, .9505]]) @ c) / [.95047, 1, 1.08883]
    f = lambda t: t ** (1 / 3) if t > .008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def parts(mask):
    """each pixel's part from the roofMap "parts" render (unlit, pure colours): roof red, rim green, plant blue, unit yellow, each
    with its other two channels about equal (a tree's green or the water's blue never is); and each pixel's brightness (a piece's
    sides are half as bright as its top)"""
    r, g, b = (mask[..., i].astype(int) for i in range(3)); hi = np.maximum(np.maximum(r, g), b)
    one = lambda p, q1, q2: (p > 60) & (p > 1.5 * np.maximum(q1, q2)) & (np.abs(q1 - q2) < .15 * p)
    return {'roof': one(r, g, b), 'rim': one(g, r, b), 'plant': one(b, r, g),
            'unit': (np.minimum(r, g) > 60) & (np.minimum(r, g) > 1.5 * b) & (np.abs(r - g) < .15 * hi)}, hi


def measure(lit, mask, at, reach):
    """the specimen's roof (the parts joined at its pixel, within reach pixels of it: its own roof, not a neighbour's that touches
    it in the frame): roof median, the rim's lit coping (its top's brightest tenth), the plant room's top median; seen: its pixels"""
    cls, hi = parts(mask); anyp = cls['roof'] | cls['rim'] | cls['plant'] | cls['unit']
    lab_, n = ndimage.label(ndimage.binary_closing(anyp, iterations=1))
    x, y = int(round(at[0])), int(round(at[1]))
    if not (0 <= x < W and 0 <= y < H): return None
    yy, xx = np.ogrid[:H, :W]; near = (xx - x) ** 2 + (yy - y) ** 2 < 25 ** 2; disc = (xx - x) ** 2 + (yy - y) ** 2 < reach ** 2
    ids = np.unique(lab_[near & (lab_ > 0)])
    if not len(ids): return {'seen': 0}
    sizes = [(lab_ == i).sum() for i in ids]; me = (lab_ == ids[int(np.argmax(sizes))]) & disc
    er = lambda m: ndimage.binary_erosion(m & me, iterations=2)
    out = {'seen': int(me.sum())}
    top = lambda m: m & (hi > .8 * np.percentile(hi[m], 95)) if m.any() else m   # (its top faces: the pieces' sides are half as bright)
    rim = top(cls['rim'] & me); rim = er(rim) if er(rim).sum() > 8 else rim   # (a parapet's top, its lit coping: a thin line, eroded only where it is wide)
    for nm, m, how in (('roof', er(cls['roof']), 'med'), ('rim', rim, 'top5'), ('plant', er(top(cls['plant'] & me)), 'med')):
        px = lit[m]
        if len(px) < 6: out[nm] = None; continue
        if how == 'top5': px = px[np.argsort(px.sum(1))][int(len(px) * .9):]
        out[nm] = [int(v) for v in np.median(px, 0)]
    return out


# --- the sheet ------------------------------------------------------------------------------------------------------------------
def hexc(c): return '#%02x%02x%02x' % tuple(c)


def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def crop_cell(im, cx, cy, w, h):
    x0 = int(round(min(max(cx - w / 2, 0), W - w))); y0 = int(round(min(max(cy - h / 2, 0), H - h)))
    return im.crop((x0, y0, x0 + int(w), y0 + int(h))).resize(CELL, Image.LANCZOS)


def swatches(R, ms):
    """the painting's samples and ours (each building's, measured), row by row: roof, rim, plant room; one cell high"""
    pw, ow = 92, 100; w = 150 + 4 * pw + 24 + max(len(ms), 1) * ow; im = Image.new('RGB', (w, CELL[1]), (246, 243, 236)); d = ImageDraw.Draw(im)
    f, fs = font(19), font(15)
    d.text((8, 2), '取樣色：概念圖｜本建築（近景受光畫面量得）', font=f, fill=(40, 40, 40))
    y = 28
    for key, lab_t in (('roof', '屋面'), ('rim', '女兒牆亮邊'), ('plant', '機房頂')):
        d.text((8, y + 14), lab_t, font=f, fill=(40, 40, 40)); x = 150
        for c in (R.get(key) or [])[:4]:
            d.rectangle([x, y, x + pw - 8, y + 50], fill=rgb(c)); L_, a, b = lab(rgb(c)); d.text((x, y + 52), f'{c}\nL{L_:.0f} {a:.0f}/{b:.0f}', font=fs, fill=(60, 60, 60)); x += pw
        if not R.get(key): d.text((x, y + 16), '未取樣', font=fs, fill=(120, 120, 120))
        x = 150 + 4 * pw + 14; d.line([x - 8, y, x - 8, y + 82], fill=(180, 170, 160), width=2)
        for i, m in enumerate(ms):
            c = m and m.get(key)
            if c: d.rectangle([x, y, x + ow - 8, y + 50], fill=tuple(c)); L_, a, b = lab(c); d.text((x, y + 52), f'#{i + 1} {hexc(c)}\nL{L_:.0f} {a:.0f}/{b:.0f}', font=fs, fill=(60, 60, 60))
            else: d.text((x + 4, y + 16), f'#{i + 1} —', font=fs, fill=(140, 140, 140))
            x += ow
        y += 90
    return im


def sheet(A, refs, P, res, meas):
    f_t, f_c, f_s = font(28), font(19), font(19)
    pad, lab_w = 8, 210; bw = lab_w + 3 * A.n * (CELL[0] + pad) + pad
    bands = []
    for k in sorted(P['picks'], key=int):
        R = refs['kinds'][k]; bs = P['picks'][k]; kk = int(k)
        bh = 44 + CELL[1] + 30 + CELL[1] + 64
        band = Image.new('RGB', (bw, bh), (246, 243, 236)); d = ImageDraw.Draw(band)
        d.rectangle([0, 0, bw, 36], fill=(196, 160, 132)); d.text((10, 3), f'類{kk}　{R.get("name", KIND_NAMES.get(kk, ""))}', font=f_t, fill=(255, 255, 255))
        x = lab_w; y = 44
        d.text((10, y + 10), '概念圖\n（目錄例圖，\n原畫 ×3–4）', font=f_c, fill=(60, 60, 60))
        for c in R.get('crops', [])[:5]:
            pth, x0, y0, z = c; pim = Image.open(pth).convert('RGB'); cw, ch = refs.get('cell', [560, 420])
            band.paste(pim.crop((x0, y0, x0 + cw // z, y0 + ch // z)).resize(CELL, Image.LANCZOS), (x, y)); x += CELL[0] + pad
        ms = [meas.get(f'{k}_{i}') for i in range(len(bs))]
        sw = swatches(R, ms); sx = bw - sw.width - pad
        if x > sx: sw = sw.crop((0, 0, max(bw - x - pad, 10), sw.height)); sx = x
        band.paste(sw, (sx, y))
        y2 = y + CELL[1] + 30
        d.text((10, y2 + 10), '同一棟：\n片中距離（現行場景｜\n新屋頂），新屋頂近景', font=f_c, fill=(60, 60, 60))
        x = lab_w
        if not bs: d.text((x + 10, y2 + 40), '資料裡找不到這一類（在取樣的畫面內）', font=f_c, fill=(150, 60, 60))
        for i, b in enumerate(bs):
            base = os.path.join(A.out, 'renders', f'{k}_{i}_')
            for j, (nm, cap) in enumerate((('off', '現行場景 · 片中距離'), ('on', '新屋頂 · 片中距離'), ('close', '新屋頂 · 近景'))):
                fn = base + nm + '.png'
                if not os.path.exists(fn): x += CELL[0] + pad; continue
                im = Image.open(fn).convert('RGB'); r = res.get(fn) or {}; at = (r.get('px') or [None])[0] or [W / 2, H / 2]
                if nm == 'close': cell = crop_cell(im, at[0], at[1], H * 4 / 3, H)
                else:
                    pw = Image.open(R['crops'][0][0]).width if R.get('crops') else 1672; cw = W * refs.get('cell', [560, 420])[0] / (A.zoom * pw)
                    cell = crop_cell(im, at[0], at[1], cw, cw * 3 / 4)
                band.paste(cell, (x, y2)); d.text((x + 4, y2 - 25), f'#{i + 1} {cap}', font=f_s, fill=(60, 60, 60)); x += CELL[0] + pad
            here = ((res.get(base + 'on.png') or {}).get('here')) or b
            kd = here.get('k', b['k']); rk = here.get('rk', b['rk'])
            note = f"#{i + 1}　畫成類{kd}" + (f"（分到類{rk}）" if rk and rk != kd else '') + f"　{b['hm']:.0f} m　{b['a']} m²　填滿 {b['fill']:.2f}" + (f"　{b.get('plan')}" if b.get('plan') else '')
            m = meas.get(f'{k}_{i}')
            if m is not None and m.get('seen', 1) < 400: note += '　（近景屋頂被擋）'
            d.text((lab_w + i * 3 * (CELL[0] + pad) + 4, y2 + CELL[1] + 6), note, font=f_s, fill=(40, 40, 40))
        bands.append(band)
    os.makedirs(os.path.dirname(os.path.abspath(A.sheet)), exist_ok=True); out = []
    for p in range(0, len(bands), 4):
        part = bands[p:p + 4]; im = Image.new('RGB', (bw, sum(b.height for b in part) + 70 + 10 * len(part)), (246, 243, 236)); d = ImageDraw.Draw(im)
        d.text((10, 10), f'屋頂樣本表 {p // 4 + 1}/{(len(bands) + 3) // 4}：每一類 {A.n} 棟資料裡的建築，片中距離（裁切到概念圖目錄的 ×{A.zoom:g}）與近景；視角 方位{A.az:g}° 仰角{A.el:g}°', font=font(24), fill=(30, 30, 30))
        y = 60
        for b in part: im.paste(b, (0, y)); y += b.height + 10
        fn = f'{A.sheet}_{p // 4 + 1}.jpg'; im.save(fn, quality=86); out.append(fn)
    return out


def main():
    A = args_(); refs = json.load(open(A.refs, encoding='utf8')); os.makedirs(os.path.join(A.out, 'renders'), exist_ok=True)
    if not A.film_d and A.frm: A.film_d = float(A.frm[0][1].split(',')[5])
    P = json.load(open(A.picks, encoding='utf8')) if os.path.exists(A.picks) else pick(A, refs)
    if A.picks_only: return
    rf, mf = os.path.join(A.out, 'render.json'), os.path.join(A.out, 'measures.json')
    sel = sorted(P['picks'], key=int) if not A.kinds else [k for k in A.kinds.split(',') if k in P['picks']]
    res = json.load(open(rf)) if os.path.exists(rf) else {}
    if not A.no_render:
        pages = {'on': [], 'off': [], 'mask': []}
        for k in sel:
            for i, b in enumerate(P['picks'][k]):
                fc, cc, pr = cams(A, P, b); base = os.path.join(A.out, 'renders', f'{k}_{i}_')
                pages['on'] += [{'q': query(A, fc, roofKinds=1), 'file': base + 'on.png', 'probe': pr}, {'q': query(A, cc, roofKinds=1), 'file': base + 'close.png', 'probe': pr}]
                if A.fresh_off or not os.path.exists(base + 'off.png'): pages['off'].append({'q': query(A, fc), 'file': base + 'off.png', 'probe': pr})   # (the current scene: kept)
                if A.no_mask:
                    if os.path.exists(base + 'mask.png'): os.remove(base + 'mask.png')   # (a mask of the roofs before: no longer this frame's)
                else: pages['mask'].append({'q': query(A, cc, roofKinds=1, roofMap='parts'), 'file': base + 'mask.png', 'probe': pr})
        if any(pages.values()):
            res.update(node('render', A, {'seed': A.seed, 'pages': [{'q': s[0]['q'], 'shots': s} for s in pages.values() if s]}, 'render'))
            json.dump(res, open(rf, 'w'))
    meas = json.load(open(mf)) if os.path.exists(mf) else {}
    for k in sel:
        for i, b in enumerate(P['picks'][k]):
            base = os.path.join(A.out, 'renders', f'{k}_{i}_'); meas.pop(f'{k}_{i}', None)
            if not (os.path.exists(base + 'close.png') and os.path.exists(base + 'mask.png')): continue
            at = ((res.get(base + 'close.png') or {}).get('px') or [None])[0]; cc = cams(A, P, b)[1]
            reach = 1.15 * .5 * math.hypot(b['L'], b['W']) * P['scale'] * H / (2 * cc[5] * math.tan(math.radians(cc[6]) / 2)) + 8   # (its half diagonal in the close frame's pixels)
            meas[f'{k}_{i}'] = at and measure(np.asarray(Image.open(base + 'close.png').convert('RGB')), np.asarray(Image.open(base + 'mask.png').convert('RGB')), at, reach)
    json.dump(meas, open(mf, 'w'), indent=1)
    if A.kinds: P = {**P, 'picks': {k: P['picks'][k] for k in sel}}; A.sheet += '_k' + '-'.join(sel)
    for fn in sheet(A, refs, P, res, meas): print(fn)


if __name__ == '__main__':
    main()

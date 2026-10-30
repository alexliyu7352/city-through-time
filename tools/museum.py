"""Museum pages (docs/MUSEUM.md): one landmark of a period city as a model of its own, at the heights it was built to, on a flat
stand, with its parts (which rest on sources, which are estimates), what the sources say of each, its museum label, and the
viewpoints whose imagined pictures are projected back onto it (tools/living.py <page>/<viewpoint>). museum.html shows it.

usage: uv run python -I tools/museum.py cities/<slug> [<page> ...]      every page of the city when none is named

  reads   cities/<slug>/museum/<page>.yaml (the landmark: node and kind and place; parts, label, life, viewpoints, sources),
          city.yaml (the node's city: the landmark as the film builds it), assets/museum/<page>/<viewpoint>.jpg and its record
  writes  build/museum/<page>.json           the page: its words, its parts' notes and status, the viewpoints and their pictures
          build/museum/<page>/model.json     the model: its records part by part, and the stand (engine/props.js buildEra reads them)
          build/museum/<page>/<vp>.jpg       each viewpoint's picture as the page loads it (and the life pictures, smaller)
          build/museum/index.json            every page: where its landmark stands in the film's model (the viewer's public mode
                                             opens a page from there: engine/view.js)
The model is the film's own generator (pipeline/citygen.py) run for the one landmark on level ground, with the exaggeration the
page gives (1: true heights). Each record goes to the first part whose `labels` (the paths the generator labels its sections
with: Builder.labelled) and `kinds` (roof: roofs) it matches; a record no part takes stops the build, so every piece of the model
is either sourced or estimated. A viewpoint's picture is used only while the viewpoint is still the one it was made from.
"""
import copy, fnmatch, json, math, os, sys

import yaml
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import citygen
import geo
import landmarks

KINDS = {'roof': (citygen.ROOF, citygen.LROOF), 'dark': (citygen.DARK,), 'earth': (citygen.EARTH,)}   # (kinds: a part may take records by what they are)
STATUS = ('sourced', 'estimated')
PIC_W, LIFE_W = 1672, 1200   # (pixels: a viewpoint's picture as the image tool makes it; a life picture beside the text)
MIN_APART = 50.0   # degrees between two viewpoints: one picture at a time, each gone 25 degrees from its own (museum.js)


def stop(page, m): raise SystemExit(f'museum {page}: {m}')


def words(page, v, what, need=('zh', 'en')):
    """a text in the page's languages"""
    if not isinstance(v, dict) or any(not str(v.get(k) or '').strip() for k in need): stop(page, f'{what}: give it in {", ".join(need)} ({{zh: .., en: ..}})')
    return {k: str(v[k]).strip() for k in need}


def find_landmark(C, D, P, page):
    """the node's city spec (its templates filled in) and the landmark the page names (by kind and place)"""
    node = next((n for n in C['film']['nodes'] if n.get('id') == P['node']), None)
    if not node or not node.get('city'): stop(page, f'node {P["node"]!r} has no city: block in city.yaml')
    F = geo.Frame(tuple(C['box']), 1.0 / C['scale'])
    cs = landmarks.templated(citygen.with_trace(copy.deepcopy(node['city']), F, D), landmarks.library(C, D), f'node {P["node"]}')
    want = P['landmark']; hits = []
    for L in cs.get('landmarks') or []:
        if not isinstance(L, dict) or L.get('kind') != want.get('kind'): continue
        if 'lon' in want and (abs(L.get('lon', 1e9) - want['lon']) > 1e-6 or abs(L.get('lat', 1e9) - want['lat']) > 1e-6): continue
        if 'id' in want and L.get('id') != want['id']: continue
        hits.append(L)
    if len(hits) != 1: stop(page, f'landmark {want}: {len(hits)} landmarks of node {P["node"]} match it (give kind with lon, lat or id: exactly one)')
    return F, cs, hits[0]


def build_model(F, cs, L, P, page):
    """the landmark alone on level ground, centred on its place: its records, each record's label, and the stand"""
    lon, lat = (L['lon'], L['lat']) if 'lon' in L else L['from']
    L = {**copy.deepcopy(L), 'exaggeration': float(P.get('exaggeration', 1))}
    level = lambda x, y: 0.0
    spec = {'origin': [lon, lat], 'theta_deg': cs.get('theta_deg', 0), 'detail': cs.get('detail', 'medium'), 'exaggeration': L['exaggeration'], 'landmarks': [L]}
    labels = []
    prims = citygen.build_city(spec, F, level, 1.0, labels=labels)
    ox, oy = F.to_utm.transform(lon, lat); th = math.radians(L.get('theta_deg', cs.get('theta_deg', 0)))
    B = citygen.Builder(F, level, 1.0, 1.0, (ox, oy))   # the stand: a level slab under it, its top the ground
    sw, sd = P.get('stage_m', [300, 200]); a, b = B.frame(ox, oy, th)(-sw / 2, 0), B.frame(ox, oy, th)(sw / 2, 0)
    B.group(); B.strip(a, b, sd, .05, part=citygen.EARTH, g=0.0, road=False)
    stand = B.finish(0)
    mx, mz = F.model(ox, oy)
    def centred(p):   # the landmark's place at the model's origin (fields 1, 2: the record's centre; 15, 16: its building's)
        q = list(p); q[1] = round(q[1] - mx, 7); q[2] = round(q[2] - mz, 7); q[10] = 0.0
        if len(q) > 16: q[15] = round(q[15] - mx, 7); q[16] = round(q[16] - mz, 7)
        return q
    site = citygen.landmark_site(L, F, cs.get('theta_deg', 0))[4]
    x0, y0, x1, y1 = site[0].bounds if site else (ox - 50, oy - 50, ox + 50, oy + 50)
    return [centred(p) for p in prims], labels, [centred(p) for p in stand], (mx, mz), math.hypot(x1 - x0, y1 - y0) / 2 * F.scale, F.scale


def assign(prims, labels, parts, page):
    """each record to the first part that takes it -> {part id: [records]}"""
    out = {p['id']: [] for p in parts}; left = {}
    for r, lab in zip(prims, labels):
        for p in parts:
            if any(fnmatch.fnmatch(lab, g) for g in p['labels']) and (not p.get('kinds') or any(r[11] in KINDS[k] for k in p['kinds'])):
                out[p['id']].append(r); break
        else: left[lab or '(no label)'] = left.get(lab or '(no label)', 0) + 1
    if left: stop(page, 'records no part takes (label: count): ' + ', '.join(f'{k}: {v}' for k, v in sorted(left.items())) + ' (add their labels to a part)')
    for p in parts:
        if not out[p['id']]: stop(page, f'part {p["id"]}: takes no record (labels {p["labels"]}{", kinds " + str(p["kinds"]) if p.get("kinds") else ""}; the labels there: {", ".join(sorted(set(labels)))})')
    return out


def camera(v, scale, page):
    """a viewpoint -> the camera [x, y, z, az, el, d, fov] in model units round the landmark (as the film's camera keys)"""
    for k in ('id', 'az', 'el', 'd_m', 'fov'):
        if k not in v: stop(page, f'viewpoint {v.get("id", "?")}: {k} is missing (id, az, el, d_m, fov; at_m [east, north, up] metres)')
    e, n, u = (list(v.get('at_m', [0, 0, 0])) + [0, 0, 0])[:3]
    return [round(e * scale, 7), round(u * scale, 7), round(-n * scale, 7), float(v['az']), float(v['el']), round(v['d_m'] * scale, 7), float(v['fov'])]


def apart(a, b):
    """degrees between two viewpoints' directions from what they look at"""
    def u(c): az, el = math.radians(c[3]), math.radians(c[4]); return (math.sin(az) * math.cos(el), math.sin(el), math.cos(az) * math.cos(el))
    return math.degrees(math.acos(max(-1.0, min(1.0, sum(x * y for x, y in zip(u(a), u(b)))))))


def picture(D, page, vp, cam, out_dir, notes):
    """a viewpoint's picture as the page loads it (a JPEG beside the model), if it is made and still belongs to this viewpoint"""
    src, rec = (os.path.join(D, 'assets', 'museum', page, vp + x) for x in ('.jpg', '.json'))
    if not os.path.exists(src): notes.append(f'{vp}: no picture yet (uv run python -I tools/living.py ref {os.path.relpath(D, ROOT)} {page}/{vp}, then gen)'); return None
    if not os.path.exists(rec): notes.append(f'{vp}: its picture has no record of the camera it was made from: tools/living.py adopt {page}/{vp} once it is checked'); return None
    made = json.load(open(rec, encoding='utf-8')).get('cam', [])
    if len(made) != 7 or any(abs(float(p) - float(q)) > 1e-6 for p, q in zip(made, cam)):
        notes.append(f'{vp}: the viewpoint moved since its picture was made ({made} -> {cam}): it no longer lines up; make it again (tools/living.py ref, gen)'); return None
    im = Image.open(src).convert('RGB')
    if im.width > PIC_W: im = im.resize((PIC_W, round(im.height * PIC_W / im.width)), Image.LANCZOS)
    f = os.path.join(out_dir, vp + '.jpg'); im.save(f, quality=88, optimize=True, progressive=True)
    return {'file': os.path.relpath(f, D).replace(os.sep, '/'), 'w': im.width, 'h': im.height}


def small(D, rel, out_dir, name):
    """a picture beside the text, at most LIFE_W wide"""
    src = os.path.join(D, rel)
    if not os.path.exists(src): raise SystemExit(f'museum: {rel}: no such picture')
    im = Image.open(src).convert('RGB')
    if im.width > LIFE_W: im = im.resize((LIFE_W, round(im.height * LIFE_W / im.width)), Image.LANCZOS)
    f = os.path.join(out_dir, name); im.save(f, quality=82, optimize=True, progressive=True)
    return os.path.relpath(f, D).replace(os.sep, '/')


def build_page(D, C, page):
    P = yaml.safe_load(open(os.path.join(D, 'museum', page + '.yaml'), encoding='utf-8')) or {}
    if P.get('id') != page: stop(page, f'id: {P.get("id")!r}: the file name\'s ({page})')
    for k in ('node', 'landmark', 'name', 'parts', 'viewpoints', 'sources', 'label'):
        if k not in P: stop(page, f'{k} is missing')
    F, cs, L = find_landmark(C, D, P, page)
    prims, labels, stand, (mx, mz), r, scale = build_model(F, cs, L, P, page)
    srcs = {k: {**words(page, v, f'sources.{k}'), 'short': words(page, v.get('short'), f'sources.{k}.short'), **({'url': v['url']} if v.get('url') else {})} for k, v in P['sources'].items()}
    cites = lambda c, what: [x if x in srcs else stop(page, f'{what}: cite {x!r} is not in sources ({", ".join(srcs)})') for x in (c or [])]
    parts = []
    for p in P['parts']:
        if p.get('status') not in STATUS: stop(page, f'part {p.get("id")}: status {p.get("status")!r}: {" or ".join(STATUS)} (unclear: estimated)')
        for k in p.get('kinds') or []:
            if k not in KINDS: stop(page, f'part {p["id"]}: kind {k!r}: one of {", ".join(KINDS)}')
        parts.append({'id': p['id'], 'labels': list(p.get('labels') or []), 'kinds': list(p.get('kinds') or []), 'status': p['status'],
                      'name': words(page, p.get('name'), f'part {p["id"]}: name'), 'note': words(page, p.get('note'), f'part {p["id"]}: note'), 'cite': cites(p.get('cite'), f'part {p["id"]}')})
    by = assign(prims, labels, parts, page)
    out = os.path.join(D, 'build', 'museum', page); os.makedirs(out, exist_ok=True)
    sw, sd = P.get('stage_m', [300, 200])
    json.dump({'scale': scale, 'size': [round(sw * scale, 7), round(sd * scale, 7)], 'exaggeration': float(P.get('exaggeration', 1)),
               'parts': [{'id': p['id'], 'prims': by[p['id']]} for p in parts], 'stand': stand},
              open(os.path.join(out, 'model.json'), 'w'), separators=(',', ':'))
    vps, notes = [], []
    for v in P['viewpoints']:
        cam = camera(v, scale, page)
        for w in vps:
            if apart(cam, w['cam']) < MIN_APART: stop(page, f'viewpoints {w["id"]} and {v["id"]} are {apart(cam, w["cam"]):.0f} degrees apart: {MIN_APART:g} or more (one picture shows at a time)')
        vps.append({'id': v['id'], 'main': bool(v.get('main')), 'cam': cam, 'name': words(page, v.get('name'), f'viewpoint {v["id"]}: name'),
                    'picture': picture(D, page, v['id'], cam, out, notes)})
    if sum(v['main'] for v in vps) != 1: stop(page, 'viewpoints: exactly one is main: true (the page opens there)')
    life = P.get('life') or {}
    meta = {'id': page, 'city': os.path.basename(D), 'cityName': words(page, C.get('name'), 'city.yaml name'), 'node': P['node'], 'name': words(page, P['name'], 'name'), 'era': words(page, P.get('era'), 'era'),
            'where': words(page, P.get('where'), 'where'), 'model': f'build/museum/{page}/model.json',
            'label': [{'head': words(page, s.get('head'), 'label head'), 'text': words(page, s.get('text'), 'label text'), 'cite': cites(s.get('cite'), 'label')} for s in P['label']],
            'life': {'text': words(page, life.get('text'), 'life text'), 'cite': cites(life.get('cite'), 'life'),
                     'pictures': [{'file': small(D, q['file'], out, f'life_{i}.jpg'), 'caption': words(page, q, f'life picture {i}'), 'credit': words(page, q.get('credit'), f'life picture {i}: credit')}
                                  for i, q in enumerate(life.get('pictures') or [])],
                     'photo': ({'file': small(D, life['photo']['file'], out, 'photo.jpg'), 'caption': words(page, life['photo'], 'life photo'), 'credit': words(page, life['photo'].get('credit'), 'life photo: credit')}
                               if life.get('photo') else None)} if life else None,
            'parts': [{k: p[k] for k in ('id', 'status', 'name', 'note', 'cite')} for p in parts], 'viewpoints': vps, 'sources': srcs}
    json.dump(meta, open(os.path.join(D, 'build', 'museum', page + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    n = sum(len(v) for v in by.values())
    print(f'{page}: {n} records in {len(parts)} parts ({", ".join(f"{p["id"]} {len(by[p["id"]])}" for p in parts)}), {len(vps)} viewpoints, '
          f'{sum(1 for v in vps if v["picture"])} with a picture -> build/museum/{page}.json')
    for m in notes: print('  ' + m)
    return {'id': page, 'node': P['node'], 'x': mx, 'z': mz, 'r': round(r, 6), 'name': meta['name']}


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    D = os.path.abspath(sys.argv[1]); M = os.path.join(D, 'museum')
    C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'))
    pages = sys.argv[2:] or sorted(f[:-5] for f in os.listdir(M) if f.endswith('.yaml')) if os.path.isdir(M) else []
    if not pages: sys.exit(f'museum: {M}: no pages (museum/<page>.yaml, docs/MUSEUM.md)')
    built = [build_page(D, C, p) for p in pages]
    idx = os.path.join(D, 'build', 'museum', 'index.json'); old = json.load(open(idx, encoding='utf-8')) if os.path.exists(idx) else []
    keep = [e for e in old if e['id'] not in {b['id'] for b in built} and os.path.exists(os.path.join(M, e['id'] + '.yaml'))]
    json.dump(sorted(keep + built, key=lambda e: e['id']), open(idx, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()

"""Museum pages (docs/MUSEUM.md): one landmark of a period city as a model of its own, at the heights it was built to, on a flat
stand, with its parts (which rest on sources, which are estimates), what the sources say of each, its museum label, and the
viewpoints whose imagined pictures are projected back onto it (tools/living.py <page>/<viewpoint>). museum.html shows it.

usage: uv run python -I tools/museum.py cities/<slug> [<page> ...]      every page of the city when none is named

  reads   cities/<slug>/museum/<page>.yaml (the landmark: node and kind and place, or `pieces`: several landmarks, each with its
          own node, built where the film has them; parts, label, life, viewpoints, sources),
          city.yaml (the node's city: the landmark as the film builds it), assets/museum/<page>/<viewpoint>.jpg and its record
  writes  build/museum/<page>.json           the page: its words, its parts' notes and status, the viewpoints and their pictures
          build/museum/<page>/model.json     the model: its records part by part, and the stand (engine/props.js buildEra reads them)
          build/museum/<page>/<vp>.jpg       each viewpoint's picture as the page loads it (and the life pictures, smaller)
          build/museum/index.json            every page: where its landmark stands in the film's model and the spot its mark
                                             points at (the viewer's public mode opens a page from there: engine/view.js)
          build/museum/plate.json            the plate without today's buildings (model.json less them) and the periods' names:
                                             what the walk-round view loads in place of the 19 MB model (engine/main.js)
Traditional Chinese: every zh text of the pages and the periods' names has its zh-Hant in museum/zh-Hant.yaml (tools/hant.py,
OpenCC s2twp, read through by a person); a zh text without one stops the build (it changed since).
The model is the film's own generator (pipeline/citygen.py) run for the one landmark on level ground, with the exaggeration the
page gives (1: true heights). A building the film tells in more than one period (a theatre in one, the hall beside it in the next)
is a page of `pieces` ({id, node, landmark}): each built from its own node's city where the film puts it, all on one stand round
the first; the labels of a piece's records begin with its id (curia/hall), so parts take them by piece. Each record goes to the first part whose `labels` (the paths the generator labels its sections
with: Builder.labelled) and `kinds` (roof: roofs) it matches; a record no part takes stops the build, so every piece of the model
is either sourced or estimated. A viewpoint's picture is used only while the viewpoint and the model are still the ones it was
made from (its record's cam, and model: the model's fingerprint, the film's generator's when it has none).
A landmark (or a piece) with `detailed: {kind, spec}` is drawn on its page by a detailed model made in Blender (tools/blender, its
kind's module; local/config.json `blender`) from the film's own sizes for it and the page's spec, in place of the generator's:
its parts are the model's objects, labelled by their names (with the piece's id first), taken by parts as records are.
"""
import copy, fnmatch, hashlib, json, math, os, struct, subprocess, sys, tempfile

import yaml
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import citygen
import geo
import landmarks
import local

KINDS = {'roof': (citygen.ROOF, citygen.LROOF), 'dark': (citygen.DARK,), 'earth': (citygen.EARTH,)}   # (kinds: a part may take records by what they are)
STATUS = ('sourced', 'estimated')
PIC_W, LIFE_W = 1672, 1200   # (pixels: a viewpoint's picture as the image tool makes it; a life picture beside the text)
MIN_APART = 50.0   # degrees between two viewpoints: one picture at a time, each gone 25 degrees from its own (museum.js)


def stop(page, m): raise SystemExit(f'museum {page}: {m}')


HANT = {}   # Simplified -> Traditional (Taiwan), museum/zh-Hant.yaml


def words(page, v, what, need=('zh', 'en')):
    """a text in the page's languages (zh-Hant from the city's zh-Hant.yaml)"""
    if not isinstance(v, dict) or any(not str(v.get(k) or '').strip() for k in need): stop(page, f'{what}: give it in {", ".join(need)} ({{zh: .., en: ..}})')
    out = {k: str(v[k]).strip() for k in need}
    if 'zh' in out:
        if out['zh'] not in HANT: stop(page, f'{what}: no zh-Hant for "{out["zh"][:30]}" in museum/zh-Hant.yaml: run uv run --with opencc python -I tools/hant.py <city> and read it through')
        out['zh-Hant'] = HANT[out['zh']]
    return out


def find_landmark(C, D, nid, want, page):
    """the node's city spec (its templates filled in, its landmarks checked and completed as compile completes them: a class's
    sizes from its defaults) and the landmark `want` names in it (by kind and place, or id)"""
    node = next((n for n in C['film']['nodes'] if n.get('id') == nid), None)
    if not node or not node.get('city'): stop(page, f'node {nid!r} has no city: block in city.yaml')
    F = geo.Frame(tuple(C['box']), 1.0 / C['scale'])
    cs = landmarks.checked(landmarks.templated(citygen.with_trace(copy.deepcopy(node['city']), F, D), landmarks.library(C, D), f'node {nid}'), f'node {nid}')
    hits = []
    for L in cs.get('landmarks') or []:
        if not isinstance(L, dict) or L.get('kind') != want.get('kind'): continue
        if 'lon' in want and (abs(L.get('lon', 1e9) - want['lon']) > 1e-6 or abs(L.get('lat', 1e9) - want['lat']) > 1e-6): continue
        if 'id' in want and L.get('id') != want['id']: continue
        hits.append(L)
    if len(hits) != 1: stop(page, f'landmark {want}: {len(hits)} landmarks of node {nid} match it (give kind with lon, lat or id: exactly one)')
    return F, cs, hits[0]


def pieces(P, page):
    """the page's landmarks: [(piece id or None, node, landmark, fix)]; one landmark (node, landmark), or `pieces`. fix: a piece
    the film puts out of line with the others (two periods' models traced apart) is moved on this page alone: move_m [east,
    north] metres and turn_deg about its own place, with why (the sources' layout); the film and city.yaml keep theirs"""
    if 'pieces' not in P:
        if 'landmark' not in P: stop(page, 'landmark is missing (or pieces: [{id, node, landmark}], for a building the film tells in several periods)')
        return [(None, P['node'], P['landmark'], {'detailed': P['detailed']} if P.get('detailed') else {})]
    if 'landmark' in P: stop(page, 'landmark and pieces: give one of them')
    out, seen = [], set()
    for i, q in enumerate(P['pieces'] or []):
        if not isinstance(q, dict) or any(k not in q for k in ('id', 'node', 'landmark')): stop(page, f'pieces[{i}]: id, node and landmark (kind with lon, lat or id)')
        if q['id'] in seen: stop(page, f'pieces: id {q["id"]!r} twice')
        fix = {k: q[k] for k in ('move_m', 'turn_deg', 'why') if k in q}
        if fix and not str((q.get('why') or {}).get('en') if isinstance(q.get('why'), dict) else '').strip():
            stop(page, f'pieces[{i}] {q["id"]}: move_m / turn_deg need why: {{zh, en}} (what the sources say and where the film has it)')
        if 'move_m' in fix and (not isinstance(fix['move_m'], list) or len(fix['move_m']) != 2): stop(page, f'pieces[{i}] {q["id"]}: move_m: [east, north] metres')
        if q.get('detailed'): fix['detailed'] = q['detailed']
        seen.add(q['id']); out.append((str(q['id']), q['node'], q['landmark'], fix))
    if not out: stop(page, 'pieces: none given')
    return out


def glb_names(f):
    """the names of a glb's mesh nodes (Blender's objects: a detailed model's parts)"""
    b = open(f, 'rb').read(); n, kind = struct.unpack_from('<II', b, 12)
    if b[:4] != b'glTF' or kind != 0x4E4F534A: raise SystemExit(f'museum: {f}: not a glb')
    return [x['name'] for x in json.loads(b[20:20 + n]).get('nodes', []) if 'mesh' in x]


def blender(page, pid, L, det, out):
    """a detailed model (docs/MUSEUM.md "Detailed models"): tools/blender/build.py run in Blender, headless, on the landmark as the
    film has it and the page's spec -> (the glb, its objects' names, what build printed)"""
    who = f'piece {pid}' if pid else 'landmark'
    if not isinstance(det, dict) or not det.get('kind'): stop(page, f'{who}: detailed: {{kind, spec}} (kind: a module of tools/blender, for instance amphitheatre)')
    exe = os.path.expanduser(str(local.get('blender') or ''))
    if not os.path.isfile(exe): stop(page, f'{who}: detailed needs Blender: local/config.json "blender" ({exe!r}) is not its program (docs/SETUP.md)')
    f = os.path.join(out, (pid or 'model') + '.glb')
    if os.path.exists(f): os.remove(f)
    with tempfile.TemporaryDirectory() as W:
        lf, sf = os.path.join(W, 'landmark.json'), os.path.join(W, 'spec.json')
        json.dump(L, open(lf, 'w', encoding='utf-8')); json.dump(det.get('spec') or {}, open(sf, 'w', encoding='utf-8'))
        r = subprocess.run([exe, '-b', '--factory-startup', '--python-exit-code', '1', '--python', os.path.join(ROOT, 'tools', 'blender', 'build.py'), '--',
                            '--kind', str(det['kind']), '--landmark', lf, '--spec', sf, '--out', f], capture_output=True, text=True)
    said = [x for x in r.stdout.splitlines() if x.startswith('build:')]
    if r.returncode or not os.path.exists(f): stop(page, f'{who}: Blender did not build its detailed model (exit {r.returncode}):\n' + '\n'.join((r.stdout + r.stderr).splitlines()[-25:]))
    return f, glb_names(f), said


def build_model(F, found, P, page, out):
    """the landmark alone on level ground, centred on its place: its records, each record's label, the stand, and the detailed
    models drawn in place of the generator's (each placed: where, turned how, at what scale) with their objects' labels.
    found: [(piece id or None, its node's city spec, the landmark, its detailed: or None)]; several pieces stand where the film
    has them, round the first one's place"""
    place = lambda L: (L['lon'], L['lat']) if 'lon' in L else L['from']
    level = lambda x, y: 0.0
    prims, labels, film_, sites, todo = [], [], [], [], []
    for pid, cs, L0, det in found:
        lon_, lat_ = place(L0)
        L = {**copy.deepcopy(L0), 'exaggeration': float(P.get('exaggeration', 1))}
        spec = {'origin': [lon_, lat_], 'theta_deg': cs.get('theta_deg', 0), 'detail': cs.get('detail', 'medium'), 'exaggeration': L['exaggeration'], 'landmarks': [L]}
        if det: todo.append((pid, cs, L0, det))   # (its detailed model, placed once the origin is known)
        else:
            lab = []
            prims += citygen.build_city(spec, F, level, 1.0, labels=lab)
            labels += lab if pid is None else [f'{pid}/{x}' if x else pid for x in lab]
        film_ += citygen.build_city({**spec, 'exaggeration': cs.get('exaggeration', 2.0), 'landmarks': [L0]}, F, level, 1.0)   # (as the film draws it: its top, for the walk-round view's mark)
        sites += citygen.landmark_site(L, F, cs.get('theta_deg', 0))[4]
    _, cs, L, _ = found[0]; lon, lat = place(L)
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
    top = max(film_, key=lambda q: q[4] + q[7]); anchor = [round(top[1], 6), round(top[4] + top[7], 6), round(top[2], 6)]
    if len(found) == 1: x0, y0, x1, y1 = sites[0].bounds if sites else (ox - 50, oy - 50, ox + 50, oy + 50)
    else:   # (round the first piece's place: every piece's ground)
        bs = [g.bounds for g in sites] or [(ox - 50, oy - 50, ox + 50, oy + 50)]
        x0, y0, x1, y1 = min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)
    detailed, objects = [], []
    for pid, cs_, L0, det in todo:   # (x east, y up, z south, metres: the glb as Blender writes it, turned about its place as the generator turns the landmark)
        f, names, said = blender(page, pid, L0, det, out)
        dx, dz = F.model(*F.to_utm.transform(*place(L0)))
        detailed.append({'file': f, 'piece': pid, 'kind': str(det['kind']), 'at': [round(dx - mx, 7), round(dz - mz, 7)],
                         'theta_deg': float(L0.get('theta_deg', cs_.get('theta_deg', 0))), 'scale': F.scale, 'said': said})
        objects += [((len(detailed) - 1, n), n if pid is None else f'{pid}/{n}') for n in names]
    return [centred(p) for p in prims], labels, [centred(p) for p in stand], (mx, mz), math.hypot(x1 - x0, y1 - y0) / 2 * F.scale, F.scale, anchor, detailed, objects


def assign(prims, labels, parts, page, objects=()):
    """each record, and each object of a detailed model, to the first part that takes it -> {part id: [records]}, {part id: [objects]}
    (a part's kinds take records by what they are: a detailed model's object is taken by its label alone)"""
    out = {p['id']: [] for p in parts}; obj = {p['id']: [] for p in parts}; left = {}
    for r, lab in list(zip(prims, labels)) + [(None, lab) for _, lab in objects]:
        for p in parts:
            if any(fnmatch.fnmatch(lab, g) for g in p['labels']) and (not p.get('kinds') or (r is not None and any(r[11] in KINDS[k] for k in p['kinds']))):
                (out if r is not None else obj)[p['id']].append(r if r is not None else lab); break
        else: left[lab or '(no label)'] = left.get(lab or '(no label)', 0) + 1
    if left: stop(page, 'records no part takes (label: count): ' + ', '.join(f'{k}: {v}' for k, v in sorted(left.items())) + ' (add their labels to a part)')
    for p in parts:
        if not out[p['id']] and not obj[p['id']]: stop(page, f'part {p["id"]}: takes no record (labels {p["labels"]}{", kinds " + str(p["kinds"]) if p.get("kinds") else ""}; the labels there: {", ".join(sorted(set(labels) | {lab for _, lab in objects}))})')
    return out, obj


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


def picture(D, page, vp, cam, out_dir, notes, model_sha, detailed):
    """a viewpoint's picture as the page loads it (a JPEG beside the model), if it is made and still belongs to this viewpoint and
    this model (its record's model: the fingerprint of the model its still showed, tools/living.py; a record with none was made from
    the film's generator, before records had one)"""
    src, rec = (os.path.join(D, 'assets', 'museum', page, vp + x) for x in ('.jpg', '.json'))
    if not os.path.exists(src): notes.append(f'{vp}: no picture yet (uv run python -I tools/living.py ref {os.path.relpath(D, ROOT)} {page}/{vp}, then gen)'); return None
    if not os.path.exists(rec): notes.append(f'{vp}: its picture has no record of the camera it was made from: tools/living.py adopt {page}/{vp} once it is checked'); return None
    made = json.load(open(rec, encoding='utf-8')).get('cam', [])
    if len(made) != 7 or any(abs(float(p) - float(q)) > 1e-6 for p, q in zip(made, cam)):
        notes.append(f'{vp}: the viewpoint moved since its picture was made ({made} -> {cam}): it no longer lines up; make it again (tools/living.py ref, gen)'); return None
    had = json.load(open(rec, encoding='utf-8')).get('model')
    if had != model_sha and (had or detailed):
        notes.append(f'{vp}: its picture was made for ' + (f'another model ({had}, now {model_sha})' if had else "the film's generator's model, and this page now draws a detailed one")
                     + ': it no longer lies on the model; make it again (tools/living.py ref, gen), or, if the change does not show, adopt it again after looking at its sheet'); return None
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
    for k in ('node', 'name', 'parts', 'viewpoints', 'sources', 'label'):
        if k not in P: stop(page, f'{k} is missing' + (' (with pieces: the period whose hall the page belongs to)' if k == 'node' and 'pieces' in P else ''))
    found, moved = [], []
    for pid, nid, want, fix in pieces(P, page):
        F, cs, L = find_landmark(C, D, nid, want, page)
        if fix.get('move_m') or fix.get('turn_deg'):
            L = copy.deepcopy(L); e_, n_ = fix.get('move_m') or (0, 0)
            if 'lon' not in L: stop(page, f'piece {pid}: move_m and turn_deg move a landmark placed by lon, lat')
            x_, y_ = F.to_utm.transform(L['lon'], L['lat']); L['lon'], L['lat'] = F.to_wgs.transform(x_ + e_, y_ + n_)
            L['theta_deg'] = L.get('theta_deg', cs.get('theta_deg', 0)) + float(fix.get('turn_deg', 0))
            moved.append({'piece': pid, 'move_m': [float(e_), float(n_)], 'turn_deg': float(fix.get('turn_deg', 0)), 'why': words(page, fix['why'], f'piece {pid}: why')})
        found.append((pid, cs, L, fix.get('detailed')))
    out = os.path.join(D, 'build', 'museum', page); os.makedirs(out, exist_ok=True)
    prims, labels, stand, (mx, mz), r, scale, anchor, detailed, objects = build_model(F, found, P, page, out)
    srcs = {k: {**words(page, v, f'sources.{k}'), 'short': words(page, v.get('short'), f'sources.{k}.short'), **({'url': v['url']} if v.get('url') else {})} for k, v in P['sources'].items()}
    cites = lambda c, what: [x if x in srcs else stop(page, f'{what}: cite {x!r} is not in sources ({", ".join(srcs)})') for x in (c or [])]
    parts = []
    for p in P['parts']:
        if p.get('status') not in STATUS: stop(page, f'part {p.get("id")}: status {p.get("status")!r}: {" or ".join(STATUS)} (unclear: estimated)')
        for k in p.get('kinds') or []:
            if k not in KINDS: stop(page, f'part {p["id"]}: kind {k!r}: one of {", ".join(KINDS)}')
        parts.append({'id': p['id'], 'labels': list(p.get('labels') or []), 'kinds': list(p.get('kinds') or []), 'status': p['status'],
                      'name': words(page, p.get('name'), f'part {p["id"]}: name'), 'note': words(page, p.get('note'), f'part {p["id"]}: note'), 'cite': cites(p.get('cite'), f'part {p["id"]}')})
    by, byo = assign(prims, labels, parts, page, objects)
    where = dict((lab, list(io)) for io, lab in objects)   # (an object's label -> [its glb's index in detailed, its name there])
    sw, sd = P.get('stage_m', [300, 200])
    json.dump({'scale': scale, 'size': [round(sw * scale, 7), round(sd * scale, 7)], 'exaggeration': float(P.get('exaggeration', 1)),
               'parts': [{'id': p['id'], 'prims': by[p['id']], **({'objects': [where[x] for x in byo[p['id']]]} if byo[p['id']] else {})} for p in parts], 'stand': stand,
               **({'detailed': [{'file': os.path.relpath(d['file'], D).replace(os.sep, '/'), **{k: d[k] for k in ('at', 'theta_deg', 'scale')}} for d in detailed]} if detailed else {})},
              open(os.path.join(out, 'model.json'), 'w'), separators=(',', ':'))
    h = hashlib.sha1(open(os.path.join(out, 'model.json'), 'rb').read())   # the model's fingerprint: a picture is made for one model (picture)
    for d in detailed: h.update(open(d['file'], 'rb').read())
    model_sha = h.hexdigest()[:16]
    vps, notes = [], []
    for v in P['viewpoints']:
        cam = camera(v, scale, page)
        for w in vps:
            if apart(cam, w['cam']) < MIN_APART: stop(page, f'viewpoints {w["id"]} and {v["id"]} are {apart(cam, w["cam"]):.0f} degrees apart: {MIN_APART:g} or more (one picture shows at a time)')
        vps.append({'id': v['id'], 'main': bool(v.get('main')), 'cam': cam, 'name': words(page, v.get('name'), f'viewpoint {v["id"]}: name'),
                    'picture': picture(D, page, v['id'], cam, out, notes, model_sha, bool(detailed))})
    if sum(v['main'] for v in vps) != 1: stop(page, 'viewpoints: exactly one is main: true (the page opens there)')
    life = P.get('life') or {}
    meta = {'id': page, 'city': os.path.basename(D), 'cityName': words(page, C.get('name'), 'city.yaml name'), 'node': P['node'], 'name': words(page, P['name'], 'name'), 'era': words(page, P.get('era'), 'era'),
            'where': words(page, P.get('where'), 'where'), 'model': f'build/museum/{page}/model.json', 'at': [mx, mz],   # (at: where it stands in the film's model, for the way back)
            'label': [{'head': words(page, s.get('head'), 'label head'), 'text': words(page, s.get('text'), 'label text'), 'cite': cites(s.get('cite'), 'label')} for s in P['label']],
            'life': {'text': words(page, life.get('text'), 'life text'), 'cite': cites(life.get('cite'), 'life'),
                     'pictures': [{'file': small(D, q['file'], out, f'life_{i}.jpg'), 'caption': words(page, q, f'life picture {i}'), 'credit': words(page, q.get('credit'), f'life picture {i}: credit')}
                                  for i, q in enumerate(life.get('pictures') or [])],
                     'photo': ({'file': small(D, life['photo']['file'], out, 'photo.jpg'), 'caption': words(page, life['photo'], 'life photo'), 'credit': words(page, life['photo'].get('credit'), 'life photo: credit')}
                               if life.get('photo') else None)} if life else None,
            'parts': [{k: p[k] for k in ('id', 'status', 'name', 'note', 'cite')} for p in parts], 'viewpoints': vps, 'sources': srcs, 'model_sha': model_sha,
            **({'moved': moved} if moved else {})}   # (pieces set where the sources put them, not where the film has them)
    json.dump(meta, open(os.path.join(D, 'build', 'museum', page + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    n = sum(len(v) for v in by.values())
    for d in detailed: print(f'{page}: {d["piece"] or "landmark"}: detailed model ({d["kind"]}) {os.path.relpath(d["file"], D)}, {os.path.getsize(d["file"]) / 1e6:.1f} MB; ' + '; '.join(x[len('build: '):] for x in d['said'] if not x.startswith('build: wrote')))
    print(f'{page}: {n} records{f" and {len(objects)} objects" if objects else ""} in {len(parts)} parts ({", ".join(f"{p["id"]} {len(by[p["id"]]) + len(byo[p["id"]])}" for p in parts)}), {len(vps)} viewpoints, '
          f'{sum(1 for v in vps if v["picture"])} with a picture -> build/museum/{page}.json')
    for m in notes: print('  ' + m)
    return {'id': page, 'node': P['node'], 'x': mx, 'z': mz, 'r': round(r, 6), 'anchor': anchor, 'name': meta['name']}


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    D = os.path.abspath(sys.argv[1]); M = os.path.join(D, 'museum')
    C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'))
    hf = os.path.join(M, 'zh-Hant.yaml')
    if os.path.exists(hf): HANT.update({e['zh']: e['zh-Hant'] for e in yaml.safe_load(open(hf, encoding='utf-8')) or []})
    pages = sys.argv[2:] or sorted(f[:-5] for f in os.listdir(M) if f.endswith('.yaml') and f != 'zh-Hant.yaml') if os.path.isdir(M) else []
    if not pages: sys.exit(f'museum: {M}: no pages (museum/<page>.yaml, docs/MUSEUM.md)')
    built = [build_page(D, C, p) for p in pages]
    idx = os.path.join(D, 'build', 'museum', 'index.json'); old = json.load(open(idx, encoding='utf-8')) if os.path.exists(idx) else []
    keep = [e for e in old if e['id'] not in {b['id'] for b in built} and os.path.exists(os.path.join(M, e['id'] + '.yaml'))]
    json.dump(sorted(keep + built, key=lambda e: e['id']), open(idx, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    mf = os.path.join(D, 'build', 'data', 'model.json')   # the walk-round view's plate: the model less today's buildings, and the periods' names
    if os.path.exists(mf):
        plate = {k: v for k, v in json.load(open(mf, encoding='utf-8')).items() if k not in ('p', 'b', 'mounds')}
        plate.update(p=[], b=[], mounds=[], name=words('plate', C.get('name'), 'city.yaml name'),
                     labels={n['id']: words('plate', n['label'], f'node {n["id"]}: label') for n in C['film']['nodes'] if n.get('city') and isinstance(n.get('label'), dict)})
        json.dump(plate, open(os.path.join(D, 'build', 'museum', 'plate.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    else: print(f'  (no build/data/model.json: the walk-round view loads the whole model; compile, then run this again)')


if __name__ == '__main__':
    main()

"""Living moments (docs/STAGING.md "Living moments"): the pictures of the period that the film projects back onto the model.
A picture is made from one shot of the model: a still of the shot as the film shows it at the moment's start (the white
model, today's city sunk, no lines, no blur), edited by an image tool into the place at that moment as the scene card
describes it, so that every wall and street lands where the model has it.
A museum page's viewpoint (docs/MUSEUM.md) is named <page>/<viewpoint> and made the same way: its still is the page's model
alone at that camera (tools/museum.mjs still, after tools/museum.py), its scene card research/museum/<page>/<viewpoint>.yaml,
its picture and record assets/museum/<page>/<viewpoint>.jpg and .json, its review files build/review/living/<page>/.

usage: uv run python -I tools/living.py ref    cities/<slug> [<id> ...]   the shot's still and the prompt (after compile)
       uv run python -I tools/living.py gen    cities/<slug> <id> ...     the picture, with the Codex CLI (if it is installed)
       uv run python -I tools/living.py adopt  cities/<slug> <id> ...     a picture made with another tool, once it is checked
       uv run python -I tools/living.py sheet  cities/<slug> [<id> ...]   the picture over the still, to check that it lines up
       uv run python -I tools/living.py check  cities/<slug>             each shot again: has the model changed under a picture?

  ref    renders build/review/living/<id>_ref.jpg (render/still.mjs at the moment's start, ?clean: no subtitles or labels; a
         museum viewpoint: tools/museum.mjs still) and
         writes build/review/living/<id>_prompt.txt from the scene card (research/living/<id>.yaml: place, when, picture,
         avoid, sources). The ref is made from build/film.json: compile first (CT_LIVING=warn while no picture exists).
  gen    asks the Codex CLI (codex exec, its built-in image generation) to edit the still by the prompt; the picture goes to
         assets/living/<id>.png, the still it was made from to assets/living/<id>_ref.jpg, and the shot to assets/living/<id>.json.
         Without the Codex CLI: give <id>_ref.jpg and <id>_prompt.txt to any image tool that edits a picture (an "image to image"
         or "edit" mode, 16:9), save its answer as assets/living/<id>.png, look at the sheet, then adopt it.
  adopt  records the shot and the still for a picture put in assets/living/ by hand (compile refuses a picture with no record).
  sheet  build/review/living/<id>_check.jpg: the still, the picture, and the two halfway blended. Look at it before using a
         picture: the buildings, walls and streets must sit on the model's (a picture that drew another view smears when projected).
  check  renders each shot again and compares it with the still the picture was made from (mean difference per pixel, 0-255):
         over 6 the model under the picture has changed (a new terrain, a rebuilt city): make the picture again.
"""
import json, os, shutil, subprocess, sys, tempfile, hashlib, datetime
import yaml
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROMPT = """Use your built-in image generation in EDIT mode on the attached image, and save the result as {out} in the current directory (16:9, the same framing). Do not write code.

This is an edit, not a new picture. Keep exactly as they are in the attached image: the camera position, the lens and the framing (nothing moves, nothing is cropped or zoomed); the horizon line at the same height in the frame; every building, wall, gate, tower and street at the same place, the same size and the same outline in the frame.

{still}

Change only the surfaces and fill the empty ground and the sky with the real place at that moment, as the sources describe it:
{picture}

Do not show: {avoid}
Look: natural colours, documentary realism, like a well-lit film still; people small in the frame, nobody posing, no close-up faces; nothing modern unless the sources name it; no text, no watermark, no border.
"""
# what the still shows, for a film's shot and for a museum page's viewpoint (the model alone on its stand)
STILL = {'living': 'The attached image is a plain white 3D model of {place}, {when}. Some of it only helps the model stand and is not a building: square slabs under monuments are the ground they stand on, dark bands at the foot of walls are shadow, flat grey strips are streets. The empty dark ground and the black sky are to be filled.',
         'museum': 'The attached image is a plain white 3D model standing alone on flat grey ground: {place}; the moment: {when}. The grey ground is the level ground round the building: paint it as that ground, running on, level, to the horizon; where it fades into the dark it only goes farther away, it does not end, drop or rise. The plain dark background is not part of the place: fill it with the land beyond and the sky, as the description says. Dark slits and openings are doorways; thin vertical sticks are timber posts.'}


def kind(m): return 'museum' if '/' in m['id'] else 'living'   # (a museum page's viewpoint, <page>/<viewpoint>, or a film's moment)
def picture(D, m, ext=None):   # (a museum page's picture is kept as a JPEG at 92: it ships from the repository, a tenth of the PNG)
    return os.path.join(D, 'assets', kind(m), m['id'] + (ext or ('.jpg' if kind(m) == 'museum' else '.png')))


def city_paths(city):
    D = os.path.abspath(city)
    if not os.path.isfile(os.path.join(D, 'city.yaml')): sys.exit(f'{city}: no city.yaml here (give the city folder, cities/<slug>)')
    return D, os.path.join(D, 'build', 'review', 'living')


def viewpoints(D, ids):
    """museum viewpoints, <page>/<viewpoint>: their cameras from build/museum/<page>.json (tools/museum.py)"""
    out = []
    for i in ids:
        page, vp = i.split('/', 1); f = os.path.join(D, 'build', 'museum', page + '.json')
        if not os.path.exists(f): sys.exit(f'{f}: build the page first (uv run python -I tools/museum.py {D} {page})')
        v = next((q for q in json.load(open(f, encoding='utf-8'))['viewpoints'] if q['id'] == vp), None)
        if not v: sys.exit(f'museum {page}: no viewpoint {vp}')
        out.append({'id': i, 'cam': v['cam'], 'page': page, 'vp': vp})
    return out


def moments(D, ids):
    if ids and all('/' in i for i in ids): return viewpoints(D, ids)
    if any('/' in i for i in ids): sys.exit('name film moments or museum viewpoints (<page>/<viewpoint>), not both at once')
    p = os.path.join(D, 'build', 'film.json')
    if not os.path.exists(p): sys.exit(f'{p}: compile first (CT_LIVING=warn uv run python -I pipeline/compile.py {D})')
    L = json.load(open(p, encoding='utf-8')).get('living') or []
    if not L: sys.exit('no living moments in build/film.json: write them in city.yaml (node living:, docs/STAGING.md "Living moments") and compile')
    by = {m['id']: m for m in L}
    for i in ids:
        if i not in by: sys.exit(f'living {i}: not in build/film.json (ids: {", ".join(by)})')
    return [by[i] for i in ids] if ids else L


def still(D, t, out_dir, prefix):
    """render/still.mjs at film time t, ?clean (the model alone), into out_dir as <prefix><t>.jpg -> its path"""
    os.makedirs(out_dir, exist_ok=True)
    r = subprocess.run(['node', os.path.join(ROOT, 'render', 'still.mjs'), os.path.basename(D), f'{t:.3f}', '--q', 'clean', '--out', out_dir, '--prefix', prefix],
                       cwd=ROOT, capture_output=True, text=True)
    f = os.path.join(out_dir, f'{prefix}{t:.3f}.jpg')
    if r.returncode or not os.path.exists(f): sys.exit(f'render/still.mjs failed:\n{r.stdout}{r.stderr}')
    return f


def shoot(D, m, out_dir, prefix):
    """the subject's still: the film at the moment's start, or the museum page's model at the viewpoint"""
    if kind(m) == 'living': return still(D, m['on'], out_dir, prefix)
    os.makedirs(out_dir, exist_ok=True); f = os.path.join(out_dir, prefix + 'still.jpg')
    r = subprocess.run(['node', os.path.join(ROOT, 'tools', 'museum.mjs'), 'still', os.path.basename(D), m['page'], m['vp'], '--out', out_dir, '--name', prefix + 'still.jpg'],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode or not os.path.exists(f): sys.exit(f'tools/museum.mjs failed:\n{r.stdout}{r.stderr}')
    return f


def card(D, m):
    p = os.path.join(D, 'research', kind(m), m['id'] + '.yaml')
    if not os.path.exists(p): sys.exit(f'{p}: write the scene card first (place, when, picture, avoid, sources; docs/STAGING.md "Living moments")')
    c = yaml.safe_load(open(p, encoding='utf-8')) or {}
    miss = [k for k in ('place', 'when', 'picture', 'avoid', 'sources') if not c.get(k)]
    if miss: sys.exit(f'{p}: missing {", ".join(miss)}')
    return c


def cmd_ref(D, R, ids):
    for m in moments(D, ids):
        c = card(D, m)
        f = shoot(D, m, os.path.dirname(os.path.join(R, m['id'])), os.path.basename(m['id']) + '_ref_')
        os.replace(f, os.path.join(R, m['id'] + '_ref.jpg'))
        place, when = c['place'].strip(), c['when'].strip()
        open(os.path.join(R, m['id'] + '_prompt.txt'), 'w', encoding='utf-8').write(
            PROMPT.format(out=os.path.basename(m['id']) + '.png', still=STILL[kind(m)].format(place=place, when=when), picture=c['picture'].strip(), avoid=c['avoid'].strip()))
        print(f'{m["id"]}: {os.path.join(R, m["id"] + "_ref.jpg")}  {os.path.join(R, m["id"] + "_prompt.txt")}')


def record(D, R, m, made):
    """the picture's record: the shot it was made from and that still (compile and check read them)"""
    os.makedirs(os.path.dirname(picture(D, m)), exist_ok=True)
    ref = os.path.join(R, m['id'] + '_ref.jpg')
    if not os.path.exists(ref): sys.exit(f'{ref}: run ref first')
    shutil.copyfile(ref, picture(D, m, '_ref.jpg'))
    json.dump({'cam': m['cam'], 'made': made, 'date': datetime.date.today().isoformat(), 'ref': os.path.basename(m['id']) + '_ref.jpg',
               'ref_sha1': hashlib.sha1(open(ref, 'rb').read()).hexdigest()}, open(picture(D, m, '.json'), 'w'), indent=1)


def cmd_gen(D, R, ids):
    if not ids: sys.exit('gen: name the moments (each takes a few minutes)')
    if not shutil.which('codex'): sys.exit('gen: no Codex CLI here; make the picture with another tool from build/review/living/<id>_ref.jpg and _prompt.txt, then adopt it')
    for m in moments(D, ids):
        ref, pr = os.path.join(R, m['id'] + '_ref.jpg'), os.path.join(R, m['id'] + '_prompt.txt')
        if not (os.path.exists(ref) and os.path.exists(pr)): sys.exit(f'{m["id"]}: run ref first')
        with tempfile.TemporaryDirectory() as W:
            r = subprocess.run(['codex', 'exec', '--skip-git-repo-check', '--ephemeral', '-s', 'workspace-write', '-C', W, '-i', ref, '-'],
                               stdin=open(pr, encoding='utf-8'), capture_output=True, text=True, timeout=1200)
            out = os.path.join(W, os.path.basename(m['id']) + '.png')
            if not os.path.exists(out): sys.exit(f'{m["id"]}: codex made no picture:\n{r.stdout[-1500:]}{r.stderr[-800:]}')
            os.makedirs(os.path.dirname(picture(D, m)), exist_ok=True)
            Image.open(out).convert('RGB').save(picture(D, m), **({'quality': 92} if picture(D, m).endswith('.jpg') else {}))
        record(D, R, m, 'codex')
        print(f'{m["id"]}: {picture(D, m)} (look at its sheet before using it)')
        cmd_sheet(D, R, [m['id']])


def cmd_adopt(D, R, ids):
    if not ids: sys.exit('adopt: name the moments')
    for m in moments(D, ids):
        if not os.path.exists(picture(D, m)): sys.exit(f'{m["id"]}: put the picture at {os.path.relpath(picture(D, m), D)} first')
        record(D, R, m, 'adopted'); print(f'{m["id"]}: recorded')


def cmd_sheet(D, R, ids):
    for m in moments(D, ids):
        ref, pic = os.path.join(R, m['id'] + '_ref.jpg'), picture(D, m)
        if not (os.path.exists(ref) and os.path.exists(pic)): print(f'{m["id"]}: no still or no picture yet'); continue
        a = Image.open(ref).convert('RGB').resize((960, 540)); b = Image.open(pic).convert('RGB').resize((960, 540))
        sh = Image.new('RGB', (1920, 1080)); sh.paste(a, (0, 0)); sh.paste(b, (960, 0)); sh.paste(Image.blend(a, b, .5).resize((1920, 540)).crop((480, 0, 1440, 540)), (0, 540))
        sh.paste(Image.blend(a, b, .5), (960, 540)); out = os.path.join(R, m['id'] + '_check.jpg'); sh.save(out, quality=90); print(out)


def cmd_check(D, R, ids):
    import numpy as np
    bad = 0
    with tempfile.TemporaryDirectory() as W:
        for m in moments(D, ids):
            old = picture(D, m, '_ref.jpg')
            if not os.path.exists(old): print(f'{m["id"]}: no picture recorded yet'); bad += 1; continue
            new = shoot(D, m, W, os.path.basename(m['id']) + '_')
            x, y = (np.asarray(Image.open(f).convert('L').resize((960, 540))).astype(float) for f in (old, new))
            d = float(np.abs(x - y).mean()); bad += d > 6
            print(f'{m["id"]}: the shot now differs from the still the picture was made from by {d:.1f} per pixel' + (' : make the picture again' if d > 6 else ''))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] not in ('ref', 'gen', 'adopt', 'sheet', 'check'): sys.exit(__doc__)
    D_, R_ = city_paths(sys.argv[2])
    {'ref': cmd_ref, 'gen': cmd_gen, 'adopt': cmd_adopt, 'sheet': cmd_sheet, 'check': cmd_check}[sys.argv[1]](D_, R_, sys.argv[3:])

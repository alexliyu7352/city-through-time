"""Model view: stills of one period city as the film shows it (its palette, its light, its terrain), from any point on the map,
before the city has a place in the film's timeline; city.yaml, script.yaml and the city's build/ are never written.

usage: python -I tools/modelview.py cities/<slug> <era> --at <lon>,<lat>[,<az>[,<el>[,<d>]]] [--at ...]
                                    [--spec <file.yaml> [--year <y>]] [--az 305] [--el 12] [--d .045] [--fov 42] [--wide] [--name <folder>]

  <era>     the id of a node of city.yaml that has a city: block, or a new id given with --spec
  --spec    a YAML file holding a city: block (what a node's city: holds, docs/MODEL.md), shown in place of the node's own
            (to try a change before writing it into city.yaml) or as a new period city at the end of the film; --year is the
            year the counter shows for a new one (default: the film's last)
  --at      the point the camera looks at, landed on the ground there; give it once per still. az/el/d after it are this
            still's own, else --az/--el/--d (defaults: the close-up of docs/MODEL.md, d .045 and el 12; az 305 has the
            room light, from the north-west, fall across the frame so slopes read)
  --wide    d .35, el 30: the whole city, for the colour and the layout
  --name    the folder of the stills under build/review/modelview/ (default: the era's id)

What it does: writes a study city at build/review/modelview/<slug>/ (a city folder of its own: a city.yaml with the film's
settings and the one node, or that node after the earlier cities it stands on, avoid_eras; copies of the prepared data; links to
research/ and assets/), compiles it, runs tools/clipcheck.py on it, and takes the stills once the city has risen
(render/still.mjs with ?bundle= on the study folder, the camera fixed and still). It prints each still and the address that
opens the same view in the preview (node tools/preview.mjs). The study has no words, sound, pins or pictures, only the city.
The terrain is the city's as prepared: a new terrain.exaggeration needs pipeline/terrain.py and prep.py run on the city.
"""
import argparse, copy, json, os, shutil, subprocess, sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import geo
import layout as LAYOUT

NODE_KEEP = ('id', 'years', 'dur', 'mood', 'label', 'col', 'tint', 'era_tint', 'ink', 'city')   # what a node's city looks like by
CLOSE = {'az': 305.0, 'el': 12.0, 'd': .045}; WIDE = {'el': 30.0, 'd': .35}


def shots(args):
    out = []
    for s in args.at:
        v = s.split(',')
        try: v = [float(x) for x in v]
        except ValueError: v = []
        if not 2 <= len(v) <= 5: raise SystemExit(f'modelview: --at {s}: give <lon>,<lat> and optionally ,<az>,<el>,<d>')
        d = {'ll': v[:2], 'az': args.az, 'el': args.el, 'd': args.d}
        for k, x in zip(('az', 'el', 'd'), v[2:]): d[k] = x
        if not 0 < d['el'] < 90: raise SystemExit(f'modelview: --at {s}: el {d["el"]:g} must be between 0 and 90 degrees')
        if not d['d'] > 0: raise SystemExit(f'modelview: --at {s}: d must be above 0 (model units; the close-up is .035-.06)')
        out.append(d)
    return out


def study_film(C, era, spec, shots_, fov, year=None):
    """the study's city.yaml: the film's own settings, its nodes reduced to the era (and the cities it stands on), one camera key
    per still in the era's node"""
    F = C['film']; nodes = {n['id']: n for n in F['nodes']}
    if era in nodes and not (nodes[era].get('city') or spec):
        raise SystemExit(f'modelview: node {era} has no city: block (nodes with one: {", ".join(n["id"] for n in F["nodes"] if n.get("city")) or "none"}); give one with --spec')
    if era not in nodes and not spec:
        raise SystemExit(f'modelview: city.yaml has no node {era}: give its city: block with --spec <file> (nodes with one: {", ".join(n["id"] for n in F["nodes"] if n.get("city")) or "none"})')
    target = {k: copy.deepcopy(v) for k, v in nodes.get(era, {}).items() if k in NODE_KEEP}
    if spec: target['city'] = spec
    if era not in nodes:
        last = F['nodes'][-1]
        target.update(id=era, years=[year, year] if year is not None else list(last.get('years', [2000, 2000])), dur=20.0, mood={'feel': 'calm', 'level': 1}, label={l: era for l in F.get('lang', ['zh', 'en'])},
                      col=target['city'].get('col', '#E8DCC6'), tint=0)
    # the cities it is built on (avoid_eras), in the film's order, ahead of it
    need, todo = [], list(target['city'].get('avoid_eras') or [])
    while todo:
        i = todo.pop()
        if i in need: continue
        if i not in nodes or not nodes[i].get('city'): raise SystemExit(f'modelview: {era} is built on {i} (avoid_eras), which is not a node with a city: block')
        need.append(i); todo += list(nodes[i]['city'].get('avoid_eras') or [])
    order = [n['id'] for n in F['nodes']]
    study = [{k: copy.deepcopy(v) for k, v in nodes[i].items() if k in NODE_KEEP} for i in sorted(need, key=order.index)] + [target]
    ids = {n['id'] for n in study}
    for n in study:
        cs = n['city']
        if cs.get('until') not in ids: cs.pop('until', None); cs.pop('until_plus', None)   # a city taken back by a later node stays up here
        n['camera'] = [{'t': 0, 'll': shots_[0]['ll'], 'az': shots_[0]['az'], 'el': shots_[0]['el'], 'd': shots_[0]['d'], 'fov': fov}]
    dur = float(target['dur'])
    target['camera'] = [{'t': round(dur * (k + 1) / (len(shots_) + 1), 2), 'll': s['ll'], 'az': s['az'], 'el': s['el'], 'd': s['d'], 'fov': fov} for k, s in enumerate(shots_)]
    S = copy.deepcopy(C); SF = S['film']
    for k in ('prologue', 'voice', 'music', 'sfx'): SF.pop(k, None)
    SF.update(drift=0, opening={'dur': 0}, closing={'lights_after': 0, 'end_after': 0, 'end_hold': .2}, nodes=study)   # (drift 0: stills of one view frame alike)
    return S


def study_folder(city, slug):
    """build/review/modelview/<slug>/: a city folder (pipeline/layout.py) that compile reads and writes instead of the city's own.
    The prepared data is copied, not linked: compile writes into build/data, and a link would carry a write into the real one."""
    S = LAYOUT.review(city, 'modelview', slug)
    os.makedirs(LAYOUT.data(S), exist_ok=True)
    for f in sorted(os.listdir(LAYOUT.data(city))):
        p = LAYOUT.data(city, f)
        if os.path.isfile(p): shutil.copy2(p, LAYOUT.data(S, f))
    for d in ('research', 'assets'):   # read only: traces, areas, outlines
        link, real = os.path.join(S, d), os.path.join(city, d)
        if os.path.lexists(link): os.remove(link)
        if os.path.isdir(real): os.symlink(os.path.relpath(real, S), link)
    if os.path.exists(os.path.join(S, 'script.yaml')): os.remove(os.path.join(S, 'script.yaml'))   # (cues from city.yaml: none)
    return S


def run(cmd, log, env=None):
    r = subprocess.run(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    open(log, 'w', encoding='utf-8').write(r.stdout)
    return r


def main():
    ap = argparse.ArgumentParser(description='stills of one period city as the film shows it (tools/modelview.py docstring)')
    ap.add_argument('city'); ap.add_argument('era')
    ap.add_argument('--at', action='append', required=True); ap.add_argument('--spec'); ap.add_argument('--year', type=int)
    ap.add_argument('--az', type=float); ap.add_argument('--el', type=float); ap.add_argument('--d', type=float); ap.add_argument('--fov', type=float, default=42.0)
    ap.add_argument('--wide', action='store_true'); ap.add_argument('--name')
    args = ap.parse_args()
    base = {**CLOSE, **(WIDE if args.wide else {})}
    for k in ('az', 'el', 'd'):
        if getattr(args, k) is None: setattr(args, k, base[k])
    city = os.path.abspath(args.city); slug = os.path.basename(os.path.normpath(city))
    if (args.name or args.era) == slug: raise SystemExit(f'modelview: build/review/modelview/{slug}/ is the study city itself: give the stills another --name')
    if not os.path.isfile(os.path.join(city, 'city.yaml')): raise SystemExit(f'modelview: {args.city}: no city.yaml here (give the city folder, cities/<slug>)')
    if not os.path.isfile(LAYOUT.data(city, 'model.json')): raise SystemExit(f'modelview: {args.city} has not been prepared: run pipeline/prep.py first')
    try: os.nice(10)   # (compile and the browser after it: the desktop stays usable)
    except OSError: pass
    C = yaml.safe_load(open(os.path.join(city, 'city.yaml'), encoding='utf-8'))
    spec = None
    if args.spec:
        spec = yaml.safe_load(open(args.spec, encoding='utf-8'))
        if isinstance(spec, dict) and 'city' in spec: spec = spec['city']
        if not isinstance(spec, dict): raise SystemExit(f'modelview: {args.spec} holds no city: block')
    sh = shots(args)
    S = study_folder(city, slug)
    yaml.safe_dump(study_film(C, args.era, spec, sh, args.fov, args.year), open(os.path.join(S, 'city.yaml'), 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False)
    env = {**{k: v for k, v in os.environ.items() if k not in ('CT_SCRIPT', 'CT_PLAN', 'CT_PASS')},   # (a draft script or a plan of the real film is not the study's)
           'CT_STUDY': '1', 'CT_DEADAIR': 'warn'}   # (compile: the city rises without the camera; a film without words)
    LAYOUT.ensure(S)
    r = run([sys.executable, '-I', 'pipeline/compile.py', S], LAYOUT.logs(S, 'compile.log'), env)
    if r.returncode:
        print(r.stdout[-3000:]); raise SystemExit(f'modelview: compile of the study failed (log: {os.path.relpath(LAYOUT.logs(S, "compile.log"), ROOT)})')
    FILM = json.load(open(LAYOUT.build(S, 'film.json'), encoding='utf-8'))
    node = next(n for n in FILM['nodes'] if n['id'] == args.era); era = next((e for e in FILM['eras'] if e['id'] == args.era), None)
    if era is None: raise SystemExit(f'modelview: the city of {args.era} came out empty (no buildings): see {os.path.relpath(LAYOUT.logs(S, "compile.log"), ROOT)}')
    up = era['on'] + era['span'] + era['grow']
    t = round(min(node['t1'] - .2, max(up + 1.0, FILM['light']['lamp'] + 2.5)), 2)
    if t < up: print(f'WARNING: {args.era} is still rising when its node ends ({up:.1f} s > {node["t1"]:.1f} s): the stills show it unfinished')
    # each still's camera as compile landed it (the ground under --at, at the film's terrain exaggeration)
    Fr = geo.Frame(tuple(C['box']), 1.0 / C['scale']); cams = []
    for s in sh:
        x, z = Fr.model_lonlat(*s['ll'])
        k = next((v for tk, v in FILM['camera'] if node['t0'] - 1e-3 <= tk <= node['t1'] + 1e-3 and abs(v[0] - x) < 2e-5 and abs(v[2] - z) < 2e-5 and v[3:6] == [s['az'], s['el'], s['d']]), None)
        if k is None: raise SystemExit(f'modelview: the camera key for --at {s["ll"]} is not in the study film (compile changed it)')
        cams.append(k)
    rc = run([sys.executable, '-I', 'tools/clipcheck.py', S], LAYOUT.logs(S, 'clipcheck.log'))
    print((rc.stdout.strip().splitlines() or ['clipcheck: no output'])[-1] + f'  ({os.path.relpath(LAYOUT.logs(S, "clipcheck.log"), ROOT)})')
    out = LAYOUT.review(city, 'modelview', args.name or args.era); os.makedirs(out, exist_ok=True)
    bundle = os.path.relpath(S, ROOT).replace(os.sep, '/') + '/'
    for i, (s, v) in enumerate(zip(sh, cams), 1):
        q = f'bundle={bundle}&cam=' + ','.join(f'{x:g}' for x in v)
        r = run(['node', 'render/still.mjs', slug, f'{t:.2f}', '--q', q, '--out', out, '--prefix', f'{i}_'], LAYOUT.logs(S, f'still_{i}.log'))
        if r.returncode: print(r.stdout[-2000:]); raise SystemExit('modelview: the still failed')
        print(f'{os.path.relpath(os.path.join(out, f"{i}_{t:.2f}.jpg"), ROOT)}   at {s["ll"][0]:.5f},{s["ll"][1]:.5f} az {s["az"]:g} el {s["el"]:g} d {s["d"]:g}')
        print(f'    in the preview (node tools/preview.mjs {slug}): http://127.0.0.1:8765/play.html?city={slug}&t={t:.2f}&{q}')
    print(f'{args.era}: risen at {up:.1f} s of the study, stills at {t:.2f} s')


if __name__ == '__main__':
    main()

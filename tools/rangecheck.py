"""After a change, every check of the stretch it touched in one command (docs/CHECKS.md "After every change"): the camera
(tools/camcheck.mjs, then camcheck.py), the text (tools/readcheck.mjs), a still every --step seconds (render/still.mjs) laid out
in contact sheets of 16 (tools/sheet.py), and the stills' brightness (YAVG as docs/CHECKS.md "Brightness" counts it). The steps
run one after another, each into its own log; a failed one does not stop the rest. The checks cannot see composition, speed or
darkness: look at every sheet.
usage: python -I tools/rangecheck.py <city_slug | city folder> (--stations id[,id..] | --from s --to s) [--step 1] [--size 960x540] [--no-stills]
  --stations  those stations and one before and one after each, the range a change touches (docs/CHECKS.md)
  a city folder: a model study's or any folder under cities/ (tools/geocheck.mjs takes the same)
writes build/review/range_<from>_<to>/ (the stills, sheet_NN.jpg, report.json) and build/logs/range_<step>.log; exit 1 when a
check fails."""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser(description='every check of one stretch of the film (tools/rangecheck.py docstring)')
    ap.add_argument('city'); ap.add_argument('--stations'); ap.add_argument('--from', dest='a', type=float); ap.add_argument('--to', dest='b', type=float)
    ap.add_argument('--step', type=float, default=1.0); ap.add_argument('--size', default='960x540'); ap.add_argument('--no-stills', action='store_true')
    A = ap.parse_args()
    D = os.path.abspath(A.city) if '/' in A.city else os.path.join(ROOT, 'cities', A.city)
    slug = os.path.relpath(D, os.path.join(ROOT, 'cities'))   # (the Node tools take a city by its folder under cities/)
    if slug.startswith('..'): sys.exit(f'rangecheck: {D} is not under {ROOT}/cities (the Node tools find a city there)')
    film = json.load(open(os.path.join(D, 'build', 'film.json'), encoding='utf-8')); nodes = film['nodes']
    if A.stations:
        ids = [n['id'] for n in nodes]; want = A.stations.split(',')
        miss = [s for s in want if s not in ids]
        if miss: sys.exit(f"rangecheck: no station {', '.join(miss)} (the film has {', '.join(ids)})")
        k = [ids.index(s) for s in want]; lo, hi = max(0, min(k) - 1), min(len(nodes) - 1, max(k) + 1)
        a, b = nodes[lo]['t0'], nodes[hi]['t1']
    elif A.a is not None and A.b is not None: a, b = A.a, A.b
    else: sys.exit('rangecheck: give --stations, or --from and --to')
    a, b = round(a, 2), round(b, 2)
    logs = os.path.join(D, 'build', 'logs'); out = os.path.join(D, 'build', 'review', f'range_{a:g}_{b:g}'); os.makedirs(logs, exist_ok=True); os.makedirs(out, exist_ok=True)
    print(f'rangecheck: {slug} {a:g}-{b:g} s', flush=True)
    steps = {}

    def run(name, cmd):
        log = os.path.join(logs, f'range_{name}.log')
        with open(log, 'w', encoding='utf-8') as f: r = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
        last = ([l for l in open(log, encoding='utf-8').read().splitlines() if l.strip()] or [''])[-1]
        steps[name] = {'ok': r.returncode == 0, 'log': os.path.relpath(log, ROOT), 'last': last[:300]}
        print(f"  {'ok  ' if r.returncode == 0 else 'FAIL'} {name}: {last[:160]}", flush=True)

    rng = ['--from', f'{a:g}', '--to', f'{b:g}']
    run('camdump', ['node', 'tools/camcheck.mjs', slug, *rng])
    run('camcheck', [sys.executable, '-I', 'tools/camcheck.py', D])
    run('readcheck', ['node', 'tools/readcheck.mjs', slug, *rng])
    report = {'city': slug, 'from': a, 'to': b, 'steps': steps}
    if not A.no_stills:
        for f in os.listdir(out):
            if f.startswith(('t_', 'sheet_')) and f.endswith('.jpg'): os.remove(os.path.join(out, f))   # (a range checked again: the last run's stills only)
        run('stills', ['node', 'render/still.mjs', slug, '--range', f'{a:g}:{b:g}:{A.step:g}', '--size', A.size, '--out', out, '--prefix', 't_'])
        ims = sorted((f for f in os.listdir(out) if f.startswith('t_') and f.endswith('.jpg')), key=lambda f: float(f[2:-4]))
        sheets = []
        for i in range(0, len(ims), 16):
            s = os.path.join(out, f'sheet_{i // 16:02d}.jpg'); sheets.append(os.path.relpath(s, ROOT))
            run(f'sheet_{i // 16:02d}', [sys.executable, '-I', 'tools/sheet.py', s, *[os.path.join(out, f) for f in ims[i:i + 16]], '--cols', '4', '--w', '480'])
        # brightness: Y of each still on the video scale (black 16, white 235), as signalstats YAVG reads the rendered film
        Y = []
        for f in ims:
            c = np.asarray(Image.open(os.path.join(out, f)).convert('RGB').resize((320, 180)), dtype=float)
            Y.append((float(f[2:-4]), 16 + float((65.481 * c[..., 0] + 128.553 * c[..., 1] + 24.966 * c[..., 2]).mean()) / 255))
        n60 = max(1, round(60 / A.step)); win = [sum(y for _, y in Y[i:i + n60]) / len(Y[i:i + n60]) for i in range(max(1, len(Y) - n60 + 1))] if Y else []
        # (the threshold judged on the unrounded value and shown cut down, never rounded up: a minute of 59.996 printed as 60.0 read as a pass)
        cut = lambda v: math.floor(v * 100) / 100
        report.update({'stills': len(ims), 'sheets': sheets, 'yavg': cut(sum(y for _, y in Y) / len(Y)) if Y else None,
                       'yavg_lowest_minute': cut(min(win)) if win else None, 'minute_below_60': min(win) < 60 if win else None,
                       'yavg_per_still': [[t, round(y, 1)] for t, y in Y]})
        if Y: print(f"  brightness: YAVG {report['yavg']} (lowest minute {report['yavg_lowest_minute']}{': BELOW 60' if report['minute_below_60'] else ''};"
                    " the film's mean wants 80 and any minute 60)", flush=True)
        print(f'  look at every sheet: {", ".join(sheets)}', flush=True)
    json.dump(report, open(os.path.join(out, 'report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    bad = [k for k, v in steps.items() if not v['ok']]
    print(f"rangecheck: {'failed: ' + ', '.join(bad) if bad else 'all checks passed'} ({os.path.relpath(out, ROOT)}/report.json)", flush=True)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()

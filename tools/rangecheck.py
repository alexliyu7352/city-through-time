"""After a change, every check of the stretches it touched in one command (docs/CHECKS.md "After every change"): the camera
(tools/camcheck.mjs, then camcheck.py), the text (tools/readcheck.mjs), a still every --step seconds (render/still.mjs) laid out
in contact sheets of 16 (tools/sheet.py) and line by line (tools/linesheet.py: each line's stills under its words), and the stills'
brightness (YAVG as docs/CHECKS.md "Brightness" counts it). The steps run one after another, each into its own log; a failed one does
not stop the rest. The checks cannot see composition, speed or darkness: look at every sheet.
usage: python -I tools/rangecheck.py <city_slug | city folder> (--stations id[,id..] | --from s --to s [--from s --to s ..]) [--step 1] [--size 960x540] [--no-stills] [--against <city>]
  --stations  each of those stations with one before and one after it, the range a change touches (docs/CHECKS.md)
  --from/--to a stretch; more than once (in pairs) for every stretch a change touched, with --stations too. Give them all in one
              command: each tool loads the film once for all of them (the load, not the stretch, is most of a short stretch's
              time), and each stretch is still checked on its own, as if alone. Stretches that overlap or touch are one
  --against   the previous version (a candidate, a model study): the line sheets show its stills of each line beside this one's
  a city folder: a model study's or any folder under cities/ (tools/geocheck.mjs takes the same)
writes, for each stretch, build/review/range_<from>_<to>/ (the stills, sheet_NN.jpg, report.json and its steps' logs) and
build/review/lines_<from>_<to>/; the tools' own logs and files build/logs/range_*. One rangecheck of a city at a time: a second
waits for the first (build/logs/rangecheck.lock), whose files it would overwrite. Exit 1 when a check of any stretch fails."""
import argparse, fcntl, json, math, os, signal, subprocess, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from linesheet import STAMP, stamp


def main():
    ap = argparse.ArgumentParser(description='every check of the stretches a change touched (tools/rangecheck.py docstring)')
    ap.add_argument('city'); ap.add_argument('--stations'); ap.add_argument('--from', dest='a', type=float, action='append', default=[]); ap.add_argument('--to', dest='b', type=float, action='append', default=[])
    ap.add_argument('--step', type=float, default=1.0); ap.add_argument('--size', default='960x540'); ap.add_argument('--no-stills', action='store_true'); ap.add_argument('--against')
    A = ap.parse_args()
    D = os.path.abspath(A.city) if '/' in A.city else os.path.join(ROOT, 'cities', A.city)
    slug = os.path.relpath(D, os.path.join(ROOT, 'cities'))   # (the Node tools take a city by its folder under cities/)
    if slug.startswith('..'): sys.exit(f'rangecheck: {D} is not under {ROOT}/cities (the Node tools find a city there)')
    film = json.load(open(os.path.join(D, 'build', 'film.json'), encoding='utf-8')); nodes = film['nodes']
    want = []
    if A.stations:
        ids = [n['id'] for n in nodes]; asked = A.stations.split(',')
        miss = [s for s in asked if s not in ids]
        if miss: sys.exit(f"rangecheck: no station {', '.join(miss)} (the film has {', '.join(ids)})")
        for k in (ids.index(s) for s in asked): want.append((nodes[max(0, k - 1)]['t0'], nodes[min(len(nodes) - 1, k + 1)]['t1']))
    if len(A.a) != len(A.b): sys.exit('rangecheck: give --from and --to in pairs, one pair a stretch')
    want += list(zip(A.a, A.b))
    if not want: sys.exit('rangecheck: give --stations, or --from and --to')
    if any(b < a for a, b in want): sys.exit('rangecheck: a stretch ends before it starts')
    SP = []   # the stretches, overlapping or touching ones merged
    for a, b in sorted((round(a, 2), round(b, 2)) for a, b in want):
        if SP and a <= SP[-1][1]: SP[-1][1] = max(SP[-1][1], b)
        else: SP.append([a, b])
    logs = os.path.join(D, 'build', 'logs'); os.makedirs(logs, exist_ok=True)
    outs = [os.path.join(D, 'build', 'review', f'range_{a:g}_{b:g}') for a, b in SP]
    said = ', '.join(f'{a:g}-{b:g}' for a, b in SP)
    lock = open(os.path.join(logs, 'rangecheck.lock'), 'a+')   # (let go when this process ends, however it ends)
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lock.seek(0); print(f'rangecheck: {slug} {said} s waits: another rangecheck of it is running ({lock.read().strip() or "?"}), and two at once would overwrite each other\'s files', flush=True)
        fcntl.flock(lock, fcntl.LOCK_EX)
    lock.seek(0); lock.truncate(); lock.write(f'pid {os.getpid()}: {said} s\n'); lock.flush()
    print(f'rangecheck: {slug} {said} s', flush=True)
    for o in outs:
        os.makedirs(o, exist_ok=True)
        for f in os.listdir(o):
            if f.endswith('.log'): os.remove(os.path.join(o, f))   # (the steps' logs of the last run of this stretch)
    steps = [{} for _ in SP]
    J = lambda name: os.path.join(logs, f'range_{name}_stretches.json')   # (a tool's result for each stretch, --json)

    def run(name, cmd, log=None, into=None):   # a tool's run -> its step (into: the stretches it counts for, all by default)
        log = log or os.path.join(logs, f'range_{name}.log')
        with open(log, 'w', encoding='utf-8') as f: r = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
        if r.returncode < 0:   # killed by a signal (a crash leaves the log empty; a Python step's traceback is faulthandler's, above)
            with open(log, 'a', encoding='utf-8') as f: f.write(f'\nrangecheck: {name} was killed by {signal.Signals(-r.returncode).name}: run it again; a second crash on the same input: report it with this log and the kernel log line (dmesg)\n')
        last = ([l for l in open(log, encoding='utf-8').read().splitlines() if l.strip()] or [''])[-1]
        st = {'ok': r.returncode == 0, 'log': os.path.relpath(log, ROOT), 'last': last[:300]}
        for i in (range(len(SP)) if into is None else into): steps[i][name] = st
        print(f"  {'ok  ' if r.returncode == 0 else 'FAIL'} {name}: {last[:160]}", flush=True)
        return st

    def split(name):   # a tool that wrote each stretch's result (--json): each stretch its own step and log; else (it died) the run's
        try: res = json.load(open(J(name), encoding='utf-8'))
        except (OSError, ValueError): return
        if len(res) != len(SP): return
        for i, r in enumerate(res):
            log = os.path.join(outs[i], f'{name}.log'); open(log, 'w', encoding='utf-8').write('\n'.join(r['lines']) + '\n')
            steps[i][name] = {'ok': r['ok'], 'log': os.path.relpath(log, ROOT), 'last': ([l for l in r['lines'] if l.strip()] or [''])[-1][:300]}
            if len(SP) > 1: print(f"    {'ok  ' if r['ok'] else 'FAIL'} {SP[i][0]:g}-{SP[i][1]:g}: {steps[i][name]['last'][:150]}", flush=True)

    rng = [x for a, b in SP for x in ('--from', f'{a:g}', '--to', f'{b:g}')]
    py = [sys.executable, '-I', '-X', 'faulthandler']
    cam = os.path.join(logs, 'range_cam.json')
    for f in (cam, J('camcheck'), J('readcheck'), J('lines')):
        if os.path.exists(f): os.remove(f)   # (a tool that fails leaves no last run's file to be read as this one's)
    run('camdump', ['node', 'tools/camcheck.mjs', slug, *rng, '--out', cam])
    run('camcheck', [*py, 'tools/camcheck.py', D, '--cam', cam, '--out', os.path.join(logs, 'range_camcheck.json'), '--json', J('camcheck')]); split('camcheck')
    run('readcheck', ['node', 'tools/readcheck.mjs', slug, *rng, '--json', J('readcheck')]); split('readcheck')
    reports = [{'city': slug, 'from': a, 'to': b, 'steps': steps[i]} for i, (a, b) in enumerate(SP)]
    if not A.no_stills:
        for out in outs:
            for f in os.listdir(out):
                if f.startswith(('t_', 'sheet_')) and f.endswith('.jpg') or f == STAMP: os.remove(os.path.join(out, f))   # (a range checked again: the last run's stills only)
        made = stamp(D)   # (the version the stills are of: tools/linesheet.py takes a folder's stills only for that version as it is then)
        if run('stills', ['node', 'render/still.mjs', slug, *[x for (a, b), out in zip(SP, outs) for x in ('--range', f'{a:g}:{b:g}:{A.step:g}', '--out', out)], '--size', A.size, '--prefix', 't_'])['ok']:
            for out in outs: open(os.path.join(out, STAMP), 'w').write(made + '\n')
        IMS = []
        for i, out in enumerate(outs):
            ims = sorted((f for f in os.listdir(out) if f.startswith('t_') and f.endswith('.jpg')), key=lambda f: float(f[2:-4])); IMS.append(ims)
            reports[i]['sheets'] = []
            for k in range(0, len(ims), 16):
                s = os.path.join(out, f'sheet_{k // 16:02d}.jpg'); reports[i]['sheets'].append(os.path.relpath(s, ROOT))
                run(f'sheet_{k // 16:02d}', [*py, 'tools/sheet.py', s, *[os.path.join(out, f) for f in ims[k:k + 16]], '--cols', '4', '--w', '480'], os.path.join(out, f'sheet_{k // 16:02d}.log'), [i])
        run('lines', [*py, 'tools/linesheet.py', D, *rng, '--size', A.size, '--json', J('lines'), *(['--against', os.path.abspath(A.against) if '/' in A.against else A.against] if A.against else [])]); split('lines')
        for i, ((a, b), out, ims) in enumerate(zip(SP, outs, IMS)):
            lines_ = os.path.join(D, 'build', 'review', f'lines_{a:g}_{b:g}')
            reports[i]['sheets'] += sorted(os.path.relpath(os.path.join(lines_, f), ROOT) for f in os.listdir(lines_) if f.startswith('lines_') and f.endswith('.jpg')) if os.path.isdir(lines_) else []
            # brightness: Y of each still on the video scale (black 16, white 235), as signalstats YAVG reads the rendered film
            Y = []
            for f in ims:
                c = np.asarray(Image.open(os.path.join(out, f)).convert('RGB').resize((320, 180)), dtype=float)
                Y.append((float(f[2:-4]), 16 + float((65.481 * c[..., 0] + 128.553 * c[..., 1] + 24.966 * c[..., 2]).mean()) / 255))
            n60 = max(1, round(60 / A.step)); win = [sum(y for _, y in Y[k:k + n60]) / len(Y[k:k + n60]) for k in range(max(1, len(Y) - n60 + 1))] if Y else []
            # (the threshold judged on the unrounded value and shown cut down, never rounded up: a minute of 59.996 printed as 60.0 read as a pass)
            cut = lambda v: math.floor(v * 100) / 100
            reports[i].update({'stills': len(ims), 'yavg': cut(sum(y for _, y in Y) / len(Y)) if Y else None,
                               'yavg_lowest_minute': cut(min(win)) if win else None, 'minute_below_60': min(win) < 60 if win else None,
                               'yavg_per_still': [[t, round(y, 1)] for t, y in Y]})
    failed = []
    for (a, b), out, R in zip(SP, outs, reports):   # each stretch's results
        json.dump(R, open(os.path.join(out, 'report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        bad = [k for k, v in R['steps'].items() if not v['ok']]
        if bad: failed.append(f"{a:g}-{b:g} ({', '.join(bad)})")
        if len(SP) > 1: print(f'stretch {a:g}-{b:g} s:', flush=True)
        if R.get('yavg') is not None: print(f"  brightness: YAVG {R['yavg']} (lowest minute {R['yavg_lowest_minute']}{': BELOW 60' if R['minute_below_60'] else ''};"
                                            " the film's mean wants 80 and any minute 60)", flush=True)
        if 'sheets' in R: print(f'  look at every sheet: {", ".join(R["sheets"])}', flush=True)
        print(f"rangecheck: {'failed: ' + ', '.join(bad) if bad else 'all checks passed'} ({os.path.relpath(out, ROOT)}/report.json)", flush=True)
    if len(SP) > 1: print(f"rangecheck: {len(SP)} stretches, {'failed in ' + '; '.join(failed) if failed else 'all checks passed in every one'}", flush=True)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()

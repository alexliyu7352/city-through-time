"""One round of changes, checked in one command (docs/CHECKS.md "After every change"): compile the city (pipeline/compile.py), list
where it now differs from the version before the round (tools/filmdiff.py), check every stretch that changed in one rangecheck
(each stretch on its own, the film loaded once: tools/rangecheck.py), then a short report: compile's faults, each stretch's verdict,
the lines the camera now shows from much farther than before, the period cities whose model changed (not checked here: look at
them with tools/eraview.mjs), the sheets to look at, and each step's time. It runs to the end by
itself: start it, wait for it once (it says at its start how long the last round of the city took), then read the report and look at
the sheets. A round is the whole list of changes made, then this once, not a run for each change.
usage: python -I tools/round.py <city_slug | city folder> --against <the version before the round> [--no-compile] [--step 1] [--size 960x540]
  --against     a city slug or folder: the approved version the round started from (not the last failed candidate)
  --no-compile  check the film as last compiled (its compile already ran in this round)
the compile's own settings (CT_PLAN, CT_DEADAIR, ...) pass through from the environment. Writes build/logs/round.json (the report)
and build/logs/round_<step>.log; one round of a city at a time (build/logs/round.lock). Exit 1 when compile or a check fails: a
compile that fails stops the round (fix every FAULT it lists, then run the round again)."""
import argparse, fcntl, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser(description='one round of changes, compiled and checked (tools/round.py docstring)')
    ap.add_argument('city'); ap.add_argument('--against', required=True); ap.add_argument('--no-compile', action='store_true')
    ap.add_argument('--step', default='1'); ap.add_argument('--size', default='960x540')
    A = ap.parse_args()
    D = os.path.abspath(A.city) if '/' in A.city else os.path.join(ROOT, 'cities', A.city)
    P = os.path.abspath(A.against) if '/' in A.against else os.path.join(ROOT, 'cities', A.against)
    for d_ in (D, P):
        if not os.path.exists(os.path.join(d_, 'build', 'film.json')) and not (d_ == D and not A.no_compile): sys.exit(f'round: no build/film.json in {d_}')
    logs = os.path.join(D, 'build', 'logs'); os.makedirs(logs, exist_ok=True)
    lock = open(os.path.join(logs, 'round.lock'), 'a+')
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: sys.exit(f'round: another round of {D} is running (build/logs/round.lock): wait for it, two would write the same build')
    RJ = os.path.join(logs, 'round.json')
    try: last = json.load(open(RJ, encoding='utf-8'))['seconds']; print(f'round: the last round of this city took {last / 60:.1f} min', flush=True)
    except (OSError, ValueError, KeyError): pass
    T0 = time.time(); steps = {}; py = [sys.executable, '-I', '-X', 'faulthandler']

    def run(name, cmd):
        log = os.path.join(logs, f'round_{name}.log'); t = time.time()
        print(f'round: {name} ...', flush=True)
        with open(log, 'w', encoding='utf-8') as f: r = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
        text = open(log, encoding='utf-8').read().splitlines()
        steps[name] = {'ok': r.returncode == 0, 'seconds': round(time.time() - t, 1), 'log': os.path.relpath(log, ROOT)}
        print(f"round: {name} {'ok' if r.returncode == 0 else 'FAILED'} in {(time.time() - t) / 60:.1f} min ({steps[name]['log']})", flush=True)
        return r.returncode, text

    def done(code, **more):
        rep = {'city': os.path.relpath(D, ROOT), 'against': os.path.relpath(P, ROOT), 'seconds': round(time.time() - T0, 1), 'steps': steps, **more}
        json.dump(rep, open(RJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f"round: {'all done, look at the sheets' if code == 0 else 'stopped'} after {(time.time() - T0) / 60:.1f} min (build/logs/round.json)", flush=True)
        sys.exit(code)

    if not A.no_compile:
        rc, text = run('compile', [*py, 'pipeline/compile.py', D])
        faults = [l.strip() for l in text if l.strip().startswith('FAULT ')]
        if rc:
            for l in faults or [l for l in text if l.startswith('compile:')][-1:] or text[-3:]: print('  ' + l[:400], flush=True)
            done(1, faults=faults)
    fd_json = os.path.join(logs, 'round_filmdiff.json')
    if os.path.exists(fd_json): os.remove(fd_json)
    rc, text = run('filmdiff', [*py, 'tools/filmdiff.py', P, D, '--json', fd_json])
    if rc or not os.path.exists(fd_json): print('\n'.join('  ' + l for l in text[-5:]), flush=True); done(1)
    FD = json.load(open(fd_json, encoding='utf-8'))
    print(f"round: {len(FD['stretches'])} stretch(es) changed against {os.path.relpath(P, ROOT)}", flush=True)
    for (a, b), w in zip(FD['stretches'], FD['what']): print(f'  {a:8.2f}-{b:8.2f}  {w[:150]}', flush=True)
    M, rest = FD.get('model', []), FD.get('rest', [])   # what filmdiff cannot place in time: not checked here, look at it yourself
    if M:
        print('round: the model changed (on screen for as long as the city stands: look at each city from every side with tools/eraview.mjs, this version and the last, then in the film where it shows it):', flush=True)
        for m in M: print(f"  {m['city']:28s} {m['on']:8.2f}-{m['off'] if m['off'] is not None else 'end':>8}  {', '.join(m['what'])}", flush=True)
    if rest: print(f"round: changed and placed nowhere by filmdiff (look where it matters): {', '.join(rest)}", flush=True)
    if not FD['stretches']: done(0, stretches=[], farther=FD['farther'], model=M, rest=rest)
    rng = [x for a, b in FD['stretches'] for x in ('--from', f'{a:.2f}', '--to', f'{b:.2f}')]
    rc, text = run('rangecheck', [*py, 'tools/rangecheck.py', D, *rng, '--against', P, '--step', A.step, '--size', A.size])
    SP = []   # the stretches as rangecheck merged them (its folders are named by them)
    for a, b in sorted((round(a, 2), round(b, 2)) for a, b in FD['stretches']):
        if SP and a <= SP[-1][1]: SP[-1][1] = max(SP[-1][1], b)
        else: SP.append([a, b])
    out = []
    for a, b in SP:
        try: R = json.load(open(os.path.join(D, 'build', 'review', f'range_{a:g}_{b:g}', 'report.json'), encoding='utf-8'))
        except (OSError, ValueError): R = {'steps': {'rangecheck': {'ok': False}}}
        bad = [k for k, v in R['steps'].items() if not v.get('ok')]
        out.append({'from': a, 'to': b, 'failed': bad, 'yavg': R.get('yavg'), 'minute_below_60': R.get('minute_below_60'), 'sheets': R.get('sheets', [])})
    print('round: each stretch', flush=True)
    for s in out: print(f"  {s['from']:8.2f}-{s['to']:8.2f}  {'FAILED ' + ', '.join(s['failed']) if s['failed'] else 'checks passed'}"
                        f"{'  (a minute below 60 YAVG)' if s['minute_below_60'] else ''}", flush=True)
    if FD['farther']:
        print('round: lines now seen from much farther than before (look at them first in the line sheets):', flush=True)
        for f in FD['farther']: print(f"  {f['line']:10s} {f['t']:8.2f} s  {f['before']:.3f} -> {f['now']:.3f}", flush=True)
    try: off = json.load(open(os.path.join(logs, 'pins_off.json'), encoding='utf-8'))
    except (OSError, ValueError): off = []
    if off:
        print('round: pins whose dot stands well above anything under it (is it on what it names? look at it there):', flush=True)
        for f in off: print(f"  {f['pin']:28s} {f['t']:8.2f} s  {f['above_m']:g} m up, {f['px']} px off", flush=True)
    print('round: the sheets, line by line beside the previous version (the checks cannot see composition: look at every one):', flush=True)
    for s in out: print('  ' + ', '.join(x for x in s['sheets'] if '/lines_' in x), flush=True)
    done(1 if any(s['failed'] for s in out) else 0, stretches=out, farther=FD['farther'], pins_off=off, model=M, rest=rest)


if __name__ == '__main__':
    main()

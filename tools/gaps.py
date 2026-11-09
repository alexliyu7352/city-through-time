"""Where the narration is silent and how its timing moved (docs/STAGING.md, the film's rhythm): from build/film.json, every gap
between one spoken line's end and the next line's start over --over seconds (the longest first, with the node they fall in and
what fills them: a picture, a living moment, the music alone), the longest gap of each node, and with --against the lines whose
start moved against another build, by how much.
    python -I tools/gaps.py cities/<slug> [--over 6] [--nodes <id> ...] [--against cities/<base>] [--json <out.json>]
A line is spoken from its t0 for `say` seconds (compile: the voice's own length); the film's last line runs to the end card."""
import argparse, json, os, sys


def film(city): return json.load(open(os.path.join(city, 'build', 'film.json')))


def node_at(F, t): return next((n['id'] for n in F.get('nodes', []) if n['t0'] <= t < n['t1']), '-')


def fillers(F, a, b):
    out = []
    for f in F.get('footage', []):
        if f['on'] < b and a < f['on'] + f['dur']: out.append(f"{f.get('mode', 'full')} {f['id']}")
    for L in F.get('living', []):
        on = L['on'] - L.get('arrive', 0); off = L['on'] + L.get('reveal', 0) + L.get('hold', 0) + L.get('out', 0)
        if on < b and a < off: out.append(f"living {L['id']}")
    return out


def main():
    ap = argparse.ArgumentParser(description='the narration\'s silences and its timing against another build')
    ap.add_argument('city'); ap.add_argument('--over', type=float, default=6.0); ap.add_argument('--nodes', nargs='*')
    ap.add_argument('--against'); ap.add_argument('--json')
    A = ap.parse_args()
    F = film(A.city); C = sorted(F.get('cues', []), key=lambda c: c['t0'])
    if not C: sys.exit(f'gaps: {A.city}: no lines in film.json')
    gaps = []
    for c, d in zip(C, C[1:]):
        a, b = c['t0'] + c.get('say', c['t1'] - c['t0']), d['t0']
        if b - a > 0: gaps.append({'from': round(a, 2), 'to': round(b, 2), 's': round(b - a, 2), 'after': c['id'], 'node': node_at(F, (a + b) / 2), 'fill': fillers(F, a, b)})
    if A.nodes: gaps = [g for g in gaps if g['node'] in A.nodes]
    long_ = sorted((g for g in gaps if g['s'] >= A.over), key=lambda g: -g['s'])
    print(f"{len(long_)} silences of {A.over:g} s or more" + (f" in {', '.join(A.nodes)}" if A.nodes else '') + ':')
    for g in long_: print(f"  {g['from']:8.2f}-{g['to']:8.2f} s  {g['s']:5.1f} s  after {g['after']:10s} in {g['node']}" + (f"  ({'; '.join(g['fill'])})" if g['fill'] else '  (the music alone)'))
    per = {}
    for g in gaps: per[g['node']] = max(per.get(g['node'], 0), g['s'])
    print('longest silence per node: ' + ', '.join(f"{n} {s:.1f}" for n, s in per.items()))
    moved = []
    if A.against:
        B = {c['id']: c['t0'] for c in film(A.against).get('cues', [])}
        moved = [{'line': c['id'], 'was': round(B[c['id']], 2), 'now': round(c['t0'], 2), 'by': round(c['t0'] - B[c['id']], 2)} for c in C if c['id'] in B and abs(c['t0'] - B[c['id']]) > .05]
        new_ = [c['id'] for c in C if c['id'] not in B]
        print(f"against {A.against}: {len(moved)} lines start elsewhere" + (f", {len(new_)} new ({', '.join(new_[:8])}{' ..' if len(new_) > 8 else ''})" if new_ else ''))
        steps = []   # where the shift changes: the place a change was made
        for m in moved:
            if not steps or abs(m['by'] - steps[-1]['by']) > .05: steps.append(m)
        for m in steps[:20]: print(f"  from {m['line']} ({m['was']} -> {m['now']} s): {m['by']:+.2f} s")
    if A.json: json.dump({'silences': gaps, 'moved': moved}, open(A.json, 'w'), indent=1)


if __name__ == '__main__':
    main()

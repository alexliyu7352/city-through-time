"""The audience pass, line by line (docs/CHECKS.md "Acceptance and reporting"): for each narration line of a stretch, the still near
its start and the still near its end under its words, and a silence of over 2 s as a row of its own, so each line can be read against
what is on screen as it is said. With --against, the previous version of the film beside it: the same line's stills there (lines
are matched by id, so a line that moved is still compared with itself), what read better before showing at a glance.
usage: python -I tools/linesheet.py <city_slug | city folder> --from s --to s [--from s --to s ..] [--stills DIR] [--against <city_slug | city folder>] [--size 960x540] [--json file]
  --from/--to  more than once (in pairs): each stretch sheeted on its own, the previous version's missing stills of all of them
               rendered on one page load
  --stills   the stills of this version, one stretch only (default: build/review/range_<from>_<to>/, which tools/rangecheck.py makes)
  --against  the previous version (a model study's folder too): its stills are taken from its build/review/range_*/ folders, and the
             seconds none of them has are rendered (render/still.mjs, into this version's lines folder)
  --json     each stretch's result: [{from, to, ok, lines}] (tools/rangecheck.py)
writes build/review/lines_<from>_<to>/lines_NN.jpg; exit 1 when a stretch could not be sheeted."""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAP = 2.0      # a silence longer than this between two lines gets a row of its own
NEAR = 0.6     # a still this close to the second wanted stands for it (rangecheck takes one a second)
TW, TH, CAP = 440, 248, 58
FONT = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'NotoSansSC-VF.ttf'), 15)   # (Latin and CJK: the first language may be either)


def city_dir(c):
    D = os.path.abspath(c) if '/' in c else os.path.join(ROOT, 'cities', c)
    slug = os.path.relpath(D, os.path.join(ROOT, 'cities'))   # (render/still.mjs takes a city by its folder under cities/)
    if slug.startswith('..'): sys.exit(f'linesheet: {D} is not under {ROOT}/cities (render/still.mjs finds a city there)')
    return D, slug


def stills_in(*dirs):   # {second: path} of the t_<s>.jpg stills in these folders
    have = {}
    for d in dirs:
        for f in os.listdir(d) if os.path.isdir(d) else []:
            if f.startswith('t_') and f.endswith('.jpg'):
                try: have.setdefault(float(f[2:-4]), os.path.join(d, f))
                except ValueError: pass
    return have


def nearest(have, t):   # (the second of the still taken, its path), or None
    k = min(have, key=lambda h: abs(h - t), default=None)
    return (k, have[k]) if k is not None and abs(k - t) <= NEAR else None


def wrap(text, width, lines=2):   # by the drawn width, not by characters (a CJK character is twice a Latin one)
    out, cur = [], ''
    for ch in text:
        if FONT.getlength(cur + ch) > width:
            out.append(cur); cur = ''
            if len(out) == lines: break
        cur += ch
    return out + ([cur] if cur and len(out) < lines else [])


def items(cues, a, b):   # (kind, id, t0, t1, caption): each line, and each silence over GAP after it
    cs = [c for c in cues if c['t1'] > a and c['t0'] < b]; out = []
    for i, c in enumerate(cs):
        out.append(('line', c['id'], c['t0'], c['t1'], f"{c['id']} [{c.get('node') or ''}] {c['t0']:.1f}-{c['t1']:.1f}: {c.get('a') or ''}"))
        if i + 1 < len(cs) and cs[i + 1]['t0'] - c['t1'] > GAP:
            n = cs[i + 1]; out.append(('gap', (c['id'], n['id']), c['t1'], n['t0'], f"SILENCE {c['t1']:.1f}-{n['t0']:.1f} ({n['t0'] - c['t1']:.1f} s), before {n['id']}"))
    return out


def seconds(t0, t1):   # the two seconds shown for a line or a silence: just after it starts and just before it ends
    return [t0 + .6, t1 - .6] if t1 - t0 > 1.6 else [(t0 + t1) / 2] * 2


def main():
    ap = argparse.ArgumentParser(description='the audience pass, line by line (tools/linesheet.py docstring)')
    ap.add_argument('city'); ap.add_argument('--from', dest='a', type=float, action='append', required=True); ap.add_argument('--to', dest='b', type=float, action='append', required=True)
    ap.add_argument('--stills'); ap.add_argument('--against'); ap.add_argument('--size', default='960x540'); ap.add_argument('--json')
    A = ap.parse_args()
    if len(A.a) != len(A.b): sys.exit('linesheet: give --from and --to in pairs, one pair a stretch')
    if A.stills and len(A.a) > 1: sys.exit('linesheet: --stills is for one stretch (several: each from its own build/review/range_<from>_<to>/)')
    D, _ = city_dir(A.city)
    cues = json.load(open(os.path.join(D, 'build', 'film.json'), encoding='utf-8'))['cues']
    if A.against:
        D2, slug2 = city_dir(A.against)
        prev = {c['id']: c for c in json.load(open(os.path.join(D2, 'build', 'film.json'), encoding='utf-8'))['cues']}
        rev = os.path.join(D2, 'build', 'review'); ranges2 = [os.path.join(rev, d) for d in sorted(os.listdir(rev)) if d.startswith('range_')] if os.path.isdir(rev) else []
    S = []   # each stretch: what its sheets need, or why it has none
    for a, b in zip(A.a, A.b):
        a, b = round(a, 2), round(b, 2); st = {'from': a, 'to': b, 'lines': []}; S.append(st)
        sdir = A.stills or os.path.join(D, 'build', 'review', f'range_{a:g}_{b:g}')
        st['have'] = stills_in(sdir)
        if not st['have']: st['fail'] = f'linesheet: no stills in {sdir}: run tools/rangecheck.py --from {a:g} --to {b:g} first, or give --stills'; continue
        out = st['out'] = os.path.join(D, 'build', 'review', f'lines_{a:g}_{b:g}'); os.makedirs(out, exist_ok=True)
        for f in os.listdir(out):
            if f.startswith('lines_') and f.endswith('.jpg'): os.remove(os.path.join(out, f))   # (a stretch sheeted again: this run's sheets only)
        rows = st['rows'] = items(cues, a, b)
        old = st['old'] = {}   # item key -> the previous version's (t0, t1), and its stills
        if A.against:
            for kind, key, *_ in rows:
                if kind == 'line' and key in prev: old[key] = (prev[key]['t0'], prev[key]['t1'])
                elif kind == 'gap' and key[0] in prev and key[1] in prev: old[key] = (prev[key[0]]['t1'], prev[key[1]]['t0'])
            st['adir'] = os.path.join(out, 'against', slug2.replace('/', '_'))   # (renders kept per previous version)
            st['have2'] = stills_in(st['adir'], *ranges2)
            st['want'] = sorted({f'{t:.2f}' for t0, t1 in old.values() for t in seconds(t0, t1) if nearest(st['have2'], t) is None})
    todo = [st for st in S if st.get('want')]
    if todo:   # the previous version's missing stills, every stretch's on one page load, each into its own lines folder
        for st in todo: st['lines'].append(f"linesheet: rendering {len(st['want'])} stills of {slug2} that its range folders do not have"); print(st['lines'][-1], flush=True)
        r = subprocess.run(['node', 'render/still.mjs', slug2, *[x for st in todo for x in (*st['want'], '--out', st['adir'])], '--size', A.size, '--prefix', 't_'], cwd=ROOT, stdout=subprocess.DEVNULL)
        for st in todo:
            if r.returncode: st['fail'] = f'linesheet: render/still.mjs {slug2} failed ({r.returncode})'
            else: st['have2'] = {**st['have2'], **stills_in(st['adir'])}
    for st in S:
        if 'fail' in st: st['lines'].append(st['fail']); print(st['fail'], file=sys.stderr, flush=True); continue
        rows, old, have, have2, out = st['rows'], st['old'], st['have'], st.get('have2'), st['out']
        per = 7 if A.against else 14   # (one item a row against the previous version, two a row without)
        sheets = []
        for si in range(0, len(rows), per):
            group = rows[si:si + per]; n_rows = len(group) if A.against else (len(group) + 1) // 2
            im = Image.new('RGB', (4 * TW + 30, n_rows * (TH + CAP) + 10), (20, 20, 20)); d = ImageDraw.Draw(im)
            for j, (kind, key, t0, t1, cap) in enumerate(group):
                x0, y0 = (0, j * (TH + CAP)) if A.against else ((j % 2) * (2 * TW + 20), (j // 2) * (TH + CAP))
                pairs = [(have, t, 'now') for t in seconds(t0, t1)]
                if A.against: pairs += [(have2, t, 'before') for t in seconds(*old[key])] if key in old else [(None, None, 'before: no such line')] * 2
                for q, (h, t, tag) in enumerate(pairs):
                    x = x0 + q * TW + (20 if q >= 2 else 0); hit = nearest(h, t) if h else None
                    if hit: im.paste(Image.open(hit[1]).convert('RGB').resize((TW, TH)), (x, y0))
                    lab = f'{tag} {hit[0]:.2f}' if hit else tag if t is None else f'{tag} {t:.2f}: no still'
                    d.rectangle((x, y0, x + FONT.getlength(lab) + 8, y0 + 20), fill=(0, 0, 0)); d.text((x + 4, y0 + 1), lab, fill=(255, 220, 0) if tag == 'now' else (120, 200, 255), font=FONT)
                d.text((x0 + 2, y0 + TH + 2), '\n'.join(wrap(cap, (4 * TW + 20 if A.against else 2 * TW) - 8)), fill=(255, 120, 120) if kind == 'gap' else (230, 230, 230), font=FONT)
            s = os.path.join(out, f'lines_{si // per:02d}.jpg'); im.save(s, quality=82); sheets.append(os.path.relpath(s, ROOT))
        st['lines'].append(f"linesheet: {len(rows)} lines and silences in {len(sheets)} sheets{' beside the previous version' if A.against else ''}: {', '.join(sheets)}"); print(st['lines'][-1], flush=True)
    if A.json: json.dump([{'from': st['from'], 'to': st['to'], 'ok': 'fail' not in st, 'lines': st['lines']} for st in S], open(A.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.exit(1 if any('fail' in st for st in S) else 0)


if __name__ == '__main__':
    main()

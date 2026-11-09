"""A candidate: a working copy of a city to try a change on, whole or cut to a few stations (docs/CHECKS.md "Report in
proportion"), compiled and checked against the version it was made from, then deleted once its change is carried back.
usage: python -I tools/candidate.py make <base slug | folder> <name> [--from <node>] [--through <node>] [--plan base|<file>] [--compile]
       python -I tools/candidate.py list
       python -I tools/candidate.py delete <name>
make    cities/<name>/ from the base. city.yaml and script.yaml: a whole candidate's are copied byte for byte (its change goes back
        by copying them back); a cut's (--from, --through: the nodes kept, the base's first and last by default) are written
        again, comments gone (its change goes back by hand). The base's other folders (research/, assets/ ...) are folders of
        links to its files: a file added in the candidate is its own, a file written through a link is the base's (replace that
        link by a copy first). build/data is copied (compile rewrites model.json and the terrain when it levels the ground,
        pipeline/grade.py, and a write through a link lands in the base), but for the imagery, which compile only reads (linked),
        and what compile makes again (the period cities, the masks: not brought). build/audio: the voice lines, the music takes
        and the one-shots linked into folders of the candidate's own (compile writes the voice track and the score beside them).
        The base's downloads are linked under the candidate's name in the raw folder (pipeline/layout.py raw: the OSM answers
        compile reads; without them a city's named outlines, decals and today's water are missing). The base's stage plan
        (--plan base: its build/logs/plan.json; or a file), the kept nodes' part of it, goes to plan_seed.json: the time compile
        inserts is then the base's, not found again and drifting. candidate.json says what the candidate is. --compile compiles
        it with that plan; every later compile and round of it takes the plan the same way:
          CT_PLAN="$(cat cities/<name>/plan_seed.json)" uv run python -I tools/round.py <name> --against <the version to compare>
        A cut is compared with the same cut of the base: make that one first, unchanged, then the candidate from it (make <cut> <name>).
list    the candidates (cities/*/candidate.json): base, cut, size on disk
delete  removes one (a folder with candidate.json and no file in git: never a city), listing what goes first; links are removed,
        never followed, and the raw link with them
A cut keeps its nodes and their lines. What the base does after its last node does not happen in it: a city or an epoch taken
back by a later node stands to the cut's end, losses, water states, glimpses and music cues timed later are left out, and so is
the closing flight (it starts from the film's last node). What came before its first node is gone: the prologue and the opening
(the first node's first camera key opens it), a readout going on from the node before, and what earlier nodes left standing
(their cities, lines and epochs, the water as it was, the music playing on): each is listed as a note, and --from an earlier
node keeps it. A city laid clear of an earlier one (avoid_eras) cannot be cut from it; a reference the cut cannot place stops
make before anything is written."""
import argparse, datetime, fcntl, json, os, re, shutil, subprocess, sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CITIES = os.path.join(ROOT, 'cities')
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import layout as LAYOUT

# build/data: what compile writes there every run (period cities, masks, decals, maps): made again, never brought
MADE = re.compile(r'(era_.+\.json|decal_\d+\.png|(hide|edge|keep|layers)\w*\.png|grow_t\.json|sites\.json|basins\.png|grounds\.png|locator\.png|water_then\.png)$')
# the large inputs compile only reads (the imagery, the land beyond the plate): linked. Everything else is copied
READ_ONLY = re.compile(r'(satellite\w*\.(png|jpg)|context16\.png)$')
SKIP_TOP = {'city.yaml', 'script.yaml', 'build', 'dist', 'candidate.json', 'plan_seed.json', '.gitignore',
            'entry.json', 'web'}   # (entry.json: tools/registry.mjs lists every cities/*/entry.json on the portal; web: a finished film's bundle)


def folder(arg):
    return os.path.abspath(arg) if '/' in arg else os.path.join(CITIES, arg)


def rel(p):
    return os.path.relpath(p, ROOT) if os.path.abspath(p).startswith(ROOT + os.sep) else os.path.abspath(p)


def base_of(m):   # (candidate.json keeps a base inside the project relative to it)
    return os.path.join(ROOT, m['base'])


def manifest(D):
    try: return json.load(open(os.path.join(D, 'candidate.json'), encoding='utf-8'))
    except (OSError, ValueError): return None


def candidates():
    return [(n, m) for n in sorted(os.listdir(CITIES)) for m in [manifest(os.path.join(CITIES, n))] if m]


def raw_dir(slug):
    """the city's own downloads (pipeline/layout.py raw), or None on a machine with no local/config.json yet"""
    import local
    try: return local.raw('cities', slug)
    except SystemExit: return None


def size(p):
    return sum(os.lstat(os.path.join(r, f)).st_size for r, _, fs in os.walk(p) for f in fs if not os.path.islink(os.path.join(r, f)))


def link_children(src, dst, skip=lambda n: False):
    """dst a folder of its own holding a link to each of src's entries (to where it really is: a base that is a candidate itself
    may go before this one does)"""
    os.makedirs(dst, exist_ok=True)
    for n in sorted(os.listdir(src)):
        if not skip(n): os.symlink(os.path.realpath(os.path.join(src, n)), os.path.join(dst, n))


# ------------------------------------------------------------------ the cut
def cut(C, S, a_id, b_id):
    """city.yaml C and script.yaml S cut, in place, to the nodes a_id..b_id -> (kept ids, notes on what the cut leaves out).
    Handled by key, never by value: a node id is also a source kind (rail), a sink style or a sound (burn)"""
    FM = C['film']; N = FM['nodes']; ids = [n['id'] for n in N]
    for x in (a_id, b_id):
        if x is not None and x not in ids: sys.exit(f'candidate: no node {x!r} in the base (nodes: {", ".join(ids)})')
    a, b = ids.index(a_id) if a_id else 0, ids.index(b_id) if b_id else len(ids) - 1
    if a > b: sys.exit(f'candidate: --from {ids[a]} comes after --through {ids[b]}')
    keep, before, after, last = set(ids[a:b + 1]), set(ids[:a]), set(ids[b + 1:]), ids[b]
    notes, SN = [], S.get('nodes') or {}
    lines = lambda nids: {q['id'] for i in nids for q in SN.get(i) or [] if isinstance(q, dict) and 'id' in q}
    items = lambda ns: {x['id'] for n in ns for k in ('routes', 'pins', 'footage', 'arrows', 'epochs', 'props', 'lines', 'areas', 'living')
                        for x in n.get(k) or [] if isinstance(x, dict) and 'id' in x}
    gone = (before | after) | lines(before | after) | (items(N[:a] + N[b + 1:]) - items(N[a:b + 1]))
    routes = {r['id'] for n in N[a:b + 1] for r in n.get('routes') or []}
    # what the earlier nodes leave standing when the cut starts (the candidate starts without it); a city goes at its until node's
    # start (+ until_plus), an epoch or a prop at its until node's end
    on_ = lambda x: x.get('until') in keep | after
    for n in N[:a]:
        cs, what = n.get('city') or {}, []
        if cs.get('persist') or cs.get('until') in after or (cs.get('until') in keep and (cs['until'] != ids[a] or float(cs.get('until_plus') or 0) > 0)):
            what.append('its city')
        what += [f'{k} {x["id"]}' for k in ('epochs', 'props', 'lines', 'routes') for x in n.get(k) or [] if x.get('persist') or on_(x)]
        if what: notes.append(f'{n["id"]} leaves standing into the cut: {", ".join(what)} (not in the candidate; --from {n["id"]} keeps it)')
    late_ = []
    for n in N[a:b + 1]:
        cs = n.get('city')
        if cs:
            out_ = [e for e in cs.get('avoid_eras') or [] if e not in keep]
            if out_: sys.exit(f'candidate: the city of {n["id"]} is laid clear of {", ".join(out_)} (avoid_eras), which the cut leaves out: its houses '
                              f'would not be the base\'s; start the cut at {ids[min((ids.index(e) for e in out_ if e in ids), default=a)]}')
            if cs.get('until') in after:   # stands to the cut's end, as through it in the base (compile warns of a city that persists:
                # that is this one). Not until its last node plus a long while: the fall and the burn would then be timed far past the end
                late_.append(f'{n["id"]} (until {cs.pop("until")})'); cs.pop('until_plus', None); cs['persist'] = True
            if cs.get('today_from') in after: cs.pop('today_from')
            for k, L in list(cs.items()):   # losses, hide regions, grounds ... timed in another node (at: {node, at})
                if not isinstance(L, list): continue
                at_ = lambda it: it['at'].get('node') if isinstance(it, dict) and isinstance(it.get('at'), dict) else None
                bad = [it.get('id') for it in L if at_(it) in before]
                if bad: sys.exit(f'candidate: node {n["id"]}: {k} {", ".join(map(str, bad))} timed in a node before its own')
                late = [it for it in L if at_(it) in after]
                if late: notes.append(f'{n["id"]}: {len(late)} of its {k} timed after the cut, left out ({", ".join(str(it.get("id")) for it in late[:6])}{" .." if len(late) > 6 else ""})')
                cs[k] = [it for it in L if at_(it) not in after]
        for k in ('epochs', 'props'):   # standing until a later node: to the cut's last
            for x in n.get(k) or []:
                if x.get('until') in after: x['until'] = last
        if (n.get('grow') or {}).get('counters_until') in after: n['grow']['counters_until'] = last
        if n.get('ghost'):
            if set(n['ghost']) - keep: notes.append(f'{n["id"]}: the ghost of {", ".join(sorted(set(n["ghost"]) - keep))} left out (its city is not in the cut)')
            n['ghost'] = [e for e in n['ghost'] if e in keep]
            if not n['ghost']: n.pop('ghost')
        for dc in n.get('decals') or []:
            if dc.get('skip'): dc['skip'] = [e for e in dc['skip'] if e in keep]
    if late_: notes.append(f'taken back after the cut, so standing to its end (compile\'s warning on a city that persists): {", ".join(late_)}')
    FM['nodes'] = N[a:b + 1]
    S['nodes'] = {k: v for k, v in SN.items() if k in keep}
    if isinstance(S.get('quiet'), dict): S['quiet'] = {k: v for k, v in S['quiet'].items() if k in keep}
    if a > 0:   # no film before the first node: no prologue, no opening line, an opening on the node's first view just long enough
        # for its lights to go out (compile: 1.2 s before the lamp, at the opening's end; earlier, their sound is laid before the film)
        k0 = next(iter(N[a].get('camera') or []), None)
        if k0 is None: sys.exit(f'candidate: the cut\'s first node {ids[a]} has no camera key of its own (a tour stop flies on from the view '
                                f'before it): start the cut at a node with one')
        ctx = [k for k in (FM.get('opening') or {}).get('context') or []] + [k for n in N[:a] for k in n.get('context') or []]
        FM.pop('prologue', None); S['prologue'] = []; S['opening'] = []
        FM['opening'] = {'dur': 1.2, 'camera': [{'t': 0, **{k: v for k, v in k0.items() if k in ('ll', 'v', 'y', 'az', 'el', 'd', 'fov')}}]}
        if ctx and float(ctx[-1]['a']) > 0: FM['opening']['context'] = [{'t': 0, 'a': ctx[-1]['a']}]   # (the land beyond the plate as the base leaves it)
        r = N[a].get('readout')
        if isinstance(r, dict) and r.pop('continues', None): notes.append(f'{ids[a]}: its readout went on from {ids[a - 1]}: here it opens a chapter of its own')
        nt = next((float(n['night']) for n in reversed(N[:a]) if 'night' in n), 0)
        if nt > 0: notes.append(f'{ids[a]}: the base comes into it at night {nt:g}; the cut comes in by day')
    elif FM.get('prologue') and {k.get('node') for k in FM['prologue'].get('scene') or []} - keep:
        FM.pop('prologue'); S['prologue'] = []; notes.append('the prologue shows moments after the cut: left out')
    if b < len(ids) - 1: (FM.get('closing') or {}).pop('camera', None)   # (the flight from the film's last view: a jump after another node)
    M = FM.get('music') or {}
    if M.get('cues'):
        ok = keep | ({'prologue'} if FM.get('prologue') else set())
        kept, out_ = [c for c in M['cues'] if c.get('node') in ok], [c for c in M['cues'] if c.get('node') not in ok]
        late = [c for c in out_ if c.get('node') in before or c.get('node') == 'prologue']
        if a > 0 and late and not any(c.get('node') == ids[a] for c in kept):
            notes.append(f'music: cue {late[-1].get("id")} plays into the cut from {late[-1].get("node")}: the cut starts without it')
        for c in kept:
            if c.get('continue') in {q.get('id') for q in out_}: c.pop('continue')
        if M.get('loop') in {q.get('id') for q in out_}: M.pop('loop')
        M['cues'] = kept; gone |= {c.get('id') for c in out_}
    WT, wt = FM.get('water_then') or [], []
    wt_gone = {w.get('id', f'water_then_{i}') for i, w in enumerate(WT) if w.get('from') not in keep}
    for i, w in enumerate(WT):
        wid = w.get('id', f'water_then_{i}')
        if w.get('from') not in keep:
            end = w.get('until') or next((q.get('from') for q in WT[i + 1:]), None)
            if w.get('from') in before and (end is None or end in after or (end in keep and end != ids[a])):
                notes.append(f'the water as it was, {wid} (from {w["from"]}), is on when the cut starts: not in the candidate')
            gone.add(wid); continue
        if w.get('until') in after: w.pop('until')
        g = w.get('glimpse')
        if g and (g.get('with') not in routes or g.get('to', 'today') in wt_gone):   # (to: today, today's water, is never gone)
            w.pop('glimpse'); notes.append(f'the water as it was, {wid}: its glimpse (with {g.get("with")}) is after the cut, left out')
        wt.append(w)
    if WT: FM['water_then'] = wt
    if isinstance(FM.get('emblem'), dict) and FM['emblem'].get('nodes'): FM['emblem']['nodes'] = [x for x in FM['emblem']['nodes'] if x in keep]
    # what is left naming something the cut left out is a form this cut does not know: stop rather than write a film that breaks
    REF, REFS, bad = {'node', 'until', 'today_from', 'from', 'counters_until', 'with', 'continue', 'loop', 'reuse'}, {'avoid_eras', 'ghost', 'skip', 'nodes'}, []
    def scan(x, path):
        if isinstance(x, dict):
            for k, v in x.items():
                if (k in REF and isinstance(v, str) and v in gone) or (k in REFS and isinstance(v, list) and any(isinstance(q, str) and q in gone for q in v)):
                    bad.append(f'{path}.{k}: {v}')
                scan(v, f'{path}.{k}')
        elif isinstance(x, list):
            for i, v in enumerate(x): scan(v, f'{path}[{i}]')
    scan(FM, 'film'); scan(S, 'script')
    if bad: sys.exit('candidate: these name what the cut leaves out, in a form tools/candidate.py does not place (teach cut() the form): ' + '; '.join(bad))
    return ids[a:b + 1], notes


# ------------------------------------------------------------------ make, list, delete
def make(A):
    B, D = folder(A.base), os.path.join(CITIES, A.name)
    if not re.fullmatch(r'[a-z0-9_]+', A.name): sys.exit(f'candidate: name {A.name!r}: lower-case letters, digits and _ (it is a slug: URLs and file names)')
    if os.path.lexists(D): sys.exit(f'candidate: {rel(D)} exists already')
    if not os.path.isfile(LAYOUT.data(B, 'model.json')): sys.exit(f'candidate: {rel(B)} has no build/data/model.json (prep it first, pipeline/prep.py)')
    whole = A.from_ is None and A.through is None
    C = yaml.safe_load(open(os.path.join(B, 'city.yaml'), encoding='utf-8'))
    S = yaml.safe_load(open(os.path.join(B, 'script.yaml'), encoding='utf-8')) if os.path.exists(os.path.join(B, 'script.yaml')) else None
    nodes, notes = [n['id'] for n in C['film']['nodes']], []
    if not whole:
        if S is None: sys.exit('candidate: a cut needs the base\'s script.yaml (the lines go with their nodes)')
        n0 = len(nodes); nodes, notes = cut(C, S, A.from_, A.through)
        whole = len(nodes) == n0   # (cut to all of it: a copy)
    pf = LAYOUT.logs(B, 'plan.json') if A.plan == 'base' else os.path.abspath(A.plan)
    try: plan = {k: v for k, v in json.load(open(pf, encoding='utf-8')).items() if k in nodes}
    except OSError:
        if A.plan != 'base': sys.exit(f'candidate: no plan file {pf}')
        plan = {}; notes.append(f'no stage plan at {rel(pf)}: compile finds the inserted time again (it may drift from the base\'s)')
    base_raw = raw_dir(os.path.basename(os.path.normpath(B)))
    raw = raw_dir(A.name) if base_raw and os.path.isdir(base_raw) else None
    if raw and os.path.lexists(raw): sys.exit(f'candidate: {raw} exists already (the raw folder of another city by this name)')
    try:
        os.makedirs(D)
        open(os.path.join(D, '.gitignore'), 'w').write('# a candidate (tools/candidate.py): never committed\n*\n')
        for f in ('city.yaml', 'script.yaml'):
            if whole and os.path.exists(os.path.join(B, f)): shutil.copy2(os.path.join(B, f), os.path.join(D, f))
            elif not whole: yaml.safe_dump(C if f == 'city.yaml' else S, open(os.path.join(D, f), 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=200)
        for n in sorted(os.listdir(B)):
            p = os.path.join(B, n)
            if n in SKIP_TOP: continue
            if os.path.isdir(p): link_children(p, os.path.join(D, n))
            else: shutil.copy2(p, os.path.join(D, n))
        os.makedirs(LAYOUT.data(D)); os.makedirs(LAYOUT.logs(D))
        for n in sorted(os.listdir(LAYOUT.data(B))):
            p = LAYOUT.data(B, n)
            if MADE.match(n): continue
            if READ_ONLY.match(n): os.symlink(os.path.realpath(p), LAYOUT.data(D, n))
            elif os.path.isdir(p): shutil.copytree(p, LAYOUT.data(D, n))
            else: shutil.copy2(p, LAYOUT.data(D, n))
        if os.path.exists(LAYOUT.logs(B, 'compile_time.json')): shutil.copy2(LAYOUT.logs(B, 'compile_time.json'), LAYOUT.logs(D, 'compile_time.json'))   # (compile says how long to wait)
        ab, ad = LAYOUT.audio(B), LAYOUT.audio(D)
        for sub, skip in (('voice', lambda n: n.startswith('track_')), ('sfx', lambda n: False), ('music', lambda n: n not in ('cand', 'code.wav'))):
            if os.path.isdir(os.path.join(ab, sub)): link_children(os.path.join(ab, sub), os.path.join(ad, sub), skip)
        if raw: os.makedirs(os.path.dirname(raw), exist_ok=True); os.symlink(os.path.realpath(base_raw), raw)
        json.dump(plan, open(os.path.join(D, 'plan_seed.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump({'base': rel(B), 'from': nodes[0] if not whole else None, 'through': nodes[-1] if not whole else None, 'nodes': len(nodes),
                   'plan': rel(pf), 'raw': raw, 'created': datetime.datetime.now().isoformat(timespec='seconds'), 'notes': notes},
                  open(os.path.join(D, 'candidate.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    except BaseException:   # (half a candidate is none: take back what was made)
        shutil.rmtree(D, ignore_errors=True)
        if raw and os.path.islink(raw): os.unlink(raw)
        raise
    print(f'candidate: {rel(D)} from {rel(B)}, ' + ('whole' if whole else f'nodes {nodes[0]} .. {nodes[-1]} ({len(nodes)})') +
          f', plan of {sum(len(v) for v in plan.values())} insertion(s) from {rel(pf)}, {size(D) / 2 ** 20:.0f} MB')
    for x in notes: print('  note: ' + x)
    print(f'  compile or check it with the plan: CT_PLAN="$(cat {rel(D)}/plan_seed.json)" uv run python -I tools/round.py {A.name} --against <the version to compare>')
    if A.compile:
        r = subprocess.run([sys.executable, '-I', '-X', 'faulthandler', os.path.join(ROOT, 'pipeline', 'compile.py'), D], cwd=ROOT,
                           env={**os.environ, 'CT_PLAN': json.dumps(plan)})
        sys.exit(r.returncode)


def show():
    rows = candidates()
    if not rows: return print('candidate: none (cities/*/candidate.json)')
    for n, m in rows:
        cut_ = f"{m['from']} .. {m['through']} ({m['nodes']} nodes)" if m.get('from') else f"whole ({m['nodes']} nodes)"
        print(f"{n:32s} of {m['base']:28s} {cut_:40s} {size(os.path.join(CITIES, n)) / 2 ** 20:7.0f} MB  {m.get('created', '')}"
              + ('' if os.path.isdir(base_of(m)) else '  (its base is gone)'))


def delete(A):
    D = os.path.join(CITIES, A.name); M = manifest(D)
    if os.path.islink(D) or not os.path.isdir(D) or M is None: sys.exit(f'candidate: {rel(D)} is no candidate (no candidate.json): delete removes only one this tool made')
    g = subprocess.run(['git', 'ls-files', '--', rel(D)], cwd=ROOT, capture_output=True, text=True)
    if g.returncode == 0 and g.stdout.strip(): sys.exit(f'candidate: {rel(D)} has files in git: a city, not a candidate')
    users = [n for n, m in candidates() if n != A.name and os.path.realpath(base_of(m)) == os.path.realpath(D)]
    if users: sys.exit(f'candidate: {", ".join(users)} made from {A.name} (their links reach into it): delete them first')
    lock = open(LAYOUT.logs(D, 'round.lock'), 'a+') if os.path.isdir(LAYOUT.logs(D)) else None
    try:
        if lock: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: sys.exit(f'candidate: a round of {A.name} is running (build/logs/round.lock): wait for it')
    print(f'candidate: removing {rel(D)} ({size(D) / 2 ** 20:.0f} MB of its own; links removed, not followed):')
    for n in sorted(os.listdir(D)):
        p = os.path.join(D, n)
        if os.path.islink(p): print(f'  {n} -> {os.readlink(p)}')
        elif os.path.isdir(p):
            k = sum(1 for r, ds, fs in os.walk(p) for f in fs + ds if os.path.islink(os.path.join(r, f)))
            print(f'  {n}/  {size(p) / 2 ** 20:.1f} MB' + (f', {k} link(s)' if k else ''))
        else: print(f'  {n}  {os.lstat(p).st_size / 1024:.0f} KB')
    raw = M.get('raw')
    if raw and os.path.islink(raw): print(f'  {raw} -> {os.readlink(raw)} (its raw link)')
    shutil.rmtree(D)   # (rmtree unlinks a link it meets inside, it never walks into one)
    if raw and os.path.islink(raw): os.unlink(raw)
    print('candidate: removed')


def main():
    ap = argparse.ArgumentParser(description='a working copy of a city to try a change on (tools/candidate.py docstring)')
    sp = ap.add_subparsers(dest='cmd', required=True)
    m = sp.add_parser('make'); m.add_argument('base'); m.add_argument('name'); m.add_argument('--from', dest='from_'); m.add_argument('--through')
    m.add_argument('--plan', default='base'); m.add_argument('--compile', action='store_true')
    sp.add_parser('list'); d = sp.add_parser('delete'); d.add_argument('name')
    A = ap.parse_args()
    {'make': make, 'list': lambda A: show(), 'delete': delete}[A.cmd](A)


if __name__ == '__main__':
    main()

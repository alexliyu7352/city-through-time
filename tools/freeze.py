"""An approved study kept exactly as it was approved, and checked later against the code as it is then.
A model study (tools/modelview.py) links its city's research/ and assets/ live, and is compiled by the code of the day: the sample
the user approved moves when a trace is edited or the generator changes, and nothing says so. freeze copies the study folder to
<name> beside it with the files its compile read (build/logs/inputs.json, compile writes it) as real copies, never links, and
writes FROZEN.json: those files' sha256, the era files', the code's commit. check compiles a copy of the frozen folder with the
code as it is and says whether every period city came out the same (the geometry, the order the buildings rise in aside).
usage: python -I tools/freeze.py <study folder> [--name <frozen folder name>]     (default <study>_frozen; never overwritten)
       python -I tools/freeze.py check <frozen folder>"""
import hashlib, json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()


def freeze(S, name=None):
    S = os.path.abspath(S); log = os.path.join(S, 'build', 'logs', 'inputs.json')
    if not os.path.isfile(log): sys.exit(f'freeze: {S} has no build/logs/inputs.json: compile it (with this version) first')
    J = json.load(open(log, encoding='utf-8')); inputs = J['inputs']
    moved = [p for p, h in inputs.items() if not os.path.isfile(os.path.join(S, p)) or sha(os.path.join(S, p)) != h]
    if moved: sys.exit(f'freeze: {", ".join(moved[:6])} changed since the study was compiled: compile it again, look at it, then freeze')
    Z = os.path.join(os.path.dirname(S), name or os.path.basename(S) + '_frozen')
    if os.path.exists(Z): sys.exit(f'freeze: {Z} exists: a frozen study is never overwritten (give another --name)')
    shutil.copytree(S, Z, symlinks=True, ignore=shutil.ignore_patterns('.study.lock'))
    for d in ('research', 'assets'):   # (the live links: replaced by the files compile read from them)
        p = os.path.join(Z, d)
        if os.path.islink(p): os.remove(p); os.makedirs(p)
    for p in inputs:
        dst = os.path.join(Z, p)
        if os.path.islink(os.path.dirname(dst)) or not os.path.isfile(dst) or os.path.islink(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.lexists(dst): os.remove(dst)
            shutil.copy2(os.path.join(S, p), dst)
    git = lambda *a: subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    eras = sorted(f for f in os.listdir(os.path.join(Z, 'build', 'data')) if f.startswith('era_'))
    man = {'study': os.path.relpath(S, ROOT), 'compiled_as_study': J['study'], 'inputs_sha256': inputs, 'eras_sha256': {f: sha(os.path.join(Z, 'build', 'data', f)) for f in eras},
           'code_commit': git('rev-parse', 'HEAD'), 'code_changed_since_commit': bool(git('status', '--porcelain', '--', 'pipeline', 'engine', 'tools'))}
    json.dump(man, open(os.path.join(Z, 'FROZEN.json'), 'w', encoding='utf-8'), indent=1)
    print(f'freeze: {os.path.relpath(Z, ROOT)} ({len(inputs)} input files copied, {len(eras)} period cities, code {man["code_commit"][:7]}{" + changes" if man["code_changed_since_commit"] else ""})')


def geometry(path):
    """an era file's records with the order they rise in left out (record field 10, its rank: it moves with the staging)"""
    J = json.load(open(path, encoding='utf-8'))
    return [p[:10] + p[11:] for p in J['prims']], J.get('lost')


def check(Z):
    Z = os.path.abspath(Z); man = json.load(open(os.path.join(Z, 'FROZEN.json'), encoding='utf-8'))
    with tempfile.TemporaryDirectory(dir=os.path.dirname(Z)) as T:   # (beside it: the Node tools find cities under cities/)
        W = os.path.join(T, 'city'); shutil.copytree(Z, W, symlinks=True)
        env = {**os.environ, 'CT_DEADAIR': 'warn', 'CT_MODELCHECK': 'warn', **({'CT_STUDY': '1'} if man['compiled_as_study'] else {})}   # (compiled as it was)
        r = subprocess.run([sys.executable, '-I', 'pipeline/compile.py', W], cwd=ROOT, env=env, capture_output=True, text=True)
        if r.returncode: sys.exit(f'freeze check: the frozen study no longer compiles:\n{r.stdout[-1500:]}{r.stderr[-1500:]}')
        bad = []
        for f in man['eras_sha256']:
            a, b = os.path.join(Z, 'build', 'data', f), os.path.join(W, 'build', 'data', f)
            if not os.path.isfile(b): bad.append(f'{f}: not made any more'); continue
            if sha(b) == man['eras_sha256'][f]: continue
            ga, gb = geometry(a), geometry(b)
            if ga != gb: bad.append(f'{f}: the buildings changed ({len(ga[0])} -> {len(gb[0])} records)')
    print('freeze check: ' + ('every period city as it was frozen' if not bad else 'changed by the code since ' + man['code_commit'][:7] + ': ' + '; '.join(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['check'] and len(a) == 2: check(a[1])
    elif a and a[0] != 'check': freeze(a[0], a[a.index('--name') + 1] if '--name' in a else None)
    else: sys.exit(__doc__)

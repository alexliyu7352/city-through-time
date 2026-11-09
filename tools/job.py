"""A long job run in the background, and what became of it (a compile, a render, a whole-film check): it runs on, niced, in its
own session, whatever happens to the shell that started it; its output goes to a log; a record says what ran, where, from
when, with which pid, and once it ends when and with what exit code. Nobody has to keep a terminal open or remember a pid.
    python -I tools/job.py start <name> [--dir <folder>] [--min-free-gb 3] -- <command> [args ...]
    python -I tools/job.py status [<name>] [--dir <folder>]      every job in the folder (or one): running, done (exit), or gone
    python -I tools/job.py wait <name> [--dir <folder>] [--timeout s]     until it ends; exits with its exit code
--dir: where the log and the record go (default build/logs/jobs under the working directory); --min-free-gb: refuse to start
when the disk holding that folder has less free (a render that runs out of disk loses its parts, docs/DELIVER.md).
A job is <name>.log and <name>.json there: {name, cmd, cwd, pid, started, ended, exit}. Start a name again once it has ended."""
import argparse, json, os, shutil, signal, subprocess, sys, time

HERE = os.path.abspath(__file__)


def rec_path(d, name): return os.path.join(d, name + '.json')


def read(d, name):
    try: return json.load(open(rec_path(d, name)))
    except (OSError, ValueError): return None


def alive(pid):
    try: os.kill(pid, 0); return True
    except ProcessLookupError: return False
    except PermissionError: return True


def state(r):
    if r is None: return 'none'
    if r.get('exit') is not None: return f"done, exit {r['exit']}"
    return 'running' if alive(r['pid']) else 'gone (ended without a record: killed, or the machine stopped)'


def start(A):
    os.makedirs(A.dir, exist_ok=True)
    r = read(A.dir, A.name)
    if r and r.get('exit') is None and alive(r['pid']): sys.exit(f"job {A.name} is still running (pid {r['pid']}); its log: {os.path.join(A.dir, A.name + '.log')}")
    free = shutil.disk_usage(A.dir).free / 1e9
    if free < A.min_free_gb: sys.exit(f'job {A.name}: only {free:.1f} GB free where it writes ({A.dir}), under --min-free-gb {A.min_free_gb}')
    if not A.cmd: sys.exit('job start: give the command after --')
    # the runner: its own session (setsid), niced, so it outlives the shell; it writes the record when the command starts and ends
    p = subprocess.Popen([sys.executable, '-I', HERE, '_run', A.name, '--dir', A.dir, '--', *A.cmd], cwd=os.getcwd(),
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    for _ in range(50):   # (until the runner has written its record)
        r = read(A.dir, A.name)
        if r and r.get('runner') == p.pid: break
        time.sleep(.1)
    print(f"job {A.name}: started (pid {r['pid'] if r else '?'}), log {os.path.join(A.dir, A.name + '.log')}")


def run(A):
    log = open(os.path.join(A.dir, A.name + '.log'), 'w')
    r = {'name': A.name, 'cmd': A.cmd, 'cwd': os.getcwd(), 'runner': os.getpid(), 'started': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'exit': None}
    try: c = subprocess.Popen(A.cmd, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, preexec_fn=lambda: os.nice(10))
    except OSError as e:
        r.update(pid=None, exit=127, ended=r['started'], error=str(e)); json.dump(r, open(rec_path(A.dir, A.name), 'w'), indent=1); return
    r['pid'] = c.pid; json.dump(r, open(rec_path(A.dir, A.name), 'w'), indent=1)
    for sig in (signal.SIGTERM, signal.SIGINT): signal.signal(sig, lambda *_: c.terminate())   # (stopping the runner stops the job)
    code = c.wait()
    r.update(exit=code, ended=time.strftime('%Y-%m-%dT%H:%M:%S%z')); json.dump(r, open(rec_path(A.dir, A.name), 'w'), indent=1)


def status(A):
    names = [A.name] if A.name else sorted(f[:-5] for f in os.listdir(A.dir) if f.endswith('.json')) if os.path.isdir(A.dir) else []
    if not names: print(f'no jobs in {A.dir}')
    for n in names:
        r = read(A.dir, n)
        print(f"{n}: {state(r)}" + (f"; started {r['started']}" + (f", ended {r['ended']}" if r.get('ended') else '') + f"; {' '.join(r['cmd'])}" if r else ''))


def wait(A):
    t0 = time.time()
    while True:
        r = read(A.dir, A.name)
        if r is None: sys.exit(f'no job {A.name} in {A.dir}')
        if r.get('exit') is not None: print(f"job {A.name}: exit {r['exit']}"); sys.exit(r['exit'])
        if not alive(r['pid']): sys.exit(f'job {A.name}: {state(r)}')
        if A.timeout and time.time() - t0 > A.timeout: print(f'job {A.name}: still running after {A.timeout:.0f} s'); sys.exit(124)
        time.sleep(5)


def main():
    argv = sys.argv[1:]; cmd = []
    if '--' in argv: i = argv.index('--'); argv, cmd = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser(description='a long job in the background, with a log and a record')
    ap.add_argument('what', choices=('start', 'status', 'wait', '_run')); ap.add_argument('name', nargs='?')
    ap.add_argument('--dir', default=os.path.join('build', 'logs', 'jobs')); ap.add_argument('--min-free-gb', type=float, default=3.0)
    ap.add_argument('--timeout', type=float)
    A = ap.parse_args(argv); A.cmd = cmd; A.dir = os.path.abspath(A.dir)
    if A.what in ('start', 'wait', '_run') and not A.name: sys.exit(f'job {A.what}: give the job a name')
    {'start': start, 'status': status, 'wait': wait, '_run': run}[A.what](A)


if __name__ == '__main__':
    main()

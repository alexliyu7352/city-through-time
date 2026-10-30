"""Machine slots: at most CT_SLOTS (2) heavy jobs at once on this machine, across every agent and worktree (SKILL.md
"Subagents and parallel work"): with many subagents at work, studies and stills started together would freeze the desktop.
A city's compile, a model study and every browser page a tool opens (stills, eraview, the checks that open the film, each
render worker) takes one, waiting for a free one; a job started by a job that holds one (CT_SLOT in its environment) takes none.
A slot is a lock on a file that the system lets go of when its process ends, however it ends (and keeps across compile's
re-run of itself). CT_SLOTS_DIR: where the locks are (default ~/.cache/city-through-time/slots, one place for every worktree).
usage: python3 -I pipeline/slots.py hold <what>   (for the Node tools, render/page.mjs: prints 'ok' once it holds a slot and
lets go when its input closes)"""
import fcntl, os, sys, time

N = int(os.environ.get('CT_SLOTS') or 2)
DIR = os.environ.get('CT_SLOTS_DIR') or os.path.join(os.path.expanduser('~'), '.cache', 'city-through-time', 'slots')
_held = None


def take(what=''):
    """hold a slot for the rest of this process (and its children, through CT_SLOT); returns at once when one is held already"""
    global _held
    if _held is not None or os.environ.get('CT_SLOT') or N <= 0: return
    os.makedirs(DIR, exist_ok=True); said = False
    while True:
        for k in range(N):
            f = open(os.path.join(DIR, f'slot{k}.lock'), 'a+')
            try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError: f.close(); continue
            f.seek(0); f.truncate(); f.write(f'pid {os.getpid()}: {what}\n'); f.flush()
            os.set_inheritable(f.fileno(), True)   # (held through os.execv: compile runs itself again for each pass)
            _held = f; os.environ['CT_SLOT'] = str(k); return
        if not said:
            print(f'waiting for a machine slot ({N} heavy jobs at once, pipeline/slots.py), held by: ' + '; '.join(holders()), file=sys.stderr, flush=True); said = True
        time.sleep(2)


def holders():
    out = []
    for k in range(N):
        try: out.append(open(os.path.join(DIR, f'slot{k}.lock'), encoding='utf-8').read().strip() or '?')
        except OSError: pass
    return out


if __name__ == '__main__' and sys.argv[1:2] == ['hold']:
    take(' '.join(sys.argv[2:]) or 'a page')
    print('ok', flush=True)
    sys.stdin.read()   # until the tool that asked closes it, or ends

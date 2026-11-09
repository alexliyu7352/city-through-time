"""Run the native Rome compiler from canonical inputs, recording opened files.

Start with tools/job.py, which supplies nice 10:
  uv run python -I tools/job.py start rome_canonical_compile \
    --dir cities/rome/research/rome_closeout -- \
    uv run python -I cities/rome/research/rome_closeout/reproduce.py
"""
from pathlib import Path
import atexit
import hashlib
import json
import os
import runpy
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
CITY = ROOT / 'cities/rome'
HERE = Path(__file__).resolve().parent
READS = set()
WRITES = set()


def audit(event, args):
    if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).absolute()
    mode = args[1] if len(args) > 1 else None
    flags = args[2] if len(args) > 2 else 0
    if (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (
            isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT)):
        WRITES.add(str(path))
    else:
        READS.add(str(path))


def save_audit():
    # Detach recording while recording the result itself.
    rows = []
    for name in sorted(READS):
        path = Path(name)
        if path.is_file():
            rows.append({'path': name, 'resolved': str(path.resolve()),
                         'bytes': path.stat().st_size, 'written_this_run': name in WRITES})
    (HERE / 'compile_opened_inputs.json').write_text(json.dumps(rows, indent=2) + '\n')


def restore_inputs(destination):
    """Restore only native compiler inputs into a fresh or partially missing build."""
    destination.mkdir(parents=True, exist_ok=True)
    for relative in ('data', 'logs', 'export', 'audio/voice', 'audio/music', 'video', 'review'):
        (destination / relative).mkdir(parents=True, exist_ok=True)
    for source in (CITY / 'assets/prep').iterdir():
        target = destination / 'data' / source.name
        if not target.exists():
            shutil.copy2(source, target)
    for relative, source in (('audio/voice/en', CITY / 'assets/audio/voice/en'),
                             ('audio/music/cand', CITY / 'assets/audio/music/cand')):
        target = destination / relative
        if not target.exists() and not target.is_symlink():
            target.symlink_to(source, target_is_directory=True)
        assert target.resolve() == source.resolve(), f'Noncanonical audio input: {target}'


def main():
    build = CITY / 'build'
    restore_inputs(build.resolve() if build.is_symlink() else build)
    sys.path.insert(0, str(ROOT / 'pipeline'))
    import layout
    raw = Path(layout.raw(str(CITY)))
    assert raw.resolve() == (CITY / 'assets/raw').resolve(), 'Canonical raw location changed'
    assert not any(path.is_file() for path in raw.rglob('*')), 'Approved Rome had no raw themes'
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'UV_THREADPOOL_SIZE'):
        os.environ[key] = '2'
    # Native pruning must not delete retained caches during this no-deletion round.
    os.environ['CT_GEN_CACHE_GB'] = '32'
    for key in ('CT_PASS', 'CT_GEN', 'CT_GEN_HITS', 'CT_T0', 'CT_SCRIPT', 'CT_STUDY'):
        os.environ.pop(key, None)
    os.environ['CT_PLAN'] = (CITY / 'plan_seed.json').read_text()
    assert isinstance(json.loads(os.environ['CT_PLAN']), dict)
    os.chdir(ROOT)
    sys.argv = [str(ROOT / 'pipeline/compile.py'), str(CITY)]
    atexit.register(save_audit)
    sys.addaudithook(audit)
    print('canonical compile: native pipeline/compile.py; CT_PLAN contains plan_seed JSON; '
          'two threads; process nice=' + str(os.getpriority(os.PRIO_PROCESS, 0)), flush=True)
    runpy.run_path(str(ROOT / 'pipeline/compile.py'), run_name='__main__')


if __name__ == '__main__':
    main()

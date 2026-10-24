"""Music generation for a city's score (the city's MUSIC.md; SKILL.md 10d): Stable Audio 3 Medium on this CPU.
usage: python -I tools/music.py cities/<slug> --list                  the cues, their spans, takes and candidates
       python -I tools/music.py cities/<slug> test                    every line of MUSIC.md's `### test` block, 30 s each
       python -I tools/music.py cities/<slug> M02 M03 [--wordings 1,2] [--seeds 1,2] [--fresh] [--force]
       python -I tools/music.py cities/<slug> heartbeat xun           a section that is no cue: 30 s each

Prompts are only in MUSIC.md: a `### <id> ...` section's first fenced block, one wording per line (wording 1, 2, ...). A cue's
place is in city.yaml film.music.cues (audio/lay.py lays them): its length is its span on build/export/timeline.json plus
END (the model closes a piece a few seconds before the length asked for, so its close falls about at the cue's end); a cue that
continues another (continue: <id>) is generated on the last CONTEXT seconds of that cue's take before the point where it is laid
to end (lay.laid_offset), the generation taking over from there: the new piece carries the old one's tempo, key and sound. The int8 model only: this build's
fp32 DiT does not run on this machine (its 5.8 GB weight cache fails validation; uncached it passed 27 GB), and the user settled
on int8 (2026-10-22, MUSIC.md §1). Candidates: build/audio/music/cand/<id>_<wording>-<seed>.wav, each with a .json
of what made it (prompt, seed, seconds, precision, the continuation); the tests: build/audio/music/test/. One at a time, niced,
THREADS threads; an existing file is kept unless --force (a long batch resumes).

The runtime is the official CPU one, Stable Audio 3's optimized/tflite (int8 DiT, flat ~2 GB of memory; on this Ryzen 3800X
30 s of audio took 61 s, 2026-10-22): SA3 = its folder, optimized/tflite in the clone this machine's local/config.json names
(stable_audio; pinned at 77e0398, with its own .venv), its weights in HF_HUB_CACHE (hf_cache there; the optimized repo needs no login)."""
import argparse, datetime, json, math, os, re, subprocess, sys, time
import yaml
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'audio'))
import lay, local

SA3 = local.path('stable_audio', 'optimized', 'tflite')
HF_CACHE = local.path('hf_cache')
THREADS = int(os.environ.get('SA3_THREADS', 8))
END = 4.0           # seconds generated past a cue's span: the model's own close falls in them (it ends 3-6 s early, 2026-10-22)
CONTEXT = 20.0      # seconds of the cue before that a continuation hears
SHORT = 30.0        # a test word or a standalone track
MAX_S = 380.0       # the medium DiT's longest rung
CFG = 2.0           # classifier-free guidance with MUSIC.md's `### negative` prompt: the A/B of 2026-10-22 (abtest/) sounded less
                    # jumbled with it (the user: C and E better than A); it runs the model twice per step


def prompts(md):
    """MUSIC.md -> {id: [wording, ...]}: each `### <id>` heading's first fenced block, one wording per non-empty line"""
    out, cur, fence = {}, None, False
    for line in open(md, encoding='utf-8'):
        if line.startswith('#'):
            cur = line.lstrip('#').split()[0] if line.startswith('### ') and line[4:].strip() else None; fence = False; continue
        if cur and line.strip().startswith('```'):
            if fence: cur, fence = None, False   # (only the first block)
            else: fence = True; out[cur] = []
            continue
        if cur and fence and line.strip(): out[cur].append(line.strip())
    return out


def slug(p):
    m = re.search(r'Instruments:\s*([^,]+)', p)
    return re.sub(r'[^a-z0-9]+', '-', (m.group(1) if m else p[:24]).lower()).strip('-')


def measure(wav):
    """what to know of a candidate before anyone hears it (SKILL.md 10d; 咸阳 M01 'long silences' left 30-40% of its candidates
    silent): its silent share and longest gap up to where its music ends, its low end (energy under 150 Hz), and its level in
    thirds (the build: rising, flat, falling)"""
    import numpy as np
    x = lay._read(wav); e = int(lay.music_end(x) * lay.SR); x_ = x[:e]; h = lay.SR // 10; n = len(x_) // h
    if not n: return {'silent': 1.0, 'gap_s': round(len(x) / lay.SR, 1), 'low': 0.0, 'thirds_db': []}
    db = 10 * np.log10(np.mean(np.square(x_[:n * h].reshape(n, h, 2), dtype=np.float64), axis=(1, 2)) + 1e-12)
    quiet = db < max(-45.0, np.percentile(db, 95) - 35)
    runs, r = [], 0
    for q in quiet: r = r + 1 if q else 0; runs.append(r)
    m = x_.mean(axis=1); sp = np.abs(np.fft.rfft(m)) ** 2; fr = np.fft.rfftfreq(len(m), 1 / lay.SR)
    th = [20 * np.log10(max(lay._rms(p), 1e-6)) for p in np.array_split(x_, 3)]
    return {'silent': round(float(quiet.mean()), 3), 'gap_s': round(max(runs) / 10, 1), 'low': round(float(sp[fr < 150].sum() / max(sp.sum(), 1e-12)), 3),
            'thirds_db': [round(v, 1) for v in th]}


def said(m):
    """a candidate's measure in one line, with what wants a look first"""
    warn = [w for w, bad in (('silent', m['silent'] > .15), ('gap', m['gap_s'] > 4), ('no low end', m['low'] < .02)) if bad]
    low = '<1%' if m['low'] < .005 else f"{m['low']:.0%}"
    return (f"silent {m['silent']:.0%}, gap {m['gap_s']:.1f} s, low {low}, level " + '/'.join(f'{v:.0f}' for v in m['thirds_db']) + ' dB'
            + (f"  ! {', '.join(warn)}" if warn else ''))


def generate(prompt, seconds, seed, out, init=None, inpaint=None, ctx=None, cfg=1.0, negative=None):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # ponytail: the runtime's venv and nice as on Linux/macOS; a Windows machine needs .venv/Scripts/python.exe and no nice
    cmd = ['nice', '-n', '19', os.path.join(SA3, '.venv', 'bin', 'python'), os.path.join(SA3, 'scripts', 'sa3_tflite.py'),
           '--prompt', prompt, '--dit', 'medium', '--decoder', 'same-l', '--dit-precision', 'w8a8', '--seconds', f'{seconds:.2f}',
           '--seed', str(seed), '--threads', str(THREADS), '--out', os.path.abspath(out)]
    if init: cmd += ['--init-audio', os.path.abspath(init), '--inpaint-range', f'{inpaint[0]:.3f},{inpaint[1]:.3f}']
    if cfg != 1.0: cmd += ['--cfg', f'{cfg}'] + (['--negative-prompt', negative] if negative else [])
    t = time.time()
    r = subprocess.run(cmd, cwd=SA3, env={**os.environ, 'HF_HUB_CACHE': HF_CACHE}, capture_output=True, text=True)
    if r.returncode or not os.path.exists(out):
        sys.stderr.write(r.stdout[-2000:] + r.stderr[-2000:]); raise SystemExit(f'music: the runtime failed on {os.path.basename(out)}')
    rev = subprocess.run(['git', '-C', SA3, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    meta = {'prompt': prompt, 'seed': seed, 'seconds': round(seconds, 2), 'precision': 'w8a8', 'decoder': 'same-l',
            'init': os.path.basename(init) if init else None, 'inpaint': [round(inpaint[0], 3), round(inpaint[1], 3)] if init else None, 'ctx': ctx,
            'cfg': cfg, 'negative': negative if cfg != 1.0 else None,
            'runtime': f'stable-audio-3 optimized/tflite {rev}', 'made': datetime.datetime.now().isoformat(timespec='seconds'),
            'wall_s': round(time.time() - t, 1)}
    meta['measure'] = measure(out)
    json.dump(meta, open(out[:-4] + '.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'  {os.path.basename(out)}: {seconds:.0f} s of audio in {meta["wall_s"]:.0f} s; {said(meta["measure"])}', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('city'); ap.add_argument('ids', nargs='*')
    ap.add_argument('--list', action='store_true'); ap.add_argument('--force', action='store_true')
    ap.add_argument('--wordings', help='1-based, e.g. 1,3 (default: all)'); ap.add_argument('--seeds', default='1')
    ap.add_argument('--fresh', action='store_true', help="a cue that continues another: make these on their own instead")
    ap.add_argument('--cfg', type=float, default=CFG, help='1 = off (one pass per step)')
    a = ap.parse_args()
    D = os.path.abspath(a.city)
    P = prompts(os.path.join(D, 'MUSIC.md'))
    music = (yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'))['film'].get('music') or {})
    cues = music.get('cues') or []
    by_id = {c['id']: c for c in cues}
    tl = json.load(open(os.path.join(D, 'build', 'export', 'timeline.json'), encoding='utf-8'))
    span = dict(zip([c['id'] for c in cues], lay.spans(cues, {n['id']: n['t0'] for n in tl['nodes']}, tl['dur']))) if cues else {}
    mdir = os.path.join(D, 'build', 'audio', 'music')
    if a.list or not a.ids:
        for c in cues:
            t0, t1 = span[c['id']]; have = sorted(f[len(c['id']) + 1:-4] for f in os.listdir(os.path.join(mdir, 'cand')) if f.startswith(c['id'] + '_') and f.endswith('.wav')) if os.path.isdir(os.path.join(mdir, 'cand')) else []
            print(f"{c['id']:6s} {c['node']:10s} {t0:7.2f}-{t1:7.2f} ({t1 - t0:5.1f} s)  wordings {len(P.get(c['id'], []))}  take {c.get('take') or '-':5s}  candidates: {' '.join(have) or '-'}")
            for k in have:   # (measured once, kept in the candidate's .json)
                f = lay.take_path(D, c['id'], k); jf = f[:-4] + '.json'; meta = json.load(open(jf, encoding='utf-8')) if os.path.exists(jf) else {}
                if 'measure' not in meta: meta['measure'] = measure(f); json.dump(meta, open(jf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
                print(f"         {k:5s} {'*' if k == c.get('take') else ' '} {said(meta['measure'])}")
        print('other sections: ' + ' '.join(k for k in P if k not in by_id))
        return
    seeds = [int(s) for s in a.seeds.split(',')]
    neg = (P.get('negative') or [None])[0]
    if a.cfg != 1.0 and not neg: raise SystemExit('music: --cfg needs MUSIC.md\'s `### negative` block (or --cfg 1)')
    for id_ in a.ids:
        if id_ not in P: raise SystemExit(f'music: MUSIC.md has no `### {id_}` section with a prompt block')
        ws = P[id_]
        pick = [int(w) for w in a.wordings.split(',')] if a.wordings else list(range(1, len(ws) + 1))
        if id_ == 'test':
            for k, p in enumerate(ws, 1):
                out = os.path.join(mdir, 'test', f'{k:02d}-{slug(p)}.wav')
                if a.force or not os.path.exists(out): generate(p, SHORT, seeds[0], out, cfg=a.cfg, negative=neg)
            continue
        c = by_id.get(id_)
        init = inpaint = ctx = None
        if c is None: seconds = SHORT   # (a standalone track)
        else:
            t0, t1 = span[id_]; seconds = max(SHORT, math.ceil(t1 - t0 + END))
            if c.get('continue') and not a.fresh:
                p_ = by_id.get(c['continue'])
                if not p_ or not p_.get('take'): raise SystemExit(f"music: {id_} continues {c['continue']}: choose its take first (city.yaml film.music.cues)")
                pf_ = lay.take_path(D, p_['id'], p_['take'])
                pm_ = json.load(open(pf_[:-4] + '.json', encoding='utf-8')) if os.path.exists(pf_[:-4] + '.json') else {}
                ps_ = span[p_['id']]
                join = round(lay.laid_offset(p_, lay._read(pf_), ps_[1] - ps_[0], False, pm_) + ps_[1] - ps_[0], 2)   # (as audio/lay.py lays it)
                k_ = min(CONTEXT, join)
                init = os.path.join(mdir, 'ctx', f"{p_['id']}_{p_['take']}@{join}.wav"); os.makedirs(os.path.dirname(init), exist_ok=True)
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{join - k_:.3f}', '-t', f'{k_:.3f}', '-i', pf_, '-c:a', 'pcm_s16le', init], check=True)
                seconds = math.ceil(k_ + t1 - t0 + END); inpaint = (k_, seconds); ctx = {'take': f"{p_['id']}_{p_['take']}", 'at': join}
        if seconds > MAX_S: raise SystemExit(f'music: {id_} needs {seconds} s; the medium DiT goes to {MAX_S:.0f} s: split the cue')
        for w in pick:
            if not 1 <= w <= len(ws): raise SystemExit(f'music: {id_} has {len(ws)} wording(s)')
            for s in seeds:
                out = lay.take_path(D, id_, f'{w}-{s}')
                if a.force or not os.path.exists(out): generate(ws[w - 1], seconds, s, out, init, inpaint, ctx, a.cfg, neg)


if __name__ == '__main__':
    main()

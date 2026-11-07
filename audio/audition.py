"""A cue cut from a recording, heard against the film before it is chosen (docs/SOUND.md "Music chosen from a library").

usage: python -I audio/audition.py <city> <cue id> <recording> --take <name> [--from <s>] [--to <s>] [--skip <a> <b> ...] [--anchor start|end]
       python -I audio/audition.py <city> --index        the page that lists every cut made so far

The take is the recording from --from to --to (its end by default), each --skip a b leaving out a..b (seconds of the recording;
the two sides cross over SEAM seconds, so cut at the same beat of two similar bars). It is written as
build/audio/music/cand/<cue>_<take>.wav with a .json of what made it (the recording, its sha256, the cuts): the film lays it
as any take (city.yaml film.music.cues: take: <name>). --anchor end (the default) lays it as compile does, its close landing
just after the cue's end; --anchor start lays it from --from at the cue's start.

The score is laid again with this take in its cue (audio/lay.py, the other cues as they are) and cut to the cue's stretch and
a few seconds round it: build/audio/music/audition/<cue>_<take>.m4a. Open the URL it prints on the city's preview server:
the picture and the narration play with that score in place of the film's (play.html score=, scoreAt=). Nothing of the film
is changed until the take is written into the cue."""
import argparse, glob, hashlib, html, json, os, subprocess, sys, wave
import numpy as np
import yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lay

SEAM = .25    # the cross-over at a skip, seconds (equal power)
AROUND = 6.0  # seconds of the film kept either side of the cue's stretch


def take_of(x, a, b, skips):
    """the recording x from a to b (seconds), each skip (s0, s1) left out, its two sides crossing over SEAM"""
    SR = lay.SR; marks = [a] + [v for s in sorted(skips) for v in s] + [b]
    parts = [x[int(round(p * SR)):int(round(q * SR))] for p, q in zip(marks[::2], marks[1::2])]
    out = parts[0]; k = int(SEAM * SR); w = np.linspace(0, np.pi / 2, k, dtype=np.float32)[:, None]
    for p in parts[1:]:
        if len(out) < k or len(p) < k: raise SystemExit('audition: a piece between two skips is shorter than the cross-over')
        out = np.concatenate([out[:-k], out[-k:] * np.cos(w) + p[:k] * np.sin(w), p[k:]])
    return out


def write_wav(f, y):
    with wave.open(f, 'wb') as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(lay.SR); w_.writeframes((np.clip(y, -.98, .98) * 32767).astype(np.int16).tobytes())


def film_inputs(D):
    """what compile hands audio/lay.py, read back from build/: the music, each node's start, the length, the lines heard,
    the declared silences and the narration track"""
    F = json.load(open(os.path.join(D, 'build', 'film.json'), encoding='utf-8'))
    T = json.load(open(os.path.join(D, 'build', 'export', 'timeline.json'), encoding='utf-8'))
    C = yaml.load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'), Loader=getattr(yaml, 'CSafeLoader', yaml.SafeLoader))
    music = (C.get('film') or {}).get('music') or {}
    pro = F.get('prologue')
    node_t0 = {**({'prologue': 0.0, '_opening': float(pro['dur'])} if pro else {}), **{n['id']: n['t0'] for n in T['nodes']}}
    voiced = [(l['t0'], l['t0'] + l['voice']) for l in T['lines'] if l.get('voice')]
    silences = [(s['t0'], s['t1']) for s in T.get('silences', [])]
    vw = os.path.join(D, T['voice']['dir'], '..', f"track_{T['voice']['lang']}.wav") if T.get('voice') else None
    return music, node_t0, float(T['dur']), voiced, silences, (os.path.normpath(vw) if vw else None)


def index(D):
    """build/audio/music/audition/index.html: every cut made so far, by cue, each a link to the preview with it"""
    A = os.path.join(D, 'build', 'audio', 'music', 'audition'); os.makedirs(A, exist_ok=True)
    slug = os.path.basename(os.path.normpath(D)); rows = {}
    for j in sorted(glob.glob(os.path.join(A, '*.json'))):
        m = json.load(open(j, encoding='utf-8')); rows.setdefault(m['cue'], []).append(m)
    out = ['<!doctype html><meta charset="utf-8"><title>Music audition</title>',
           '<style>body{font:15px system-ui,sans-serif;margin:24px;background:#16181c;color:#e8e8e8}a{color:#9cc8ff}td{padding:8px 12px;'
           'border-bottom:1px solid #333;vertical-align:top}textarea{width:100%;height:5em;background:#222;color:#eee}</style>',
           f'<h2>{html.escape(slug)}: music audition</h2><p>Each link opens the preview at the cue with that cut in the score.</p><table>']
    for cue, ms in rows.items():
        out.append(f'<tr><td><b>{html.escape(cue)}</b><br>{ms[0]["t0"]:.0f}-{ms[0]["t1"]:.0f} s</td><td>')
        for m in ms:
            cuts = ', '.join(f'{a:.1f}-{b:.1f}' for a, b in m['skips']) or 'none'
            out.append(f'<label><input type="radio" name="{html.escape(cue)}" value="{html.escape(m["take"])}"> '
                       f'<a href="/{html.escape(m["url"])}" target="_blank">{html.escape(m["take"])}</a></label> '
                       f'{html.escape(os.path.basename(m["source"]))} {m["from"]:.1f}-{m["to"]:.1f} s, skips {cuts}<br>')
        out.append('</td></tr>')
    out.append('</table><p><button onclick="pick()">Copy my picks</button></p><textarea id="o"></textarea><script>function pick(){'
               'const r=[...document.querySelectorAll("input:checked")].map(i=>i.name+": "+i.value);'
               'const o=document.getElementById("o");o.value=r.join("\\n");o.select();navigator.clipboard&&navigator.clipboard.writeText(o.value)}</script>')
    open(os.path.join(A, 'index.html'), 'w', encoding='utf-8').write('\n'.join(out))
    return os.path.join(A, 'index.html')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('city'); ap.add_argument('cue', nargs='?'); ap.add_argument('recording', nargs='?')
    ap.add_argument('--take'); ap.add_argument('--from', dest='a', type=float, default=0.0); ap.add_argument('--to', dest='b', type=float)
    ap.add_argument('--skip', nargs=2, type=float, action='append', default=[]); ap.add_argument('--anchor', choices=('start', 'end'), default='end')
    ap.add_argument('--index', action='store_true')
    o = ap.parse_args(); D = os.path.abspath(o.city)
    if o.index or not o.cue: print(os.path.relpath(index(D))); return
    if not (o.recording and o.take): raise SystemExit('audition: a cue needs a recording and --take <name>')
    music, node_t0, dur, voiced, silences, vw = film_inputs(D)
    cues = music.get('cues') or []
    if not any(c['id'] == o.cue for c in cues): raise SystemExit(f'audition: no cue {o.cue!r} in city.yaml film.music.cues')
    x = lay._read(o.recording); n = len(x) / lay.SR; b = n if o.b is None else min(o.b, n)
    if not 0 <= o.a < b: raise SystemExit(f'audition: --from {o.a} is not inside the recording (0-{n:.1f} s)')
    for s0, s1 in o.skip:
        if not o.a < s0 < s1 < b: raise SystemExit(f'audition: skip {s0}-{s1} is not inside {o.a}-{b:.1f} s')
    y = take_of(x, o.a, b, o.skip)
    f = lay.take_path(D, o.cue, o.take); os.makedirs(os.path.dirname(f), exist_ok=True); write_wav(f, y)
    sha = hashlib.sha256(open(o.recording, 'rb').read()).hexdigest()
    made = {'source': os.path.abspath(o.recording), 'sha256': sha, 'from': o.a, 'to': round(b, 3), 'skips': [list(s) for s in sorted(o.skip)], 'seam': SEAM, 'made': 'audio/audition.py'}
    json.dump(made, open(f[:-4] + '.json', 'w', encoding='utf-8'), indent=1)
    mine = lambda c: {**{k: v for k, v in c.items() if k != 'offset'}, 'take': o.take, **({'offset': 0.0} if o.anchor == 'start' else {})}   # (an offset written for another take does not hold)
    alt = {**music, 'cues': [mine(c) if c['id'] == o.cue else c for c in cues]}
    res = lay.lay(D, alt, node_t0, dur, voiced, silences, vw, write=False)
    if not isinstance(res, tuple): raise SystemExit('audition: nothing laid')
    out, buf = res
    t0, t1 = next((c['t0'], c['t1']) for c in out['cues'] if c['id'] == o.cue)
    a, z = max(0.0, t0 - AROUND), min(dur, t1 + AROUND)
    A = os.path.join(D, 'build', 'audio', 'music', 'audition'); os.makedirs(A, exist_ok=True)
    wf = os.path.join(A, f'{o.cue}_{o.take}.wav'); write_wav(wf, buf[int(a * lay.SR):int(z * lay.SR)])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wf, '-c:a', 'aac', '-b:a', '160k', wf[:-4] + '.m4a'], check=True); os.remove(wf)
    slug = os.path.basename(os.path.normpath(D)); rel = os.path.relpath(wf[:-4] + '.m4a', os.path.join(D, 'build'))
    url = f'play.html?city={slug}&t={max(0.0, t0 - 3):.1f}&play=1&score={rel}&scoreAt={a:.3f}'
    off = lay.laid_offset(next(c for c in alt['cues'] if c['id'] == o.cue), y, t1 - t0, o.cue == cues[-1]['id'], {})
    json.dump({'cue': o.cue, 'take': o.take, 't0': t0, 't1': t1, 'url': url, **made}, open(wf[:-4] + '.json', 'w', encoding='utf-8'), indent=1)
    index(D)
    print(f'{o.cue} {t0:.1f}-{t1:.1f} s ({t1 - t0:.1f} s): take {o.take}, {len(y) / lay.SR:.1f} s; the cue starts {off:.1f} s into the take, '
          f'its close at {lay.closing(y):.1f} s of it ({lay.closing(y) - off - (t1 - t0):+.1f} s from the cue\'s end)'
          + ''.join(f'\n  note: {m}' for m in out.get('notes') or []))
    print(f'  hear it: http://127.0.0.1:<port>/{url}\n  all cuts: {os.path.relpath(os.path.join(A, "index.html"), os.path.join(D, "build"))}')


if __name__ == '__main__':
    main()

"""A cue cut from a recording, heard against the film before it is chosen (docs/SOUND.md "Music chosen from a library").

usage: python -I audio/audition.py <city> <cue id> <recording> --take <name> [--from <s>] [--to <s>] [--skip <a> <b> ...] [--anchor start|end]
       python -I audio/audition.py <city> --stills       the film's pictures under every cue, a still each STILL_STEP s (once per version of the picture)
       python -I audio/audition.py <city> --index        the page that lists every cut made so far

The take is the recording from --from to --to (its end by default), each --skip a b leaving out a..b (seconds of the recording;
the two sides cross over SEAM seconds, so cut at the same beat of two similar bars). It is written as
build/audio/music/cand/<cue>_<take>.wav with a .json of what made it (the recording, its sha256, the cuts): the film lays it
as any take (city.yaml film.music.cues: take: <name>). --anchor end (the default) lays it as compile does, its close landing
just after the cue's end; --anchor start lays it from --from at the cue's start.

The score is laid again with this take in its cue (audio/lay.py, the other cues as they are) and cut to the cue's stretch and
a few seconds round it: build/audio/music/audition/<cue>_<take>.m4a, and with the narration mixed in, <cue>_<take>_mix.m4a.
The page (--index, build/audio/music/audition/index.html on the city's preview server) plays each cut's mix over stills of the
film (--stills) and its subtitles: a choice heard in seconds, with no model to load. Each cut also links to the film itself
(play.html score=, scoreAt=), for the few worth a look in motion. Nothing of the film is changed until the take is written into the cue."""
import argparse, glob, hashlib, html, json, os, subprocess, sys, wave
import numpy as np
import yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lay

SEAM = .25    # the cross-over at a skip, seconds (equal power)
AROUND = 6.0  # seconds of the film kept either side of the cue's stretch
STILL_STEP = 2   # a still of the film every this many seconds (the page shows the nearest)
STILL_SIZE = '640x360'


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


def stills(D):
    """the film's pictures under every cue (and AROUND either side), a still each STILL_STEP s, into
    build/audio/music/audition/stills: only the missing ones, all again when the picture changed (film.json, its score aside)"""
    music, node_t0, dur, *_ = film_inputs(D)
    cues = music.get('cues') or []
    if not cues: raise SystemExit('audition: no cue in city.yaml film.music.cues')
    A = os.path.join(D, 'build', 'audio', 'music', 'audition', 'stills'); os.makedirs(A, exist_ok=True)
    F = json.load(open(os.path.join(D, 'build', 'film.json'), encoding='utf-8')); F.pop('score', None)
    stamp = hashlib.sha256(json.dumps(F, sort_keys=True).encode()).hexdigest(); sf = os.path.join(A, 'stamp')
    if not os.path.exists(sf) or open(sf).read() != stamp:
        for f in glob.glob(os.path.join(A, 't_*.jpg')): os.remove(f)
    want = set()
    for a, b in lay.spans(cues, node_t0, dur):
        want.update(range(max(0, int((a - AROUND) // STILL_STEP) * STILL_STEP), int(min(dur, b + AROUND)) + 1, STILL_STEP))
    todo = sorted(t for t in want if not os.path.exists(os.path.join(A, f't_{t}.jpg')))
    if todo:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        subprocess.run(['node', os.path.join(root, 'render', 'still.mjs'), os.path.basename(os.path.normpath(D)), *map(str, todo), '--out', A,
                        '--size', STILL_SIZE, '--prefix', 't_'], cwd=root, check=True, stdout=subprocess.DEVNULL)
    open(sf, 'w').write(stamp)
    print(f'{len(want)} stills ({len(todo)} new): {os.path.relpath(A, D)}')


PAGE = r"""<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Music audition</title>
<style>body{font:15px system-ui,sans-serif;margin:0;background:#16181c;color:#e8e8e8}a{color:#9cc8ff}main{max-width:1100px;margin:auto;padding:16px}
#stage{position:sticky;top:0;background:#16181c;padding:8px 0 10px;z-index:2}#pic{width:100%;max-width:640px;aspect-ratio:16/9;background:#000;display:block}
#sub{min-height:3.2em;max-width:640px;margin:6px 0;line-height:1.45}#sub small{color:#aaa}audio{width:100%;max-width:640px}#now{color:#ffd479;margin:4px 0}
td{padding:8px 10px;border-bottom:1px solid #333;vertical-align:top}button{background:#2b5d9b;color:#fff;border:0;border-radius:4px;padding:4px 10px;cursor:pointer}
button.m{background:#3a3f48;margin:2px}.note{color:#bbb;font-size:13px}textarea{width:100%;height:5em;background:#222;color:#eee}</style>
<main><div id="stage"><img id="pic" alt=""><div id="now">Pick a cut below: its music and the narration play over stills of the film.</div>
<div id="sub"></div><audio id="au" controls preload="auto"></audio></div><h2>__TITLE__</h2><table>__ROWS__</table>
<p><button onclick="pick()">Copy my picks</button></p><textarea id="o"></textarea></main>
<script>const L=__LINES__,STEP=__STEP__;let A=0,last=-1;const au=document.getElementById('au'),pic=document.getElementById('pic'),sub=document.getElementById('sub');
function at(ft){let lo=0,hi=L.length-1,r=null;while(lo<=hi){const m=(lo+hi)>>1;if(L[m][0]<=ft){r=L[m];lo=m+1}else hi=m-1}return r&&ft<r[1]?r:null}
function show(){const ft=A+au.currentTime,k=Math.round(ft/STEP)*STEP;if(k!==last){last=k;pic.src='stills/t_'+k+'.jpg';new Image().src='stills/t_'+(k+STEP)+'.jpg'}
const l=at(ft);sub.innerHTML=l?l[2]+(l[3]?'<br><small>'+l[3]+'</small>':''):''}
au.addEventListener('timeupdate',show);au.addEventListener('seeked',show);
const blobs={};   // (each mix fetched whole: a server that does not answer range requests leaves an <audio> unseekable)
async function play(b,t){const d=b.dataset;document.getElementById('now').textContent=d.label+' (loading)';
if(au.dataset.mix!==d.mix){blobs[d.mix]??=await fetch(d.mix).then(r=>r.blob()).then(x=>URL.createObjectURL(x));au.src=blobs[d.mix];au.dataset.mix=d.mix;A=+d.a;last=-1;
await new Promise(r=>au.readyState>=1?r():au.addEventListener('loadedmetadata',r,{once:true}))}
document.getElementById('now').textContent=d.label;au.currentTime=Math.max(0,(t??+d.t0-3)-A);au.play();show()}
function pick(){const r=[...document.querySelectorAll('input:checked')].map(i=>i.name+": "+i.value);const o=document.getElementById('o');o.value=r.join("\n");o.select();navigator.clipboard&&navigator.clipboard.writeText(o.value)}</script>"""


def index(D):
    """build/audio/music/audition/index.html: every cut made so far, by cue; each plays its mix over the stills (--stills) and the
    subtitles, at its cue or at one of its marks, and links to the film itself with it"""
    A = os.path.join(D, 'build', 'audio', 'music', 'audition'); os.makedirs(A, exist_ok=True)
    slug = os.path.basename(os.path.normpath(D)); rows = {}
    for j in sorted(glob.glob(os.path.join(A, '*.json'))):
        m = json.load(open(j, encoding='utf-8')); rows.setdefault(m['cue'], []).append(m)
    T = json.load(open(os.path.join(D, 'build', 'export', 'timeline.json'), encoding='utf-8'))
    langs = [l_ for l_ in ('en', 'zh') if any(l_ in (l.get('text') or {}) for l in T['lines'])] or [None]
    txt = lambda l, k: html.escape(((l.get('text') or {}).get(k) or '') if isinstance(l.get('text'), dict) else (str(l.get('text') or '') if k == langs[0] else ''))
    lines = [[round(l['t0'], 2), round(l['t1'], 2), txt(l, langs[0]), txt(l, langs[1]) if len(langs) > 1 else ''] for l in T['lines']]
    out = []
    for cue, ms in rows.items():
        out.append(f'<tr><td><b>{html.escape(cue)}</b><br>{ms[0]["t0"]:.0f}-{ms[0]["t1"]:.0f} s</td><td>')
        for m in ms:
            lab = html.escape(f'{cue} {m["take"]}')
            dat = (f'data-mix="{html.escape(m["mix"])}" data-a="{m["a"]:.3f}" data-t0="{m["t0"]:.3f}" data-label="{lab}"' if m.get('mix') else '')
            cuts = ', '.join(f'{a:.1f}-{b:.1f}' for a, b in m['skips']) or 'none'
            out.append(f'<div><label><input type="radio" name="{html.escape(cue)}" value="{html.escape(m["take"])}"> <b>{html.escape(m["take"])}</b></label> '
                       + (f'<button {dat} onclick="play(this)">listen</button> ' if dat else '(made before mixes: cut it again) ')
                       + ''.join(f'<button class="m" {dat} onclick="play(this,{t:.2f})">{html.escape(k)}</button>' for k, t in (m.get('marks') or []) if dat)
                       + f' <a href="/{html.escape(m["url"])}" target="_blank">film</a>'
                       + (f'<div class="note">{html.escape(m["note"])}</div>' if m.get('note') else '')
                       + f'<div class="note">{html.escape(os.path.basename(m["source"]))} {m["from"]:.1f}-{m["to"]:.1f} s, skips {cuts}</div></div>')
        out.append('</td></tr>')
    page = PAGE.replace('__TITLE__', html.escape(slug) + ': music audition').replace('__ROWS__', '\n'.join(out)) \
               .replace('__LINES__', json.dumps(lines, ensure_ascii=False)).replace('__STEP__', str(STILL_STEP))
    open(os.path.join(A, 'index.html'), 'w', encoding='utf-8').write(page)
    if not os.path.isdir(os.path.join(A, 'stills')): print('  (no stills yet: audio/audition.py <city> --stills)')
    return os.path.join(A, 'index.html')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('city'); ap.add_argument('cue', nargs='?'); ap.add_argument('recording', nargs='?')
    ap.add_argument('--take'); ap.add_argument('--from', dest='a', type=float, default=0.0); ap.add_argument('--to', dest='b', type=float)
    ap.add_argument('--skip', nargs=2, type=float, action='append', default=[]); ap.add_argument('--anchor', choices=('start', 'end'), default='end')
    ap.add_argument('--index', action='store_true'); ap.add_argument('--stills', action='store_true')
    ap.add_argument('--note', help='what sets this cut apart, in the words of whoever chooses (shown on the page)')
    ap.add_argument('--mark', action='append', default=[], metavar='LABEL=SECONDS', help='a moment of the film to hear it at (film seconds)')
    o = ap.parse_args(); D = os.path.abspath(o.city)
    if o.stills: stills(D)
    if o.index or o.stills or not o.cue: print(os.path.relpath(index(D))); return
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
    wf = os.path.join(A, f'{o.cue}_{o.take}.wav'); win = buf[int(a * lay.SR):int(z * lay.SR)]; write_wav(wf, win)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wf, '-c:a', 'aac', '-b:a', '160k', wf[:-4] + '.m4a'], check=True); os.remove(wf)
    mx = win.copy()   # (the narration over it, as the film will be heard: the page plays this over the stills)
    if vw and os.path.exists(vw): v_ = lay._read(vw)[int(a * lay.SR):int(z * lay.SR)]; mx[:len(v_)] += v_[:len(mx)]
    pk = float(np.abs(mx).max()) if len(mx) else 0.0
    if pk > .97: mx *= .97 / pk
    mf = os.path.join(A, f'{o.cue}_{o.take}_mix.wav'); write_wav(mf, mx)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mf, '-c:a', 'aac', '-b:a', '128k', mf[:-4] + '.m4a'], check=True); os.remove(mf)
    marks = [(k_, float(v_)) for k_, _, v_ in (m_.rpartition('=') for m_ in o.mark)]
    if any(not a <= t_ <= z for _, t_ in marks): raise SystemExit(f'audition: a --mark is outside this cut\'s stretch ({a:.1f}-{z:.1f} s)')
    slug = os.path.basename(os.path.normpath(D)); rel = os.path.relpath(wf[:-4] + '.m4a', os.path.join(D, 'build'))
    url = f'play.html?city={slug}&t={max(0.0, t0 - 3):.1f}&play=1&score={rel}&scoreAt={a:.3f}'
    off = lay.laid_offset(next(c for c in alt['cues'] if c['id'] == o.cue), y, t1 - t0, o.cue == cues[-1]['id'], {})
    json.dump({'cue': o.cue, 'take': o.take, 't0': t0, 't1': t1, 'url': url, 'mix': os.path.basename(mf[:-4] + '.m4a'), 'a': a, 'z': z,
               'note': o.note, 'marks': marks, **made}, open(wf[:-4] + '.json', 'w', encoding='utf-8'), indent=1)
    index(D)
    print(f'{o.cue} {t0:.1f}-{t1:.1f} s ({t1 - t0:.1f} s): take {o.take}, {len(y) / lay.SR:.1f} s; the cue starts {off:.1f} s into the take, '
          f'its close at {lay.closing(y):.1f} s of it ({lay.closing(y) - off - (t1 - t0):+.1f} s from the cue\'s end)'
          + ''.join(f'\n  note: {m}' for m in out.get('notes') or []))
    print(f'  all cuts, each heard over stills of the film: {os.path.relpath(os.path.join(A, "index.html"), D)} on the preview server '
          f'(audio/audition.py {os.path.basename(os.path.normpath(D))} --stills once for the pictures); in the film itself: http://127.0.0.1:<port>/{url}')


if __name__ == '__main__':
    main()

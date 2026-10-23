"""The score laid on the film's timeline (SKILL.md 10d; the city's MUSIC.md), for the preview and the mix:

  city.yaml film.music.source cues (the default): the cues below; code: the code score (audio/codescore.py writes it from the
                              timeline, lay_code() lays it), the fallback when a city has no generated or brought music
  city.yaml film.music.cues   [{id, node, take, offset, gain, fade_in, continue}] in film order. A cue starts at its node (the
                              first at the film's start) and runs to the next cue's start, so it follows the timeline when nodes
                              move. It plays its chosen take, build/audio/music/cand/<id>_<take>.wav (tools/music.py makes them),
                              from `offset` seconds into it, or else from where its own ending (the model ends a piece a few seconds
                              before the length asked for) lands RING after the cue's end; a cue that continues another starts
                              where the generation took over (its take's .json) and crosses over sample to sample, its take
                              beginning as the one before it.
  film.music.stop_in_silences the music stops in the declared silences (script.yaml quiet and pause), with a hard cut
  film.music.loop             a cue whose take the preview plays on in a loop once the film has ended (the user, 2026-10-22: a
                              viewer of the web version may stay on the end card), made seamless: its close crossed into its start

A cue rises over FADE_IN from its node and rings out XF seconds under the next one. Under each voiced line the music dips DUCK_DB; where nobody speaks it sits UNDER_DB
below the narration's speaking level (each cue levelled on its own laid stretch, then its `gain` in dB; the code score on the
stretches where it sounds). Writes build/audio/music/score.wav (48 kHz stereo: what the mix lays) and score.m4a (what the
preview plays beside the narration)."""
import hashlib, json, os, subprocess, wave
import numpy as np

SR = 48000
XF = 3.0                      # an outgoing cue rings out this long under the next
RING = .5                     # a take's close (where its last fade begins) lands this long after its cue's end
FADE_IN = 2.5                 # a cue (not a continuation) rises at least this long
PRE, PRE_MAX = 1.5, 6.0       # and starts this long before its node, or before the cue before it begins to close if that is earlier
                              # (from earlier in its take, where there is room): it rises while the other fades, no hole between
JOIN = 1.0                    # a continuation crosses over this long, ending at the join
DUCK_DB = 10.0                # the dip under a voiced line
DUCK_IN, DUCK_OUT = .25, .6   # it starts this long before the line and recovers this long after it
UNDER_DB = 5.0                # the music where nobody speaks: this far below the narration
CUT = .05                     # the hard cut into and out of a silence
END_FADE = 3.0                # the last cue fades over the film's last seconds
LOOP_XF = 4.0                 # the loop's close crosses into its start over this long
SFX_UNDER = 6.0               # a sound effect's loudest moment: this far below the narration's speaking level,
SFX_OVER = 3.0                # or this far above the score around it where the score is louder (the lights go out in the climax)


def _read(f):
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 's16le', '-ac', '2', '-ar', str(SR), '-'],
                                     capture_output=True, check=True).stdout, np.int16)
    return x.reshape(-1, 2).astype(np.float32) / 32768


def _rms(x): return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)))) if len(x) else 0.0


def music_end(x):
    """where a take's music ends: after the last 100 ms above both -45 dBFS and its loud level less 35 dB (the model ends a piece
    3-6 s before the length asked for and leaves the rest silent)"""
    h = SR // 10; n = len(x) // h
    db = 10 * np.log10(np.mean(np.square(x[:n * h].reshape(n, h, 2), dtype=np.float64), axis=(1, 2)) + 1e-12)
    on = np.nonzero(db > max(-45.0, np.percentile(db, 95) - 35))[0]
    return (on[-1] + 1) * h / SR if len(on) else len(x) / SR


def closing(x):
    """where a take's close begins: after the last half second within 10 dB of its median level (its last fade, before the end)"""
    h = SR // 2; e = int(music_end(x) * SR) // h
    db = 10 * np.log10(np.mean(np.square(x[:e * h].reshape(e, h, 2), dtype=np.float64), axis=(1, 2)) + 1e-12)
    on = np.nonzero(db >= np.median(db) - 10)[0]
    return (on[-1] + 1) * h / SR if len(on) else music_end(x)


def continues(c, meta):
    """a take made on the close of the cue before (tools/music.py writes where, ctx); the cue's continue: only says how to make
    new ones, so a cue may keep a take made either way"""
    return bool(meta.get('ctx') or (c.get('continue') and meta.get('inpaint')))


def take_meta(D, c):
    f = take_path(D, c['id'], c['take'])[:-4] + '.json' if c.get('take') else ''
    return json.load(open(f, encoding='utf-8')) if f and os.path.exists(f) else {}


def laid_offset(c, x, span, last, meta):
    """where in its take a cue starts: as written (offset); where a continuation took over; or else so that the take's close
    begins RING after the cue's end, and the last cue's music ends with the film: its climax inside its stretch (the user,
    2026-10-22: the climaxes ran past their nodes)"""
    if 'offset' in c: return float(c['offset'])
    if continues(c, meta): return float((meta.get('inpaint') or [0])[0])
    return max(0.0, (music_end(x) if last else closing(x) + RING) - span)


def take_path(D, cue_id, take):
    return os.path.join(D, 'build', 'audio', 'music', 'cand', f'{cue_id}_{take}.wav')


def spans(cues, node_t0, dur):
    """each cue's (t0, t1) on the film: from its node (the first from 0) to the next cue's start (the last to the film's end)"""
    t0s = []
    for i, c in enumerate(cues):
        if c.get('node') not in node_t0: raise SystemExit(f"music: cue {c.get('id')}: no node {c.get('node')!r}")
        t0s.append(0.0 if i == 0 else node_t0[c['node']])
    if any(b <= a for a, b in zip(t0s, t0s[1:])): raise SystemExit('music: the cues must start in film order, at different nodes')
    return list(zip(t0s, t0s[1:] + [dur]))


def voice_level(voice_wav, voiced):
    """the narration's speaking level (RMS over its lines), or -20 dBFS without one"""
    if not (voice_wav and os.path.exists(voice_wav) and voiced): return 10 ** (-20 / 20)
    with wave.open(voice_wav) as w_: v_ = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).astype(np.float32) / 32768; vr_ = w_.getframerate()
    return _rms(np.concatenate([v_[int(a * vr_):int(b * vr_)] for a, b in voiced]))


def lay_sfx(D, kinds, events, dur, voiced, voice_wav=None, score_wav=None):
    """film.sfx (the page events that keep a sound beside a laid score): the one-shots of build/audio/sfx/<kind>.wav (audio/mix.py
    --kit) at their events [(t, kind)], each with its loudest 100 ms SFX_UNDER below the narration or SFX_OVER above the score there,
    whichever is louder, as one track for the preview and
    the mix: build/audio/sfx_track.wav and .m4a. Returns film.json's sfx {kinds, file, wav} (file: None until the kit is made)."""
    out = {'kinds': list(kinds), 'file': None}
    fs = {k: os.path.join(D, 'build', 'audio', 'sfx', k + '.wav') for k in kinds}
    if not kinds or not all(os.path.exists(f) for f in fs.values()): return out
    ref = voice_level(voice_wav, voiced) * 10 ** (-SFX_UNDER / 20)
    N = int(dur * SR) + 1; buf = np.zeros((N, 2), np.float32); h = SR // 10
    sc = _read(score_wav) if score_wav and os.path.exists(score_wav) else None
    for k in kinds:
        x = _read(fs[k]); n = len(x) // h
        loud = float(np.sqrt(np.mean(np.square(x[:n * h].reshape(n, h, 2), dtype=np.float64), axis=(1, 2)).max())) if n else _rms(x)
        for t, k_ in events:
            if k_ != k: continue
            i = int(round(t * SR)); y = x[:N - i]
            here = _rms(sc[i:i + len(y)]) * 10 ** (SFX_OVER / 20) if sc is not None else 0.0
            buf[i:i + len(y)] += y * (max(ref, here) / max(loud, 1e-6))
    wf = os.path.join(D, 'build', 'audio', 'sfx_track.wav')
    with wave.open(wf, 'wb') as w_: w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((np.clip(buf, -.98, .98) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wf, '-c:a', 'aac', '-b:a', '160k', wf[:-4] + '.m4a'], check=True)
    out.update(file=os.path.relpath(wf[:-4] + '.m4a', os.path.join(D, 'build')), wav=os.path.relpath(wf, os.path.join(D, 'build')),
               events=[[round(t, 3), k] for t, k in events])
    return out


def lay(D, music, node_t0, dur, voiced, silences, voice_wav=None):
    """music: city.yaml film.music; node_t0 {node id: start}; voiced [(t0, t1)] the lines heard; silences [(t0, t1)] declared.
    Returns film.json's score {file, wav, cues, missing} (file: None while no cue has a take)."""
    cues = (music or {}).get('cues') or []
    if not cues: return None
    sp = spans(cues, node_t0, dur)
    out = {'cues': [{'id': c['id'], 't0': round(a, 3), 't1': round(b, 3), 'take': c.get('take')} for c, (a, b) in zip(cues, sp)],
           'missing': [c['id'] for c in cues if not c.get('take')], 'file': None}
    if len(out['missing']) == len(cues): return out
    target = voice_level(voice_wav, voiced) * 10 ** (-UNDER_DB / 20)   # (the music UNDER_DB below the narration)
    N = int(dur * SR) + 1
    buf = np.zeros((N, 2), np.float32)
    notes, joins, prev_close = [], {}, None
    for i, (c, (t0, t1)) in enumerate(zip(cues, sp)):
        if not c.get('take'): continue
        f = take_path(D, c['id'], c['take'])
        if not os.path.exists(f): raise SystemExit(f"music: cue {c['id']}: no take {os.path.relpath(f, D)} (tools/music.py)")
        meta = take_meta(D, c)
        x = _read(f)
        cont = continues(c, meta)
        nxt = cues[i + 1] if i + 1 < len(cues) else None
        off = laid_offset(c, x, t1 - t0, nxt is None, meta)
        joins[c['id']] = (f"{c['id']}_{c['take']}", round(off + t1 - t0, 2))   # (where a continuation of it must take over)
        ctx = meta.get('ctx')
        if cont and ctx and i and [ctx.get('take'), round(float(ctx.get('at', 0)), 2)] != list(joins.get(cues[i - 1]['id'], ('', 0))):
            notes.append(f"{c['id']} was made on {ctx.get('take')} at {ctx.get('at')} s, now the cue before is laid as {joins.get(cues[i - 1]['id'])}: generate it again")
        into_cont = bool(nxt and nxt.get('take') and continues(nxt, take_meta(D, nxt)))
        pre = JOIN if cont else (min(off, PRE_MAX, t0 - min(t0, prev_close if prev_close is not None else t0) + PRE) if i else 0.0)
        prev_close = t0 + closing(x) - off   # (film seconds)
        a = t0 - pre                                                      # laid from (film seconds)
        b = t1 if into_cont else (min(t1 + XF, dur) if nxt else dur)      # laid to
        s0 = int(round((off - (t0 - a)) * SR))
        if s0 < 0: raise SystemExit(f"music: cue {c['id']}: offset {off} leaves no room for the crossover")
        seg = x[s0:s0 + int(round((b - a) * SR))].copy()
        if len(seg) < int(round((b - a) * SR)) - 1: notes.append(f"{c['id']}: the take ends {b - a - len(seg) / SR:.1f} s early")
        # level on its own stretch (t0..t1), then its gain
        own = x[int(off * SR):int((off + t1 - t0) * SR)]
        if _rms(own) < 1e-4: raise SystemExit(f"music: cue {c['id']}: the take is silent from {off} s")
        seg *= target / _rms(own) * 10 ** (float(c.get('gain', 0)) / 20)
        n = len(seg); r = np.arange(n) / SR
        g = np.ones(n, np.float32)
        g *= np.clip(r / (JOIN if cont else max(pre, float(c.get('fade_in', FADE_IN)))), 0, 1)   # (a continuation: linear, against the linear fade-out before it)
        if into_cont: g *= np.clip((t1 - a - r) / JOIN, 0, 1)
        elif nxt: g *= (1 - np.clip((r - (t1 - a)) / XF, 0, 1)) ** 2   # (over its own ending, under the next cue's rise)
        else: g *= np.clip((dur - a - r) / END_FADE, 0, 1)
        g[-min(n, int(.05 * SR)):] *= np.linspace(1, 0, min(n, int(.05 * SR)))   # (never a click where the take runs out)
        k = int(round(a * SR)); buf[k:k + n] += (seg * g[:, None])[:N - k]
    _dip(buf, dur, voiced, silences, music)
    _write(D, buf, out, notes, 'lower a cue gain')
    d_ = os.path.join(D, 'build', 'audio', 'music')
    lc = next((c for c in cues if c['id'] == (music or {}).get('loop')), None)
    if (music or {}).get('loop') and not lc: raise SystemExit(f"music: loop: no cue {music['loop']!r}")
    if lc and lc.get('take'):   # the loop after the film: the take to its close, the close crossed into the start
        x = _read(take_path(D, lc['id'], lc['take'])); x = x[:int(music_end(x) * SR)]
        k = int(LOOP_XF * SR); p_ = np.linspace(0, np.pi / 2, k, dtype=np.float32)[:, None]
        y = x[k:].copy(); y[-k:] = y[-k:] * np.cos(p_) + x[:k] * np.sin(p_)
        y *= target / max(_rms(y), 1e-6)
        lf = os.path.join(d_, 'loop.wav')
        with wave.open(lf, 'wb') as w_: w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((np.clip(y, -.98, .98) * 32767).astype(np.int16).tobytes())
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', lf, '-c:a', 'aac', '-b:a', '160k', lf[:-4] + '.m4a'], check=True)
        out['loop'] = os.path.relpath(lf[:-4] + '.m4a', os.path.join(D, 'build'))
    return out


def _dip(buf, dur, voiced, silences, music):
    """the dips under the voice and the stops in the silences, at 100 Hz then per sample"""
    tc = np.arange(int(dur * 100) + 2) / 100
    depth = np.zeros_like(tc)
    for a, b in voiced:
        depth = np.maximum(depth, np.clip(np.minimum((tc - (a - DUCK_IN)) / DUCK_IN, ((b + DUCK_OUT) - tc) / DUCK_OUT), 0, 1))
    env = 10 ** (-DUCK_DB * depth / 20)
    if (music or {}).get('stop_in_silences'):
        for a, b in silences: env *= 1 - np.clip(np.minimum((tc - a) / CUT, (b - tc) / CUT), 0, 1)
    buf *= np.interp(np.arange(len(buf)) / SR, tc, env).astype(np.float32)[:, None]


def _write(D, buf, out, notes, lower):
    """build/audio/music/score.wav and .m4a; out (film.json's score) gets their paths and the notes"""
    pk = float(np.abs(buf).max())
    if pk > .98: notes.append(f'peak {pk:.2f}: scaled to 0.98 ({lower})'); buf *= .98 / pk
    d_ = os.path.join(D, 'build', 'audio', 'music'); os.makedirs(d_, exist_ok=True)
    wf = os.path.join(d_, 'score.wav')
    with wave.open(wf, 'wb') as w_: w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((buf * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wf, '-c:a', 'aac', '-b:a', '160k', wf[:-4] + '.m4a'], check=True)
    out.update(file=os.path.relpath(wf[:-4] + '.m4a', os.path.join(D, 'build')), wav=os.path.relpath(wf, os.path.join(D, 'build')), notes=notes)


def timing(film):
    """what the code score is written against (audio/codescore.py): the lights, the eras' washes and burns, the growth, the end,
    the chord plan and tempo. A code score made for another timing is out of step with the picture."""
    L = film.get('light', {}); G = film.get('grow') or {}
    key = {'dur': film.get('dur'), 'light': [L.get(k) for k in ('lamp', 'lightsOut', 'lights', 'darks')], 'end': (film.get('end') or {}).get('t'),
           'epochs': [[e.get('on'), e.get('off'), e.get('offStyle'), bool(e.get('yr'))] for e in film.get('epochs', [])],
           'bands': [b.get('t') for b in G.get('bands', [])], 'music': {k: (film.get('music') or {}).get(k) for k in ('chords', 'bpm')}}
    return hashlib.sha1(json.dumps(key, sort_keys=True).encode()).hexdigest()[:12]


def _loud_rms(x):
    """the level where the music sounds: RMS over the 100 ms blocks within 30 dB of its loud level (not its silences)"""
    h = SR // 10; n = len(x) // h
    if not n: return _rms(x)
    p = np.mean(np.square(x[:n * h].reshape(n, h, 2), dtype=np.float64), axis=(1, 2))
    db = 10 * np.log10(p + 1e-12); on = db > max(-60.0, np.percentile(db, 95) - 30)
    return float(np.sqrt(p[on].mean())) if on.any() else _rms(x)


def lay_code(D, music, dur, voiced, silences, voice_wav=None, timing_=None):
    """film.music.source: code: build/audio/music/code.wav (audio/codescore.py) laid like the cues: UNDER_DB below the narration
    where it sounds, then `gain` (film.music.gain, dB), dipped under each voiced line. Returns film.json's score (file: None while
    there is no code score yet)."""
    f = os.path.join(D, 'build', 'audio', 'music', 'code.wav')
    out = {'source': 'code', 'cues': [], 'missing': [], 'file': None}
    if not os.path.exists(f): out['missing'] = ['code']; return out
    meta_f = f[:-4] + '.json'; meta = json.load(open(meta_f, encoding='utf-8')) if os.path.exists(meta_f) else {}
    notes = [] if timing_ is None or meta.get('timing') == timing_ else ['the code score was written for another timeline: run audio/codescore.py again']
    x = _read(f); N = int(dur * SR) + 1
    buf = np.zeros((N, 2), np.float32); buf[:min(N, len(x))] = x[:N]
    if _rms(buf) < 1e-4: raise SystemExit('music: the code score is silent')
    buf *= voice_level(voice_wav, voiced) * 10 ** (-UNDER_DB / 20) / _loud_rms(buf) * 10 ** (float((music or {}).get('gain', 0)) / 20)
    e = int(END_FADE * SR); buf[-e:] *= np.linspace(1, 0, e, dtype=np.float32)[:, None]
    _dip(buf, dur, voiced, silences, music)
    _write(D, buf, out, notes, 'lower film.music.gain')
    return out

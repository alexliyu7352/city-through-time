"""How loud the music sits under the narration (docs/SOUND.md "Levels"), as the preview plays it: the score track laid by compile
against the narration track, before the mix. For each music cue: the loudest second of music heard inside a spoken line, set
against that line (dB under the voice: more is quieter music), and the cue's quietest stretches (whether a line is spoken
over them). With --against, the same for another build and the change cue by cue.
    python -I audio/levels.py cities/<slug> [--against cities/<other>] [--quiet 3] [--json <out.json>]
Reads build/film.json (score.cues; cues: each line's t0 and its spoken length say), build/audio/music/score.wav and the voice
track's WAV beside its m4a. A cue's margin is what the ear judges under a line: a 1 s window wholly inside the line, stepped
0.1 s, against the RMS of the whole line; the quiet stretches are 4 s windows a second apart, digital silence left out."""
import argparse, json, os, sys
import numpy as np
import soundfile as sf

WIN, STEP, QWIN, SILENT_DB = 1.0, .1, 4.0, -80.0


def db(x): return 20 * np.log10(max(float(x), 1e-12))


def load(city):
    B = os.path.join(city, 'build'); F = json.load(open(os.path.join(B, 'film.json')))
    sc = F.get('score') or {}
    if not sc.get('wav'): sys.exit(f'levels: {city}: no laid score in film.json (score.wav)')
    m, sr = sf.read(os.path.join(B, sc['wav']), dtype='float64'); m = m.mean(1) if m.ndim > 1 else m
    v, sr2 = sf.read(os.path.join(B, F['voice']['file'][:-4] + '.wav'), dtype='float64'); v = v.mean(1) if v.ndim > 1 else v
    if sr2 != sr: sys.exit(f'levels: {city}: the score is {sr} Hz and the voice {sr2} Hz')
    lines = [(c['t0'], c['t0'] + c.get('say', c['t1'] - c['t0'])) for c in F.get('cues', [])]
    return F, sc.get('cues') or [], m, v, sr, lines


def measure(city, n_quiet):
    F, cues, m, v, sr, lines = load(city)
    rms = lambda x: float(np.sqrt(np.mean(x * x))) if len(x) else 0.0
    out = []
    for c in cues:
        best = None   # (margin, t, music dB, line dB)
        for a, b in lines:
            if b <= c['t0'] or a >= c['t1'] or b - a < WIN: continue
            lv = rms(v[int(a * sr):int(b * sr)])
            if lv <= 0: continue
            t = max(a, c['t0'])
            while t + WIN <= min(b, c['t1']) + 1e-9:
                mv = rms(m[int(t * sr):int((t + WIN) * sr)])
                if mv > 0 and (best is None or db(lv) - db(mv) < best[0]): best = (db(lv) - db(mv), t, db(mv), db(lv))
                t += STEP
        q, t = [], c['t0']
        while t + QWIN <= c['t1']:
            mv = rms(m[int(t * sr):int((t + QWIN) * sr)])
            if db(mv) > SILENT_DB: q.append((db(mv), t, any(a < t + QWIN and t < b for a, b in lines)))
            t += 1.0
        quiet = []
        for lv_, t_, vo in sorted(q):   # the quietest, at least 30 s apart
            if all(abs(t_ - u['t']) >= 30 for u in quiet): quiet.append({'t': round(t_, 1), 'db': round(lv_, 1), 'voiced': vo})
            if len(quiet) >= n_quiet: break
        seg = m[int(c['t0'] * sr):int(c['t1'] * sr)]
        out.append({'cue': c['id'], 't0': c['t0'], 't1': c['t1'], 'rms_db': round(db(rms(seg)), 2),
                    'under_voice_db': round(best[0], 2) if best else None, 'at': round(best[1], 2) if best else None,
                    'music_db': round(best[2], 2) if best else None, 'line_db': round(best[3], 2) if best else None, 'quiet': quiet})
    return out


def main():
    ap = argparse.ArgumentParser(description='music under the narration, cue by cue')
    ap.add_argument('city'); ap.add_argument('--against'); ap.add_argument('--quiet', type=int, default=3); ap.add_argument('--json')
    A = ap.parse_args()
    a = measure(A.city, A.quiet); b = measure(A.against, A.quiet) if A.against else None
    print(f"{'cue':12s} {'s':>17s}  {'under voice':>11s}  {'at s':>8s}" + (f"  {'before':>7s}  {'change':>6s}  {'cue level':>9s}" if b else '') + '   quietest (s, dB, voiced)')
    for i, c in enumerate(a):
        o = next((x for x in b or [] if x['cue'] == c['cue']), None)
        u = f"{c['under_voice_db']:9.2f} dB" if c['under_voice_db'] is not None else '        none'
        row = f"{c['cue']:12s} {c['t0']:8.1f}-{c['t1']:8.1f}  {u}  {c['at'] if c['at'] is not None else '':>8}"
        if b:
            ou = o and o['under_voice_db']
            row += (f"  {ou:7.2f}  {c['under_voice_db'] - ou:+6.2f}  {c['rms_db'] - o['rms_db']:+7.2f} dB" if ou is not None and c['under_voice_db'] is not None else '        -       -          -')
        row += '   ' + ', '.join(f"{q['t']} ({q['db']}{', voiced' if q['voiced'] else ''})" for q in c['quiet'])
        print(row)
    if A.json: json.dump({'city': A.city, 'cues': a, **({'against': A.against, 'before': b} if b else {})}, open(A.json, 'w'), indent=1)


if __name__ == '__main__':
    main()

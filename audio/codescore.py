"""The code score (city.yaml film.music.source: code; SKILL.md 10d): music written in code over the film's own timeline and played
on sampled instruments (audio/sampler.py), the fallback when a city has no generated or brought music: no model, offline, free.
Its sample libraries (VSCO 2 CE and VCSL, CC0, about 670 MB) are downloaded once: uv run python -I tools/instruments.py.
usage: python -I audio/codescore.py cities/<slug>      after compile and render/events.mjs (it reads build/film.json, events.json and
       export/timeline.json). Writes build/audio/music/code.wav (+ code.json: the timing it was written for, audio/lay.py timing())
       and lays it on the film like the cues (audio/lay.py lay_code: under the narration, dipped under each line), so the preview
       plays it and the mix lays it at once; compile lays it again on every run and says when the timeline has moved (run this again).
The palette of the white-model style: mallets and glass for things switching on, bowed vibraphone for held light, contrabass and
cellos as a floor, brass and timpani for the two weights (a burn, the turn), and the music dips just before a burn. Harmony follows
the film's sections; a city can change the chord plan (film.music.chords) and the tempo (film.music.bpm)."""
import datetime, json, os, sys, zlib
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sampler as S, sfx as X, lay as LAY
SR = X.SR
CITY = os.path.abspath(sys.argv[1])
B_ = os.path.join(CITY, 'build')   # (pipeline/layout.py)
FILM = json.load(open(os.path.join(B_, 'film.json'), encoding='utf-8'))
EVJ = json.load(open(os.path.join(B_, 'events.json'), encoding='utf-8'))
DUR = EVJ['dur']; EV = EVJ['ev']; LT = FILM['light']
MUSIC = FILM.get('music', {})
BPM = MUSIC.get('bpm', 100); BEAT = 60 / BPM
N = int((DUR + 3) * SR)
MUS, HIT = (np.zeros((N, 2), np.float32) for _ in range(2))
S.seed(7)
rng = np.random.default_rng(11)
USED = set()

def place(buf, events, g=1.0):
    ev = []
    for e in events:
        d = dict(e) if isinstance(e, dict) else dict(zip(('t', 'inst', 'pitch', 'dur', 'vel', 'pan'), e))
        if d['t'] < 0 or d['t'] > DUR + .5: continue
        USED.add(d['inst']); ev.append(d)
    if not ev: return
    y = S.render(ev, dur=N / SR, master=False); buf[:len(y)] += y[:len(buf)] * g

# ------------------------------------------------------------------ harmony: a chord plan over the film's sections
# chords as (bass, [pad pitches], [mallet arpeggio]); the plan maps epoch / band ids to chords and can be overridden by film.music.chords
CHORDS = {
    'Dm':  ('D2', ['A3', 'D4', 'F4'], ['D4', 'A4', 'F4', 'A4']),
    'Gm':  ('G2', ['D3', 'G3', 'Bb3'], ['G3', 'D4', 'Bb3', 'D4']),
    'Cm':  ('C2', ['G3', 'C4', 'Eb4'], ['C4', 'G4', 'Eb4', 'G4']),
    'Bb':  ('Bb1', ['F3', 'Bb3', 'D4'], ['Bb3', 'F4', 'D4', 'F4']),
    'F':   ('F2', ['C3', 'F3', 'A3'], ['F4', 'C5', 'A4', 'C5']),
    'Eb':  ('Eb2', ['Bb3', 'Eb4', 'G4'], ['Eb4', 'Bb4', 'G4', 'Bb4']),
    'Fsus': ('F2', ['C3', 'F3', 'Bb3'], ['F4', 'C5', 'Bb4', 'C5']),
    'Gsus': ('G2', ['D3', 'G3', 'C4'], ['G4', 'D5', 'C5', 'D5']),
    'Ab':  ('Ab1', ['Eb3', 'Ab3', 'C4'], ['Ab4', 'Eb5', 'C5', 'Eb5']),
    'Fm':  ('F1', ['C3', 'F3', 'Ab3'], ['F4', 'C5', 'Ab4', 'C5']),
    'Db':  ('Db2', ['Ab3', 'Db4', 'F4'], ['Db4', 'Ab4', 'F4', 'Ab4']),
    'C':   ('C2', ['G3', 'C4', 'E4'], ['C4', 'G4', 'E4', 'G4']),
}
PLAN = {'prologue': 'Dm', 'burn': 'Cm', 'turn': 'Ab', 'turn_floor': 'Fm', 'coda': 'Db', 'lights': 'C'}
PLAN.update(MUSIC.get('chords', {}))
EPOCH_CHORDS = ['Gm', 'Bb', 'F', 'Fsus', 'Eb', 'Ab', 'Ab', 'Ab']     # by epoch order (qin, han, tang, ming, airport, dig, ...)
BAND_BASS = ['Eb2', 'F2', 'G2', 'Ab2', 'Bb2', 'C3', 'D3', 'Eb3']     # the growth: the bass climbs a step per band

def chord_of(key): return CHORDS[PLAN.get(key, key)] if PLAN.get(key, key) in CHORDS else CHORDS['Dm']

def score():
    m, h = [], []
    lamp_t, lo, lights, end = LT['lamp'], LT['lightsOut'], LT['lights'], FILM['end']['t']
    darks = LT.get('darks', [])
    dark0, dark1 = (darks[0] if darks else (lights, lights))
    epochs = sorted(FILM.get('epochs', []), key=lambda e: e['on'])
    grow = FILM.get('grow'); bands = sorted(grow['bands'], key=lambda b: b['t']) if grow else []
    first_on = min([e['on'] for e in epochs if e['on'] > lamp_t + 1] + [bands[0]['t'] if bands else dark0])
    # white: one held, bowed tone, the room
    m += [dict(t=.3, inst='vibraphone_bowed', pitch='G4', dur=lo - .6, vel=.33, pan=-.2, attack=.4, release=.5),
          dict(t=.8, inst='vibraphone_bowed', pitch='C5', dur=lo - 1.1, vel=.28, pan=.25, attack=.4, release=.5)]
    # prologue (lamp -> first epoch): an open floor, a slow mallet pulse
    bass, pad, arp = chord_of('prologue')
    m += [dict(t=lamp_t, inst='contrabass', pitch=bass, dur=first_on - lamp_t - .3, vel=.5, attack=.3, release=.4),
          dict(t=lamp_t + .2, inst='cellos', pitch=pad[0], dur=first_on - lamp_t - .5, vel=.4, pan=-.25, attack=.6, release=.4),
          dict(t=lamp_t + .6, inst='vibraphone_bowed', pitch=pad[2].replace('4', '5'), dur=first_on - lamp_t - 1.2, vel=.34, pan=.3, attack=.8)]
    k = 0; t = lamp_t + BEAT
    while t < first_on - .5:
        m.append(dict(t=t, inst='marimba', pitch=arp[k % 4], dur=.4, vel=.3, pan=-.3 + .2 * (k % 3))); k += 1; t += BEAT * 2
    # epochs: each wash gets its chord (floor + pad + a hand-chime), held until the next epoch; a burn ends in a weight and a bare floor
    for i, e in enumerate(epochs):
        if e['on'] <= lamp_t + 1 or e['on'] >= dark0: continue
        nxt = min([x['on'] for x in epochs if x['on'] > e['on']] + [bands[0]['t'] if bands and bands[0]['t'] > e['on'] else dark0, dark0])
        stop = min(nxt, e['off']) if e.get('off') is not None else nxt
        bass, pad, arp = CHORDS[EPOCH_CHORDS[i % len(EPOCH_CHORDS)]]
        m += [dict(t=e['on'], inst='contrabass', pitch=bass, dur=max(1.5, stop - e['on'] - .2), vel=.52, attack=.2, release=.5),
              dict(t=e['on'] + .1, inst='cellos', pitch=pad[0], dur=max(1.5, stop - e['on'] - .3), vel=.4, pan=-.2, attack=.5, release=.5),
              dict(t=e['on'] + .3, inst='violas', pitch=pad[1], dur=max(1.5, stop - e['on'] - .5), vel=.3, pan=.2, attack=.9, release=.5),
              dict(t=e['on'] + .2, inst='hand_chimes', pitch=arp[0].replace('4', '5'), dur=1.5, vel=.5, pan=.3)]
        if e.get('yr'):   # a layer that lights dated things: a vibraphone chord as it arrives
            m += [dict(t=e['on'] + .4, inst='vibraphone', pitch=p, dur=1.6, vel=.3, pan=-.3 + .3 * j) for j, p in enumerate(pad)]
        if e.get('off') is not None and e.get('offStyle') == 'burn':
            b0 = e['off']; bass2, pad2, _ = chord_of('burn')
            h += [dict(t=b0, inst='timpani', pitch='C3', dur=3, vel=1.0), dict(t=b0, inst='gran_cassa', pitch='hit', vel=.95), dict(t=b0, inst='gong2', pitch='big', vel=.75, pan=.1),
                  dict(t=b0 + .01, inst='bass_drum', pitch=None, vel=.9)]
            for p, inst, v in (('C2', 'tuba', .9), ('C3', 'trombone', .85), ('G3', 'trombone', .8), ('Eb4', 'horn', .75), ('C4', 'horn', .75)):
                h.append(dict(t=b0, inst=inst, pitch=p, dur=1.2, vel=v, release=.6))
            m += [dict(t=b0 + .4, inst='contrabass', pitch=bass2, dur=max(1.5, nxt - b0 - .5), vel=.48, attack=.6, release=.6),
                  dict(t=b0 + 1.2, inst='vibraphone_bowed', pitch=pad2[1], dur=max(1.0, nxt - b0 - 1.6), vel=.33, pan=-.3, attack=.6)]
    # marks (a mound, a roof, a site lighting up): one glass-like note each
    for ev in EV:
        if ev['type'] == 'mark' and ev['t'] < dark0:
            m.append(dict(t=ev['t'], inst='hand_chimes', pitch=['D6', 'F6', 'A5', 'C6'][zlib.crc32(ev.get('id', '').encode()) % 4], dur=1.4, vel=.42, pan=float(rng.uniform(-.5, .5))))
    # the growth: the bass climbs a step per band, mallets divide finer each band, pizzicato from the second, horns from the fourth
    if bands:
        gend = dark0
        for i, b in enumerate(bands):
            a = b['t']; z = bands[i + 1]['t'] if i + 1 < len(bands) else gend
            bass = BAND_BASS[i % len(BAND_BASS)]
            m.append(dict(t=a, inst='contrabass', pitch=bass, dur=z - a + .1, vel=.55, attack=.05, release=.2))
            m.append(dict(t=a, inst='cellos', pitch=bass.replace('2', '3').replace('1', '2'), dur=z - a + .1, vel=.4, pan=-.2, attack=.1, release=.2))
            div = [2, 2, 4, 4, 6, 6][min(i, 5)]
            root = S.name(S.midi(bass) + 24)
            arp = [root, S.name(S.midi(root) + 7), S.name(S.midi(root) + 4), S.name(S.midi(root) + 7)]
            n = int(round((z - a) / (BEAT / div)))
            for q in range(n):
                m.append(dict(t=a + q * BEAT / div, inst='marimba', pitch=arp[q % 4], dur=.2, vel=.4 + .1 * (q % div == 0), pan=-.35 + .7 * ((q * 3) % 7) / 6))
            m.append(dict(t=a, inst='hand_chimes', pitch=S.name(S.midi(root) + 12), dur=1.2, vel=.5, pan=.3))
            if i >= 1:
                for q in range(n // 2):
                    m.append(dict(t=a + q * BEAT / div * 2, inst='violins_pizz', pitch=S.name(S.midi(arp[(q + 2) % 4]) + 12), dur=.2, vel=.38, pan=.4))
            if i == 3:
                m += [dict(t=a, inst='horn', pitch=p, dur=gend - a - .3, vel=.5, pan=pn, attack=.8, release=.8) for p, pn in ((S.name(S.midi(bass) + 12), -.2), (S.name(S.midi(bass) + 19), .2))]
    # the turn (after the dark): first sound after the silence, warm brass + timpani, then a minor floor with a heartbeat
    if darks:
        T0 = dark1 + .3; bass, pad, _ = chord_of('turn'); bassf, padf, _ = chord_of('turn_floor')
        for p, inst, v, pn in ((pad[0].replace('3', '2'), 'trombone', .75, -.2), (pad[1].replace('3', '3'), 'trombone', .7, .2), (pad[0], 'horn', .75, -.3), (pad[2], 'horn', .72, .3), (bass, 'tuba', .7, 0)):
            h.append(dict(t=T0, inst=inst, pitch=p, dur=3.0, vel=v, pan=pn, attack=.05, release=1.2))
        h += [dict(t=T0, inst='timpani', pitch=bass.replace('1', '2'), dur=3, vel=.85), dict(t=T0, inst='gran_cassa', pitch='hit', vel=.7), dict(t=T0, inst='sus_cymbal', pitch='bow', vel=.55, pan=.2)]
        coda0 = T0 + (lights - T0) * .55
        m += [dict(t=T0 + .2, inst='organ_soft', pitch=p, dur=coda0 - T0, vel=.33, pan=pn, attack=.6, release=.6) for p, pn in ((padf[0], 0), (padf[1], -.3), (padf[2], .3))]
        m += [dict(t=T0 + 2.5, inst='contrabass', pitch=bassf, dur=coda0 - T0 - 2.5, vel=.52, attack=.3), dict(t=T0 + 2.5, inst='cellos', pitch=padf[0], dur=coda0 - T0 - 2.5, vel=.4, pan=-.2, attack=.4)]
        for q in range(0, int((coda0 - T0 - 3) / BEAT), 2):
            h.append(dict(t=T0 + 3 + q * BEAT, inst='timpani', pitch=bassf.replace('1', '2'), dur=1, vel=.5 + .05 * (q % 4 == 0)))
        for ev in EV:   # the tombs again: one low glass note each
            if ev['type'] == 'mark' and ev['t'] > dark1:
                m.append(dict(t=ev['t'], inst='vibraphone', pitch='G5', dur=1.6, vel=.45, pan=float(rng.uniform(-.5, .5))))
        bassc, padc, _ = chord_of('coda')
        m += [dict(t=coda0, inst='contrabass', pitch=bassc, dur=lights - coda0, vel=.5, attack=.4),
              dict(t=coda0, inst='vibraphone_bowed', pitch=padc[1], dur=lights - coda0, vel=.36, pan=-.3, attack=.6),
              dict(t=coda0 + 2.0, inst='vibraphone_bowed', pitch=padc[2], dur=lights - coda0 - 2, vel=.34, pan=.3, attack=.8),
              dict(t=coda0, inst='organ_soft', pitch=padc[0], dur=lights - coda0, vel=.28, attack=.5)]
    # lights up: a major chord, horns, a bell on the end card
    bassl, padl, _ = chord_of('lights')
    m += [dict(t=lights, inst='contrabass', pitch=bassl, dur=DUR - lights, vel=.5, attack=.4, release=1.5),
          dict(t=lights, inst='horn', pitch=padl[2].replace('4', '3'), dur=3.5, vel=.5, pan=-.2, attack=.6, release=1.2),
          dict(t=lights, inst='horn', pitch=padl[0], dur=3.5, vel=.5, pan=.2, attack=.6, release=1.2),
          dict(t=lights, inst='vibraphone_bowed', pitch=padl[1].replace('4', '5'), dur=DUR - lights - .5, vel=.4, pan=-.3, attack=.6),
          dict(t=lights, inst='vibraphone_bowed', pitch=padl[2].replace('4', '5'), dur=DUR - lights - .5, vel=.36, pan=.3, attack=.9),
          dict(t=end, inst='tubular_bells', pitch=padl[1].replace('4', '5'), dur=4, vel=.6), dict(t=end + 2 * BEAT, inst='hand_chimes', pitch=padl[2].replace('4', '6'), dur=3, vel=.35, pan=.4),
          dict(t=end + 3 * BEAT, inst='hand_chimes', pitch=padl[1].replace('4', '6'), dur=3, vel=.3, pan=-.4)]
    place(MUS, m); place(HIT, h)

def gate(a, b_, floor, f=.06):
    g = np.ones(N); i0, i1 = int(a * SR), int(b_ * SR); k = int(f * SR)
    if i1 > i0 + k: g[i0:i0 + k] = np.linspace(1, floor, k); g[i0 + k:i1] = floor
    return g[:, None]

def main():
    if MUSIC.get('source') != 'code': raise SystemExit(f"codescore: {os.path.basename(CITY)}'s film.music.source is {MUSIC.get('source', 'cues')!r}, not code")
    score()
    mus = S.room(MUS, .6, .24) * .5; hit = S.room(HIT, .7, .26) * .75
    for e in EV:   # a short suck-out before a burn
        if e['type'] == 'burn': mus *= gate(e['t'] - .45, e['t'] - .005, .05)
    d_ = os.path.join(B_, 'audio', 'music'); os.makedirs(d_, exist_ok=True)
    sf.write(os.path.join(d_, 'code.wav'), (mus + hit).astype(np.float32), SR)
    json.dump({'timing': LAY.timing(FILM), 'instruments': sorted(USED), 'made': datetime.datetime.now().isoformat(timespec='seconds')},
              open(os.path.join(d_, 'code.json'), 'w', encoding='utf-8'), indent=1)
    open(os.path.join(B_, 'audio', 'instrument_credits.txt'), 'w', encoding='utf-8').write('\n'.join(S.credits(sorted(USED))) + '\n')
    print(f'code score: {DUR:.1f} s, instruments: {", ".join(sorted(USED))}')
    # lay it now (compile does the same on every run), from the timeline compile exported
    tl = json.load(open(os.path.join(B_, 'export', 'timeline.json'), encoding='utf-8'))
    voiced = [(l['t0'], l['t0'] + l['voice']) for l in tl['lines'] if l.get('voice')]
    vw = os.path.join(B_, 'audio', 'voice', f"track_{tl['voice']['lang']}.wav") if voiced and tl.get('voice') else None
    out = LAY.lay_code(CITY, MUSIC, FILM['dur'], voiced, [(s['t0'], s['t1']) for s in tl.get('silences', [])], vw, LAY.timing(FILM))
    FILM['score'] = out
    sx = FILM.get('sfx') or {}
    if sx.get('file'):   # the sound effects again, now that there is a score to stand out from (lay_sfx: SFX_OVER)
        FILM['sfx'] = LAY.lay_sfx(CITY, sx['kinds'], [tuple(e) for e in sx['events']], FILM['dur'], voiced, vw, os.path.join(d_, 'score.wav'))
    json.dump(FILM, open(os.path.join(B_, 'film.json'), 'w'), ensure_ascii=False, indent=1)
    print(f"laid: {out['file']}" + ''.join('; ' + n for n in out.get('notes', [])))

if __name__ == '__main__':
    main()

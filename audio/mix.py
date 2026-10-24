"""The mix of a city-through-time film -> <city>/build/audio/mix.wav (+ stems/*.wav).
usage: python -I audio/mix.py <city_dir>            the mix
       python -I audio/mix.py <city_dir> --kit      film.sfx's one-shots (build/audio/sfx/<kind>.wav), before compile lays them
It lays the tracks compile laid on the timeline: the score (film.score: the cues of film.music, or the code score; audio/lay.py, already
levelled against the narration and dipped under it), the sound effects (film.sfx) and the narration (film.voice). The score and the
effects go through a gentle bus compressor, all of it falls silent in the film's dark stretches, and the master lands at -14.4 LUFS,
true peak -4.6 dB (render/mux.mjs then takes it to -14). Reads <city>/build/film.json and events.json (the page's events)."""
import os, sys, json
import numpy as np, soundfile as sf, soxr
from scipy.signal import butter, sosfilt
from scipy.ndimage import uniform_filter1d, maximum_filter1d
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sampler as S, sfx as X
SR = X.SR
CITY = os.path.abspath(sys.argv[1])
B_ = os.path.join(CITY, 'build')   # (pipeline/layout.py)
FILM = json.load(open(os.path.join(B_, 'film.json'), encoding='utf-8'))
EVJ = json.load(open(os.path.join(B_, 'events.json'), encoding='utf-8'))
DUR = EVJ['dur']; LT = FILM['light']
SCORE, VOICE = FILM.get('score'), FILM.get('voice')
SFX = FILM.get('sfx') or {}   # city.yaml film.sfx: the page events that keep a sound beside a laid score (e.g. the lamp,
                              # the burning, the lights going out), laid by compile as one track from the one-shots --kit makes
N = int((DUR + 3) * SR)
rng = np.random.default_rng(11)

def sos(kind, f, o=2): return butter(o, f, kind, fs=SR, output='sos')
def lpf(x, f, o=2): return sosfilt(sos('low', min(f, SR * .45), o), x, axis=0)
def hpf(x, f, o=2): return sosfilt(sos('high', f, o), x, axis=0)
def bpf(x, a, b, o=2): return sosfilt(sos('band', [a, min(b, SR * .45)], o), x, axis=0)
def tv(d): return np.arange(int(d * SR)) / SR
def put(buf, x, at, g=1.0, pan=0.0):
    if at < 0 or at > DUR + 1: return
    if x.ndim == 1: X.add(buf, x.astype(np.float32), at, g, pan)
    else:
        s = int(at * SR); e = min(len(buf), s + len(x))
        if s < len(buf): buf[s:e] += x[:e - s] * g
# ------------------------------------------------------------------ the kit: the showroom's sounds (relays, the lamp strike, the burn)
def relay(v=1.0):
    a = X.clack(.7, v); b_ = X.thump(.6 * v, 55)
    n = max(len(a), len(b_)); y = np.zeros(n); y[:len(a)] += a; y[:len(b_)] += b_ * .8
    return y
def lamp(v=1.0):
    t = tv(1.4)
    zap = hpf(rng.standard_normal(len(t)), 2500) * np.exp(-t / .012) * .6
    whump = np.sin(2 * np.pi * (52 + 30 * np.exp(-t / .05)) * t) * np.exp(-t / .35)
    buzz = np.sin(2 * np.pi * 100 * t) * (1 - np.exp(-t / .08)) * np.exp(-t / .5) * .12
    return (zap + whump + buzz) * v
def swell(d, f0, f1, v=1.0, q=.5):
    """the air of a light wash: band noise whose centre slides f0 -> f1, rising then settling"""
    t = tv(d); x = rng.standard_normal(len(t)); out = np.zeros_like(x); seg_ = 2048
    for i in range(0, len(x), seg_):
        k = i / len(x); fc = f0 * (f1 / f0) ** k
        out[i:i + seg_] = bpf(x[max(0, i - 512):i + seg_], fc * (1 - q / 2), fc * (1 + q / 2))[-len(x[i:i + seg_]):]
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    return out * e * v
def crackle(d=1.8, v=1.0):
    """the burn: a flicker of crackles under a falling air band"""
    t = tv(d); x = rng.standard_normal(len(t)) * (rng.random(len(t)) < .012)
    x = bpf(x, 1200, 7000) * np.exp(-t / (d * .6)) * 2.0
    return (x + swell(d, 2400, 300, .6, .6)) * v
# ------------------------------------------------------------------ mix and master
def load(rel):   # a track compile wrote (build/<rel>), stereo at SR, the film's length
    x, sr = sf.read(os.path.join(B_, rel), dtype='float32', always_2d=True)
    if sr != SR: x = soxr.resample(x, sr, SR).astype(np.float32)
    if x.shape[1] == 1: x = np.repeat(x, 2, 1)
    y = np.zeros((N, 2), np.float32); y[:min(N, len(x))] = x[:N]; return y
def lufs(x):
    import subprocess, tempfile, re
    with tempfile.TemporaryDirectory() as d:   # (the film's length as a float WAV, about 300 MB: removed after each measure)
        f = os.path.join(d, 'm.wav'); sf.write(f, x.astype(np.float32), SR)
        out = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', f, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', out)[-1])
def true_peak(x): return float(np.abs(soxr.resample(x, SR, 4 * SR)).max())
def tp_limit(x, ceil):
    up = np.abs(soxr.resample(x, SR, 4 * SR)).max(1); n = len(x)
    pk = np.pad(up, (0, max(0, n * 4 - len(up))))[:n * 4].reshape(-1, 4).max(1)
    g0 = np.minimum(1.0, ceil / np.maximum(pk, 1e-9)); look = int(.004 * SR)
    g = -maximum_filter1d(-g0, 2 * look + 1); g = uniform_filter1d(g, look); g = np.minimum(g, -maximum_filter1d(-g0, 3))
    return x * g[:, None]

def kit():
    """film.sfx's one-shots, each through the fx room and filters the mix gives the fx, to build/audio/sfx/<kind>.wav
    (python audio/mix.py <city> --kit): compile lays them on the timeline (audio/lay.py), the preview plays that track
    and the mix lays it, so the preview sounds as the film will"""
    burn = max([e.get('burn') or 1.5 for e in FILM.get('eras', []) if e.get('sinkStyle') == 'burn'] or [1.5])
    def lights(b): put(b, relay(.9), .05, .8, -.4); put(b, relay(.7), .19, .6, .4)
    make = {'relay': lambda b: put(b, relay(1.0), .05, .9, -.3), 'lamp': lambda b: put(b, lamp(1.0), .05, .9, .1),
            'burn': lambda b: put(b, crackle(burn + .6, 1.0), .05, .6, .1), 'lights': lights}
    d_ = os.path.join(B_, 'audio', 'sfx'); os.makedirs(d_, exist_ok=True)
    for k in SFX.get('kinds', []):
        if k not in make: raise SystemExit(f'mix --kit: no one-shot for {k!r} (there are: {", ".join(make)})')
        b = np.zeros((int((burn + 3) * SR), 2), np.float32); make[k](b)
        x = hpf(S.room(b, .35, .12), 38, 2); x = x - (1 - 10 ** (-5 / 20)) * lpf(x, 62, 2)
        n = len(x) - int(np.argmax(np.abs(x[::-1]).max(1) > 1e-4))   # (to where it falls silent)
        sf.write(os.path.join(d_, k + '.wav'), x[:n].astype(np.float32), SR); print(f'kit: {k} {n / SR:.1f} s')

def main():
    if not (SCORE and SCORE.get('wav')):
        raise SystemExit('mix: no score in film.json: compile lays the cues (film.music.source: cues) or the code score '
                         '(source: code: python -I audio/codescore.py <city> first)')
    mus = load(SCORE['wav'])
    fx = load(SFX['wav']) if SFX.get('wav') else np.zeros((N, 2), np.float32)
    def gate(a, b_, floor, f=.06):
        g = np.ones(N); i0, i1 = int(a * SR), int(b_ * SR); k = int(f * SR)
        if i1 > i0 + k: g[i0:i0 + k] = np.linspace(1, floor, k); g[i0 + k:i1] = floor
        return g[:, None]
    for a, b_ in LT.get('darks', []):   # the silence
        mus *= gate(a + .05, b_ + .25, .0, .25); fx *= gate(a + .3, b_ + .25, 0., .2)
    stems = {'music': mus, 'fx': fx}
    if VOICE: stems['voice'] = load(VOICE['file'][:-4] + '.wav')   # (the narration track's WAV beside its m4a)
    shelf = 10 ** (-5 / 20)
    x = hpf(stems['music'], 38, 2); stems['music'] = x - (1 - shelf) * lpf(x, 62, 2)   # (the fx track was filtered in --kit)
    bus = stems['music'] + stems['fx']
    lvl = np.sqrt(uniform_filter1d((bus ** 2).max(1), int(.012 * SR)))
    thr = 10 ** (-12 / 20) * np.percentile(lvl, 99.9)
    g = np.where(lvl > thr, (thr + (lvl - thr) / 2.5) / np.maximum(lvl, 1e-9), 1.0)
    g = uniform_filter1d(-maximum_filter1d(-g, int(.008 * SR)), int(.03 * SR))
    mix = bus * g[:, None] + stems.get('voice', 0)
    mix = mix[:int(DUR * SR)]
    fade = int(1.2 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
    for _ in range(3):
        I = lufs(mix); mix = mix * 10 ** ((-14.4 - I) / 20); mix = tp_limit(mix, 10 ** (-4.6 / 20))
    print(f'master: {lufs(mix):.2f} LUFS, true peak {20 * np.log10(true_peak(mix)):.2f} dBTP')
    os.makedirs(os.path.join(B_, 'audio', 'stems'), exist_ok=True)
    sf.write(os.path.join(B_, 'audio', 'mix.wav'), mix.astype(np.float32), SR)
    for name, b_ in stems.items(): sf.write(os.path.join(B_, 'audio', 'stems', name + '.wav'), b_[:int(DUR * SR)].astype(np.float32), SR)
    m = mix.mean(1); Fq = np.fft.rfftfreq(len(m), 1 / SR); P = np.abs(np.fft.rfft(m)) ** 2
    lo = P[(Fq > 20) & (Fq < 120)].sum(); rest = P[(Fq >= 120) & (Fq < 16000)].sum()
    print(f'low/rest {10 * np.log10(lo / rest):.1f} dB')

if __name__ == '__main__':
    kit() if '--kit' in sys.argv[2:] else main()

"""Mend the seams of a generated voice (docs/SOUND.md "Voice and the timeline"). A text-to-speech service that makes its audio in
pieces can join them with a jump: one sample to the next the wave leaps (by up to a third of full scale), heard as a click or a pop
in the line, on every playback, phone speaker included. A seam is found by its shape: the second difference of the wave swings
+D then -D across one sample, far above its level around (a consonant's noise and a voiced pulse do not have that shape at the
voice's own sample rate), and the jump D is audible. It is mended by spreading the jump over a few milliseconds either side
(a smoothed step of -D): the length, timing and every other sample stay as they were.

voicecut.py mends each take before it cuts it. Lines already cut, without cutting them again:
    python -I audio/seams.py <file or dir> ... --out <dir>      (writes the mended files there, same names; --check: only counts)
Run on the voice's own files (the service's sample rate), before any resampling: a resampled jump rings and no longer has its shape."""
import argparse, glob, os, sys
import numpy as np
import soundfile as sf
from scipy.ndimage import uniform_filter1d

SCORE, MIN_JUMP, HALF = 10.0, .01, .01   # how far over its surroundings, the smallest jump mended (about -40 dB), the spread (s) either side


def find(x, sr):
    """the seams of a mono wave: [(sample where the jump lands, jump)]"""
    r = np.zeros_like(x); r[2:] = x[2:] - 2 * x[1:-1] + x[:-2]   # a jump D between j-1 and j: r[j] = +D, r[j+1] = -D
    w = int(.01 * sr); n = 2 * w + 1
    around = uniform_filter1d(r ** 2, n) * n
    cand = np.where((np.abs(r[:-1]) > MIN_JUMP) & (np.sign(r[:-1]) == -np.sign(r[1:])) & (np.abs(r[:-1] + r[1:]) < .5 * np.abs(r[:-1])))[0]
    out = []
    for j in cand:
        if j < 3 or j > len(x) - 4: continue
        level = np.sqrt(max((around[j] - r[j] ** 2 - r[j + 1] ** 2) / (n - 2), 1e-12))   # the level around, the seam itself left out
        jump = (x[j] - x[j - 1]) - .5 * ((x[j - 1] - x[j - 2]) + (x[j + 1] - x[j]))   # less the slope the wave already had
        if abs(r[j]) > SCORE * level and abs(jump) >= MIN_JUMP: out.append((int(j), float(jump)))
    return out


def mend(x, sr):
    """x (mono or channels last) with its seams mended, and the seams found"""
    y = np.array(x, dtype=np.float64, copy=True); h = max(1, int(HALF * sr)); seams = []
    k = np.arange(-h, h); ramp = .5 - .5 * np.cos(np.pi * (k + h + .5) / (2 * h))   # 0 -> 1 across the seam
    for _ in range(4):   # two seams close together show only once the first is mended
        new = find(y.mean(1) if y.ndim > 1 else y, sr)
        if not new: break
        for j, d in new:
            a, b = max(0, j - h), min(len(y), j + h)
            fix = d * (ramp[a - (j - h):b - (j - h)] - (np.arange(a, b) >= j))   # the jump taken out at j, given back smoothly around it
            y[a:b] += fix[:, None] if y.ndim > 1 else fix
        seams += new
    return y.astype(np.asarray(x).dtype), seams


def main():
    ap = argparse.ArgumentParser(description='mend the seams of a generated voice')
    ap.add_argument('paths', nargs='+'); ap.add_argument('--out'); ap.add_argument('--check', action='store_true')
    A = ap.parse_args()
    if not A.check and not A.out: sys.exit('seams: give --out <dir> (the mended files go there) or --check')
    files = sorted(f for p in A.paths for f in (glob.glob(os.path.join(p, '*')) if os.path.isdir(p) else [p])
                   if f.lower().endswith(('.wav', '.flac')))
    if A.out: os.makedirs(A.out, exist_ok=True)
    total, worst = 0, []
    for f in files:
        info = sf.info(f); x, sr = sf.read(f, dtype='float64')
        y, seams = mend(x, sr); total += len(seams); worst += [(abs(d), os.path.basename(f), j / sr) for j, d in seams]
        if A.out: sf.write(os.path.join(A.out, os.path.basename(f)), y, sr, subtype=info.subtype)
    print(f'seams: {total} mended in {len(files)} files' + ('' if A.out else ' (counted only)'))
    for d, f, t in sorted(worst, reverse=True)[:8]: print(f'  {f} {t:.3f} s: jump {d:.3f}')


if __name__ == '__main__':
    main()

"""Cut voice takes into one file per line (docs/SOUND.md "Voice and the timeline"). A take is one generation of several lines
read as continuous speech, whole sentences, so a sentence that the subtitles split over two lines keeps its flow. Each line is
found in its take by forced alignment of the known words (torchaudio MMS_FA) and cut at the quietest point between its last
word and the next line's first: the files laid end to end are the take again, its own pauses included. Nothing is trimmed at
the take's start or end (trimming eats first words).

    python -I audio/voicecut.py --takes <dir of <take>.wav> --lines <tsv> --out <city>/build/audio/voice/<lang>

<tsv>: a header, then take, line id, the line's words as said (numbers in words, as the voice text has them), in film order.
Writes <out>/<line id>.flac and <out>/takes.json {line id: [take, start s, end s]}: compile lays a line that starts where the
line before it in the same take ends straight after it (no gap of its own), and keeps its usual gaps between takes.
Prints the words the aligner found least sure of (a misread, a skipped or an added word shows there): listen to those first.
Number words always score near 0 with this model (its training text had the digits taken out), wherever they are said right.
Needs torch and torchaudio (CPU is enough; the model, 1.2 GB, downloads once to TORCH_HOME)."""
import argparse, csv, json, os, re, unicodedata
import numpy as np
import soundfile as sf

FADE_IN, FADE_OUT = .005, .02   # at a cut between two lines of a take
CHUNK_S, CTX_S = 30.0, 1.0      # the aligner hears the take in pieces this long, with this much either side for context
NUMBER_WORDS = set('zero oh one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen '
                   'eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million point first second '
                   'third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth fourteenth fifteenth sixteenth '
                   'seventeenth eighteenth nineteenth twentieth thirtieth'.split())   # (left out of the least-sure list: see above)


def words_of(text):
    """the words as the aligner spells them: lowercase a-z and apostrophes, accents dropped, hyphens and dashes split words"""
    t = unicodedata.normalize('NFKD', text.lower().replace('’', "'"))
    t = ''.join(c for c in t if not unicodedata.combining(c))
    return [w.strip("'") for w in re.split(r"[^a-z']+", t) if w.strip("'")]


def emission_of(model, wav16, sr16):
    """the aligner's frame-by-frame letter probabilities for a whole take, heard in overlapping pieces"""
    import torch
    n, c, k = len(wav16), int(CTX_S * sr16), int(CHUNK_S * sr16)
    out = []
    for a in range(0, n, k):
        b = min(n, a + k); a0, b0 = max(0, a - c), min(n, b + c)
        with torch.inference_mode():
            e, _ = model(torch.from_numpy(wav16[a0:b0]).float()[None])
        f = e.shape[1] / (b0 - a0)   # frames per sample
        out.append(e[0, round((a - a0) * f):round((b - a0) * f)])
    return torch.cat(out)


def quietest(x, sr, t0, t1):
    """the middle of the quietest 10 ms between t0 and t1 seconds (widened to 80 ms when the words touch)"""
    if t1 - t0 < .08: m = (t0 + t1) / 2; t0, t1 = m - .04, m + .04
    a, b, h = max(0, int(t0 * sr)), min(len(x), int(t1 * sr)), int(.01 * sr)
    if b - a <= h: return (t0 + t1) / 2
    e = np.convolve(x[a:b] ** 2, np.ones(h), 'valid')
    return (a + int(np.argmin(e)) + h // 2) / sr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--takes', required=True); ap.add_argument('--lines', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--worst', type=int, default=6, help='the least sure words listed per take')
    A = ap.parse_args()
    import torch, torchaudio
    from torchaudio.pipelines import MMS_FA
    model, tok, align = MMS_FA.get_model(), MMS_FA.get_tokenizer(), MMS_FA.get_aligner()
    model.eval(); sr16 = int(MMS_FA.sample_rate)
    takes = {}
    with open(A.lines, encoding='utf-8') as f:
        for row in list(csv.reader(f, delimiter='\t'))[1:]:
            takes.setdefault(row[0], []).append((row[1], row[2]))
    os.makedirs(A.out, exist_ok=True)
    index, report = {}, []
    for take, lines in takes.items():
        x, sr = sf.read(os.path.join(A.takes, take + '.wav'), dtype='float32')
        x = x.mean(1) if x.ndim > 1 else x
        wav16 = torchaudio.functional.resample(torch.from_numpy(x), sr, sr16).numpy()
        words, owner = [], []
        for i, (_, said) in enumerate(lines):
            w = words_of(said); words += w; owner += [i] * len(w)
        em = emission_of(model, wav16, sr16)
        spans = align(em, tok(words))
        sec = len(wav16) / sr16 / em.shape[0]   # seconds per frame
        wt = [(s[0].start * sec, s[-1].end * sec, sum(q.score * (q.end - q.start) for q in s) / sum(q.end - q.start for q in s)) for s in spans]
        first = [owner.index(i) for i in range(len(lines))]
        cuts = [0.0] + [quietest(x, sr, wt[first[i + 1] - 1][1], wt[first[i + 1]][0]) for i in range(len(lines) - 1)] + [len(x) / sr]
        for i, (lid, said) in enumerate(lines):
            a, b = int(round(cuts[i] * sr)), int(round(cuts[i + 1] * sr))
            y = x[a:b].copy()
            if i > 0: n = int(FADE_IN * sr); y[:n] *= np.linspace(0, 1, n)
            if i < len(lines) - 1: n = int(FADE_OUT * sr); y[-n:] *= np.linspace(1, 0, n)
            sf.write(os.path.join(A.out, lid + '.flac'), y, sr, subtype='PCM_16')
            index[lid] = [take, round(a / sr, 4), round(b / sr, 4)]
            ws = [k for k in range(len(words)) if owner[k] == i]
            report.append((take, lid, (b - a) / sr, len(ws) / max(.1, wt[ws[-1]][1] - wt[ws[0]][0])))
        worst = sorted((k for k in range(len(words)) if words[k] not in NUMBER_WORDS), key=lambda k: wt[k][2])[:A.worst]
        print(f'{take}: {len(x) / sr:.1f} s, {len(lines)} lines, {len(words)} words, least sure: '
              + ', '.join(f'{words[k]} {wt[k][0]:.1f}s ({wt[k][2]:.2f})' for k in worst), flush=True)
    json.dump(index, open(os.path.join(A.out, 'takes.json'), 'w'), indent=0)
    r = sorted(q[3] for q in report)
    print(f'{len(report)} lines cut; words a second (first word to last) median {r[len(r) // 2]:.2f}, slowest '
          + ', '.join(f'{q[1]} {q[3]:.2f}' for q in sorted(report, key=lambda q: q[3])[:3]) + ', fastest '
          + ', '.join(f'{q[1]} {q[3]:.2f}' for q in sorted(report, key=lambda q: -q[3])[:3]))


if __name__ == '__main__':
    main()

"""The film's words on its final timeline, written out for whoever needs them (build/export/):

  subtitles.json            [{t0, t1, text}] both languages, one cue per line (srt.py's input; the same times as the picture)
  <slug>.srt                both languages, one block per line (what dist/ gets)
  <slug>.<lang>.srt / .vtt  one language
  script_timed.tsv          one row per line: id, node, start, end, the time it has before the next line starts (a voice must fit
                            in it), the time reading it needs, and the text in every language: the sheet for voice work

Times are the compiled ones (pipeline/compile.py): a line's start never moves without a recompile, and the exports are rewritten
with it."""
import json, os


def _ts(s, sep=','):
    ms = int(round(max(0.0, s) * 1000))   # round once, then split (1.9996 -> 00:00:02,000)
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{sep}{ms % 1000:03d}'


def write(out_dir, slug, cues, langs, read_time, end_t):
    """cues: the film's [{id, node, t0, t1, a, b}] (a, b: the first and second language); read_time(text) -> seconds"""
    os.makedirs(out_dir, exist_ok=True)
    cs = sorted(cues, key=lambda c: c['t0'])
    texts = lambda c: [c.get('a'), c.get('b')][:len(langs)]
    json.dump([{'t0': c['t0'], 't1': c['t1'], 'text': '\n'.join(t for t in texts(c) if t)} for c in cs],
              open(os.path.join(out_dir, 'subtitles.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    def srt(path, pick):
        blocks = [f'{k}\n{_ts(c["t0"])} --> {_ts(c["t1"])}\n{pick(c)}\n' for k, c in enumerate(cs, 1)]
        open(path, 'w', encoding='utf-8').write('\n'.join(blocks))
    def vtt(path, pick):
        blocks = [f'{c["id"]}\n{_ts(c["t0"], ".")} --> {_ts(c["t1"], ".")}\n{pick(c)}\n' for c in cs]
        open(path, 'w', encoding='utf-8').write('WEBVTT\n\n' + '\n'.join(blocks))
    srt(os.path.join(out_dir, f'{slug}.srt'), lambda c: '\n'.join(t for t in texts(c) if t))
    for i, lg in enumerate(langs):
        pick = lambda c, i=i: texts(c)[i] or ''
        srt(os.path.join(out_dir, f'{slug}.{lg}.srt'), pick); vtt(os.path.join(out_dir, f'{slug}.{lg}.vtt'), pick)
    rows = ['\t'.join(['id', 'node', 'start', 'end', 'room', 'reading'] + langs)]
    for k, c in enumerate(cs):
        room = (cs[k + 1]['t0'] if k + 1 < len(cs) else end_t) - c['t0']
        rows.append('\t'.join([c['id'], c.get('node') or '', f'{c["t0"]:.3f}', f'{c["t1"]:.3f}', f'{room:.2f}', f'{max(read_time(t) for t in texts(c) if t):.2f}']
                              + [(t or '').replace('\t', ' ') for t in texts(c)]))
    open(os.path.join(out_dir, 'script_timed.tsv'), 'w', encoding='utf-8').write('\n'.join(rows) + '\n')

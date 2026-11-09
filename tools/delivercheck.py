"""The finished film's own numbers, measured on the delivered file (docs/DELIVER.md): what it is (length, picture, sound, size),
its brightness minute by minute and its darkest 60 s against docs/CHECKS.md "Brightness", black frames, loudness and true peak,
and any metadata a delivered file must not carry. One pass over the film.
    python -I tools/delivercheck.py <film.mp4> [--closing <s>] [--json <out.json>]
--closing: where a deliberately dark ending begins (the closing night city): the minute flags leave it out, and say so.
Exit 1 when a flag is up: the whole film's mean YAVG under 80, a minute under 60 (or a 60 s stretch: where), loudness off
-14 LUFS by more than 1 LU, true peak over -1 dBTP, or metadata (an encoder, a title, a date, chapters)."""
import argparse, json, os, re, subprocess, sys, tempfile

WHOLE_MIN, MINUTE_MIN, LUFS, LU_TOL, TP_MAX = 80.0, 60.0, -14.0, 1.0, -1.0
KEEP_TAGS = {'major_brand', 'minor_version', 'compatible_brands', 'language', 'handler_name', 'vendor_id'}   # the container's own structure
STRINGS = (b'x264', b'Lavf', b'Lavc', b'HandBrake', b'libx265', b'encoder')


def probe(f):
    return json.loads(subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', '-show_chapters', f],
                                     capture_output=True, check=True, text=True).stdout)


def main():
    ap = argparse.ArgumentParser(description="the finished film's own numbers")
    ap.add_argument('film'); ap.add_argument('--closing', type=float); ap.add_argument('--json')
    A = ap.parse_args()
    P = probe(A.film); fmt = P['format']; dur = float(fmt['duration'])
    vs = next(s for s in P['streams'] if s['codec_type'] == 'video'); au = next((s for s in P['streams'] if s['codec_type'] == 'audio'), None)
    flags, R = [], {'file': os.path.abspath(A.film), 'seconds': round(dur, 3), 'bytes': int(fmt['size']),
                    'video': f"{vs['codec_name']} {vs['width']}x{vs['height']} {vs.get('avg_frame_rate')}", 'frames': int(vs.get('nb_frames') or 0),
                    'audio': f"{au['codec_name']} {au.get('sample_rate')} Hz {au.get('channels')} ch" if au else None}
    # one pass: black frames on every frame, brightness twice a second at 640 wide (CHECKS.md), loudness on the sound
    with tempfile.NamedTemporaryFile('w+', suffix='.txt') as st:
        fc = f"[0:v]blackdetect=d=0.1:pix_th=0.10,fps=2,scale=640:-2,signalstats,metadata=mode=print:file={st.name}[v]" + (';[0:a]ebur128=peak=true[a]' if au else '')
        cmd = ['nice', '-n', '10', 'ffmpeg', '-hide_banner', '-nostats', '-i', A.film, '-filter_complex', fc, '-map', '[v]'] + (['-map', '[a]'] if au else []) + ['-f', 'null', '-']
        err = subprocess.run(cmd, capture_output=True, text=True).stderr
        st.seek(0); yt = []; t = None
        for ln in st:
            m = re.search(r'pts_time:([\d.]+)', ln)
            if m: t = float(m.group(1))
            m = re.search(r'lavfi\.signalstats\.YAVG=([\d.]+)', ln)
            if m and t is not None: yt.append((t, float(m.group(1))))
    # brightness
    ys = [y for _, y in yt]; whole = sum(ys) / len(ys) if ys else 0
    end = A.closing if A.closing is not None else dur
    mins = []
    for k in range(int(dur // 60) + 1):
        v = [y for t, y in yt if k * 60 <= t < (k + 1) * 60]
        if v: mins.append({'from': k * 60, 'to': min((k + 1) * 60, round(dur, 3)), 'yavg': round(sum(v) / len(v), 2), 'closing': (k + 1) * 60 > end})
    roll = []   # the darkest 60 s stretches before the closing, a half second apart
    for i in range(len(yt)):
        a = yt[i][0]
        if a + 60 > end: break
        v = [y for t, y in yt[i:i + 120] if t < a + 60]
        roll.append((sum(v) / len(v), a))
    low = sorted(roll)[:1]
    under = []   # the stretches whose 60 s mean is under the flag
    for y, a in sorted((r for r in roll if r[0] < MINUTE_MIN), key=lambda r: r[1]):
        if under and a <= under[-1]['to'] - 60 + .6: under[-1]['to'] = round(a + 60, 1); under[-1]['lowest'] = min(under[-1]['lowest'], round(y, 2))
        else: under.append({'from': round(a, 1), 'to': round(a + 60, 1), 'lowest': round(y, 2)})
    R['brightness'] = {'whole_yavg': round(whole, 2), 'minutes': mins, 'darkest_60s': {'from': round(low[0][1], 1), 'yavg': round(low[0][0], 2)} if low else None,
                       'under_60_stretches': under, 'closing_from': A.closing}
    if whole < WHOLE_MIN: flags.append(f'whole-film brightness YAVG {whole:.1f} < {WHOLE_MIN:.0f}: look at it as CHECKS.md "Brightness" says (the phone look)')
    for m_ in mins:
        if m_['yavg'] < MINUTE_MIN and not m_['closing']: flags.append(f"minute {m_['from']}-{m_['to']} s YAVG {m_['yavg']} < {MINUTE_MIN:.0f}")
    for u in under: flags.append(f"60 s from {u['from']} to {u['to']} s under {MINUTE_MIN:.0f} (lowest {u['lowest']}): a deliberate dark stretch whose subject reads, or too dark")
    # black frames
    R['black'] = [{'from': float(a), 'to': float(b)} for a, b in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', err)]
    # loudness (the summary ebur128 prints at the end)
    if au:
        I = re.findall(r'I:\s+(-?[\d.]+) LUFS', err); LRA = re.findall(r'LRA:\s+([\d.]+) LU', err); TP = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', err)
        R['loudness'] = {'lufs': float(I[-1]) if I else None, 'lra': float(LRA[-1]) if LRA else None, 'true_peak_dbtp': float(TP[-1]) if TP else None}
        if I and abs(float(I[-1]) - LUFS) > LU_TOL: flags.append(f'loudness {I[-1]} LUFS, not {LUFS:.0f} within {LU_TOL:.0f} LU (render/mux.mjs normalises: was the mix muxed again?)')
        if TP and float(TP[-1]) > TP_MAX: flags.append(f'true peak {TP[-1]} dBTP over {TP_MAX:.0f}')
    # metadata
    tags = {**{f'format:{k}': v for k, v in (fmt.get('tags') or {}).items()}, **{f"stream{s['index']}:{k}": v for s in P['streams'] for k, v in (s.get('tags') or {}).items()}}
    extra = {k: v for k, v in tags.items() if k.split(':', 1)[1] not in KEEP_TAGS}
    with open(A.film, 'rb') as fh:
        head = fh.read(4 << 20); fh.seek(max(0, R['bytes'] - (4 << 20))); tail = fh.read()
    found = sorted({s.decode() for s in STRINGS if s in head or s in tail})
    R['metadata'] = {'tags': extra, 'chapters': len(P.get('chapters') or []), 'strings': found}
    if extra: flags.append(f'metadata tags {sorted(extra)}')
    if P.get('chapters'): flags.append(f"{len(P['chapters'])} chapters in the file")
    if found: flags.append(f'encoder strings in the file: {found}')
    R['flags'] = flags
    # report
    print(f"{R['file']}\n  {R['seconds']} s, {R['bytes'] / 1e9:.2f} GB, {R['video']}, {R['frames']} frames; {R['audio']}")
    b = R['brightness']
    print(f"  brightness: whole YAVG {b['whole_yavg']}; darkest 60 s from {b['darkest_60s']['from'] if b['darkest_60s'] else '-'} s "
          f"({b['darkest_60s']['yavg'] if b['darkest_60s'] else '-'}); minutes " + ' '.join(f"{m_['from']}:{m_['yavg']:.0f}{'*' if m_['closing'] else ''}" for m_ in mins))
    print(f"  black: " + (', '.join(f"{x['from']:.2f}-{x['to']:.2f} s" for x in R['black']) or 'none'))
    if au: print(f"  loudness: {R['loudness']['lufs']} LUFS, LRA {R['loudness']['lra']} LU, true peak {R['loudness']['true_peak_dbtp']} dBTP")
    print(f"  metadata: {len(extra)} tags beyond the container's own, {R['metadata']['chapters']} chapters, strings {found or 'none'}")
    print('  flags:' + (''.join(f'\n    {f}' for f in flags) if flags else ' none'))
    if A.json: json.dump(R, open(A.json, 'w'), indent=1)
    sys.exit(1 if flags else 0)


if __name__ == '__main__':
    main()

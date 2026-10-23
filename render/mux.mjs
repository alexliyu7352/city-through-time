// The delivered film: node render/mux.mjs <video.mp4> <mix.wav> <out.mp4> [--fps 24] [--grain 2]
// (adapted from lemo-opuscar core/render/mux.sh, MIT; see NOTICE). The picture is encoded at the target rate (held stretches get
// copied frames) with film grain (--grain 0: none); the audio gets a two-pass loudnorm to -14 LUFS / true peak -1.2 dB (one pass
// misses by about 0.5 LU) and silence to the picture's length when it is shorter (a longer one is cut to the picture).
// Nothing about the tools goes out (SKILL.md 交付): no tags or chapters, no encoder strings in the container, x264's settings SEI
// removed from the stream, AAC written bitexact.
// The audio must decode whole, or nothing is written: no audio stream, decoder errors, or fewer seconds decoded than the file
// claims stop the mux (a WAV streamed with `ffmpeg ... -f wav -` has a placeholder length: its three known notes are let through).
// Silent audio (below -70 LUFS, which loudnorm cannot measure) skips the normalisation with a warning. At the end the film's
// loudness is measured and a miss (outside -14 +-1 LU, or a peak above -1 dB) is warned about.
import fs from 'fs'; import { spawnSync } from 'child_process';

const args = process.argv.slice(2), take = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : d; };
const FPS = +take('--fps', 24), GR = +take('--grain', 2), [V, A, O] = args;
const die = m => { console.error('mux: ' + m); process.exit(1); };
if (!V || !A || !O) die('usage: node render/mux.mjs video.mp4 mix.wav out.mp4 [--fps 24] [--grain 2]');
for (const f of [V, A]) if (!fs.existsSync(f)) die(`not found: ${f}`);
if (!(FPS > 0) || !(GR >= 0)) die('--fps must be a number above 0, --grain 0 or more');
const run = (cmd, a) => { const r = spawnSync(cmd, a, { encoding: 'utf8', maxBuffer: 1 << 28 }); if (r.error) die(`${cmd}: ${r.error.code === 'ENOENT' ? 'not installed (or not on PATH)' : r.error.message}`); return r; };
const dur = f => parseFloat(run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).stdout);

// pass 1: measure, decoding the whole file
if (!run('ffprobe', ['-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', A]).stdout.trim()) die(`no audio stream in ${A}`);
const LN = 'loudnorm=I=-14:TP=-1.2:LRA=11';
const m = run('ffmpeg', ['-hide_banner', '-nostats', '-progress', 'pipe:2', '-i', A, '-af', `${LN}:print_format=json`, '-f', 'null', '-']);
if (m.status) die(`ffmpeg cannot read the audio ${A}: ${m.stderr.trim().split('\n').slice(-2).join(' ')}`);
const errs = m.stderr.split('\n').filter(l => l.startsWith('[') && /error|invalid|corrupt|header missing|overread|truncat|incomplete/i.test(l));
const bad = errs.filter(l => !/Ignoring maximum wav data size|Packet corrupt \(stream = \d+, dts = NOPTS\)|corrupt input packet in stream \d+/.test(l));
if (bad.length) die(`the audio ${A} is damaged; ffmpeg reported while decoding it:\n${bad.slice(0, 2).join('\n')}`);
const ot = [...m.stderr.matchAll(/^out_time=(\d+):(\d+):([\d.]+)$/gm)].pop(), dec = ot ? +ot[1] * 3600 + +ot[2] * 60 + +ot[3] : 0, claim = dur(A);
if (!/Estimating duration from bitrate/.test(m.stderr) && claim - dec > Math.max(.15, claim * .05)) die(`only ${dec.toFixed(2)} s of the ${claim} s that ${A} claims could be decoded: the file is damaged or cut off`);
if (errs.length) console.error(`mux: note: ffmpeg complained about the header or ending of ${A} (typical of a streamed WAV), but all ${dec.toFixed(2)} s decoded; continuing`);
const J = JSON.parse(m.stderr.slice(m.stderr.lastIndexOf('{'), m.stderr.lastIndexOf('}') + 1));
const K = ['input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset'], norm = K.every(k => J[k] != null && !/inf|nan/i.test(J[k]));
const AF = norm ? `${LN}:measured_I=${J.input_i}:measured_TP=${J.input_tp}:measured_LRA=${J.input_lra}:measured_thresh=${J.input_thresh}:offset=${J.target_offset}:linear=true` : 'anull';
if (!norm) console.error('mux: warning: the audio is silent or quieter than -70 LUFS, so loudness normalisation was skipped');

// pass 2: the film
const VD = dur(V), AD = dur(A);
let pad = '';
// (apad needs a named channel layout; a WAV from soundfile has none, and ffmpeg then refuses the graph: named here, samples unchanged)
if (AD > 0 && VD > 0 && AD < VD - 0.02) { pad = `,aformat=channel_layouts=stereo|mono,apad=whole_dur=${VD}`; console.error(`mux: note: the audio (${AD} s) is shorter than the video (${VD} s); padding it with silence`); }
const VF = (GR ? `fps=${FPS},noise=c0s=${GR}:allf=t` : `fps=${FPS}`) + ',format=yuv420p';
const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', V, '-i', A, '-filter_complex', `[0:v]${VF}[v];[1:a]${AF},aresample=48000${pad}[a]`,
  '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-r', String(FPS), '-bsf:v', 'filter_units=remove_types=6',
  '-c:a', 'aac', '-b:a', '256k', '-flags:a', '+bitexact', '-map_metadata', '-1', '-map_chapters', '-1', '-fflags', '+bitexact',
  '-movflags', '+faststart', '-shortest', O], { stdio: ['ignore', 'inherit', 'inherit'] });
if (r.status !== 0 || !fs.existsSync(O) || !fs.statSync(O).size) { fs.rmSync(O, { force: true }); die(`ffmpeg failed while writing ${O} (its message is above)`); }
console.log(O);
const R = run('ffmpeg', ['-hide_banner', '-nostats', '-i', O, '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr.split('\n').filter(l => /^\s+(I|LRA|Peak):/.test(l)).slice(0, 3);
console.log(R.join('\n'));
if (norm) {
  const I = parseFloat((R.find(l => /^\s+I:/.test(l)) || '').split(/\s+/)[2]), P = parseFloat((R.find(l => /^\s+Peak:/.test(l)) || '').split(/\s+/)[2]);
  if (I < -15 || I > -13 || P > -1) console.error(`mux: warning: the film missed the target (-14 LUFS, true peak <= -1.2 dB): measured ${I} LUFS, peak ${P} dB. The mix is probably clipping or has very hot peaks: lower it and tame the peaks, then mux again`);
}

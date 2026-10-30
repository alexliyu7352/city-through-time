"""A city's web bundle: what play.html needs to play the film in a browser, from another server (docs/PUBLISH.md).
usage: python -I tools/web.py cities/<slug>            -> cities/<slug>/dist/web/ (+ bundle.json: every file, its size and SHA-256;
                                                       poster.jpg 1280 wide and poster_thumb.webp 640 wide, for the entry page)
       python -I tools/web.py cities/<slug> --entry    a draft of cities/<slug>/entry.json (the entry page lists the city from it:
                                                       tools/registry.mjs), from the film: where it is, its years, length,
                                                       languages and chapters; fill in the rest (CONTRIBUTING.zh-Hant.md)
Upload the folder as it is (a Hugging Face dataset, a GitHub repository served by GitHub Pages, any host that allows cross-origin
reads) and give its URL as the city's `bundle` in cities.json; the page then plays play.html?city=<slug>&bundle=<url>.
Only what the page loads goes in (engine/main.js: the timeline, the model and its masks, the era cities, the decals and plates, the
pools' and grounds' maps, the narration, score and sound-effect tracks as m4a, the footage and pictures; museum.html: the museum pages,
tools/museum.py), laid out as in the city folder: build/... and assets/.... It stops when film.json names a file of the build that is
not in that list (the page would stop on it).
Nothing else does: no WAV, no internal test plates (satellite_hr), no reference pictures. The footage is re-encoded for streaming. The fonts are not in it: the page loads
them from the project's fonts/ (a city that uses a new font brings it to fonts/ in its pull request)."""
import hashlib, json, os, shutil, subprocess, sys


def files(D):
    """the page's loads, relative to the city folder (engine/main.js)"""
    B = os.path.join(D, 'build')
    F = json.load(open(os.path.join(B, 'film.json'), encoding='utf-8'))
    out = ['build/film.json'] + [f'build/data/{n}' for n in ('model.json', 'stats.json', 'lines.json', 'water.png', 'layers1.png', 'layers2.png',
                                                              'layers3.png', 'hide.png', 'hide2.png', 'edge.png', 'edge2.png', 'locator.png')]
    out.append('build/data/terrain16.png' if os.path.exists(os.path.join(B, 'data', 'terrain16.png')) else 'build/data/terrain.png')
    built = [d.get('file') for d in F.get('decals') or []] + [(F.get('satellite') or {}).get('file'), (F.get('context') or {}).get('file'),
             (F.get('grow') or {}).get('tfile')] + [e.get('file') for e in F.get('eras') or []]
    built += [(F.get(k) or {}).get('file') for k in ('voice', 'score', 'sfx', 'basinMap', 'groundMap')] + [(F.get('score') or {}).get('loop')]
    out += ['build/' + f for f in built if f]
    out += [f['file'] for f in F.get('footage') or []]   # (relative to the city folder: assets/...)
    out += [v['file'] for v in F.get('living') or []]   # living moments' pictures (assets/living/)
    M = os.path.join(B, 'museum')   # museum pages (tools/museum.py): what museum.html and the viewer's public mode load
    if os.path.exists(os.path.join(M, 'index.json')):
        out += ['build/museum/index.json'] + (['build/museum/plate.json'] if os.path.exists(os.path.join(M, 'plate.json')) else [])
        for e in json.load(open(os.path.join(M, 'index.json'), encoding='utf-8')):
            P = json.load(open(os.path.join(M, e['id'] + '.json'), encoding='utf-8'))
            out += [f'build/museum/{e["id"]}.json', P['model']] + [v['picture']['file'] for v in P['viewpoints'] if v.get('picture')]
            out += [q['file'] for q in (P.get('life') or {}).get('pictures') or []] + ([P['life']['photo']['file']] if (P.get('life') or {}).get('photo') else [])
    # every file of the build that film.json names (a `file` or `tfile`, at any depth) must be in: the page loads it by that name, and
    # a texture added to the film but not to this list left the bundle's player stopped on a missing file
    def named(o):
        if isinstance(o, dict):
            for k, v in o.items(): yield from ([v] if k in ('file', 'tfile') and isinstance(v, str) else named(v))
        elif isinstance(o, list):
            for v in o: yield from named(v)
    left = sorted({'build/' + f for f in named(F) if os.path.isfile(os.path.join(B, f))} - set(out))
    if left: raise SystemExit(f'web: film.json names {", ".join(left)}, which the bundle would leave out: add it to files() in tools/web.py (the page loads it)')
    return list(dict.fromkeys(out))


def entry(D):
    """the city's cities.json entry as far as the film can tell it (CONTRIBUTING.md has every field)"""
    import yaml
    C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'))
    F = json.load(open(os.path.join(D, 'build', 'film.json'), encoding='utf-8'))
    w, s_, e, n = C['box']; nodes = F['nodes']; slug = os.path.basename(D)
    return {'slug': slug, 'name': {'en': C['name'].get('en', slug), 'zh-Hans': C['name'].get('zh', '')},
            'location': [round((w + e) / 2, 3), round((s_ + n) / 2, 3)],
            'years': [int(nodes[0]['years'][0]), int(nodes[-1]['years'][1])], 'duration': round(F['dur'], 1),
            'narration': (F.get('voice') or {}).get('lang'), 'subtitles': C['film'].get('lang', []),
            'chapters': [{'t': round(x['t0'], 1), 'year': int(x['years'][0]), 'color': x.get('col', '#ffffff')} for x in nodes],
            'authors': [{'name': '', 'url': ''}], 'summary': {'en': ''},
            'poster': '<bundle url>poster.jpg', 'thumb': '<bundle url>poster_thumb.webp', 'watch': [], 'bundle': None, 'download': None,
            'ai': [], 'license': 'CC BY-SA 4.0', 'added': __import__('datetime').date.today().isoformat()}


def main():
    D = os.path.abspath(sys.argv[1]); out = os.path.join(D, 'dist', 'web')
    if '--entry' in sys.argv:
        f = os.path.join(D, 'entry.json'), json.dumps(entry(D), ensure_ascii=False, indent=2) + '\n'
        if os.path.exists(f[0]): return print(f[1] + f'(cities/{os.path.basename(D)}/entry.json exists: the draft above was not written)')
        open(f[0], 'w', encoding='utf-8').write(f[1]); return print(f'wrote cities/{os.path.basename(D)}/entry.json: fill in the names, summary, authors, poster and links')
    fs = files(D)
    missing = [f for f in fs if not os.path.exists(os.path.join(D, f))]
    if missing: raise SystemExit('web: missing (compile, then render/events.mjs and the music first): ' + ', '.join(missing))
    if os.path.isdir(out): shutil.rmtree(out)
    man = []
    for f in fs:
        dst = os.path.join(out, f); os.makedirs(os.path.dirname(dst), exist_ok=True)
        if f.endswith('.mp4'):   # footage: cut every frame a keyframe for the renders (make.sh); for the web, a keyframe a second, about a tenth the size
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(D, f), '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '26', '-g', '24',
                            '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-map_metadata', '-1', dst], check=True)
        else: shutil.copy2(os.path.join(D, f), dst)
        h = hashlib.sha256(open(dst, 'rb').read()).hexdigest()
        man.append({'path': f, 'bytes': os.path.getsize(dst), 'sha256': h})
    poster = os.path.join(D, 'dist', 'poster.jpg')   # (the entry page shows these: entry.json poster and thumb)
    if os.path.exists(poster):
        for name, w, args in (('poster.jpg', 1280, ['-q:v', '3', '-fflags', '+bitexact', '-flags:v', '+bitexact']), ('poster_thumb.webp', 640, ['-c:v', 'libwebp', '-quality', '80'])):
            dst = os.path.join(out, name)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', poster, '-vf', f'scale={w}:-2', '-map_metadata', '-1', *args, dst], check=True)
            man.append({'path': name, 'bytes': os.path.getsize(dst), 'sha256': hashlib.sha256(open(dst, 'rb').read()).hexdigest()})
    total = sum(m['bytes'] for m in man)
    json.dump({'slug': os.path.basename(D), 'files': man, 'bytes': total}, open(os.path.join(out, 'bundle.json'), 'w', encoding='utf-8'), indent=1)
    print(f'web bundle: {len(man)} files, {total / 1e6:.0f} MB -> {os.path.relpath(out)}')
    for m in sorted(man, key=lambda m: -m['bytes'])[:5]: print(f"  {m['bytes'] / 1e6:6.1f} MB  {m['path']}")


if __name__ == '__main__':
    main()

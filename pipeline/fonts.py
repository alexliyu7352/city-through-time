"""The fonts library: complete open-licence fonts kept in <root>/fonts/ (in git, with their licences), chosen per city by family
name in city.yaml (film.fonts, one font per job) and resolved by compile.

  python -I pipeline/fonts.py list <root>                    the families in fonts/, their weights and character counts
  python -I pipeline/fonts.py add <root> "<Family Name>"     fetch a family from github.com/google/fonts (ofl/ or apache/):
                                                             its variable font when it has one (all weights in one file),
                                                             else its upright static files; and its licence text

Complete fonts, not subsets: a subset holds only the characters the film used when it was made, and a character added to the
copy later is drawn in a system font (heavier, another shape: one subtitle line in two weights). compile checks that every
character of the copy is in the font that draws it (coverage), so a missing glyph stops the build instead of reaching the screen.
Only fonts whose licence allows redistribution (SIL OFL 1.1, Apache 2.0) go into fonts/: the folder is published with the project."""
import glob, json, os, re, sys, urllib.request

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
EXT = ('.ttf', '.otf', '.woff2', '.woff')


def index(root):
    """{family: [{file, wmin, wmax}]} for every font file in <root>/fonts (family and weights read from the font itself)"""
    from fontTools.ttLib import TTFont
    out = {}
    for f in sorted(glob.glob(os.path.join(root, 'fonts', '*'))):
        if not f.lower().endswith(EXT): continue
        t = TTFont(f, lazy=True)
        fam = t['name'].getDebugName(16) or t['name'].getBestFamilyName()
        ax = {a.axisTag: (a.minValue, a.maxValue) for a in t['fvar'].axes} if 'fvar' in t else {}
        w = ax.get('wght', (t['OS/2'].usWeightClass, t['OS/2'].usWeightClass))
        out.setdefault(fam, []).append({'file': os.path.basename(f), 'wmin': w[0], 'wmax': w[1]})
    return out


def find(idx, family, weight):
    """the face of `family` that holds `weight` -> {file, wmin, wmax}; SystemExit naming what is there when there is none"""
    if family not in idx:
        raise SystemExit(f'fonts: no {family!r} in fonts/ (have: {", ".join(sorted(idx))}); fetch it: python -I pipeline/fonts.py add . "{family}"')
    for f in idx[family]:
        if f['wmin'] <= weight <= f['wmax']: return f
    raise SystemExit(f'fonts: {family!r} has no weight {weight} in fonts/ (have: ' + ', '.join(f'{f["file"]} {f["wmin"]:.0f}-{f["wmax"]:.0f}' for f in idx[family]) + ')')


def missing(root, face, chars):
    """the characters of `chars` the face has no glyph for"""
    from fontTools.ttLib import TTFont
    cmap = TTFont(os.path.join(root, 'fonts', face['file']), lazy=True).getBestCmap()
    return sorted(c for c in set(chars) if ord(c) not in cmap)


def _get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=300).read()


def add(root, family):
    """fetch a family from github.com/google/fonts into <root>/fonts (once)"""
    slug = family.lower().replace(' ', '')
    for lic in ('ofl', 'apache'):
        try: listing = json.loads(_get(f'https://api.github.com/repos/google/fonts/contents/{lic}/{slug}'))
        except Exception: continue   # noqa: BLE001 (not under this licence directory)
        fonts_ = [x for x in listing if x['name'].endswith('.ttf') and 'Italic' not in x['name']]
        var = [x for x in fonts_ if '[' in x['name']]
        os.makedirs(os.path.join(root, 'fonts'), exist_ok=True)
        for x in (var or fonts_):
            dst = os.path.join(root, 'fonts', re.sub(r'\[[^]]*\]', '-VF', x['name']))   # (Inter[opsz,wght].ttf -> Inter-VF.ttf)
            if os.path.exists(dst): print('kept', os.path.basename(dst)); continue
            data = _get(x['download_url']); open(dst + '.part', 'wb').write(data); os.replace(dst + '.part', dst)
            print('fetched', os.path.basename(dst), len(data), 'bytes')
        lic_file = next((x for x in listing if x['name'] in ('OFL.txt', 'LICENSE.txt')), None)
        if lic_file:
            dst = os.path.join(root, 'fonts', f'{"OFL" if lic == "ofl" else "LICENSE"}-{slug}.txt')
            if not os.path.exists(dst): open(dst, 'wb').write(_get(lic_file['download_url']))
        return
    raise SystemExit(f'fonts: {family!r} is not in github.com/google/fonts (ofl/ or apache/): add the files by hand, with their licence, only if it allows redistribution')


if __name__ == '__main__':
    cmd, root = sys.argv[1], sys.argv[2]
    if cmd == 'add':
        add(root, sys.argv[3])
    elif cmd == 'list':
        from fontTools.ttLib import TTFont
        for fam, faces in index(root).items():
            for f in faces:
                n = len(TTFont(os.path.join(root, 'fonts', f['file']), lazy=True).getBestCmap())
                print(f'{fam:24s} {f["file"]:32s} weight {f["wmin"]:.0f}-{f["wmax"]:.0f}  {n} characters')
    else:
        sys.exit(__doc__)

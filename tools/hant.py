"""Traditional Chinese (Taiwan) for a city's museum pages and the walk-round view (docs/MUSEUM.md): every Simplified (zh) text of
cities/<slug>/museum/<page>.yaml, the city's name and its period cities' names (city.yaml) converted with OpenCC s2twp (Taiwan
characters, words and phrases) into cities/<slug>/museum/zh-Hant.yaml, a list of { zh, zh-Hant } for a person to read through.
A pair already there keeps its zh-Hant (a correction made by hand stays); a zh text no longer used is dropped. tools/museum.py takes
each zh-Hant from that file and stops when a zh text has none (it changed since this ran).

usage: uv run --with opencc python -I tools/hant.py cities/<slug>      (OpenCC is needed only here, not by the pages or the build)
"""
import os, sys

import yaml


def zh_texts(o, out):
    """every zh text in a page's mapping, in order"""
    if isinstance(o, dict):
        if isinstance(o.get('zh'), str) and o['zh'].strip(): out.append(o['zh'].strip())
        for v in o.values(): zh_texts(v, out)
    elif isinstance(o, list):
        for v in o: zh_texts(v, out)
    return out


def main():
    if len(sys.argv) != 2: sys.exit(__doc__)
    try: import opencc
    except ImportError: sys.exit('hant: no OpenCC here: run it as uv run --with opencc python -I tools/hant.py <city>')
    D = os.path.abspath(sys.argv[1]); M = os.path.join(D, 'museum'); f = os.path.join(M, 'zh-Hant.yaml')
    C = yaml.safe_load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'))
    texts = zh_texts([C.get('name')] + [n.get('label') for n in C['film']['nodes'] if n.get('city')], [])
    for p in sorted(os.listdir(M)):
        if p.endswith('.yaml') and p != 'zh-Hant.yaml': zh_texts(yaml.safe_load(open(os.path.join(M, p), encoding='utf-8')), texts)
    old = {e['zh']: e['zh-Hant'] for e in (yaml.safe_load(open(f, encoding='utf-8')) or [])} if os.path.exists(f) else {}
    cc = opencc.OpenCC('s2twp'); out, new = [], 0
    for s in dict.fromkeys(texts):
        if s not in old: new += 1
        out.append({'zh': s, 'zh-Hant': old.get(s) or cc.convert(s)})
    with open(f, 'w', encoding='utf-8') as w:
        w.write('# Traditional Chinese (Taiwan) for the museum pages and the walk-round view: tools/hant.py (OpenCC s2twp), read through by a person\n')
        yaml.safe_dump(out, w, allow_unicode=True, sort_keys=False, width=1000)
    print(f'{os.path.relpath(f)}: {len(out)} texts, {new} new (read them through), {len(set(old) - set(texts))} dropped')


if __name__ == '__main__':
    main()

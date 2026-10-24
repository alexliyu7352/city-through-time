"""Copy check: reads the compiled film (cues on the final timeline, and what the picture shows meanwhile) and says where words are
missing, where there are too many, and where they break the house style. Advice for whoever writes the script (a person or an
agent): it changes nothing, and silence the film means to keep is declared in script.yaml (quiet:). Thresholds: film.copy in
city.yaml (defaults below).

  add    a long silence while the picture brings something named (a pin, an area, a beam's label, a photo, the sky's names, a new
         stop) that no nearby line mentions; or a very long silence
  cut    a line too long for one reading, lines so close together that the picture has no room, a phrase said twice
  style  numbers not in digits 0-9: Chinese numerals (dates, years, measures, counts), full-width digits, any script's own digits
  check  a line about years after the year on the counter (later: true in script.yaml when meant)"""
import re
import i18n

DEFAULTS = {'max_zh': 22, 'gap_s': 8.0, 'long_gap_s': 15.0, 'mention_window_s': 12.0, 'dense_window_s': 20.0, 'dense_share': .9,
            'repeat_min': 3, 'repeat_window_s': 120.0, 'keep': ['十五五']}
CJK = r'[一-鿿]'
CN_DIGIT = '〇零一二三四五六七八九'
CN_NUM = CN_DIGIT + '十百千万两'
UNITS = '公里|平方公里|公顷|米|亩|号线|万户|万家|万人|万锭|枚纱锭'
COUNTERS = '[条條座个個处處次位名户戶家所间間栋棟幢层層道门門口棵株只隻头頭匹辆輛艘架部本卷件项項批片块塊种種类類届屆期岁歲倍]'
FUNC = '的了在是这那里一也就和与着把被从到'


def _cn_year(s):
    """'一九八三' -> 1983 (digit by digit), else None"""
    val = {'〇': 0, '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
    if not s or any(c not in val for c in s): return None
    return int(''.join(str(val[c]) for c in s))


def years_in(text):
    """the years AD a line names: 4-digit Arabic or Chinese-digit years (never ones after 前, BCE)"""
    out = []
    for m in re.finditer(r'(?<![前\d.,])(1\d{3}|20\d{2})(?![\d,])(?!\s*(?:多|余)?年(?:间|里|来|多|前(?!后)))', text): out.append(int(m.group(1)))   # (not a span: 2000多年里, 6000年前)
    for m in re.finditer(rf'(?<!前)([{CN_DIGIT}]{{4}})年', text):
        y = _cn_year(m.group(1))
        if y: out.append(y)
    return out


def native_digits(text):
    """digits other than 0-9: full-width, Arabic-Indic, Persian, Devanagari, Thai and every other script's own (Unicode Nd)"""
    import unicodedata
    return sorted({c for c in text if unicodedata.category(c) == 'Nd' and not ('0' <= c <= '9')})


def chinese_numerals(text, keep):
    """spans written in Chinese numerals where the house style wants Arabic: multi-digit runs (years, numbers), months and days,
    numbers with a unit of measure"""
    t = text
    for k in keep: t = t.replace(k, '□' * len(k))
    t = re.sub(r'(?<=[0-9.])[十百千万亿]', '□', t)   # (5万, 1.2亿: Arabic digits with a magnitude word are the house style)
    hits = [m.group(0) for m in re.finditer(rf'[{CN_DIGIT}]{{2,}}', t)]
    hits += [m.group(0) for m in re.finditer(r'(?:十[一二]?|[一二三四五六七八九])月', t)]
    hits += [m.group(0) for m in re.finditer(r'(?:[一二三]?十[一二三四五六七八九]?|[一二三四五六七八九])日', t)]
    hits += [m.group(0) for m in re.finditer(rf'[{CN_NUM}点]+(?:{UNITS})', t)]
    hits += [m.group(0) for m in re.finditer(rf'[{CN_NUM}]+号(?!线)', t)]   # numbered things: 6号宫殿, 1号线 (above)
    # counts: 四十一条, 九座, 二期, 两千四百年 (not 一 or 两 alone: 一座城 is the language's article, 两座城 its 'both'; not 几十座,
    # which is no number; not 百年 or 千年 without a digit; idioms and quotations: film.copy.keep)
    for m in re.finditer(rf'(?<![{CN_NUM}几数])([{CN_NUM}]+)({COUNTERS}|年)', t):
        run, what = m.groups()
        if run in ('一', '两') or (what == '年' and not (re.search('[十百千万]', run) and re.search('[一二三四五六七八九两]', run))): continue
        hits.append(m.group(0))
    return sorted(set(hits), key=lambda h: t.find(h))


def _year_at(yl, t):
    for (t0, y0), (t1, y1) in zip(yl, yl[1:]):
        if t0 <= t <= t1: return y0 + (y1 - y0) * (t - t0) / ((t1 - t0) or 1)
    return yl[-1][1] if yl else None


def _names_shown(film, a, b):
    """what the picture names between a and b: [(t, what, name)]"""
    out = []
    for p in film.get('pins', []):
        if a <= p['t0'] < b and p.get('text'): out.append((p['t0'], 'pin', p['text']))
    for f in film.get('footage', []):
        if a <= f['on'] < b: out.append((f['on'], 'photo' if f.get('mode') != 'full' else 'footage', f.get('title') or f.get('id')))
    for r in film.get('routes', []):
        if a <= r['on'] < b and r.get('a'): out.append((r['on'], 'beam', r['a']))
    sky = film.get('sky') or {}
    for g in sky.get('groups', []):
        if a <= g['on'] < b and g.get('a'): out.append((g['on'], 'sky', g['a']))
    for n in film.get('nodes', []):
        if a <= n['t0'] < b: out.append((n['t0'], 'stop', n.get('label') or n['id']))
    return sorted(out)


def _screen_texts(film):
    """[(t, what, text)]: the film's text on screen other than the subtitles"""
    out = [(p['t0'], 'pin', p.get(k)) for p in film.get('pins', []) for k in ('text', 'sub')]
    out += [(r.get('t0', r.get('on', 0)), 'readout', r.get(k)) for r in film.get('readouts', []) for k in ('label', 'note')]
    out += [(L.get('t0', 0), 'place name', L.get(k)) for L in film.get('labels', []) for k in ('a', 'b')]
    out += [(f['on'], 'caption', f.get(k)) for f in film.get('footage', []) for k in ('title', 'sub', 'kicker')]
    out += [(r['on'], 'beam label', r.get(k)) for r in film.get('routes', []) for k in ('a', 'b')]
    out += [((film.get('end') or {}).get('t', 0), 'end card', s) for s in [(film.get('end') or {}).get('title_a')] + list((film.get('end') or {}).get('lines', []))]
    return [(t, w, s) for t, w, s in out if s]


def _core(name):
    """the part of a name a line would say: '六号宫殿 · 高 11.3 米' -> '六号宫殿'"""
    return re.split(r'\s*[·（(]\s*', name)[0].strip()


def check(film, cfg=None, quiet=(), lang='zh'):
    """[(t, node, kind, message)] for the film's cues; quiet: [(t0, t1)] stretches meant to be silent; lang: the first language
    (its pack: the longest line, in its own units, and whether its numerals are Han)"""
    P = i18n.pack(lang)
    C = {**DEFAULTS, 'max_zh': P.get('max_line', 22), **(cfg or {})}
    han = P.get('numerals') == 'han'
    cues = sorted(film.get('cues', []), key=lambda c: c['t0'])
    yl = film.get('yearline') or []
    nodes = film.get('nodes', [])
    node_at = lambda t: next((n['id'] for n in nodes if n['t0'] <= t < n['t1']), '-')
    in_quiet = lambda a, b: any(q0 <= a + .5 and b - .5 <= q1 for q0, q1 in quiet)
    F = []
    # add: silences
    t_start = (film.get('light') or {}).get('lamp', 0.0); t_end = (film.get('end') or {}).get('t', film.get('dur', 0))
    marks = [(t_start, t_start)] + [(c['t0'], c['t1']) for c in cues] + [(t_end, t_end)]
    for (_, a), (b, _) in zip(marks, marks[1:]):
        if b - a < C['gap_s'] or in_quiet(a, b): continue
        said = ''.join(c['a'] for c in cues if a - C['mention_window_s'] <= c['t0'] <= b + C['mention_window_s'])
        shown = _names_shown(film, a, b)
        unsaid = [(t, k, nm) for t, k, nm in shown if k in ('pin', 'beam', 'sky') and _core(nm) and _core(nm) not in said]   # (photos and chapter titles carry their own captions)
        ctx = ('; meanwhile ' + '; '.join(f'{k} "{nm}" at {t:.0f} s' for t, k, nm in shown[:5])) if shown else ''
        if unsaid:
            F.append((a, node_at(a), 'add', f'{b - a:.0f} s without words while the picture names ' + '; '.join(f'{k} "{nm}" at {t:.0f} s' for t, k, nm in unsaid[:4]) + ', which no line near it says: a line could'))
        elif b - a >= C['long_gap_s']:
            F.append((a, node_at(a), 'add', f'{b - a:.0f} s without words ({a:.0f}-{b:.0f} s){ctx}: a line, or mark it quiet in script.yaml if the silence is meant'))
    # cut: long lines, crowding, repeats
    for c in cues:
        n = i18n.line_length(lang, c['a'])
        if C['max_zh'] and n > C['max_zh']: F.append((c['t0'], c.get('node') or '-', 'cut', f'{c["id"]}: {n} characters (at most {C["max_zh"]}): split it or say less — {c["a"]}'))
    read = i18n.reading_time
    i = 0
    while i < len(cues):
        w0 = cues[i]['t0']; grp = [c for c in cues[i:] if c['t0'] < w0 + C['dense_window_s']]
        share = sum(read(c['a']) for c in grp) / C['dense_window_s']
        if len(grp) >= 3 and share > C['dense_share']:
            F.append((w0, cues[i].get('node') or '-', 'cut', f'{len(grp)} lines in {C["dense_window_s"]:.0f} s from {w0:.0f} s (reading fills {share:.0%} of it): '
                      f'no room for the picture; drop or merge one ({", ".join(c["id"] for c in grp)})'))
            i += len(grp); continue
        i += 1
    names = {_core(p['text']) for p in film.get('pins', []) if p.get('text')} | {_core(L.get('a') or '') for L in film.get('labels', [])}   # (place names may recur; a stop's title said twice in the narration is a repeat)
    grams = {}
    for c in cues:
        s = c['a']
        for L in range(C['repeat_min'], 7):
            for k in range(len(s) - L + 1):
                g = s[k:k + L]
                if (re.fullmatch(f'{CJK}+', g) and not re.search(f'[{CN_NUM}年月日]', g) and not any(g in u or u in g for u in UNITS.split('|'))
                        and g[0] not in FUNC and g[-1] not in FUNC): grams.setdefault(g, []).append(c)   # (not numbers, dates, measures, or a phrase that begins or ends on a function word)
    topic = {g for g, cs in grams.items() if len({c['id'] for c in cs}) >= 4}
    done = set()
    for g in sorted(grams, key=len, reverse=True):
        cs = list({c['id']: c for c in grams[g]}.values())
        if len(cs) != 2 or g in topic: continue
        a_, b_ = cs
        named = any(g in nm for nm in names if nm)   # a place name may recur, but not in two lines running
        if abs(a_['t0'] - b_['t0']) > (30.0 if named else C['repeat_window_s']) or (a_['id'], b_['id']) in done: continue
        if any(g in x for x in done if isinstance(x, str)): continue
        done.add((a_['id'], b_['id'])); done.add(g)
        F.append((b_['t0'], b_.get('node') or '-', 'cut', f'"{g}" is said in {a_["id"]} ({a_["t0"]:.0f} s) and again in {b_["id"]} ({b_["t0"]:.0f} s)'))
    # style: numerals
    for c in cues:   # every language of the line: digits 0-9 only
        hits = (chinese_numerals(c['a'], C['keep']) if han else []) + [f'{d} ({c_})' for c_ in (c.get('a'), c.get('b')) if c_ for d in native_digits(c_)]
        if hits: F.append((c['t0'], c.get('node') or '-', 'style', f'{c["id"]}: digits 0-9 for {"、".join(hits)}'))
    for t, what, text in _screen_texts(film):   # and every other text on screen (city.yaml): pins, readouts, names, captions, the end card
        hits = (chinese_numerals(text, C['keep']) if han else []) + native_digits(text)
        if hits: F.append((t, node_at(t), 'style', f'{what} "{text}" (city.yaml): digits 0-9 for {"、".join(hits)}'))
    # check: later years
    ny = {n['id']: n.get('years') for n in nodes}
    for c in cues:   # (a stop's own years are its range: the counter runs through them; later means after the stop's last year)
        y_end = (ny.get(c.get('node')) or [None, _year_at(yl, c['t0'])])[1]
        later = [y for y in years_in(c['a']) if y_end is not None and y > y_end + .5]
        if later and not c.get('later'):
            F.append((c['t0'], c.get('node') or '-', 'check', f'{c["id"]}: speaks of {", ".join(map(str, later))}, after this stop\'s {y_end:.0f} (later: true in script.yaml if meant)'))
    return sorted(F)


def report(findings):
    """the report as text, by node"""
    out, last = [], None
    for t, node, kind, msg in findings:
        if node != last: out.append(f'\n[{node}]'); last = node
        out.append(f'  {t:6.1f} s  {kind:5s}  {msg}')
    return '\n'.join(out).lstrip('\n') + '\n'

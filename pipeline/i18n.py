"""Languages (docs/SCRIPT.md): the words the program itself puts on screen, per language, from i18n/<code>.yaml
(a language pack: its writing system, the longest subtitle line, its numerals, how a year is written and the shared words such as
today / footage / imagined). The city's own words (lines, place names, captions) are in its script.yaml and city.yaml, one text
per language of film.lang.

  pack(code)              the pack for a language code (zh, zh-Hant, en, ja, ko, fr, ...); SystemExit when there is none
  script_of(text)         'cjk' (Han, kana), 'hangul', 'latin' or 'other' for the bulk of a text
  reading_time(text)      seconds a viewer needs to read a text nobody says (pins, notes, title cards; all writing systems in it)
  speaking_time(code, t)  seconds a narrator takes to say a line in that language, before its voice is recorded (pack: speak)
  year(code, y, tick)     a year as the language writes it (y < 0: before the common era)

Reading speeds: Han and kana 4.5 characters a second, hangul 6 syllables, Latin and other alphabets 15 letters, plus 1.5 s, at
least 1.8 s (the Han and Latin figures are the ones the films were timed with; hangul measured per syllable block). A line of
narration is timed by its voice alone, and by speaking_time until the voice is recorded: a subtitle is read faster than it is
heard, so no subtitle holds a line. Writing systems this does not handle (right-to-left: Arabic, Hebrew) stop the build where a
text uses them."""
import os, re
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CJK = r'[\u3000-\u303F\u3040-\u30FF\u3400-\u9FFF\uF900-\uFAFF\uFF00-\uFFEF]'   # CJK punctuation, kana, Han, compatibility, full-width forms
HANGUL = r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]'
RTL = r'[\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF]'   # Hebrew, Arabic and their presentation forms
READ_CJK = r'[\u3000-\u9FFF\uF900-\uFAFF]'   # (what reading_time counts at 4.5 a second: CJK punctuation, kana, Han; full-width , ; : at 15
                                           # as the films were timed: do not widen it, or every Chinese film's timing moves)
READ_HANGUL = r'[\uAC00-\uD7AF\u1100-\u11FF]'
_PACKS = {}


def pack(code):
    if code not in _PACKS:
        p = os.path.join(ROOT, 'i18n', f'{code}.yaml')
        if not os.path.exists(p):
            have = sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, 'i18n')) if f.endswith('.yaml'))
            raise SystemExit(f'i18n: no language pack for {code!r} (i18n/{code}.yaml; there are: {", ".join(have)}): copy one and translate its words')
        P = yaml.safe_load(open(p, encoding='utf-8'))
        for k in ('script', 'year', 'words'):
            if k not in P: raise SystemExit(f'i18n/{code}.yaml: no {k}')
        _PACKS[code] = P
    return _PACKS[code]


def script_of(text):
    s = text or ''
    n = {'cjk': len(re.findall(CJK, s)), 'hangul': len(re.findall(HANGUL, s)), 'latin': len(re.findall(r'[A-Za-zÀ-ɏ]', s))}
    k = max(n, key=n.get)
    return k if n[k] else 'other'


def reading_time(text):
    s = text or ''
    if re.search(RTL, s): raise SystemExit(f'i18n: right-to-left text is not supported yet: {s[:40]}')
    cjk = len(re.findall(READ_CJK, s)); han = len(re.findall(READ_HANGUL, s))
    other = len(re.sub(rf'{READ_CJK}|{READ_HANGUL}|\s', '', s))
    return max(1.8, cjk / 4.5 + han / 6.0 + other / 15 + 1.5)


def speaking_time(code, text):
    """seconds a narrator takes to say text in this language: the pack's speak (Han and kana characters a second for cjk,
    syllables for hangul, words for alphabets), measured on recorded lines; a pack without it stops the build of a film voiced in it"""
    P = pack(code); r = P.get('speak'); s = text or ''
    if not r: raise SystemExit(f'i18n/{code}.yaml: no speak (how fast a narrator speaks {P.get("name", code)}): time a few recorded lines and add it')
    n = (len(re.findall(r'[\u3040-\u30FF\u3400-\u9FFF\uF900-\uFAFF]', s)) if P['script'] == 'cjk' else
         len(re.findall(r'[\uAC00-\uD7AF]', s)) if P['script'] == 'hangul' else len(s.split()))
    return n / float(r)


def year(code, y, tick=False):
    Y = pack(code)['year']; r = int(round(y))
    f = (Y.get('tick_bce', Y['bce']) if tick else Y['bce']) if r < 0 else (Y.get('tick_ce', Y['ce']) if tick else Y['ce'])
    return f.format(y=abs(r))


def word(code, key):
    w = pack(code)['words'].get(key)
    if w is None: raise SystemExit(f'i18n/{code}.yaml: no word {key!r}')
    return w


def line_length(code, text):
    """how long a subtitle line is in the units its pack's max_line counts (Han and kana, or hangul syllables); 0 for alphabets"""
    sc = pack(code)['script']
    if sc == 'cjk': return len(re.findall(r'[\u3040-\u30FF\u3400-\u9FFF\uF900-\uFAFF]', text or ''))   # (Han and kana; not punctuation)
    if sc == 'hangul': return len(re.findall(r'[\uAC00-\uD7AF]', text or ''))
    return 0


if __name__ == '__main__':   # a check of every pack and the year formats
    import sys
    for f in sorted(os.listdir(os.path.join(ROOT, 'i18n'))):
        if not f.endswith('.yaml'): continue
        c = f[:-5]; P = pack(c)
        print(f'{c:8s} {P["name"]:10s} {P["script"]:7s} {year(c, -350)!r:16s} {year(c, -350, True)!r:14s} {year(c, 1975)!r:8s} '
              f'{word(c, "today")} · {word(c, "imagined")} · {word(c, "chapter").format(n="04")}')
    sys.exit(0)

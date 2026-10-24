"""The film's words, apart from its pictures: cities/<slug>/script.yaml holds every line of narration (the subtitles, later the
voice), in the order shown; city.yaml holds none. One line:

  - { id: qin_capital, zh: "...", en: "...", with: "stage", later: false, note: "..." }

  id     stable name of the line (unique in the film): voice files, exports and anything on screen that follows a line use it
  with   the picture the line waits for (compile's schedule_lines): shot:<camera key shot>, pin:<id>, card:<footage id>,
         stage[:<name>] or node (the node's arrival); lead: seconds before it. Pictures can follow a line in turn (with: <line id>)
  t      seconds from the start of the node's picture (moves with every hold the camera planner inserts); the
         opening line counts from the film's start
         With neither, a line follows the one before as soon as it has been read, through any hold of the camera.
  <lang> the text in every language of film.lang (city.yaml), e.g. zh and en
  later  true when the line speaks of years after the node's own (the year counter shows the node's year): the copy check asks
         for it, so a line about later years is a decision, not an accident
  note   for whoever writes, translates or voices the line (not shown)

script.yaml:  langs: [zh, en]
              opening: [<line>]                 the film's first line, over the title
              nodes: { <node id>: [<line> or { pause: <seconds>, why: "..." }, ...] }   (a pause: a silence meant to be there)
              quiet: { <node id>: [[from, to, why], ...] }   stretches of a node meant to be silent (the copy check leaves them)

  python -I pipeline/script.py migrate cities/<slug>     move the cues out of city.yaml into script.yaml (once per older city)
  CT_SCRIPT=<draft.yaml> python -I pipeline/compile.py cities/<slug>   compile (and preview) a draft of the script, script.yaml untouched"""
import os, re, sys
import yaml


def load(city, langs, node_ids):
    """script.yaml -> {'opening': [line], 'nodes': {node id: [line]}, 'quiet': {...}}; SystemExit on a malformed script"""
    p = os.environ.get('CT_SCRIPT') or os.path.join(city, 'script.yaml')   # (CT_SCRIPT: compile a draft without touching script.yaml)
    if not os.path.exists(p): return None
    if os.environ.get('CT_SCRIPT'): print(f'  script: the draft {p}')
    S = yaml.safe_load(open(p, encoding='utf-8')) or {}
    bad = lambda m: SystemExit(f'script.yaml: {m}')
    seen = set(); nodes = S.get('nodes') or {}
    for nid in nodes:
        if nid not in node_ids: raise bad(f'node {nid!r} is not in city.yaml (nodes: {", ".join(node_ids)})')
    for where, lines in [('opening', S.get('opening') or [])] + [(f'node {k}', v or []) for k, v in nodes.items()]:
        for ln in lines:
            if 'pause' in ln:
                if not isinstance(ln['pause'], (int, float)) or ln['pause'] <= 0: raise bad(f'{where}: pause must be seconds > 0: {ln}')
                if not ln.get('why'): raise bad(f'{where}: a pause says why it is there (why: "..."): {ln}')
                continue
            if 'id' not in ln: raise bad(f'{where}: a line has no id: {ln}')
            if 'with' in ln and 't' in ln: raise bad(f'{where}: line {ln["id"]}: with or t, not both')
            if ln['id'] in seen: raise bad(f'{where}: the id {ln["id"]!r} is used twice')
            seen.add(ln['id'])
            if not re.fullmatch(r'[a-z0-9_]+', ln['id']): raise bad(f'{where}: id {ln["id"]!r}: use lower-case letters, digits and _ (it names files)')
            for lg in langs:
                if not ln.get(lg): raise bad(f'{where}: line {ln["id"]} has no {lg} text')
            if not isinstance(ln.get('t', 0), (int, float)): raise bad(f'{where}: line {ln["id"]}: t must be seconds')
    return {'opening': S.get('opening') or [], 'nodes': {k: v or [] for k, v in nodes.items()}, 'quiet': S.get('quiet') or {}}


def _flow(d):
    """one line as YAML flow mapping, keys in a fixed order, strings quoted"""
    keys = ['id', 't'] + [k for k in d if k not in ('id', 't', 'note')] + (['note'] if 'note' in d else [])
    q = lambda v: v if isinstance(v, (int, float)) and not isinstance(v, bool) else ('true' if v is True else 'false' if v is False else '"' + str(v).replace('\\', '\\\\').replace('"', '\\"') + '"')
    return '{ ' + ', '.join(f'{k}: {q(d[k])}' for k in keys) + ' }'


def migrate(city):
    """move the cues of city.yaml (film.opening.cue, nodes[].cues) into script.yaml; ids <node>_<n>"""
    cy = os.path.join(city, 'city.yaml'); sp = os.path.join(city, 'script.yaml')
    if os.path.exists(sp): raise SystemExit(f'{sp} exists: nothing to migrate')
    text = open(cy, encoding='utf-8').read(); C = yaml.safe_load(text); FM = C['film']
    langs = FM.get('lang', ['zh', 'en'])
    out = [f'# The film\'s narration: every line, in the order shown (pipeline/script.py). Pictures are in city.yaml.',
           f'langs: [{", ".join(langs)}]', '']
    op = (FM.get('opening') or {}).get('cue')
    if op: out += ['opening:', f'  - {_flow({"id": "opening", **op})}', '']
    out.append('nodes:')
    for nd in FM['nodes']:
        cs = nd.get('cues') or []
        if not cs: continue
        out.append(f'  {nd["id"]}:')
        for k, c in enumerate(cs, 1): out.append(f'    - {_flow({"id": f"{nd['id']}_{k}", **c})}')
    open(sp, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    # city.yaml without them: the cue blocks (a `cues:` key and the lines indented under it) and the opening `cue:` line
    lines, keep, i = text.split('\n'), [], 0
    while i < len(lines):
        m = re.match(r'^(\s*)cues:\s*(\[.*\])?\s*(#.*)?$', lines[i])
        if m:
            ind = len(m.group(1)); i += 1
            if m.group(2) is None:
                while i < len(lines) and (lines[i].strip() == '' or len(lines[i]) - len(lines[i].lstrip()) > ind): i += 1
            continue
        if re.match(r'^\s*cue:\s*\{', lines[i]) and op: i += 1; continue
        keep.append(lines[i]); i += 1
    open(cy, 'w', encoding='utf-8').write('\n'.join(keep))
    n = sum(len(nd.get('cues') or []) for nd in FM['nodes']) + (1 if op else 0)
    print(f'{n} lines -> {sp}; city.yaml keeps the pictures')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'migrate': migrate(sys.argv[2])
    else: sys.exit(__doc__)

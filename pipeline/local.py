"""This machine's paths and settings: local/config.json (not in git). Every machine lays its disks out its own way, so nothing
here is fixed in code: the file is written at first use from templates/local.json, after asking the user (docs/SETUP.md).

local/                       this machine (in .gitignore); by default everything heavy sits here, in one place
  config.json                the keys below; a relative path is from the project root, an absolute one is used as is, ~ expands
  raw/                       raw: downloaded data: shared by cities (ghsl/, tiles/, cmab/<province>/, naturalearth/; city.yaml raw.cmab is
                             relative to it), and each city's own in cities/<slug>/ (osm/, overture/: pipeline/layout.py raw)
  ref/                       ref: originals of footage and photos as downloaded (a city's assets/footage/make.sh cuts its clips from them)
  models/                    stable_audio: the Stable Audio 3 clone (tools/music.py); hf_cache: its weights (HF_HUB_CACHE)
  instruments/               instruments: the sample libraries of the code score

chrome  a Chrome binary for rendering when Playwright's own headless shell will not install ("" = Playwright's own)
workers how many pages render at once
cloudflare  (optional, not in the template) the user's own site on Cloudflare Pages, tools/deploy.mjs: {"api_token", "account_id",
            "project"}; the environment's CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID come first (docs/PUBLISH.md)

The file is read only when a key is asked for: scripts that need no path run without it.
usage from a shell: python -I pipeline/local.py <key>      prints the value (a path key resolved)"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, 'local', 'config.json')
PATHS = ('raw', 'ref', 'stable_audio', 'hf_cache', 'instruments')
_cfg = None


def get(key):
    global _cfg
    if _cfg is None:
        if not os.path.exists(FILE):
            raise SystemExit(f'no local/config.json: copy templates/local.json there and set this machine\'s paths (docs/SETUP.md)')
        _cfg = json.load(open(FILE, encoding='utf-8'))
    if key not in _cfg: raise SystemExit(f'local/config.json has no "{key}" (templates/local.json lists every key)')
    return _cfg[key]


def path(key, *p):
    return os.path.normpath(os.path.join(ROOT, os.path.expanduser(get(key)), *p))


def raw(*p): return path('raw', *p)


if __name__ == '__main__':
    k = sys.argv[1]
    print(path(k) if k in PATHS else get(k))

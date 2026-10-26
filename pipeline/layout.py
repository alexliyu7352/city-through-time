"""Where a city's files live: one place, every script asks here (the engine and the node tools follow the same layout).

cities/<slug>/                   what a person writes or brings (in git)
  city.yaml                      the film: nodes, camera, areas, fonts ...
  FACTS.md  CREDITS  research/   sources and credits
  assets/                        photos and footage the film shows
  build/                         everything made from them (not in git; rebuild with tools/build.mjs)
    film.json  events.json       the compiled timeline, and every event the page fires on it (sound)
    data/                        model, masks, terrain, imagery, era cities: fetched or computed (slow to remake: keep)
    logs/                        prep log, the stage plan, checks (clipcheck, camcheck, readcheck)
    export/                      subtitles and other timed exports
    audio/                       the mix and its stems
    video/                       the picture alone, before the mix is laid on
    review/                      stills and contact sheets made while reviewing
  dist/                          what is delivered: <slug>.mp4, <slug>.srt, poster.jpg (not in git)

<raw root>/cities/<slug>/        the city's own downloads, on this machine (pipeline/local.py; not in git): osm/, overture/
"""
import os


def build(city, *p): return os.path.join(city, 'build', *p)
def data(city, *p): return build(city, 'data', *p)
def logs(city, *p): return build(city, 'logs', *p)
def export(city, *p): return build(city, 'export', *p)
def audio(city, *p): return build(city, 'audio', *p)
def video(city, *p): return build(city, 'video', *p)
def review(city, *p): return build(city, 'review', *p)
def dist(city, *p): return os.path.join(city, 'dist', *p)


def raw(city, *p):
    """the city's own downloads (its OSM answers, its Overture footprints): <raw root>/cities/<slug>/. Data that serves many
    cities (GHSL tiles, CMAB provinces, imagery tiles, Natural Earth) stays shared under the raw root, and a reader takes from it
    only what covers the city's box, never a file chosen by its place in a folder listing (docs/DATA.md)"""
    import local
    return local.raw('cities', os.path.basename(os.path.normpath(city)), *p)


def box(city):
    """the city's box (west, south, east, north) from its city.yaml: the extent every download and reader of the city uses"""
    import yaml
    f = os.path.join(city, 'city.yaml')
    if not os.path.isfile(f): raise SystemExit(f'{city}: no city.yaml here (give the city folder, cities/<slug>)')
    return tuple(yaml.safe_load(open(f, encoding='utf-8'))['box'])


def ensure(city):
    """make the build and delivery folders"""
    for f in (data, logs, export, audio, video, review, dist): os.makedirs(f(city), exist_ok=True)

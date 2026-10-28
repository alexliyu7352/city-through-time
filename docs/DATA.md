# Data rules: where buildings, maps and years come from, and how to label them honestly

## The most common mistakes in this step

- The frame is too big and mostly farmland, so the city does not fill the picture; and the place the story needs is outside the frame → set the frame according to "Extent and scale".

## Getting started

Copy `templates/city.yaml` to `cities/<slug>/city.yaml` and fill in the extent (box), scale and data sources;
fetch OSM with `uv run python -I pipeline/osm.py cities/<slug>` (it fetches the city's area, worked out from the box in city.yaml); run `pipeline/terrain.py` (DEM) and `pipeline/satellite.py` (Sentinel-2) once each;
produce the model with `uv run python -I pipeline/prep.py cities/<slug>`. Then render one white-model still to confirm the extent and scale.

**Where downloads live.** Downloads stay outside git, under this machine's raw root (`raw` in `local/config.json`). What only one city uses, its OSM answers and
its Overture footprints, goes in that city's own folder, `<raw root>/cities/<slug>/` (`pipeline/layout.py` `raw`). What serves many cities stays shared under the raw root:
GHSL tiles (`ghsl/`, one tile covers 1000 km), CMAB provinces (`cmab/`), imagery tiles (`tiles/`), Natural Earth. Every fetch and every reader takes the city's
**area**, not its box: the plate is a north-up rectangle in metres cut from the box, and the box turned into metres leans, so half of each
plate edge stands outside the box (by a few hundred metres; Xianyang 360 m). The area is the lon/lat box around the plate (`pipeline/geo.py` `Frame.area`,
`pipeline/layout.py` `area`); data fetched for the box alone leaves that ground without terrain, buildings or roads. A reader takes the file made for
the area, or the shared tiles that cover it (`pipeline/ghsl.py`). If `terrain.py` prints a WARNING that the DEM leaves part of the plate empty, find the missing
tile before going on: it is not a limit of the data to note. Never choose a raw file by its place in a folder listing (the first
or the last name): with a second city on the machine, that file is the other city's.

## Building footprints, heights, years

| Region | Adapter | Footprint | Height | Year | Licence |
|---|---|---|---|---|---|
| China | `pipeline/cmab.py` (`buildings.source: cmab`) | CMAB natural-city shapefile (Web Mercator) | estimated, MAE 3.8 m | first year an impervious surface appears in GAIA, 1985–2018; `AF2018` = after 2018; the earliest layer is written "already there by XXXX" | CC BY 4.0 (credit on the screen and in CREDITS) |
| Global fallback | `pipeline/overture_ghsl.py` (`buildings.source: overture_ghsl`, see below) | Overture Maps buildings | Overture `height` / `num_floors`×3.2 m, 9 m if missing | GHS-BUILT-S R2023A built-up area in 5-year periods (1975–2030, 100 m): the first period in which the cell holding the centroid reaches the threshold; those already there in 1975 are written "already there in 1975" | Overture ODbL/CDLA, GHSL CC BY 4.0 |
| Netherlands | (reserved) 3DBAG + BAG bouwjaar | ground truth | ground truth | ground truth | CC BY 4.0 |
| New York | (reserved) NYC Building Footprints `CNSTRCT_YR` / PLUTO YearBuilt | ground truth | ground truth | ground truth | public domain |
| Europe | (reserved) EUBUCCO (years for only 24%), Spanish Catastro | ground truth | mostly | partly | ODbL |

CMAB download: the provincial zips of figshare article 27992417 (Shaanxi = `shanxisheng.zip`, Shanxi = `shanxi.zip`); unzip into `raw/cmab/<province>/`, and `prep.py` finds every shapefile that intersects the extent by itself.

### Steps of the overture_ghsl adapter (global cities)

1. Overture: use DuckDB to select footprint, height and num_floors in the city's area from `s3://overturemaps-us-west-2/release/<release>/theme=buildings/type=building/` (needs network and duckdb + the spatial extension; `pipeline/overture_ghsl.py fetch cities/<slug> --release <name>`, into the city's own raw folder).
   Release names expire and old ones are taken down: first list the current ones (`curl 'https://overturemaps-us-west-2.s3.amazonaws.com/?prefix=release/&delimiter=/'`),
   then give the name explicitly and write the name into CREDITS (with a wrong name nothing is fetched). A DuckDB scan is heavy; do not run it at the same time as rendering or mixing.
2. GHSL: download the tiles of GHS_BUILT_S_E{1975..2030}_GLOBE_R2023A_54009_100 that cover the city's area (JRC open data; `pipeline/overture_ghsl.py ghsl cities/<slug>`: one tile, or two to four for a box across a tile edge); `prep.py` takes each building centroid's first built-up period from them.
3. The bands of `prep.py` use 5-year periods: `[already there in 1975, 1980–1989, 1990–1999, 2000–2009, 2010–2019, after 2020]`.
4. The screen and FACTS.md must say: "Years are estimates from GHSL 5-year built-up periods, accuracy 100 m".

## Maps (OpenStreetMap, ODbL)

`pipeline/osm.py` fetches by theme and caches by query hash in the city's own raw folder (`<raw root>/cities/<slug>/osm/`): water (water surfaces and river lines), roads, rail, historic (heritage sites, protected areas, tombs), places, aeroway.
Of the Overpass servers only overpass-api.de is stable, and it is slow (10–60 seconds a query); if the cache exists, do not fetch again.
Credit: write © OpenStreetMap contributors on the identity tag and the end card; write ODbL in CREDITS. Derived databases (raw/, data/) carry the same licence; the video itself is not restricted.

## Extent and scale

The model covers only the modern main urban area centred on the historic core, with a long side of about 20–30 km, at scale 1:10000 (plate about 2.5 m). Do not make the whole of a very large city.
`box` is in WGS84; `prep.py` chooses the UTM zone itself; one model unit = 1 model metre.

- **The extent must let the city fill the picture:** frame the historic core and the places the narration will mention; if most of the frame is farmland, tighten it, or the city does not fill the picture and looks like a patch of crumbs.
- **The extent must enclose both ends of the story:** if a place the story needs lies just outside the frame, widen the frame that way; for mountains and water far outside the frame use `terrain.context` (MODEL.md "Ground and terrain") and do not enlarge the plate.
- Xianyang: a 25 km frame was mostly farmland and 30,000 buildings could not fill it (a density that fills it is about 70,000 buildings in 319 km²), so it was tightened to the historic core; the front hall of Epang Palace is 700 m outside the frame, and
  for "from Epang cross the Wei, joining Xianyang" the southern limit was widened to 34.245, ending at 31 × 22 km.
- **After changing `box`, rerun the whole chain**, one job at a time: `osm.py` and, for Overture, `overture_ghsl.py fetch` (new area) → `terrain.py` → `satellite.py` → `prep.py` → compile. The same after a pipeline update changes the area every download covers (`layout.area`): a city prepared before keeps the old area's files, which are never read again, so `terrain.py` and `prep.py`
  stop on the missing new ones until the chain has run. Always write positions in the city settings as longitude/latitude
  (`ll:`, `lon`/`lat`), never as model coordinates (`v:`, `x`/`z`): when the plate centre moves, all model coordinates are wrong. Change in the same pass every place on screen that states the plate size ("Numbers on screen" in SCRIPT.md).

## Pictures and footage

Pictures in the film have two uses: each historic node ends with "the same place today" (footage, photos), and the look of the time (old maps, archive photos, old paintings, artefacts, imagined pictures based on the sources).

- **The picture list** (`research/images.md`, one section per station): for a picture found, record the source and licence; for a scene that has no picture but deserves one, mark it too (the city at its most prosperous,
  the scenes of major events, the mood of a poem, not limited to the main line), say what is to be drawn and the basis for the details (the sources for buildings, clothes, objects, terrain). When writing the script, use it to decide
  which imagined pictures to generate (SCRIPT.md "Pictures").
- Priority: taken by the user or licensable by the user → Wikimedia Commons (CC BY / CC BY-SA / CC0; search "<city> aerial", "<landmark>" and the English name, `Special:MediaSearch?type=video`) → open material of governments and museums → web videos (internal testing only).
- First look up the author and licence of all candidate files at once with the Commons API (`https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|extmetadata&titles=File:A|File:B&format=json`,
  at most 50 at a time), drop those whose licence does not fit, then download them one by one (the CC0 photos and 4K CC BY-SA videos of Xianyang were found this way in one query).
- Download: the Commons original `https://upload.wikimedia.org/...` with `curl -L -o <explicit file name>`; use yt-dlp for Bilibili and the like. Keep the original in the local ref folder (`ref` in `local/config.json`), not in the repository.
- Processing: find where the original's subtitles and watermark sit and crop them out (`crop`). In web videos the position of subtitles and place-name bars changes: sample a frame every few seconds along the whole clip and set the crop box by the innermost bar,
  not by looking at a single frame. Then scale to 1600×900, desaturate by about 15%, and convert to all-intra H.264
  (`-g 1`, so the page can seek frame by frame), and put it in `cities/<slug>/assets/footage/`.
  The command looks like: `ffmpeg -ss S -t D -i in -vf "crop=…,scale=1600:900,fps=24" -an -c:v libx264 -crf 20 -g 1 out.mp4`.
- On screen: length and manner follow STAGING.md "Footage and pictures": 4K video full frame for 7–9 seconds (slow push-in, letterbox bars, top left "今天 · TODAY · 實拍" ("Today · TODAY · live footage") + place name, bottom right the source),
  high-resolution photos in the right-hand panel, low-resolution material as a small card with a leader line; do not flash by in 4–6 seconds.
- Web player bundle: all-intra frames are only for the renderer's frame-accurate seeking (Xianyang's footage is about 33 Mbps, 104 MB); when `tools/web.py` packs the bundle it re-encodes it into a streaming format for the web
  (CRF 26, `-g 24`, faststart; the whole Xianyang bundle fell from 206 MB to 121 MB). Do not put render-grade material on the web as it is.
- Reproducible: write the crop and transcode commands into `cities/<slug>/assets/footage/make.sh` (.mp4 files are not in the repository; the originals are in the local ref folder).
- Record: the FACTS.md table "Footage and photos" (clip, on-screen label, source, licence, time point in the original); CREDITS lists CC and "non-CC · internal testing only · must be replaced before release" separately.

## High-resolution satellite base (internal testing only)

- `pipeline/imagery_tiles.py`: fetches Esri World Imagery level-15 tiles (about 4 m), stitches and reprojects them into the plate's UTM frame, and writes `data/satellite_hr.jpg`. The tiles are cached in `tiles/` under the local raw folder.
- It is not open data. `film.satellite_source: hr` is for internal testing only; any version to be released goes back to `sentinel` (Copernicus Sentinel-2, releasable, credit required). CREDITS must list them separately.

## Honest labelling (must appear on screen)

- The readout source line: dataset name + the word "estimate" (example: `CMAB · GAIA 不透水面首次出現年份（估算）` (first year an impervious surface appears, estimate)).
- Pins or labels of schematic polygons get "（示意）" ("schematic"); estimated positions get "（位置示意）" ("location schematic").
- End card lines two and three: data sources and licences; "heights and years are estimates"; "historical sources: see FACTS.md".

## Modern "growing taller": GHSL built volume (`pipeline/ghsl_change.py`)

- Data: GHS-BUILT-V R2023A, 100 m cells, every 5 years 1975–2030 (2025 and 2030 are projections; only up to 2020 is read), CC BY 4.0. Download: `uv run python -I pipeline/ghsl_change.py fetch cities/<slug>` (the 1000 km tiles that cover the box, one or more; 12 periods, about 220 MB a tile).
- Use: for each of today's buildings take the volume series of its cell; if the building already exists later and the cell's volume grew by 1.5 times or more, treat it as "rebuilt taller": it first appears at the height of f0 (= volume then / volume in 2020), and grows to today's height in the periods where the volume grew most. `grow.change: ghsl`.
- What it cannot do: **demolition.** The observed volume of R2023A never decreases in any cell (checked over the whole Xianyang extent: no cell decreased between two periods), and no public data records demolished buildings. The film does not talk about demolition.
- On-screen label: "GHSL 建成体积 · 100 m · 5 年 · 估算" (GHSL built volume · 100 m · 5 years · estimate).

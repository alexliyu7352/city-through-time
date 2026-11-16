# Data rules: where buildings, maps and years come from, and how to label them honestly

## The most common mistakes in this step

- The frame is too big and mostly farmland, so the city does not fill the picture; and the place the story needs is outside the frame → set the frame according to "Extent and scale".

## Getting started

Copy `templates/city.yaml` to `cities/<slug>/city.yaml` and fill in the extent (box), scale and data sources;
fetch OSM with `uv run python -I pipeline/osm.py cities/<slug>` (it fetches the city's area, worked out from the box in city.yaml); fetch the buildings (CMAB unzipped, or for `overture_ghsl` both `pipeline/overture_ghsl.py fetch` and `ghsl`, below: `terrain.py` takes today's buildings out of the surface, so it stops until they are there); run `pipeline/terrain.py` (DEM) and `pipeline/satellite.py` (Sentinel-2) once each;
produce the model with `uv run python -I pipeline/prep.py cities/<slug>`, and check its heights against real storeys with `uv run python -I tools/heightcheck.py cities/<slug>` (where OSM has storeys; a warning means the heights need the layers in "Correcting building heights" below; its tables go in the report). Then render one white-model still to confirm the extent and scale: before the film has nodes, `uv run python -I pipeline/compile.py cities/<slug>` writes a stand-in film (the plate's centre from low, then the whole plate), and `node render/still.mjs <slug> 3 8` takes the low view and the whole plate. Both moments remain under the studio light; the 8-second view fits the plate's corners and height envelope with room around them, without the projection or chapter overlays.

Sentinel scenes can cover only part of their MGRS grid tile. `satellite.py` keeps its preferred scenes, fills uncovered pixels from other scenes matching the same search, and records those additions in `satellite.json` `fill_scenes`. It stops without replacing existing outputs if coverage is still incomplete: widen `--from`/`--to` or raise `--cloud`, then rerun it. A successfully written mosaic has `coverage_percent: 100`; do not accept a black strip as a data limit.

**Where downloads live.** Downloads stay outside git, under this machine's raw root (`raw` in `local/config.json`). What only one city uses, its OSM answers and
its Overture footprints, goes in that city's own folder, `<raw root>/cities/<slug>/` (`pipeline/layout.py` `raw`). What serves many cities stays shared under the raw root:
GHSL tiles (`ghsl/`, one tile covers 1000 km), CMAB provinces (`cmab/`), 3D-GloBFP cells (`globfp/`), imagery tiles (`tiles/`), Natural Earth. Every fetch and every reader takes the city's
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

### Correcting building heights

An estimated-height dataset can be wrong in both directions at once: tested against about 2,200 OSM storey counts in a dense
Chinese city centre, CMAB read two- and three-storey lanes at about 23 m and towers of more than twelve storeys at about 32 m
(rank correlation 0.13), so the city read as one flat slab and its old quarters as blocks. Three opt-in layers under `buildings` correct the primary adapter's heights, applied in
this order, each one only where it has evidence, and each recorded per building (before and after) in
`build/data/building_heights.json`:

1. **`height_correction`**: an outside footprint dataset with heights. Each primary building takes the overlap-area-weighted
   median of the dataset's heights over it, where the dataset's footprints cover at least `min_cover` of its area (default 0.3);
   otherwise it keeps its own height. The dataset's own footprints are never drawn.
2. **`height_supplement`**: matched OSM `height` or `building:levels`, raising and, with `lower: true`, also lowering a building
   (below).
3. **`height_zones`**: researched polygons of a known height or storey range, for low old quarters that no dataset separates
   from their blocks. Schematic (estimated).

None of them changes a footprint, a year, an age method or the building order. With none of the keys, prep is exactly as
without this section.

```yaml
buildings:
  source: cmab
  exaggeration: 1.0
  height_correction: { source: globfp, min_cover: 0.3 }
  height_supplement:
    source: osm
    floor_height_m: 3.2
    lower: true            # matched OSM heights and storeys lower as well as raise (default false: raise only)
    # Optional: tall whole buildings entirely absent from the primary footprints.
    fill_gaps:
      min_height_m: 100
      min_levels: 30
      ghsl_threshold_m2: 1500
    # Optional: separately modelled landmarks, excluded from matching and gap fill.
    exclude_osm: [way/123456]
  height_zones: research/height_zones.geojson   # or a list of zones written here (below)
```

#### The dataset correction (3D-GloBFP)

3D-GloBFP (Che et al. 2024, Earth Syst. Sci. Data 16, 5357-5374) maps buildings worldwide, each with a height estimated from
satellite data, under CC BY 4.0. In the same test it followed real heights much better than CMAB (rank correlation 0.42
against 0.13; three storeys or fewer at a median 16 m, more than twelve at 53.5 m) but is still an estimate: it stays
labelled one. Other datasets tested were flat (CNBH-10m, GHSL ANBH: about 20-30 m everywhere) or non-commercial (GBA, CC BY-NC,
which the films' CC BY-SA licence cannot take).

- Fetch once per city: `uv run python -I pipeline/globfp.py fetch cities/<slug>`. It lists the ten figshare parts once into
  `<raw root>/globfp/index.json` (DOI, version, licence, md5 of every file), then downloads only the grid cells whose bounds, in
  their file names, meet the city's area (`pipeline/layout.py` area); a cell already there with the right md5 is kept. Cells
  are shared by every city they cover. The zips stay zipped (prep reads them in memory: a cell unzipped is three times larger).
  `prep.py` never fetches; it stops and names the missing cells.
- Where 3D-GloBFP has no cell, or covers too little of a footprint, the building keeps the primary's height; the sidecar counts
  `corrected`, `raised`, `lowered`, `low_cover` and `no_cover`.
- Credit in CREDITS: "Building heights corrected with 3D-GloBFP (Che et al. 2024), CC BY 4.0", with the citation and the DOI of
  each part used (`building_heights.json` layers.dataset: `citation`, `tiles`). On screen the readout's source line names it
  with the primary (`CMAB+3D-GloBFP+OSM`), still marked as estimates.

#### OSM heights and storeys

1. Fetch `uv run python -I pipeline/osm.py cities/<slug> building_heights` once for the city's area. It caches building and part
   polygons carrying `height` or `building:levels`; existing caches are not fetched again. `prep.py` never silently fetches data.
2. `pipeline/heights.py` reads **existing whole buildings**, excluding construction, proposed buildings and separate roof,
   antenna or other parts. `height` is metres by default; explicit metric or feet/inches units are converted. Ranges, multiple
   values and invalid numbers are refused. `ele` is not a building height. An explicit height takes precedence over a storey
   count; `building:levels × floor_height_m` is only an **estimate**, excluding underground storeys. The default 3.2 m is the same
   convention used by the Overture adapter, not an OSM measurement or a guarantee about roof height.
3. A reference's centroid must be inside the primary footprint (3 m mapping tolerance), with at least 70% overlap of the smaller
   polygon, at least a 1:4 area ratio and at least 35% intersection-over-union. One reference raises at most one primary polygon.
   Nearly tied matches or conflicting nearly tied references are refused. There is no nearest-building transfer across a road
   or from a small tower to a large podium. A higher matched reference raises the primary height. A lower one leaves it unchanged,
   unless `lower: true`: then it lowers it too (an OSM storey count is better evidence for one building than a remote-sensing
   estimate over a merged block); the report counts `raised` and `lowered` apart. Absent or ambiguous references leave it
   unchanged. No year, age method, footprint or primary building order changes.
4. Rerun `prep.py`. `build/data/building_heights.json` records every raised building, primary height, reference ID, name, tag,
   URL, overlap, estimate flag, cache snapshot and matching counts, plus unmatched references at least 200 m high.
   `stats.json` includes the selected height source for each of its tallest ten; `model.json` keeps its existing building format.
   This is the **prepared dataset's** tallest ten, not a city's complete real-world ranking: unmapped or unmatched towers remain
   a gap, not an invented height. `uv run python -I pipeline/heights.py inspect cities/<slug>` explains the overlap and
   centroid distance of mapped towers against the prepared footprints without changing them. Disabling the supplement
   resets the sidecar to `enabled: false` rather than leaving an earlier run's changes active. Test parsing and matching with
   `uv run python -I pipeline/heights.py selftest`.
5. Credit both datasets: primary footprints and age estimates, plus © OpenStreetMap contributors, ODbL 1.0, for supplemented
   heights and storey counts. Record the selected source and remaining uncertainty in FACTS.md and CREDITS. On-screen labelling
   must distinguish mapped heights, storey-based estimates and the original estimated years; a supplement does not make all
   heights or construction years ground truth. OSM height conventions and an owner's architectural height can differ; preserve
   the tag actually used and explain the difference instead of quietly replacing it with a preferred number.

`fill_gaps` is optional and uses the same whole-building references. It adds a footprint only when its explicit height is at
least `min_height_m`, or its height is inferred from at least `min_levels` storeys. Its centroid must be on the plate and its
entire footprint must have **no intersection at all** with any primary footprint, even a small overlap or a shared boundary.
Accepted additions cannot intersect each other either. This is deliberately stricter than height matching: a reference with
an ambiguous primary counterpart remains a gap, rather than duplicating a tower or replacing primary geometry.

Download GHSL with `uv run python -I pipeline/overture_ghsl.py ghsl cities/<slug>` before enabling gap fill. The tool reuses
that adapter's `first_epoch` sampler and the GHS-BUILT-S R2023A 100 m cells, with the same built-up threshold and five-year
spreading described below. A reference with no qualifying epoch is skipped, never assigned an invented construction year.
All primary footprints, order, years and age methods remain unchanged; additions are appended with `age_method: epoch`.
The sidecar records each addition's OSM ID, height tag, footprint source, GHSL epoch and estimate flag; stats also distinguish
the source epoch (`year`) from the spread model year (`model_year`). Record GHSL's CC BY 4.0 credit in CREDITS and label the
screen "GHSL 100 m / 5-year built-up periods, estimated". Already built up in 1975 describes the cell's ground, **not** a
present-day tower's construction in 1975.

Put researched landmarks in `exclude_osm` by exact `type/id`, not a translated name. They take their documented existence
events and separate `landmarks.py` models; exclusions do not erase the primary base. Use the existing landmark masks when
the independent models are built. Until then, report the prepared base and landmark studies separately, including the
remaining skyline gaps. A height-envelope study is schematic massing, not a completed landmark reconstruction.

#### Researched height zones

Old low quarters (lanes of two- or three-storey houses, an old town's courtyard fabric) are often one footprint per block in
the primary data, and every height layer above then still gives the block one height, usually too high. A zone gives the
buildings inside a researched polygon the height the sources give that quarter:

- Either a list in `buildings.height_zones`, each `{polygon: [[lon, lat], ...], storeys: [2, 3], source: "...", label: "..."}`,
  or a GeoJSON path in the city folder (`research/height_zones.geojson`) whose features carry the same keys as properties.
  Each zone has exactly one of `height_m` and `storeys`, a number or `[low, high]`; `floor_height_m` defaults to 3.2.
  `source` (where the height comes from, also in FACTS.md) and `label` (what the zone is) are required.
- A primary building whose centroid lies inside takes the zone's height; with a range, each building its own value in it,
  from its centroid (the same every run), so a quarter does not stand as one flat block. Where zones overlap, the first listed
  wins. OSM gap-fill towers keep their own heights. Zones come last: they override the dataset and OSM for the buildings inside,
  so draw a zone around the low fabric only, not round a tower standing in it.
- Zones are schematic: the sidecar marks each one `schematic: true` and its buildings' height source says so; label them
  "schematic (estimated)" in FACTS.md and in the readout's source line (the stand-in film adds `zones schematic`).

#### Checking the heights

Run `uv run python -I tools/heightcheck.py cities/<slug>` after every prep that changes heights, and give its tables in step 2's
report. It matches the OSM buildings that carry storeys to the prepared footprints and prints, per storey band, the model's
median against storeys x 3.2 m with the error and the rank correlation, at each stage: the primary's heights, after the
dataset correction, and final (with the appearance sidecar's own child heights). Once OSM applies, the rows it set agree by
construction, so it also prints the final table without them. A rank correlation **under about 0.3 before the OSM layer is a
warning**: the city reads flat or inverted whatever the supplement fixes; try the dataset correction and look at the tallest
list. It also lists the tallest buildings with the layer that set each, every layer's counts, and with
`--areas research/<file>.yaml` (`areas: [{id, ll: [lon, lat], radius_m}]`) each area's median height at each stage, to see a
quarter before and after its zone. It reads only and writes `build/logs/heightcheck.txt`.

Choose the present-day vertical factor **after** correcting heights. `buildings.exaggeration: 1` preserves true skyline
proportions (a 632 m tower is 0.0632 model metres at 1:10000); do not stretch surveyed or mapped skyscrapers fourfold because an
earlier dataset was too low. This setting applies to today's base, independently of terrain and schematic period house types.
A separately modelled landmark uses its documented geometry and `exaggeration: 1` for true proportions. Its period city's
existing `hide_layer` / `keep_layer` and `today_from` mechanism clears the corresponding base footprints; it replaces the base
block rather than standing on it or duplicating it. Give the landmark its researched construction / opening event in staging:
the primary dataset's first-impervious-surface year stays an estimate even after its present-day height is corrected.

### Optional appearance footprints

`buildings.today_footprints` is absent/off by default. It produces `build/data/today_footprints.json` for a colour renderer,
without changing `model.json`, `stats.json`, the primary indices, years or white geometry. It works with any primary adapter.

```yaml
buildings:
  today_footprints:
    enabled: false
    source: osm_matched       # primary | osm_matched
    regularize: guarded      # 'off' | guarded (quote 'off' in YAML)
    split_coverage: 0.4
    split_distribution: 0.7
    protect_bi: []            # reviewed primary identities whose appearance must retain the original outline
```

Fetch `pipeline/osm.py CITY building_footprints` explicitly: unlike building_heights this includes outlines without heights.
prep never fetches it. Parts, construction and invalid outlines are excluded; polygon holes remain. Named landmarks in the
height supplement's exclude_osm and appended gap-fill records retain their primary base. The cache is not added to the
general named-geometry lookup, so fetching it cannot change historic traces or the white film.

Use `protect_bi` for reviewed named buildings whose roof silhouette differs from the mapped ground outline, or where a
whole-building tag actually represents a base or part. It prevents both OSM replacement and regularization without changing
height supplementation. Identities refer to the exact prepared model, not OSM IDs; missing identities are refused. Review the
list again if primary data changes. Protection retains matching decisions for other buildings, then reruns the normal overlap
guards against the restored outlines. It does not authorize or create a separate landmark model.

One-to-one candidates use heights.py's shared geometry scores and reject ambiguous or multiple references. Splits are considered
first: each whole-building child must have at least 70% inside a unique primary parent. The union covers at least 40% of the
parent, and its convex hull covers at least 70% to reject groups missing a whole wing. The hull is only a distribution test,
never output geometry. These configurable thresholds require a plan overlay review in the city's research. Overlapping children
are refused. Final quantized alternatives are checked together against all other buildings: a new overlap over 0.01 m² beyond
the original overlap rejects both changed parents. Rollbacks are checked again until stable; rejected split groups retain the
primary outline rather than drawing only one child. Candidate and accepted parent/child counts are reported separately.

Every child keeps its parent's bi, original centre, year and grow/renew timing; it makes no new construction-date claim.
Height stays at the approved primary value, raised only by that child's valid explicit, non-estimated OSM height; a lower
height or storey estimate does not change it. With `height_supplement.lower: true` each child instead takes its own OSM height,
or its own storeys x `floor_height_m`, up or down (a split block's tower and its low neighbour each their own), except under a
height zone: a parent a zone set keeps the zone's height in every child, since zones come last. The sidecar then says
`child_heights: both ways`. No OSM start_date is used. New outlines are seated on the same terrain.

`regularize: guarded` applies only where the sum of whole-building OSM intersection areas is at most 1 m². It tries topology-preserving
2 m simplification and near-axis least-movement constraints within 10 degrees. The axis adjustment is at most 1 m Hausdorff;
the combined change at most 3 m and 3% area, with holes preserved. Failed stages keep their preceding shape; final new overlaps
roll back the whole parent. Label these outlines schematic, not measured improvements. Defaults may be tightened with
simplify_m, angle_deg, max_move_m and max_area_change; regularization can be off independently of OSM replacement.

Normal prep writes the sidecar after its unchanged outputs. `pipeline/prep.py CITY --footprints-only` rebuilds just it after
the prepared model changes (including terrain grading), leaving primary data alone. Disabled prep writes an explicit disabled
sidecar to stop stale alternatives. Web packing includes only enabled sidecars. Credit the OSM snapshot and ODbL in CREDITS.

The integration API is `await S.buildTodayFootprints(sidecar)` (or exported `buildTodayFootprints(model, sidecar, options)`
in studio.js). It returns `{geometry, skipBi, skipCentres}` and never changes the source mesh. The sparse geometry has normal
city attributes plus aBi; all children share the original aCtr and parent timing. The colour renderer hides those original
parents only in its colour material and draws the sparse geometry; the white material keeps the original. Do not fold original
vertices or copy dates from the sidecar. A Float64-stream SHA256 binds all primary building records/metadata to the sidecar;
an outdated or malformed sidecar is refused. The sidecar also records the source file's exact SHA256. This API does not itself
load a sidecar or alter mini.js: a renderer must explicitly opt in, including its shadows, AO and tree avoidance.

Checks: `pipeline/footprints.py selftest`, `node tools/footprintcheck.mjs --selftest`, and `node tools/footprintcheck.mjs CITY`.
`pipeline/footprints.py review CITY AREAS.yaml OUT_FOLDER` makes before/after plan overlays and coverage figures; AREAS holds
`areas: [{id, ll: [lon,lat], radius_m, focus_bi}]`. Keep OUT_FOLDER under the city's build/review. Use
`render/still.mjs --format png --seed N` for exact white-frame comparisons; default JPEG output stays unchanged. Before delivery,
compare prepared files byte for byte, check white PNG pixels against the baseline and verify disabled/missing-sidecar behavior.

### Steps of the overture_ghsl adapter (global cities)

1. Overture: use DuckDB to select footprint, height and num_floors in the city's area from `s3://overturemaps-us-west-2/release/<release>/theme=buildings/type=building/` (needs network and duckdb + the spatial extension; `pipeline/overture_ghsl.py fetch cities/<slug> --release <name>`, into the city's own raw folder).
   Release names expire and old ones are taken down: first list the current ones (`curl 'https://overturemaps-us-west-2.s3.amazonaws.com/?prefix=release/&delimiter=/'`),
   then give the name explicitly and write the name into CREDITS (with a wrong name nothing is fetched). A DuckDB scan is heavy; do not run it at the same time as rendering or mixing.
2. GHSL: download the tiles of GHS_BUILT_S_E{1975..2030}_GLOBE_R2023A_54009_100 that cover the city's area (JRC open data; `pipeline/overture_ghsl.py ghsl cities/<slug>`: one tile, or two to four for a box across a tile edge); `prep.py` takes each building centroid's first built-up period from them.
3. The bands of `prep.py` use 5-year periods: `[already there in 1975, 1980–1989, 1990–1999, 2000–2009, 2010–2019, after 2020]`.
4. The screen and FACTS.md must say: "Years are estimates from GHSL 5-year built-up periods, accuracy 100 m".
5. A building's period is when its cell was first built up: it went up some time in the five years before. `prep.py` spreads each building over those five years
   by its place (the same every run), so a period's buildings come up through it instead of all in one second at a fixed camera (`buildings.epoch_spread: false` keeps
   the periods' own years). The bands and counts stay by period. GHSL's 2025 and 2030 are projections, not measurements: a building first built up in them
   was not there in 2020's imagery and stands in today's footprints, so it is spread over 2020-2025, never dated by the projection.

## Maps (OpenStreetMap, ODbL)

`pipeline/osm.py` fetches by theme and caches by query hash in the city's own raw folder (`<raw root>/cities/<slug>/osm/`): water (water surfaces and river lines), roads, rail, historic (heritage sites, protected areas, tombs), places, aeroway.
Of the Overpass servers only overpass-api.de is stable, and it is slow (10–60 seconds a query); if the cache exists, do not fetch again.
Credit: write © OpenStreetMap contributors on the end card (and in the description); write ODbL in CREDITS. The identity line at the top keeps where and how big the city is: a credit there is too small to read on a phone, and compile faults one. Derived databases (raw/, data/) carry the same licence; the video itself is not restricted.

## Extent and scale

Set the extent by the story: the historic core and every place the narration needs, tight enough that the built city fills the picture (for instance a long side of about 20–30 km for a large city, at scale 1:10000: plate about 2.5 m); far mountains and water go in `terrain.context`. Do not make the whole of a very large city.
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
- On screen: how footage and pictures are shown (how long, and as full frame, panel or card) is set in one place, STAGING.md "Footage and pictures" ("the same place today");
  this file keeps the data side: where the material comes from and its licence (above, and the record below), and its resolution, which decides the modes it can take there.
- Web player bundle: all-intra frames are only for the renderer's frame-accurate seeking (Xianyang's footage is about 33 Mbps, 104 MB); when `tools/web.py` packs the bundle it re-encodes it into a streaming format for the web
  (CRF 26, `-g 24`, faststart; the whole Xianyang bundle fell from 206 MB to 121 MB). Do not put render-grade material on the web as it is.
- Reproducible: write the crop and transcode commands into `cities/<slug>/assets/footage/make.sh` (.mp4 files are not in the repository; the originals are in the local ref folder).
- Record: the FACTS.md table "Footage and photos" (clip, on-screen label, source, licence, time point in the original); CREDITS lists CC and "non-CC · internal testing only · must be replaced before release" separately.

## High-resolution satellite base (internal testing only)

- `pipeline/imagery_tiles.py`: fetches Esri World Imagery level-15 tiles (about 4 m), stitches and reprojects them into the plate's UTM frame, and writes `data/satellite_hr.jpg`. The tiles are cached in `tiles/` under the local raw folder.
- It is not open data. `film.satellite_source: hr` is for internal testing only; any version to be released goes back to `sentinel` (Copernicus Sentinel-2, releasable, credit required). CREDITS must list them separately.

## Honest labelling (must appear on screen)

- The readout source line: dataset name + the word "estimate" (example: `CMAB · GAIA 不透水面首次出現年份（估算）` (first year an impervious surface appears, estimate)).
- Corrected heights name every height source (`CMAB+3D-GloBFP+OSM`), still as estimates; researched height zones add "schematic" (`示意` in Chinese).
- Pins or labels of schematic polygons get "（示意）" ("schematic"); estimated positions get "（位置示意）" ("location schematic").
- End card lines two and three: data sources and licences; "heights and years are estimates"; "historical sources: see FACTS.md".

## Modern change: GHSL built-up series (`pipeline/ghsl_change.py`)

- Data: GHS-BUILT-V R2023A, 100 m cells, every 5 years 1975–2030 (2025 and 2030 are projections; only up to 2020 is read), CC BY 4.0. Download: `uv run python -I pipeline/ghsl_change.py fetch cities/<slug>` (the 1000 km tiles that cover the box, one or more; 12 periods, about 220 MB a tile).
- What it holds: when each cell's **built-up ground** grew, not how tall it grew. Its volume for every epoch is that epoch's built surface times the cell's 2018 height (GHSL Data Package 2023, §2.3): a cell's volume over its surface stays the same from 1975 to 2020 (checked over Xianyang: 2,299 growing cells, spread 0.003 % at the median). So it dates when a plot became built-up (the first layer of a building dataset that says only "there by 1987", spread over 1975–1987 by its cell's growth) and counts the new buildings per year; **never show a building growing taller from it** (an earlier version did, for a third of Xianyang's buildings, from growth that was all ground). `grow.change: ghsl`.
- What it cannot do: **demolition.** The observed volume of R2023A never decreases in any cell (checked over the whole Xianyang extent: no cell decreased between two periods), and no public data records demolished buildings. Nothing in the film shows or implies demolition from GHSL data (it records none); a demolition the sources record is told and staged from those sources, with its basis.
- On-screen label: "GHSL 建成体积 · 100 m · 5 年 · 估算" (GHSL built volume · 100 m · 5 years · estimate).

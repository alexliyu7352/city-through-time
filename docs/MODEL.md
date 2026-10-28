# Period cities and terrain

## The most common mistakes in this step

- One ring, a few rows of grid cells, houses that are only walls, an empty city → one whole city per period generated from the sources, filled in, checked item by item against the sources' drawings ("A whole city for each period", "No empty cities").
- A hard-coded terrain exaggeration, so the foundation on a slope is taller than the house → measure by slope ("Appearance and height").
- Houses of another region or period drawn with the built-in houses (north China's courtyards), or a city's own code drawing its houses → declare the house types from the research and look at them on the sheet first ("House types").

## A whole city for each period

**Every historic period is a 3D model of a whole city:** write a `city:` spec in the node, and `pipeline/citygen.py` generates it (walls, gates and barbicans, main streets and lane network, courtyard / dwelling / dormitory plots,
palace courtyards, terraces, elevated corridors, temples, bell towers, pagodas, cotton mills, stations, bridges, boats, trees; the houses of other regions and periods: "House types"). Follow the sources where there are sources (archaeological plans, gazetteer city maps, OSM site outlines); where there are none, follow the custom of contemporary cities of the same kind and label the picture "schematic".
Do the close-up for the city with the fullest sources first; close-up camera distance 0.035–0.06 (about 0.1 m per pixel), elevation 10–15°, gliding along the main street inside the walls (`fov: 40–44`),
and lay the other periods only once the houses are recognisable as houses. Take these stills with `uv run python -I tools/modelview.py cities/<slug> <era> --at <lon>,<lat>`
(a city not in city.yaml yet: `--spec <file> --year <y>`): it compiles that city alone in a study folder beside the film and shows it in the film's own palette and light, with the camera landed on the ground
(by default the close-up above); city.yaml, script.yaml and build/ stay as they are, so never copy or swap them to take model stills. For a city with no schematic, first send a research subagent to find the archaeological and documentary layout (written into `research/`); do not fill in with grid cells.
Every historic period needs at least one low-angle close-up (elevation 10–15°) so that the audience sees that houses are houses; the wide shot is used only to see the colour change and the growth.
For a part made from the sources, check the model against that drawing item by item: position, orientation, tiers, size; no error from compile or clipcheck does not mean it is right
(example: the three tiers of a platform were stacked in the wrong direction, and no check will report that).
**After any change to a period city's model or to the look** (citygen, a house type, `engine/props.js`, the light and shading), look at every period city from every side:
`node tools/eraview.mjs <slug> [--eras a,b]` first runs `tools/geocheck.mjs`, which stops on any face of a period city or prop that points into its piece (such a face is either not drawn from
outside, so a near wall goes missing and the inner side of the far wall shows through, or is lit as if it faced away, so a gable end shines white in its roof); it then takes each period city's
densest houses from eight bearings at two heights, its four largest landmarks from four bearings each (where a stair, a tree or a road meets a big building)
and the whole city from four, in the film's look and in a check look (plain white, everything sharp, the key light fixed in the room, so a face
is seen to turn from lit to shade as the camera goes round), one sheet per city and look in `build/review/eraview/`. Look at every sheet before reporting: a fault on one side of a house does not
show in a still from the other side. The same scene is a page for looking round by hand, with the user or alone: `play.html?city=<slug>&view` (printed by `tools/preview.mjs`; drag to turn,
right-drag to move, the wheel to come closer, the arrow keys to turn, a double click to look at a point; tick the period cities to show, each at its place on the plate; 全 / 近 for the whole city or
its houses up close; 成片 / 檢查 for the two looks; `&quality=low` is faster and leaves out the period cities' shadows).
**Every compile checks the period cities' models** (geocheck, and clipcheck: things standing in one another, a tree in a house, a street stopping short) and stops when
one fails, after writing the film, naming the check and its log (`build/logs/geocheck.log`, `clipcheck.log`); fix the model and compile again, never set the check to warn
for the film (`CT_MODELCHECK=warn` is for model studies, tools/modelview.py). **A street ends at something:** another street, a gate, the foot of the stair or the face of
the building it leads to, or the edge of the city; an avenue's end written 80 m short of the palace it leads to reads as a broken road (clipcheck `streets_short`:
the end of a street 10 m wide or more that points at a landmark, earthwork or wall 20-150 m ahead without reaching it). When writing a street's points toward a
building, end it at that building's stair or face, not at a round number near it.

## House types

The generator's built-in houses (`typ: courtyard`, `dwelling`, `hut`, `slab`, `wards`) are one region's: north China's. A city elsewhere, or a period whose houses differ,
declares its house types from the research, as data: `types:` at the top of city.yaml (for all its periods) or in a node's `city:` (that period only). A fabric names a type with
`typ:` and gives the lot (`lot: [width, depth]` in metres; no `h_m`: a type is as tall as its storeys). A name the city does not declare is looked up in the shared library,
`types/<name>.yaml` (one file per type, written out whole; `types/han_courtyard.yaml` is one). Every key is a fact from the sources, and `basis` says which are estimates:

```yaml
types:
  <name>:
    where: <the region>                 # where, when, basis: required
    when: <the period>
    basis: research/<notes>.md, <what the numbers come from; which are estimates>
    form: row                           # detached | row (wall to wall, a yard behind) | court (one building round a court or a light well) | compound (separate buildings round a yard inside a wall)
    storeys: [2, 4]                     # fewest and most (storey_m: 3.2 by default)
    roof: { shape: gabled, pitch_deg: 30, overhang_m: 0.5, ridge: along }   # shape (OpenStreetMap roof:shape): flat, gabled, hipped, pyramidal, skillion, mansard, gambrel, dome, onion, round; ridge: along or across the street (detached, row)
    ground: shops                       # closed | shops | arcade (the upper storeys over a walk; arcade_m)
    # court: { frac: 0.3 } (court, compound: the court's share of the lot); yard_wall_m; portico_m; podium_m
```

A type written in the city can start from another (`from: <name>`) and change some keys; it still writes its own where, when and basis. A type's name is its own (never a
built-in one). A key a type does not have, a key its form does not use, or a missing where, when or basis stops compile with what to write. A round roof (`dome` over
the body's oval, `onion`, `round`: a barrel along the ridge) rises with its curve, so it takes no pitch and no eaves, and keeps its true shape while the walls are
exaggerated (a stretched dome reads as an egg). A city's own scripts (`research/*_gen.py`) lay out where things are; what a house looks like is a type, never code in the city, so every city builds with the same generator.
Look at the types before laying the city: `uv run python -I tools/modelview.py cities/<slug> <era> --sheet --at <lon>,<lat>` (a flat open place) builds a block of each type the period
declares or its fabric names, at the film's close-up distance, in its palette and light, and puts the stills side by side in `sheet.jpg`. Show the user the sheet, and lay the city once
each type reads as itself.

## Boundaries, overlay and change

The boundary is computed automatically from the generated buildings; for a boundary the buildings cannot give (a village moat) add `outline:`, and the footprints of the historic cities at the end are also drawn from it;
a city laid over the previous period writes `avoid_eras: [<id>]`, so the new quarters go around the old city. Walls, elevated corridors and street surfaces on slopes tilt with the slope (citygen `lay`); do not make them into steps segment by segment.
The later period must show change: a new city laid over the previous one must differ clearly in scale or layout (adding a few small courtyards does not count), enlarged according to the sources; the old city stays underneath, and after the colour change use a wide shot first
so that the audience sees the new city grow around the old one, then move closer (example: Xianyang's imperial capital follows the 《史記》 (Records of the Grand Historian): the palaces of the six states
line up along the north slope, and the new quarters of 120,000 households surround the old city).

## No empty cities

**No empty cities:** restore the period cities from drawings as far as possible (archaeological plan → reconstruction drawing or model → film and TV set → imagination by the custom of the same period), and label each item with its basis (excavation / documents / film and TV / imagination);
whatever is not excavated is labelled "schematic". Do not leave large empty spaces inside a palace city or inside walls (except ponds, gardens, squares, fields); fill the areas with no data by custom or by film layout.
`stages` select parts by name (`id` / `group`), never by index: the index breaks whenever the list changes.
Generate large numbers of buildings from the research list with a generator (example: `cities/xianyang/research/han_gen.py`, coordinates in metres with the front hall as origin), noting the basis for each item;
run clipcheck afterwards, and overlaps and clipping must be 0. A single building made from a reconstruction drawing (Qin Palace No. 1) may use `exaggeration` to lower the height exaggeration and keep its original proportions.
Roads must be continuous and textured: lay a road on a slope in segments, with adjacent segments taking the same height at the seam and meeting end to end without overlapping (a height difference leaves a thin shadow, and two overlapping faces flicker,
which looks like a broken dashed line); the road surface is drawn with rammed-earth grain and patches, and roads also have wheel ruts along them (one lane 4.2 m, the two ruts 1.4 m apart), which fade out automatically when the ground covered by a pixel
is larger than the texture, so they do not flicker from afar. Always lay a city on the ground the engine actually draws (`terrainio.plate_mesh`: the plate is a grid of about 48 m cells with flat triangles inside the cells,
higher than the sampled terrain in hollows), not on the sampled terrain; the base of a building takes the highest point in its footprint, sampled every 8 m or so.
**A house stands on one plane:** houses differ in height with the ground, but inside one house the ground was levelled before it was built. Every lot of a fabric and every walled court
up to 300 m (`Builder.COURT_M`; a palace city spans more ground than one plane can follow) is made one plane first (`Builder.lot_site`): fitted to the ground under the lot and raised just enough
that the ground nowhere pokes through, level where the ground is level, tilted with the hill up to 4 % (`Builder.lot_slope`); on a steeper slope the lot stands on a platform (台基) down to the
ground, and its walls keep their height on top of it. Every part of the house (wings, walls, gate, court, its trees) stands on that plane: never put the parts of one house each on its
own ground (the wings stepped against the walls and the court, each on a darker plinth of its own, and read as broken), and never let the foundation of a steep lot go into the
walls (a court on the 北阪 stood behind a wall as tall as a city's). clipcheck's `floating` knows the platforms.
**Large plots get multi-courtyard mansions:** a courtyard plot deeper than 60 m (`Builder.MANSION_D`) is built automatically as a mansion: one courtyard every 30 m or so along the central axis, side courtyards added on both sides of a wide plot, and the surrounding wall drawn in every detail.
A single courtyard cannot fill a large plot, leaving only a few thin houses at the edge around empty ground, which looks like an empty frame at low detail.
Likewise, a market must have rows of shops in every cell, and a workshop area must be drawn as courtyards one by one as excavated (`workshops`), not a single row along the street or scattered points: from afar they look like empty frames and grains of sand.
The sizes hard-coded in a generator (house depth, number of stall rows, number of courtyard sequences) must be tried on the largest plot in the city's settings: a large plot that cannot be filled gets only an outline, which is an empty frame at low detail.
When changing a threshold, avoid the batch the user has just seen and approved; do not let half of them change and half not.
**Lay out blocks from an old map or an archaeological plan** (`city.trace`): first register the map (georeferencing in QGIS), then trace on it the walls (polygons), streets (lines), blocks (polygons)
and landmarks (points or polygons), save them as GeoJSON in `research/`, write `kind` of each shape as wall, street, block or landmark, and the other properties are the settings of that item
(`lot`, `typ`, `w_m`, `shops`, the landmark's `type`…); houses in a block line up along the block's own long side, not the city-wide grid (`traced` in `pipeline/citygen.py`).
What is traced is built together with what is written in `city:`, and the two can be mixed. No city has used this feature yet; the first time, show the user a small piece first.
**Shops along a street** form a row wall to wall, of similar height, with a back yard behind each shop body and the yard walls joined in one line (with gaps between shops, uneven heights and open backs, a row looks like a row of teeth when seen obliquely from behind). Not built yet: houses on steep slopes lined up along contour lines (see "Ground and terrain").
clipcheck's `paving_under` checks whether the paving and yards are covered by the plate (more than 0.3 m counts), and it must be 0. A new quarter needs streets and lanes (`streets`, `lanes: {region}`); it cannot be only a field of houses.

## Appearance and height

**The dark room is the brightness ratio between the subject and the plate, not how black the plate is:** lift the plate with a blue tint, make the lit faces of the white model bright, and make the ring of light and the buildings of the current period the brightest,
most saturated small areas in the picture; lift the mid-tones with a curve and leave the black level alone; do not raise the whole thing to grey. On a phone in bright surroundings the dark parts smear together, and platform compression hurts dark gradients most.
For thresholds and how to measure, see CHECKS.md "Brightness".
Dark plate (`palette.plate/plateSide/water/plateEmit`), ivory model, edge lines (`film.edges`); three separate height exaggerations: `terrain.exaggeration` (terrain),
`buildings.exaggeration` (today's buildings), `city.exaggeration` (period cities, default 2). **Set the terrain exaggeration by slope; do not hard-code it:**
the foundation on a slope on screen is "actual drop × terrain exaggeration", and a house is "height × building exaggeration"; example: with terrain ×6 and buildings ×2,
the foundation of a courtyard on a slope is as tall as the walls, and the house looks stretched. `pipeline/terrain.py` measures the slope inside each dynasty city's extent and prints
one `foundations:` line per city: how much of a reference house's height (12 m wide, 6 m high × the city exaggeration) is taken by the highest tenth of foundations, and the highest exaggeration that stays within 30%;
if the configured exaggeration is above the limit of the steepest city, it prints a WARNING. After building, clipcheck's `tall_foundation` measures again with the real houses (it counts when the highest tenth exceeds 30% of the house height;
it must be 0), and also prints, on each line, the highest exaggeration this city can bear. Example: on the Xianyang plain even ×10 is fine, the north slope is about ×4.5, and the film uses ×3.
Mountain cities have big slopes and can mostly take only ×1–1.5 (the mountain is already high enough). Houses and halls on slopes also have a darker ring of plinth (`PLINTH`), so a high foundation reads as a plinth or stilt house and not as a stretched wall.

## Ground and terrain

**The ground is bare earth:** GLO-30 measures roofs, so `terrain.py` digs out every 30 m cell touched by today's building outlines (the source and fill of buildings) and levels it with the surrounding streets, yards and fields
(it does not use "data height minus building height": a cell mixes roofs and streets and the building height is an estimate, so the subtraction comes out pitted).
Tombs, loess plateaus and river banks are not buildings and stay as they are. `terrain.bare: false` does not level.
Not built yet (wait for the first mountain city): houses on steep slopes lined up along contour lines, and no houses where it is too steep.
**Terrain is exaggerated at two scales** (`terrain.detail: { below_m: 150, exaggeration: 1 }`, the default): large terrain such as plateaus, terraces and river valleys is exaggerated by `terrain.exaggeration`;
small relief below 150 m keeps its original height (×1). Copernicus GLO-30 is a surface model and measures today's roofs and treetops, and most of the small relief in a city is those;
exaggerating them by the large-terrain factor (for example ×6) makes 4 m of relief 24 m on screen, much taller than a 5 m dwelling, and the ancient city looks as if built on a heap of rubble. The true terrain is stored separately as `terrain_true16.png`;
take from it anything that prints metres (sections). After changing, rerun `pipeline/terrain.py` and `pipeline/prep.py`, then compile.
The two scales have a cost: steep scarps narrower than `below_m` (plateau edges, river banks) are flattened too, so the drop drawn at the foot of a landmark on a slope gets larger; changing `below_m` only moves the problem to another city.
After the change, look at clipcheck's `tall_foundation`, then take a close-up still of the landmarks on slopes (`tools/modelview.py`).
**Hills on the plate:** the plate is dark and the room light is high, so a hill reads only where light rakes across it; when the story stands on hills (the list below is not empty), write
`terrain.shade: { k: 1 }`: one fixed low sun (default `az: 325, el: 25`, from the north-west; the room light turns with the camera, this sun stays put) lights the slopes turned to it, as `terrain.context`'s shade does beyond the plate,
while flat ground and water keep the plate's colour. It needs only compile; `k` from 0 to 2 (2 begins to glow). `tools/modelview.py` looks across this light by default.
**Before touching the terrain** (exaggeration, scale, bare earth), list the landmarks that the sources name and that stand on a slope (terraces, plinths, palaces built along the slope), and after the change compare their heights on screen one by one
with the numbers in the narration (example: when the narration says "built on a high terrace", the picture must show it standing on a high terrace).
**Distant terrain:** when a mountain or water the story needs is outside the plate (Xianyang: Mount Jiuzong, the origin of the city's name, is 23 km outside the plate), do not enlarge the plate (the city would shrink and look empty); use
`terrain.context`: terrain only, the same colour as the plate, fading into darkness at the edge; next to the plate it uses the plate's height exaggeration and farther away drops to `exaggeration_far`
(with the plate's exaggeration a mountain becomes a wall; Xianyang's plate is ×3, the far terrain 2.5), and the readout must state the exaggeration. The grid must be fine enough to show ridges (at 150 m Xianyang's Mount Jiuzong was ground down to a dune; at 60 m it appears),
and the extent covers only the stretch from the plate to that mountain; `shade: { az, el, k }` is one fixed low-angle side light that lights only the slopes facing the light (flat ground keeps the plate's dark colour,
and lighting everything would look like snowfield): without it, distant mountains in the plate's colour are almost invisible against the night sky. After adding or changing `terrain.context`, rerun `pipeline/terrain.py`. Show it only in the nodes that need it (the `context` keyframe); a pin standing on it may appear only while it is shown (compile blocks it).
**Before measuring, confirm which copy you are measuring:** one thing often has several copies (terrain has the 8-bit `terrain.png`, the 16-bit `terrain16.png` and `terrain_true16.png`; the engine reads the 16-bit one).

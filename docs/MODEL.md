# Period cities and terrain

## The most common mistakes in this step

- One ring, a few rows of grid cells, houses that are only walls, an empty city → one whole city per period generated from the sources, filled in, checked item by item against the sources' drawings ("A whole city for each period", "No empty cities").
- A hard-coded terrain exaggeration, so the foundation on a slope is taller than the house → measure by slope ("Appearance and height").
- Houses of another region or period drawn with the built-in houses (north China's courtyards), or a city's own code drawing its houses → declare the house types from the research and look at them on the sheet first ("House types").
- A landmark of another region drawn with the generator's own kinds (a Chinese hall for a temple, a box for a dome) → one of the classes for any region, its sizes from the sources ("Landmarks of any region").
- A whole city laid in one go and sent back whole → one quarter first: its low close-up and a wide shot, approved, then the rest the same way ("A whole city for each period").
- Lots stamped over a district in a few fixed sizes, one bearing per district: from afar the city reads as tiled fields with stepped edges → blocks traced from the map, houses along each block's own streets ("Lay out blocks from an old map").
- A share of house types or a storey count with no basis, labelled "schematic" (a made-up ratio decides what the whole city looks like) → the share and the storey range written from the sources first ("House types").
- Open ground left as bare plate (gardens, a palace hill, the ground between public buildings): in a built-up city it reads as a lake → drawn as what it is, or filled by the sources ("No empty cities").
- Shapes no source has (a garden as a regular hexagon, a quarter cut along a ruler line) → traced from the registered map, or following streets and terrain, labelled schematic.
- Schematic houses kept where a sourced building stood → the sourced building first; the schematic houses in its way are moved or dropped, and the note says so.

## A whole city for each period

**Every historic period is a 3D model of a whole city:** write a `city:` spec in the node, and `pipeline/citygen.py` generates it (walls, gates and barbicans, main streets and lane network, courtyard / dwelling / dormitory plots,
palace courtyards, terraces, elevated corridors, temples, bell towers, pagodas, cotton mills, stations, bridges, boats, trees; the houses of other regions and periods: "House types"). Follow the sources where there are sources (archaeological plans, gazetteer city maps, OSM site outlines); where there are none, follow the custom of contemporary cities of the same kind and label the picture "schematic".
**Walls of any tradition:** `style: tower` (and `hip`, `han3`) builds the Chinese wall: a battered rammed-earth body, bastions (马面), gate towers with roofs, barbicans and a moat; `style: curtain` builds the masonry curtain wall of Rome, medieval Europe, the Islamic world and the like: an upright crenellated body, flat-topped towers projecting outward (`tower_shape: square | round`) at its corners, every `tower_every_m` along it and at `tower_pts`, each gate a dark passage between two towers, no roofs and no moat unless `moat: true`. A regular spacing written in a source (the Aurelian wall's 100 Roman feet) is a basis; one read off a map is an estimate, labelled so. A wall that does not close (one ending at a river or a cliff on both sides) is `pts:` instead of `ring:`, run with the city on its left; it has no inside, so a fabric on `region: walls` takes only the closed rings.
**Every period city starts from its research:** from the survey of step 1 (`research/period_cities.md`), research what the model needs before laying anything: the plans and positions of its buildings, the
house types and their share and storeys, the streets and lots of its quarters, its open ground, each item sourced or marked estimate, written into `research/<period>_*`. Periods are independent here:
one research subagent per period, in parallel (SKILL.md "Subagents and parallel work"). Research done only when a sample is sent back costs a round each time.
**Every period city starts with one quarter:** lay one quarter from its sources, show its low close-up and a wide shot, and lay the rest of the city only after it is approved (a whole city laid on a wrong idea is redone whole; a quarter is redone in a round).
Once a study is approved, freeze it: `uv run python -I tools/freeze.py <study folder>` keeps it with exactly the files its compile read (a study links research/ live, so an edited trace
moved an approved sample without a word), and `tools/freeze.py check <frozen folder>` later says whether the code of the day still builds it the same, before it is merged or built on.
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
show in a still from the other side. Each city is shown as it stands at a moment of the film, never with a part and what replaced it at once: a city that loses parts while
it stands (`lose:`) at the fewest moments that between them show every part of it whole (just before each loss that takes a part not yet shown, and once its last part has
risen), one set of sheets each (`<era>_m<k>_<look>.jpg`); `--at <seconds>` takes one moment of the film instead. eraview also takes a model study's folder. The same scene is a page for looking round by hand, with the user or alone: `play.html?city=<slug>&view` (printed by `tools/preview.mjs`; drag to turn,
right-drag to move, the wheel to come closer, the arrow keys to turn, a double click to look at a point; tick the period cities to show, each at its place on the plate; 全 / 近 for the whole city or
its houses up close; 成片 / 檢查 for the two looks; 時刻 1, 2 .. for the moments of a city that loses parts; `&at=<seconds>` shows every city ticked at that moment of the film;
`&quality=low` is faster and leaves out the period cities' shadows).
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
    ground: shops                       # closed | shops | arcade (the upper storeys over a walk; arcade_m); a court's street wing has its shops either side of its way in; never behind a yard wall (detached, compound)
    # court: { frac: 0.3 } (court, compound: the court's share of the lot); yard_wall_m; portico_m; podium_m
```

A type written in the city can start from another (`from: <name>`) and change some keys; it still writes its own where, when and basis. A type's name is its own (never a
built-in one). A key a type does not have, a key its form does not use, or a missing where, when or basis stops compile with what to write. A round roof (`dome` over
the body's oval, `onion`, `round`: a barrel along the ridge) rises with its curve, so it takes no pitch and no eaves, and keeps its true shape while the walls are
exaggerated (a stretched dome reads as an egg). A pitched roof keeps its pitch too: `pitch_deg` is the angle on screen (a 25-degree roof stretched x2 stood at 43 degrees and read as another country's steep gables). A city's own scripts (`research/*_gen.py`) lay out where things are; what a house looks like is a type, never code in the city, so every city builds with the same generator.
**Choose the form by how the buildings were built.** A block built in one go as one building (a block of flats round a light well, a barracks, a monastery, a mill's dormitories) is one body of one height:
`court` or `detached` on a lot the size of the block, `storeys` a single number. `row` is for a street built house by house, each on its own narrow lot, where a `storeys` range gives the street its uneven skyline.
On the sheet, a row whose units step up and down shows each unit's gable end standing above its lower neighbour: when the sources describe the block as one building, that sawtooth is wrong.
Look at the types before laying the city: `uv run python -I tools/modelview.py cities/<slug> <era> --sheet --at <lon>,<lat>` (a flat open place) builds a block of each type the period
declares or its fabric names, at the film's close-up distance, in its palette and light, and puts the stills side by side in `sheet.jpg`. Show the user the sheet, and lay the city once
each type reads as itself.
**How much of a quarter each type takes is a fact too:** write the share and its basis (a count in the sources, an excavated quarter, a named comparison) beside the layout before laying
the city, quarter by quarter; a share written "schematic" with no basis decides what the whole city looks like. Heights vary between buildings as the sources' storey range says, not by copying one block in rows.

## Landmarks of any region

The generator's own landmark kinds (`hall`, `terrace`, `palace`, `pagoda`, `court`…) are north China's. Elsewhere a landmark is one of a few classes of massing, written as data in
the node's `city.landmarks` with its sizes in metres from the research (`pipeline/landmarks.py`); the classes reach the monuments of most traditions, so a city never needs code of its own.
A building that stands in several periods or several places (a temple kept through three stations, a type of insula block) is written once in city.yaml's `landmark_types` (name -> the
landmark without its place, or files holding such a mapping or `{landmarks: [{name, ..}]}`); each copy is `{template: <name>, lon, lat, ..}` with what differs, a traced one too. On a slope a landmark is levelled at the highest ground under it with a
platform below, as a monument stands; a small building let into the hill (a hut, a house on a hillside) writes `site: cut`: levelled half-way, cut on the uphill side and filled on the
downhill, so it does not stand on a podium half its own height (today's ground and the terrain's exaggeration make every slope steeper than the ancient one):

- `ring`: seats or rooms round an open floor. Amphitheatres (`plan: oval`: the band of seats keeps one depth all round, so the arena is the narrower oval it is), theatres (`half`, `sweep_deg`, a `stage`), circuses and stadia (`u`, `obround`, a `spina`), round houses (`round`, `section: building`).
- `dome`: a round or polygonal building under a dome: rotundas, mausoleums, domed churches and mosques, baptisteries, stupas. A `base` block, a `drum`, the dome's `shape` (hemisphere, saucer, pointed, onion, bulbous, helmet, bell, cone), a `lantern`, an `oculus`, a `peristyle`; `sweep_deg: 180` is a half dome.
- `long_hall`: a long hall under one roof: temples (`colonnade`, `podium`), basilicas, churches and cathedrals (`aisles`, `transept`, `apse`, `buttresses` with `flying`), stoas, market and prayer halls, palace halls (`roof.flared`, `roof.eaves: 2`: East Asian roofs); roofs gabled, hipped, hip_gable, pyramidal, flat, vault, mansard.
- `column`: a tall shaft: obelisks and honorific columns (`taper`, `pedestal`), towers and keeps (`parapet`), minarets (`stages` with `balcony_m`), pagodas (`stages` with an `eave` each), lighthouses, shikharas (`top: shikhara`).
- `stepped`: a stepped platform or pyramid: pyramids (`tiers: 1, top: 0`), ziggurats, Mesoamerican platforms (`stair: {at: all}`), terraces on a round or polygonal plan (`slope: vertical`).
- `arches`: a wall of arches: triumphal arches and gates, aqueducts and arched bridges (`tiers`, `from`/`to`; a run over 120 m is laid in pieces, each on its own ground), arcades and loggias, iwans and great portals (`through: false`: deep recesses, dark at the back).
- `revolve` and `prism`: free solids for a form no class has: a section turned round an axis (a television tower, a bell-shaped stupa), an outline raised (a star fort, a building round its court: `holes_m`) or a section laid along (a vault).
- `parts`: several of these together, each placed (`at`, `theta_deg`, `z_m` above the whole's ground, or `atop` another part: a lantern on a dome, a spire on a tower) and copied (`repeat`: `mirror`, `ring`, `line`, `corners`); the parts may overlap, the model shows their union. A part on another stands on it with `atop`, never a `z_m` counted by hand: a dome keeps its true curve while the other heights are exaggerated, so a height added up from the sizes misses its top.

```yaml
landmarks:
  - kind: parts                     # a rotunda with a portico before it
    name: rotunda
    lon: 0.0                        # its centre
    lat: 0.0
    theta_deg: 0                    # turned counter-clockwise from east; at 0 its front faces south
    basis: research/<notes>.md, diameter and drum from the survey; the portico's columns estimated
    parts:
      - { kind: dome, d_m: 58, drum_h_m: 30, dome: { shape: saucer, rise_m: 14 }, oculus_m: 9 }
      - { kind: long_hall, at: [0, -38], w_m: 34, d_m: 16, h_m: 15, colonnade: { at: front, n_front: 8 }, roof: { shape: gabled, pitch_deg: 23 } }
  - kind: column                    # a minaret: a shaft, two balconies, a pointed cap
    lon: 0.0
    lat: 0.0
    basis: research/<notes>.md
    stages: [ { w_m: 3.8, h_m: 50, balcony_m: 1.2 }, { w_m: 3.2, h_m: 12, balcony_m: 1.0 } ]
    top: { shape: cone, h_m: 12 }
```

Every key, its range, its default and what it means: `uv run python -I pipeline/landmarks.py [kind]`, the same table compile checks against: a key a class does not have, a value
out of range, a missing size or a missing `basis` stops compile with what to write. Each size comes from the sources and `basis` says which are estimates; a size the sources do not
give is taken from a building of the same type and period (named in the research note), not a round number. Proportions that tell a wrong guess at once: a hemispherical dome rises
half its width, a pointed one about three quarters, an onion about one and a quarter times its drum's width; an Ottoman pencil minaret is about 19 times as tall as it is wide,
a square North African one about 5; a Gothic nave about 3 times as high as wide; an Egyptian pyramid rises 0.64 of its base, Mesoamerican ones 0.3–0.45; an amphitheatre's band of
seats is about as deep as its wall is high.

**A monument stands level:** a landmark of these classes is built on one level plane, on a platform where the ground falls away under it (like a house's lot, "A house stands on one
plane" in "No empty cities"); a long run of arches is the exception: its top runs straight from one end to the other and its arches reach down to the ground under them (a valley's
are the taller), never pieces stepping up and down with the ground. **Heights are exaggerated less the taller a landmark is:** the city's exaggeration makes a 6 m house read at the
film's scale, but a monument tall enough to read on its own keeps the proportions people know it by (stretched twice, a pyramid's 52° faces stand at 68°, a triumphal arch becomes a
tower), so a landmark of these classes takes the city's factor faded by its height, one factor for the whole of it (`exaggeration` sets its own: 1 for one drawn after a true
elevation); a dome keeps its true curve in any case (`dome.keep_curve`): stretched, a dome reads as an egg. Thin elements that carry a skyline (minarets, spires, masts)
are a few pixels wide at a kilometre and vanish in the wide shots; look at the period city's wide still (eraview) and say so when the film relies on one.

**Look before laying the city:** `modelview --sheet` builds every landmark of these classes the period declares, each from four sides at a distance that fits its size, beside its
house types, and puts the stills in `sheet.jpg`; show the user the sheet. **Not drawn yet** (say so rather than stand in a solid): open frames of thin members (iron towers,
gasholder frames, truss bridges: a solid shape reads as an obelisk), buildings below the ground (rock-hewn churches, stepwells), helical ramps (a stepped cone stands in), ribs and
flutes on domes and shafts. A form the classes cannot make is added to them, as a key of a class (its line in `FIELDS` and its drawing) or a new class, never as code in a city.

## Boundaries, overlay and change

**A part of a city lost while the rest stands** (`lose:` in the period city): a fire that takes some quarters, a city shrinking to its core, a lake drained for a new
building. Do not take the whole city away and raise a smaller one in its place: what stood through the change would sink and rise again, and the audience reads a city
destroyed and rebuilt. A loss names what it takes as a stage does (`select` by id or group; every part when absent, trees only when named), inside its `region` and outside
its `keep` (a ring of `[lon, lat]`, several, or `osm:<name>`; or `{landmarks: [ids], .., region: ring}`: the parts it names stand whatever the region), and when: `at` in the city's own node (seconds or `{with: <line>}`), or `{node: <id>, at: ...}` in a later
node while the city still stands (`until`). `style: sink` (the default) or `burn` (the part catches fire for `burn` seconds first); `ring: in` (from outside toward `from`,
the default: a city shrinking to its core) or `out` (from `from` outward: a fire spreading); `dur` seconds. Each building goes whole as the ring passes it; the rest does
not move. A street, lane or wall that the select does not name one by one runs on past the region: only its stretch inside goes, not all or none of it by where its middle falls. compile refuses a part lost before it has risen, after the city is taken back, in two losses, or a loss that takes nothing; at most sixteen per city. A city laid later
over the old one (`avoid_eras`) may build where a part was lost by its node (fields where houses were: a `trees` region there); clipcheck counts a lost part and what rises
where it stood as never standing together. **A landmark built later where houses stood** (a forum cut through a quarter, a palace raised on a burnt one) is named in the
loss that clears its ground (`for: [<id>]`): citygen lays the houses over its site instead of leaving it empty from the city's start, the loss takes every building on
the site (the ground citygen would have kept clear; with a `region`, that too), and compile stops when the landmark's stage starts before they are gone. Such a landmark goes later only by a loss that names it in its `select` (a lake drained before the arena on its ground: the arena waits for the water too). Trees on the site stay unless a loss names them, and the houses there do not keep a tree out, so the new precinct's garden is planted where they stood; clipcheck counts a tree that rises before the house under it is gone. Without `for`
a landmark's site is empty from the start, which is right only for what stood there before the houses. The city's outline and the ground where today's buildings stepped aside stay as they were (a shrunken city's walls usually stand).
**How many period cities:** as many as the history has. At most eight stand or are drawn (a ghost outline) at the same moment, each lighting one channel (where today's buildings
step aside, its front and its edge); cities apart in time share a channel, and compile says which (`era channels`) or stops at a ninth at once.

The boundary is computed automatically from the generated buildings; for a boundary the buildings cannot give (a village moat) add `outline:`, and the footprints of the historic cities at the end are also drawn from it;
a city laid over the previous period writes `avoid_eras: [<id>]`, so the new quarters go around the old city. Walls, elevated corridors and street surfaces on slopes tilt with the slope (citygen `lay`); do not make them into steps segment by segment.
The later period must show change: a new city laid over the previous one must differ clearly in scale or layout (adding a few small courtyards does not count), enlarged according to the sources; the old city stays underneath, and after the colour change use a wide shot first
so that the audience sees the new city grow around the old one, then move closer (example: Xianyang's imperial capital follows the 《史記》 (Records of the Grand Historian): the palaces of the six states
line up along the north slope, and the new quarters of 120,000 households surround the old city).

## No empty cities

**No empty cities:** restore the period cities from drawings as far as possible (archaeological plan → reconstruction drawing or model → film and TV set → imagination by the custom of the same period), and label each item with its basis (excavation / documents / film and TV / imagination);
whatever is not excavated is labelled "schematic". Do not leave large empty spaces inside a palace city or inside walls (except ponds, gardens, squares, fields); fill the areas with no data by custom or by film layout.
An open space that is kept is drawn as what it is: a garden, park or grove as trees over the whole area (`trees: [{region: [[lon, lat], ...]}]`, about `step_m` 16 apart, scattered rather than in rows, never on a street or in a building; a region is one ring or a list of rings, where a ring inside the first is a hole in it (a court or a pond left open) and a ring apart from it another area (several gardens, as a loss's region lists them), and a ring crossing the first is refused; `[[ring, hole], [ring], ..]` groups them; for trees, grounds and fabric alike); left as bare plate inside a built-up city it reads as a lake.
Open ground (a field, a yard, a works or parade ground, a sports ground, the lawn under a garden's trees) is a ground: `grounds: [{id, region, surface: earth | grass | gravel | paved}]`. The plate takes that surface while the city stands, under its light and following the terrain exactly (earth as the streets' rammed earth, paved as an asphalt road, grass darker, gravel lighter); houses, streets and trees stand on it, and water is drawn over it; a platform a lot or a court stands on takes the surface where it lies inside (its court, its apron), as a court's trees stand on its top.
A ground is open space, not the ground under a built-up quarter: the lanes, yards and courts between the houses of a quarter stay the dark plate, the figure and ground a city is read by from near and far; a quarter laid on one ground reads as a plaster slab with its houses lost on it (compile warns when houses cover more than a quarter of a ground). Huts standing apart on a village's earth are on a ground; an open space wider than a few lots inside a city (a square, a garden, a vacant block) is one.
A later ground in the list is laid over an earlier one (a yard written after its field cuts its place out of it); each period city keeps its own, so one place can be a field in one period and a lawn in the next.
Stages and losses name a ground by `id` or `group` as any part (a loss takes a ground only when it names it: open ground outlives the houses round it); the grounds and pools of one film share 32 slots, so grounds of one city that come and go together are one entry whose region has several rings.
A region may cover a building with a court (a portico, a cloister: the court is planted, the walls are not) and a court on a platform (its trees stand on the platform's top); a garden is part of the city's outline.
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
**Lay out blocks from an old map or an archaeological plan** (`city.trace`): register the picture and trace on it with `pipeline/register.py`, never with conversions of your own
(written by hand they mirrored pictures, took 111,320 m a degree everywhere and read projected rasters as lon/lat). A GeoTIFF carries its registration; a figure without one is fitted
to control points read off it (`{image, controls: [{id, pixel, lonlat}], method: similarity | affine}`: each point's residual and its error when left out are printed, a mirrored fit
is refused), a plan with a scale bar to one known point (`{image, origin, m_per_px, north_deg}`). Read the walls (polygons), streets (lines), blocks (polygons) and landmarks (points or
polygons) off it as pixels in a YAML (`id`, `kind`, `pixels`, the entry's keys, and `provenance: {basis, ...}`), then `uv run python -I pipeline/register.py trace cities/<slug> <file.yaml>
--overlay <png>` writes the GeoJSON in `research/` and draws it back over the picture: look at the overlay before building. `kind` is wall, street, block or landmark, and the other
properties are the settings of that item (`lot`, `typ`, `w_m`, `shops`, the landmark's `type`…); `provenance` rides along and the model ignores it. In Python, `register.outline_landmark`
makes a traced outline a prism of the classes and `register.fit_circle` measures a rim (QGIS's georeferencer is fine where it can be used). **The houses of a quarter between its traced
streets** are laid by `uv run python -I tools/parcels.py cities/<slug> <parcels.yaml>`, never by a packer of your own: from the built-up ground less landmark sites, gardens, water,
walls and shop rows, it cuts blocks along the streets, splits a large block by a bent lane, fills each with whole courtyard houses turned to their street and rows of
shop-houses along the fronts, and writes them as a trace with a report (lot sizes, bearings, the share built, the ground left); the types, sizes and storeys are the city's research. Houses in a block line up along the block's
own long side, not the city-wide grid (`traced` in `pipeline/citygen.py`).
What is traced is built together with what is written in `city:`, and the two can be mixed; the first time, show the user a small piece first. A layout worked out beside the
model (lots, streets, gardens or a loss's region laid round landmarks) takes each landmark's ground from `citygen.landmark_site`, the ground citygen itself keeps clear, never a box of
its own round the anchor (that put houses on one side of a temple's platform).
**Shops along a street** form a row wall to wall, of similar height, with a back yard behind each shop body and the yard walls joined in one line (with gaps between shops, uneven heights and open backs, a row looks like a row of teeth when seen obliquely from behind). Not built yet: houses on steep slopes lined up along contour lines (see "Ground and terrain").
clipcheck's `paving_under` checks whether the paving and yards are covered by the plate (more than 0.3 m counts), and it must be 0. A new quarter needs streets and lanes (`streets`, `lanes: {region}`); it cannot be only a field of houses.

## Appearance and height

**The dark room is the brightness ratio between the subject and the plate, not how black the plate is:** lift the plate with a blue tint, make the lit faces of the white model bright, and make the ring of light and the buildings of the current period the brightest,
most saturated small areas in the picture; lift the mid-tones with a curve and leave the black level alone; do not raise the whole thing to grey. On a phone in bright surroundings the dark parts smear together, and platform compression hurts dark gradients most.
For thresholds and how to measure, see CHECKS.md "Brightness".
Dark plate (`palette.plate/plateSide/water/plateEmit`), ivory model, edge lines (`film.edges`). Water (rivers, draped and dug pools, moats) is told from the
ground by how it moves, not by its colour alone: it is darker than `palette.water` and glossy, fine ripples run across it with the wind and carry the room's light,
a thin lit line follows its shore, and small glints flare on it now and then; the ripples and glints that would be finer than a pixel or two are left out, so a wide
shot shows a still, sheened surface and a close one a moving one (engine/studio.js waterSlope, waterGlint). Three separate height exaggerations: `terrain.exaggeration` (terrain),
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
**A pool is a dug basin** (`kind: pool`): its water stands at the lowest point of its rim, and the plate inside it is lowered below the water while it stands
(back when it is taken back or lost), so a lake on uneven ground is water from bank to bank. Pools that touch (an L-shaped lake drawn as two) share one level.
When today's ground rises more than `banks_m` (6 m) round a pool, compile stops: dug there it would stand in a pit, and the place or the size is usually wrong
(today's ground is not the ancient one; a pool drawn across the foot of a hill); move it within what its source allows, and say so in its note, or, for a basin
truly cut that deep, write `banks_m` with its basis. When the source fixes the place and today's ground still rises across it (the ancient ground is lost:
a valley filled, a hillside cut back), write `level: draped`: the plate itself is its water while it stands (as today's rivers are drawn), showing where it
was and not how high it stood; label it schematic on screen. Its water's edge is its outline exactly as drawn (compile keeps the distance to it in the pool map,
so it is smooth at any size and does not step with the map's texels), so the outline is what the audience sees: trace it from the source's plan, not a box round it. Today's buildings step aside from its whole outline as it rises; a loss's ring spans its outline (any pool's)
and takes its water point by point as it passes. clipcheck's `water_under_plate` finds water the ground rises through (a ditch on a slope).
**Today's buildings stand on the lowest ground under them:** `prep.py` puts each building's base on the lowest point of the plate under its footprint (the plate as the engine draws it, `terrainio.plate_mesh`)
and its top where its height puts it above the ground at its centroid, so a building on a slope reaches down to the ground on its downhill side instead of hanging in the air.
clipcheck's `today floating` counts any building that does not, which is how a model prepared on an older terrain shows: after `terrain.py`, run `prep.py` again.
**Terrain is exaggerated at two scales** (`terrain.detail: { below_m: 150, exaggeration: 1 }`, the default): large terrain such as plateaus, terraces and river valleys is exaggerated by `terrain.exaggeration`;
small relief below 150 m keeps its original height (×1). Copernicus GLO-30 is a surface model and measures today's roofs and treetops, and most of the small relief in a city is those;
exaggerating them by the large-terrain factor (for example ×6) makes 4 m of relief 24 m on screen, much taller than a 5 m dwelling, and the ancient city looks as if built on a heap of rubble. The true terrain is stored separately as `terrain_true16.png`;
take from it anything that prints metres (sections). After changing, rerun `pipeline/terrain.py` and `pipeline/prep.py`, then compile.
The two scales have a cost: steep scarps narrower than `below_m` (plateau edges, river banks) are flattened too, so the drop drawn at the foot of a landmark on a slope gets larger; changing `below_m` only moves the problem to another city.
After the change, look at clipcheck's `tall_foundation`, then take a close-up still of the landmarks on slopes (`tools/modelview.py`).
**Hills on the plate:** the plate is dark and the room light is high, so a hill reads only where light rakes across it; when the story stands on hills (the list below is not empty), write
`terrain.shade: { k: 1 }`: one fixed low sun (default `az: 325, el: 25`, from the north-west; the room light turns with the camera, this sun stays put): a slope turned to it is lit in the plate's own hue
(a steel blue on a dark blue plate), a slope turned away darker, flat ground and water keep the plate's colour. Never a white light: white added on the dark plate read as snow lying on the hills.
It needs only compile; `k` from 0 to 2; `col` changes its hue (the plate's colour unless written). `tools/modelview.py` looks across this light by default.
**Before touching the terrain** (exaggeration, scale, bare earth), list the landmarks that the sources name and that stand on a slope (terraces, plinths, palaces built along the slope), and after the change compare their heights on screen one by one
with the numbers in the narration (example: when the narration says "built on a high terrace", the picture must show it standing on a high terrace).
**Distant terrain:** when a mountain or water the story needs is outside the plate (Xianyang: Mount Jiuzong, the origin of the city's name, is 23 km outside the plate), do not enlarge the plate (the city would shrink and look empty); use
`terrain.context`: terrain only, the same colour as the plate, fading into darkness at the edge; next to the plate it uses the plate's height exaggeration and farther away drops to `exaggeration_far`
(with the plate's exaggeration a mountain becomes a wall; Xianyang's plate is ×3, the far terrain 2.5), and the readout must state the exaggeration. The grid must be fine enough to show ridges (at 150 m Xianyang's Mount Jiuzong was ground down to a dune; at 60 m it appears),
and the extent covers only the stretch from the plate to that mountain; `shade: { az, el, k }` is one fixed low-angle side light that lights only the slopes facing the light (flat ground keeps the plate's dark colour,
and lighting everything would look like snowfield): without it, distant mountains in the plate's colour are almost invisible against the night sky. After adding or changing `terrain.context`, rerun `pipeline/terrain.py`. Show it only in the nodes that need it (the `context` keyframe); a pin standing on it may appear only while it is shown (compile blocks it).
**Before measuring, confirm which copy you are measuring:** one thing often has several copies (terrain has the 8-bit `terrain.png`, the 16-bit `terrain16.png` and `terrain_true16.png`; the engine reads the 16-bit one).

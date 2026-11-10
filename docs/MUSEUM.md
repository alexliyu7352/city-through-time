# Museum pages and the old cities to walk round

Two pages beside the film, for the city's web bundle (PUBLISH.md): the old cities to walk round, and a museum page for one building.
They show the film's own models, but they are not the film: no timeline, no film camera, no lens.

## The most common mistakes in this step

- A museum page with the film's look (dark room, era colour, depth of field) → a bright neutral room, everything sharp: the page is for seeing the building, not for its mood.
- A part shown as known that the sources only guess at (a roof form, a stair's place, the half that was never dug) → every part is sourced or estimated, and an unclear one is estimated ("Parts").
- A picture whose roofs and walls do not sit on the model, or a viewpoint moved after its picture was made → look at the `sheet` before using it; tools/museum.py drops a picture whose viewpoint moved.
- Two viewpoints close together → 50 degrees or more apart: one picture shows at a time.
- A still with the ground ending in a hard edge → the image tool paints the edge as a cliff or a plateau; the stand fades out toward the
  horizon in every still (engine/museum.js), the prompt says the ground runs on.
- The walk-round view loading the whole film (about 100 MB, today's city, footage, fonts) → it loads the plate and one hall's cities.
- Museum pages built but the site shows none → the site reads them from the web bundle: tools/museum.py, then tools/web.py, then publish the bundle.

## Walking the old cities

`play.html?city=<slug>&view&free` (with `&bundle=` on the site): the viewer's public mode (engine/view.js). One period at a time, chosen like a hall
(`&era=<id>`, else the period of the city's first museum page, else its last: the cities standing at its moment, an imperial
capital over the city it grew from), in the film's look but sharp, the whole window, mouse and touch, down to an eye a few metres over the streets; `&cam=tx,ty,tz,az,el,d` where to stand. It loads only the plate
(`build/museum/plate.json`: the model without today's buildings, written by tools/museum.py) and each hall's period cities when the hall
is chosen: a phone can open it. A landmark that has a museum page carries the film's pin (engine/overlay.js: a dot on the building's top,
a pole up to its name) while seen from above or near; the pin and the building open the page in the same tab, which leads back to the same
hall and the same place (`&era`, `&from`): one tab is easier to follow on a phone than two.

## Where visitors find them

The site (site/app.js) offers both on a city's panel when the city has a web bundle: a link to the walk-round view, and a line of the
museum pages listed in the bundle's `build/museum/index.json` (read when the panel opens; a bundle without one shows none). The film
player's bar (`&play`) links to the walk-round view at the latest period the film has come to. Each opens in a new tab, as the player
does, so the site or the film stays where it was. The site finds museum pages only in the bundle: run tools/museum.py before
tools/web.py packs it (PUBLISH.md).

## A museum page

`museum.html?city=<slug>&id=<page>` shows one landmark of a period city as a model of its own: at the heights it was built to (the film
stretches heights so a city reads at its scale; a museum model does not), on a flat stand, in a bright neutral room, turned and zoomed
freely. It is written in `cities/<slug>/museum/<page>.yaml` (Xianyang's `qin_palace1.yaml` is the example) and built by
`uv run python -I tools/museum.py cities/<slug>` into `build/museum/` (the model, a few tens of kilobytes, and the pictures as the page loads them).

- **The building:** `node` and `landmark` (its kind and place, as in city.yaml) name it; the model is the film's generator run for it alone
  on level ground, `exaggeration: 1`, or its detailed model ("Detailed models" below). A generator labels the sections it draws (citygen
  `Builder.labelled`); a kind with no labels is one part.
  A building the film tells over more than one period (a theatre in one city, the hall where a ruler was killed in the next) is one
  page of `pieces`: `[{id, node, landmark}]`, each landmark found in its own node's city and built where the film puts it, all on one
  stand round the first piece's place (`at_m` and `stage_m` are measured from there; make the stand cover every piece). `node` then
  names the period whose hall the page belongs to. A piece's records are labelled with its id first (`curia/hall`), so a part takes
  them by piece (`labels: [curia/*]`). List the pieces the page shows: two nodes that both carry the same building at one place give
  it twice. Two periods' models are traced apart, and a piece can stand out of line with the others (a theatre
  30 m off the axis of the portico behind its stage): the page sets it where the sources put it, `move_m: [east, north]` and
  `turn_deg` about its own place with `why: {zh, en}`, and says so on the page; the film and city.yaml keep their own.
- **Parts:** each record goes to the first part whose `labels` (fnmatch on the label path, `west/platform`) and `kinds` (`roof`) take it;
  a record no part takes stops the build. Each part has `status: sourced` (an excavation report, or a text relaying one, says so) or
  `estimated` (a reconstruction, a mirror of the half that was dug, a guess), a short `note` in the page's languages saying what the sources
  say and what the model guesses, and `cite` (codes of `sources`). The visitor sees the two in two tones and clicks a part for its note.
- **The label:** what the building was, what we know and how (who dug it, what report, what we could not read), and the model's own
  choices; then life in that time, from the finds and the film's pictures of the period with their labels. Plain words; every fact from
  the research notes and FACTS.md, with its `cite`.
- **Viewpoints:** three or four cameras round the building (`az`, `el`, `d_m`, `fov`, `at_m`), 50 degrees or more apart, one `main` (the
  page opens there). Each gets an imagined picture made as a living moment's is (STAGING.md "Living moments"): its scene card
  `research/museum/<page>/<viewpoint>.yaml`, then `uv run python -I tools/living.py ref|gen|sheet cities/<slug> <page>/<viewpoint>` (the
  still is the page's model alone at that camera, `node tools/museum.mjs still`). The picture is exact only from its own camera: the page
  shows it full within 10 degrees of it and none past 25 (and as the distance leaves it), and only on what that camera sees (a
  wall's far side or the floor behind it takes none of it: engine/studio.js projDepth), it comes back near any viewpoint by itself, and
  while it shows a label says it is an AI reconstruction from the sources. The page opens on the main picture as a plain image and the
  model takes over on the same camera, so the visitor sees the picture at once.
- **Languages:** Chinese as the film writes it (`zh`), Traditional Chinese for Taiwan and English (`&lang=zh-Hans|zh-Hant|en`). The
  `zh-Hant` texts are converted, not written: `uv run --with opencc python -I tools/hant.py cities/<slug>` (OpenCC s2twp) writes every zh text
  of the pages and the periods' names into `museum/zh-Hant.yaml`; read it through (OpenCC can take a historical word for a modern one: 谷道
  became 穀道, 镜像 映象, 陕西历史 陝西曆史) and correct it there, where a correction stays. tools/museum.py stops on a zh text without one.
- **The way back:** a museum page opened from the walk-round view returns to it on the same hall, where the visitor stood; opened on its
  own, to its building's hall, looking at it.
- **Publishable only:** the page ships the model, its pictures and the life pictures, small; never a non-CC picture, a reference drawing
  or an internal plate. The pictures are AI-generated: list them in CREDITS with their date and tool.
- **Check:** `node tools/museum.mjs shots <slug> <page>` (desktop and phone: the main picture, turned 5, 15 and 30 degrees, the two tones,
  a part's note); look at each at full size.

## Detailed models

The film's generator draws a landmark as massing: right at a city's scale, plain on a page where the visitor stands at its foot (an
amphitheatre as one ring with dark rectangles for its arches). A page can draw the landmark, or one of its pieces, from a detailed
model made in Blender instead: `detailed: {kind, spec}` beside `landmark` (or in the piece). The film keeps the generator's.

- **Kinds:** a kind is a module of `tools/blender/` (`amphitheatre`: an oval of arcaded storeys with their orders, the attic, the
  seating in bands, the arena wall), built with `tools/blender/kit.py` (profiles swept round a plan curve, arched bays, columns).
  It takes the sizes the film gives the landmark (its `from_landmark`: for an amphitheatre `outer_m`, `inner_m`, `h_m`, `bays`,
  `arena_wall_m`), then the page's `spec` over them; what neither gives is the module's `DEFAULT`, an estimate, and the part it
  shapes says so in its note. A building of another type is a new module (`DEFAULT`, `from_landmark(L)`, `build(spec)` returning one
  object per part), listed in `tools/blender/build.py` `KINDS`.
- **Parts:** the model's objects, by name (an amphitheatre's: `facade_arcades`, `orders`, `attic`, `cavea`, `podium`, `arena`), are
  taken by `labels` as records are, a piece's with its id first (`theatre/cavea`); `kinds` take records only.
- **Building it:** `tools/museum.py` runs Blender headless (local/config.json `blender`, docs/SETUP.md; a second or two) and writes
  `build/museum/<page>/<piece or model>.glb`, Draco-compressed (an amphitheatre of 182,000 triangles is under 1 MB), turned and placed
  as the generator places the landmark. The page draws it with the white model's material: the tones, the picking and the pictures
  lie on it as on records. To look at a kind alone: `<blender> -b --factory-startup --python tools/blender/build.py -- --kind <kind>
  --out <file>.glb --render <file>.png --cam az,el,d,fov,tx,ty,tz` (a still in Blender's own renderer, the page's light).
- **Pictures:** a picture is made for one model. Its record keeps the model's fingerprint (tools/living.py), and tools/museum.py uses
  it only on that model: a page turned to its detailed model drops the pictures made from the generator's, to be made again from the
  new still (`tools/living.py ref`, then `gen`).

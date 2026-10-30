# Museum pages and the old cities to walk round

Two pages beside the film, for the city's web bundle (PUBLISH.md): the old cities to walk round, and a museum page for one building.
They show the film's own models, but they are not the film: no timeline, no film camera, no lens.

## The most common mistakes in this step

- A museum page with the film's look (dark room, era colour, depth of field) → a bright neutral room, everything sharp: the page is for seeing the building, not for its mood.
- A part shown as known that the sources only guess at (a roof form, a stair's place, the half that was never dug) → every part is sourced or estimated, and an unclear one is estimated ("Parts").
- A picture whose roofs and walls do not sit on the model, or a viewpoint moved after its picture was made → look at the `sheet` before using it; tools/museum.py drops a picture whose viewpoint moved.
- Two viewpoints close together → 50 degrees or more apart: one picture shows at a time.

## Walking the old cities

`play.html?city=<slug>&view&free` (with `&bundle=` on the site): the viewer's public mode (engine/view.js). One period at a time, chosen like a hall
(`&era=<id>`: the cities standing at its moment, an imperial capital over the city it grew from), in the film's look but sharp, the whole window,
mouse and touch, down to an eye a few metres over the streets. A landmark that has a museum page is marked, and opens it.

## A museum page

`museum.html?city=<slug>&id=<page>` shows one landmark of a period city as a model of its own: at the heights it was built to (the film
stretches heights so a city reads at its scale; a museum model does not), on a flat stand, in a bright neutral room, turned and zoomed
freely. It is written in `cities/<slug>/museum/<page>.yaml` (Xianyang's `qin_palace1.yaml` is the example) and built by
`uv run python -I tools/museum.py cities/<slug>` into `build/museum/` (the model, a few tens of kilobytes, and the pictures as the page loads them).

- **The building:** `node` and `landmark` (its kind and place, as in city.yaml) name it; the model is the film's generator run for it alone
  on level ground, `exaggeration: 1`. A generator labels the sections it draws (citygen `Builder.labelled`); a kind with no labels is one part.
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
  shows it full within 10 degrees of it and none past 25 (and as the distance leaves it), it comes back near any viewpoint by itself, and
  while it shows a label says it is an AI reconstruction from the sources. The page opens on the main picture as a plain image and the
  model takes over on the same camera, so the visitor sees the picture at once.
- **Publishable only:** the page ships the model, its pictures and the life pictures, small; never a non-CC picture, a reference drawing
  or an internal plate. The pictures are AI-generated: list them in CREDITS with their date and tool.
- **Check:** `node tools/museum.mjs shots <slug> <page>` (desktop and phone: the main picture, turned 15 and 30 degrees, the two tones,
  a part's note); look at each at full size.

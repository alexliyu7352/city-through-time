# Staging grammar (every city must follow it)

Follow it when making a new city; do not reinvent it. Settings keys and the tools that check them are in parentheses.
The goal is international, artistic, modern moving images, not a data chart: one running visual motif, a restrained colour logic, big numerals, white space, a continuous camera that always has a reason,
sound and light in sync. The white-model projection is only a starting point, not a ceiling; where nothing is written below, use this standard on your own, then show the user.

## The most common mistakes in this step

- The whole city changes colour at once, changes happen off camera, a whole area pops up at once, the camera cuts hard → rules 1–9.
- Non-CC pictures and videos get mixed into the preview shown to the user → on screen use only CC, public domain or the user's own material; if there is none, use a labelled imagined picture ("Footage and pictures").

## Basic grammar

Today's white-model city is there from start to finish (`rise.ghost: 1`); each node tints the whole city with that node's colour (node `tint`); a period city replaces that piece of today's city in place
(today's buildings sink with a ring of light spreading from the origin, and the old city rises); moving a capital, moving house, river changes and distances use light lines (`routes:`, `[km]` fills in the distance automatically).
While a period city stands, today's city keeps about a fifth of its light (`era_look.dim: 0.8`): the period city is the figure, and in the later periods today's city is dense and tall around a small old town (at half its light it took the frame).
A city that rises in stages stands once its first stage is up, so a landmark built later in the node does not keep today's city bright, and the city unlit, until it rises.
The plate is a deep blue, not black (`palette.plate`, Xianyang `#3a4757`): in a wide shot most of the frame is plate, so the plate sets how dark the film feels.
The events with the most room need a close, brightly lit camera with the subject filling the frame, not only dark wide shots (for the brightness threshold see CHECKS.md "Brightness").
No hard cuts between nodes: do not write the next node's first camera keyframe at t 0 (let the camera fly from the last position of the previous node), and a node that changes colour needs a wide shot in which the whole city can be seen.

## Rules

1. **Ring expanding = change inside the ring; ring contracting = change outside the ring.** When a new period's city grows from a point, the ring (or a band of light sweeping along a line) follows the growing front
   (`city.stages`: `from` radiates, `sweep` sweeps a line). When a city is taken back, the old city sinks wherever the contracting ring has swept and today's city returns (`fall: in`, burning or demolishing a city);
   when it is replaced by the next node, it is taken back along with the next node's colour-change ring (`fall: out`, the default). **An expanding ring always runs out of the picture before it disappears:** the city's ring keeps accelerating outward after the last
   building, until the whole ring is outside the picture (compile's `stagecraft.ring_exit`: the farthest ground visible at the picture edge) and only then fades out; it must not stop and go out in the middle of the picture.
2. **While change happens, only the ring glows.** Do not light whole plots; once the city has settled, a thin neon line lights up at its outer edge, lighting only the buildings beside the line (`era_look.line/light_m/halo_m`),
   and this line goes out first when a change begins.
3. **Every big node gets a clearly different colour, and everything the ring sweeps over turns into this colour, including the old city still standing.** The colours of two adjacent nodes must not be close (orange and gold cannot be told apart);
   better still if the colour has a source (after the Qin unification "上黑" (honouring black) → the imperial capital uses ink-gold: `ink`). The old city in later nodes uses that node's colour and strength (node `tint`).
4. **Change happens only where the audience can see it.** If a beam points at the new city, wait for the beam to land before it grows; with no beam, wait until the camera has arrived. A hand-written `at` is only "the earliest":
   if the camera has not settled it moves later automatically (9a). **The node's colour-change ring is sent only when the change begins**, from the start of the change (the beam's landing point or the city's origin); when the city draws its own ring, the node ring
   does not draw a second front (two stacked at one point turn into a disc of light); if no visible change is inside the ring, it is not drawn. Today's city dimming also follows the ring (outside the ring it stays as it was).
   camcheck's `offscreen` and `ring_unseen` must be 0.
5. **Buildings grow one by one, each as a whole.** A whole area must not pop up at once; use stages (`stages`, example: the palaces of the six states from west to east, new quarters around the old city), 1–1.5 seconds per building (`grow`).
   **The first change of a node happens right at the start of the node** (picture first, subtitle after): do not push it later to wait for a subtitle. A node may have more than one change,
   and the later ones follow the subtitle that tells them and are staged separately; do not merge them into the first. Example, Xianyang's imperial capital has two: ① the imperial capital is established (happens on entering the node: the colour-change ring dyes the Qin capital into the imperial capital, and the palaces south of the Wei,
   Epang and the Heng Bridge grow), ② after the states were destroyed, the palaces of the six states are rebuilt and the rich households are moved to build a new city (with 「那時，每滅一國」 ("then, every time a state was destroyed") and 「十二萬戶」 ("120,000 households")).
   **A city can have only one stage growing at a time:** the engine draws one growth light per city; if two stages grow at once, the buildings of the second pop up without a band of light.
   To grow together, merge them into one stage (example: the palaces of the six states and the new quarters use the same west-to-east beam); compile reports an error when two stages of the same city overlap in time.
   The growth ring by default spreads from the city's origin (`origin`), and the camera must be able to see the origin; a stage far from the origin (example: south of the Wei) must write `from` to spread from its own place,
   otherwise the planner waits until the camera returns to the origin before it lets it grow.
5b. **Pictures must not cover a change that is happening.** What counts is the screen, not the time:
   - A full-frame video (`mode: full`) covers the whole picture. The 3D clock does not stop (the preview just does not draw 3D under the video), so the covered time counts as "the camera is not looking":
     city growth automatically waits until the video ends (compile's `covered`).
     Changes that span the whole picture (colour-change ring, satellite transition, area lighting) do not wait by themselves, and compile blocks them.
   - A half-screen picture (`mode: panel`, the right 64%) may coincide with a change as long as the change happens on the left of the picture and no more than a third is covered (compile checks by projection every 0.25 seconds).
     Changes that span the whole picture (the node's colour-change ring, the growth wave of modern buildings, the satellite transition, area lighting) count as covered.
   - When covered, in order: compose the shot so the change falls on the left → move the picture to after the change ends within the same narration (example: the picture of Shang Yang's construction is moved to after the Qin capital has finished growing, matched with 「宫殿筑在渭北的高台上」 ("the palaces were built on the high terraces north of the Wei"))
     → turn it into a small card (`card`, not restricted; example: the picture of Xiang Yu burning the palaces, followed by 「如今只剩一片田野」 ("now only fields are left"); delayed, it would not match).
     A half-screen picture works better than a small card, so use it where possible.
   - Do not lengthen a node to place a picture, or leave a gap in the narration; pace comes first. A document card (`doc`) on the right must not cover the part that is growing.
   - The small card, half-screen picture, section and document card on the right share the same place: put only one at a time, each aligned with the line that speaks of it, and judge by screenshot.
     Example: a photo of the Han Changling tomb and the section of the north slope appeared together and their two titles overlapped; changed so the photo goes with 「帝王的長眠之地」 ("the resting place of emperors") and the section with 「比河谷高出約90米」 ("about 90 m above the river valley").
   - What compile does automatically: when a half-screen picture covers a change, it is delayed until the change ends, but not out of its line (the line it follows, or the line being spoken when it appears); if it cannot be delayed in, it reports an error.
     Some scenes do not matter when covered; write `force: true` on that picture: it is shown at the original time, with a single line of notice.
5c. **No dead air** (compile blocks it, `build/logs/deadair.txt`): ① more than 3 seconds with nothing (no text, the model unchanged, no picture, the camera almost still); ② more than 5 seconds between two lines with "nothing to read":
   deliberate silence (`quiet`, `pause`), pictures with captions (footage, photos, cards, sections), and the way flying to the next station all count as having something, and the rest counts as empty. A common cause: the planner inserted a hold in the middle of a line, and the next line was pushed to after the hold.
   Fixes: let the next line follow on, have the line that speaks of a picture use `with:` that picture and adjust `lead`, shorten the node's tail or the hold, or state `pause` explicitly (example: 4 seconds after the last line before the lights go out).
   A node with much picture and little text (Xianyang's Han: 7 lines in 64 seconds) should spread the gaps to 3–5 seconds between every two lines, not gather them into one 10-second stretch.
5d. **The source note in the readout column decides how short a station can be** (readcheck): the note must be read through (Chinese 4.5 characters per second, plus 1.5 seconds), and a station that is too short does not allow it.
   Before shortening a station, look at its note; to make it short, simplify the note (on-screen text, ask the user).
   The same goes for tags: a tag can be read only as long as the camera stays there (example: a close-up that holds only 1.8 seconds cannot be read through by an English tag).
6. **Burning and demolishing a city:** the ring spreads and dyes the inside deep red, then fire starts (three tenths of the buildings burn, the rest are charred, the fire moves through the city), then the ring contracts toward the fire's origin, and the city sinks wherever it has passed.
   The contracting ring must be easy to see: it sweeps in from outside the picture for 2 seconds (`timing.contract_in`), then contracts for 5 seconds or more inside the picture (the city's `sink` is the two parts together, Xianyang 7.5 seconds),
   and only when it has finished does the line "如今……" ("now …") follow. A city that is burned or demolished (`fall: in`) must fall as soon as the contracting ring passes: write `fall_dur` 0.25 (the default 1.4 is for a city taken back along with the colour-change ring),
   and the falling buildings go dark together with their self-illumination, otherwise the ring has already swept past and the houses are still standing outside it (Xianyang: both burned cities, the Qin capital and the imperial capital, use 0.25). Sparks must be visible: draw them at actual size (thin bright lines about 40 m long, a few pixels at 10 km, no more than 11 pixels close up, never big round dots), and a quarter of them are embers that drift higher and last longer.
7. **Modern year-by-year growth:** the ring first takes back the buildings newer than the starting year (`reset: { year }`), then they grow back one by one with the years, always white (`grow.mono`).
   Each building grows at the moment the year counter first reaches its year (1.8 seconds; compile gives the engine the year line `grow.yl`), flashes, and stays warm for `grow.warm` seconds (Xianyang 4 seconds),
   with the front of growth continuously visible all the way; do not pop up in a cluster of two or three seconds by era (clustered popping with long stretches of no growth looks like nothing is growing).
   **Buildings grow only when they are in the picture:** if the camera is not looking at it when the year arrives, wait until it first enters the picture (time covered by full-screen footage does not count) before it grows; a batch entering the picture together
   grows within a few seconds in order of year (2 seconds per thousand buildings, at least 2 seconds, at most 12 seconds: `see_*` in compile's `TIMING`). compile writes the buildings that have to wait into `data/grow_t.json`, and the rest grow with the year.
   Key places use only one warm yellow light (`epochs:`).
   The camera rises from above the old town and pulls out to an oblique overview; do not squeeze everything together with a telephoto, and do not look straight down so that the city becomes small dots.
   **Building data must have no large blank areas:** where the main data (CMAB) is missing (villages and towns, some new towns), fill with Overture building outlines (`buildings.fill: overture_ghsl`,
   filled only where no main-data building lies within `fill_gap_m`, the year taken from the GHSL built-up area and labelled estimate; licences OSM ODbL + Shi et al. 2023 CC BY 4.0).
8. **A city history's unique idea deserves a scene** (Qin Xianyang's 「法天象地」 ("modelling heaven and earth")): `sky:` night colour, star groups drawn in the corresponding places in subtitle order, one pair of names per group, a single pale colour, thin lines, restrained.
   The rhythm of this scene is composed: the algorithm inserts no hold or move closer during `sky` (as with beam following, this stretch belongs to itself).
   For a unique idea in the city's history (example: Qin Xianyang's 「法天象地」) use the node's `sky:`: night colour covers the city, and star groups are drawn on the city in subtitle order (`enclosure` wall, `band` Heavenly River,
   `asterism` star group, `line` a row of stars), each group with a pair of names (star group · place name), a single pale colour, thin lines; label the star-group shapes "schematic".
9. **The camera's baseline:** no hard cuts between nodes (the next node's first keyframe is not written at 0); azimuth does not jump across 0/360 (camcheck `spin`); the camera does not enter buildings or the ground (camcheck).
   9a–9k are the detailed rules for time, beams, camera and tags.
   Camera azimuth is interpolated value by value: 0 followed by 357 makes a full turn, so write -3 (camcheck checks `spin`).
9a. **Time is computed by an algorithm, not written as seconds by hand** (`pipeline/stagecraft.py`). A city change begins at the earliest moment when all of these hold: the beam has landed;
   the start of the change (the beam's landing point, `from`, or the city `origin`) is within the central 60% of the picture, and the city takes at least 12% of the picture height; the camera target has settled — a camera still pushing in also counts
   (distance shortening by no more than half per second; pulling out does not count). If it settles only for a moment it starts anyway and 9e supplies the hold; if none can be found at all, compile reports an error and asks for a camera aimed at it. Ring speed is computed by the picture: inside the picture it takes at least `timing.ring_view` (2.8) seconds, and it speeds up only once out of the picture;
   each growth stage takes at least 4 seconds (2 seconds for a small place), and the front moves at most a third of the picture width per second. The engine and camcheck read only the sampled curve compile writes (computed in one place, used in two).
9b. **The refresh method is chosen by size:** if the changed area is large on screen (over 1 km or 35% of half the picture width), expand a ring of light from the start; if it is small (a village, one ward), use "refresh within the area":
   the ground is not lit, the city's outline (thin geometric lines, not a mask image) is traced from both ends on the side where the scan begins and joins on the opposite side, and the houses grow in order with a flash on top
   (a mask image has 7.6 m per cell, which is jagged up close, so effects for small areas are always drawn with geometry); things laid out along a line (`sweep`) use one sweep line. All rings and contracting rings share one drawing method:
   a bright core of 1–2 pixels, a soft glow of a few pixels, a faint trail on one side, with width computed in screen pixels; appearing and disappearing both fade in and out over about 0.4 seconds.
9c. **The beam's landing point is the centre of the circle** (`routes: impact: true`): on landing, first a flash (decaying over 0.35 seconds), then a shock wave spreading for 1.6 seconds (shorter looks like nothing happened);
   a ring with the new colour spreads from the landing point, and the city grows with it.
   **The camera follows the beam** (`follow: {el, d, land_d}`, and for one that does not land on a city add `hold` = seconds to stay after landing; compile's `follow_shot`): the algorithm chooses the direction — directly behind the beam, behind it 25° / 45° / 65° to the left or right,
   or straight from the side — simulates the whole flight for each, and the flight must satisfy "the start is in the picture at launch, the head of the beam stays in the picture throughout, the landing point is in the picture at landing"; among the directions that pass, it picks the one nearest the camera's current
   heading. The aim point is a little ahead of the beam head and rises with the arc of the beam (`FOLLOW_LIFT`), so the top of the arc does not shoot out of the top edge of the picture. A hand-written `follow.az` is only an exception
   and must pass the same check, or it reports an error. The camera needs enough time to get from where it was before the beam is fired (if not enough, time is inserted before launch).
   **After landing the camera turns to the whole city:** hold on the landing point for 0.6 seconds (the flash), then turn, in the time the movement needs, to the city's own direction (the azimuth of the node's first hand-written camera, or north up if none),
   and pull out until all the buildings of the first stage of the city are in the picture (no closer than at landing: a small town is seen together with its surroundings, so the colour-change ring can be seen); the city and the ring start only when the camera is in place,
   and only after that does the camera move closer to see detail. This stretch of camera belongs to compile; hand-written keyframes falling inside it are skipped (compile prints them).
9d. **Modern change follows the data's time and does not assume growth from the core outward:** `grow.change: ghsl` uses GHSL built volume (100 m, 5 years) to find the buildings that were "later rebuilt taller", first low then tall;
   the counter shows new builds and rises; `follow_change` makes the camera fly low to the place where change is densest in each period (`region` limits it to the city the film is about).
   There is no data on demolition: GHSL's observed volume never decreases, and no public data records demolished houses — the picture does not speak of demolition.
9e. **The time the camera gives to change is supplied by the algorithm** (compile's `plan_stages`, with the result in `build/logs/plan.json`; compile reruns itself until nothing more is needed):
   (a) if an earlier keyframe is already aimed at the city but the camera has not held, hold the camera at that frame and the city grows there; (b) after the last building has grown, the camera holds for at least `timing.hold_after` (2.5) seconds;
   (c) if the key buildings of a new city have never been seen closely from start to finish (in the picture, with the surrounding `look_focus_m` 400 m taking 40% or more of the picture height for 3.5 seconds; the node's own close-ups also count),
   fly over and take a look after it has grown. Where to look follows a priority (compile's `look_target`): ① what the film names (a landmark within 250 m of a node pin); ② key buildings traced with light
   (palace courts enclosed by walls, offices, temples, markets, armouries; or buildings in a small place traced with an outline); ③ other landmark buildings; within the same level pick the largest. Residential blocks, the low-detail parts used for wide shots,
   and ditches, ponds and kilns are never chosen; if none of the three levels has one, it does not move closer.
   Everything supplied is inserted time: the node gets longer, and the later subtitles and camera move back together.
   **The planner has an equilibrium:** an inserted hold changes the camera, and the camera changes the time to insert in the next pass, so changing one number (`lead`, a hold, a keyframe's seconds) can add a dozen seconds to a whole station.
   When changing the camera, change one number at a time, and each time look at the `plan (pass N): node … +… s` lines compile prints and whether `build/logs/plan.json` changed; if it changed, undo first;
   leave enough `lead` on lines tied to pictures, and do not force "narration time" to be inserted, otherwise every pass gives a different result (example: changing a station's `lead` from 7 to 4 turned a hold from 8 seconds into 20).
9f. **The camera must not jump:** between any two keyframes (hand-written, inserted, or the landing of a beam-following shot) leave enough time to move (`stagecraft.move_time`: target movement, zoom, turn and
   pitch converted into picture widths, at most 0.6 picture widths per second); if not enough, time is inserted automatically; finally compile checks every 0.25 seconds and reports an error if within half a second the camera moves more than one picture, turns 60°,
   or zooms 1.5 times or more (except when covered by full-screen footage).
9g. **When a ring contracts the camera descends with it, but always more slowly than the ring:** as soon as the contracting ring of a burned or demolished city enters the picture, the whole ring must stay in the picture until it has finished (this governs only the contracting ring,
   by its size at that moment; an expanding ring still runs out of the picture). compile produces this camera: during the stretch when the ring sweeps in from outside the picture (`timing.contract_in`, see rule 6) the camera turns to the fire's origin; the ring's starting size is computed from
   "the whole ring can fit in the picture when aimed at the fire's origin"; the distance shortens by the square root of the ring's radius and may be no closer than needed to frame the ring at that moment, so the ring also keeps getting smaller on screen;
   it finally stops at the next hand-written camera.
9h. **Pins and place names are the same kind of tag** (a pin must be pinned on the plate: where most of a place is off the plate, pin it to the part inside the plate and note in the name which way it extends; compile blocks pins off the plate; `h_m` is counted from the ground there: for a palace on a plateau, the pin stands on the plateau, not at the plate's zero height sunk into the slope; when the building leaves the picture the pin fades out with it and does not stick at the picture edge): a dot, a thin upright pole, a small dark box hanging from the top of the pole, the pole being the box's edge (no separate colour bar); type 20 / 14 pixels.
   Pole length and whether the box is on the left or right are arranged by compile (`pipeline/tags.py`): tags shown at the same time never cover one another, and avoid the subtitles, readouts, minimap and timeline; they stay fixed during their appearance.
   When a historic node's pin is not in the picture, compile only prints `warning: pin … is off screen` (only the modern section reports an error): every one must be handled, by making the last frame of the camera aim at it (for example the plinth),
   or by confirming that it is acceptable and telling the user; after fixing a pin's height or position, look again whether the camera still catches it. Do not add a pin with the same name as a geographic label (`film.labels`): the two overlap (compile warns when they appear together).
9i. **The modern section is one timeline** (`tour:`): city growth is the background (from the earliest year of the data: GHSL 1975), and the camera visits each point in time in order; a node writes `tour: {ll, d, el}`,
   compile computes the time to fly from the previous station (what the movement needs, and the year runs at most one year per second); during the flight the year runs forward and the camera circles the city (about 5° per second), on arrival the year stops,
   and after the telling it moves on. Do not insert events in the middle of growth to force the camera to hurry; a faraway event is the next station. Stop at whatever year the data reaches (the picture is labelled "资料至 2020" ("data up to 2020")).
   **Each station's camera is computed from what it tells** (compile's `tour_subjects`): all pins and areas (`areas`) of this station are framed in the picture (leaving room for the tags), and `ll`/`d`
   are used only when there is no subject; compile checks that each pin is in the picture for most of the time it appears, and reports an error in the modern section if not (mark one that truly cannot be seen `offscreen_ok`).
   A tag that was never drawn (the point is at the picture edge and the tag box does not fit) fails readcheck; for one the user agrees to ignore, write `unseen_ok: true` on that tag or area (it does not change the framing, it only lets the check pass).
   When the subject spans most of the plate and cannot be framed, raise the pitch (`tour.el` about 60), so that the plate fills the picture; do not pull out to see the black beyond the plate (Xianyang: 2006 the two cities, 2014 the new area).
   Before proposing "just change the camera a little", compute first: the space each tag box needs (about 200 px above), minus the readout area, minimap, subtitle band and timeline, and how far out the camera has to pull at the current heading to fit them;
   if the result is not a small change, hand it to the user as it is to decide.
   The place name of the place this station tells stays displayed from the moment of flying there until this station ends (place names normally show only in the wide shot).
9j. **When telling of an ancient city site, trace its outline again** (node `ghost: [<era id>]`): the vanished city reappears as thin lines and light on the ground under today's city,
   so the audience sees "the new city grows on the old city".
9k. **Areas named by a subtitle must be drawn** (node `areas: [{id, col, with or at, flash, zh, en}]`, boundaries in `research/*_areas.geojson`): administrative districts, new areas, new towns,
   factory areas and protected areas each get a glowing outline in one colour, plus the name, appearing with the line that names it (`with:`); whichever the subtitle is telling flashes once (`flash`); when two or more appear at once, the readout area gets a legend (`legend`).
   Each area is also a mask: buildings inside the area take its colour (`fill`: 0.2 for a large administrative district, 0.45 for a small factory area; dyed in the building material itself, like the dyeing of period cities — added only in the projected light it would be washed out by the white walls' ordinary lighting, leaving the ground coloured and the houses still white), the edge glows, and the outline keeps its screen width in the wide shot —
   thin lines on the ground are blocked by houses in dense urban areas and cannot be seen on their own. There are 12 mask channels in all (`data/layers1-3.png`), and masks that do not overlap in time and place share a channel.
   The plate inside an area takes only a veil of its colour, thinner as the area grows (compile writes `wash`: full up to 1 km², half at 2 km², a tenth from 10 km²): a district filled at full strength covered half the frame in one colour,
   and a warm colour thinned on the dark plate turns to mud; the outline and the buildings inside carry the colour. The wash always reaches the whole outline (a `reach` shorter than the area is raised to fit: short of it, the wash ended in a soft circle across the area, an edge that is nothing).
   For an area for which research found only a representative point and no boundary (example: the five new towns of Xixian New Area have no boundary in OSM or in public documents), put only the name on the point and do not draw a self-made frame;
   a number in a subtitle uses only a number with a named source (「遺址保護範圍縮到二十多平方公里」 ("the site protection area was reduced to over twenty square kilometres") rests only on one unnamed official's statement and does not go on screen).
   If the boundary is not official, label it "schematic". The part beyond the plate's boundary is naturally cut off.

## Footage and pictures

Each historic node ends with "the same place today" (`footage:`, `mode: full | panel | card | doc`): 4K video full frame for 7–9 seconds, high-resolution photos in the right-hand panel,
low-resolution material as a small card with a leader line (`anchor`), a document card for old maps; do not let footage flash by. **On-screen third-party material is only CC or public domain** (Wikimedia Commons);
the user's own shots or material the user has the right to license may also be used, with the licence stated in CREDITS. If there is none of these, a scene worth a picture gets an imagined picture based on the sources (which scenes get pictures and how to generate them: SCRIPT.md "Pictures"; label the card "根據史料想像" ("imagined from the sources"), and state it in CREDITS).
An imagined picture in the film uses `mode: panel` (right half, blended into the map) with the kicker 「想象图 · IMAGINED · 据史料」 ("imagined picture · IMAGINED · from the sources"), placed when nothing is growing on the model; non-CC material is allowed only for pipeline tests on the local machine,
not stored in the repository, and not in the preview shown to the user.
Take a screenshot of every new card, photo and document card: what the picture covers (minimap, the part that is growing, the subtitle band) can only be seen on a screenshot, and portrait pictures collide most easily
(the caption often lands on the subtitle). When replacing a piece of material or an imagery source, change together the places on screen where its source is written in (the readout's source line, the end card `end.lines`,
CREDITS); compile does not compare them.
**Footage:** during preview playback the video plays natively and is corrected only when out of sync, and 3D is not drawn when full-screen footage covers the picture; the final film is still positioned exactly frame by frame. Full screen uses only video of 1600×900 or higher; lower resolution becomes a small card.

**Living moments** (node `living:`): a picture of the period made from one shot of the model and projected back onto it from that shot's own camera. The camera arrives at the shot and stops,
today's city sinks, a thin ring of light spreads from the viewer's feet and turns the white model into the living town, the sky and the far land come with it; it holds (a slow zoom, mist, rain),
dissolves back to the model, and the camera goes on. It shows what the plate cannot: the daily life of the place at one moment, on the model the audience has been watching, not beside it.
- **Use two or three a film**, on key beats that can be told as one moment of life (a street the morning after rain, a market, a crowd going to the games), with the line that tells it (`with:`).
  Never over a change on the model, never with another picture at the same time (compile stops). A scene that only needs to be seen, not lived in, stays an imagined panel.
- **The shot:** low, close (`d` 0.01–0.04, the period city's streets and roofs filling the frame, a gate or a landmark far off), `fov` 35–45. The camera flies to it in `arrive` seconds from where the film's
  camera is: put the keys before it close enough that the arrival is not a dive. While the picture is up the camera only zooms (`zoom`, 0.94 by default): the projection is exact only from its own camera,
  and a camera that moves smears it.
- **The picture follows the sources:** write the scene card `research/living/<id>.yaml` (`place`, `when`, `picture`: what the moment shows, each detail from the sources; `avoid`: what the sources rule out,
  later or modern things; `sources`: the notes and FACTS lines). Then compile (`CT_LIVING=warn` while there is no picture), `uv run python -I tools/living.py ref cities/<slug> <id>` (the shot as a still and
  the prompt), `gen` (the Codex CLI edits the still; with another image tool, give it the still and the prompt, save the answer as `assets/living/<id>.png`, then `adopt`), and look at the `sheet`:
  the picture's buildings, walls and streets must sit on the model's (an image tool that drew another view: make it again), and nothing in it may contradict the card. Ask the user which image tool they
  have, as for imagined pictures (SCRIPT.md "Pictures").
- **A picture belongs to its shot and its model:** compile stops when the shot changed after the picture was made; after a change to the model or the terrain, `tools/living.py check` tells which
  pictures no longer fit (CHECKS.md).
- **Label and credit:** the kicker 「AI 生成重现 · AI-GENERATED RECONSTRUCTION · 据史料」 shows while the picture is up (written by compile from the language packs); the card's sources go into CREDITS,
  and the platforms' AI-content declarations are made when the film is published (PUBLISH.md).
- Keys: `{ id, with | at, shot: { ll, az, el, d, fov, y }, arrive: 2.5, reveal: 3.5, hold: 6, out: 1.5, back: 2, zoom: 0.94, from: viewer | [lon, lat], weather: { rain: 0..1, mist: 0..1, mist_y: 0.7 },
  file: assets/living/<id>.png, zh, en }` (zh/en: an optional title under the kicker).

**Spot** (node `spot:`): when the narration speaks of one place in a wide shot (the palaces on the north slope, a market, a gate), the light falls on it and the rest of the room goes dark:
`{ ll: [lon, lat], r_m: 600, with | at, until, hold, dur, dim: 0.16, boost: 1.35, fade: 0.8 }`. The eye goes to the subject at once without the camera moving; keep it for the beats where a wide shot has to stay wide.

## Minimap, satellite and ending

The locator minimap and the geographic labels (`film.labels`) appear automatically; the period cities' extents are drawn on the minimap. `film.night_look: { deep: 1 }` turns the night into a night city: today's walls and roofs go dark and fewer windows burn brighter, warm and cool, so a telephoto look across the river at night reads as a sea of lights (0: the white city with lit windows). The modern section can write `night: 1` for night-time window lights and light flowing along the road network.
Satellite imagery is used only in the final overview of the whole plate, made into a scan transition from white model to imagery with `sweep: true`,
and `back_at` sweeps back to the white model (the ending's footprints and light lines are drawn on the white model, so that the node colours can be seen);
`pipeline/imagery_tiles.py` can fetch Esri level-15 imagery (about 4 m, `film.satellite_source: hr`), which is not open data and may be used only to test the pipeline on the local machine;
the preview shown to the user and the final film always use Sentinel-2 (`sentinel`, 10 m, clear enough for the overview of the whole plate).
The ending uses the `footprints` projection to trace the actual footprints of the period cities on the satellite image, then strings the centres of the eras together with a line of light.

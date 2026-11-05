# Preview and checks

## The most common mistakes in this step

- Running the whole film after every change, so the user's computer freezes and they cannot type → normally check only the stations the change touched, and run the whole film only before rendering the final film, and only after asking ("After every change").
- Saying "fixed" without having looked at that second and that object → "Accept on the thing the user pointed at" (under "Acceptance and reporting").

## Preview

`uv run python -I pipeline/compile.py cities/<slug>`;
`node tools/preview.mjs <slug>` starts a local server, and the user opens in Chrome the `play.html?city=<slug>&play=1` it prints to play live; judge each node yourself when it is done (the audience pass below), then lay the next one,
and show the user long stretches of the film (SKILL.md workflow).
Also produce contact sheets (`node render/still.mjs <slug> --range a:b:step` + `tools/sheet.py`) and check section by section: whether pins are out of frame, whether layers are visible, whether the camera is aimed at the subject.
A period city that has no place in the film yet is looked at with `tools/modelview.py` (MODEL.md), its house types with `--sheet` (MODEL.md "House types"); every period city of the film from every side with `tools/eraview.mjs` and the `play.html?city=<slug>&view` page (MODEL.md).
Before showing the user, follow "Acceptance and reporting" below: the server is still running, you have taken a screenshot yourself to confirm it is the new version, remind the user to refresh, and speak only of what the preview really has.

## After every change

Check after every change and show the user only when everything is at zero, **but check only the range the change touched:** every station whose time or content changed, plus one station before and after each (first compare the start times of the stations before and after the change;
a station that was shortened or pushed also counts). `uv run python -I tools/clipcheck.py cities/<slug>` (model clipping: houses over walls, houses over streets, landmarks overlapping each other, slopes eating into buildings,
two period cities existing at the same time overlapping, floating, trees inside buildings, streets stopping short of what they lead to; it does not render, and runs over the whole city) and `node tools/geocheck.mjs <slug>` (faces of the period cities and props that point the wrong way; it does not render): compile runs both and stops when either fails, `node tools/camcheck.mjs <slug> --from <a> --to <b>` then `uv run python -I tools/camcheck.py cities/<slug>`
(camera clipping: camera underground, inside a building, line of sight blocked), `node tools/readcheck.mjs <slug> --from <a> --to <b>` (text dwell time), and look at screenshots second by second
(`node render/still.mjs <slug> --range <a>:<b>:1` + `uv run python -I tools/sheet.py`): problems the checks cannot find (composition, too fast, too dark) are caught by this step.
**One command runs them all for the range:** `uv run python -I tools/rangecheck.py <slug> --stations <id>[,<id>..]` (those stations and one before and after each; or `--from <a> --to <b>`;
a model study's folder works too): camcheck, readcheck, a still a second in contact sheets of 16 and line by line (`build/review/lines_<a>_<b>/`: each line's stills under
its words; with `--against <previous version>`, that version's stills of the same line beside them, only stills rendered from that version as it is now: a folder of stills carries a `stills.stamp`), and the stills' brightness, each step logged, a failed step does not stop the
others, and `build/review/range_<a>_<b>/report.json` holds the results. Do not write a script of your own for this; then look at every sheet.
**A round of changes, in one command:** `uv run python -I tools/round.py <slug> --against <the approved version the round started from>` compiles,
lists with filmdiff every stretch that changed, runs one rangecheck over all of them and reports compile's faults, each stretch's verdict, the lines the camera
now shows from much farther than before (look at those first: what was seen close often read better) and every line sheet. It runs to the end by itself:
make every change on the round's list first, then start it once and wait for it once (it says how long the last round took). Run the steps by hand only
to look into one of them.
**Give it every stretch the change touched in one command** (`--from <a> --to <b>` once for each, or every station in `--stations`), not one command a stretch:
each tool loads the film once for all of them, and on a long film the load, not the stretch, is most of a short stretch's time; each stretch is still checked on its own
(its own folder, sheets, report and verdict), and stretches that overlap or touch are checked as one. **Never run two checks of one city at once** (two rangechecks,
two camchecks, the tools by hand beside its rangecheck): the same tool writes the same files (camcheck's camera dump, a stretch's stills), and one run's results would
be read as the other's. A second rangecheck of a city waits for the first.
A film with living moments: after any change to the model, the terrain or a living shot, `uv run python -I tools/living.py check cities/<slug>` (each shot rendered again and compared with the still its picture was made from; over 6 per pixel the picture no longer fits: make it again), and look at each moment's `sheet`.
Whole-film screenshots, camcheck and readcheck freeze the user's computer so they cannot type; run them only in the round that fixes the whole film and before rendering the final film, and ask the user first (DELIVER.md).
Screenshots default to 1920×1080; `--size` accepts only 16:9 (for example 960x540), and the whole picture is scaled in proportion;
going wider than 1920 is only enlargement, and the text layer is drawn at 1920 wide, so it does not get clearer.
Every warning compile prints at the end must be handled, none left alone: keys in city.yaml that no code reads (a typo, a wrong place, or a form this version does not have: writing it has no effect), colours of two adjacent stations that are too close, a pin and a place name with the same name appearing together, the last station not being this year, houses standing on the water the film shows while they stand (today's or `water_then`'s), a river ending in mid-plate at a `water_then` stretch's edge, a period city standing in its period colour to the last frame (`persist` with no `until` or `today_from`), a word run into a number in the text on screen (`by1900`, `Porta Pia ·1870`: a space lost where a script made the text). If a coordinate is more than
one plate width from the plate and the far-terrain extent (mostly longitude and latitude mistyped or reversed), compile stops directly.

## Brightness

- How to measure: `ffmpeg -ss <a> -t <seconds> -i <video> -vf "fps=2,scale=640:-2,signalstats,metadata=mode=print:file=<output>" -f null -`, and read YAVG (mean),
  YLOW, YHIGH (8-bit, black 16, white 235); in the preview stage measure the screenshots of `render/still.mjs`. Normally measure only the changed stretches, and the whole film only before rendering the final film (ask the user first).
- Thresholds: whole-film mean YAVG ≥ 80; the mean of any one minute ≥ 60; the event with the most room must not be darker than the whole-film mean. Reference values: YHIGH of the lit faces of the subject about 140–190,
  plate 26–38 (visibly dark blue, not black), black level 18–24; the white of subtitles and interface does not exceed 235 (check with `signalstats=stat=brng`).
- Finally look on a phone: lights on indoors, or by a window in daytime, screen brightness about half; building outlines can be told apart, the wide shots have not smeared into one, the subtitles are not glaring.

## Acceptance and reporting

- **The audience pass:** play the stretch at speed, with the subtitles, as a viewer who does not know the city, then write down what it leaves (SKILL.md "Judge as the audience").
  Then go through it line by line against the storyboard: each line carried by what is on screen as it is said, a far place on a map as it is named (STAGING.md "A picture
  for every key beat"); each change on the model seen happening and read at that camera distance, with no picture beside it (STAGING.md 5b); the year counter only forward
  (STAGING.md "Basic grammar"); tags in plain words, readable at their size. Compare a revised stretch with its previous version, frame beside frame, every stretch the
  revision touched, the camera moves made to fix a check too: `uv run python -I tools/filmdiff.py <previous version> <slug>` lists them (camera, lines, panels, tags, routes,
  fronts, light: a light lowered or raised for one stretch can drown the subject of another, the whole wall's line in a city grown too bright) and prints one `tools/rangecheck.py --against <previous version>` command for all of them, whose line sheets lay the two versions side by side: what read better before goes back.
  Set each station's length against its voice (the example runs about 1.25×); a station well above it is gathering silences: list every gap over 8 seconds and what is on screen. What fails here is restaged, whatever the checks say; a station handed over with one of these left costs the user a round.
- **Hand over whole:** show the user a round when all of it is done, not station by station while the rest is still being fixed.
- **Before showing the user:** confirm the preview server is still running (after a power cut or reboot, run `node tools/preview.mjs` again); take a screenshot yourself to confirm it is already the new version, and remind the user to "look again after refreshing"
  (an open page may have been loaded halfway through a change); speak only of what the preview really has (example: when the preview cannot play sound yet, do not ask the user to "listen in the preview").
- **Accept on the thing the user pointed at:** confirm by screenshot at that second and on that object, not on something beside it (example: for an area's colouring look at the houses changing colour, not only the ground);
  when replacing an effect, look once at the farthest and once at the nearest camera: "not deleted" does not mean "visible" (example: sparks shrunk to 3 pixels cannot be seen even up close).
- **A review rule adopted midway runs over the whole film** before the next handover, not only over the stretches changed since: a stretch that never changed
  was never seen under the new rule (it passes every comparison with the version before it).
- **A fault the user names is one of a kind:** fix it, then go through every line of the film for the same fault before handing back (example: one far place
  named without a map means checking every place each line names, not only the one pointed at). The user should never have to find the second one.
- **A check passes when the picture is right, not when the model is shaped to its exception:** an exception (a wall ending in a tower is a joint, a pin
  marked `offscreen_ok`) is for the case it names. A model bent to fit one (a vertex set inside another wall so a crossing reads as a joint) hides the fault the
  check was written for: fix what is on screen, and when a check is wrong for a real case, say so in the handover instead.
- **When the user says "it changed", compare before reasoning about the cause:** rebuild the commit before the change (`git worktree add`, or `git archive` into a temp folder), and compare screenshots at the same second;
  find the cause by elimination: paint each part a different colour, remove them one by one, and see which one the defect follows; do not decide the cause first.
- **Verify before you say it:** before saying "the program does it this way", read the program; "checks pass" must be run on the state after the last change, stating which stretch was run; before saying "the picture is unchanged", compare
  `build/film.json` before and after the change (framing is computed from pins, areas and lines, so removing one tag also moves the composition). When a test fails, first examine the test itself (a mistyped URL, a missing file),
  then draw a conclusion.
- **Report in proportion to the change:** a small fix reports what changed, the link, and the checks of the stretch it touched; time spent on proofs, receipts and
  repeated reviews of unchanged parts is time the user waits. To verify is to run the check and give its result in a line; it is not to write a receipt, an audit
  script or an equivalence file for it. Iterate on the touched station with its neighbours (a candidate of those stations only), then put it back. A candidate is a copy of the city's build
  (hundreds of MB for a large city): once its change is back, delete it, keeping only the version the user is viewing and the one filmdiff compares with (old candidates left behind filled a disk).
- **State the scope of the effect:** one building, one station, one city, or the whole film and all cities. When changing a judgement shared by all nodes, compile the whole film and compare each station's duration, `build/logs/plan.json` and
  `build/logs/deadair.txt`, not only the stretch where the problem appeared.

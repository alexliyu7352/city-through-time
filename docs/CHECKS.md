# Preview and checks

## The most common mistakes in this step

- Running the whole film after every change, so the user's computer freezes and they cannot type → normally check only the stations the change touched, and run the whole film only before rendering the final film, and only after asking ("After every change").
- Saying "fixed" without having looked at that second and that object → "Accept on the thing the user pointed at" (under "Acceptance and reporting").

## Preview

`uv run python -I pipeline/compile.py cities/<slug>`;
`node tools/preview.mjs <slug>` starts a local server, and the user opens in Chrome the `play.html?city=<slug>&play=1` it prints to play live; show the user each node when it is done, then lay the next one.
Also produce contact sheets (`node render/still.mjs <slug> --range a:b:step` + `tools/sheet.py`) and check section by section: whether pins are out of frame, whether layers are visible, whether the camera is aimed at the subject.
A period city that has no place in the film yet is looked at with `tools/modelview.py` (MODEL.md), its house types with `--sheet` (MODEL.md "House types").
Before showing the user, follow "Acceptance and reporting" below: the server is still running, you have taken a screenshot yourself to confirm it is the new version, remind the user to refresh, and speak only of what the preview really has.

## After every change

Check after every change and show the user only when everything is at zero, **but check only the range the change touched:** every station whose time or content changed, plus one station before and after each (first compare the start times of the stations before and after the change;
a station that was shortened or pushed also counts). `uv run python -I tools/clipcheck.py cities/<slug>` (model clipping: houses over walls, houses over streets, landmarks overlapping each other, slopes eating into buildings,
two period cities existing at the same time overlapping, floating; it does not render, and runs over the whole city), `node tools/camcheck.mjs <slug> --from <a> --to <b>` then `uv run python -I tools/camcheck.py cities/<slug>`
(camera clipping: camera underground, inside a building, line of sight blocked), `node tools/readcheck.mjs <slug> --from <a> --to <b>` (text dwell time), and look at screenshots second by second
(`node render/still.mjs <slug> --range <a>:<b>:1` + `uv run python -I tools/sheet.py`): problems the checks cannot find (composition, too fast, too dark) are caught by this step.
Whole-film screenshots, camcheck and readcheck freeze the user's computer so they cannot type; run them only in the round that fixes the whole film and before rendering the final film, and ask the user first (DELIVER.md).
Screenshots default to 1920×1080; `--size` accepts only 16:9 (for example 960x540), and the whole picture is scaled in proportion;
going wider than 1920 is only enlargement, and the text layer is drawn at 1920 wide, so it does not get clearer.
Every warning compile prints at the end must be handled, none left alone: keys in city.yaml that no code reads (a typo, a wrong place, or a form this version does not have: writing it has no effect), colours of two adjacent stations that are too close, a pin and a place name with the same name appearing together, the last station not being this year. If a coordinate is more than
one plate width from the plate and the far-terrain extent (mostly longitude and latitude mistyped or reversed), compile stops directly.

## Brightness

- How to measure: `ffmpeg -ss <a> -t <seconds> -i <video> -vf "fps=2,scale=640:-2,signalstats,metadata=mode=print:file=<output>" -f null -`, and read YAVG (mean),
  YLOW, YHIGH (8-bit, black 16, white 235); in the preview stage measure the screenshots of `render/still.mjs`. Normally measure only the changed stretches, and the whole film only before rendering the final film (ask the user first).
- Thresholds: whole-film mean YAVG ≥ 80; the mean of any one minute ≥ 60; the event with the most room must not be darker than the whole-film mean. Reference values: YHIGH of the lit faces of the subject about 140–190,
  plate 26–38 (visibly dark blue, not black), black level 18–24; the white of subtitles and interface does not exceed 235 (check with `signalstats=stat=brng`).
- Finally look on a phone: lights on indoors, or by a window in daytime, screen brightness about half; building outlines can be told apart, the wide shots have not smeared into one, the subtitles are not glaring.

## Acceptance and reporting

- **Before showing the user:** confirm the preview server is still running (after a power cut or reboot, run `node tools/preview.mjs` again); take a screenshot yourself to confirm it is already the new version, and remind the user to "look again after refreshing"
  (an open page may have been loaded halfway through a change); speak only of what the preview really has (example: when the preview cannot play sound yet, do not ask the user to "listen in the preview").
- **Accept on the thing the user pointed at:** confirm by screenshot at that second and on that object, not on something beside it (example: for an area's colouring look at the houses changing colour, not only the ground);
  when replacing an effect, look once at the farthest and once at the nearest camera: "not deleted" does not mean "visible" (example: sparks shrunk to 3 pixels cannot be seen even up close).
- **When the user says "it changed", compare before reasoning about the cause:** rebuild the commit before the change (`git worktree add`, or `git archive` into a temp folder), and compare screenshots at the same second;
  find the cause by elimination: paint each part a different colour, remove them one by one, and see which one the defect follows; do not decide the cause first.
- **Verify before you say it:** before saying "the program does it this way", read the program; "checks pass" must be run on the state after the last change, stating which stretch was run; before saying "the picture is unchanged", compare
  `build/film.json` before and after the change (framing is computed from pins, areas and lines, so removing one tag also moves the composition). When a test fails, first examine the test itself (a mistyped URL, a missing file),
  then draw a conclusion.
- **State the scope of the effect:** one building, one station, one city, or the whole film and all cities. When changing a judgement shared by all nodes, compile the whole film and compare each station's duration, `build/logs/plan.json` and
  `build/logs/deadair.txt`, not only the stretch where the problem appeared.

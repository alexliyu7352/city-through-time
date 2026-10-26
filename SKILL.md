---
name: city-through-time
description: "Make “A City Through Time” (《一城春秋》) data films: given a city and a starting era, research the sources, fetch building and map data, and render a white-model projection film that lights the city up era by era (white model, dark room, light as the actor; local language plus English, English only for English-speaking cities). Trigger words: 一城春秋, A City Through Time, 城市變遷影片 (city-change film), 白模城市影片 (white-model city film), 按年代點亮城市 (light a city up by era)."
---

# city-through-time · 一城春秋 · A City Through Time

Input: a city name and a starting era (for example "Xianyang, from the Neolithic"). Output: the film, subtitles, cover and description in `cities/<slug>/dist/`,
plus `TREATMENT.md`, `FACTS.md` and `CREDITS` in the city folder. The project root is the folder this file is in; `cities/xianyang/` is a complete example,
so look at it first when unsure how to write something.

**Before anything else, research included: if `local/config.json` does not exist, do step 0 now.** Read `docs/SETUP.md`, ask the
user about each machine path it lists, and write the file; start no other step until it exists. Ask only about those paths: a city's
own files (research, `FACTS.md`, `city.yaml`, `build/`, `dist/`) always live in `cities/<slug>/` inside the project.

**This file is the index.** It holds only the core constraints and the workflow. Before each step, read that step's file (the "Read first" column of the workflow table) and follow it; read the next step's file only when you get there.
After a context compaction, an agent change or a few days' break, first work out "Which step are we on", then read that step's file. When the user names a part to change, read the file that part belongs to
(camera and staging: STAGING; narration: SCRIPT).

## Core constraints (apply to every step)

Working with the user
- **Propose first, then act.** Before changing code, a data format, the engine or the workflow, state the reason and the approach, and change it only after the user agrees. When the user says "let's discuss first", only look things up and take screenshots; change no files.
  A new request made midway goes into the plan with a note of which step it falls in; do not do it on the spot.
- **Change only what was named.** Redo only the part the user sent back. If you find a better setting, use it only where named and add one line ("this works elsewhere too") for the user to decide.
  **The problem the user points at is an example:** find the same defect in the same picture or the same generator yourself, and list it for the user before fixing.
- **Small batch first, then the whole film.** Fix the few spots pointed at and test only those; apply the same fix to the whole film only after the user confirms it in the preview.
- **Praised passages are the baseline.** Record them in TREATMENT.md (seconds, what works), and check every later batch of changes against them; they must not regress.
- **Reports must be checkable.** Give film time (mm:ss), node and file name; if only half is done, say which parts are still wrong; record deferred problems as a list and pick it up in the next round without being asked;
  if the previous report was wrong, correct it first in the next one. Before saying "checks pass" or "the picture is unchanged", actually run and compare (CHECKS.md).
- **Use the tool as it actually is.** Before asking the user to operate a tool, look at its real interface (ask the user for a screenshot if you cannot get it); look up a model's parameters in the code of the exact version that will run.
  For a design you are unsure about (timeline, music workflow, staging), look at how comparable works and open-source projects do it, then propose.
- **Pushing, uploading and publishing each need the user's go-ahead on that occasion.** Consent for the last one covers only the last one; after a commit, report "not pushed yet".

Computer and files
- Local paths and settings live only in `local/config.json` (SETUP.md); always run Python as `uv run python -I …`.
- **One heavy job at a time:** do not run rendering, mixing, music generation, DuckDB scans and whole-film screenshots at the same time. Render with 2 workers and nice by default. Write the progress of long jobs to a log file
  and read it with a separate command; do not pipe into `| tail`. To wait for a background job, wait on its PID or output file, not on the process name (`pgrep` matches its own shell). Whole-film screenshots and checks freeze the user's computer so they cannot type:
  normally check only the stations you changed; run the whole film only in the round that fixes the whole film and before rendering the final film, and ask the user first.
- **Try things on a copy.** For A/B tests and removing a part to see the effect, use a temporary folder or a git worktree. If you touched `build/` or a city's settings, restore it afterwards and confirm it is back to what it was.
  Undo changes by hand; do not use `git checkout --` or `git reset --hard` (they also throw away other uncommitted changes). Try new languages and new ways of writing things in a copied
  city folder, delete it afterwards, and do not change the real settings.
- **Keep scripts in the project.** Put generator, measurement and check scripts in the city's `research/` or `tools/`, not only in a temp directory (it is cleared between rounds).
- **List before deleting.** Delete only what the user named and obvious junk. Research notes, reports and source texts are the city's data; do not delete them. Before deleting, check file by file whether it is in git,
  whether a copy exists elsewhere, and whether a process is using it (`lsof +D <directory>`, `ps`).
- **A new city is configuration, not code changes.** When fixing a problem, ask whether a mountain city, a city with no building data, or a non-Chinese city would hit it too; if the fix can be general, change the shared code.
- The user's shell may be zsh: `for f in $list` does not split on spaces, and the `:p` in `$c:path` is read as a modifier. Write `for f in a b c` and `"${c}:path"`.

Honesty
- Every fact the agent researched and put into the film needs a real source in FACTS.md (this binds the agent's research, not the user and not the narrator's feelings).
  Copy the user writes or edits is used as is without demanding a source; raise it only when it contradicts data you found.
- Label schematic as schematic and estimated as estimated: the period cities are schematic models; building years are not construction years (CMAB gives the first year an impervious surface appears; GHSL gives built-up area in 5-year periods),
  and there is no building-by-building data before 1975. Do not put a dot on a site with no public coordinates, or label it "location schematic".
- On screen, use third-party material only if it is CC, public domain, or something the user has the right to license. AI-generated narration, music and imagined pictures are labelled on screen and in the end card.

Writing rules
- A rule that holds for any city goes into the file of the step it belongs to (only rules for every step go in this file). Write each rule once, in the same change that changes the practice. A rule that belongs to one city only
  goes in that city's own files. A habit of one particular user is kept in the agent's own memory, not in a public file.
- **Write for an agent with no context.** Write only the rule and the reasons that are needed. No renames, no version history, no dates, no who-said-what-when, no "I/we", and nothing the reader cannot see
  (local reference videos, internal notes, code names from a conversation). Give examples from settings and numbers that can be looked up in `cities/xianyang/`.
- **Skill files are written in English:** `SKILL.md`, the step files in `docs/`, and the comments in the templates. Keep Chinese only where it is data (quoted narration or on-screen text, place names, book titles), with an English gloss in parentheses the first time.

## Workflow

| Step | What to do | Read first | Done when (★ = the user must approve) |
|---|---|---|---|
| 0 | First use: local paths, install the environment | `docs/SETUP.md` | `local/config.json` written; `uv sync` and `npm ci` have run |
| 1 | Research: timeline, choice of stations, through-line, sources | `docs/RESEARCH.md` | `FACTS.md` and `research/` (including story material `stories.md` and the picture list `images.md`); ★ the story and the station list |
| 2 | Extent and data: frame, scale, map, buildings, terrain | `docs/DATA.md` | extent and data sources in `city.yaml`, `prep.py` has run; ★ one white-model still to check the scale |
| 3 | Script: story outline, detailed outline, treatment, copy, timeline, pictures | `docs/SCRIPT.md` | `TREATMENT.md`, nodes, `script.yaml`; ★ story outline, ★ detailed outline, ★ narration draft |
| 4 | Period cities and terrain | `docs/MODEL.md` | one whole city per period, generated from the sources, clipcheck at zero |
| 5 | Staging: rings, camera, tags, pictures, footage | `docs/STAGING.md` | compile has no errors, every warning handled |
| 6 | Preview and checks | `docs/CHECKS.md` | checks at zero for every station the change touched; ★ the user has seen this station in the preview |
| 7 | Sound: voice, music, effects | `docs/SOUND.md` | `VOICE.md`, `MUSIC.md`, all three tracks audible in the preview; ★ each piece of music |
| 8 | Render and deliver | `docs/DELIVER.md` | ★ render only after the user approves the preview; `dist/` has video, subtitles, description; whole-film checks and brightness pass the thresholds |
| 9 | Publish: cover, upload, portal page (only when the user wants it public) | `docs/PUBLISH.md` | ★ cover concept; ★ every upload and push has the user's go-ahead on that occasion |

Do steps 3–6 node by node: finish one station, show it to the user, then lay the next. Sound comes after picture: copy final → picture → preview → voice → compile again
(timeline final) → music and effects → render.

## Which step are we on

| What you see | Step |
|---|---|
| No `local/config.json` | 0 |
| No `cities/<slug>/FACTS.md`, or the station list has not been approved by the user | 1 |
| FACTS.md exists, no `build/data/model.json` | 2 |
| The model exists, and some nodes are unfinished or have not been shown to the user | 3–6 (check TREATMENT.md and the preview, and ask the user which station you are at) |
| All pictures seen, but no voice yet, or the music is not settled | 7 |
| No `dist/<slug>.mp4`, or the film is older than the last change | 8 |
| The film exists and the user wants it public | 9 |

## File map

- `engine/` the player page (three.js: `main.js` reads film.json and plays it, `studio.js` is the white-model scene and projection shaders, `overlay.js` is readouts, pins, subtitles, the end card).
- `pipeline/` data fetching (`osm.py`, `cmab.py`, `overture_ghsl.py`, `ghsl.py`, `terrain.py`, `satellite.py`; `layout.py` says where a city's files and downloads live), `prep.py` (→ model), `citygen.py` (period cities),
  `compile.py` (city.yaml → film.json), `fonts.py` (font library).
- `render/` stills, event table, video, composing the final film; `audio/` music scheduling, code score, sampler, mixing; `tools/` checks (subcheck, readcheck, clipcheck,
  camcheck, motioncheck), `build.mjs` (one command renders the film), `music.py`, `web.py` (web player bundle), `registry.mjs` and `site.mjs` (portal site).
- A city folder holds what is written and brought in by hand (goes into git); `build/` holds what is generated (not in git; `build/data` is slow to rebuild, so do not delete it casually); `dist/` holds the finished products (`pipeline/layout.py`).
- `templates/` templates; `i18n/` language packs; `fonts/` fonts; `index.html` + `site/` the portal page (the land `site/land.bin` is produced by `tools/portal_land.py`;
  `?lite` shows how the phone version draws); `play.html` the player (`?bundle=` reads an external player bundle).

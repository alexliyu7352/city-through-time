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
- **Propose first, then act.** Propose, with the reason and the approach, any change that outlives this film or changes what the user approved (the engine's look, data formats, the
  workflow, other cities' output), and make it only after the user agrees. Bug fixes, a city's own generators and tools that serve a round's notes are yours: list them in the commit
  and the report. When the user says "let's discuss first", only look things up and take screenshots; change no files.
- **A round's list is set before it starts, then frozen.** A round is the user's notes, sorted first: quick fixes (a tag moved, a label, a picture found or swapped,
  a line's binding) make one round, done and shown first; rebuilds (a section restaged as a tour, a model re-traced from new sources, a new picture generated) the
  next. One round for both keeps the user waiting for the slowest item while the quick ones sit done. A request made midway is placed, not lost and not mixed in
  silently: it goes to the next round's list (or the plan, with the step it falls in), unless it is small and touches nothing in progress, or the user wants it now;
  say where it went, and list any addition in the report. A list that grows while the round runs keeps the round from ever ending, and every addition reopens
  checks already done. Research for a note stops when the picture is right; the rest goes to the notes for later. Build a tool now when it saves time in this round.
- **Make sure it fits before building it.** Before modelling, staging or compiling what a note, a decision or the plan asks for, add up what it needs against what it
  has: a stretch's seconds against the lines that tell it, the stages it must show and the flights between them (STAGING.md "A picture for every key beat"); the
  narration's length against the film's; a render's disk against the free space. When it cannot fit, say so with the sum and the ways to make it fit (stages the
  words do not tell apart made one, a pause, a longer line, a part left out) and let the one who asked choose, the user included, before any compile. A compile is
  the dearest way to find that a plan cannot fit: each try costs a whole compile, and a plan that cannot fit fails every try.
- **The user judges the story and the film; you judge the steps towards them.** The user's approvals are the ★ in the workflow table: the story, the narration, the scale,
  the film in the preview, the music, the render and what is published. House types, quarters, samples, a station's camera and timing are yours: judge them against the
  step's done line and the example city, and go on. Do not wait for an approval no ★ asks for: each such round stalls the work and leaves the user judging details while
  nobody judges the film as a whole.
- **The audience is the world.** The film is for viewers anywhere: people who know neither the city nor its country, many of them reading the subtitles in a second
  language. Neither the city's own people nor native speakers are the measure. The film itself tells what the story needs: when it happens, who holds the city, who a
  person is and why something changes; nothing may rely on what a local, a historian or a native speaker already knows.
- **Judge as the audience, not only by the checks.** Checks at zero say the film is not broken, not that it works. Before showing anything, watch and listen to it as that
  viewer, in every language the film shows (each is read on its own), and write down what they would remember of it: the story in one sentence, and for each big passage a line, a number or a picture. Set its
  strongest moments beside the example film's (`cities/xianyang/`, whose shape is rise, peak, fall, return) for strength, not slot for slot: each city has the shape its own
  history has (RESEARCH.md §2). A stretch weaker or vaguer than the example is not done, whatever the checks say. The main agent reviews a subagent's piece the same way.
- **Change only what was named.** Redo only the part the user sent back. If you find a better setting, use it only where named and add one line ("this works elsewhere too") for the user to decide.
  **The problem the user points at is an example:** the work is done when that defect is gone everywhere it occurs (for instance the same picture, the same generator, the rest of the film); find it yourself.
- **Small batch first, then the whole film.** Fix the few spots pointed at and test those first; then spread the fix wherever it leaves approved and praised stretches unchanged (check
  against the approved version, for instance `tools/round.py --against`), and report each place it touched (mm:ss). Where the fix would change how an approved passage looks or sounds,
  show it in the next preview; do not stop the work to wait for a confirmation.
- **Praised passages are the baseline.** Record them in TREATMENT.md (seconds, what works), and check every later batch of changes against them; they must not regress.
- **A report is the result, the pictures and what is not done.** What changed and where (film time (mm:ss), node and file name), the stills or the stretch of the
  preview to look at, the checks' result lines, and what is still wrong or deferred (a list, picked up in the next round without being asked); not how it was done.
  If only half is done, say which parts are still wrong; if the previous report was wrong, correct it first in the next one. Before saying "checks pass" or "the
  picture is unchanged", actually run and compare (CHECKS.md "Report in proportion to the change").
- **The record is git and the checks, not documents.** Commit the city folder when a step is done and after each round of changes, the message saying what changed and
  the checks' own result lines; the checks are programs (compile's, `tools/rangecheck.py`'s report). Do not write receipts, audits or proof files: the user neither reads
  nor needs them, and they cost the time the film needs.
- **Use the tool as it actually is.** Before asking the user to operate a tool, look at its real interface (ask the user for a screenshot if you cannot get it); look up a model's parameters in the code of the exact version that will run.
  For a design you are unsure about (timeline, music workflow, staging), look at how comparable works and open-source projects do it, then propose.
- **Pushing, uploading and publishing each need the user's go-ahead on that occasion.** Consent for the last one covers only the last one; after a commit, report "not pushed yet".

Computer and files
- Local paths and settings live only in `local/config.json` (SETUP.md); always run Python as `uv run python -I …`.
- **One heavy job at a time:** do not run rendering, mixing, music generation, DuckDB scans and whole-film screenshots at the same time. Render with 2 workers and nice by default.
  **Every long job goes through one entry** (a compile, a round, a render, a mix, a whole-film check, a model study): `uv run python -I tools/job.py start <name> -- <command>`
  runs it niced in its own session with its log and a record of its command, pid, start, end and exit code (`status`, and `wait <name>` blocks until it ends and exits
  with its code). Not a helper of your own that spawns it, and not piped into `| tail`: a job started another way leaves no record of how it ended or how long it took.
  To wait for a job something else started, wait on its PID or output file, not on the process name (`pgrep` matches its own shell).
  **A job comes back to you only when it ends or fails.** Between its start and its end the one thing to do with it is wait, without spending turns, noticing an early
  failure (compile says at its start how long the last one took): for instance a notification when the job exits, or a blocking wait on the process that returns when
  it dies, with the longest time limit the environment allows; never a look every half-minute, never a fixed sleep that outlasts a crash, and no progress report.
  A wait the environment cuts short (its own time limit; `job.py wait --timeout` exits 124) says nothing new: wait again at once, without reading the log. Each look is
  a whole turn of yours, which in a long conversation takes longer than the half-minute it waits: a ten-minute compile watched that way costs twenty turns. Light work
  that does not depend on the job goes on meanwhile. Whole-film screenshots and checks freeze the user's computer so they cannot type:
  normally check only the stations you changed; run the whole film only in the round that fixes the whole film and before rendering the final film, and ask the user first.
- **Try things on a copy.** For A/B tests and removing a part to see the effect, use a temporary folder or a git worktree. If you touched `build/` or a city's settings, restore it afterwards and confirm it is back to what it was.
  Undo changes by hand; do not use `git checkout --` or `git reset --hard` (they also throw away other uncommitted changes). Try new languages and new ways of writing things in a copied
  city folder, delete it afterwards, and do not change the real settings. A copied city folder is a candidate made and deleted with `tools/candidate.py`, whole or
  cut to a few stations (CHECKS.md "Report in proportion"), never a script of your own.
  **A copy lives one round; the city folder is the film's one source.** Before the next round starts, the changes the last round keeps are in `cities/<slug>/`,
  committed and compiled there (`tools/filmdiff.py` between that build and the round's candidate lists no stretch), and the round's candidates are deleted; the
  next round's candidate is made from the city folder. Nothing the film is built from lives only in a candidate, a temporary folder, another disk or a script
  outside the project. A copy kept on as the next round's base becomes a second source: its timing drifts from the first, its files point into other rounds, and
  gathering the film's real sources back together costs a round of its own.
- **Keep scripts in the project.** Put generator, measurement and check scripts in the city's `research/` or `tools/`, not only in a temp directory (it is cleared between rounds).
- **List before deleting.** Delete only what the user named and obvious junk. Research notes, reports and source texts are the city's data; do not delete them. Before deleting, check file by file whether it is in git,
  whether a copy exists elsewhere, and whether a process is using it (`lsof +D <directory>`, `ps`).
- **A new city is configuration, not code changes.** When fixing a problem, ask whether a mountain city, a city with no building data, or a non-Chinese city would hit it too; if the fix can be general, change the shared code.
- The user's shell may be zsh: `for f in $list` does not split on spaces, and the `:p` in `$c:path` is read as a modifier. Write `for f in a b c` and `"${c}:path"`.

Subagents and parallel work
- **The main agent coordinates; subagents build.** A film fills one session with research, script, every period and every check; once that context is large, every action re-reads it
  and the work slows to a crawl. Keep the main session for the plan, the user's decisions, review and merging, and give each self-contained piece to a subagent started with a fresh
  context (one that does not inherit this conversation: Codex `spawn_agent` without forking the turns, Claude Code's Agent tool, or whatever the environment offers). Where no subagent can
  be started, start each piece in a new session from the same brief.
- **A round of revisions starts with a fresh context.** Once a round's list is set and frozen ("A round's list is set before it starts" above), write the
  handoff (`templates/handoff.md`, into the city's `research/`) and do the round in a new session or a subagent with a fresh context started from it. The old
  conversation is looked up, not carried: it holds withdrawn rulings and earlier versions, which a long context takes for current (a lost close shot put back
  wide, a base chosen from the wrong version), and every action in it costs more. A round is the user's list; what review sends back inside it (a fix that
  missed, a fix that broke something next to it) stays in the round and goes to the same subagent (Review before merging), which already knows the code and
  the files: a new one spends its first quarter of an hour reading them again. The fetches of a round that do not wait on each other (the sources a note
  needs, the pictures to find and check for their licence) start at once in parallel subagents, each returning its file, its source and its licence; the
  staging waits only for what it uses. A fresh session with a handoff is for a context grown stale or large, not for a batch the agent holding the files can
  finish in minutes.
- **A piece** is work with its own inputs and its own files: one period city (step 4, once the research, the extent and the approved house types exist), one research question (step 1),
  the candidates for one music cue (step 7). Not a piece: what the user decides, the stations' staging (step 5 goes station by station, each building on the last), and a change to
  files several pieces share (the engine, the pipeline, types shared by periods, the shared keys of `city.yaml`): those stay with the main agent.
- **The brief is all the subagent knows.** It gives the subagent what it needs to meet its done line without guessing: the goal and its done line (the workflow table); the rules that
  bind its piece and where they are; the files it owns (for a period city: `research/<period>_*` and its study spec, built with `tools/modelview.py --spec` under its own name) and the
  files it must not touch; and how to report (paths of stills, the checks' lines, open questions, short). Have it read in full only what bears on its piece (for a period city, for
  instance, the step's doc, `FACTS.md`, the approved types). Catch a wrong idea on a small part before the whole is built (for instance one quarter judged by the main agent before the
  whole city, MODEL.md, after which the same subagent continues); where a subagent ends when it reports, resume it rather than start a new one. It does not ask the user anything; it
  asks the main agent.
- **Run in parallel what shares no files:** every period city at once, each its own subagent, when the environment can run that many (and every research question). The machine
  is shared: heavy jobs stay one at a time across all agents (rendering, mixing, music generation, whole-film checks), and a city's compile, a model study and every page a tool opens
  take one of two machine slots (`pipeline/slots.py`) and wait for a free one, so many subagents at work queue there instead of freezing the machine. The main agent merges one
  piece at a time into `city.yaml`, after review.
- **Reasoning effort by the kind of work**, set when starting the subagent (the model and effort options of the spawn call), measured from the main agent's own level: that level for
  research, the story and the script, and for reviewing and judging pictures; one level below for laying out a city from approved sources and types and for running checks and fixing
  what they find; the lowest for mechanical edits (moving files, renaming, formatting). Never above the main agent's level: the levels above it mostly add time, and time is what the
  subagents are for.
- **Models:** a subagent runs on the main agent's own model or on the one a tier below it (the same provider's next lighter model), never on a stronger one, and never two tiers
  below. A stronger model, or a level above the main agent's, can spend the user's whole quota on one piece. When a piece seems to need a stronger model than the main
  agent's, ask the user first, with the reason; do not start it.
- **Wait for the subagents in the same turn.** After starting them, wait for each to finish (the environment's wait call), then collect, review and report, all before the turn
  ends: a session that ends its turn while its subagents work may not wake when they finish, and their work sits until someone writes to it. A subagent, like a job,
  comes back when it is done or needs a decision: wait with the longest time limit the wait call takes, and when a wait returns with nothing new, wait again at once;
  do not ask a subagent how far it has got. Each wait that returns is a turn of the main agent's, in the largest context of all.
- **Review before merging.** The main agent checks each piece against its step's done line and the rules before it goes into the film; a piece sent back goes to the same subagent with the
  reason (it keeps its context), not to a new one. The user's approvals (★ in the table) are asked by the main agent.

Honesty
- Every fact the agent researched and put into the film needs a real source in FACTS.md (this binds the agent's research, not the user and not the narrator's feelings).
  Copy the user writes or edits is used as is without demanding a source; raise it only when it contradicts data you found.
- Label schematic as schematic and estimated as estimated: the period cities are schematic models; building years are not construction years (CMAB gives the first year an impervious surface appears; GHSL gives built-up area in 5-year periods),
  and there is no building-by-building data before 1975. A pin at public coordinates stays as it is; a position estimated from the sources is labelled "location schematic";
  a place with no basis for a position at all is mentioned without a pin.
- Careful means checked, not left out. A well-known story, saying or figure the film needs is looked up and verified like any fact; one that cannot be verified is told as
  legend, with "about", or as the range the sources give. Leaving a city's most memorable material out because it needed checking makes a film nobody remembers.
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
| 1 | Research: timeline, choice of stations, through-line, sources | `docs/RESEARCH.md` | `FACTS.md` and `research/` (including story material `stories.md`, the picture list `images.md` and the period cities' survey `period_cities.md`); ★ the story and the station list |
| 2 | Extent and data: frame, scale, map, buildings, terrain | `docs/DATA.md` | extent and data sources in `city.yaml`, `prep.py` has run; ★ one white-model still to check the scale |
| 3 | Script: story outline, detailed outline, treatment, copy, timeline, pictures | `docs/SCRIPT.md` | `TREATMENT.md`, nodes, `script.yaml`; ★ story outline, ★ detailed outline, ★ narration draft, each shown after your own listener review (SCRIPT.md); ★ the storyboard (each line → what is on screen) |
| 4 | Period cities and terrain | `docs/MODEL.md` | one whole city per period, generated from the sources, what the storyboard asks for first, clipcheck at zero; its quarters and type sheets judged by you (no ★) |
| 5 | Staging: rings, camera, tags, pictures, footage | `docs/STAGING.md` | compile has no errors, every warning handled; every key beat has its picture (STAGING.md "A picture for every key beat") |
| 6 | Preview and checks | `docs/CHECKS.md` | checks at zero for every station the change touched; your audience pass on it; ★ the user has seen the film in the preview, in long stretches |
| 7 | Sound: voice, music, effects | `docs/SOUND.md` | `VOICE.md`, `MUSIC.md`, all three tracks audible in the preview; ★ each piece of music |
| 8 | Render and deliver | `docs/DELIVER.md` | ★ render only after the user approves the preview; `dist/` has video, subtitles, description; whole-film checks and brightness pass the thresholds |
| 9 | Publish: cover, upload, portal page (only when the user wants it public) | `docs/PUBLISH.md` | ★ cover concept; ★ every upload and push has the user's go-ahead on that occasion |

The period cities of step 4 do not depend on each other: build them at once ("Run in parallel what shares no files"). Staging and its checks (steps 5 and 6) are judged
station by station (the done lines of steps 5 and 6, the audience pass), so that each station plays well coming out of the one before: a later station adapts to an
earlier, already-judged one, never the other way round, unless that earlier station is judged again. Show the user long
stretches (a third of the film, or all of it) rather than each station: the user judges how the film plays as a whole, which no single station shows. Sound follows what it is timed to:
the voice's timing follows the final copy, and the timing of music and effects follows the final timeline (copy final → picture → preview → voice → compile again
(timeline final) → music and effects → render). Work that depends on neither (casting the voice, music research, candidates) can start earlier, within the one-heavy-job limit.

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
- `pipeline/` data fetching (`osm.py`, `cmab.py`, `overture_ghsl.py`, `ghsl.py`, `terrain.py`, `satellite.py`; `layout.py` says where a city's files and downloads live and the area every download covers), `prep.py` (→ model), `citygen.py` (period cities), `landmarks.py` (landmarks of any region as classes of massing; `python -I pipeline/landmarks.py` lists every key),
  `compile.py` (city.yaml → film.json), `fonts.py` (font library).
- `render/` stills (`still.mjs` takes a moment by name too: `cue:<line>`, `node:<id>[.end]`, `loss:<era>/<loss>`, `year:<y>`, each with an offset), event table, video, composing the final film; `audio/` music scheduling, code score, sampler, mixing,
  `levels.py` (the music under the narration, cue by cue), `seams.py` (a generated voice's clicks mended); `tools/` `delivercheck.py` (the finished film's own numbers), `job.py` (a long job in the background), `gaps.py` (the narration's silences, and the lines a change moved against a base), `candidate.py` (a working copy of a city, whole or cut to a few stations, to try a change on, then delete), checks (subcheck, readcheck, clipcheck,
  camcheck, motioncheck, geocheck, phonecheck (the film's shaders on a phone's graphics); `round.py` compiles a round of changes and checks every stretch it changed in one command (compile, filmdiff, rangecheck); `rangecheck.py` runs the checks and stills of every stretch a change touched in one command; `linesheet.py`, which it runs, lays each line's stills under its words, beside the previous version's with `--against`; `filmdiff.py` lists the stretches a revision changed and one `rangecheck.py --against` command for all of them), `pipeline/register.py` (an old map or a plan registered and traced into lon/lat, with an overlay to check), `parcels.py` (a quarter's whole-building lots along its streets, as a trace), `freeze.py` (an approved study kept as it was, checked later), `modelview.py` (stills of a period city before it is in the film; `--sheet`: its house types and landmarks side by side), `eraview.mjs` (every period city from every side; the page `play.html?city=<slug>&view` to look round by hand), `living.py` (the pictures of living moments: the shot's still, the prompt, the picture, its check; a museum page's viewpoints too), `museum.py` and `museum.mjs` (a museum page for one building: its model, parts, label and pictures, `docs/MUSEUM.md`), `hant.py` (its Traditional Chinese, OpenCC s2twp, read through), `build.mjs` (one command renders the film), `music.py`, `web.py` (web player bundle), `registry.mjs` and `site.mjs` (portal site; `--city`: one city's own site), `deploy.mjs` (the user's city as a site of its own on Cloudflare Pages, never a copy of the portal).
- A city folder holds what is written and brought in by hand (goes into git); `build/` holds what is generated (not in git; `build/data` is slow to rebuild, so do not delete it casually); `dist/` holds the finished products (`pipeline/layout.py`).
- `templates/` templates; `types/` the shared library of house types (docs/MODEL.md "House types"); `i18n/` language packs; `fonts/` fonts; `index.html` + `site/` the portal page (the land `site/land.bin` is produced by `tools/portal_land.py`;
  `?lite` shows how the phone version draws); `play.html` the player (`?bundle=` reads an external player bundle; `?view&free` the old cities to walk round); `museum.html` a museum page (`docs/MUSEUM.md`).

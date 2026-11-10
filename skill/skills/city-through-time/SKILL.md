---
name: city-through-time
description: "Make “A City Through Time” (《一城春秋》) data films: given a city and a starting era, research the sources, fetch building and map data, and render a white-model projection film that lights the city up era by era (white model, dark room, light as the actor; local language plus English, English only for English-speaking cities). Also its museum pages and its web player. Trigger words: 一城春秋, A City Through Time, 城市變遷影片 (city-change film), 白模城市影片 (white-model city film), 按年代點亮城市 (light a city up by era)."
---

# A City Through Time · 一城春秋

This skill holds no code. All the work happens in a **workspace**: a clone of
https://github.com/alexliyu7352/city-through-time. The workspace holds:
- the film engine and the pipeline that turns sources and map data into the film;
- the tools and their checks;
- the step-by-step rules (`AGENTS.md` and `docs/`);
- every city made so far (`cities/xianyang/` is the complete example).

The rules live in the workspace, next to the code they describe, so they always match its version.

## 1. Find or make the workspace

1. **Already in one?** It is the current folder or one of its parents when it has `AGENTS.md`, `engine/` and
   `pipeline/citygen.py`. Use it.
2. **The user named a folder?** Use that one. If it is not a workspace yet, clone into it (step 3).
3. **Otherwise, ask the user once where to put it.** Suggest `~/city-through-time`, and say what it takes:
   - about 300 MB for the clone;
   - about 5 GB of working space per city (downloaded map and building data, frames while rendering);
   - about 6 GB more only if the music is generated locally.
   Then clone it:
   ```sh
   git clone https://github.com/alexliyu7352/city-through-time.git <folder>
   ```
   If the user means to send their city back to the shared site, clone their fork instead (they fork it on GitHub
   first); `CONTRIBUTING.md` in the workspace says how the pull request goes.
4. **An existing workspace, a new city:** bring it up to date before starting, with `git pull --ff-only` when its
   working tree is clean. If it has local changes, ask the user before touching them.

## 2. Work inside it

From here on the workspace is the project root: run every command from it.

**Read its `AGENTS.md` first and follow it.** It has:
- the workflow and the approval points;
- the hard rules and the checks;
- which `docs/` file covers each step.

Its first step is **first use**. On a computer that has no `local/config.json` yet, `docs/SETUP.md` covers it:
- the local paths, asked of the user one at a time;
- `uv sync` and `npm ci`;
- the tools the film needs: Node 20 or newer, uv, ffmpeg, exiftool, Chrome.

The agent does all of this itself. The user only answers the questions.

A new city's folder (`cities/<slug>/`) is made from the workspace's `templates/`, as `AGENTS.md` says. Its research,
data, model, script, sound and renders all stay in that folder.

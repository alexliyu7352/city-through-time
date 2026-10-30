# Make a film of your city

English · [繁體中文](MAKING.zh-Hant.md) · [简体中文](MAKING.zh-Hans.md)

This guide takes you from zero to a city film, using the A City Through Time skill. Claude Code (the coding agent) makes the film. You set the direction and check every step in the browser. The rules are in [`SKILL.md`](../SKILL.md) and the step guides it points to (`docs/`), and the agent follows them.

## 1. Watch one first

Watch the Xianyang film on the [entry page](https://cities.go5.si/xianyang/) to see what the result looks like: a white model, one colour per era, a continuous narration, and a source for every fact.

## 2. Prepare your computer

| You need | Used for |
|---|---|
| [Claude Code](https://claude.com/claude-code) | the agent that makes the film |
| Node 20 or later | the player and rendering tools |
| [uv](https://docs.astral.sh/uv/) | the Python environment (it downloads Python 3.12 itself) |
| ffmpeg, exiftool | assembling the video, removing metadata |
| Chrome and a graphics card | rendering the picture (it runs without a graphics card, but much slower) |

Disk: about 5 GB of workspace per city (downloaded map and building data, frames and audio tracks while rendering). If you generate the music with a local model, the model takes about 6 GB more.

For scale (Xianyang, a 12 min 30 s film, on a 2019 desktop): one compile takes about 3 minutes, rendering the whole film about 36 minutes, and mixing about 2 minutes. Research and section-by-section revision take the most time, usually several days.

## 3. Install

```sh
git clone https://github.com/alexliyu7352/city-through-time.git
ln -s "$PWD/city-through-time" ~/.claude/skills/city-through-time
```

The second line lets Claude Code find the skill. Then open Claude Code inside the `city-through-time` folder.

## 4. First use

Tell the agent: "Use A City Through Time to make <city>, starting from <era>." The first time, it runs the "first use" step:

- It asks where on this computer to keep data, and writes the answer to `local/config.json` (not in git). We suggest keeping everything under `local/` in the project; if the disk is too small, large files can go on another drive.
- It checks that the tools are installed, and sets up the environment with `npm ci` and `uv sync`.

## 5. The workflow

The agent works in the order below and stops after every step to show you. When it needs to change code or switch approach, it first explains the reason and the approach and only goes ahead once you agree; for a problem you name, it changes only those places, and it finds similar problems itself and lists them for you:

1. **Research**: a timeline, the source and original text of every fact (`FACTS.md`), and the turning points chosen for this city.
2. **Data**: set the area (about 20–30 km square), fetch OpenStreetMap, buildings, terrain and satellite imagery, then render one white-model still so you can check the scale.
3. **Past cities**: generate the city of each era from archaeological reports and historical sources, marked "schematic" on screen.
4. **Script and timeline**: first write one continuous narration, then let the picture follow its sentences.
5. **Preview**: `node tools/preview.mjs <city>` starts a local server; open the address it prints in Chrome to play the film. Watch each section as it is done, and tell the agent about any problem.
6. **Narration, music and sound effects**: the agent first asks which way to go: record it yourself, an online service (for example MiniMax), a local model (for example Stable Audio 3), a CC music library, or code-written music (no model, offline, free, as a fallback). The chosen way and its terms of use (whether it may be made public, whether it may be used commercially) are written to the city's `VOICE.md` and `MUSIC.md`. Sound effects (the moments a light column lands, the city burns, the lights go out) can be picked or left out; all three can be heard in the preview.
7. **Finished film**: only after you approve in the preview does it render: `node tools/build.mjs <city>`. It runs all the checks and delivers the film, bilingual subtitles, cover and description in `dist/`.

## 6. Principles to keep

- **Every fact needs a source**, written in `FACTS.md`. If you cannot find one, leave the fact out.
- **Mark schematic as schematic and estimated as estimated**: past cities are schematic models, and building years are satellite estimates.
- **Use only material that can be published**: CC-licensed or public-domain images and footage, with author and licence written into `CREDITS`.
- **Say clearly what is AI-generated**: the narration, music and imagined scenes are all labelled on screen and in the end credits.

## 7. When it is done

To add it to the entry page, follow [`CONTRIBUTING.md`](../CONTRIBUTING.md): upload the film, optionally publish a web bundle, and open a pull request. For a site of your own, a free Cloudflare account is enough: `node tools/deploy.mjs --project <name>` publishes the entry page and your city at `https://<name>.pages.dev/` (step 3 of the same file).

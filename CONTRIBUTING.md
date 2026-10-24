# Contributing to A City Through Time

English · [繁體中文](CONTRIBUTING.zh-Hant.md) · [简体中文](CONTRIBUTING.zh-Hans.md)

There are two ways to take part: **submit a city** so it appears on the entry page, or **improve the code and the skill**.

## Submit a city

This repository holds text data only: a city's config, script, fact sources, copyright notes and research notes. Finished films, web bundles, posters, images and music live elsewhere (video sites, Hugging Face, your own GitHub Pages), and the entry page just links to them. Xianyang is this project's example. Its folder keeps the images, poster and web bundle (`cities/xianyang/web/`, which the entry page plays straight from GitHub Pages), so you can follow it from start to finish. A city you submit does not need to do the same.

### 1. Make the film first

Follow [`docs/MAKING.md`](docs/MAKING.md) to finish a film. All the checks of `node tools/build.mjs <city>` must pass.

### 2. Upload the film

Upload `cities/<city>/dist/<city>.mp4` to YouTube, Bilibili or another video site. You can use `dist/description.md` as the title and description. The film's address goes into `watch` in `entry.json` later.

### 3. Web bundle and poster

With a web bundle, viewers can play the film in the browser right on the entry page, and can drag, pause, and switch narration and music on or off. The web bundle is optional, but the poster must be hosted somewhere, because the entry page's collection needs it.

```sh
uv run python -I tools/web.py cities/<city>
```

It packs the files the player needs into `cities/<city>/dist/web/` (about 121 MB for Xianyang). Only files the page really reads are included: no WAV files and no internal test images. The posters are in there too: `poster.jpg` (1280 wide) and `poster_thumb.webp` (640 wide, used by the collection and search). If you upload only the film and no web bundle, host these two images on their own. Fonts are not in the bundle; the player reads them from this project's `fonts/` (a city that uses a new font must add it to `fonts/` in its pull request).

The place that hosts the web bundle must **allow cross-origin reads by web pages**. Both of these work:

**Hugging Face dataset (recommended)**: public datasets are free and large files are fine.

```sh
uvx --from huggingface_hub hf auth login
uvx --from huggingface_hub hf upload <your-account>/city-through-time-bundles cities/<city>/dist/web <city> --repo-type dataset
```

Web bundle address: `https://huggingface.co/datasets/<your-account>/city-through-time-bundles/resolve/main/<city>/`

**Your own GitHub repository with GitHub Pages**: create a public repository, put the contents of `dist/web/` in a `<city>/` folder, and in the repository's Settings → Pages choose to publish from the main branch. Limits: each file under 100 MB, the whole site under 1 GB.

Web bundle address: `https://<your-account>.github.io/<repo-name>/<city>/`

Other static hosts (for example Cloudflare R2) also work, as long as the response carries `Access-Control-Allow-Origin`.

**Check before uploading**: the voice and music services you used must allow public distribution of the generated audio in their terms, and this must be noted in `CREDITS`.

**Trial play**: append `play.html?city=<city>&play=1&bundle=<web bundle address>` to the entry page address. It counts only if it plays from start to end.

### 4. Write `cities/<city>/entry.json`

The entry page recognises your city through this file. First let the tool generate a draft from the film:

```sh
uv run python -I tools/web.py cities/<city> --entry
```

It writes `cities/<city>/entry.json`, filling in the location, years, length, languages and the colour of each chapter. You fill in the rest:

| Field | Content |
|---|---|
| `slug` | The name of the city folder (lowercase letters, digits, hyphens), also the city page address: `https://cities.go5.si/<slug>/`. It must not match a folder of the site itself or a language code (for example `site`, `ja`); the check rejects it |
| `name` | The city name in five languages: `en`, `ja`, `zh-Hant`, `zh-Hans`, `es` (a missing one falls back to English) |
| `location` | `[longitude, latitude]` |
| `years` | `[start, end]`, negative for BCE |
| `duration` | Film length (seconds) |
| `narration`, `subtitles` | Narration language, subtitle languages (language codes, for example `zh`, `en`) |
| `authors` | `[{ "name": "…", "url": "…" }]` |
| `summary` | A two or three sentence summary, in the same languages as `name` |
| `poster` | https address of the poster (1280 wide), for example `<web bundle address>poster.jpg` (the example city Xianyang uses the path inside the repository) |
| `thumb` | https address of the thumbnail (640 wide), for example `<web bundle address>poster_thumb.webp` |
| `watch` | `[{ "site": "YouTube", "url": "…" }, { "site": "Bilibili", "url": "…" }]`: list every site you published to. The entry page shows them all, and **the first is the default** ("Watch the film" plays it). Paste the ordinary film address (without a start time). YouTube and Bilibili are embedded in the entry page, and you can switch sites in the player window; other sites are shown as links |
| `bundle` | `{ "url": "web bundle address", "mb": 121 }`, or `null` if there is none |
| `download` | (optional) `{ "url": "…" }`, the download address of the film file |
| `ai` | The AI-generated parts: `narration`, `music`, `imagined` |
| `license` | `CC BY-SA 4.0` |
| `chapters` | Start second, year and colour of each chapter (generated by the tool; the entry page draws them as a colour bar) |
| `added` | Date added, `YYYY-MM-DD` (the newest comes first in the collection) |

At least one of `watch` and `bundle` is required. If neither exists yet, the entry page shows "The film is being published".

You do not write the `cities.json` that the entry page reads, or each city's own page: on every merge to main, GitHub Actions generates them from all cities' `entry.json` files (`tools/site.mjs`). City pages come in five languages: English at `https://cities.go5.si/<slug>/`, the others at `/ja/<slug>/`, `/zh-hant/<slug>/`, `/zh-hans/<slug>/` and `/es/<slug>/`. The title, summary, share preview image (the poster) and film information are all written into the page, so pasting it into social media shows a preview of the city, and search engines can find it. When you preview locally with `node tools/preview.mjs`, a copy is generated into `_site/` first, and opening `http://127.0.0.1:8765/<slug>/` shows it.

### 5. Open a pull request

Include only the text files in `cities/<city>/`:

- `entry.json`, `city.yaml`, `script.yaml` (the script), `CREDITS` (copyright notes), `FACTS.md` (fact sources), `TREATMENT.md`, `VOICE.md`, `MUSIC.md`;
- research notes in `research/` (text such as .md, .txt, .json, .csv, .geojson);
- notes on where assets came from, for example `assets/README.md`, and `assets/footage/make.sh` for cutting live-action footage (the assets themselves are not included).

Do not include: images, posters, music, video, PDFs and other non-text files (.gitignore already blocks them, and the PR check does too); `build/`, `dist/`, `local/`, `internal/`; account details (voice IDs, keys) and local paths.

After you open the PR, GitHub Actions checks automatically that the `entry.json` fields are complete, that the addresses are correct, and that no files other than text were added (`node tools/registry.mjs --check`, which you can also run locally first).

In the PR description, write: the check results (the lines printed by `tools/build.mjs`), which third-party material was used and under what licences, and which parts are AI-generated.

### What review looks at

- **Facts**: spot-check the sources in `FACTS.md`; check that schematic and estimated pictures are marked on screen.
- **Licences**: every piece of third-party material is in `CREDITS` and may be published; the city data and film are agreed to be under CC BY-SA 4.0.
- **Film**: watch it through; subtitles and text stay inside the frame, no black frames, normal loudness.
- **Web bundle and poster**: play it once; the poster opens.

## Improve the code and the skill

- If you have a problem or an idea, open an issue first; a small fix can go straight into a pull request.
- Follow the existing style of the code (naming, comment density, how files are divided). Write each rule once in `SKILL.md`; do not repeat it.
- If you change the compiler, player or renderer, run the relevant checks: use `node render/still.mjs` to produce a few stills to compare before and after, and if needed run a section of `tools/clipcheck.py`, `tools/camcheck.*` or `tools/readcheck.mjs`.
- Use uv for Python (`uv add` to add packages, and commit `uv.lock` with it) and npm for Node (commit `package-lock.json` with it).
- Do not commit local paths: always read paths from `local/config.json` (`pipeline/local.py`, `render/local.mjs`).

## Licence

Code you submit is under MIT ([`LICENSE`](LICENSE)); city data and films are under CC BY-SA 4.0 ([`LICENSE-CONTENT.md`](LICENSE-CONTENT.md)).

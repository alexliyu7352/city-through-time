# Publishing to the portal (only when the user wants it public)

## The most common mistakes in this step

- Pushing without asking → every push and upload waits for the user's go-ahead on that occasion.
- Using an automatic frame from the film as the cover (with subtitles and no title) → first present a cover concept for the user to confirm, then make the image ("Cover").
- Checking the terms of the voice and music only just before release → they should have been checked when the service was chosen (SOUND.md); confirm once more at this step.

## Cover

Make the cover only when the engineering is done and it is time to upload. The most important thing on a cover is the title and the subtitle; the picture comes second.
1. **Present the design concept to the user first:** the title, the subtitle, which moment of the film is used as the picture (usually the event with the most tension in the film, for example the burning of Xianyang or the Qin unification), and the layout;
   one for the Chinese and one for the English platforms. The title is one line of big type (Chinese 4–8 characters, English 2–5 words), the subtitle says which city and what kind of film, and the series name goes in a corner as a mark.
   A cover is a promise: draw what really is in the film. Make the image only after the user confirms the concept.
2. **Render one clean frame:** re-render that moment with the engine, with no subtitles, readout, minimap or timeline; pull the camera in so that the subject (firelight, golden light) takes a third of the picture or more
   and is the brightest place in the whole image. The 16:9 master is 3840×2160, with the subject and the text inside the central 4:3 area; also lay out a 3:4 (1080×1440) for a portrait cover.
3. **Ask the user whether to use AI to process it:** if so, hand the rendered image to AI to strengthen (light, smoke, sparks, depth of field, sky), keeping the white-model city and the node light colours; for tools see
   SCRIPT.md "Pictures"; the text can also be written into the image by AI, and after it comes out the agent and the user check it character by character. Without AI, or if the text AI wrote is wrong, set the text yourself with the fonts in `fonts/`.
4. **Test:** make two or three versions (example: the main image, an imagined picture from the film, another event), and test them together with YouTube's Test & Compare, deciding the winner by watch time, about two weeks;
   on platforms with no free A/B, use the main image.

Save the final cover as `dist/poster.jpg`: `tools/web.py` makes the portal's `poster.jpg` and `poster_thumb.webp` from it.

## Upload and the portal

The steps shown to the user are in `CONTRIBUTING.zh-Hant.md`. The repository takes only text data; the finished film, player bundle, posters, pictures and music all live outside:
- First ask the user where to put them and which account to use; every upload step needs the user to log in themselves or give explicit consent (once public it cannot be taken back); a git push is also an upload and each one needs the user's say on that occasion;
- Before going public, fix which files may be public: before creating a public repository or the first push, scan file by file for local paths, account IDs (such as the voice ID of the narration), email addresses and keys; non-CC material,
  modelling reference pictures, `local/`, `build/`, `dist/` and internal documents do not go in; removing from tracking is not removing from history, and the first commit pushed cannot be taken back;
- The finished film: the user uploads it to a video site (YouTube, Bilibili…) and the address is written in `watch` of `entry.json` (fill in as many as the film is published on; the first is the portal's default;
  store the ordinary watch address and remove parameters such as `&t=`; confirm that a test video is still there, because a player reports a string of errors for a video that was taken down); a separate download (`download`) can also be put up;
- The web player bundle: `uv run python -I tools/web.py cities/<slug>` packs it into `dist/web/`, taking only files the page reads (no WAV, no internal test pictures),
  and the posters `poster.jpg` (1280 wide) and `poster_thumb.webp` (640 wide) are in it too; `bundle.json` records the size of each file, and the player's loading screen computes its progress from it,
  so the whole folder goes up as it is. The place it goes must allow cross-origin reads by web pages: Hugging Face datasets are recommended
  (free, and big files are no problem); or the user's own GitHub repository with Pages (single file 100 MB, site within 1 GB); for other static hosts confirm there is
  `Access-Control-Allow-Origin`. Write the address into `bundle.url` and the size into `bundle.mb`; when no player bundle is made, the two poster images must also go outside.
  Before uploading, confirm that the terms of the voice and music services allow public distribution of the generated audio, and write it into CREDITS; for the part that does not allow commercial use (Xianyang: MiniMax narration is for personal, non-commercial use only),
  state in `LICENSE-CONTENT.md` that it is not under the CC BY-SA licence, because CC BY-SA lets others use it commercially;
- `cities/<slug>/entry.json`: `uv run python -I tools/web.py cities/<slug> --entry` writes a draft (position, era, length, languages, chapter colours),
  to which you add names and descriptions in five languages (en, ja, zh-Hant, zh-Hans, es), the author, the https addresses of the poster and thumbnail, the AI-generated parts (`ai`) and `added`;
  a film with living moments (STAGING.md) lists them among the AI-generated parts, and when it is uploaded the platform's AI-content declaration is made (YouTube: altered or synthetic content, yes; Bilibili: the AI-generated content statement; in mainland China the publisher labels AI-generated content);
  `node tools/registry.mjs --check` checks the fields (the slug is also the city page's address and must not equal the name of the site's own folders or a language code), whether the city's text files contain local paths,
  account IDs and keys, whether Chinese punctuation is stuck after a Markdown URL, and whether `watch` carries a start time; add `--online` to also ask the video site whether it can be embedded and whether the bundle's host
  allows other sites to read it (CORS). The portal reads `cities.json`, and the standalone page of each city in five languages (`https://cities.go5.si/<slug>/`, `/zh-hant/<slug>/`…, with share previews and video information) is generated automatically by GitHub Actions
  with `tools/site.mjs`; do not edit them by hand. The canonical addresses, share images and the full addresses in the sitemap are fixed when the site is generated: after setting or changing the domain, deploy once more;
  the share cards of social sites cannot be verified from here, so ask the user to paste the link once and look;
- Try locally first: `node tools/preview.mjs` (it first generates the site into `_site/`), then open `http://127.0.0.1:8765/<slug>/`, then try the player bundle with
  `play.html?city=<slug>&play=1&bundle=<address>`; a city with museum pages (MUSEUM.md) runs `tools/museum.py` before packing, and the bundle carries them:
  `play.html?city=<slug>&view&free&bundle=<address>` and `museum.html?city=<slug>&id=<page>&bundle=<address>`;
- Submitting a pull request: include only the text files in `cities/<slug>/` (entry.json, city.yaml, script.yaml, CREDITS, the .md files, the text notes in research/,
  and material descriptions such as assets/README.md); no pictures, music or video, which the PR check blocks (`tools/registry.mjs --check --base`).
  The exception is this project's example city Xianyang: it keeps its pictures, posters and web player bundle in full (`cities/xianyang/web/`, copied there after repacking, with the bundle in entry.json pointing to it,
  so the portal plays directly from GitHub Pages; `.gitignore` and the check make an exception for it), while the modelling reference pictures and the original footage still stay out of git.

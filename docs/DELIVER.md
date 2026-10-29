# Rendering and delivery

## The most common mistakes in this step

- Forgetting the description, not clearing the metadata → deliver both with the video.
- The film is too dark → measure the brightness of the whole film before rendering, and deliver only when it passes the threshold (CHECKS.md "Brightness").
- Reporting the loudness of the mix → use the numbers measured on the final film.

## Rendering (only after the user approves in the preview)

`node tools/build.mjs <slug>` (add `--no-data` when the data already exists; add `--no-video` when the frames are already rendered).
`dist/poster.jpg` written by `tools/build.mjs` is a placeholder of one frame from the film; the real cover is made at publishing (PUBLISH.md "Cover").
Rendering also delivers the **description** `dist/description.md`, one for each language of the film:
a one-line summary, a short description (social post), a long description (video platform), chapter times (from the nodes in `build/export/timeline.json`; the first at 0:00, each chapter at least 10 seconds),
how it was made and the sources and licences (the authors of CC BY / BY-SA material must be named), the AI-generation statement, the author's credit,
and the project's credit, which LICENSE requires wherever a film is published: "Made with 一城春秋 · A City Through Time" and https://github.com/alexliyu7352/city-through-time. For facts use only what is in the narration and FACTS.md.
The delivered files **carry no metadata:** when `render/mux.mjs` composes them it writes no encoder tag, chapters or other metadata, strips the parameters x264 writes into the video
(removing only the SEI), and AAC carries no Lavc string; the cover is written bitexact, with no encoder note. Clean old files on hand: `exiftool -all=`, then confirm with `strings`.
build runs subcheck, clipcheck, camcheck, readcheck (including: text must not sit on the subtitle band, and two pieces of text must not overlap), motioncheck, a black-frame check, and loudness (−14 LUFS).
The whole-film checks run in this step; ask the user first whether the computer can be taken over now. For a change that touches the whole film (terrain, fonts, the whole-film timeline) when only the affected stations were run,
note at that time "run the whole film before rendering the final film", and catch up in this step. The whole-film brightness is also measured in this step; for the threshold see CHECKS.md "Brightness".
Report the loudness and peak taken from the final film as measured by `render/mux.mjs`, not those of the mix (the two differ by a few tenths of a LUFS).
When motioncheck reports "looks like a cut", pull out a few frames to see whether it is a bad frame or the camera turning fast; report the latter to the user, who decides whether to slow it down.

## Handover

Tell the user where the files are, and remind them of the third-party data and licences listed in CREDITS (CMAB CC BY, OSM ODbL, fonts OFL, sample library) and of the items in FACTS.md labelled schematic / estimated.

# Rome source media and prepared data

The final city specification, narration, models and media are frozen. This folder contains the film's source pictures, living-moment references, cover artwork and the following local source packages. Media stays outside git as required by PUBLISH.md; its descriptions and credits remain text sources.

- `audio/voice/en/`: 361 repaired FLAC lines and `takes.json`. These are the final narration inputs, not the earlier uncorrected lines. `audio/voice/original/` preserves original takes and cuts; `audio/voice/rome_voice_en.md` is the delivered text.
- `audio/music/source/`: six source recordings. `audio/music/cand/`: all ten audition edits and metadata. `audio/music/selected_metadata/`: the five selected edits; original metadata is retained separately. See MUSIC.md and CREDITS for attribution and licences.
- `covers/r15/`: original generated artwork, clean model references, prompts/provenance and typography variants. The selected masters are `titles_v2/rome_A_zh1_{wide,portrait}.jpg`, `rome_A_en_{wide,portrait}.jpg`, and `rome_A_en_time_wide.jpg`.
- `prep/`: thirteen preserved inputs from the approved preparation: `model.json`, `model_ungraded.json`, `stats.json`, `terrain.json`, `terrain.png`, `terrain16.png`, `terrain_true16.png`, `terrain_ungraded.png`, `terrain16_ungraded.png`, `satellite.png`, `satellite.json`, `water.png`, and `lines.json`. They are prepared data, not results freshly recreated by compile; retain them when removing generated builds.
- `raw/`: intentionally empty. The approved candidate read no raw OSM themes. The older Rome download cache is separately preserved; placing its themes here would change the compiler's inputs and must not happen silently.

On this machine `audio`, `prep` and `raw` point to independent, persistent canonical storage. They do not point to a trial candidate or temporary directory. Keep these source packages; an ordinary rebuild does not fetch or regenerate their contents. Sources requiring an online service or image generator cannot be recreated byte for byte from prompts alone.

To restore missing generated build inputs and compile the frozen city:

```sh
uv run python -I tools/job.py start rome_canonical_compile --dir cities/rome/research/rome_closeout -- uv run python -I cities/rome/research/rome_closeout/reproduce.py
uv run python -I tools/job.py wait rome_canonical_compile --dir cities/rome/research/rome_closeout
```

The helper restores these prepared inputs and the canonical audio links, sets the retained plan seed and uses the native compiler with two threads. It does not render, mix or mux. Preserve the final film independently of these generated files.

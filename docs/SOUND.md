# Sound: voice, music, effects

## The most common mistakes in this step

- Writing music prompts from impression → first research the music of each period of this city (RESEARCH.md §8).
- Applying a parameter conclusion from another version to the version that actually runs → look at the code of the version that will actually run.
- Cutting the voice into lines and then also trimming leading and trailing silence, which eats the start of the words.
- Checking the terms of the voice and music services only just before release → check them at the moment the service is chosen.

## Tools and models

- **Tools and models as they actually are:** before asking the user to operate a tool, first look at its real interface (ask the user for a screenshot if you cannot get it), and every setting value you write down must be findable on the interface;
  look up a model's parameters in the code of the exact version that will run (`--help`, source code), treat research only as a lead, and if unsure do an A/B with the same prompt and the same seed.

## Voice, music and the timeline

**Voice and the timeline:** a complete film has three things: narration, music and effects. Use only programs throughout (compile, `render/`, ffmpeg), no editing software, so that changing one line or swapping one piece reruns the whole thing.
Every sound in the final film must first be audible in the preview, and the preview and the final film use the same track. Voice (recorded or generated) is one file per line, put in `build/audio/voice/<language>/<line id>.wav` (mp3, m4a and ogg are also fine),
with the language defaulting to the first language (`film.voice.lang`). After compiling again: a line with a voice file uses the voice's length (plus 0.3 seconds), and moves together with the picture of that line;
compile also arranges each line's voice by time into one audio track, `build/audio/voice/track_<language>.wav`, which plays together in the preview (`?play=1`), pulled back whenever it differs from the picture by more than 0.15 seconds;
there is no sound while paused, dragging or stepping frame by frame, and the M key switches the narration on and off; when the music is laid it plays together, and the B key switches the music; the kept effects (`film.sfx`, first make single sounds with `uv run python -I audio/mix.py <city> --kit`, then compile) also play together, and the N key switches them, and the final mix uses the same track; after playing to the end card, the segment named by `film.music.loop` keeps looping, and pressing play again or dragging stops it (the audio track is converted to m4a and loaded whole: the preview server does not support range reads, and jumping inside a large WAV eats the start of a line; small errors are chased with playback speed, not by jumping).
When a voice generated as one whole piece (with fixed pauses between lines) is cut into one file per line: cut at the pauses, leave 0.15 seconds of silence before and after, with a 5 ms fade-in and 20 ms fade-out,
and **do not trim leading and trailing silence** (it eats the first word of a line and produces pops: in a film of 92 lines, 83 had half of the first word eaten); after cutting, check the number of lines and each line's length against its character count, and listen to the openings of a few lines (do not go by length alone). Before voicing, ask the user how (recording, online service, local model), and write the choice into the city's `VOICE.md` (Xianyang: MiniMax).
Before writing the voice workflow, look at the tool's real interface (emotion options, how much text at once, whether it can be set line by line); if a whole piece can be generated at once, do not split it into batches,
and do not write options the interface does not have.
When a voice or music service is chosen, check its terms at the same time (whether the output can be distributed publicly, whether it can be used commercially, whether registration is needed), write them into `VOICE.md` and `MUSIC.md`, and ask the user whether the video will earn money. Things belonging to the account (voice ID, keys) stay only on the local machine and do not go into git.
The same goes for music: first ask the user how (online AI, local model, a CC / public-domain library, composing, or a code score), and write the choice into the city's `MUSIC.md`:
- **Two ways of laying it** (`film.music.source`): `cues` (default) lays pieces of music node by node, whether generated, from a library or composed by hand; `code` is a code score as a fallback:
  no model, offline, free, written with sampled instruments over the film's own timeline (`audio/codescore.py`; download the sample library once first with `uv run python -I tools/instruments.py`, about 700 MB),
  run `uv run python -I audio/codescore.py cities/<slug>` after compile and after `render/events.mjs`, and once it is written it is laid directly, and pressing B in the preview plays it just the same;
  after that every compile lays it again, and when the timeline changes it reminds you to rerun (`tools/build.mjs` runs it itself). A code score is only music; the effects are still chosen with `film.sfx`.
- Sections: divide by nodes and the emotional line; the style comes from the confirmed story outline and the emotional line (SCRIPT.md "The director fixes the story first");
- The prompt of each section: written in `MUSIC.md` in one place only;
- The chosen wording and seed: so that regenerating gives the same piece;
- Licence and credit.
Before writing prompts, **first research the music of each period of this city:** instruments, genres, sources in historical records or archaeology, separating evidence, inference and modern convention, written in `research/music.md`;
the notes of the research process (the separate notes of each research thread, the source texts) go together in `research/music_notes/`: they are this city's data, and go into git with the city,
and must not be left in the project root or in a folder not in git (left there they are easily taken as unneeded and deleted).
Then fix the city sound that runs through the whole film and the lead of each section; do not write from impression.
Also find out which instrument words the generation model recognises and which parameters work: look at the code of the exact version that will run (`--help`, source code), treat research and official descriptions only as leads, and if unsure do an A/B with the same prompt and
the same seed (example: the original weights of Stable Audio 3 Medium are documented as having no negative prompt, and changing the seed hardly changes the result; the official CPU version used by `tools/music.py` in fact has `--cfg` and `--negative-prompt`,
and changing the seed also gives a different piece; after A/B, CFG 2.0 with a negative prompt came out smoother). For a rare instrument word, generate a short piece of it alone and ask the user to listen and confirm it sounds right before writing it into a whole section (the model does not know the sheng:
"sheng" came out like a zheng). Before running a model locally, first check whether the official project offers separate versions for CPU, Mac and NVIDIA, and then discuss disk, memory and login with the user (example: the official CPU version of Stable Audio 3 Medium
has weights of 3 GB, no login, 2 GB of memory; the standard weights need 15 GB of disk and about 20 GB of memory); before changing to a bigger version, first get 30 seconds running under the memory limit,
measure the usage and time, and change the default only once it runs.
Xianyang: Stable Audio 3 Medium generated locally, 11 sections. Songs on the internet are copyrighted and are not used; use only music you generated yourself, CC or public domain.
Lay the music with a director's eye: each section is generated only a few seconds longer than its node, so that the climax and the close fall inside the section; scene changes fade in and out with no gap in the middle; only where the same sound continues (the drums of the imperial capital → the burning of the city) is it generated as a continuation of the end of the previous section
(`continue:`), and where the era or the picture changes it is written for its own picture and does not continue (generating as a continuation of the previous section makes the style follow the previous era); a pause in the narration must not cut the music, and the moment after the last line is spoken is when the music pushes to its climax.
Prompts must not contain words such as silence, pause or rest, which the model takes literally (writing long silences left 30–40% of the candidates with no sound): for sparseness write a sustained underlying drone,
for rhythm write the rhythm out; simplify a prompt by cutting instruments only, not emotion, and keep in each section one line of the emotional course read from that station's narration. Measure each candidate first for silence ratio, longest gap and loudness trend
(`tools/music.py` prints them on generation, `--list` lists them one by one, and mark with ! silence over 15%, a gap over 4 seconds, no low frequencies), and do not let the user hear one with a problem. Adjacent nodes within the same emotion use the same piece of music (Xianyang: Han and Tang are combined into one). After laying, measure the loudness dip in the 2 seconds before and after each scene change, not by ear alone
(compile prints each scene change's dip when it lays the music, and marks 10 dB or more with !); when trimming the beginning of a piece, the start must land on a hit (a rest of more than one second after the start is warned by compile,
which also computes the offset that lands on the next hit); if you change a section that is continued from, the section that continues it must be regenerated.
When asking the user to listen, attach a table: section name, start and end in the film, node, file used, other candidates; regenerate only the section the user sends back.
The end-card credits are written in city.yaml's `end.credits`: author, voice, music (other roles can be added, adding the role name first to `credit_<role>` in each language pack).
AI-generated voice and music must be stated as "AI generated"; the same credit goes in CREDITS. Ask the user how to credit them on the end card at the same time as the voice and music are chosen.
`build/export/timeline.json` is the final timeline: every line (including voice length), every change on the model, pictures, deliberate silences, and each station's emotion; music and effects are made from it.
Order: copy final → picture → compile, preview → voice → compile again (timeline final) → music, effects → render.

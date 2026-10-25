# Script: story, treatment, copy, timeline, languages and fonts

## The most common mistakes in this step

- Writing the narration without agreeing with the user what story to tell → first produce a story outline, and write the narration and subtitles only after the user confirms it ("The director fixes the story first").
- Reporting facts one by one → first write one connected narration with contrast, echo and a landing on people ("Copy").
- Writing seconds by hand, so one change breaks everything → compile schedules the narration and the changes ("Subtitles and the timeline"; STAGING.md 9a, 9e).
- Making every station the same length, or fixing the total length first and squeezing things in → nodes have different weight ("Treatment and nodes").
- Discovering halfway that there is no story to tell, and going back to research → before writing the script, read the story material collected in research (`research/stories.md`, RESEARCH.md §3).

## The director fixes the story first

In this step you are the director of the film, not a data clerk: the data is material, and what story to tell and what the audience remembers afterwards are your choice, to be settled with the user first.
Do the following in order; go on only when the user confirms each step:

1. **Story outline:** read `research/stories.md` and the confirmed station list, and write an outline for the user to read:
   - One sentence: what kind of city the film is about and what story (Xianyang: a city that was once the centre of the world, burned into fields, shrank to a small town, and two thousand years later grew into one city with Chang'an across the river);
   - The arc of the story: which stations carry the beginning, development, turn and close;
   - The longest passages: for the most important events and people of the city, what is told in each and why it matters, and what the protagonist achieved (RESEARCH.md §2);
   - For each part: what is told, who the protagonist is, the narrator's feeling, roughly how long;
   - How the opening introduces the city and its name, and how the ending lands on the city's future;
   - For each big passage, the picture only this film can show: a fire spreading, the city shrinking inside its walls, new roads lighting up one by one,
     the city growing year by year. A story the model cannot show (an interior, a work of art, a face) is named as a picture to supply ("Pictures");
     a big passage that has no picture of its own on the model is a sign to choose another moment of the same story. Check each big passage against what this
     medium shows best: a city burning, sinking or shrinking, rising or spreading, rebuilt in place, lines of light drawn across it. If the history has such a moment
     and the outline does not use it, say why. An extent or an order known only roughly is not a reason: draw it schematic from the best description and label it
     (RESEARCH.md §6); leave out only what no source supports;
   - Prologue: which moment the opening shows the audience first, with which lines, and the question it ends on ("Prologue");
   - Pictures: which scenes get pictures, and whether to use found pictures or generated imagined ones ("Pictures").

   Until the user confirms the outline, write no narration and arrange no picture.
2. **Treatment:** write `TREATMENT.md` from the confirmed outline ("Treatment and nodes").
3. **Narration draft:** write the continuous narration for the whole film from the outline ("Copy") and show it to the user; only after confirmation cut it into subtitles and write it into `script.yaml`.
4. **Emotional line:** fix the narrator's feeling at each station from the outline (`mood`, "Emblem and emotional line"); the style of the music also comes from the outline and the emotional line (SOUND.md).

If the direction of the story has to change midway, go back to the outline and confirm it again with the user; do not patch it piecemeal on the subtitles.

## Treatment and nodes

Write `TREATMENT.md` from the confirmed outline (emblem, node table, colour logic, subtitle design, music direction), then write the nodes into `film.nodes` of `city.yaml` (node system: each node carries its own year, seconds, layers, props, pins, subtitles and camera; the film's length is the sum of the nodes).
Besides "event", the node table has a column "what the city becomes at this station" (position, shape, status, industry): cover the event column and read only this one; delete or rewrite a station whose cell is empty.
**Nodes have different weight:** a major turning point (becoming a capital, unification, destruction of the city, becoming a municipality) gets enough picture and more than one line of narration; transition stations get a few lines.
Do not make every station the same length, and do not fix the total length first and squeeze things in
(example: Xianyang's imperial capital is 77 seconds, the 1975 station 13.5 seconds). When the material is not enough, go back to research; never invent.

## Prologue

Open the film with a 15–25 second prologue that shows the audience the most striking moment of the whole film first, then tells the story from the beginning. Platforms measure an opening by "how many are left after 30 seconds";
if the first 30 seconds do not say why this city is worth watching, the audience leaves.
- The prologue is a separate piece: it has its own camera, narration and music, and differs from that scene in the main film; the city model is shared with the main film. It ends in black and cuts to the opening of the main film; no rewinding.
- Use the event with the most room and the strongest picture in the outline (Xianyang: the golden light of the imperial capital and the fire that burned the city). The camera is close and brighter than in the main film, with the subject filling the frame.
- Mostly real scenes drawn by the engine (about 70%), with one or two imagined pictures mixed in to supply the people and scenes a white model cannot give. What appears in the prologue must be seen in the main film:
  the prologue and the cover are promises to the audience.
- Two or three lines of narration, ending on a question (Xianyang: 「它從哪裡來？又怎樣活到今天？」 ("Where did it come from? And how did it live to today?")); do not give away the main film's reversal in advance (Xianyang: do not say 「只撐了15年」 ("it lasted only 15 years")).
- The music uses the same voice as in the main film (Xianyang: the drums of the imperial capital), and one sound effect from the main film may be added.
- Test: if this moment appears once more in the main film, is it better or worse? If worse, choose another moment.

Settings (`film.prologue` in `city.yaml`; the lines go in `script.yaml` under `prologue:`):

```yaml
film:
  prologue:
    dur: 20                                   # seconds before the opening; the opening and everything after it start this much later
    fade: 0.8                                 # seconds of closing black (default 0.8); the opening comes up out of it in 0.5 s
    mood: { feel: grief, level: 3 }           # for the music (build/export/timeline.json `prologue`)
    scene:                                    # from t (prologue seconds) on, the city shows the main film at <node> + at and plays on
      - { t: 0,  node: empire, at: 40 }
      - { t: 9,  node: burn,   at: 6 }
    camera: [{ t: 0, ll: [<lon>, <lat>], az: 20, el: 25, d: 0.5 }, ...]   # the prologue's own shots, t in prologue seconds
    footage: [{ id: p_fire, file: assets/imagined/<name>.jpg, mode: card, at: 11, dur: 3.5, ... }]   # same form as a node's footage, at in prologue seconds
    sfx: [{ t: 9, kind: burn }]               # one-shots of film.sfx at prologue seconds
  music: { cues: [{ id: M00, node: prologue, take: ... }, ...] }   # a cue at the prologue starts at 0; the next cue starts with the opening
```

- `scene`: only the city follows the borrowed moment (model, light rings, fire, the night sky); the camera, subtitles and pictures keep the
  prologue's own clock. Each key is a cut: pair it with a camera key at the same t. The camera jump check leaves the prologue alone (it is
  cut like a trailer).
- `script.yaml`: `prologue: [{ id, zh, en, t? }]`. A line without `t` follows the one before once it has been read; every line must end
  before the closing black (compile stops otherwise). No `with`, no `pause`.
- Check the prologue with stills (`node render/still.mjs <slug> 2 10 16`) next to the same moments of the main film: the same city, other shots.

## Pictures

Decide the pictures from the outline, not only on the main line: scenes worth a look get pictures too, such as the city at its most prosperous (Han and Tang Chang'an), the mood of a poem (Wang Wei's 「渭城朝雨」 ("morning rain at Weicheng")), the scenes of major events.
Use first the CC pictures found in the picture list (`research/images.md`, DATA.md "Pictures and footage"); for the rest, generate imagined pictures based on the sources; for how to do it and how to label it see STAGING.md "Footage and pictures".
Each picture gets one line of narration about it, and when placed it must not cover a change that is happening (STAGING.md 5b).
To generate imagined pictures: first ask the user which image-generation tools they have; if none, give the prompt to the user, who generates it with another AI and puts it in `assets/imagined/`.
If the user has the Codex CLI, it can be used: `codex exec --skip-git-repo-check -` reads the prompt from stdin; tell it to draw one 16:9 picture with its built-in image generation and copy it to
`assets/imagined/<name>.png` (in practice 1672×941, about two minutes each, can run in parallel). Each prompt states the scene and the period details (buildings, clothes, objects, terrain,
following the sources in the picture list); use one common style and negative prompt for the whole film so that the pictures look like a set.
For people with no portrait from their time: a later portrait must be labelled "後人想像" ("imagined by later generations"); photos of modern statues mostly look bad, so do not use them.

## Emblem and emotional line

The emblem (optional): borrow an object to personify the city (the brightest moment of the city, or its abstract embodiment, such as a phoenix). It is an extra, not a requirement:
if its meaning is weak, or it plays badly on the white model (a 3D object floating over the city looks like a prop), do not use it at all, or echo it once each in the opening and the ending (the opening still introduces the city and its name first);
when it is removed, remove the narration tied to it as well (Xianyang uses no emblem: `emblem: none`). If used: add make<Emblem>() in `engine/props.js` or reuse makeTally;
**the emblem must not steal the show:** it appears only at the turning points of the emotional main line, and the opening belongs to the city and its name; when a station has no time to speak of it, use only the picture, or a card with text, and add no narration.
**Declare it to compile (a hard constraint):** `film.emblem` must be written: `none`, or `{ name, meaning, nodes: [...] }`; every node must have
`mood: { feel, level }`: the narrator's feeling at this station, `wonder` (the land and the earliest people), `pride` (the city rises, heroes), `grief` (decline, destruction, loss),
`wistful` (what was hoped for did not come, farewell), `hope` (a new city grows, a new start), `calm` (the city lives quietly), with `level` 1–3. compile stops without them.
They are written into `build/export/timeline.json`, and the music rises and falls with them; compile also prints the whole emotional line (`arc:`), so you can see at a glance whether the rises and falls are right.
If `emblem: none` but tally keyframes are written, compile stops.

## Copy

First write a continuous narration for the whole film from the confirmed outline (telling the city's story, not reporting facts one by one), and cut it into subtitles after the user confirms; every **fact** the agent researched and wrote must be traceable to FACTS.md.
The narrator is an erudite, objective elder with feeling: proud when the city rises and heroes appear, sad when the city declines or is destroyed, seeing hope when a new city grows. The narrator's own feelings, judgements and associations
(「這份執念，從咸陽開始」 ("this obsession began in Xianyang"), 「盼了 10 多年的合一，就此落了空」 ("the union hoped for over 10 years came to nothing")) need no source: this is a work, not a news broadcast. The gate is only at the step of collecting material.
**It must have a story; it must not merely read out fixed facts again.** Common methods:
- Contrast: set two things side by side so the audience feels the gap by themselves (the First Emperor wanted 「二世三世至於萬世」 ("second generation, third generation, to ten thousand generations"), and the next line is 「然而，它只撐了15年」 ("Yet it lasted only 15 years")).
- Echo: plant a line early and take it back later (Han: 「帝王長眠的高原」 ("the plateau where emperors sleep") → 1991: 「帝王長眠的高原，成了飛向遠方的起點」 ("the plateau where emperors sleep became the starting point of flights to far places");
  Qin capital: 「商鞅統一了秦國的尺、斗和秤」 ("Shang Yang unified Qin's rulers, measures and scales") → imperial capital: 「文字、車軌、尺和秤，從此全天下一樣」 ("writing, axle widths, rulers and scales, from now the same under all heaven");
  imperial capital: 「渭水是天河，橫橋是牽牛」 ("the Wei is the Heavenly River, the Heng Bridge is the Cowherd star") →
  ending: 「兩座城沒有合併，卻長成同一座城，就像2000多年前，渭水兩岸本是一座咸陽」 ("the two cities did not merge, yet grew into one city, just as over 2,000 years ago the two banks of the Wei were one Xianyang")).
- Landing on people: end a passage of facts with a line about a person's situation (after the state cotton mill restructuring, 「一代紡織人的青春，就留在了這裡」 ("a generation of textile workers left their youth here")).

## Writing subtitles and readouts

- Length of one subtitle: Chinese characters ≤22 characters (CJK ≤22 characters), English ≤70 characters, other scripts follow the limit in `i18n/<code>.yaml`.
- One fact per subtitle, the first language on top and the second language below ("Languages"); write "傳說" ("legend"), "可能" ("possibly"), "示意" ("schematic") for what is uncertain.
- **Numbers are always Arabic numerals 0–9, in every language:** years, dates, times of day, quantities, measures, percentages, ordinals (Line 1, Phase 3). Write them that way from the start of the narration, not by changing them afterwards:
  do not use Chinese numerals (一九八三年, 八百八十二), Japanese kanji numerals, Arabic-Indic digits (٠١٢٣), Persian digits, Devanagari (०१२), Thai (๐๑๒) or any other script's own digit characters,
  and no full-width digits (１２３) either. The film is for audiences of different languages, and numbers are the common part.
  The only exceptions are proper nouns and fixed expressions: names of plans or events (「十五五」 ("the 15th Five-Year Plan")), idioms and set phrases (一座又一座, 一層一層), quotations (「火三月不滅」 ("the fire burned for three months")),
  and **historical dating in the original form:** regnal-era years (洪武四年, 乾隆十六年, 武德二年), sexagenary-cycle years, years of other calendars. Do not convert them to the Common Era in the narration:
  the Common Era year is already on the year panel on the left of the screen, and keeping the original dating gives the flavour of the period.
  Write the exceptions into `film.copy.keep` in city.yaml, and the copy check stops mentioning them.
- The readout (left column) holds only one big number (the year counter or one statistic), one label line, one source line.
- Reading-time rule: Chinese characters ÷ 4.5 + English letters ÷ 15 + 1.5 seconds, at least 1.8 seconds; stretch the film rather than delete facts.

## Subtitles and the timeline

**Subtitles are written in `cities/<slug>/script.yaml`** (`templates/script.yaml`; city.yaml holds only the picture), one name (id) per line, in the order spoken.
**compile schedules the time; never write seconds by hand** (`schedule_lines`):
- A line that talks about a particular picture gets `with:` and is spoken only when that picture appears: `shot:<shot name of a camera keyframe>`, `pin:<tag>`, `card:<card>`, `stage[:<stage name>]`, `node`;
  `lead:` brings it forward by some seconds (a negative number delays it).
- Other lines have no time: they follow when the line before has been read (0.35 seconds between), and may run into the camera's hold; the first line of a node comes 0.5 seconds after the node is reached.
- `{ pause: seconds, why: "..." }`: a deliberate silence (it does not count as dead air).
- Pictures can also follow lines: cards, routes, areas, map lines, projections and a city's growth stages get `with: <line id>` (`plus:` is some seconds later);
  tags and sections with `with:` show from the start of that line to its end (or `until: <line id>`) plus `hold` seconds. "The end of that line" is the subtitle's own length,
  without the 0.4 seconds (`extra`) the subtitle stays after being read: to close together with the subtitle, add 0.4 to `hold`.
  When an area has `with:`, its outline starts at that line, the name appears afterwards and stays until the node ends (if `until`/`hold` are written, it follows the tag's rule); `flash` can also be written as `{ with: <line id>, plus: seconds }`.
- `t:` (the second of the node's picture): follows picture time, and is pushed later when the planner inserts holds. Use it only to wait deliberately for a breath.
- A line that introduces a picture must have `with:` that picture; when a picture (starfield, image, section) is delayed or brought forward, look at the camera hold and tag times of the same stretch together
  (if the picture is delayed but the camera does not hold longer, the tag follows the camera into the subtitle band).
compile writes `build/logs/copy.txt`, the copy check, with suggestions "add a line" and "cut" (suggestions only; it does not change the copy):
`add`: a long time with no text while the picture names a place (pin, area, beam, star group) that no line mentions, or a silence that is too long; `cut`: a line over 22 characters, three or more lines in 20 seconds with almost no gap,
the same statement made twice; `style`: should use Arabic numerals 0–9 (years, dates, quantities, measures; Chinese numerals, full-width digits and other scripts' own digits all count); `check`: mentions a year later than this station (if deliberate, write `later: true` on that line).
Deliberate silences are written in `quiet:` of script.yaml. The thresholds are in city.yaml `film.copy`.
compile also writes `build/export/`: `.srt` and `.vtt` for the bilingual and for each language, and `script_timed.tsv` (for each line: start, end, seconds to the next line, seconds needed to read it: for voice recording).
The number check also scans on-screen text other than subtitles (pins, readouts, place names, photo captions, beam labels, the end card). Proper nouns and quotations that keep the original form go in `film.copy.keep`
(Xianyang: 十五五, 國棉一廠 (State Cotton Mill No. 1), 火三月不滅).
**Change copy as a draft first:** save the draft separately (for example `build/review/script_draft.yaml`), compile the draft with `CT_SCRIPT=<draft> uv run python -I pipeline/compile.py cities/<slug>`
and look at it in the preview, leaving script.yaml untouched; give the user a before-and-after comparison line by line, and swap it into script.yaml only after confirmation.
Each subtitle stays at least Chinese characters ÷ 4.5 + English letters ÷ 15 + 1.5 seconds. When earlier lines cannot be finished, compile inserts time only where needed (before the picture that line has to wait for,
and the picture waits along; if the last line cannot be finished, the node is lengthened), and does not stretch the whole node proportionally. The last node must be the current year (compile warns if it is not).
When the second language's subtitle exceeds the single-line safe width (subcheck prints WIDE), split it into two lines with an id each; do not delete words and do not shrink the type size.

## Numbers on screen

Numbers on screen that are decided by geometry or settings must not be written by hand: for the distance between two points use `[km]`; `{…}` in text can take `{plate_km[0]:.0f}` (plate width, depth in km),
`{cfg.terrain.exaggeration:g}` (any setting in city.yaml, for example the exaggeration), `{km('id')}` (length of a line or perimeter of an area, in km), `{km2('id')}` (area of an area, in
square km; the id is of a research area, an epoch or a line), `{stats.…}` (this is how Xianyang writes its plate size and the far-terrain exaggeration). Numbers given by the sources are written as the sources give them, not replaced by what the schematic model measures
(Xianyang palace city perimeter: the report says 2747 metres, the readout says about 2.7 km; the schematic frame measures 2.77 km). Where no placeholder can fetch the number (the imagery source), when you change settings or geometry, change the readout, the opening note, the end card and CREDITS at the same time. Before changing
the model's geometry (moving a wall, moving the frame, changing a plot), first look up the numbers that the subtitles and readouts state about it, and after the change they must still match (example: moving only one wall makes the perimeter disagree with the readout, so shift the whole frame instead).

## Fonts

**Fonts are set per job in city.yaml** (`film.fonts`, nine jobs: first-language title and subtitle `primary_strong`, body `primary`, two sans-serif `primary_sans` / `primary_sans_strong`, two for big numerals `numeral` / `numeral_strong`,
two for the second language `secondary` / `secondary_strong`, small monospace `mono`), giving a font name and weight; compile looks in `fonts/` by the name inside the font file, and reports an error, never letting the browser fill in a system font, if the font is not found, has no such weight,
or the copy contains a character the font cannot draw (if only the characters used by the film were stored, changing the copy would turn new characters into system-font characters, and one subtitle line would have uneven weight). `fonts/` holds only complete fonts under licences that allow redistribution (SIL OFL 1.1, Apache 2.0),
committed to git together with the licence text; add a new font with `uv run python -I pipeline/fonts.py add . "<Family>"` (fetched from the Google open-source font library), and see what exists with `fonts.py list .`.
Test weights, do not follow the suggestion list: render 3 seconds with the official pipeline (final film crf 19, then recompress to simulate platforms at 4 Mbps and 2.5 Mbps) and measure: still subtitles change only 0.2–0.4 grey levels frame to frame,
and thin strokes do not flicker with compression; the real problem is that English weight 200 is almost invisible over bright buildings, so use at least 300. When changing a font or weight, likewise render a few seconds and look first.

## Languages

**Languages** (`film.lang`, one or two, any language that has a language pack, not limited to Chinese and English). Language packs are in `i18n/<code>.yaml`
(existing: zh, zh-Hant, en, ja, ko, fr): script, the maximum length of a subtitle, number rules, how years are written (前 350, 紀元前350年, 기원전 350년, 350 BCE),
and the words the program itself puts on screen (今天 (today), 實拍 (live footage), 想像圖 (imagined picture), 新建 (new), 長高 (taller), CHAPTER, LOCATOR). New language: copy a language pack and translate it, and check with `uv run python -I pipeline/i18n.py`.
- The city's own words: every line of narration needs every language (script.yaml); pins, place names and card titles are written per language (`zh:`, `ja:`…); readouts, identity, end card, sections and sources
  can be written in one language (the first) or per language (`{ ja: ..., en: ... }`). If any text on screen lacks a language, compile lists it and stops.
- Reading time by script: Chinese characters and kana 4.5 characters per second, Hangul 6 syllables per second, letters 15 per second; subtitle size by script (first line: Chinese 38, Latin 34; second line: Latin 30, Chinese 32).
- The font must be able to draw that language (compile checks, and stops on a missing glyph): for Japanese, the Source Han Serif SC used has kana; for Korean choose another font that has Hangul.
- Right-to-left scripts (Arabic, Hebrew) are not supported yet: compile stops when it meets them.
- A first language other than Chinese has been through only a short test (Japanese-English: subtitles, years, counter, missing-glyph errors all correct), and no real film yet; look more closely at every passage the first time.
- Default choice of language: a city that is not English-speaking uses the local language + English (the local language is the first language, the big-type line); an English-speaking city uses English only (`lang: [en]`). If the user specifies otherwise, follow the user.

# Research: timeline, selection, story material and sources

Goal: the user gives only a city and a starting era. The agent finds the timeline, the choice of stations, the through-line, the story material and the geometry itself, and every item can be traced back to its source.
Research is the script's stock room: the events, people, stories and the locals' feelings that the script will need are collected in this step, so that writing the script does not require going back to look things up.

## The most common mistakes in this step

- Filling in a generic dynasty table (Neolithic → Qin → Han → Tang → Ming → railway) with every station weighted the same → first answer the questions in §2; every station must be this city's own.
- Collecting only dry records of "what happened in which year" → collect the course of events, people, details and the locals' feelings together (§3), or there will be no story to tell when the script is written.
- Making archaeological digs or tombs into stations; putting connections such as bridges, roads and subways too early → follow the priority order in §2.
- Letting the story stop at today's statistics → tell it up to this year and end on the city's future (§4).
- Lists pasted by subagents and the user contain many errors → go back to the original text item by item (§4, §7).
- Writing the music, clothes and objects of "that era" from impression → first find out what actually existed in that era (§8).

## 1. How to do it

1. Build the timeline with WebSearch / WebFetch, with a URL and the original text for every fact (research subagents may be used; brief them as in §7).
2. Answer the questions in §2, then choose the stations and the through-line (§5).
3. Collect story material for each station (§3).
4. Write the results into the city folder: `FACTS.md` (the source of every claim on screen) and `research/` (notes, reports, source texts, `stories.md`, `images.md`),
   which go into git with the city: they are this city's data, not temporary files.
5. Open the original text yourself once more for the key facts: the opening and the ending, every year shown on screen, people's and places' names, quotations.
6. **Show the user the story first, then the station table**, and go to the next step only when the user approves:
   - one sentence that says what the city wins, loses and becomes (the stakes), not an abstract theme such as "a city that keeps rewriting itself";
   - the shape: the highest peak, the deepest fall, where the film turns, and the narrator's feeling rising and falling across the stations;
   - the two or three big passages (minutes each), the people who drive them and the picture only this film can show for each (SCRIPT.md),
     and which stations are short transitions;
   - the opening and the ending (the city's future, and an echo of an earlier station if there is one);
   - then the table: for each station the year, what happens and what the city becomes, the story and its people, big or short, and the status of the sources.

## 2. Selection: what is worth telling

The weight of history comes from two things: the turning points the city went through, and the events and people that matter greatly to the city and deserve to be remembered. The number of archaeological finds is not weight.
In order of priority:

1. **Status and major events:** founding the city, becoming a capital, unification, moving the capital, becoming a municipality, promotion in rank, and events that happened here and matter greatly to the city
   (Xianyang: Qin unified the six states and Xianyang became the capital of the first unified empire; Xiang Yu burned the city).
2. **People and stories:** people who made decisions or left stories here, and stories that happened here (Xianyang: King Ying Zheng of Qin destroyed the six states, took the title First Emperor and founded China's first unified empire here; Shang Yang moved the capital to Xianyang and carried out his reforms here; Wang Wei saw off a friend at Weicheng).
3. **Rise and fall:** prosperity, war, decline, rebuilding.
4. **Urban form:** new districts, new towns, lakes, river channels, the direction the city grew.
5. **Industry:** the rise, peak, decline and transformation of an industry (Xianyang: textile city → electronics city → state cotton mill restructuring → Western Screen Valley).
6. **Connections** (considered last): bridges, railways, airports, subways, area codes. They become a station only if they changed the city's fate or carry a story themselves
   (Xianyang: the 029 area code merger, which carried the hope of the two cities becoming one).

Test: if this station is removed, does the audience understand a piece less of "who this city is, what it went through, how it became today"? If not, it is not a station.

**Give major events enough room:** the most glorious or most painful moment of a city is not a station carried by one line of narration; it can be a story of several minutes.
Research it thoroughly at this stage: causes, course, key people, details, the effect on the city (Xianyang: King Ying Zheng of Qin destroyed the six states in 10 years and took the title First Emperor, dividing the world into 36 commanderies;
for every state he destroyed, he rebuilt its palaces as exact copies on the north slope of Xianyang, and moved 120,000 of the richest households under heaven to Xianyang; writing, axle widths and weights and measures were unified from here for the whole world).
Tell the protagonist of such an event fully too: what he achieved and why it matters; write the disputed points as facts according to the sources, and do not use him only as a contrast to the decline that follows.

**Tell an epic, not a list of public works.** Choose the stations as the film's director already: the city is the protagonist, and it has stakes. An epic has a rise,
a peak, a fall or a loss, a return and a future; name the people who drove each of them (rulers, builders, invaders, saints, artists, ordinary residents whose words survive).
A station whose story is a building programme, an administrative act or a planning policy is a short transition at most, unless something was won or lost there.
Compress a stretch without drama, but never leave the modern era empty: the city growing building by building from the first year of the data
(GHSL: 1975) is one of this film's signature pictures (STAGING.md 9i), and the story must reach this year. Give the decades of living memory their own
stations (new districts, industries that rose or fell, events that shook the city, the people of those years), and end on this year and the future. Test: read the station table aloud as one story; if it sounds like a list of projects, rewrite it.

**First find what makes this city different from other cities, then decide the structure.** Before fixing the stations, answer these questions; the answers decide the opening, the longest passages, the unique scene and the ending:
1. Where the name comes from: say it in the opening (Xianyang: Mount Jiuzong to the north and the Wei river to the south, so mountain and water are both "yang").
2. What are the most important and most memorable events and people for this city: they are the longest passages of the film.
3. What planning or geography does it have that other cities do not: give it a scene (STAGING.md rule 8; Xianyang: Qin Xianyang modelled on heaven and earth, the terraces of the Xianyang plateau).
4. Was the city site moved, and how: staying put and moving are both stories (Chengdu has not moved in over 2,000 years; Xianyang moved several times).
5. What identities history has given it (Xianyang: Qin capital, imperial capital, Weicheng, county town, textile city, electronics city, airport city).
6. Is there something that is there from start to finish (the through-line in §5; for the optional emblem see SCRIPT.md).
7. What its future is: what is being built, what is planned, what the locals look forward to (the outlook at the end, §4).

Do not fill the station list in generic dynasty order; every station must be this city's own.

**Archaeology and tombs:** they become a station only when they changed the city itself, for example the conflict between new-town construction and site protection, or a site that became a city park or landmark. An excavation by itself, find counts
and tombs are never a station of their own, at most a sentence inside one. When the ancient part is about the city, archaeology is the source of "how we know", not the story itself.

**Every station needs a place on the model:** a region (a district, new town, factory area, protected area), a line (a bridge, subway, railway) or a point; a point is enough.
The station's story is what happened and who did it; the model shows where. Do not choose stations for what can be built on the model. Facts and stories that have no place
go into the narration and are matched with the picture of the station they belong to; they do not become a station of their own.

The Xianyang 1975–2026 example: Rainbow factory (electronics city), becoming a municipality and its districts, the airport, state cotton mill restructuring, Xianyang Lake, the 029 merger, Qin-Han New City and the site protection area, Xixian New Area,
the subway into Xianyang, two cities one line, the "15th Five-Year Plan" and Western Screen Valley. Counter-examples: fire in the treasury, an ancient tomb under the airport, a newly announced tomb (archaeological detail, not a turning point of the city).

## 3. Story material: collect here what the script will use

Record not only "what happened" but also what makes it a story, in `research/stories.md`, one section per station:

- **People:** who made what decision here and what they said; quote their words exactly, with the source.
- **Scenes and details:** how it looked then, the scale, numbers, objects, sounds (Xianyang: 「每破諸侯，寫放其宮室，作之咸陽北阪上」 ("whenever he broke a feudal lord, he copied that lord's palaces and built them on the north slope of Xianyang")).
- **The feelings of this city's people:** what they hoped for, what they lost, why they are proud. Local gazetteers, news interviews, commentary and oral accounts can all be sources.
  Example: Xianyang and Xi'an are too close and their history is too entangled. After the 029 merger in 2006, Xianyang people hoped the two cities would become one and the old glory would return; in 2017 the Xixian New Area was handed to Xi'an to administer,
  the finest piece of land went to Xi'an, and a merger would never happen. So the 2017 line is wistful, not a neutral administrative change.
  These feelings decide the narrator's emotion and also how the ending closes (Xianyang: the two cities did not merge, yet grew together).
- **Poems and allusions:** poems, idioms and legends about this place (Xianyang: Wang Wei's 《送元二使安西》 (Seeing Yuan the Second Off to Anxi) and its 「渭城朝雨」 ("morning rain at Weicheng")). Mark legends as "legend".
- **Scenes worth a picture:** the city at its most prosperous, the scenes of major events, the mood of a poem; note the source where there is a picture, and mark the scene even where there is none (DATA.md "Pictures and footage").
- **Threads that can echo:** an early event and a later one that can be set against each other (Xianyang: in Qin times the two banks of the Wei were one Xianyang; over 2,000 years later Xianyang and Xi'an grew into one city across the Wei).

The sources for story material are held to the same standard as facts (the status marks in §4): they need not be official records; verifiable reports, interviews, gazetteers and scholars' works are all fine;
do not collect what has no source. Use `stories.md` first when writing the script; when it is not enough, go back to this step and research more; never invent.

## 4. The timeline

From the starting era to today, each entry has: year (BCE as a negative number), event, source URL, the original quotation, a status mark.
Status: [OK] original text opened; [SEC] only Wikipedia or a search summary; [WEAK] tourism or aggregator site; [EST] estimate.
Only [OK] and [SEC] may go on screen; for the key years of a [SEC] entry find one more source or note it in FACTS.md. When two sources conflict, record both and use the more conservative wording on screen.
Copy numbers as in the original (for checking); for how to write them in the narration see SCRIPT.md.

**Tell it up to this year, and close on the future:** the last station reaches this year (the latest government work report, statistical bulletin, this year's major events); the ending must land on the city's future:
what is being built, what is planned, what the locals look forward to, and only then is the story complete. The outlook needs sources too: write a plan as a plan and an expectation as an expectation, never as already done.

These requirements bind the agent's own research and govern facts. The narrator's feelings, judgements and associations need no source (that is the voice of the work), but a feeling must not be written as a new fact.
Copy the user writes themselves (local history, family memory, material not online) is used as is without demanding a source; raise it only when it contradicts data you found.
Material the user pastes from elsewhere (a list from another agent, a web article, a chronology) is not the user's own copy: treat it as leads, go back to the original item by item as in this section, and keep off the screen whatever cannot be found;
when what you find differs from what was pasted, write what you found and tell the user. Practices it suggests are adopted only after testing (example: a pasted Xianyang modern station list kept only three and a half items after checking:
"the textile street" had no source; "Western Display Valley" was actually "Western Screen Valley"; "2019 subway era" had to be told in two steps, crossing the boundary in 2019 and entering the main city in 2023).

## 5. The through-line (anchor)

Find something that has existed from the start and can still be seen today, so the audience recognises the same city in every era: a river and its ferry crossing, a plateau, an axis, a city gate,
an industry that continues. The Chengdu model: the Jinsha site, buried 3,000 years ago and dug up during construction in 2001, whose Sun Bird became the city emblem (archaeology counts here because it became a symbol of the city).
Scoring order:
1. Its changes are themselves turning points of the city (moved, rebuilt, abandoned, reused), each with a clear year.
2. It lies within the model extent (otherwise it can only be a prologue or use an edge signpost).
3. Its source is official, scholarly or mainstream media original text, not a tourism site.
4. Better still if the echo can repeat (for example in Xianyang: the Wei river's ferries, bridges, lake and subway rewrite the relation between the two banks again and again).

## 6. Geometry

Check OSM first: `historic=*`, `site_type`, `archaeological_site`, `tomb`, `citywalls`, protected-area polygons (the historic theme of pipeline/osm.py already fetches them).
Use an outline where one exists (`osm_polygons:` / `mounds: osm:`) and record the way id in FACTS.md.
Where there is no outline, draw a schematic polygon from the literature (`polygons:`) and label it "schematic" on screen. A point with no coordinates is mentioned only in a subtitle, with no pin.
For an area a subtitle names (an administrative district, new area, new town, factory area, protected area), find the boundary: OSM administrative boundaries, official planning maps, the townships and streets it is made of; if none is found, draw a schematic one from the description of its four limits.
Write everything into `research/<topic>_areas.geojson` (properties.id, status, source), and record the source and method of each item in the research file.
Earthworks and platforms that still exist today, such as mounds, are built as real geometry with `mounds:` (base from the OSM outline, height from the literature, a customary value where nothing is recorded, with a note).

## 7. Briefing research subagents

- The brief begins with the selection rules and priority order of §2: status and major events, people and stories first, connections last; archaeology and tombs are listed only when they changed the city.
- Name the output files and sections: timeline, story material (§3), coordinate table, ranking of anchor candidates, numbers, a list of unverified items.
- Require a URL and the original text for every item; require a distinction between original text and the fetcher's summary ([PARAPHRASE]); story material also carries sources (a person's own words, gazetteer, interview).
- Government sites are often unreachable: have the subagent note the URL, and the main agent tries again or uses a news reprint.
- The main agent must check again itself: the anchor event, every year shown on screen, people's and places' names, and qualifiers where one word makes the sentence wrong ("international", "first", "into the urban area").
  An entry with no original text attached counts as unverified (example: in a 15-item Xianyang list, the year Xianyang Lake was filled, subway phase 2 "into the urban area", the word "international" for the airport, and "China's first colour picture tube"
  were all wrong or had no source).
- The output path is `cities/<slug>/research/` (notes, reports and source texts all go there; separate notes of music research go in `research/music_notes/`), and it goes into git with the city.
  After a summary is written, the original notes stay as they are: the summary has no item-by-item sources and original text.

## 8. Period feel: first find out what actually existed then

For music, clothes, objects, architectural details and prompts for imagined pictures, before writing, research what actually existed in that era and place, separating evidence (excavated, primary text), inference and modern convention,
and write it into `research/<topic>.md` with a source for each item. An "ancient style" written from impression is mostly an anachronism.
Example (Xianyang, `cities/xianyang/research/music.md`): from impression one would use the xiao flute and guqin as the city's sound, French horn and low brass for the Qin section, and erhu for the burning of the city; research showed that Qin has Li Si's 「擊甕叩缶彈箏搏髀」 ("striking jars and pots, plucking the zheng, slapping the thigh"), the drums of the terracotta army pits,
the Qin bells and bianzhong and stone chimes; brass and erhu are anachronisms, and no local basis for the xiao and guqin can be found in Guanzhong. In the end: drum as pulse, xun as memory, zheng as the voice of Qin.

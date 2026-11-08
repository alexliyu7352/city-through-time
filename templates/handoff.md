# Handoff: <city>, round <n>

What a new session needs to do this round, and nothing else. Written when the round's list is set; the session that takes the
round starts here, not from the old conversation (SKILL.md "A round of revisions starts with a fresh context").

## The version to compare against
The last version the user passed (a city folder or a candidate), and what of it the user has seen and passed: the
`--against` of `tools/round.py`. The round builds on the latest candidate: keep the fixes already accepted in it, and redo only what was sent back.

## The round's list (frozen)
Each note as the user gave it, with the place in the film (station, line id, seconds) and the decision taken on it, if any.
A note that comes during the round goes to the next round's list, unless it is small and touches nothing in progress, or the user wants it now (list it in the report).

## What must not change
The approved narration and subtitles, approved stations and models, anything the user has passed; the outputs the user is
looking at (the preview being watched).

## Where the work is
The candidate's folder, the files it is made from (city.yaml, script.yaml, the scripts that build it), the shared tools'
version (git commit).

## Known limits and open questions
What the last round could not do and why (a tool's gap reported, a picture with no open licence), decisions still to ask the user.

## Next
The first command of the round, and the one that checks it:
`uv run python -I tools/round.py <slug> --against <version>`.

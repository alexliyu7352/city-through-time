# A City Through Time · 一城春秋 — the skill

An agent skill that makes a city's film through time: the city's history from the sources, today's buildings from open map
data, and the city of each era lit up on a white model, with narration, music and subtitles.
- Films and the project: https://cities.go5.si
- The code, rules and finished cities (the workspace): https://github.com/alexliyu7352/city-through-time

This repository holds only the skill. On first use the agent clones the workspace where you choose, sets up its tools and
starts your city. You answer its questions and approve the story and the film.

## Install

Any agent that reads skills (Claude Code, Codex, Cursor, Gemini CLI and others), with the [skills CLI](https://skills.sh):

```sh
npx skills add alexliyu7352/city-through-time-skill -g
```

Claude Code, as a plugin:

```
/plugin marketplace add alexliyu7352/city-through-time-skill
/plugin install city-through-time@city-through-time
```

Then say: "Use A City Through Time to make <city>, starting from <era>."

You need Node 20 or newer, [uv](https://docs.astral.sh/uv/), ffmpeg, exiftool, git, and a computer with a graphics card and Chrome.

## 安裝（繁體中文）

這個倉庫只放技能本身。第一次使用時，代理會把工作區（[city-through-time](https://github.com/alexliyu7352/city-through-time)：程式、規則和已做好的城市）clone 到你指定的位置，裝好環境，再開始做你的城市。

```sh
npx skills add alexliyu7352/city-through-time-skill -g
```

或在 Claude Code 裡：`/plugin marketplace add alexliyu7352/city-through-time-skill`，再 `/plugin install city-through-time@city-through-time`。

然後說：「用一城春秋做〇〇，從〇〇時代開始」。

## 安装（简体中文）

这个仓库只放技能本身。第一次使用时，代理会把工作区（[city-through-time](https://github.com/alexliyu7352/city-through-time)：代码、规则和已做好的城市）clone 到你指定的位置，装好环境，再开始做你的城市。

```sh
npx skills add alexliyu7352/city-through-time-skill -g
```

或在 Claude Code 里：`/plugin marketplace add alexliyu7352/city-through-time-skill`，再 `/plugin install city-through-time@city-through-time`。

然后说：「用一城春秋做〇〇，从〇〇时代开始」。

---

This repository is published from the `skill/` folder of the workspace repository (`git subtree push --prefix=skill`);
change it there.

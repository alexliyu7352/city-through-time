# A City Through Time · 一城春秋 — the skill

An agent skill that makes a city's film through time: the city's history from the sources, today's buildings from open map
data, and the city of each era lit up on a white model, with narration, music and subtitles.
- Films and the project: https://cities.go5.si (so far Xianyang and Rome)
- Project introduction video: [English](https://www.youtube.com/watch?v=ZeqlfaAadHg) · [中文](https://www.youtube.com/watch?v=CbMU4t607tc)
- The code, rules and finished cities (the workspace): https://github.com/alexliyu7352/city-through-time

This repository holds only the skill. On first use the agent clones the workspace where you choose, sets up its tools and
starts your city. You answer its questions and approve the story and the film.

## Install

Every agent on this computer that reads skills (Claude Code, Codex, Cursor, Gemini CLI and others), with the [skills CLI](https://skills.sh):

```sh
npx skills add alexliyu7352/city-through-time-skill -g -y
```

Run it in a terminal: it installs the skill for every agent it finds on this computer (Claude Code, Codex, Cursor, Gemini CLI and others) and into the shared `~/.agents/skills`. Run from inside an agent, it installs for that agent alone.

Claude Code, as a plugin:

```
/plugin marketplace add alexliyu7352/city-through-time-skill
/plugin install city-through-time@city-through-time
```

Then say: "Use A City Through Time to make <city>, starting from <era>."

You need Node 20 or newer, [uv](https://docs.astral.sh/uv/), ffmpeg, exiftool, git, and a computer with a graphics card and Chrome.

## 安裝（繁體中文）

這個倉庫只放技能本身。第一次使用時，代理會把工作區（[city-through-time](https://github.com/alexliyu7352/city-through-time)：程式、規則和已做好的城市）clone 到你指定的位置，裝好環境，再開始做你的城市。

專案介紹影片：[中文](https://www.youtube.com/watch?v=CbMU4t607tc) · [English](https://www.youtube.com/watch?v=ZeqlfaAadHg)。已經做好的片：[咸陽](https://cities.go5.si/xianyang/)、[羅馬](https://cities.go5.si/rome/)。

```sh
npx skills add alexliyu7352/city-through-time-skill -g -y
```

在終端機裡執行：它會替這台電腦上找得到的每個代理（Claude Code、Codex、Cursor、Gemini CLI 等）都裝上，也裝進共用的 `~/.agents/skills`。在某個代理裡面執行的話，只會裝給那一個代理。

或在 Claude Code 裡：`/plugin marketplace add alexliyu7352/city-through-time-skill`，再 `/plugin install city-through-time@city-through-time`。

然後說：「用一城春秋做〇〇，從〇〇時代開始」。

## 安装（简体中文）

这个仓库只放技能本身。第一次使用时，代理会把工作区（[city-through-time](https://github.com/alexliyu7352/city-through-time)：代码、规则和已做好的城市）clone 到你指定的位置，装好环境，再开始做你的城市。

项目介绍视频：[中文](https://www.youtube.com/watch?v=CbMU4t607tc) · [English](https://www.youtube.com/watch?v=ZeqlfaAadHg)。已经做好的片：[咸阳](https://cities.go5.si/xianyang/)、[罗马](https://cities.go5.si/rome/)。

```sh
npx skills add alexliyu7352/city-through-time-skill -g -y
```

在终端里运行：它会给这台电脑上找得到的每个代理（Claude Code、Codex、Cursor、Gemini CLI 等）都装上，也装进共用的 `~/.agents/skills`。在某个代理里面运行的话，只会装给那一个代理。

或在 Claude Code 里：`/plugin marketplace add alexliyu7352/city-through-time-skill`，再 `/plugin install city-through-time@city-through-time`。

然后说：「用一城春秋做〇〇，从〇〇时代开始」。

---

This repository is published from the `skill/` folder of the workspace repository (`git subtree push --prefix=skill`);
change it there.

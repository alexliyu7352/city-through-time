# 参与《一城春秋》

[English](CONTRIBUTING.md) · [繁體中文](CONTRIBUTING.zh-Hant.md) · 简体中文

两种参与方式：**交一座城市**，让它出现在入口页；或**改进代码与技能**。

## 交一座城市

这个仓库只收文本数据：城市的配置、文案、史实出处、版权说明和研究笔记。成片、播放包、海报、图片、音乐都放在外部（视频网站、Hugging Face、你自己的 GitHub Pages），入口页只是链接过去。咸阳是本项目的示例，文件夹里保留了图片、海报和网页播放包（`cities/xianyang/web/`，入口页直接从 GitHub Pages 播放），方便从头到尾照着做一遍；提交的城市不用照它放。

### 1. 先把片做出来

照 [`docs/MAKING.zh-Hans.md`](docs/MAKING.zh-Hans.md) 做完一部片，`node tools/build.mjs <城市>` 的检查都要通过。

### 2. 上传视频

把 `cities/<城市>/dist/<城市>.mp4` 上传到 YouTube、B 站或其他视频网站，标题和说明可以直接用 `dist/description.md`。视频网址之后填进 `entry.json` 的 `watch`。

### 3. 网页播放包和海报

有播放包，观众就能在入口页直接用浏览器播放，而且可以拖动、暂停、开关旁白和配乐。播放包可以不做，但海报一定要放在外部某个地方，入口页的馆藏要用。

```sh
uv run python -I tools/web.py cities/<城市>
```

它会把播放器需要的文件打包到 `cities/<城市>/dist/web/`（咸阳约 121 MB），只收页面真的会读的文件：没有 WAV，也没有内部测试用的图。海报也在里面：`poster.jpg`（1280 宽）和 `poster_thumb.webp`（640 宽，馆藏和搜索用）。只放视频、不做播放包时，就把这两张图单独放上去。字体不在包里，播放器会从本项目的 `fonts/` 读（用了新字体的城市，要在 pull request 里把字体加进 `fonts/`）。

放播放包的地方必须**允许网页跨域读取**。以下两种都可以：

**Hugging Face 数据集（建议）**：公开数据集免费，大文件没问题。

```sh
uvx --from huggingface_hub hf auth login
uvx --from huggingface_hub hf upload <你的帐号>/city-through-time-bundles cities/<城市>/dist/web <城市> --repo-type dataset
```

播放包网址：`https://huggingface.co/datasets/<你的帐号>/city-through-time-bundles/resolve/main/<城市>/`

**你自己的 GitHub 仓库，开 GitHub Pages**：建一个公开仓库，把 `dist/web/` 里的东西放进 `<城市>/` 文件夹，在仓库的 Settings → Pages 选从 main 分支发布。限制：单个文件 100 MB 以内、整个网站 1 GB 以内。

播放包网址：`https://<你的帐号>.github.io/<仓库名>/<城市>/`

其他静态主机（例如 Cloudflare R2）也可以，只要响应带 `Access-Control-Allow-Origin`。

**上传前先确认**：配音、配乐用的服务，条款允许公开分发生成的音频文件，并写进 `CREDITS`。

**试播**：在入口页网址后面接 `play.html?city=<城市>&play=1&bundle=<播放包网址>`，能从头播到尾才算数。

### 4. 写 `cities/<城市>/entry.json`

入口页靠这份文件认得你的城市。先让工具从视频生成草稿：

```sh
uv run python -I tools/web.py cities/<城市> --entry
```

它会写出 `cities/<城市>/entry.json`，填好位置、年代、片长、语言和各章的颜色，其他的你补上：


| 字段 | 内容 |
|---|---|
| `slug` | 城市文件夹的名字（小写英文、数字、连字符），也是城市页的网址：`https://cities.go5.si/<slug>/`。不能和网站自己的文件夹或语言代码同名（例如 `site`、`ja`），检查会拦住 |
| `name` | 城市名，五种语言：`en`、`ja`、`zh-Hant`、`zh-Hans`、`es`（缺的会改用英文） |
| `location` | `[经度, 纬度]` |
| `years` | `[起, 迄]`，公元前用负数 |
| `duration` | 片长（秒） |
| `narration`、`subtitles` | 旁白语言、字幕语言（语言代码，例如 `zh`、`en`） |
| `authors` | `[{ "name": "…", "url": "…" }]` |
| `summary` | 两三句简介，语言同 `name` |
| `poster` | 海报的 https 网址（1280 宽），例如 `<播放包网址>poster.jpg`（示例城市咸阳用仓库里的路径） |
| `thumb` | 小图的 https 网址（640 宽），例如 `<播放包网址>poster_thumb.webp` |
| `watch` | `[{ "site": "YouTube", "url": "…" }, { "site": "Bilibili", "url": "…" }]`：发布到几个网站就填几个，入口页全部列出，**第一个是默认**（“观看影片”播它）。贴平常的视频网址（不要带开始时间）；YouTube 和 B 站会在入口页里嵌入播放，播放窗口里可以切换网站，其他网站显示成链接 |
| `bundle` | `{ "url": "播放包网址", "mb": 121 }`，没有就填 `null` |
| `download` | （可选）`{ "url": "…" }`，视频文件的下载网址 |
| `ai` | AI 生成的部分：`narration`、`music`、`imagined` |
| `license` | `CC BY-SA 4.0` |
| `chapters` | 各章的开始秒数、年份和颜色（工具生成，入口页画成色带） |
| `added` | 加入的日期，`YYYY-MM-DD`（馆藏最新的排前面） |

`watch` 和 `bundle` 至少要有一个；两个都还没有时，入口页会显示“影片正在上架”。

入口页读的 `cities.json` 和每座城的独立页面都不用你写：每次合并到 main，GitHub Actions 会从所有城市的 `entry.json` 自动生成（`tools/site.mjs`）。城市页有五种语言，英文在 `https://cities.go5.si/<slug>/`，其他语言在 `/ja/<slug>/`、`/zh-hant/<slug>/`、`/zh-hans/<slug>/`、`/es/<slug>/`；标题、简介、分享预览图（海报）和视频信息都写在页面里，贴到社交网站会显示这座城的预览，搜索引擎也找得到。本地用 `node tools/preview.mjs` 预览时会先生成一份到 `_site/`，打开 `http://127.0.0.1:8765/<slug>/` 就能看到。

### 5. 开 pull request

只放 `cities/<城市>/` 里的文本文件：

- `entry.json`、`city.yaml`、`script.yaml`（文案）、`CREDITS`（版权说明）、`FACTS.md`（史实出处）、`TREATMENT.md`、`VOICE.md`、`MUSIC.md`；
- `research/` 里的研究笔记（.md、.txt、.json、.csv、.geojson 这类文本）；
- 素材从哪里来的说明，例如 `assets/README.md`、剪实拍用的 `assets/footage/make.sh`（素材本身不放）。

不要放的：图片、海报、音乐、视频、PDF 等非文本文件（.gitignore 已经拦住，PR 的检查也会拦）；`build/`、`dist/`、`local/`、`internal/`；帐号信息（声音 ID、密钥）、本地路径。

开 PR 后 GitHub Actions 会自动检查：`entry.json` 字段齐不齐、网址对不对，以及有没有放了文本以外的文件（`node tools/registry.mjs --check`，本地也能先跑）。

PR 说明里写：检查结果（`tools/build.mjs` 打印出的那几行）、用了哪些第三方素材与许可、哪些是 AI 生成的。

### 审核看什么

- **史实**：抽查 `FACTS.md` 的出处；示意、估算有没有在画面上标明。
- **许可**：每一份第三方素材都在 `CREDITS`，而且可以公开；城市数据和视频同意用 CC BY-SA 4.0。
- **视频**：看一遍；字幕、文字不出框，没有黑帧，响度正常。
- **播放包和海报**：试播一次，海报打得开。

## 改进代码与技能

- 有问题或想法，先开 issue；小修正可以直接开 pull request。
- 代码照现有的写法（命名、注释密度、文件分工）。一条规则在 `SKILL.md` 写一次，不要重复。
- 改了编译、播放器或渲染，跑一下相关的检查：`node render/still.mjs` 出几张单张对照改动前后，必要时跑 `tools/clipcheck.py`、`tools/camcheck.*`、`tools/readcheck.mjs` 的一段。
- Python 用 uv（`uv add` 加包，`uv.lock` 一起提交），Node 用 npm（`package-lock.json` 一起提交）。
- 不要提交本地路径：路径一律从 `local/config.json` 读（`pipeline/local.py`、`render/local.mjs`）。
- 改代码、数据格式或引擎之前，先在 issue 或 pull request 里说明原因和做法，谈定再改。
- 改了一大段代码，提交前读一遍 diff 里删掉的行：每一行被删掉的输出、写文件、检查都要说得出为什么删（例：改字体时顺手删掉写出字幕时间表的那一行，`.srt` 就一直停在旧内容，没有检查会发现）。
- 新增一种写法（配置键、参数）：先在不改任何城市配置的情况下编译，证明 `build/film.json` 和其他输出跟改之前逐位一致（`cmp`），再改城市配置去用它；文档里写的写法要有一座城真的用上（compile 会列出没有代码读的键，但一种写法整个没接上，要有一座城用上才看得出来）。新加的守门检查，先故意触发一次确认它会拦，还原后确认输出没变。
- 改了中间文件的编码或位置（让位遮罩 `hide*.png`、`build/data` 里的文件、film.json 的字段），读它的地方要一起改：引擎（`engine/studio.js` 的 `hideK`）、`tools/camcheck.py`、`tools/clipcheck.py`；路径从 `pipeline/layout.py` 取。只改一处，检查会假装通过。
- 自定义的顶点变形（升起、让位）要用 `deformMaterial()` 同时套到 AO 的法线材质和每个网格的 `customDepthMaterial`，否则 AO 和阴影里还看得到变形前的形状；着色器里 `exp()` 的距离先夹到 ≥ 0（距离是负的，exp 会变 inf，乘 0 成 NaN，泛光再把它扩成黑色方块）。
- 去掉依赖、换工具之前先存一份对照（编译输出、事件表、混音、单张画面），改完逐项比；有的输出本来每次都略有不同，先把同一版连跑两次量出这个差异，拿它来比，不跟零比。升级前先看项目实际用的解释器和版本（`.venv` 里的，不是系统的）。
- 咸阳没走过的路径（声音比画面短、没有配乐、别的语言）用假的输入跑一次（无声的 WAV、几秒的假片段）。工具写的临时文件要自己清；要能重现的输出不用 Python 的 `hash()`（每次运行都不一样），改用 `zlib.crc32`。
- 改了文件名、流程或数字，用 `grep -rn` 扫所有文档（三种语言）和入口页的语言包 `site/i18n.js`，旧说法一起改；文档里的大小、文件名照工具这次的输出写。
- 文档里的网址写成 `[文字](网址)` 或 `<网址>`，后面不要直接接中日文或全角标点：GitHub 的自动链接只在空白处结束，会把后面的字也当成网址。推送前可以用 GitHub 的 Markdown 转换 API 渲染一次看。
- 改入口页：先用界面设计的技能定方向，搜索、下拉菜单、手机版是基本件；改完在 1024–1920 宽和 360、390 宽、五种语言、减少动态、没有 WebGL 下各截一张看；页内链接（`#…`）在网站根和子路径部署下都不能重新加载页面。

## 许可

你交的代码采用 MIT（[`LICENSE`](LICENSE)）；城市数据和视频采用 CC BY-SA 4.0（[`LICENSE-CONTENT.md`](LICENSE-CONTENT.md)）。

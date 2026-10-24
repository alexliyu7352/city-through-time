# 參與《一城春秋》

兩種參與方式：**交一座城市**，讓它出現在入口頁；或**改進程式與技能**。

## 交一座城市

這個倉庫只收文字資料：城市的設定、文案、史實出處、版權說明和研究筆記。成片、播放包、海報、圖片、音樂都放在外部（影片網站、Hugging Face、你自己的 GitHub Pages），入口頁只是連過去。咸陽是本專案的示例，資料夾裡保留了圖片、海報和網頁播放包（`cities/xianyang/web/`，入口頁直接從 GitHub Pages 播放），方便從頭到尾照著做一遍；提交的城市不用照它放。

### 1. 先把片做出來

照 [`docs/MAKING.zh-Hant.md`](docs/MAKING.zh-Hant.md) 做完一部片，`node tools/build.mjs <城市>` 的檢查都要通過。

### 2. 上傳影片

把 `cities/<城市>/dist/<城市>.mp4` 上傳到 YouTube、B 站或其他影片網站，標題和說明可以直接用 `dist/description.md`。影片網址之後填進 `entry.json` 的 `watch`。

### 3. 網頁播放包和海報

有播放包，觀眾就能在入口頁直接用瀏覽器播放，而且可以拖動、暫停、開關旁白和配樂。播放包可以不做，但海報一定要放在外部某個地方，入口頁的館藏要用。

```sh
uv run python -I tools/web.py cities/<城市>
```

它會把播放器需要的檔案打包到 `cities/<城市>/dist/web/`（咸陽約 215 MB），只收頁面真的會讀的檔：沒有 WAV，也沒有內部測試用的圖。海報也在裡面：`poster.jpg`（1280 寬）和 `poster_thumb.webp`（640 寬，館藏和搜尋用）。只放影片、不做播放包時，就把這兩張圖單獨放上去。字型不在包裡，播放器會從本專案的 `fonts/` 讀（用了新字型的城市，要在 pull request 裡把字型加進 `fonts/`）。

放播放包的地方必須**允許網頁跨網域讀取**。以下兩種都可以：

**Hugging Face 資料集（建議）**：公開資料集免費，大檔沒問題。

```sh
uvx --from huggingface_hub hf auth login
uvx --from huggingface_hub hf upload <你的帳號>/city-through-time-bundles cities/<城市>/dist/web <城市> --repo-type dataset
```

播放包網址：`https://huggingface.co/datasets/<你的帳號>/city-through-time-bundles/resolve/main/<城市>/`

**你自己的 GitHub 倉庫，開 GitHub Pages**：建一個公開倉庫，把 `dist/web/` 裡的東西放進 `<城市>/` 資料夾，在倉庫的 Settings → Pages 選從 main 分支發布。限制：單一檔案 100 MB 以內、整個網站 1 GB 以內。

播放包網址：`https://<你的帳號>.github.io/<倉庫名>/<城市>/`

其他靜態主機（例如 Cloudflare R2）也可以，只要回應帶 `Access-Control-Allow-Origin`。

**上傳前先確認**：配音、配樂用的服務，條款允許公開散布生成的音檔，並寫進 `CREDITS`。

**試播**：在入口頁網址後面接 `play.html?city=<城市>&play=1&bundle=<播放包網址>`，能從頭播到尾才算數。

### 4. 寫 `cities/<城市>/entry.json`

入口頁靠這份檔案認得你的城市。先讓工具從影片產生草稿：

```sh
uv run python -I tools/web.py cities/<城市> --entry
```

它會寫出 `cities/<城市>/entry.json`，填好位置、年代、片長、語言和各章的顏色，其他的你補上：


| 欄位 | 內容 |
|---|---|
| `slug` | 城市資料夾的名字（小寫英文） |
| `name` | 城市名，五種語言：`en`、`ja`、`zh-Hant`、`zh-Hans`、`es`（缺的會改用英文） |
| `location` | `[經度, 緯度]` |
| `years` | `[起, 迄]`，西元前用負數 |
| `duration` | 片長（秒） |
| `narration`、`subtitles` | 旁白語言、字幕語言（語言代碼，例如 `zh`、`en`） |
| `authors` | `[{ "name": "…", "url": "…" }]` |
| `summary` | 兩三句簡介，語言同 `name` |
| `poster` | 海報的 https 網址（1280 寬），例如 `<播放包網址>poster.jpg`（示例城市咸陽用倉庫裡的路徑） |
| `thumb` | 小圖的 https 網址（640 寬），例如 `<播放包網址>poster_thumb.webp` |
| `watch` | `[{ "site": "YouTube", "url": "…" }, { "site": "Bilibili", "url": "…" }]`：發布到幾個網站就填幾個，入口頁全部列出，**第一個是預設**（「觀看影片」播它）。貼平常的影片網址（不要帶開始時間）；YouTube 和 B 站會在入口頁裡嵌入播放，播放視窗裡可以切換網站，其他網站顯示成連結 |
| `bundle` | `{ "url": "播放包網址", "mb": 215 }`，沒有就填 `null` |
| `download` | （可選）`{ "url": "…" }`，影片檔的下載網址 |
| `ai` | AI 生成的部分：`narration`、`music`、`imagined` |
| `license` | `CC BY-SA 4.0` |
| `chapters` | 各章的開始秒數、年份和顏色（工具產生，入口頁畫成色帶） |
| `added` | 加入的日期，`YYYY-MM-DD`（館藏最新的排前面） |

`watch` 和 `bundle` 至少要有一個；兩個都還沒有時，入口頁會顯示「影片正在上架」。

入口頁讀的 `cities.json` 不用你改：每次合併到 main，GitHub Actions 會從所有城市的 `entry.json` 自動產生（`tools/registry.mjs`）。本機用 `node tools/preview.mjs` 預覽入口頁時也會先產生一份。

### 5. 開 pull request

只放 `cities/<城市>/` 裡的文字檔：

- `entry.json`、`city.yaml`、`script.yaml`（文案）、`CREDITS`（版權說明）、`FACTS.md`（史實出處）、`TREATMENT.md`、`VOICE.md`、`MUSIC.md`；
- `research/` 裡的研究筆記（.md、.txt、.json、.csv、.geojson 這類文字）；
- 素材從哪裡來的說明，例如 `assets/README.md`、剪實拍用的 `assets/footage/make.sh`（素材本身不放）。

不要放的：圖片、海報、音樂、影片、PDF 等非文字檔（.gitignore 已經擋住，PR 的檢查也會擋）；`build/`、`dist/`、`local/`、`internal/`；帳號資訊（聲音 ID、金鑰）、本機路徑。

開 PR 後 GitHub Actions 會自動檢查：`entry.json` 欄位齊不齊、網址對不對，以及有沒有放了文字以外的檔案（`node tools/registry.mjs --check`，本機也能先跑）。

PR 說明裡寫：檢查結果（`tools/build.mjs` 印出的那幾行）、用了哪些第三方素材與授權、哪些是 AI 生成的。

### 審核看什麼

- **史實**：抽查 `FACTS.md` 的出處；示意、估算有沒有在畫面上標明。
- **授權**：每一份第三方素材都在 `CREDITS`，而且可以公開；城市資料和影片同意用 CC BY-SA 4.0。
- **影片**：看一遍；字幕、文字不出框，沒有黑幀，響度正常。
- **播放包和海報**：試播一次，海報打得開。

## 改進程式與技能

- 有問題或想法，先開 issue；小修正可以直接開 pull request。
- 程式碼照現有的寫法（命名、註解密度、檔案分工）。一條規則在 `SKILL.md` 寫一次，不要重複。
- 改了編譯、播放器或渲染，跑一下相關的檢查：`node render/still.mjs` 出幾張單張對照改動前後，必要時跑 `tools/clipcheck.py`、`tools/camcheck.*`、`tools/readcheck.mjs` 的一段。
- Python 用 uv（`uv add` 加套件，`uv.lock` 一起提交），Node 用 npm（`package-lock.json` 一起提交）。
- 不要提交本機路徑：路徑一律從 `local/config.json` 讀（`pipeline/local.py`、`render/local.mjs`）。

## 授權

你交的程式碼採 MIT（[`LICENSE`](LICENSE)）；城市資料和影片採 CC BY-SA 4.0（[`LICENSE-CONTENT.md`](LICENSE-CONTENT.md)）。

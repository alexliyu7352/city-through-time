# 參與《一城春秋》

[English](CONTRIBUTING.md) · 繁體中文 · [简体中文](CONTRIBUTING.zh-Hans.md)

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

它會把播放器需要的檔案打包到 `cities/<城市>/dist/web/`（咸陽約 121 MB），只收頁面真的會讀的檔：沒有 WAV，也沒有內部測試用的圖。海報也在裡面：`poster.jpg`（1280 寬）和 `poster_thumb.webp`（640 寬，館藏和搜尋用）。只放影片、不做播放包時，就把這兩張圖單獨放上去。包裡的 `bundle.json` 記著每個檔的大小，播放器的載入畫面照它算進度，要跟著一起放上去。字型不在包裡，播放器會從本專案的 `fonts/` 讀（用了新字型的城市，要在 pull request 裡把字型加進 `fonts/`）。

放播放包的地方必須**允許網頁跨網域讀取**。以下三種都可以：

**Hugging Face 資料集（建議）**：公開資料集免費，大檔沒問題。

```sh
uvx --from huggingface_hub hf auth login
uvx --from huggingface_hub hf upload <你的帳號>/city-through-time-bundles cities/<城市>/dist/web <城市> --repo-type dataset
```

播放包網址：`https://huggingface.co/datasets/<你的帳號>/city-through-time-bundles/resolve/main/<城市>/`

**你自己的 GitHub 倉庫，開 GitHub Pages**：建一個公開倉庫，把 `dist/web/` 裡的東西放進 `<城市>/` 資料夾，在倉庫的 Settings → Pages 選從 main 分支發布。限制：單一檔案 100 MB 以內、整個網站 1 GB 以內。

播放包網址：`https://<你的帳號>.github.io/<倉庫名>/<城市>/`

**你這座城自己的網站，Cloudflare Pages**：有免費的 Cloudflare 帳號就行，不用自己的網域。一條指令把你的城市發布成一個網站：首頁就是這座城的頁面（五種語言），帶 3D 播放器、古城漫遊、展館和播放包，頁尾一行小字註明用一城春秋製作；不帶入口頁、地球儀和別的城市（入口頁是本專案自己的網站，不必複製一份）。網址是 `https://<城市>.pages.dev/`。先準備一次：Cloudflare 帳號；一個 API token（My Profile → API Tokens → Create Token → Custom token，權限只要 Account · Cloudflare Pages · Edit）；帳號 ID（Workers & Pages 頁面的 Account details）。`entry.json` 的播放包和海報寫成網站裡的路徑，跟咸陽一樣（`cities/<城市>/web/`），先打包，再執行（要 Node 22 以上）：

```sh
export CLOUDFLARE_API_TOKEN=<token> CLOUDFLARE_ACCOUNT_ID=<帳號 ID>
node tools/deploy.mjs --city <城市> --dry-run   # 只建好、檢查，不上傳
node tools/deploy.mjs --city <城市>
```

Pages 專案名預設就是城市的資料夾名，想換一個就加 `--project <專案名>`。播放包網址（給入口頁的 pull request 用）：`https://<專案名>.pages.dev/cities/<城市>/web/`。單一檔案超過 20 MiB 時，`tools/web.py` 會自動切成幾份，播放器讀的時候再拼回來。細節在 [`docs/PUBLISH.md`](docs/PUBLISH.md)。

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
| `slug` | 城市資料夾的名字（小寫英文、數字、連字號），也是城市頁的網址：`https://cities.go5.si/<slug>/`。不能和網站自己的資料夾或語言代碼同名（例如 `site`、`ja`），檢查會擋 |
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
| `bundle` | `{ "url": "播放包網址", "mb": 121 }`，沒有就填 `null` |
| `download` | （可選）`{ "url": "…" }`，影片檔的下載網址 |
| `ai` | AI 生成的部分：`narration`、`music`、`imagined` |
| `license` | `CC BY-SA 4.0` |
| `chapters` | 各章的開始秒數、年份和顏色（工具產生，入口頁畫成色帶） |
| `added` | 加入的日期，`YYYY-MM-DD`（館藏最新的排前面） |

`watch` 和 `bundle` 至少要有一個；兩個都還沒有時，入口頁會顯示「影片正在上架」。

入口頁讀的 `cities.json` 和每座城的獨立頁面都不用你寫：每次合併到 main，GitHub Actions 會從所有城市的 `entry.json` 自動產生（`tools/site.mjs`）。城市頁有五種語言，英文在 `https://cities.go5.si/<slug>/`，其他語言在 `/ja/<slug>/`、`/zh-hant/<slug>/`、`/zh-hans/<slug>/`、`/es/<slug>/`；標題、簡介、分享預覽圖（海報）和影片資訊都寫在頁面裡，貼到社群網站會顯示這座城的預覽，搜尋引擎也找得到。本機用 `node tools/preview.mjs` 預覽時會先產生一份到 `_site/`，打開 `http://127.0.0.1:8765/<slug>/` 就能看到。

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
- 程式碼照現有的寫法（命名、註解密度、檔案分工）。一條規則只寫一次：每一步都適用的寫在 `SKILL.md`，其他寫在那一步的子檔（`docs/`）。
- 改了編譯、播放器或渲染，跑一下相關的檢查：`node render/still.mjs` 出幾張單張對照改動前後，必要時跑 `tools/clipcheck.py`、`tools/camcheck.*`、`tools/readcheck.mjs` 的一段。
- Python 用 uv（`uv add` 加套件，`uv.lock` 一起提交），Node 用 npm（`package-lock.json` 一起提交）。
- 不要提交本機路徑：路徑一律從 `local/config.json` 讀（`pipeline/local.py`、`render/local.mjs`）。
- 改程式、資料格式或引擎之前，先在 issue 或 pull request 裡說明原因和做法，談定再改。
- 改了一大段程式，提交前讀一遍 diff 裡刪掉的行：每一行被刪掉的輸出、寫檔、檢查都要說得出為什麼刪（例：改字型時順手刪掉寫出字幕時間表的那一行，`.srt` 就一直停在舊內容，沒有檢查會發現）。
- 新增一個寫法（設定鍵、參數）：先在不改任何城市設定的情況下編譯，證明 `build/film.json` 和其他輸出跟改之前逐位元相同（`cmp`），再改城市設定去用它；文件裡寫的寫法要有一座城真的用上（compile 會列出沒有程式讀的鍵，但一個寫法整個沒接上，要有一座城用上才看得出來）。新加的守門檢查，先故意觸發一次確認它會擋，還原後確認輸出沒變。
- compile 用會記下讀過哪些鍵的 dict 讀 city.yaml（`Seen`），結尾列出沒有程式讀的鍵：把設定攤成新的 dict（`{**cs}`、`dict(cs)`）會把每個鍵都記成讀過，要另做一份時用 `Seen(dict.items(cs))` 並共用原來的 `read`（`hide_layer` 那一處）；自己讀 city.yaml 的工具（prep.py、terrain.py…），鍵名用引號寫在程式裡，compile 才知道有人讀。
- 改了中間檔的編碼或位置（讓位遮罩 `hide*.png`、`build/data` 裡的檔、film.json 的欄位），讀它的地方要一起改：引擎（`engine/studio.js` 的 `hideK`）、`tools/camcheck.py`、`tools/clipcheck.py`；路徑從 `pipeline/layout.py` 取。只改一處，檢查會假裝通過。
- 自訂的頂點變形（升起、讓位）要用 `deformMaterial()` 同時套到 AO 的法線材質和每個網格的 `customDepthMaterial`，否則 AO 和陰影裡還看得到變形前的形狀；著色器裡 `exp()` 的距離先夾到 ≥ 0（距離是負的，exp 會變 inf，乘 0 成 NaN，泛光再把它擴成黑色方塊）。
- 拿掉依賴、換工具之前先存一份對照（編譯輸出、事件表、混音、單張畫面），改完逐項比；有的輸出本來每次都略有不同，先把同一版連跑兩次量出這個差異，拿它來比，不跟零比。升級前先看專案實際用的直譯器和版本（`.venv` 裡的，不是系統的）。
- 加一種隨時間發生的事（一種損毀、一次清空）時，把所有會躲開建築的生成器都掃一遍（樹、地面、巷道、平台）：它們不看時間，會把之後才拆的房子當成一直都在，或把之後才蓋的東西當成已經在。
- 加了一道防護（會讓 compile 停下的檢查）之後，接著試城市對被保護的東西做的下一步（之後拆掉它、交給下一座城）：防護常常也擋住了下一步的正當寫法。
- 從貼圖畫出的硬邊（水岸、地面的邊）存到邊的距離，不要只存「在裡面」的旗標：只存旗標，一旦有光影把邊緣提亮（天空的反光），貼圖的格子就會變成階梯露出來。
- 檢視器（自由視角、整城對照圖）用同一個時間點驅動所有隨時間變化的輸入：固定一部分、強制另一部分，會組出影片裡從來不會有的狀態（一棟房子和之後蓋在它原址上的地標同時站著）。
- 有備用路徑（手機上縮小的著色器、沒有半浮點時的 8 位元畫面），就在每個用到它的頁面（影片、走進古城、展館頁）強制走一次並截圖對照（網址加 `gpu=fit`、`gpu=8bit`）：備用路徑只在少數裝置上出現，它漏掉的功能在開發機上看不到。
- 引擎裡寫死的數量（一部片的水池和地面、同時站著的城、一座城的損毀）要嘛照影片的用量決定大小（compile 只在超過預設時寫進 film.json，引擎照它開），要嘛在編碼本身的上限讓 compile 停下並說明怎麼辦；不要默默截掉，也不要每撞到一次就調大一次。
- 咸陽沒走過的路徑（聲音比畫面短、沒有配樂、別的語言）用假的輸入跑一次（無聲的 WAV、幾秒的假片段）。工具寫的暫存檔要自己清；要能重現的輸出不用 Python 的 `hash()`（每次執行都不一樣），改用 `zlib.crc32`。
- 改了檔名、流程或數字，用 `grep -rn` 掃所有文件（三種語言）和入口頁的語言包 `site/i18n.js`，舊說法一起改；文件裡的大小、檔名照工具這次的輸出寫。
- 文件裡的網址寫成 `[文字](網址)` 或 `<網址>`，後面不要直接接中日文或全形標點：GitHub 的自動連結只在空白處結束，會把後面的字也當成網址。推送前可以用 GitHub 的 Markdown 轉換 API 渲染一次看。
- 改入口頁：先用介面設計的技能定方向，搜尋、下拉選單、手機版是基本件；改完在 1024–1920 寬和 360、390 寬、五種語言、減少動態、沒有 WebGL 下各截一張看；頁內連結（`#…`）在網站根和子路徑部署下都不能重新載入頁面。

## 授權

你交的程式碼採附署名條件的 MIT（[`LICENSE`](LICENSE)）；城市資料和影片採 CC BY-SA 4.0（[`LICENSE-CONTENT.md`](LICENSE-CONTENT.md)）。

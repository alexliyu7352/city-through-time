# 資料規約：建築、地圖、年份從哪裡來，怎麼誠實地標

## 這一步最常犯的錯

- 框太大、大半是農田，城撐不滿畫面；故事要的地方又在框外 → 照「範圍與比例」定框。

## 開始

複製 `templates/city.yaml` 到 `cities/<slug>/city.yaml`，填範圍（box）、比例、資料來源；
`uv run python -I pipeline/osm.py <w> <s> <e> <n>` 抓 OSM（存到本機 raw 下）；`pipeline/terrain.py`（DEM）與 `pipeline/satellite.py`（Sentinel-2）各跑一次；
`uv run python -I pipeline/prep.py cities/<slug>` 產出模型。先渲染一張白模試看，確認範圍與比例。

## 建築輪廓、高度、年份

| 區域 | 適配器 | 輪廓 | 高度 | 年份 | 授權 |
|---|---|---|---|---|---|
| 中國 | `pipeline/cmab.py`（`buildings.source: cmab`） | CMAB 自然城市 shapefile（Web Mercator） | 估算，MAE 3.8 m | GAIA 不透水面首次出現年份 1985–2018，`AF2018` = 2018 後；最早一層寫「XXXX 年已有」 | CC BY 4.0（圖幅與 CREDITS 署名） |
| 全球兜底 | `pipeline/overture_ghsl.py`（`buildings.source: overture_ghsl`，見下） | Overture Maps buildings | Overture `height` / `num_floors`×3.2 m，缺則 9 m | GHS-BUILT-S R2023A 建成區 5 年期（1975–2030，100 m）取質心所在格首次 ≥ 門檻的期；1975 已有者寫「1975 年已有」 | Overture ODbL/CDLA，GHSL CC BY 4.0 |
| 荷蘭 | （預留）3DBAG + BAG bouwjaar | 真值 | 真值 | 真值 | CC BY 4.0 |
| 紐約 | （預留）NYC Building Footprints `CNSTRCT_YR` / PLUTO YearBuilt | 真值 | 真值 | 真值 | 公有 |
| 歐洲 | （預留）EUBUCCO（年份只有 24%）、西班牙 Catastro | 真值 | 多數 | 部分 | ODbL |

CMAB 下載：figshare 文章 27992417 的各省 zip（陝西 = `shanxisheng.zip`，山西 = `shanxi.zip`），解壓到 `raw/cmab/<省>/`，`prep.py` 自動找所有與範圍相交的 shapefile。

### overture_ghsl 適配器的步驟（全球城市）

1. Overture：用 DuckDB 從 `s3://overturemaps-us-west-2/release/<release>/theme=buildings/type=building/` 以 bbox 篩出 footprint、height、num_floors（需要網路與 duckdb + spatial extension；`pipeline/overture_ghsl.py fetch`）。
   release 名稱會過期，舊的會下架：先列出現有的（`curl 'https://overturemaps-us-west-2.s3.amazonaws.com/?prefix=release/&delimiter=/'`），
   再指定名稱，並把名稱寫進 CREDITS（名稱不對就什麼都抓不到）。DuckDB 掃描很重，不和渲染、混音同時跑。
2. GHSL：下載 GHS_BUILT_S_E{1975..2030}_GLOBE_R2023A_54009_100 對應圖幅（JRC 開放資料），`pipeline/overture_ghsl.py years` 用 rasterio 取每棟質心的首次建成期。
3. `prep.py` 的 bands 用 5 年期：`[1975 年已有, 1980–1989, 1990–1999, 2000–2009, 2010–2019, 2020 後]`。
4. 畫面與 FACTS.md 必須寫：「年份為 GHSL 建成區 5 年期估算，精度 100 m」。

## 地圖（OpenStreetMap，ODbL）

`pipeline/osm.py` 以主題抓取並按查詢雜湊快取到 `raw/osm/`：water（水面與河道線）、roads、rail、historic（歷史遺跡、保護區、陵墓）、places、aeroway。
Overpass 只有 overpass-api.de 穩定，慢（10–60 秒一題），快取存在就不重抓。
署名：畫面身份標籤與片尾寫 © OpenStreetMap contributors；CREDITS 寫 ODbL。衍生資料庫（raw/、data/）同授權；影片本身不受限。

## 範圍與比例

模型只涵蓋以歷史核心為中心的現代主城區，長邊約 20–30 km，比例 1:10000（台面約 2.5 m）。超大城市不做全市。
`box` 用 WGS84，`prep.py` 自動選 UTM 分區，模型單位 1 = 1 模型公尺。

- **範圍要讓畫面裝滿城**：框住歷史核心和旁白會講到的地方；框裡大半是農田就收緊，否則城撐不滿畫面，看起來只是一片碎屑。
- **範圍要包住故事的兩端**：故事要的地方只差一點在框外，就把框往那邊擴；遠在框外的山水用 `terrain.context`（MODEL.md「地面與地形」），不擴台面。
- 咸陽：25 km 的框大半是農田，3 萬棟建築撐不滿（撐得滿的密度大約是 319 km² 裡 7 萬棟），收緊到歷史核心；阿房宮前殿在框外 700 m，為了
  「自阿房渡渭，屬之咸陽」把南界擴到 34.245，最後是 31 × 22 km。
- **改了 `box` 要整串重跑**，一次跑一件：`osm.py`（新範圍）→ `terrain.py` → `satellite.py` → `prep.py` → compile。城市設定裡的位置一律寫經緯度
  （`ll:`、`lon`/`lat`），不寫模型座標（`v:`、`x`/`z`）：台面中心一動，模型座標就全錯。畫面上寫了台面大小的地方一起改（SCRIPT.md「畫面上的數字」）。

## 圖片與實拍

片中的圖有兩種用處：每個歷史節點結尾接「今天的同一個地方」（實拍、照片），以及當時的樣子（古地圖、檔案照、古畫、文物、根據史料的想像圖）。

- **配圖清單**（`research/images.md`，一站一節）：找到的圖記下來源和授權；沒找到、但值得配圖的場景也標出來（城市最繁榮的樣子、
  重大事件的場面、詩文的意境，不限主線），寫明要畫什麼，以及細節的依據（建築、服飾、器物、地形的出處）。寫劇本時照它決定
  哪些生成想像圖（SCRIPT.md「配圖」）。
- 優先順序：用戶自己拍的、或用戶有權授權的 → Wikimedia Commons（CC BY / CC BY-SA / CC0，搜「<城市> 航拍」「<地標>」與英文名，`Special:MediaSearch?type=video`）→ 政府與博物館開放素材 → 網路影片（只做內部測試）。
- 先用 Commons API 一次查完候選檔的作者和授權（`https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|extmetadata&titles=File:A|File:B&format=json`，
  一次最多 50 個），授權不合的篩掉，再一個一個下載（咸陽的 CC0 照片和 4K CC BY-SA 影片都是這樣一次查出來的）。
- 下載：Commons 原檔 `https://upload.wikimedia.org/...`，用 `curl -L -o <明確檔名>`；B 站等用 yt-dlp。原檔放本機的 ref 資料夾（`local/config.json` 的 `ref`），不進倉庫。
- 處理：找出原片字幕與水印的位置，裁掉（`crop`）。網路影片的字幕和地名條位置會變：整段每隔幾秒抽一張，按最靠畫面內側的那一條定裁切框，
  不要只看一格。然後縮放到 1600×900，降飽和約 15%，轉全 I 幀 H.264
  （`-g 1`，頁面才能逐幀定位），放 `cities/<slug>/assets/footage/`。
  命令的樣子：`ffmpeg -ss S -t D -i in -vf "crop=…,scale=1600:900,fps=24" -an -c:v libx264 -crf 20 -g 1 out.mp4`。
- 上屏：長度和方式照 STAGING.md「實拍與圖片」：4K 影片全幅 7–9 秒（緩推、上下黑邊，左上「今天 · TODAY · 實拍」+ 地名，右下來源），
  高解析照片右側面板，低解析素材小卡片加引線；不要 4–6 秒一閃而過。
- 網頁播放包：全 I 幀只是給渲染逐格定位用的（咸陽的實拍約 33 Mbps、104 MB），`tools/web.py` 打包時會替網頁重壓成串流格式
  （CRF 26、`-g 24`、faststart；咸陽整包從 206 MB 降到 121 MB），不要把渲染用的素材直接放上網。
- 可重現：裁切與轉碼命令寫進 `cities/<slug>/assets/footage/make.sh`（.mp4 不進倉庫，原檔在本機 ref 資料夾）。
- 記錄：FACTS.md「實拍與照片」表（片段、畫面標註、來源、授權、原片時間點）；CREDITS 分列 CC 與「非 CC · 僅內部測試 · 發布前必須替換」。

## 高解析衛星底圖（僅內部測試）

- `pipeline/imagery_tiles.py`：抓 Esri World Imagery 第 15 級瓦片（約 4 m），拼接並重投影到台面的 UTM 框，輸出 `data/satellite_hr.jpg`。瓦片快取在本機 raw 下的 `tiles/`。
- 不是開放資料。`film.satellite_source: hr` 只用於內部測試；任何要發布的版本改回 `sentinel`（Copernicus Sentinel-2，可發布，需署名）。CREDITS 必須分列。

## 誠實標示（畫面上必須出現）

- 讀數來源行：資料集名稱 + 「估算」字樣（例：`CMAB · GAIA 不透水面首次出現年份（估算）`）。
- 示意多邊形的釘標或標籤加「（示意）」；估算位置加「（位置示意）」。
- 片尾第二、三行：資料來源與授權；「高度與年份為估算」；「史料來源見 FACTS.md」。

## 現代的「長高」：GHSL 建成體積（`pipeline/ghsl_change.py`）

- 資料：GHS-BUILT-V R2023A，100 m 格、1975–2030 每 5 年一期（2025、2030 是推估，只讀到 2020），CC BY 4.0。下載：`uv run python -I pipeline/ghsl_change.py fetch <w> <s> <e> <n>`（一個 1000 km 圖幅 12 期約 220 MB）。
- 用法：今天的每棟建築取所在格的體積序列；建築已在之後，格的體積又長了 1.5 倍以上，就當成「翻建變高」：先以 f0（＝當時體積／2020 體積）的高度出現，在體積增長最多的那幾期長到今天的高度。`grow.change: ghsl`。
- 不能做的：**拆除**。R2023A 的觀測體積在每一格都不會減少（咸陽全範圍檢查過，沒有任何一格在兩期之間減少），也沒有公開資料記錄已拆的建築。畫面不講拆除。
- 畫面標示：「GHSL 建成体积 · 100 m · 5 年 · 估算」。

# 資料規約：建築、地圖、年份從哪裡來，怎麼誠實地標

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
2. GHSL：下載 GHS_BUILT_S_E{1975..2030}_GLOBE_R2023A_54009_100 對應圖幅（JRC 開放資料），`pipeline/overture_ghsl.py years` 用 rasterio 取每棟質心的首次建成期。
3. `prep.py` 的 bands 用 5 年期：`[1975 年已有, 1980–1989, 1990–1999, 2000–2009, 2010–2019, 2020 後]`。
4. 畫面與 FACTS.md 必須寫：「年份為 GHSL 建成區 5 年期估算，精度 100 m」。

## 地圖（OpenStreetMap，ODbL）

`pipeline/osm.py` 以主題抓取並按查詢雜湊快取到 `raw/osm/`：water（水面與河道線）、roads、rail、historic（歷史遺跡、保護區、陵墓）、places、aeroway。
Overpass 只有 overpass-api.de 穩定，慢（10–60 秒一題），快取存在就不重抓。
署名：畫面身份標籤與片尾寫 © OpenStreetMap contributors；CREDITS 寫 ODbL。衍生資料庫（raw/、data/）同授權；影片本身不受限。

## 範圍與比例

模型只涵蓋以歷史核心為中心的現代主城區，長邊 20–30 km，比例 1:10000（台面約 2.5 m）。超大城市不做全市。
`box` 用 WGS84，`prep.py` 自動選 UTM 分區，模型單位 1 = 1 模型公尺。

## 實拍與照片（「今天」回聲）

- 優先順序：Wikimedia Commons（CC BY / CC BY-SA / CC0，搜「<城市> 航拍」「<地標>」與英文名，`Special:MediaSearch?type=video`）→ 政府與博物館開放素材 → 網路影片（只做內部測試）。
- 下載：Commons 原檔 `https://upload.wikimedia.org/...`，用 `curl -L -o <明確檔名>`；B 站等用 yt-dlp。原檔放本機的 ref 資料夾（`local/config.json` 的 `ref`），不進倉庫。
- 處理：找出原片字幕與水印的位置，裁掉（`crop`），縮放到 1600×900，降飽和約 15%，轉全 I 幀 H.264（`-g 1`，頁面才能逐幀定位）；4–6 秒一段，放 `cities/<slug>/assets/footage/`。
- 上屏：全幅、緩推、上下黑邊，左上「今天 · TODAY · 實拍」+ 地名，右下來源。照片（.jpg）也可以用同一個槽。
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

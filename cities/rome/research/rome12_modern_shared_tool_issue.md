# 12站：GHSL語義與原生生長的合併前問題

本件只報證據，沒有修改pipeline、engine、tools、docs、正式資料或staging。

## 1. GHS-BUILT-V不提供歷時增高觀測

**原始資料：** [JRC GHS-BUILT-V R2023A metadata](https://data.jrc.ec.europa.eu/dataset/ab2f107a-03cd-47a3-85e5-139d8ec63283)，Description第2段；下載留存於`model_reference/rome12_modern/jrc_built_v_metadata.html`。已核讀原文關鍵語：

> average building height in the year 2018

> assumed as constant in the 100m resolution cell

**獨立核對：** [GHSL Data Package 2023原PDF](https://human-settlement.emergency.copernicus.eu/documents/GHSL_Data_Package_2023.pdf?t=1683540422)，§2.3，印刷p33／PDF p38，公式`BUVOL = ANBH × BUSURF`。ANBH來自2018高度，BUSURF是多時期建成面。已下載原PDF並以pdftotext全文讀取相關段，原檔、文字及該頁圖在`model_reference/rome12_modern/`。這已超過FACTS S47原有的「僅讀搜尋摘錄」狀態。

**本機數據最小案例：** 台面內100m cell中心`[12.5983612295,41.9202241780]`，來自本機R2023A：

| 年 | S m² | V m³ | V/S m |
|---|---:|---:|---:|
| 1975 | 2,354 | 33,762 | 14.3424 |
| 2000 | 3,537 | 50,729 | 14.3424 |
| 2020 | 10,000 | 143,423 | 14.3423 |

體量增長約4.25倍時，V/S仍固定。它不能區分水平擴張、原址增高或拆舊建新；不能讓該cell中的每座現代樓先低後高，並標成觀測到的「改建增高」。`ghsl_change.change()`的`vL>=v0*1.5`、`f0=v0/vL`只依此比值產生`renew`，沒有額外歷時高度證據。

**受影響的共用介面：** `pipeline/ghsl_change.py change()`、`pipeline/compile.py`的`grow.change: ghsl`與taller counters、`engine/studio.js`的`aGrowH`高度插值；`docs/DATA.md`及`docs/STAGING.md`的相應說法。主線需決定修正語義／演法。本站提案先不啟用`change: ghsl`，保留GHSL建成面估計生長。沒有否定城市可能增高，只是不以本產品證明。

## 2. Overture年代是離散cell閾值，原生設定不會自動連續逐年分配

`overture_ghsl.first_epoch()`以輪廓質心所在100m cell第一次達到1500m²建成面（cell的15%）的節點，指定整棟的估計年代。這是本專案方法，並非JRC公布的逐棟建造年，也不是GHS-AGE的50%定義。

本機16,287個1975後至2020輪廓只有1980、1985……2020九個年代。`grow.yl`會把年份轉成出現時間，但不把同年代的樓分散到那五年。`engine/studio.js`使用`tOfYear(yr-.5)`及1.8秒rise，`grow.bands[].spread`在有年線時不負責分散。已在畫面內的同年代樓仍會成批出現；`grow_t.json`只錯開晚入鏡的樓。單靠這份片段無法保證STAGING第7條的全程連續生長。

若主線要在五年期間內分配，必須保留「估算／插值／分配示意」，不可假作逐年觀測。本件不自製packer、dating或shader，也不為避免成批而任意飛出畫面。

## 3. 生長年線會延伸進2024–2026，需攔住預測年代

`pipeline/compile.py`的`grow['yl']`取生長開始後的整條film年線，並無`LAST_OBSERVED`上限；後續`world_returns`是2024–2026。本機有23筆`year=2025`、3筆`year=2030`。只加`reset+grow`時，23筆將在2025跟年份升起，冒作歷史建造；3筆2030通常不在故事年內升起。26筆完整索引與原值在`rome12_modern_inventory.json → projection_dated_buildings`。

最小邏輯案例：`yl=[[0,1975],[60,2020],[80,2026]]`，原生`t_of_year(2025-.5)`得到75秒，故2025預測輪廓會被排進後續2026故事。正式合併前須由主線處理歷史上限或把這些樓保留為未定年現況背景；不得把它們任意改成年代1975或2020。本件未改model.json。

## 4. tour不適合把本站整段直接套成一站

現有`tour`對`years:[1975,2020]`先補至少45秒flight，在flight中跑到2020，之後整個spoken stop停於2020；它也禁止stop cues帶`year:`。這與12a「城市長到1990時同圖帶過世界盃」不相容。本站應由主代理保留連續年份及同構圖安排，不增加球場tour stop。若用`year:1990`鎖旁白，`node_years()`又會在該句整段鎖年；導演要求不中止全城生長，因此不在提案中加入它。

## 重現與檢查

`uv run --no-sync --offline python -I cities/rome/research/rome12_modern_inventory.py`實際退出0。結果與日誌：`rome12_modern_inventory.json`、`rome12_modern_inventory.log`。只讀既有48 ZIP的城市視窗、既有Overture及model.json。沒有跑正式compile／rangecheck，亦未聲稱它們通過。

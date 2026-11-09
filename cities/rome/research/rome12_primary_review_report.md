> 主線後續已同步1d0c911，歷史增高已移除；下文實碼與repro為修前證據。五年bin暫按原資料、不自寫分配；12生長止於2020，2024–26不演預測新建。此決定已採納，無須重報原三項。

research/rome12_primary_review_report.md — 三項均已證實為原生共用路徑的語義／合併風險；已寄 本機交接記錄/20261030-0318-rome-ghsl-growth-semantics.md。羅馬正式第12站尚未啟用生長，不能稱現有成片已出錯。

## 範圍與依據

只複核 `rome12_modern_shared_tool_issue.md` 前三項。已讀專案 SKILL、MODEL、STAGING、FACTS 全文，以及 survey、原 issue、inventory、validation 與受影響原生程式。交接所稱 `review.md` 沒有現存對應檔；依主代理確認，改讀 `research/rome12_modern_validation.json`，沒有補造原審查結果。

本次重用已存 JRC PDF／HTML 和原 inventory；實看既有 PDF 第38頁圖，核對 Table 10（印刷p21／PDF第26頁）與§2.1（印刷p6／PDF第11頁）文字。四個原來源檔 SHA256 均符合先前 validation；現行 model.json 的 SHA256 也符合 inventory。未開啟任何 GHSL ZIP，未重掃48個檔案。

| 項目 | 判定 | primary 支持的範圍 |
|---|---|---|
| BUILT-V 能否證明「後來改建增高」 | **已證實不能**；原生程式仍如此推論 | JRC固定2018 cell平均高度，再乘多期建成面；沒有歷時高度觀測 |
| 五年bin是否會自動逐年分散 | **已證實不會**；已入鏡、沒有延後覆寫的同年代樓同時起升 | JRC提供五年估算格網，不提供本片逐棟逐年起升次序；成批時刻由本地程式與模型證實 |
| 2025預測是否會溢入抵達2026的故事 | **已證實有此路徑**；23筆2025在示例年線可觸發，3筆2030不會 | JRC明列2025／2030為預測；是否排入影片由本地讀取器與年線證實 |

## 1. BUILT-V 的歷史高度語義

[JRC BUILT-V metadata](https://data.jrc.ec.europa.eu/dataset/ab2f107a-03cd-47a3-85e5-139d8ec63283) Description第2句明說，把2018平均建築高度固定於100m cell，再投影到多期建成面。[JRC原始Data Package PDF](https://human-settlement.emergency.copernicus.eu/documents/GHSL_Data_Package_2023.pdf?t=1683540422) §2.3／PDF第38頁給 `BUVOL = ANBH × BUSURF`，ANBH為2018高度，BUSURF為多期建成面。這支持「V不是獨立的歷時增高證據」，不支持「城市從未增高」或「每棟高度已知」。

本地 cell `[12.598361229495202,41.92022417802447]`：1975的S/V為2354m²／33762m³，2020為10000m²／143423m³；V/S只有14.3423–14.3425m的整數編碼差異。V變為4.248倍，S變為4.248倍，沒有新的高度資訊。

真實呼叫路徑：

- `pipeline/compile.py:1257` 的 `grow.change: ghsl` → `pipeline/ghsl_change.py:59` 的 `change()`；第83–90行依V增逾1.5倍產生 `renew`、`f0=v0/vL`。
- `pipeline/compile.py:2026` 輸出 renew／early／counts；`engine/main.js:63` → `engine/studio.js:555` 的 `setRenew()` → 第537／549行 `aGrowH` → 第395行高度插值。
- `engine/main.js:520` 把 counts 畫成 new／taller；`pipeline/compile.py:1269` 也把 renew 當 follow_change 的增高事件。共用文字在 `docs/DATA.md:96`、`docs/STAGING.md:103`。

最小重現直接呼叫現行 `change()`，只以此cell的既有V序列替代磁碟cube，放一座**測試用**1975足跡；輸出 `renew=[[0,0.235,2010,2020]]`、taller count=1。它顯示同一演算法會將固定高度條件下的建成面增加推為「先矮後高」；不宣稱此測試足跡是真實古樓。`early` 是同一回傳中的另一用途，這項證據不要求刪掉其1975–1987估計分配。咸陽現存 `cities/xianyang/city.yaml:814` 也啟用同一介面，屬共用問題。

## 2. 五年bin的同步起升

[JRC原PDF](https://human-settlement.emergency.copernicus.eu/documents/GHSL_Data_Package_2023.pdf?t=1683540422) §2.1與Table 10區分五個影像觀測時點（1975、1990、2000、2014、2018）和十二個五年估算格網。2020亦不能叫獨立直接觀測；產品沒有每棟1981、1982等竣工年。

`pipeline/overture_ghsl.py:63` 的 `first_epoch()`遍歷共用 EPOCHS，質心cell首次達本專案1500m²門檻就給整座足跡該節點；`load()`的第102–104行交給prep。`pipeline/prep.py:69` 將該年原樣寫進model。現行模型與inventory一致：1975後至2020共16,287座，只有1980、1985……2020九組，1995組3,463座。

`engine/studio.js:106` 的 `tOfYear()`、第392行起升及第274行閃光均使用 `year−0.5`；年線有效時，不走帶有hash／spread的另一分支。同一估計年、沒有aGrowT覆寫的樓因此相同時刻起升。`pipeline/compile.py:1878` 的原生 `t_of_year()`在示例1975→2020共60秒的年線，將所有1995組排在26.0秒，1.8秒升起；不會平均分到1990–1995。

`pipeline/compile.py:1903` 只對遲逾0.5秒才入鏡的樓列進grow_t錯開；已入鏡者不在此列。這證實原生片段不能保證全程連續生長，**不是**已驗證16,287座同時出現在同一鏡頭。原片段沒有 `change: ghsl`，因此也不會走 `early` 的1975–1987分配。若主線採五年區間內的逐棟分配，應標「插值／分配示意」，不能把它當新增觀測。

## 3. 預測年代沿後續全片年線觸發

[JRC原PDF](https://human-settlement.emergency.copernicus.eu/documents/GHSL_Data_Package_2023.pdf?t=1683540422) Table 10明列2025與2030為未來格網預測，§2.1亦說其經時空插值／外推求得。2026成為過去或現在，不會將R2023A的2025預測事後變成觀測。

`pipeline/ghsl.py:8` 的EPOCHS含2025／2030；`pipeline/overture_ghsl.py:71` 無歷史截止，現行model因此保留23筆2025、3筆2030。`pipeline/compile.py:1485` 從生長起點擷取**後續整條**film yearline寫入 `grow['yl']`，未裁到2020；第1887行的待入鏡清單也無上限。`engine/main.js:65` 將此年線傳入shader，接第392行實際起升公式。`ghsl_change.LAST_OBSERVED=2020`只限制該模組，未保護這條普通生長路徑。

本次抽取並執行真實compile中的年線建構四個敘述及 `t_of_year()`，輸入 `[[0,1975],[60,2020],[80,2026]]`，輸出yearline仍含2026；`t_of_year(2025−0.5)=75.0`。所以2025組在計數器2024.5即可啟動，會落入2024–2026段，晚入鏡則可能再延後。2030組得到 `1e6` 未觸發值，不是26筆都會在2026前升起。

羅馬正式 `modern_growth`（`city.yaml:11010`）尚無reset／grow，`world_returns`（第11032行）為2024–2026；以上是加入原片段後的確證路徑，非正式成片秒數。建議主線決定歷史生長上限／預測樓的現況背景表示，保留其未知歷史年；不得將26筆任意改定1975或2020。

## 原報告補正與待驗

原三項判斷成立；精度補正如下：metadata為Description第2**句**；2025樓以2024.5啟動；只有23筆2025在此示例年線能觸發，3筆2030留在年線之外；五年同步結論受入鏡覆寫條件限制。FACTS S47仍記「只取得搜尋摘錄」，本次已核本機原始PDF，這是補證，不自行改FACTS。`LAST_OBSERVED`也不等於2020有直接高度／影像觀測。

待主線決定forecast上限與區間示意分配；待主代理於正式staging合併後驗證可見節奏、鏡頭與標籤。沒有跑正式compile、render、rangecheck、eraview、modelview或全片測試，沒有模型／鏡頭驗收結論。原issue第4項tour不在本次複核與寄件範圍。

## 可重現交付與檔案

在 `本機保留檔/ctt-trial` 實跑，退出0：

```sh
uv run --no-sync --offline python -I cities/rome/research/rome12_primary_review_repro.py
```

結果：native renew `[0,0.235,2010,2020]`；九組／16,287座；2025為23筆、起點75.0秒；原來源hash一致、model符合inventory、受保護輸入hash未變。腳本僅寫本件evidence JSON，完整版本SHA256在其中；複核程式時git HEAD為 `092cdaf154c70336ed24874dfc8ca010986d287e`。

- 報告：`research/rome12_primary_review_report.md`
- 最小重現：`research/rome12_primary_review_repro.py`
- 退出0的輸出與完整輸入hash：`research/rome12_primary_review_evidence.json`
- 已寄信箱：`本機交接記錄/20261030-0318-rome-ghsl-growth-semantics.md`
- 沿用inventory／原始索引：`research/rome12_modern_inventory.json`
- 沿用原核對收據：`research/rome12_modern_validation.json`
- 原始PDF：`research/model_reference/rome12_modern/GHSL_Data_Package_2023.pdf`
- 原始PDF文字：`research/model_reference/rome12_modern/GHSL_Data_Package_2023.txt`
- 已實看頁圖：`research/model_reference/rome12_modern/ghsl_volume_method_pdf38.png`
- 原始metadata：`research/model_reference/rome12_modern/jrc_built_v_metadata.html`

本件只新增以上三個 `rome12_primary_review_*` 與一則信箱檔；未修改原報告、source、model、staging、共用程式或docs。

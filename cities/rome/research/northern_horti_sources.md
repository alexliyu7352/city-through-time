# 113年北側園林：由古路、階地與谷坡約束植栽

本輪只更正Sallustiani與Lucullani兩筆植栽範圍。原先六點保留區是早期布局的概括留地，並非來源圖上的園界；直接用來種樹和計算發光外框，是上一版的錯誤。住宅、公共建築、街道和其餘園地的輸入保留。

## 採用來源及界線

- `model_reference/lanciani_northern_horti.tif`：沿用Rumsey／Stanford館藏原有KML配準，EPSG:4326，沒有另擬控制點。來源瓦片、網址、bounds與SHA-256見同名`_sources.json`。原圖跨越多個年代；古路、古代構築、地形、Aurelian城牆和近代莊園須分辨，不能看見閉合線就當113年園牆。
- FACTS S123的Dell’Era研究，133頁：Sallustiani在兩條Salaria道路之間，與後期in Pincis園產的範圍分開。其附圖是研究比較，不拿來新配準，也不將後世擴張範圍倒放113年。
- S123的Platner／Ashby條目：Lucullani東西側以古路、山坡約束，北界不詳。DAR的共和聖域僅作位置核對，不把目錄標籤點擴成一座建築。
- `model_reference/northern_horti_terrain_reference.jpg`以既有`terrain_true16.png`和原生terrainio／Rasterio檢視現地坡形，沒有改地形。這是現代DEM參考，不是古代地坪測繪；園地推定以古圖地貌為先，不把今日填高的谷地當作113年的精確標高。

## 逐段對照

所有橙色閉合線都是**113年植栽示意範圍**，不是已發掘產界。圖上可以辨認的是下列道路與地形約束；原圖沒有給出兩園完整的113年園界。

| 園林／邊段 | 圖上能核對的東西 | 採用方式與估值 |
|---|---|---|
| Lucullani西／南側 | 標有Horti Lucullani的階地、坡折向南彎下；不是六角形的一條斜邊 | 逐點沿階地曲線收邊；古園產界與精確種植退距不詳，植栽邊仍標示意。 |
| Lucullani東側 | 通往Porta Pinciana的彎曲道路廊道 | 依道路彎向留出通行帶；不是把全園放在一個固定朝向的多邊形裡。 |
| Lucullani北側 | 未找到完整產界；附近另有Aciliorum遺構與後世莊園 | 在聖域附近的上部階地作示意接線，與東側古路相接；不複製Aciliorum半圓建築、Medici產界或Aurelian城牆。 |
| Sallustiani西側 | Salaria Vetus／Pinciana道路走廊向南彎轉 | 沿其東側配置植栽；個別退距為估值，保留街廊。 |
| Sallustiani東側 | Salaria Nova方向的道路廊道；Porta Collina與舊城防地形相鄰 | 依圖收回原先向東切入其他地區的概括角點，不以後來城市街區作113年園界。 |
| Sallustiani南側 | Vallis Sallustiana與Servian坡折向西南延伸，接Alta Semita一帶 | 沿谷地、坡折接線；DAR的Horti內住宅點只核對位置，不當足跡或復原其113年立面。 |
| Sallustiani北側 | 谷地北緣的長曲坡；西段上部台地沒有清楚園界 | 東段循圖上的谷緣曲線；西段沿台地接到道路，接線明標示意。不將北側Aurelian牆線或Villa Ludovisi邊界照搬成園牆。 |

可逐點核對的資料為[northern_horti_boundaries.geojson](northern_horti_boundaries.geojson)：保存地理座標、2000×960研究裁圖上的採點位置、原影像雜湊與basis。[原圖疊合](model_reference/northern_horti_after_overlay.jpg)與[可放大SVG](northern_horti_source_overlay.svg)僅供研究，不進電影素材。

## 原生生成與保留項目

兩筆資料同時更新在`imperial_113_geography.yaml`與`imperial_113_reservations.geojson`，避免重新匯出時六角形回來。`add_imperial_landscape.py`仍只整理布局；既有`build_imperial_config.py`輸出原生`trees.region`，citygen負責植樹、道路／牆體避讓和城市外框。沒有自製植樹器、平滑發光外框、改地形或改共用程式。

其餘已通過園地保留範圍與做法。原生植栽共用隨機序列，改變北園的數量會使後續園地的個別樹位與通用樹冠略變，不能聲稱每棵樹逐筆凍結；院內植栽、台地落地及園林可讀性需重新檢查。所有住宅與公共建築的來源特徵應與前輪相同，另比較實際模型中所有非樹構件。

重現順序：原有`fetch_lanciani_core.py`取得北側研究窗 → 既有`plot_forum_palatine_trace.py`疊合GeoJSON → `add_imperial_landscape.py --name imperial_completion` → `build_imperial_config.py … --name imperial_completion --houses imperial_housing_types.yaml` → 原生`modelview.py`、clipcheck／geocheck及eraview。數值與樣張驗收見[northern_horti_review.md](northern_horti_review.md)。

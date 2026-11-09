# 建城期第一形制交件

狀態：**來源調查與待批准單屋形制交件完成。** 兩柱門廊候選已由原生工具生成，sheet及12°四面已實看；沒有鋪整城，沒有改正式影片或批准模型。

調查見 [survey](rome01_founding_survey.md)，每個新增數字見 [housing basis](rome01_founding_housing_basis.md)，原始像素與公式見 [controls](rome01_founding_controls.json)。本次只有一屋外量體，不是完整構造復原、已批准考古落位或753BCE同期聚落。

## 先看什麼

- [12°四面與稍遠景合表](../build/review/modelview/rome01_founding_close/rome01_founding_close_sheet.jpg)，獨立研究片00:02.86；30°、120°、210°、300°四面，`d=.0034`。
- [正面原圖](../build/review/modelview/rome01_founding_close/1_2.86.jpg)及[另一側門廊](../build/review/modelview/rome01_founding_close/4_2.86.jpg)：真門洞、兩根細前柱、外伸覆頂與主屋接合。
- [原生標準sheet](../build/review/modelview/rome01_founding_sheet/sheet.jpg)，獨立研究片00:04.66。它的單屋鏡距下限`.012`使此5m房屋很小，故補上述原生近景；不是考古路旁街坊。
- [北向方法並列](model_reference/rome01_founding/rome01_founding_registration_review.jpg)及[七柱洞圖間對照](model_reference/rome01_founding/rome01_founding_graphic_match.jpg)。

12°四面原圖1–4及稍遠第5張、標準sheet的四面與總覽均已看過。可見完整主體，圓端／短脊的構件接線仍存在；門廊是小幅外伸，不是獨立門樓。沒有巨型高台。近景原生景深會軟化細柱，不能當精細榫架或茅束已復原。

展示點12.45,41.84與背景現代白模只是形制展示地，不是Cermalus落位；畫面750 BCE是「約VIII世紀中葉」的研究片標籤，沒有修改正式753 BCE傳統紀年。shape自身×1只作真比例比較，全域設定未改。sheet工具自帶的一條8m展示道路沒有同期來源，**不納入建城期道路提案**；近景spec沒有這條道路。

## 原生檢查實際結果

| 對象 | 結果 | 實際日誌 |
|---|---|---|
| `rome01_founding_sheet` | 9構件＝8件單屋＋展示道路；geocheck全部朝外；clipcheck適用項全0、top tenth地基0% | [modelview輸出](rome01_founding_sheet_modelview.log)、[compile](../build/review/modelview/rome01_founding_sheet/build/logs/compile.log)、[clipcheck](../build/review/modelview/rome01_founding_sheet/build/logs/clipcheck.log) |
| `rome01_founding_close` | 8構件；geocheck全部朝外；clipcheck的重疊、浮空、地形切入、穿牆、鋪地及高地基等適用項全0 | [modelview輸出](rome01_founding_close_modelview.log)、[geocheck](../build/review/modelview/rome01_founding_close/build/logs/geocheck.log)、[clipcheck原JSON](../build/review/modelview/rome01_founding_close/build/logs/clipcheck.json) |
| 研究算術／schema | 既有五主體構件逐項不變；兩前柱均接觸覆頂下緣；現行`landmarks.check`接受資料 | [data_check](rome01_founding_data_check.json)；此項不是模型檢查的替代 |

compile的「末年不是2026」與無旁白dead-air提示屬獨立模型研究片的預期限制，未作成片通過宣告。沒有關閉檢查、修改檢查閾值或把研究片的warn模式用在正式影片。

本輪實看來源圖：F01原p.6圖1、p.7圖2、p.8轉型正文／圖；F04完整平剖及木架復原；F02 Davico單屋照片；F03官方PDF原嵌入頁1；NF01 Fidene剖視圖。七柱洞和北向研究圖亦已實看。Lanciani只作現代遺構方向的背景比較，未拿它建VIII世紀街區。

## 原生取景工具的限制

原先study固定覆寫城市slug的問題經主線修復後，本件才用獨立`--name`執行；輸出、資料、日誌全在`rome01_founding_sheet`及`rome01_founding_close`。本件未改共用程式，也沒有建立輸入副本。

標準 [eraview日誌](rome01_founding_eraview.log)與成片／檢查兩張總表已實看，但**不作有效近景驗收**：這屋是`parts`地標，沒有fabric，auto dense目標會落在空地；landmark列又受`.012`最短鏡距而很小。最小重現：

```sh
node tools/eraview.mjs cities/rome/build/review/modelview/rome01_founding_close --eras rome01_founding --d 0.0034
```

這一問題只回報主代理，未修共享工具。另有既有原生VIEW helper按明確target產生的固定target圖，存於`build/review/modelview/rome01_founding_views/`，設定為`research/rome01_founding_native_views.json`；未逐張判圖，不作本件檢查依據，也未新寫或改動capture helper。主要可審輸出仍為上述原生sheet和12°四面。

## 可重現命令

```sh
uv run --no-sync --offline python -I cities/rome/research/rome01_founding_prepare.py
uv run --no-sync --offline python -I tools/modelview.py cities/rome rome01_founding --spec cities/rome/research/rome01_founding_spec.yaml --year -750 --sheet --at 12.45,41.84 --name rome01_founding_sheet
uv run --no-sync --offline python -I tools/modelview.py cities/rome rome01_founding --spec cities/rome/research/rome01_founding_spec.yaml --year -750 --at 12.45,41.84,30,12,0.0034 --at 12.45,41.84,120,12,0.0034 --at 12.45,41.84,210,12,0.0034 --at 12.45,41.84,300,12,0.0034 --at 12.45,41.84,30,30,0.008 --name rome01_founding_close
```

## 仍缺什麼

房型尚待導演確認，這是擴展一區前的實際停止點。原刊北向的歷史原因、A＝3原文編號對照、古地坪高程、全村戶數／比例與精確邊界尚未知；已明選有界示意分支，不因這些未知無限延展研究。上部高度、理想圓端、門廊屋坡及細部都是明列比較估值；目前只能批准或退回這個外量體，不能宣稱整個建城期城市或正式01站完成。

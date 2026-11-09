# 羅馬：第2步資料、範圍與尺度

## 已確認的製作基準

範圍、水平1:10000及建築顯示高度×3已由導演確認。第4步首個帝都模型已按MODEL量測，現採地形×2：參考地基24%、實際19%，均低於30%，高地基檢查0。市中心近景見[model_review.md](model_review.md)，其他時期隨建模續驗。

導演確認英文旁白SHA-256：`b106e072a961d6181c7447dfe62fb42f1cbce8097e838f91fae2c406b8113353`，1,638詞，未改動。原14:16是朗讀與觀看的文字估算；正式雙語字幕排程另見[第3步核對](script_review.md)。

共用程式由主線修復並同步。本輪沒有改共用程式、套用舊修補提案、git pull或重裝依賴；依序重跑terrain → satellite → prep → compile → 靜幀。

## 範圍與下載覆蓋

- 已確認的WGS84取框box：`[12.36, 41.80, 12.64, 42.00]`；UTM 33N／EPSG:32633。
- 實地台面23.228 × 22.208公里，模型約2.323 × 2.221公尺。未涵蓋整個行政區。
- **下載及讀取以台面外接框area為準：** `[12.356, 41.797, 12.6436, 42.003]`。UTM正北台面邊緣會超出原經緯度box；下載area並不是擴大已確認的台面。
- 依DATA「Where downloads live」，城市專屬建築和OSM放在raw根目錄下的`cities/rome/`；GHSL仍放共用`ghsl/`。機器路徑只由local/config.json決定，查找用`layout.area(city)`。
- 古城、梵蒂岡、庇亞門、奧運村及Cinecittà在框內。75公里未來河流廊道依細綱用範圍示意補充，不擴大底模硬塞全線。

## 資料來源與新結果

| 資料 | 版本／範圍 | 本輪結果與界線 |
|---|---|---|
| Overture建築 | Buildings，2026-10-21.0；新area | 原始**150,044**筆；79,975筆有height，14,778筆有樓層，61,530筆兩者皆缺而回退9m。height／樓層欄位可重疊，不相加當總數。prep後**140,866**個輪廓 |
| GHSL建成面S及體量V | R2023A，100m、5年節點；R4_C20及R5_C20 | 共48份共用ZIP沿用；歷史序列到2020，2025／2030是預測 |
| OpenStreetMap | 新area；六主題 | 原始元素：water 545、roads 4,648、rail 2,230、historic 2,249、places 67、aeroway 13 |
| Copernicus DEM GLO-30 | 30m；N42及N41兩圖塊 | 774×740網格；**100%覆蓋，沒有缺邊補值** |
| Sentinel-2 L2A | 2025-10-28三景；10m | 2323×2221拼接，100%覆蓋；影像不是2026實拍 |

Overture歸屬與授權依[官方頁](https://docs.overturemaps.org/attribution/#buildings)；其他歸屬見[CREDITS](../CREDITS)。GHSL年代不是逐棟實測竣工年；畫面須標「Years are estimates from GHSL 5-year built-up periods, accuracy 100 m」。

### 更正：原98.7%／1.3%不是資料限制

舊記錄把「DEM覆蓋98.7%、其餘約1.3%補值」列作原始資料限制，這個判斷撤回。原因是程式以原box取數，漏掉投影台面伸出box的邊緣；不是該處沒有公開DEM。

修復後以area讀取下列兩圖塊，地形日誌覆蓋達100%，沒有缺資料WARNING：

- `Copernicus_DSM_COG_10_N42_00_E012_00_DEM`
- `Copernicus_DSM_COG_10_N41_00_E012_00_DEM`

裸地處理仍會移除建築覆蓋單元的表面高程並由周圍推估地面；這是DSM轉地面的方法，與缺少邊緣資料的補值不同。舊記錄保存在[archive](archive/data_acquisition_before_area_fix.md)，不得再引用為現況。

## 本輪命令及日誌

建築和OSM的新area快取已由主線提供，本輪沒有重下；`overture_ghsl.py fetch cities/rome`及`osm.py cities/rome`會沿用相符快取。既有Python與Node依賴保持不變。

重工作依下列順序執行，完整日誌均在`build/logs/`：

```sh
nice -n 10 uv run --no-sync --offline python -I pipeline/terrain.py cities/rome
nice -n 10 uv run --no-sync --offline python -I pipeline/satellite.py cities/rome
nice -n 10 uv run --no-sync --offline python -I pipeline/prep.py cities/rome
nice -n 10 uv run --no-sync --offline python -I pipeline/compile.py cities/rome
nice -n 10 node render/still.mjs rome 5.5 --prefix white_model_area_
```

對應日誌：terrain_area.log、satellite_area.log、prep_area.log、compile_area.log、white_model_area.log，全部退出0。後續第3步編譯另記compile_script.log，不混用尺度審查的結果。

## 實際產物與核對

- [新白模靜幀](../build/review/stills/white_model_area_5.5.jpg)：1920×1080，尺度審查小片00:05.5、extent_review節點。已實際看圖，台面完整入鏡，河流、城市紋理及邊緣資料可辨。不是正式影片時間碼，也不是山丘近景驗收。
- [model.json](../build/data/model.json)：140,866個有效輪廓，與stats一致；EPSG:32633，台面大小未改。prep另輸出water 118、roads 4,648、rail 1,885、subway 345、rivers 11項；與OSM原始元素數口徑不同。
- [地形元資料](../build/data/terrain.json)：高程0–191m，裸地處理涉及41%單元；[衛星元資料](../build/data/satellite.json)保留三景ID。
- [新結構核對](data_validation.json)：原始與模型筆數、例外數量、覆蓋及確認狀態。
- 已確認尺度的舊靜幀保留於`build/review/approved_extent/white_model_5.5.jpg`；尺度設定保留於[city_extent_approved_before_script.yaml](archive/city_extent_approved_before_script.yaml)，新尺度審查film保留於`build/review/white_model_area_film.json`。
- 現行city.yaml已進入第3步十四站字幕排程，尺度審查命令使用的是上述存檔設定；不能直接在正式腳本00:05.5重現同一幅圖。

## 真正的資料限制與後續

1. **高度估算：** 61,530筆原始建築回退9m；模型96筆高度在0.1m精度四捨五入為0。近景前須檢查，不宣稱每個輪廓都有準確測高。
2. **歷史年代：** 19,154筆未進入1975–2020歷史分組，包括僅在2025預測層達閾值23筆、2030層3筆；這26筆不能當歷史實測竣工年。
3. **第4步地形驗收：** 先列帕拉蒂尼、卡比托利歐、賈尼科洛及埃斯奎林等敘事山丘；用各期城市範圍的foundations輸出選擇倍率，再以實際房屋檢查最高一成地基不超過房高30%、tall_foundation為0，交市中心近景確認丘陵可見。建築×3已確認；首個帝都模型採地形×2，量測與近景見model_review.md，其他時期續驗。

第2步重跑結果與更正已獲導演確認，不重開同一門檻。第3步已按英文旁白重排為13:36.90、空白0；第4步首個帝都模型與地形近景已開始驗收。其他時期、逐站分鏡、聲音及成片尚未完成。第2步存檔靜幀保持當時的地形×1，不覆寫成新的地形審查圖。



### 2026-11-04 增长镜头的资料标记

金色范围取现有 `build/data/model.json` 中 1975 < 首次建成年份 ≤ 2020 的建筑轮廓（16,284 条面），依原生增长排程升起，不另加建筑。画面上的「1975年后新建」指向建筑记录 90397：12.53669029233001, 41.8943669861406，分配年份为 1975.69；这是 GHSL 五年期内的估算分配，不是逐栋实测竣工日期。原有 2020 年线终点前移到 r10_003，r10_001–002 展示资料范围的增长，随后在2020年城景中回顾迁居生活；旁白不变。

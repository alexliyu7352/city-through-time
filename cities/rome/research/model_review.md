# 羅馬第4步：首個時代城市與地形驗收

目前交付入口改為[Forum—Palatine小片核對](forum_palatine_trace_review.md)，使用獨立原生modelview研究資料夾；本頁以下只保留舊試作履歷，勿執行末尾的舊命令。

> **舊試作記錄，相關驗收結論撤回。** 本文下面保留當時記錄，不能作目前第4步通過依據：舊房屋實際用了北中國內建 `dwelling`，舊競技場／Circus用了自訂分段塔，檢視腳本改過真實設定及審查外觀，均不再採用。新版房型／地標改用 `types:` 與通用類別，官方工具產出的樣張、估值及限制見 [imperial_sample_sources.md](imperial_sample_sources.md)。地形×2仍為候選，須待新整城布局按現行坡度／地基規則重驗；舊24%／19%及近景不能代替該驗收。

## 範圍與保留值

先做來源較完整的113年帝都整城示意，採[model_sources.md](model_sources.md)的分區、地標與年代界線。獨立模型審查使用model_review_city.yaml，不把113年的完整城市放進正式-27年場景；審查後恢復已重排為13:36.90的正式city.yaml與字幕輸出。

已確認的台面、1:10000、現代建築×3不變。第一座時代城市使用MODEL預設的時代建築×2；個別競技場體量保持×1。不是將現代建築×3倒當成所有歷代形制。

## 地形操作前的坡地地標清單

| 地標 | 故事裡必須看見什麼 | 來源與界線 |
|---|---|---|
| 帕拉蒂尼山與Forum谷地 | 聚落／宮殿站在山上，谷地仍低；不能削平山丘換取地基過關 | S02、model_sources.md官方Palatine布局；今日DEM不是古代每一處地坪 |
| 卡比托利歐山與Forum | 相鄰山丘、山口與低處的高差；後期廣場改形另建模型 | S39、Trajan官方布局及Lanciani；113年不出米開朗基羅廣場 |
| Oppian／Esquiline與競技場谷地 | 大火由低處上山的地形關係；湖址不是整城水淹 | S05、S63及Lanciani29/30 |
| 賈尼科洛山與河岸 | 後期磨坊的高處與供水關係 | S11；本輪113年模型不提前放537年斷供 |
| Palatine Stadium | 宮殿東側較低的一帶，不能共用整個宮殿的單一高度 | 官方Stadium資料約低10m；現代地形與古代平台不能等同 |

地形×1雖通過地基檢查，實看近景仍不夠清楚；因此在坡度上限內比較×2，並重新跑terrain → prep → compile → clipcheck → 靜幀。沒有削山或抬高整片宮城。×1對照圖留在build/review/model/terrain_x1/。

## 模型與來源界線

- [imperial_trace.geojson](imperial_trace.geojson)為根據文獻布局及現代遺址錨點製作的示意，不是已完成配準的考古描圖；逐項依據見imperial_feature_basis.json。
- 以不規則、各有朝向的分區生成實體房屋，留廣場、河流、園林及競技空間；不使用全城均一格子或三世紀城牆當113年城界。
- 現有通用gable／hall與矩形量體用於第一輪體量；沒有套中國宮殿、重檐或城樓。競技場拱券、裝飾與精細座席未復原，本輪不能稱完整建築復原驗收。
- 除有據遺址位置外，外圍街區邊界、住宅尺寸、高度及填補均屬示意；不將AD14標籤點當成113年逐棟測繪。
- 正式電影的火災、湖址替換、分期成長及鏡頭尚待逐站配置；這輪只驗收首個時期的整城體量、地形及房屋辨識。

## 本輪輸出與檢查

本輪已生成41,903個幾何primitive，來自176項地標量體／構件、55個住宅區塊及7條街軸。這些primitive不是建築筆數，不與140,866個現代輪廓相加。

**採用地形×2。** 官方foundations的參考房屋最高一成地基為房高24%，上限×2.5；實際生成房屋為19%，上限×3。所選×2低於兩者較嚴的×2.5，且均低於30%。150m以下細小起伏仍按既有雙尺度規則保持×1。

[clipcheck_model.log](../build/logs/clipcheck_model.log)所有適用幾何檢查均為0：houses_vs_walls、houses_vs_streets、landmarks_overlap、today_vs_era、floating、terrain_cut、paving_under、tall_foundation。首次發現兩組Palatine殿翼相交5處，已把示意殿翼收在各自不規則遺址的內院範圍，重新生成及核對後歸零；沒有改檢查門檻或共用程式。

已實際看過輸出：

- [市中心山丘近景](../build/review/model/palatine_hill_close_8.jpg)：獨立審查片00:08，imperial_layout_113。聚焦Palatine及相鄰谷地，附由同一DEM生成的10m等高線，協助核對坡地；等高線是技術審查輔助，不預設進正式電影。
- [較寬的市中心對照](../build/review/model/city_centre_hills_8.jpg)：同一審查片00:08。地形×2，收起現代底模以免遮住古代街區，審查用地面色／鏡頭與正式分鏡分開。
- [低角度住宅近景](../build/review/model/roman_houses_8.jpg)：同片00:08，俯角12°、距離0.05模型公尺；屋頂、門面及院落可辨。外圍住宅排布與形制仍為示意，尚非逐棟復原驗收。

hill_view_recipes.json及cameras.json在同一review目錄保留鏡頭參數。丘陵的視覺辨識交導演看圖確認，未提前標為已獲確認。

審查配置共24.4秒、沒有旁白；安靜時段僅在model_review_script.yaml聲明，沒有把正式191條字幕或29項密度提醒靜音。審查片結束於113年的編譯WARNING是刻意的單時期範圍，不是正式影片結尾；正式影片仍結束於2026。

原city.yaml文字及正式film.json／字幕輸出均已恢復；目前正式排程仍13:36.90。只有經量測選定的地形倍率×2保留在正式設定，1:10000、現代建築×3、確認旁白與本機設定不變。

## 本輪未完成的內容

其他歷代城市尚未鋪設；113年首輪示意也未完成逐建築立面、拱券、精細座席及全部考古尺寸的形制驗收。64年火勢、湖址替換、分期成長和正式鏡頭仍待逐站配置。29項字幕密度提醒全部保留在subtitle_density_review.md，沒有宣稱全片檢查通過。

```sh
uv run --no-sync --offline python -I cities/rome/research/build_imperial_config.py
uv run --no-sync --offline python -I cities/rome/research/make_terrain_contours.py
nice -n 10 uv run --no-sync --offline python -I cities/rome/research/render_model_study.py --data
nice -n 10 uv run --no-sync --offline python -I cities/rome/research/render_hill_views.py
```

重工作序列：terrain → prep → 單模型compile → clipcheck → 2張靜幀 → 恢復正式設定並compile。沒有配音、音樂或全片截圖。

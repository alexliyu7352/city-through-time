# 房型形式與山丘側光核對

依據：`docs/MODEL.md`的House types，尤其「Choose the form by how the buildings were built」及斜屋頂保持畫面角度；Hills on the plate的台面同色側光。本輪只處理三款房型及山丘近景，未改旁白、正式分鏡或地形倍率。

## 三款房型

| 房型 | 核對後設定 | 依據及修改原因 |
|---|---|---|
| H1 內院住宅 | court、固定一層，地塊18×28m | 符合一次建成的一棟住宅；保留。單院仍為示意，未稱atrium與peristyle全宅復原。 |
| H2 底商出租樓 | detached、固定五層，整棟地塊36×30m | 原row、3–5層及12×18m窄戶把同一棟樓拆成高低街屋，違反選形式規則。改一體同高；來源不確定完整內院，故不用court。地塊仍屬具名類比推定，非Ara Coeli實測外框。 |
| H3 低層鋪房 | detached、固定一層，整座地塊18×18m | 原row與1–2層沒有逐戶建造、加層的來源依據。改完整一層鋪房量體；不再暗示已證實樓上住宅或夾層。 |

來源與估值界線已同步更正FACTS S84–S85及[樣品依據](imperial_sample_sources.md)。樣品列是同型建物的並列展示，間距及排數不是古羅馬街廓密度復原。

三型屋面仍是推定25°，由新版共用工具保留角度；沒有把數值改成較小角度來抵消房高×2。生成檔60件山牆屋頂，依記錄中的`atan2(rise,span/2)`量得24.9953°至25.0082°（輸出取整誤差）；見[量測記錄](../build/review/modelview/imperial_houses_form_update/evidence/roof_pitch.json)。

[最新房型樣張](../build/review/modelview/imperial_houses_form_update/houses_sheet.jpg)：由左至右H1、H2、H3，俯角35°、距離.032、fov42°。官方modelview `--sheet`產出；[原色全向檢視](../build/review/modelview/imperial_houses_form_update/imperial_houses_form_update_film.jpg)及[檢查外觀](../build/review/modelview/imperial_houses_form_update/imperial_houses_form_update_check.jpg)已實看。

本版[geocheck](../build/review/modelview/imperial_houses_form_update/evidence/geocheck.log)：486件，面向錯誤0。[clipcheck](../build/review/modelview/imperial_houses_form_update/evidence/clipcheck.log)：所有適用穿模項目0；現代建築浮空0，高地基0，地基最高一成佔房高約0%。

## 山丘設定及近景

原設定`terrain.shade: {k: 1}`已符合新版鍵值，保留。固定光az325°、el25°，`col`未另寫，原色檢視會採台面`#3a4757`：向光坡面為鋼藍，背光坡面變暗；沒有白色地形光。重編譯後使用主線的新shader，沒有自訂等高線、改色shader、地形後製或共用程式修補。

[交付近景：Forum谷地望帕拉蒂尼山](../build/review/modelview/palatine_hill_shade_update/forum_to_palatine_az215.jpg)。上方偏右的白色量體是S90的Aula Regia錨點，高地向前景谷地下降。山丘以同色明暗表現，沒有用白色亮帶冒充山脊。

官方modelview先編譯只有該地標的獨立樣品；再用內建模型檢視器的原色`VIEW`介面取景（`look: film, today: false`），鏡頭目標由檢視器落在地面。未替換真實city.yaml／film.json，未寫新的造型或檢視工具。完整相機參數為[palatine_hill_views.json](palatine_hill_views.json)：Forum目標12.4853,41.8919、方位215°、俯角10°、距離.085；其餘角度與較寬modelview靜幀一併留存供核對。

本輪讀的是實際渲染的`terrain16.png`，不是8-bit fallback或true16：輸出地形場在Forum目標約22.4m、Aula Regia位置約43.6m，×2後兩點畫面高差約42.4m。這是現代DEM的濾波地形取樣，**不是古代地坪的考古量測**。地形×2與150m以下起伏×1不變；×2仍待整城布局後按坡度／地基規則驗收。

地標樣品[geocheck](../build/review/modelview/palatine_hill_shade_update/evidence/geocheck.log)：16件，面向錯誤0；[clipcheck](../build/review/modelview/palatine_hill_shade_update/evidence/clipcheck.log)：所有適用項目0，現代浮空0，高地基0。這只驗證該樣品，未宣布整個第4步通過。

正式城市設定、英語旁白、本機設定、兩份16-bit地形及現代模型會與本輪前雜湊核對；記錄存於樣品evidence。本輪沒有重跑下載、DEM或prep，也沒有啟用已封存的舊模型腳本。

# AD113整城示意模型

導演確認：公共建築、營區的位置與量體、有據街道、地形×2及本版 geocheck／clipcheck 結果通過。**住宅半部退回**：下列9,835棟及其樣張只保留作被退回版本的對照；不能再稱其密度、比例或格網布局已確認。Subura69棟樣區其後已確認；本輪擴展住宅的逐區依據見[imperial_housing_atlas.md](imperial_housing_atlas.md)。下列樣張／數字保留被退回住宅版本的歷史記錄。主線地標 id／group 已同步，頂層接受，parts 不接受；不再等待該介面。

本輪是第4步的獨立113年末景，原生modelview研究片00:06.22（不是正式03站時間碼）。新增模型未接入-27至113年的正式生長分期；旁白、字幕及13:36.90文字骨架維持原檔。

[六張樣張](../build/review/modelview/imperial_113_final/city_review.jpg)依次為整城、帝國廣場、Julia、Palatine山坡、Subura街區、Emporium倉庫。[整城全景](../build/review/modelview/imperial_113_final/whole_from_southwest.jpg)；[俯視圖](../build/review/modelview/imperial_113_final/whole_plan.jpg)；[山坡近景](../build/review/modelview/imperial_113_final/palatine_southwest_slope.jpg)。

## 整城與來源

20個來源約束的城市分區，連同Castra Praetoria營區：Forum—Palatine、帝國廣場、Subura、Campus Martius／Flaminius、Quirinal／Viminal、Esquiline／Caelian、Aventine、沿河商倉與Transtiberim。不是奧勒良牆內的四世紀羅馬，也不是把參考圖空白等同無人。原生生成9,835棟住宅（9,455院宅、380租樓）、48件公共建築／宮殿／橋／倉庫量體、48棟示意兵舍、840條主街／內巷線和一處營牆，共146,871 primitives。數量是這版示意模型的配置，不能換成人口或古代戶數。

院宅／租樓沿已確認types；Julia保持已確認真券洞的17／7孔、雙層券廊及內廳。主要新增量體包括Palatine分台宮殿、Curia／Aemilia／神廟、Caesar／Augustus／Nerva／Trajan／Peace廣場、Marcellus／Pompey／Balbus劇場、Domitian stadium、Trajan／Agrippa／Nero浴場、Augustus墓、Porticus Aemilia與河岸倉庫、兩座島橋及營區。公共院庭、園林與倉庫區分別留地；110火災後的Pantheon位置沒有硬放118–125的完工圓頂。

配準、逐件實證／估值、年代與尚未復原的細節見[整城來源](imperial_113_sources.md)，採用內容補入FACTS S95–S103。輸入為[布局資料](imperial_113_layout.geojson)、[地理約束](imperial_113_geography.yaml)、[地標定位](imperial_113_placements.yaml)，原生規格為[imperial_113_city.yaml](imperial_113_city.yaml)。[配準底圖疊圖](imperial_113_source_overlay.png)僅供研究，未把第三方圖搬入影片assets。

## 已確認小片的保留

[編譯紀錄核對](../build/review/modelview/imperial_113_final/evidence/parcel_and_baseline_audit.json)：原41個來源要素相同；原33棟與Julia／Castor所有模型幾何相同，缺失0、增加0（只排除生長時間欄）。住宅申報9,835、實際9,835，空地塊0；正式城市設定／字幕／旁白／地形／現代模型／film.json／本機設定共14項保護檔雜湊未變。

首輪自查發現4組新地標相交、4棟原小片住宅被新增道路避讓扣掉，已修正：南接路沿原Vicus Tuscus南端續接，內巷為原地塊保留完整路寬；Flavia院庭回到Aula軸西側、Augustana下院只取較窄西庭；Augustus的主要exedrae回到Mars廟兩側，Nerva主院與後方門廊範圍分清；Marcellus採配準圖的劇場圓心／舞台軸；Saepta按完整柱廊邊界定位而非標籤點。新增營牆使用原生避讓所需的外側留地，未擠掉Viminal住宅。

## 地形與檢查

在獨立研究城市執行原生`pipeline/terrain.py`，依這版整城範圍重新量測：地形×2時，參考屋地基最高一成約佔屋高20%，低於30%；原生建議上限×3.5。實際模型clipcheck的高地基0，最高一成約0%。因此本113年模型保留×2、150m以下細節×1及同色固定低光`shade.k:1`。全片倍率仍需其餘時期建好後，按最陡者覆驗。

重跑研究副本的terrain16／true16均與正式原檔逐位元相同；既有現代底模仍對應同一地形，浮空0，沒有在正式資料夾重跑prep或改地形。原生`geocheck`面向錯誤0；`clipcheck`所有適用穿模／相交／浮空／切地／道路項目0。檔案在[evidence](../build/review/modelview/imperial_113_final/evidence/)。

[成片光照各面](../build/review/modelview/imperial_113_final/imperial_113_film.jpg)及[檢查光照各面](../build/review/modelview/imperial_113_final/imperial_113_check.jpg)已逐張看：每種光照16張密宅近景、16張四大地標、4張整城，共72張。另保留23個定位視角；[相機選項](imperial_113_views.json)，使用原生VIEW／render/page，不另做模型檢視器、地形shader或建築造型。

## 尚有的模型限制與交接

這是完整城市的示意量體版本，不是每一棟113年建築的精細考古復原。劇場／競技場ring外廊、宮殿細柱廊及房間、浴場細部、雕刻與拱門銘文仍有簡化。Cestio古橋形制、部分浴場／私宮上構明列同期推定；Horrea Agrippiana二／三層異文維持待核，只保留位置，不擅定上構。今日DEM不等於古地坪，也未為對上文獻數字硬挖10m。

主線地標id／group介面已同步並在新研究模型使用；parts不收這兩鍵。本輪只交113年整城供確認，正式03站分期、其他時期、29項字幕密度提醒、後續分鏡與聲音仍在後續工作。

可在原生檢視頁看整城，開頁後刷新：
http://127.0.0.1:8766/play.html?city=rome&view&bundle=cities/rome/build/review/modelview/rome/&eras=imperial_113

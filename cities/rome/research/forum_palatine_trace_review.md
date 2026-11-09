# AD113小片交付：Forum—Palatine西北麓

> 本文為上一版10棟小樣記錄。來源與配準方法獲確認，密度與Julia外觀被退回；目前交付請看[密度／券廊修訂核對](forum_palatine_density_review.md)。本文舊樣張與數字保留供同鏡比較，不作目前驗收結論。

本輪落實已確認順序的前半：記錄已審房型／山丘基線、更正舊地基結論，取得配準來源，改寫布局整理腳本，先交一小片街區。**尚未擴展113年整城，也未進第5步。**

## 看這些圖

- [原色低角度近景](../build/review/modelview/forum_palatine_trace_sample/native_low_az315.jpg)：內建模型檢視器VIEW、az315°、俯角12°、距離.035，收起現代底模以看清本片。這是模型檢視，沒有電影時間碼。
- [原色布局俯視](../build/review/modelview/forum_palatine_trace_sample/native_plan_az305.jpg)：VIEW、az305°、俯角35°、距離.045。
- [放回影片外觀的近景／俯視雙圖](../build/review/modelview/forum_palatine_trace_sample/street_sheet.jpg)：獨立modelview研究片00:05.84，節點`forum_palatine_113`，不是正式03站。現代底模及房型沒有改色或後製。
- [新增Julia四面樣品](../build/review/modelview/forum_palatine_landmarks/sheet.jpg)：獨立研究片00:04.66。只用現成long_hall；形制及限制見[來源L7](forum_palatine_sources.md)。
- [全向原色](../build/review/modelview/forum_palatine_trace_sample/forum_palatine_113_film.jpg)／[全向檢查色](../build/review/modelview/forum_palatine_trace_sample/forum_palatine_113_check.jpg)：現成eraview的八方近景、地標四面及全片四向，兩張均已實看。自動近景以住宅為目標，部分角度裁掉高地標頂部；完整量體看其地標列／末列與上述獨立近景，不把近景當完整地標構圖驗收。
- [配準來源與布局對照](forum_palatine_source_overlay.png)（[SVG原檔](forum_palatine_source_overlay.svg)）：藍色道路、紫色地標錨點、橙色**示意**填補區；原圖只供研究，不入片。這是靜態GIS對照，PNG以現有ImageMagick轉換；Chrome直接截該SVG曾超時，沒有修改共用渲染器。模型VIEW兩張已正常截取並實看。

## 改了什麼、依據什麼

| 項目 | 本輪落實 | 依據 |
|---|---|---|
| 已審基線 | 三型形式、固定層數、25°屋面及鋼藍山丘記入TREATMENT；舊24%／19%結論撤回 | SKILL的Praised passages；MODEL的選形式、屋面角度與坡度規則 |
| 街廓 | 讀取館藏已配準Lanciani及DAR局部圖，使用native city.trace；OSM校位。有據街道與示意內巷／宅地分開標來源 | MODEL的Lay out blocks from an old map；原生traced規格 |
| 程式 | build_imperial_config.py現在只整理布局資料並引用既有types／地標資料；停用hall／tower拼競技場、任意縮小地標及三角剖分住宅區 | MODEL的House types、Landmarks of any region、No empty cities；舊四檔保存在archive/pre_registered_layout |
| 形制／落位 | Julia採官方101×49m外廓與30m中央廳的概括量體；Castor改到遺址中心、正面朝Forum | MODEL要求逐項核位置、朝向、層級及尺度；FACTS S89、S92 |
| 填補 | 7個示意分配區實際生成10棟：5內院宅、1整棟出租樓、4低鋪房。不是古代戶數估算 | 已審三型及MODEL完整地塊規則；逐項basis見forum_palatine_feature_basis.json |
| 年代 | 不依共和末住宅標籤在Augustan倉庫址加房；不將DAR的64年前Nova Via搬到113年 | FACTS S93；DAR及PArCo的分期資料 |
| 檢視 | 原生modelview、eraview與VIEW；正式city.yaml／film.json沒有被替換 | MODEL及CHECKS的獨立樣品／全向檢視規則 |

第一輪有15個布局要素，卻只生成1棟住宅；原生工具只放完整地塊，不是零錯誤就等於街區完整。已按現成工具的地塊規則調整**示意**分配區，避開道路與地標的原生6m留距；沒有搬動有據地標、改已審房型或改共用程式。次輪7棟後，最終確認10棟；早期稀疏試圖不作交付基線。

## 檢查與保留限制

[最終geocheck](../build/review/modelview/forum_palatine_trace_sample/evidence/geocheck.log)：246件primitive，面向錯誤0。[最終clipcheck](../build/review/modelview/forum_palatine_trace_sample/evidence/clipcheck.log)：房屋／街道／地標交疊、浮空、地形侵入、鋪地被蓋及高地基等適用項目均0；現代浮空0。primitive不是棟數，[棟數記錄](../build/review/modelview/forum_palatine_trace_sample/evidence/counts.json)按原生FAB的building origin計10棟。

此谷地小樣的原生地基最高一成輸出約0%，不能推論Palatine、Aventine等整城坡地已合格。地形×2仍為候選，待完整城市用terrain參考坡度與實際tall_foundation雙重驗收，並逐一比較坡地地標。山丘與兩份16-bit地形未改。

研究片由modelview固定生成20秒、沒有字幕，故仍列出「末站113非2026」、末段5秒空白和copy的20秒無詞提醒；這是獨立研究片的範圍／排程，不能稱整片CHECKS通過，也不以新增旁白或假2026站消除提醒。正式13:36.90骨架與29項字幕密度待辦沒有改動。bundle.json是選用檔，原生頁面以既有單檔fallback正常載入，未造空檔壓掉404。

10項受保護檔案的[前後雜湊](../build/review/modelview/forum_palatine_trace_sample/evidence/protected_baseline.json)全部相同：正式城市與字幕、導演中英旁白、已審房型、terrain16／true16、現代模型、正式film及local config。未git pull、未重裝依賴、未改共用程式。

## 下一批仍待做

小片確認後再擴展完整AD113城市。Horrea、Palatine宮殿、其他公共建築及全城分區另核來源／年代；新增形制仍先交原生四面樣品。再按整城坡度定地形，其後才鋪其他時期及正式分鏡。完整城市、分期成長、29項密度提醒、living moments與聲音均未完成；進新步驟前重讀該步文件全文。

另已核實一個正式分期會用到的共用介面缺口：`pipeline/compile.py`的stage selector只按`id`／`group`找項目，但`pipeline/landmarks.py`的通用地標校驗不接受這兩鍵。對本輪Julia執行原生check，實際回覆`no key group, id`。小樣只用一次`landmarks: true`，不受此限制；正式03站要按建造年代細分地標成長時，須先由主線補齊介面。已列待辦，未自行改共用程式、改用列表索引或提前把末景一次升起。

## 重建入口

```sh
uv run --no-sync --offline python -I cities/rome/research/build_imperial_config.py cities/rome/research/forum_palatine_layout.geojson --name forum_palatine
uv run --no-sync --offline python -I tools/modelview.py cities/rome forum_palatine_113 --spec cities/rome/research/forum_palatine_city.yaml --year 113 --at 12.4841,41.89125,315,12,.035 --at 12.48525,41.89180,180,12,.035 --at 12.48465,41.89140,305,45,.055 --name forum_palatine_trace_sample
```

eraview從`cities/`工作目錄執行：`nice -n 10 node ../tools/eraview.mjs rome/build/review/modelview/rome --eras forum_palatine_113 --d .035`。VIEW的兩個目標及參數在`forum_palatine_views.json`；使用`render/page.mjs`的openFilm／shot及內建window.VIEW操作，不含本城造型或檢視器實作。8766預覽已實際載入並截圖，VIEWINFO只有本輪forum_palatine_113，HTTP film與本機逐byte相同；打開既有頁面須重新整理。

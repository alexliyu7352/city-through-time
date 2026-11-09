# Subura 住宅樣區交付

第4步獨立模型 `subura_sample`，研究片完全升起後00:18.14；不是正式03站的時間碼。僅重鋪這一片，未將方法套到113年整城。

## 樣張

- [低角度近景：12°、距離0.035](../build/review/modelview/subura_sample/low_northeast.jpg)
- [樣區遠景：40°、距離0.072](../build/review/modelview/subura_sample/far_north.jpg)
- [俯視街廓及完整區界](../build/review/modelview/subura_sample/plan.jpg)
- [沒有景深／光邊的原生檢查光照](../build/review/modelview/subura_sample/far_south_check.jpg)
- [原生房型 sheet](../build/review/modelview/subura_housing_types/sheet.jpg)

這一片是**較晚考古平面的形態示意轉用**，不是113年逐棟原址復原。203–211年的FUR10g描線、放置／比例尺推定、具名樓高比較和無確證的住宅比例，均先寫於[依據](subura_housing_basis.md)。Lanciani本身沿館藏配準；把模型放在該底圖上，不等於已替FUR碎片完成原址配準。新商業內巷不另命名成第二條已知Clivus Suburanus。

## 對照退回事項

| 問題 | 本樣區的改動 | 依據與限制 |
|---|---|---|
| 三個固定宅地、全區一個方向 | 以考古平面描出的街形形成7個不規則街廓；完整院樓先放，臨街面及殘餘窄地另放小型商住房。69宅地以0.1m計有50組尺寸，以1°計有21種軸向。沒有65×79m巷網、三尺寸格網或隨機扭歪房屋。 | MODEL「A whole city」「Lay out blocks」；10g為較晚原型，確切宅界、尺度和放置仍示意，不能冒作113地籍。 |
| 整格裁邊與大片楔形空地 | 宅地隨各塊可用深度調整；先完整院樓、再臨街補齊，避免小宅地先切碎大樓位置。餘地為窄通道和後方工作／生活院；最大的連通餘地雖1618.7m²，但其最大內接開放半徑僅5.26m，不能把總面積當一塊大空場。光邊與原成片look保留，另交檢查光照供核對。 | MODEL「No empty cities」；FUR10f有共用後方工作／生活空間。用途及細界是同期示意，不是出土逐院辨識。樣區外藍地是尚未重鋪的其他住宅區。 |
| 9455一層院宅對380固定五層租樓 | 撤回原比例。新模型實量一層1、二層11、三層33、四層23、五層1棟。院樓只有一個等高樓體，樓與樓之間才改變層數。 | MODEL「House types」；三／四層為Soffitto Dipinto與Diana具名近時期比較，五層只取Ara Coeli高樓比較；一／二層低宅參照Pompeii。層高、分配與住宅功能詳列估值，模型數量不等於已知歷史比例。 |
| 只記「示意」而沒有研究順序 | FACTS S104及依據表按考古平面、具名復原、同期文獻與習俗逐項分開；不需要再用影視替代已有資料。 | MODEL「No empty cities」「House types」；未找到113年Subura定量普查，沒有杜撰百分比，也沒有把4世紀Regionaries回填113年。 |
| 公共建築已通過 | 97件公共／營區來源要素和其已編譯幾何保留；30條既有街道保留，包括直接對照凍結小片的全部6條街／內巷。地形×2及14個保護檔未變。 | [實際模型與基線比對](../build/review/modelview/subura_sample/evidence/model_audit.json)：公共幾何缺失0、新增0；街道改動0。 |

房型配置：完整多層院樓36棟（3層12、4層23、5層1）、臨街小型商住房31棟、低層院宅2棟，合計69。這些是模型的形制分類，無法直接等同產權、出租戶或居民比例。

## 驗證

原生compile：4356 primitives；geocheck面向錯誤0；clipcheck的牆／街／地標相交、浮空、切地、鋪地及高地基等適用項目均0，正式底模浮空0。研究片空白0。編譯的「終站113而非2026」提示與20秒無旁白的copy建議，屬獨立無聲模型研究片，未把正式終站或旁白改成113年。

原生eraview兩種光照、72個視角的總覽均已看。最終保留清單另逐件對照原小片的6條街／內巷，沒有以名稱中的lane判斷是否可刪；補回兩條原小片內巷後重新編譯、檢查及拍各面，並從8766實際預覽拍攝交付的近／遠景。查核與完整輸入留在[evidence](../build/review/modelview/subura_sample/evidence/)。

地標頂層已用主線新增的id，stage按名字選landmarks／walls／streets／fabric；沒有索引或parts內id／group，沒有修改共用程式。

## 保留的限制

- 缺113年Subura完整住宅地籍及棟數比例，不能把此樣區擴展為整城統計。後續仍須逐區採用各自的考古／復原依據。
- 舊版原生court底商未畫的問題已由91a506a修正：中門兩側現在有店面；仍未逐間復原每座考古店室。小型臨街商住房可見原生店面。側／背面為較簡的實牆，並非每面都已復原窗洞、陽台與裝飾。
- 不把碎片破邊當古城邊界；這裡只是一個研究窗。樣區之外的舊住宅尚未重做，也未在這份研究片中顯示。

實際預覽（刷新後按「近」，可拖曳旋轉；「全」會包含全部保留公共建築）：
http://127.0.0.1:8766/play.html?city=rome&view&bundle=cities/rome/build/review/modelview/rome/&eras=subura_sample

本樣區其後已由導演確認；依本輪指示擴整城，樣區原始輸入保持凍結。


## 導演確認與主線店面修正

本片69棟、街形、樓高、邊緣及依據／估值區分已確認。原輸入及樣張凍結於`build/review/modelview/approved_subura/`。主線91a506a重編後，院門兩側店面已在同一近景核看；更新圖與模型在`build/review/modelview/subura_shops_91a506a/`，不再沿用舊版「底商未畫」限制。整城僅直接合併凍結輸入，不重排本片。

# AD14：Forum西南—Velabrum—Palatine山麓樣區

本研究只做一個約250m級的連續街坊，不是AD14整城或正式03站。選區以Julia後側、Vicus Iugarius與Vicus Tuscus為骨架，東緣包含Horrea Agrippiana；不納入Livia、Augustus宅或後來的Palatine宮殿。所有新增檔以`early_imperial_sample_`開頭；113與Livia的既有輸入只讀。

## 來源層級與配置界線

|項目|來源層級與可用內容|本樣區如何處理／仍缺|
|---|---|---|
|Tuscus與Iugarius|DAR考古地形研究；[Tuscus正文](https://www.digitalaugustanrome.org/records/vicus-tuscus/)及[Velabrum正文](https://www.digitalaugustanrome.org/records/velabrum/)支持兩條古路、Forum出口及Horrea旁古鋪面。Tuscus在Horrea以南的線形有爭議。|只採已核Forum至Horrea附近的街廊；OSM北段校位、已配準考古圖校方向。6m寬是估值。未把113年所有巷網倒放，也不延至有爭議的Argentarii段。|
|內巷與樣區南緣|已知商業、密建居住和通行功能；缺逐棟地籍。|連接兩條有據街道的巷道屬同期習俗示意，4.2m沿既審小樣的量體估值。南側巷道是研究片收束位置，不宣稱發掘出一條AD14街道；不畫城牆或產界。模型外框由完整建物自動生成。|
|Julia|考古平面及具名官方復原。DAR [Julia](https://www.digitalaugustanrome.org/records/basilica-iulia/)支持Augustan外廓未被後世整修改變；PArCo教學冊、FACTS S92/S124給101×49m與五廊、雙層券廊、30m中廳。|沿用已核原生parts，位置、方向及尺寸逐項核對；屋面、券廊高和孔形簡化仍是估值。AD12奉獻日期有討論，AD14已有該建築與其基本外廓不因此撤除。|
|Castor|AD6重建的考古／具名Caen復原；FACTS S89/S124。|沿用已核30×50m台基、8前柱、12.5m柱高和朝Forum方向。7m台基、14.5m檐高、退牆、屋頂及側柱數概括仍是估值，不稱完整實測復原。|
|Horrea Agrippiana|DAR [Horrea](https://www.digitalaugustanrome.org/records/horrea-agrippiana/)支持Agrippan矩形、多層倉庫，並排除FUR42/5a誤認；FACTS S120記官方原三層／另一頁二層異文。|以OSM13426221遺存牆線的47×52.6m近似矩形校位，保留原生完整院樓量體。選原三層解讀，但AD14上部與層數並非定論；4.25m層高、9m翼寬、立面凹口與22°屋面皆是建模比較估值。未引用Domitianic Paedagogium作AD14直接證據，未放二世紀末院神龕馬賽克。|
|Horrea北側宅第|DAR [Domus: Vicus Tuscus](https://www.digitalaugustanrome.org/records/domus-vicus-tuscus/)記1980年代S.Maria Antiqua下發現晚共和／Augustan atrium，AD25–30才覆建；早報可能商業／住宅，業主歸屬更不確定。|不以DAR215標籤點生成完整宅界；選區的普通住宅在Tuscus西側，這處未定全外廓留在東側裁界外。2023新發現的共和宅是否同一發掘區交主代理查，未把兩條敘述合併成一個確定故事。|
|Velabrum住宅與店面|DAR Velabrum記晚共和繁忙商業、成排鋪房、倉庫和密集居住；同文指出兩條大街之間除Cloaca外，考古平面大致未知。|未知宅界不得冒稱考古描摹。住宅適用性、用途／層數的採用規則必須先寫在`early_imperial_sample_housing_basis.md`；候選區先保留，不用113年房數、Hadrian院樓或五層Ara Coeli填滿。|
|多層文字證據|同期原典 [Vitruvius2.8.17](https://lexundria.com/vitr/2.8.17/mg)明記羅馬以多個上層房間增加居住空間。|支持AD14附近的羅馬不能被畫成全低宅；不給本街區每棟層數、court平面或租樓比例。具名適用比較由主代理補核後再放住宅。|
|Forum邊緣|既有考古圖和公共空間用途，FACTS S119。|僅保留兩條街出口之間的鋪地帶，寬7m為估值；不把113圍繞晚期紀念物的整塊鋪地切口倒放，也不把空間種成樹林。|

已到考古地形研究與具名復原層；未用影視，也不以影視覆蓋可用考古資料。沒有考古全平面處，補全屬同期習俗。源圖均僅研究，不上屏；公開可讀不等於已取得影片使用權。

## 配準、像素與錨點

DAR沿既存XYZ z17瓦片的EPSG:3857；來源圖`model_reference/dar_forum_palatine_z17.tif`為768×768px。Affine為`[1.1943285669558463,0,1389625.1742245033,0,-1.1943285669549368,5145129.247931784]`。這是官方圖塊配準，沒有另擬控制點。

Lanciani沿`model_reference/lanciani_core_sources.json`的館藏KML LatLonBox，原圖1280×1024px、EPSG:4326；Affine為`[0.000003824134077026753,0,12.48290708734373,0,-0.000003824134077040631,41.89340657055924]`。圖中跨多期，紅色近代路與後期Tiberiana輪廓不當AD14。

原始瓦片URL、雜湊與source manifests存既有`model_reference/`；本樣區只新增以自身前綴命名的檢視副本和來源清冊，不改原配準。

|錨點|本樣區經緯度|DAR原配準像素|方向、尺度與位階|
|---|---|---|---|
|Julia遺址中心|12.4847834,41.8919606|146.15,267.82|長軸153.89°；native深度軸故theta63.89°；101×49m，雙層券廊及30m中廳。|
|Castor遺址中心|12.4856301,41.8916788|225.07,303.11|正面NE，theta153.69°；30×50m台基，AD6柱列版本。|
|Horrea牆線中心|12.4850165346,41.8908289736|167.88,409.51|theta44.8°；47×52.6m近似矩形，完整院樓共一原生平面。|

DAR標籤點與上述遺址中心相差約10–20m，圖示輪廓也不是現地測量；不拿標籤點當新中心、不平移模型去迎合標籤、不稱源圖輪廓與現代測點已精密配準。來源疊圖與逐件表分列來源線、示意線及現地錨點。

## 選區內保留與排除

住宅候選地塊位於Julia後側與Tuscus西側，按本街廓可用深度逐棟配完整樓體。公共建物原址、native階梯、院落和有據街廊優先，示意宅地不得迫使其移址。非廣場的剩地不自動命名為Augustus私園；沒有已知園界，不補大塊樹林掩蓋未施工。

未納入Saturn、Vesta住宅、Nova Via全段、Scalae Graecae復原、Livia、Augustus宅與Apollo圖書館，避免不必要的新形制／未定相位。Flavian宮殿、Domitian坡道入口和Tiberiana晚期大院不在本樣區。Terrain×2、現代建築×3、1:10000、正式配色與旁白不改。

## 原生檢查與交付邊界

`tools/modelview.py`的真實CLI已讀；輸入以`--spec research/early_imperial_sample_city.yaml --year14 --name early_imperial_sample`建立獨立study。任何compile、modelview、eraview或still前，向主代理取獨占工作時段；沒有許可不執行。最終須在最後資料變更後取原生geocheck、clipcheck與film/check eraview，另交低角度、廣角及俯視。檢查零不代表畫面獲准；圖片判斷與導演審核由主代理負責。

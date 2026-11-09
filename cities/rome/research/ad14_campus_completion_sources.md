# AD14 Campus 五項公共用途補齊

本包只交研究、原生資料與採用建議。原生形體均為有界示意，不是完整考古復原；不改正式配置、已准樣區、AD113或共享程式。`ad14_campus_completion_build.py`只輸出YAML／GeoJSON與資料檢查，沒有生成網格或呼叫native流程。

## CC01 Agrippa浴場

[DAR浴場條目](https://www.digitalaugustanrome.org/records/thermae-agrippa/)支持早期存在、南北軸及不對稱布局；其本身說明地圖矩形是最大已知範圍，北界未明，不能把它當逐室平面。沿既有z17原圖四點／原配準及約68×135m留地，不沿用AD113的Trajan式屋群，也不把後期Ciambella大圓廳確定為AD14。

選擇同類比較為Monika Trümper等的[2024年Stabian浴場發掘報告](https://pompeiisites.org/wp-content/uploads/6-E-Journal-Truemper.pdf)，PDF頁3–7、圖6／17。早期大laconicum直徑7.15m；它在80BCE後改建時被拆，因此這是晚共和浴室類型比較，並非把它說成AD14還站在Pompeii。該報告證明院旁串列浴室、服務房與非對稱地塊適配，不支持把Pompeii各相位直接複製到Rome。

模型採7.15m為比較模數，主要浴室寬14.3、長42.9m，依[Vitruvius5.10.4](https://lexundria.com/vitr/5.10/mg)浴室寬長1:3作估值。大室牆高7.15m、桶頂加7.15m，低翼牆高同取7.15m，是把具名小laconicum與同書5.10.5高等於寬的理想規則轉成一組低單層外量體；**不是Agrippa任何一間房的實測高度，也不代表一般浴室都用laconicum比例**。小圓汗室7.15m直徑／鼓高，半球加3.575m；其位置是功能示意。南北翼、兩大室、26×32m院及各房偏移均為同類習俗估配，覆蓋有據浴場用途而不假裝出土房線。15°屋面、0.2m出檐、0.715m開孔、0.15m院面為顯示與屋架估值。

## CC02 Diribitorium

[DAR Diribitorium](https://www.digitalaugustanrome.org/records/diribitorium/)支持7BCE完工、AD14覆屋，以及Augustan牆基配Severan碎片的斜外廓。沿既有四點約137×46m留地，不以label19作中心；NE斜角保存在低部原生prism。

覆屋選擇一座有側廊的整體大廳作**結構類型假說**。100羅馬尺木材僅作29.6m中央屋跨比較，餘寬兩邊分攤，不當館高或137m全長的無支承跨距。簷高14.8m取同期具名[Fano basilica，Vitruvius5.1.6的50尺整柱](https://lexundria.com/vitr/5.1/mg)；側廊柱高取其5.1.5「等於側廊寬」規則，現資料約6.36m。15°主屋面、低側廊屋頂及屋緣內縮是形體估配；不聲稱Diribitorium已知有這些支柱／分跨。原生直屋頂在來源斜輪廓內縮，外輪廓仍由來源低體控制。這解決已知有屋頂的AD14狀態，並保留內支承／真實屋高未知的界線。

## CC03 Porticus Liviae

[DAR](https://www.digitalaugustanrome.org/records/porticus-liviae/)的7BCE公共四面廊、Clivus Suburanus入口和與Via in Selci垂直關係，現在已有含完整院體的正確z17原圖。`controls.json`保留38點外廓及四個主體角；原生中心取外廓主體，不取329標籤。[Stanford10opqr](https://formaurbis.stanford.edu/fragment_10opqr.html)直接保留四面雙柱列、大小不同的exedrae及中央功能爭議；Severan圖只能佐證長期平面，不能把各細節一律證為AD14。

內部比例參照[Macaulay／Spoth-Torres，GRE的Porticus Liviae](https://roman-gardens.github.io/id/18a75adaf8/)，fig.1是Carandini／Carafa2012 tab.109的具名平面再版，原圖與169px＝40m尺均保存。主矩形圖讀約123×72m；DAR主體約119×73m，未平均兩者：**位置與絕對外廓選DAR，院及柱列相對比例選fig.1，四角仿射套合後縮放約數％**。仿射控制及殘差全在controls，可重現而非假稱另做測地控制。四廊及兩列柱有原生體，來源突出的exedrae亦有同高簡化量體；中央僅另存未解平面，既不補神廟，也不種樹佔住。院面0.15m是薄鋪地。

高度採單層柱列5.92m，取具名同期Fano的20羅馬尺側廊pilaster比較。上加0.71m檐部（原生簡化成整片廊頂厚度）及0.35m薄屋頂；0.8m背牆、0.85m柱徑／0.86收分為比例估值。這不是Liviae實測原高。GRE fig.2圖說用了two-story字樣，但圖像是雙列柱／藤架的透視、沒有可靠層高或第二層測量；本包不據該圖說再加整層。fig.1標Ara Concordiae也是其中一說，不解除中央泉／壇／廟爭議。頁首Date「7CE」與其正文7BCE相衝突，採DAR／正文7BCE，不採metadata錯置。

## CC04 Agrippa Pantheon

明選[DAR所引Loerke p.50／La Rocca的「露天圓院＋覆頂環廊」](https://www.digitalaugustanrome.org/records/pantheum/)分支，替代前包Tortorici低邊界代理；不是聲稱爭論已解。保留原OSM圓弧／北廊錨點與44×20m、十前柱、7.75m北伸，以及21.25m寬南連接體。0.61m厚／1.65m存高碎牆只存為考古記錄，**完全不用1.65m作AD14全高，也不把AD14畫成廢墟**。

現代外圓半徑29.118m仍只作同址空間控制。環廊寬6m借同期Fano20尺側廊約5.92m取整，內院半徑約23.118m；外牆／拱起高12.5m借已核AD6 Castor／Pollux柱高，不冒稱原Pantheon牆高實測。內柱11.1m加1.4m檐部、柱徑1m／0.86收分、0.8m外牆為估值。6m環廊上以半圓桶拱截面作3m升高、0.6m殼厚的旋轉體；315°覆廊留45°北入口。柱數／開角／殼厚都是示意，環廊不是完整混凝土大穹頂。北前廊15m簷、13.5m柱、1.5m平台和15°屋面沿前包早期Castor／Apollo比較；連接體8m深及12.5m高仍估值。完整外量體可供採用，真實高度／柱式／覆蓋範圍仍未定。未直接核讀Beltrami或Loerke原刊，具名分支經DAR綜述引用。

## CC05 Naumachia Augusti／Nemus Caesarum

明選[DAR採用的Taylor低地矩形定位](https://www.digitalaugustanrome.org/records/naumachia/)。另有Coarelli較南的FUR28定位和Coleman橢圓池說，這次不混合、不把其差異縮成幾米誤差。藍色池的12點及四個軸控制來自既有官方z15原配準圖；北緣對Via Aurelia、東南近S.Francesco a Ripa。長寬採Res Gestae23經DAR換算的533×355m；**矩形是具名Taylor復原分支，絕非標籤182周圍自造的精確池岸**。來源角圓及局部寬差保存在GeoJSON的`original_source_geometry`，native矩形另存`native_geometry`；避讓窗包兩者。地圖讀點約10–20m或更大誤差之外，定位學說本身還有未量化不確定性。

原生使用現有通用`pool`，保有water材質及水平面，另給三片沿原圖綠色、北路、坡折與東側建成邊的`trees.region`和一條連Via Aurelia的園路。園界是明列的用途窗口／地形道路示意，不是園產界；先扣池與8m邊距。樹距16m、高8m、冠3.5m沿S111的同城Augustus墓周林地示意規約，不聲稱植株普查；4.2m園路寬沿既有AD14小徑估配。沒有任意完整圍牆或競技場看台。

pool的0.3m是既有原生水面顯示厚度，不是古池深度。Taylor可能1.5m平均深、現代8m埋深都**不從DEM扣除**。pool現狀取DEM中心水面，後續native樣張必須核水面是否被周緣DEM遮住；沒有可靠古水準面，本研究不另造一個絕對海拔值或修改地形。島與橋有文獻存在證據，本項有限包不選未知形狀／尺寸；不影響已補池／周林的公共用途。這不是已完成native地形驗收。

## 來源登錄與權利

已下載的五篇DAR正文、Stanford10opqr、Vitruvius5.1／5.10及Trümper原PDF存於`model_reference/ad14_campus_completion_*`，各原URL／bytes／sha256在`ad14_campus_completion_downloads.json`。原考古論著未直接取得者只透過DAR引述，不冒稱原刊已讀。DAR、官方考古圖及GRE圖只作研究，沒有取得影片上屏授權；既有Pantheon OSM控制沿©OpenStreetMap contributors／ODbL。

既有Campus配準來源`model_reference/ad14_public_dar_campus_sources.json`原樣保留；新Porticus Liviae crop的9張瓦片及EPSG3857 transform存`model_reference/ad14_campus_completion_liviae_sources.json`，正確含院體。Naumachia沿既有z15拼接及`ad14_fabric_dar_city_sources.json`，不重新自設控制點。所有量圖仍承襲DAR研究復原的不確定性，z17數米、z15約10–20m局部差不能視為測繪精度。現代DEM已含地形，所有古地坪相對下降不加入DEM。

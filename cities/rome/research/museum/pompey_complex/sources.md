# Pompey museum：來源、原生模型範圍與待建條件

本頁的對象是**龐培劇場＋柱廊＋龐培議事廳**，前55年起，展示前44年遇刺以前的形態。不是劇場單件頁，也不把Curia Julia混入。`museum/pompey_complex.yaml`採主線`f75c04f`新增的原生`pieces:[{id,node,landmark}]`，首件Curia作共同座標中心，頁面node指定`republic_pompey_observation`展廳。已核讀並在root合併後的原生工具實跑整組CPU驗證，待root生成明亮真高近圖。未寫candidate、flatten assembly、共享工具、canonical city、film、script、CREDITS或zh-Hant。未生成圖片、未跑GPU。

## 已讀來源與證據界線

本輪先讀`FACTS.md` S29／劇場、FUR39ac、Curia與園庭相關補記，並讀`research/rome02_pompey_refine_sources.md`、`rome02_pompey_refine_review.md`、`rome02_republic_quarter_sources.md`、`rome02_republic_quarter_garden_sources.md`、`rome02_republic_whole_sources.md`及canonical原件。沒有新網搜／新下載。下列「已讀」指本輪真正打開既存原文或圖，並不把既有筆記列的所有bibliography冒作親讀。

|頁內ID|既存原件／本輪核讀|可以支持|不能支持|
|---|---|---|---|
|M01|[Sovrintendenza：La Curia di Pompeo](https://www.sovraintendenzaroma.it/content/la-curia-di-pompeo/)；`research/model_reference/rome02_republic/pompey_curia_official.txt`正文|前44年3月15日元老院會議、凱撒遇刺於龐培議事廳；B/C廟後tufa基座；劇場—園廊—廳關係|未在此輪重看官方PDF全部五頁；既有筆記中的近代油畫不是考古立面。本頁不重建室內龐培像與遇刺場面|
|M02|[Marra等2021作者稿](https://www.earth-prints.org/server/api/core/bitstreams/360b9464-fa88-42e6-8306-22f1e37bc193/content)；`research/model_reference/rome02_pompey_refine/marra_curia_2021_author.txt`，PDF第4–5頁文字|近方形24×27m獨立廳、東廊中央位置；前55年啟用；原期與Augustan封堵材料／分期分開|作者稿未附Fig1影像；24×27m不是完整室內淨空或精確門窗立面。原高未給|
|M03|[Monterroso Checa2022原PDF](https://helvia.uco.es/bitstream/handle/10396/24612/17_Monterroso_Checa.pdf?isAllowed=y&sequence=1)；同夾`monterroso_complex_2022.txt`印刷300–301頁及前後園廊爭論段；實看`monterroso_p301_fig17_18.png`|獨立廳分支；Fig18A為Pompeian，18B才有封堵；後加latrines與廳不屬同一原期|完整共和立面、簷高、中央單門、屋頂和廊柱柱式未定。文中對晚二世紀約40m舞台的討論不能證前44年36m舞台；本頁將既有36m明標估值。未因作者質疑巨大雙林就斷言庭內無樹|
|M04|[Vitruvius5.9](https://lexundria.com/vitr/5.9/mg)；`research/model_reference/rome02_republic_quarter/vitruvius_5_9.html`全文|§1具名Pompey劇場後廊、避雨／準備舞台用具；§5、7的露天綠植、步行與排水原則|一般理想不是44年逐樹清冊、已知路寬、逐條排水或已知地坪。不能從理想柱式直接確定Pompey實際柱式|
|M05|[Vitruvius5.1](https://lexundria.com/vitr/5.1/mg)；`research/model_reference/ad14_campus_completion_vitruvius_5_1.html`全文，重點§6–9|Fano公共會堂50 Roman ft整柱、20ft支承；已有模型將其換算14.8／5.92m作有限比較|不是Curia Pompeia考古高程，不是共和建築通用層高；14.8m與5.92m均estimated|
|M06|[Stanford FUR39ac編目](https://formaurbis.stanford.edu/fragment_39ac.html)；`research/model_reference/rome02_republic_quarter/garden_stanford_39ac.html`，Description／Identification／Significance全文|大理石原件的圖形編目；較晚柱廊、長方形與點方塊的園池／柱／樹解讀爭議；長與寬精確性並不相同|Severan圖不是44年園庭調查；不能逐點種樹、復原兩池或把每個房間倒放。此輪未另外取得石片原始3D掃描|
|M07|[DAR Theatrum Pompeium](https://www.digitalaugustanrome.org/records/theatrum-pompeium-pompeianum/)；`research/model_reference/rome02_republic/dar_pompey_theatre.txt`全文|既有學術綜述：55BCE、向東cavea、原期與AD80後舞台分開；早期平直舞台為比較復原|本頁未親讀其所引Capoferro Cencetti、Sear、Gros全部原著；這是明列的二手綜述，不升格為新發掘。未用Severan曲折stage或爭議Venus突出部補模型|
|M08|[DAR Porticus Pompeianae](https://www.digitalaugustanrome.org/records/porticus-pompeianae/)；`research/model_reference/rome02_republic/dar_porticus_pompeianae.txt`全文|既有學術綜述：舞台後園廊、東端Curia及約180×135m中央區概述|以Severan平面為主；不能宣稱每一段44BCE長度、商鋪、niche或植物點位已知|

M01–M06為官方、原研究、古典原文或原石刻編目；M07/M08是明列的**既有學術綜述**。本輪沒有新來源，所以沒有以非primary新查補證。Lanciani配準與Caen尺寸只沿canonical geometry的既有basis認定為**先前模型值**，本輪未重看Lanciani該劇場圖版／未找到可逐數核對36／44／14／48的Caen原件，不能宣稱新核實測。不要引用它們冒充共和原高的直接證據。

## canonical精確match與保留範圍

以`museum.find_landmark`現有精確比對實跑；每個`kind＋id`在其指定node均命中一件。前3件在`republic_pompey_observation`，後4件在`republic_late_city`。後者在影片疊加前者；單取late node的landmarks會漏東半部，不可只憑同一時刻名稱猜全部都在一個node。

|來源node|landmark kind／id|lon, lat|theta_deg|資料子件／native records|既有labels|
|---|---|---|---|---|---|
|republic_pompey_observation|parts／curia_pompeia_east_frontage|12.47654878442462, 41.89512914804693|−88.21962144590233|16／71|空字串×71|
|republic_pompey_observation|parts／rome02_quarter_north_gallery|12.475339172704063, 41.89565194572005|1.7803785540976662|4／22|空字串×22|
|republic_pompey_observation|parts／rome02_quarter_south_gallery|12.475432489353004, 41.89450108313437|−178.21962144590233|6／24|空字串×24|
|republic_late_city|ring／pompey_theatre|12.47355, 41.8953|90|0／98|空字串×98|
|republic_late_city|parts／pompey_gallery_north_west|12.4744757, 41.8956129|1.7803785540999968|4／24|空字串×24|
|republic_late_city|parts／pompey_gallery_south_west|12.474569, 41.894462|−178.2196214459|4／24|空字串×24|
|republic_late_city|parts／pompey_gallery_west_cross|12.4740353, 41.8950154|−88.2196214459|4／39|空字串×39|

共**302 geometry records**，不含stand；資料子件38個，ring另為1件。各landmark既有`exaggeration:1`均保留。Curia原資料16子件沒有id，不能把現有空labels誤寫成`hall`、`roof`、`east/*`等不存在路徑。劇場ring同樣無細分labels。

本頁只選這七件既有建築，不改任何位置、形制、repeat、atop或比例。園內31樹群、grounds、貼地小徑、南側商住、北側百柱廊、四神廟與Venus寺不在`build_model`的單件landmark輸出內。三張scene cards不得把缺席建築「補得比較像」。植物用途在life與來源說明，配圖只用不遮輪廓的低植被色澤示意，不創造確定逐樹布局。

## 實際mesh bounds／真高度

輕量計算用`uv run --no-sync --offline python -I`載canonical、呼叫現有`find_landmark`／`build_model`，不寫build檔；再把原生records交`engine/props.js`的`buildEra`在Node CPU端算實際geometry bounding box。這**不是渲染**，也不是用保留地／`landmarks.extent`代替實際mesh。F.scale=0.0001。下表為**每件自己錨點**的東E、北N公尺界限；上高為其native平地輸出最大值，均不含stand，已四捨五入0.001m（僅計算精度，地理證據仍約5–10m及未量化圖解差）。

|landmark id|E min…max|N min…max|native最大高度m|相對Curia錨E,N m|
|---|---|---|---|---|
|curia_pompeia_east_frontage|−63.722…14.056|−69.608…67.370|18.315|0, 0|
|rome02_quarter_north_gallery|−35.017…35.017|−4.743…4.743|8.147|−98.6, 61.0|
|rome02_quarter_south_gallery|−35.017…35.017|−4.743…4.743|8.147|−94.6, −67.0|
|pompey_theatre|−75.190…15.000|−75.190…75.190|36.150|−248.2, 26.3|
|pompey_gallery_north_west|−36.616…36.616|−4.793…4.793|8.147|−170.4, 58.7|
|pompey_gallery_south_west|−36.616…36.616|−4.793…4.793|8.147|−166.4, −69.3|
|pompey_gallery_west_cross|−5.759…5.759|−67.701…67.701|8.147|−208.9, −6.5|

native records最低y=−3m是平地生成時的工具裙基／展示基礎，**不是考古埋深，也不是三米高古平台**。地表stand頂為0；不可把地下裙基畫成地表斷崖。真高度指倍率1，並不表示未知古高已成實測：Curia的14.8m是比較檐高，加覆屋後模型頂18.315m；廊柱5.92m，上頂8.147m；劇場h_m36加顯示地面頂36.150m。

以Curia錨為共同原點，實際整組union：E[−323.390,14.056]、N[−74.201,101.490]、Up[−3,36.150]；約**337.446×175.691m**。平面中心E−154.667/N13.645，頁draft採`at_m:[-154.67,13.64,12]`。不使用現有ring保留外框178m深作相機寬度，因為半劇場實際東西只90.190m。

需要root真高明亮近看的既有缺口：舞台最東E−233.200與西橫廊最西E−214.659之間約**18.541m**空隙；劇場錨N26.3與園廊中軸並不完全重合。這是現有模型近似關係，不能稱考古街寬，不移動建築消縫。北南廊間小型assembly接縫亦保留。這些**不構成已判模型不可讀**，但全貌圖必須實看，不能只靠數值過關。

## 原生工具缺口與可用做法

已讀主線`f75c04f`實作：每個piece依其node精確match一件，`landmarks.checked`補齊defaults；`build_model`逐件按原地理位置生成並以第一件錨平移一次，labels加piece id，原空字串會變成**piece id本身**，有子標籤時才是`pieceID/label`。因此本頁每個part同時列`pieceID`及`pieceID/*`，不只寫萬用尾綴而漏掉空子標籤。七件須全選一次，不取另一node的同址重複版本。Curia與theatre必含；其餘五件分別是北中、南中、西北、西南、西橫廊，沒有另放含相同段落的晚期porticus整件。

原生類別本來能用`kind:parts`組建，且內部禁止再巢狀parts；在獨立持久candidate裡flatten既有子件、保留repeat／atop與座標本是可行的資料做法。**本輪root明確要求不要做candidate flatten／assembly**，所以沒有建立，也不讓最後來源依賴臨時／snapshot。此處只採主線原生集合，無自建renderer或native替身。

`pieces`對應每source id及`source id/*`兩種part pattern；Curia part id為工具需要的`main`。每件3D體量都含估高／屋面，所以全標`estimated`，平面、分期與用途的有據部分在note逐項交代；**不為雙色效果把整廳或展示地坪標sourced**。如主線日後能不改形制地提供穩定部件索引labels，可再把可證平面與估高組件細分；目前不要臆造labels。

`tools/museum.mjs shots`桌面以`main` geometry的boundingSphere中心投影後實點，可能點到Curia＋東廊組合的空園庭而不是實牆；手機則以`data-part="main"`可直接開。root做桌面part圖時要實看點擊結果，必要時用原生頁面部件按鈕選`main`再拍，無須改共享shots工具。

## 三個視角與仍待實看

以Curia錨為`at_m`公尺原點（東、北、上）。`overview` az0/el28/d540/fov42、`reverse` az120/el28/d650/fov42，兩者看整組；`hall` az255/el18/d135/fov42、at[−10,0,8]，由園庭西北偏西近看入口，是刻意局部近圖，不要求把劇場塞在同一近景。全貌距離按上述真mesh bounds及原生`buildEra`CPU透視投影選取；須在原生bright頁面與手機實看後固定，才可living ref/gen。

原生多件CPU檢核：7個matcher各命中1件；302records全分到main71／theatre98／north_middle22／south_middle24／north_west24／south_west24／west_cross39，零漏件、零空part。比較實際primitive形狀、位置及種類，精確重複數0；未疊加另一個含同址內容的porticus整件。3視角方向夾角分別99.753°、94.144°、116.661°，皆高於50°；雙語欄位、所有cite ID及三張原生card必填欄位已驗。主視角330m時全組地表以上mesh投影NDC x[−0.784,0.847]、y[−0.520,0.411]，無裁切；reverse距離另留前景餘量。`hall`是局部，整個複合體有部分在鏡頭後方，不能把後方theatre的透視座標當近景fit失敗，也不能改相機成另一座廳。這些數值不代替明亮頁面實看；未執行museum整頁輸出／zh-Hant，該步由root統一做。

本輪只看了既存`build/review/modelview/rome02_pompey_refine/4_2.86.jpg`與whole第2圖：前者可辨獨立山牆廳、門洞和較低柱廊，後者為城市片的遠背景且有景深，**兩張均不是明亮museum真高驗收**。沒有用既存暗片／景深圖宣稱整組品質已過；root原生build與bright近圖後，若劇場／廳仍太粗讀不出，立刻回報，不換形制、不先出想像圖。

三張cards放同夾`overview.yaml`、`reverse.yaml`、`hall.yaml`。同為前44年會議之前的平常白日，人物微小、沒有凱撒／龐培特寫或血戲；材料、屋瓦顏色與低植被是受來源約束的示意，不宣稱出土色譜。`hall`不畫透明剖面或內部席位；若原生近圖因原件截窗／遮擋讀不出入口，先退回相機核對而非生成另一座廳。

最終原生shots構圖修正：16:9的原始ref雖未裁切，但桌面與手機較窄的展館舞台會切到劇場或議事廳。overview由330m改540m，reverse由410m改650m，hall局部近景不變；重新拍ref與生成兩張全貌圖，不移動模型、不以圖消去18.541m空隙。

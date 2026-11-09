# Pompey museum：來源、原生模型與頁面校正

> 以下校正節以前為初次建置紀錄，當時待辦已完成；本次校正與最新驗收見末節。舊紀錄的「待root生成／未生成圖片／待實看」不表示目前仍未驗收。

本頁的對象是**龐培劇場＋柱廊＋龐培議事廳**，前55年起，展示前44年遇刺以前的形態。不是劇場單件頁，也不把Curia Julia混入。`museum/pompey_complex.yaml`採原生`pieces`，首件Curia作共同座標中心，頁面node指定`republic_pompey_observation`展廳。下列原始錨點、尺寸和初建檢查保留作校正前依據；本次頁面定位、重新生圖與視覺結果見末節。只修本展館頁，不改共享工具、canonical city、film或script。

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

本頁只選這七件既有建築；保留形制、repeat、atop與比例，僅在展館頁校正劇場位置與方向（見下節）。影片與city.yaml原位保留。園內31樹群、grounds、貼地小徑、南側商住、北側百柱廊、四神廟與Venus寺不在`build_model`的單件landmark輸出內。三張scene cards不得把缺席建築「補得比較像」。植物用途在life與來源說明，配圖只用不遮輪廓的低植被色澤示意，不創造確定逐樹布局。

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

校正前外框量得舞台最東E−233.200與西橫廊最西E−214.659相距18.541m，但兩者斜度不同、極值取自不同橫向位置，不能當成舞台背牆到橫廊的垂直淨距。劇場末筆box的E−240.2是舞台**中心**，不是東面；其14m厚度使東面再向東7m。以中心冒作面而得到的約26m距離也不採用。現頁校正與實體接點計算見下節；北南廊小型assembly接縫保留。

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

既有原生shots構圖：overview由330m改540m，reverse由410m改650m，以容納桌面與手機較窄舞台；hall局部近景不變。這次先保留三鏡，從校正後原生模型重新拍ref，三張全部重新生成；不以想像圖代替幾何校正。


## 展館頁的同軸與相接校正（2026-11-09）

### 實看來源後的選擇

本次實看既存Monterroso2022印刷293頁Fig14（`rome02_republic_quarter/garden_monterroso-17.png`，Baltard/Canina歷史復原）、294頁Fig15（`garden_monterroso-18.png`，博物館模型）、301頁Fig17/18（`rome02_pompey_refine/monterroso_p301_fig17_18.png`，廳遺構及分期），以及已配準DAR地圖`ad14_public_dar_campus_z17.png`。另重讀M08既存原文：柱廊“directly behind the stage building”、西邊為stage building，廳在東廊中央；M04是具名劇場後廊的古典原文。這些圖與文字共同支持**同軸且相接**，因此不只南移/轉向，亦關閉劇場與西廊分離的大空隙。Fig14/15是文中討論的復原，不冒充共和遺構測繪；其晚期曲折舞台、神廟、樹池等均不移植到本頁。301頁考古圖只約束廳與東廊，不能獨立給出全組長度。

來源支持的是建築關係，不是本次位移小數。片中劇場與柱廊來自不同node的既有近似定位；只在`museum/pompey_complex.yaml`的theatre piece設定`move_m: [20.6, -33.4]`（東20.6m、南33.4m）和`turn_deg: 1.7803785541`，繞自身錨點轉動。其餘六件與所有302個records的形制、尺寸、parts及節點不變。`why`、頁面“Reading the model”及西橫廊note明說影片仍偏北且分離，city.yaml與既定成片未變。

### 為何移劇場，而不縮柱廊或移議事廳

不能據現有材料判定「柱廊長度比Lanciani的cavea定位更準」。本次未重新核Lanciani原版的劇場描點，只有canonical basis的近似中心／150m外徑與固定90°方向；M06編目反而明說FUR的柱廊**寬度與遺構相合，長度不相合**，所以也不能把保留的廊長當成前44年的精密實測。兩者不在本次可量化的獨立測量比較範圍。

選Curia/東廊作錨的理由是：M01遺址位置、M02的24×27m獨立廳與東廊中央關係，以及M03 p301 Fig17/18的原期遺構，共同限制其東端位置與關係；本次也實看`rome02_pompey_refine/dar_registration_overlay.png`，綠色廳／東廊控制線確實取DAR圖形中斷處而非27字樣（controls記EPSG3857、約0.89m/pixel、5–10m位置不確定度，不能當現代測地）。北南廊與東廊已從這組配準導出相同方向；獨立theatre原點與90°方向來自另一node的較早示意定位。相較於重新描量或伸縮整條廊、改動發掘支持的廳關係，頁面上保持這套完整廊庭、把單一劇場作剛體移到同軸相接，是在**保留所有既有尺寸**前提下表達M04/M08與已看平面所支持關係的有限選擇。它沒有宣稱否定Lanciani的古址，也沒有宣稱FUR廊長已勝過其他測量；若要判定絕對坐標或共和全組尺寸，需要另一輪重測，非本頁關係修正可回答。

### 位移與接點的估配方法

以原生EPSG:32633的Curia錨為E,N原點，已配準東廊方向−88.21962144590233°，共同東向軸u=(cos1.7803785541°, sin1.7803785541°)，橫向n與u垂直。原Curia錨(0,0)，cross錨(−208.89654,−6.49062)m；cross的軸側偏n·p=+0.00261m，故可用穿Curia的共同軸。原劇場錨(−248.22710,+26.29715)m，其側偏+33.99650m；只南移29.8m會忽略軸斜率，仍不共線。

旋轉後stage中心為theatre錨+8u，深14m，背面為theatre錨+15u；cross西側地坪為cross錨−3.46u，屋簷再向西0.20m。選stage背面與屋簷西邊相接，故理想錨在u方向−227.65735m、n方向0m，E,N=(−227.54745,−7.07296)m；相對原位(+20.67965,−33.37012)m。YAML採0.1m的(+20.6,−33.4)m，向西保守留0.1m量化餘量以免簷邊切入舞台背牆。原生座標也有0.1m輸出量化；保留約0.2m舞台背牆到廊地坪/柱的餘量，避免把劇場實體推進廊柱。這是現有簡化模型的拼接容差，不是已考證的古代空巷，也不是26m的考古街寬。

校正前的頁、模型、三張圖、ref、metadata與cards已保存到`internal/rome_museum_alignment/before/`。舊cards“必須保留stage gap”的限制已刪除；現在只要求生成圖遵照**校正後**ref，不自行移動、增補或融合兩個屋面。


### 原生幾何與俯視驗證

`measure.mjs`讀校正前保留模型與本次原生輸出，經`engine/props.js buildEra`量實際三角形（非landmark保留框）。共同u軸東偏北1.78038°、n是垂直側向；以下側偏是native量化後的模型值，公尺小數只用來排除拼接重疊，不代表考古精度。

|piece|校正前錨E,N（m）|校正後錨E,N（m）|校正前→後側偏n（m）|
|---|---|---|---|
|Curia/東廊|0,0|不變|0→0|
|劇場|−248.2,+26.3|−227.6,−7.1|+33.998→−0.025|
|北廊中段|−98.6,+61.0|不變|+64.034→+64.034|
|南廊中段|−94.6,−67.0|不變|−64.029→−64.029|
|西北廊|−170.4,+58.7|不變|+63.966→+63.966|
|西南廊|−166.4,−69.3|不變|−64.097→−64.097|
|西橫廊|−208.9,−6.5|不變|−0.007→−0.007|

南北廊是中軸兩側的廊，不是每根廊都放到中軸上；其成對中點接近n=0。新stage背面u=−212.708m，cross地坪西面u=−212.461m，cross屋簷西邊u=−212.661m：牆至地坪淨距約0.247m、牆至屋簷淨距約0.047m，均為正，沒有把stage實體推進柱廊。七件各自record數仍為71/98/22/24/24/24/39，合計302；其餘六件逐筆與before完全相同。

實看`build/review/museum/pompey_complex_alignment/before_overhead.jpg`與`after_overhead.jpg`，原先偏北的劇場已回到園庭與廳中線、舞台背面接近西廊，無明顯重疊；`bright_overview.jpg`、`bright_reverse.jpg`、`bright_hall.jpg`由原生museum頁暫時隱去圖片拍得，確認真高形體、廊柱、舞台與議事廳門洞可讀，沒有換renderer。三張living ref亦逐一實看後才gen。三鏡的az/el/d/fov/at_m完全保留。


這裡的共同軸還用**議事廳本體**核對，沒有只把第一件錨點當成古廳中心：main的原生records 1..4（廳牆、門牆、檐cap與屋頂，不含東廊翼）在u方向界為±13.680m、n方向界為±12.300m，其外框中線確為E,N=(0,0)。相反，main整件「廳＋東廊翼」的世界外框中心是E−24.833/N−1.119m；六件「整個園廊＋廳」的世界外框中心則是E−100.302/N−3.415m。主線約N−3.5的數值對應後者這種compound中心，不是廳本體中線，也不能不顧1.78°斜率便把劇場移到同一世界N。北/南中廊成對中點的n側偏約+0.003m，西北/西南廊成對約−0.065m；新劇場約−0.025m、西橫廊約−0.007m。這些殘差在native 0.1m座標量化附近；俯視已共軸可讀，保留這些估配容差，不為小數重改模型。


## 本次最新驗收結果（2026-11-09）

原生`museum.py cities/rome pompey_complex`完成：302 records、7 parts、3 viewpoints、3 with a picture。三張圖均經原生`living.py ref/gen/sheet`：先逐一實看ref，再生成並看完整圖與sheet；metadata的ref SHA1一致，工具記為codex、日期2026-11-09。最終reverse遵照ref保留近東廊、右長廊以及舞台腳下西橫廊的實背牆；沒有把它們換成開口柱列。圖中材質、屋瓦色、低植被與微小人物仍只是示意，沒有用成圖補上模型缺席的神廟、池、樹列或屋內席位。

`living.py check`三鏡都通過：overview平均差0.1、局部最大2.2；reverse 0.0/0.0；hall 0.3/3.9（工具門檻平均6、局部12）。這只驗證ref未在圖片下改掉；幾何與圖像的貼合另由sheet及現場頁面實看驗收，沒有以數值替代。

原生`tools/museum.mjs shots rome pompey_complex --lang zh-Hant`輸出11張桌面/手機圖，已逐張看主圖、轉15°、轉30°、有據/推測切換、部件note與手機全文；另實看`pompey_complex_alignment/desktop_*.jpg`與`phone_*.jpg`的三鏡及新西橫廊note。兩個全景鏡在桌面和390px手機均容納整組，hall保留原本局部近景用途；15°時圖片淡出、30°回到白模，切換和點選可用。所有完整上部體量仍標推測，沒有為雙色把整棟改標有據。新note明寫本頁移劇場而影片仍保留錯位/空隙；繁體字及腳注可讀、面板沒有截文。DOM的document/viewport寬分別1600/1600、390/390，無橫向溢出。前後clean overhead和明亮原生三鏡亦已實看；本次沒有更改三鏡camera、建築尺寸、節點、標籤或既定成片。

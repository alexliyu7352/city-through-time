# Colosseum：詳細模型、尺寸證據與80年界線

本筆記記錄尺寸查證與文字修訂；影片、共用模型及相機不變。詳細模型與新圖的最終檢查另由原生工具完成。
已看 `internal/blender_pilot/five_pages.jpg`（main工作樹），逐段讀
`tools/blender/amphitheatre.py` 的 `DEFAULT`、`from_landmark` 和 `build`。
舊筆記中241個generator records、矩形暗標、未分attic及其投影檢查，**不適用於新模型**。
新模型輸出名稱為 `facade_arcades`、`orders`、`attic`、`cavea`、`podium`、`arena`。

## 實讀來源

|代碼|原文位置與網址|採用範圍／限制|
|---|---|---|
|S06|[KCL Art of Making，Colosseum](https://aofm-os.kdl.kcl.ac.uk/explore/monuments/113/)，正文首三段，2026-11-10重讀|80年啟用；外牆材料；三層半柱依次Tuscan／Ionic／Corinthian，第四層為壁柱。條目所列考古書目未逐本讀。|
|S86|[Roma Capitale](https://www.turismoroma.it/it/node/1155)，建築介紹中從「L'edificio, destinato」至「L'arena」三段，2026-11-10重讀|189×156m、逾48m、三層各80券、arena76×46m及覆沙木地板。這是整座建築概述，不能逐項證80年完工。|
|S86V|[D’Anna／Molari，Il velarium del Colosseo](https://amsacta.unibo.it/6307/1/Velarium%2007-01-2020%2B.pdf)，本輪讀原PDF印頁3、9、22及相關圖說|p3對開幕期遮陽留有疑問；p9 Fig8辨Titus幣上桅杆與收帆（轉用Graefe圖）；p22記現存頂層托架／孔。其新遮陽篷方案及86×54m場地不採。|
|E07|[PArCo，I sotterranei del Colosseo](https://colosseo.it/mirabilia/i-sotterranei-del-colosseo/)，沿用並重讀專案存檔 `research/model_reference/imperial03_events_colosseum_hypogeum.txt` 歷史正文首段|開幕時木構技術空間，Domitian時改永久砌體。不將省略地下設施寫成80年地下空無一物。|
|E08|[Taylor等，2016](https://waters.iath.virginia.edu/Journal9Taylor_et_al.pdf)，印頁26注29，重讀專案存檔 `imperial03_events_taylor2016_p26.txt`|引晚期編年史「up to the shields」討論Domitian完成頂部。古代原文未另讀；木構地下空間以E07為準。|
|E09|[Elkins，The Flavian Colosseum Sestertii，NC166（2006）](https://www.academia.edu/354684/_The_Flavian_Colosseum_Sestertii_Currency_or_Largess_Numismatic_Chronicle_166_2006_211_221)，原論文印頁212與216–217錢幣目錄|Titus80–81幣已畫頂層及clipei；作者明言錢幣可預畫未竣工建築，因此不是完工證明。讀作者上傳正文，非摘要轉述。|
|E10|[Elkins，Publicizing Victory，INR14（2019）](https://www.academia.edu/44855461/_Publicizing_Victory_The_Frequency_and_Audience_of_Flavian_Judaea_Capta_Coins_from_the_Imperial_Mints_Israel_Numismatic_Research_14_2019_117_130)，原論文印頁124–126，Fig5–6|中央入口上quadriga與凱旋拱式入口圖像；第三層中央像群的辨讀及其保留語氣。不能推成每個券洞固定同樣雕像。|
|N01|[Berlin Münzkabinett，18200446](https://ikmk.smb.museum/object?id=18200446)，[館方原幣反面照片](https://ikmk.smb.museum/images/n0/459/rs_opt.jpg)|館方定80–81年、RIC II.1² Titus184；本輪直接看照片，可見頂層圓形裝飾。照片有Public Domain Mark，但本輪僅作研究，未納入公開媒體。|
|M01|[P. Colagrossi，L’Anfiteatro Flavio nei suoi venti secoli di storia（1913）](https://www.gutenberg.org/files/68663/68663-h/68663-h.htm#cap2-1)，PartI ChII，印頁41–45（HTML保留原頁碼）|原書建築描述給出下表實數；p44–45另記作者親察第三層XXXIII券之像座痕。尺寸段未列逐券量測方法、未將古代／近代修補逐一分層，因此不能直接稱80年精測。|

BM1844,0425.712原館頁回403；不冒稱已直接核讀該頁，改核Berlin原幣。
Wilson Jones 1993《Designing amphitheatres》的[作者上傳頁](https://www.academia.edu/14783704/Designing_amphitheatres_R%C3%B6mische_Mitteilungen_100_1993_391_441)
未提供可讀原文預覽（頁面混入其他文章），下載需登入；未讀到原圖33，不將搜尋摘要當已核測繪。

## 尺寸查核及spec取捨

`from_landmark`實際傳入外189×156m、ring55m、top48m、80券和podium參數4m。
這些沿用canonical；48m是概括高度，55m環深形成約79×46m內場，長軸較S86多3m。
不是只接受古人量尺：近代研究所記的建筑尺寸也可作概括復原依據，但不升格成80年完工清單。
採M01的三層高度與4.30m券寬、S06核實的柱式，並保留修補／分期限制；所有parts仍estimated。

|所查欄位|找到的原書／研究實數|目前處理與原因|
|---|---|---|
|三層 `h`|M01 p42：10.50／11.85／11.60m，後兩值明含柱座|採入spec（數值與DEFAULT相同）。來源是原書所記立面總高，並未逐券將後修分層；頁文明示這個限制。|
|`arch_w`|M01 p42三層均4.30m；另有二手計算表給4.44m，與DEFAULT4.20m不同|採M01的4.30m入三列spec，不採圖上換算4.44m；保留起拱估值，不宣稱逐券原尺寸皆相等。|
|`spring`|M01 p42只給券全高7.10／6.50／6.40m，未直接給起拱；由半圓假定可算4.95／4.35／4.25m，但上層起算面與程式柱座偏移需核圖|不把推導升格原文實測。DEFAULT為4.95／4.90／4.90，build另加pedestal，因此實際本層地面起拱4.95／6.50／6.50m。|
|上層 `pedestal`|M01只說總高含柱座，並另說觀眾廊地面在柱座頂、內欄牆約1m；沒有給外柱座獨立高度|不能把1m內欄牆改當柱座高；DEFAULT兩層各1.60m estimated。|
|attic高度／`attic_to_m`|M01 p42：13.90m，含柱座及底下方墩；p41街面至頂50m；S86逾48m|測量起訖不同，且開幕期頂層有E09分期問題。不用13.90硬改top48；現模型attic底0.6+10.5+11.85+11.6=34.55，名義高13.45m為估配。|
|各層柱式|S06明確Tuscan／Ionic／Corinthian；M01 p42–43把第一層稱非典型Doric、attic壁柱Corinthian|前三層與DEFAULT一致；attic模型是簡化方塊柱頭，並未雕刻Corinthian。文案不再說柱式未核實。|

[Homer-Dixon計算原附表](https://homerdixon.com/wp-content/uploads/2017/07/theupsideofdown-colosseum-walkthrough.pdf)
p4注5明說由Rea／Taylor／Wilson Jones圖換算；p6 Table6列spring4.95／4.45／4.40m、首層span4.44m；p9 Table8列另一組floor-to-ceiling高度。
本輪實讀這些頁，只用來追原文，不把其能耗模型的插值當獨立考古測量，更不把不同樓層定義直接填入 `storeys`。

`spec_of`只淺層覆寫，`storeys`須完整三列（不能只覆寫有據的h／order而繼承各列其餘值）。
故spec三列中的spring4.95／4.90／4.90及pedestal0／1.6／1.6只是備載原DEFAULT估值，沒有新增或偽稱來源支持；註解及part note均明示。
新採值只有券寬4.20→4.30m；層高／柱式雖加入spec，效果與原DEFAULT相同。
後續若核到原測繪，spring必須連同floor／pedestal起訖口徑重核，不直接用「券全高減半徑」替換。

## 四項只報證據，不建模

|項目|80年前後有何證據|能主張到哪裡|
|---|---|---|
|二、三層券內statues|Titus80–81幣有券內像形；E10 pp124–126詳辨第三層中央群像，使用不同幣模互證。M01 pp44–45記親見第三層像座痕|第三層有同期圖像及不精確定年的物證；第二層每券配置未由本輪原論文逐洞核實，更不能證開幕日160尊已全裝、逐尊材質／題材／高度。本頁省略，不是宣稱當年無像。|
|attic clipei|N01原幣照片可見頂層圓形裝飾；E09 p212直接辨為shields，並明確警告錢幣可能預畫|可說80–81年官方圖像已有圓盾方案；不能因此確定80年實牆與40盾均完工。E08晚期記述另留Domitian完成問題。|
|velarium masts|S86V p9 Fig8辨Titus幣上桅杆與收帆；p22托架、孔為遺構證據，p3卻對最初遮陽不確定|有同期圖像線索，沒有可保證80開幕桅杆數／高度／繩路的施工記錄。240是現存托架系統的復原總數，不等於已核80年裝備表。現模型已有托架與孔，沒有桅杆。|
|axial entrance porches|E10 p124見Titus幣中央入口上quadriga，並與Haterii凱旋拱式入口浮雕比較；M01 p44記軸入口旁柱與檐部碎件|支持顯著裝飾的入口圖像；未找到可分期到80、能定外凸門廊尺寸與四處同形的原測繪。幣側的雙層porticus在E09 p213解作Baths of Titus，不能搬成軸入口門廊。|

四項是否補建由main決定；本輪模型及scene cards均不加。同期圖像有某細節，與80年開幕時實際已裝成，是不同強度的主張。

## DEFAULT與分件對照

- `facade_arcades`：層高／券口依spec，起拱及柱座見上表；牆厚2.4m、內牆2m、廊深4.5m、內券寬外券九成；archivolt[.45,.2]、impost[.35,.18]及筒拱均估配。
- `orders`：base0.6m、半柱r0.5m、上層柱座1.6m、統一檐部高.7+.6+.4=1.7m及截面估配。柱式可辨，不等於柱頭細節測繪。
- `attic`：窗在隔一券處、壁柱、托架、檐口孔；孔／托架構成有遺構支持，模型位置、尺寸及80年狀態不逐項升格有據。
- `cavea`：terrace40m；bands由上而下rows10/24/4、rise .55/.62/.45、run .8/.78/1.4m、drop2/1.6/0、walk1.5/1.3/0m；stairs64、vomitoria64（每段牆）、portico160柱/h7/r.35m及平頂皆estimated。
- `podium`／`arena`：4m是傳入參數，build的pod_top=4+.9，欄牆再加.9，故平台約4.9m、牆頂約5.8m。頁文已改正，不再聲稱畫面牆高只有4m。沙面在arena物件，沒有地下室或木板厚度物件。

六個object由五個parts各配一次；arena part同收podium及arena。每個part含估配細節，故全部estimated。
相機沿用south／northeast／northwest；舊generator241件的取景聲明不適用。最終原生詳細模型為6objects／5parts，三鏡新圖均已採用，桌面與手機實看完成。
最終GLB名稱與分件、refs／sheet／adopt、桌機手機shots由runtime驗收。

查證階段的輕量驗證：YAML／zh-en／cite存在通過；由實際模組AST取得六個object名後呼叫原生`museum.assign`，六件各配一次、五part皆非空；三張卡欄位齊全；相機與HEAD一致且方向間距≥50°；spring／pedestal備載值與實際DEFAULT相等。其後已完成Hant逐字核讀、原生詳細模型建置、三鏡ref／gen／sheet／adopt、livingcheck及桌面／手機shots；不是沿用舊模型的檢查。

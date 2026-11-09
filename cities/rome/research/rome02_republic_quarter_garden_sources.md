# Porticus Pompei庭內園植補正

本輪只補批准411件quarter的庭內，13樓、Curia及全部既有廊／街不變。先native freeze當前quarter，舊輸入與所有舊圖保存在`rome02_republic_quarter_buildings_approved_frozen`。新件用獨立`rome02_republic_quarter_garden_spec.yaml`與新study名，沒有覆寫批准spec或重跑住宅parcels。

更正此前判斷：Dio44.16只述角鬥士藏在peristyle房間，**不能支持整庭無樹或全庭空板**；Monterroso對巨大雙林的質疑亦不是排除所有園植。這次把有文獻基礎的綠植步行用途實際畫出。

|ID|已讀原件／定位|採用|界線|
|---|---|---|---|
|G01|[Vitruvius5.9](https://lexundria.com/vitr/5.9/mg)，§1、5、7，全文已讀；歸檔`model_reference/rome02_republic_quarter/vitruvius_5_9.html`|Pompey是劇場後廊具名例；中間露天區應有綠植及步行，§7談砂面排水步行地。新增樹區與原生貼地步行線。|近時期理想與Pompey例證的組合，不是44年植栽點、砂路寬或排水考古圖。砂與排水原則不等於全庭鋪石或已知標高；未繪地下排水。|
|G02|[Propertius2.32.11–16](https://www.poetryintranslation.com/PITBR/Latin/PropertiusBkTwo.php)，2.32段；Kline譯文，正文已核|具名Pompey廊有整齊懸鈴木列及遮蔭。用外緣分段樹列、內側散植表園植與散步關係。|屬Augustan詩歌的近時期證詞，不宣稱同一株／同一行在44年已有；不能據文字反推出Severan兩個完整長矩形。沒有從詩歌倒造確定44年的泉池或雕像。|
|G03|[Vitruvius5.9.1／5.11.4](https://lexundria.com/vitr/5.11/mg)，兩章已讀|5.9所列Athens Eumenes廊是具名劇場後步行／庇雨比較；5.11的Greek xysta用懸鈴木園植、樹間步行及休息地作近時期公共園廊習俗比較。|前者不提供Eumenes確定植樹位，後者是理想類型而非Pompey測繪；只補未知綠植／步行配置，不放入希臘競技場或借其建築尺寸。|
|G04|[Monterroso2022，印刷292–296與300–301](https://helvia.uco.es/bitstream/handle/10396/24612/17_Monterroso_Checa.pdf?isAllowed=y&sequence=1)，已存原PDF；本輪實看Fig14 Baltard／Canina、Fig15 Gismondi；Fig18A/B沿批准分期|Fig14把樹放在內庭，Fig15與作者解讀偏向北外側；具名復原之間的分歧需保留。新園林依G01/G02取庭內綠植示意，Curia仍沿批准Pompeian分支，不稱已解決園林全布局。|不把作者對巨型雙林的質疑變成「庭內不得有綠植」，也不把19世紀圖或Gismondi後期模型的每個樹位稱共和實測。|
|G05|[Stanford FUR39ac編目](https://formaurbis.stanford.edu/fragment_39ac.html)，Description／Identification全文已核|原石刻編目明列長方區及點方塊的池、園或柱解讀不一，故不用Severan點方塊逐個生樹；只核後世資料的限制。|這不是44年種植圖，編目指出的疑問不阻止以G01–G03補示意園植。|

## 每項模型值

- 庭內兩側均有園植。北側一條7個位置樹列、南側分兩段2＋4個位置，外緣沿既有廊行進；中間另四個**不作實體花壇邊界**的散植區，循新步行線分段。這些不是Severan雙長園的等比例描摹；外形只作本窗的植栽用途域。
- 懸鈴木品類依G02；使用原生通用樹冠，只表樹木，並未重建物種葉形。`h_m:6`、`r_m:2.6`、散植約17m間距、行內約13–16m、行數及全部樹位為量體估值；沒有來源給本區44年逐樹普查或已知成熟樹高。原生隨機樹冠略有高低，不稱精確修剪測量。
- 主要走道4.8m寬，接批准Curia門前4.8m閾；北側橫行及南側斜接各3m，接既存庭邊路及南廊側入口。寬、線位與分叉是製作估配；用途按G01/G03。原生`path:true`將約3cm顯示薄面貼今日地形，沒有馬車轍，不造整庭prism及12m整平基礎。未改DEM或既有公共地坪。
- 中央通行軸與門前保持可讀；樹列和散植間留出步行空間。已批建築用`landmark_site`取得原生含6m的用地。其U形assembly的外包保留區包括露天庭，不能把整個保留區誤認為實牆；按照MODEL允許「region涵蓋有院建築、在空院種植」，用原生`plant()`的實體／平台避讓落樹，不自行寫幾何避讓器。新散植區由原生街路避讓，樹列在圖讀選定的行走線之外。
- 原圖座標、來源像素及native tree資料在`rome02_republic_quarter_garden_inventory.json`；新增步行線的同檔model／provenance在`rome02_republic_quarter_garden_trace.yaml/.geojson`。`garden_overlay.png`先實看再建，像素只控制相接關係，不提高示意植物／路線的證據等級。

範圍只在批准庭內，不擴城、不新增其他公共建築或住宅；古地面鋪材與標高仍不確定，但園植／步行用途已用模型實際表達，不能再以文字代替。

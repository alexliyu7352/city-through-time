# 113年：公共來源優先、內庭與Circus坡地

本輪仍在第4步，只改113年模型研究。住宅的街廓／房型做法已通過，並非每棟示意住宅不可移；有據公共建築優先。保留上一輪園地的用途、範圍與原生植栽做法，不以示意住宅迫使公共建築移址。未改共用程式、地形×2、比例、旁白或正式影片。

## 三處公共建築

|項目|依據、選擇及模型估值|處理|
|---|---|---|
|Magna Mater|[DAR](https://www.digitalaugustanrome.org/records/magna-mater-aedes/)及OSM1860921遺存牆線；33×17m基台、六柱前廊、AD3後修復。立面、柱高及階梯依S114的具名比較估值，沒有把早期已廢小池畫回。|按牆線錨點放回；移除2棟衝突示意住宅，不移廟。|
|Flavia東側小廳|S113／配準Lanciani、[宮殿研究](https://www.persee.fr/doc/befar_0257-4101_1999_mon_303_1?pageId=T1_389)與[Caen](https://rome.unicaen.fr/monument/palaisdomitien/)；小廳20×30m、檐高16m及確切局部位置為圖讀估值，傳稱Lararium的祭祀功能不作定論。|小廳作Flavia原生parts的一部分，共用大廳地坪。Augustana上院原估矩形的西北翼退讓此廳；東南半翼另收6.5m，修正與有據161×48m Stadium的重疊。不是移動整座宮殿。|
|Horrea Agrippiana|[DAR](https://www.digitalaugustanrome.org/records/horrea-agrippiana/)核矩形、多層，否定用錯FUR平面的做法；OSM13426221牆線的近似47×52.6m矩形定位。[PArCo地坪編目](https://colosseo.it/percorsi/camminare-sulla-storia-mosaici-e-pavimenti-in-marmo-nel-foro-romano-e-del-palatino/)說原有三層，[同園區另一頁](https://colosseo.it/percorsi/scoprire-egitto-parco-archeologico-colosseo/)說兩層。|選原有三層解讀，明列113分期／層數仍不確定；以鄰近Domitianic Paedagogium及已審服務院比較，估4.25m一層。9m翼寬、22度屋面、三排矩形凹口及其間距為估值；連續12.75m牆體，不是三座廳懸空相疊。移除5棟示意住宅。|

Vigna原先為避住宅而採台地初估中心西南19m的錨點，本輪恢復配準台地的初估中心，另移除2棟示意住宅。內側128×116m建築與160×140m台地仍分開，前者為估配，不把台地尺寸冒作完整建築實測外框。

## 移除的9棟住宅

|原因|原住宅id|
|---|---|
|Vigna來源位置|`subura_west_block_0335_house_03658`、`subura_west_block_0335_house_03700`|
|Magna Mater|`velabrum_boarium_block_0247_house_02524`、`velabrum_boarium_block_0262_house_02687`|
|Horrea Agrippiana|`middle_rental`、`velabrum_boarium_block_0262_house_02675`、`velabrum_boarium_block_0262_house_02678`、`velabrum_boarium_block_0262_house_02686`、`velabrum_boarium_block_0291_house_02922`|

原住宅特徵及移除原因逐筆保存在[changes](imperial_completion_changes.json)。其餘8868塊住宅用原宅界、房型和固定層數，不重鋪住宅區。原生row／detached會隨共享隨機序列改變少量院深／屋深，移除房屋後不能宣稱每個模型記錄逐byte相同；本輪如實列出這些差異。5394座保留的固定層數court／compound，實際模型幾何仍逐件相同；所有住宅均核實有生成、層數符合類型、無穿模。

## 園林及Palatine—Circus空地

|地方|本輪處理與依據界線|
|---|---|
|Vigna|沿S112中央庭園種植；主線5dd2c1e讓樹站在台地上。39棵樹的地面與台面最大顯示誤差0.037m，沒有仍埋在台面以下的樹。|
|Pompey|[Stanford FUR39ac](https://formaurbis.stanford.edu/fragment_39ac.html)、既存DAR／Caen支持柱廊內園林；150×105m種植範圍、16m間距及8m通用樹高為估值。內庭61棵，廊牆內0。|
|Peace|[Roma官方發掘介紹](https://www.turismoroma.it/it/node/1053)支持花壇與水景。兩片38×76m植栽帶為讀圖／園藝示意，非宣稱發掘出113年的兩塊花壇；6m通用樹、14m間距為估值。內庭31棵，廊牆內0。|
|Sallustiani／Lucullani|園地範圍計入原生城市外框；檢查所有院外樹點均在外框內或原生8m簡化邊緣的10m容差內。另拍遠景確認發光範圍確實包住園林。|
|Circus朝向的外廊|[Roma Capitale導覽](https://www.turismoroma.it/sites/default/files/itinerari-romani-la-culla-della-civilta-2196.pdf)、配準Lanciani與Caen支持Augustana朝Circus的半圓外廊。100m寬、28m投影、雙層4m柱廊、具體柱數及平面細節為估值；只配置原生column／prism，不自製曲面或檢視器。|
|外廊、Paedagogium及Circus之間|按MODEL「No empty cities」補出坡地庭園299棵；確切113園界及種植配置無完整考古平面，明列同期習俗補全。既有街道保持暢通，Circus整個場地從種植範圍扣除；沒有把可種植的競技場內圈誤種成樹林。外廊內的台面保留為開放前庭，不把每塊空地都種滿。|

[TESS4968](https://tess.beniculturali.unipd.it/web/scheda/?recid=4968)將現存Schola Praeconum定為Severan，本版不為填空而倒放；同樣不加Septizodium、晚期Stadium內橢圓或已被宮殿埋住的共和住宅。無資料坡地作園林是示意，不冒作新發掘結論。

## 原生工具與檢查

移除上一輪對樹木障礙的手動外框遮罩，直接把完整region交給原生工具；牆體、prism洞、圓環中間、平台及坡度由主線處理。園界因單環格式需要而分片，並非自製種樹器。建築與所有造型仍由既有原生類別生成。

Horrea曾嘗試把三層long_hall用atop相疊；`landmarks.top`對flat roof仍加入按斜屋頂計的高度，近景與實際記錄顯示樓層懸空。沒有改共用程式；最後採本來就應連續的倉庫牆體，用原生三排凹口表現三層，未手算z去懸疊樓層。此工具限制不影響本輪最終模型。

最終只有113獨立模型研究，原生geocheck／clipcheck及目標園林數值另存本輪evidence。20秒無旁白、停113及末段靜止，是modelview研究設計；不宣稱正式全片聲音、字幕或鏡頭檢查已完成。未做整片渲染、聲音或第5步分鏡。

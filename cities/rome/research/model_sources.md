# 羅馬第4步：帝都城市布局與形制來源

目前採用狀態：113年公共建築／營區、有據街道及地形×2已確認；舊9,835棟格網住宅退回。新[Subura69棟樣區](subura_sample_review.md)已確認，現依同法完成20區住宅，[遠景與各區近景](imperial_housing_review.md)交審；逐區採用順序、來源年代與示意缺口見[住宅來源表](imperial_housing_atlas.md)。舊整城住宅資料只供對照，不是確認基線。

範圍：第03站前27年至113年的城市示意。先做資料最多的帝都近景，供模型辨識房屋、街道與丘陵；不是把今日遺址或4世紀復原圖整張倒放到113年。採用的模型依據已補入FACTS；未改旁白、正式city.yaml或共用程式。下列為研究參考，外部圖片未放入assets或片中。

## 可建模的整座城市

以**約14年的Digital Augustan Rome作早期帝都基線**，按已核年代加入Flavian宮殿、競技場及Trajan廣場／柱。不能用三世紀奧勒良城牆圈出113年城市，也不能用四世紀14區圖作同年已密建的外框。

University of Arizona Archaeological Mapping Lab的[Digital Augustan Rome](https://www.digitalaugustanrome.org/credits/)由David Gilman Romano主持，Mark Davison作圖。[Continentia](https://www.digitalaugustanrome.org/records/continentia/)（學術地形條目）指出建成區早已超過Servian城牆及pomerium；主要外展為西北Campus Flaminius至Campus Martius，及西南Emporium沿河倉庫與右岸發展。Transtiberim相對較小；東北／東邊有大面積horti，不是均勻住宅地毯。圖上留白是缺證據，不能當成無人。

據此，整城可分為下列**概括連續城市群**，不預設單一規整外框：

| 區段 | 模型安排 | 定位與界線 |
|---|---|---|
| Forum—Palatine—Circus主核 | 廣場／神廟／宮殿／住宅相連，山丘與谷地分開 | Lanciani 29、35，公園官方Palatine說明及現代已核遺址位置 |
| 帝國廣場北側—Subura—Esquiline／Viminal谷地 | 依主要街軸分街廓；住宅、沿街商鋪、內院，保留不規則密度 | Lanciani22及30；DAR Subura／Argiletum／Clivus Suburanus的概括地形 |
| Campus Flaminius—Campus Martius | 劇院、柱廊及公共空間間穿插街區，北側不整片塞房 | DAR Continentia、地標位置；新增地標另核時期 |
| Forum Bovarium／Velabrum—Aventine—Emporium | 沿河商倉與坡地住宅；大倉庫和一般住宅尺度分清 | DAR Emporium／Horrea／Vicus Tuscus；南端不以後來城牆當建成邊 |
| Transtiberim | 河右岸有較小城市片區，與核心由橋相接，Janiculum高處不一律密建 | DAR Continentia（14年基線；113年外展須標示意） |
| 北／東側horti及邊緣 | 林園、田地與分散建築有意留白；道路沿線外伸，不畫平滑同心圈 | DAR Continentia；以證據不足及非密建區分，不造精確113年城界 |

這是**可據以生成整城的分區布局**；尚未配準描摹為已驗收GeoJSON。113年外圍的逐棟／逐街界線沒有在本輪找到完整實證，故整城外展標Schematic。建成區不是Servian城牆、pomerium或後來Aurelian城牆中的任一條線。

## 地理對位與可直接讀取的資料

### Digital Augustan Rome，約AD14

已保存官方公開API的463筆地標條目：
[records.json](model_reference/digital_augustan_rome_records.json)。位置有WGS84經緯度的項目另整理為[候選定位點GeoJSON](model_reference/augustan_location_candidates.geojson)。

**這些是地圖標記點，不是建物測繪邊界。** 部分條目僅有近似位置或未確定平面，原分類保存在properties。不能把精細經緯度小數誤當考古測量精度；64年火災及後續重建也不能保證14年的房屋在113年原樣保留。

可定位的代表點（經度、緯度；地圖標記）：

| 項目 | WGS84點 | 用途與限制 |
|---|---|---|
| Basilica Iulia | 12.484821，41.891866 | Forum南側長建築定位；具體外框用考古圖 |
| Castor神廟 | 12.485602，41.891541 | 與Basilica Iulia之間是Vicus Tuscus已核出口 |
| Horrea Agrippiana | 12.485034，41.890657 | Vicus Tuscus南續的有據倉庫／鋪面錨點 |
| Domus: Vicus Tuscus | 12.485392，41.891018 | 不確定平面住宅的定位，不能當輪廓 |
| Domus: Sacra Via | 12.486957，41.891686 | 住宅街區錨點，非完整住宅區外框 |
| Horrea: Sacra Via | 12.488242，41.891172 | 商倉定位，需避後世Basilica Maxentius幾何 |
| Domus: Palatium (9) | 12.487714，41.891217 | Palatine北麓住宅候選，平面不確定 |
| Vicus Patricius | 12.495934，41.898037 | 街道的地圖標記，不是一整條路線 |
| Porticus Aemilia／Emporium | 12.474278，41.880517 | 沿河商倉區錨點，倉庫形制與住宅分清 |

現有OSM的roads主題只收主要道路，沒有包含Via Sacra及Regola的這些小街。本輪嘗試另取幾條局部街道，Overpass分別回406及502，**沒有取得新的可用路線**；不假報已完成地理描線。

DAR地圖是配準raster overlay，不是多邊形API。已保存4張zoom13概覽tile供定位：
`dar_z13_4379_3043.png`、`dar_z13_4380_3043.png`、`dar_z13_4379_3044.png`、`dar_z13_4380_3044.png`。
它們沿標準Web Mercator slippy-tile座標，URL模板：
`https://phf-cms-prod.s3.us-west-2.amazonaws.com/maps/digital-augustan-rome/{z}/{x}/{y}.png`。
地圖署名Parrhasian Heritage Foundation；未見可上屏的CC／PD授權，僅研究參考。

### Lanciani平面與現代配準

Rodolfo Lanciani，Forma Urbis Romae，1893–1901。University of Virginia的[Aquae Urbis Romae圖版索引](https://waters.iath.virginia.edu/forma_urbis.html)提供原圖掃描。本輪已下載並實看：

| 本機檔 | 圖版 | 能讀出的布局 |
|---|---|---|
| [lanciani_22_forums.jpg](model_reference/lanciani_22_forums.jpg) | XXII，Fori Imperiali | Trajan／Augustus／Caesar／Nerva等廣場的相鄰方向、Quirinal山麓、Argiletum與Subura周邊 |
| [lanciani_29_forum_palatine.jpg](model_reference/lanciani_29_forum_palatine.jpg) | XXIX，Forum Romanum | Forum谷地、Palatine、Sacra Via、競技場西半，以及後世遺構的層疊 |
| [lanciani_30_oppian_colosseum.jpg](model_reference/lanciani_30_oppian_colosseum.jpg) | XXX，Thermae Traiani | Oppian坡地、金宮遺構、競技場東側Ludus Magnus，局部街軸與商業設施 |
| [lanciani_35_circus_palatine.jpg](model_reference/lanciani_35_circus_palatine.jpg) | XXXV，Circus Maximus | Palatine南坡、Circus長軸／看台、Caelian方向與坡地關係 |

原黑線是古代遺構，**黑線也混有不同古代年代**；紅／藍另是後世城市層，不能把整張抄成113年。圖29上的Venus and Roma、Basilica Maxentius等正是必須排除的後來建築。

[David Rumsey / Stanford館藏記錄](https://www.davidrumsey.com/luna/servlet/detail/RUMSEY~8~1~308707~90078572)提供Lanciani拼接圖及Google Earth配準網路連結。本輪存下的[lanciani_georeference.kmz](model_reference/lanciani_georeference.kmz)只有doc.kml及NetworkLink，**不含全幅高解析影像，也不是完整離線地圖**。它給出WGS84包圍框，並連向：
`https://rumsey3.s3.amazonaws.com/Rome_Historical_Lanciani/0/0/0.kmz`。
可作後續地理對位工具，再用競技場、Circus、Castor神廟等仍可辨遺址核對配準誤差，不能直接宣稱已配準完成。本輪沒有下載全套tiles。

## 可落位的幾段街軸與街區

1. **Vicus Tuscus短段：** [DAR學術條目](https://www.digitalaugustanrome.org/records/vicus-tuscus/)核實Forum出口在Castor神廟與Basilica Iulia之間，向南到Horrea Agrippiana旁有古鋪面。可用上述三個地標和Lanciani29畫這一段；再往Forum Bovarium／Circus的精確續線有爭論，畫概括連接並標示意，不把直線連心當精確街道。
2. **Regola沿河商倉街區：** [Sovrintendenza官方頁](https://sovraintendenzaroma.it/i_luoghi/roma_antica/monumenti/insula_di_san_paolo_alla_regola)明說現代Via di San Paolo alla Regola沿共和古路，連Circus Flaminius與Campus Martius；Via delle Zoccolette／Via di S. Paolo alla Regola大致沿河，Via del Conservatorio／Via dei Pettinari大致垂河。Domitian時期倉庫成排、沿平行河流的街巷，範圍大約在今日Pettinari與Arenula之間。可依這些有據街軸製作局部商倉街廓；整個區塊邊界仍標概括，不自造每一棟平面。
3. **Argiletum—Subura—Clivus Suburanus：** [DAR Subura](https://www.digitalaugustanrome.org/records/subura/)稱繁忙街區沿Cispian與Oppian間谷地，自Argiletum向Servian牆延展；西入口在Madonna dei Monti附近。可沿谷地畫不規則街巷／住宅塊，向Forum連接，不能在整個山頭套同一正交格網。條目全文及作者Elisha Ann Dumser見[API記錄](model_reference/digital_augustan_rome_subura.json)。
4. **Palatine北麓：** [DAR Palatium](https://www.digitalaugustanrome.org/records/palatium/)支持Sacra Via以南至Clivus Palatinus之間的高級住宅密集區；山頂街網則不清楚。已核Domus定位點可分布於北麓，丘頂不能隨意添一組整齊街網冒作實證。

## 首輪整城模型的工作窗

下列bbox按上文已核地點及源圖地形選作**製作研究窗**，順序是[西、南、東、北]；是方便落位、裁切與近景取景的建模推定，**不是史料給出的精確113年住宅區外框，也不能整個矩形均勻塞房**。先依河流、主街、古蹟及園林遮罩分出不規則區塊，再生成房屋。

| 區塊 | 建議工作窗WGS84 | 先落位的錨點／街軸 | 填充方式與保留 |
|---|---|---|---|
| Palatine北麓住宅—Forum | [12.4845,41.8899,12.4888,41.8922] | Basilica Iulia、Castor、Horrea Agrippiana、Domus Palatium (4–9)；Vicus Tuscus短段 | 住宅沿山麓與街緣，Forum／宮殿平台不填一般房屋，丘頂街網不當實證 |
| Subura谷地 | [12.4885,41.8930,12.5020,41.8985] | Augustus廣場背牆、Argiletum、Madonna dei Monti西入口、Clivus Suburanus、Vicus Patricius標記 | 隨谷地與不規則街軸形成連續街廓，北東邊與Horti不作同密度鋪滿；具體路線仍示意 |
| Regola沿河商倉 | [12.4701,41.8918,12.4765,41.8948] | Pons Agrippae標記[12.469985,41.893157]作河岸參照；現代Pettinari／Conservatorio垂河，S. Paolo alla Regola／Zoccolette沿河 | 依官方描述做成排Domitian商倉，不把Severan四層住宅原樣倒用；河面及街巷留空 |
| Emporium—Aventine河岸 | [12.4710,41.8785,12.4785,41.8840] | Porticus Aemilia標記[12.474278,41.880517]及Tiber | 大倉庫片區與Aventine坡地住宅分尺度，不能用一種小房子均勻填滿 |

整城的概括建模工作窗可取[12.465,41.875,12.512,41.918]，只界定需要研究的古代主城工作空間，不改已確認台面，也不是城市邊界。外輪廓由生成建築與已核布局形成；AD14基線以後、至113年的新增與重建分群標明。113年獨立模型可先審查，但不能把它提前放進正式03站的前27年鏡頭。

## 地標形制與坡地驗收

第4步已確認[Forum—Palatine西北麓小樣](forum_palatine_sources.md)，並擴展為[113年整城示意模型](imperial_113_review.md)。舊primitive拼塔／任意縮放地標、三角剖分街區的程式與資料已保存在`archive/pre_registered_layout/`，不再作驗收依據；`build_imperial_config.py`只匯出已標來源的布局資料，造型使用已審types及現成地標類別。現已取得館藏自帶配準的Lanciani局部瓦片與DAR z17小窗，並核實現有OSM快取包含Vicus Tuscus／Via Sacra。舊`imperial_city.yaml`仍是已停用試驗；目前獨立整城規格為`imperial_113_city.yaml`，詳本輪交付。

| 地標 | 已核資料與建模要點 | 年代／限制 |
|---|---|---|
| Palatine宮殿群 | [公園Palatino](https://colosseo.it/area/palatino/)說明從Augustus諸宅到後繼宮殿的累積；[官方地面／馬賽克導覽](https://colosseo.it/percorsi/camminare-sulla-storia-mosaici-e-pavimenti-in-marmo-del-palatino/)給Domus Flavia的中央長方形peristyle、三面殿室，北Aula Regia、南宴會廳；Domus Augustana是較小房間與柱廊園庭 | 可做113年宮殿布局參考；晚期地板及後世修補不能當初建面貌；不用中國宮殿／城樓形制 |
| Palatine所謂Stadium | [官方條目](https://colosseo.it/mirabilia/stadio-palatino/)：161×48m，西南端曲線，宮殿東側約低10m；三面柱廊與東側exedra | Domitian晚1世紀已有，113年可概括；後來Hadrian／Severan裝飾不倒用；內部晚期橢圓圍場不放113年 |
| Colosseum valley與湖 | [官方Domus Aurea](https://colosseo.it/area/domus-aurea/)：人工湖在競技場谷地，金宮核在Palatine與Oppian，建築間是園林 | 湖無精確邊界，依谷地概括示意；不能做全城水淹。競技場80年啟用依既有FACTS S06；外廓／朝向以遺址幾何和Lanciani核 |
| Circus Maximus | [Sovrintendenza](https://sovraintendenzaroma.it/content/circo-massimo-2)：在Palatine與Aventine間Valle Murcia，Caesar起砌石，Trajan大規模重建；[市府旅遊頁](https://www.turismoroma.it/it/luoghi/circo-massimo)給概略600×140m | 64火災前與113年末景應分期，不能同形一鍵替換；357年新增方尖碑不能放入113年 |
| Trajan Forum／柱 | [官方博物館頁](https://mercatiditraiano.it/it/sede/area_archeologica/foro_di_traiano)：整體約300×185m，開鑿Quirinal／Capitoline相接山坡；廣場兩側柱廊與exedra，一端Basilica Ulpia，後方柱及兩側圖書室 | 112廣場／113柱分期。官方重建圖已保存為[trajan_forum_reconstruction.jpg](model_reference/trajan_forum_reconstruction.jpg)，研究參考、未取得入片授權。圖中後部的Trajan廟等如年代未核，不採作113年必有細節 |
| Regola商倉 | [官方頁](https://sovraintendenzaroma.it/i_luoghi/roma_antica/monumenti/insula_di_san_paolo_alla_regola)及[官方兩頁說明PDF](model_reference/san_paolo_alla_regola.pdf)有Domitian倉庫、沿河街巷及後世剖面 | 1世紀倉庫可用；現存至少4層的辦公／住宅／庭院配置主要是Severan改建，不能作113年的逐層實證。地下8m是現代地面相對考古層，不能把倉庫直接埋在今日DEM下8m來演當年城市 |

坡地近景宜用**Forum谷地—Palatine北麓／丘頂**對照，並讓Circus或競技場谷地提供另一個低處。文獻直接支持Palatine西南／西北側陡坡、北東鞍部較緩；Palatine Stadium約低宮殿10m是可核對的局部高差。不能為通過tall_foundation而把丘陵削平；今日DEM也不是古代每一處地坪。

## 不可放進113年末景的常見錯置

- 奧勒良城牆（271起）；第04站才出現。
- [Venus and Roma神廟](https://colosseo.it/mirabilia/tempio-di-venere-e-roma/)（121起），尤其今日雙後殿包含後來重建形制。
- [Basilica Maxentius](https://colosseo.it/mirabilia/basilica-di-massenzio/)（308起），其位置原先有Horrea Piperataria，不能把後來大殿倒放。
- Constantine拱門、Caracalla浴場、Diocletian浴場；本輪不新增旁白事實，只列建模排除項。
- 今天修復的Curia內飾不能當113年原狀：[官方Curia頁](https://colosseo.it/mirabilia/curia-iulia/)明示有Diocletian重修遺存。

## 其他研究參照與權利

[Stanford Digital Forma Urbis](https://formaurbis.stanford.edu/)的10g碎片辨識Subura大街、巷道、店面、公寓、庭院等，可作形制比較；但整張大理石圖是203–211年，不是113年。依[Stanford權利聲明](https://formaurbis.stanford.edu/docs/FURcopyright.html)，本輪**沒有下載或保存碎片照片及3D模型**。

公園2020年新聞素材頁有Forum／Sacra Via／Palatine平面下載候選；瀏覽工具可開圖片URL，但本機curl遇TLS失敗，沒有假報檔案已存。頁面限定新聞用途，不能直接當本片素材：
[新聞素材頁](https://colosseo.it/press_kit/il-parco-archeologico-del-colosseo-riapre-i-cancelli-il-1-giugno-2/)。

所有已存掃描、地圖tile、PDF、官方重建圖及API資料只供此專案研究與建模核對；未完成可上屏素材核權。Lanciani原圖作者、年代與後續掃描提供者分開記錄，不把古圖年代等同現代掃描／重建圖的授權。正式片中使用自行生成的Schematic模型，仍需在FACTS補入實際採用的地理／形制來源。

檔案清單、來源及雜湊見[model_reference/README.md](model_reference/README.md)。

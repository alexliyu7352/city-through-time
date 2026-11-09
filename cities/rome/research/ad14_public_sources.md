# AD14 公共量體提案來源

這是早期版本研究與原生資料提案；主代理已採用19件keep，另外三件沿已過AD14樣區原件。新形制按逐項狀態待審；未編譯、未看模型，也不是第4步整城驗收。

## 第一批可用資料

`ad14_public_inventory.json` 逐件覆蓋既有107件公共要素，分開 keep／revise／omit，保存原形來源id、錨點與版本標記。`ad14_public_keep_proposed.yaml` 只輸出現成原生landmark欄位。keep指低細節量體可重用，不表示其上部已被測成AD14原貌。三件已過樣區物件以正式AD14樣區輸入為準，這份清單不授權改動其幾何、順序或Horrea層數。

已全文讀取AGENTS、SKILL、RESEARCH、MODEL、FACTS及交接所列七份既有研究正文；已有來源與各自讀圖／估值界線直接保留。未把DAR標籤當幾何中心、未用`period_ce`篩早期建築。原始重複48件兵舍均逐件列omit，建營20–23年與舊模型25標記不同。

保留量體的文獻依據見 `early_imperial_layout_sources.md` 的「113公共量體逐項分流」、FACTS S89/S92/S96/S98/S100/S114/S120/S124–127；其原形／定位依據保存在每筆basis及來源trace內。外部參照僅研究，未授權上屏；OSM錨點沿原ODbL署名。

## AP01 Circus Maximus

[DAR Circus Maximus](https://www.digitalaugustanrome.org/records/circus-maximus/)，已直接核讀正文（段落 Caesar dimensions／Dionysius seating／Our map）。這是考古地形研究綜述，非本輪直接取得Humphrey或Ciancio Rossetto原發掘。

可用：Caesar/Augustus U形看台；文獻尺寸有621×118m及650×125m兩種換算；DAR估看台深28m，最低石造、上兩級木構，外側一層廊及店舖。起跑閘12個；10BCE方尖碑。原生`ring u`可承載概括看台，但永久連續中央spina不應在AD14沿用；DAR認為其可能二世紀才建。轉柱間距約335m也是復原假說。高度尚無測量值，應由具名復原／座席坡角比較明列估值，不能把三個座席區誤作三層外拱廊。

## AP02 Basilica Paulli／Aemilia

[DAR Basilica Paulli](https://www.digitalaugustanrome.org/records/basilica-paulli/)，已直接核讀全文。54BCE重建、34BCE奉獻、14BCE火後Augustan修復，AD22只是後修。Forum一側Porticus Gai et Luci有十五間店舖及雙層券廊；現有單廳不表現這個街面。圖號LTUR I fig.102及FUR16e作尋圖線索，尚未據其未讀圖版聲稱量得尺寸。

## AP03 Forum Iulium

[DAR Forum Iulium](https://www.digitalaugustanrome.org/records/forum-iulium/)，已直接核讀全文。早期廣場三邊柱廊、NW端Venus神廟，SW後方商舖；北側與Augustus廣場接合仍假設。DAR說46BCE首奉獻、44BCE完成再奉獻；其他官方來源對完工／Octavian工程有不同概括，本提案不以44年作精確施工完工定論。現有四邊實體圍框不宜直接作早期精確形態。Chalcidicum辨識有爭議，模型不把爭議功能寫死。

## 待補與採用界線

新／改形幾何分批保存；最先處理Circus、Aemilia、Caesar Forum、Agrippa公共區、Augustus Forum四exedrae。Augustus宅兩古台地7–9m差不能變成DEM上加8m；Livia尚未批准屋頂候選，也未把現代外框填滿。Apollo圖書館早期存在不證明現有Domitian雙apsidal halls可用。

## AP04 Circus：具體原生提案及高度估算

`ad14_public_revisions_proposed.yaml` 的Circus採621×118m文獻換算分支；不是把舊600×140m/20m Trajan版本換日期。以28m席帶算出62m內寬，兩直段各562m，東南半圓半徑59m；原址中心 `[12.48531,41.88592]`、theta−32°直接沿原已核OSM11384819／Lanciani谷軸，不能稱重新測得Augustan端點。

上部沒有精確古高，採[Vitruvius5.6.3](https://lexundria.com/vitr/5.6/mg)同期劇場座席的最低高/最大深比例1.25/2.5=0.5作**跨娛樂建築類型的估算**，28×0.5加估3m席前牆＝17m。不是把Vitruvius劇場規則說成Circus測量；分界位置、平台寬、17m及起跑閘4.25m全是模型選值。native `ring`的席帶28m會自動只生成兩個大區，故改用原生`prism.section_m`及半周`revolve.profile_m`資料明列三區，沒有自製網格函式。圖面應核三帶、曲端向SE、起跑端向NW。

最小形體仍不畫木構支架、外側一層廊的完整通行空間、店房與euripus，也不畫尚缺本輪位置/高度核對的第一方尖碑；**第一方尖碑在10BCE已存在，缺畫不能寫成不存在**。本提案用三個大席帶表示Dionysius記述的材質分區；白模材質不區分木/石，不能聲稱已復原所有層次。[DAR pulvinar](https://www.digitalaugustanrome.org/records/pulvinar-ad-circum-maximum/)明說無依據估其尺寸，因此不加一座任意尺度的皇帝包廂。[DAR obelisk](https://www.digitalaugustanrome.org/records/obeliscus-circus-maximus/)給約3m方基與兩轉柱中點；整體高度及現代原址套合尚待別次具體採用。

## AP05 Aemilia：店數不等於券數；兩組尺寸不混作測量

[PArCo，2020-07-21官方資料，印刷/PDF第8頁](https://colosseo.it/sito/wp-content/uploads/2020/07/CS-Visita-Presidente-Senato.pdf)明列Augustan正面**16券**，其後商舖，再後才是basilica。DAR記**15商舖**；二者不是同一計數。官方同頁說北側有兩小廊的相位差別，通用對稱`aisles`不能準確畫此四廊內部，本提案明列未復原。

[Platner/Ashby1929，pp.74–75](https://penelope.uchicago.edu/Thayer/E/Gazetteer/Places/Europe/Italy/Lazio/Roma/Rome/_Texts/PLATOP%2A/Basilica_Aemilia.html)給主廳約90×27m，且仍稱15券；[Caen具名復原正文](https://rome.unicaen.fr/monument/basiliqueemilienne/)則說70×29m與16券。採PArCo對Augustan券數的明確敘述、Platner/Ashby的主廳概略尺寸；不同範圍／版本的70與90m不能平均成80m或宣稱互相一致。原trace的99×27m單廳並非上述90m內廳的實測。

本提案保留OSM1766532中心與theta55.74°，主廳改90×27m。原99m長遺址範圍作街面估配；SW側十五單元平均6.6m，深8m；再外留8m通廊，雙層16券前沿在local x=−30.1m。shop凹口朝SW，`through:false`只示入口深度；並未畫通入basilica的三條實際通道。主廳18m、側廊9m、店體7m及券廊15m以**早期Julia／同期商舖比較估值**保留，無Ulpia作早期直接證據。兩層樓板、完整走廊屋頂、非對稱第四廊與柱式未復原；能先審街面尺度，不能稱完整建築考古復原。

## AP06 Caesar Forum：原址及改形範圍

現有原生trace錨點 `[12.4849,41.89392]`、theta36°是已配準完整廣場的近似位置，非DAR110標籤；160×75m是既有帶估值外廓。新提案沿此控制，三邊低坡屋面的柱廊取代完整四邊實體圍框，NW端另置Venus，SW店面保留低量體。柱廊8m/10m、店面5m/7m、Venus30×46m/17m都為具名同址／早期Castor比較估值。

西南20個店面開口以132m÷6.6m的Aemilia店寬比較選值，**不是出土二十店清冊**。DAR說店室部分嵌入山坡；本提案只畫地表街面，沒有臆畫地下室。神廟八前柱為通用早期廟式代理，側柱未復原，不搬Trajan雕飾或Basilica Argentaria。[Mercati官方頁](https://www.mercatiditraiano.it/it/sede/area_archeologica/foro_di_cesare)已核讀46BCE首奉獻；該頁配圖明標Trajan時代，**未拿該圖當AD14立面圖**。北接合與Chalcidicum具體形態仍為未解項。

## AP07–AP12：已核讀、尚未轉成可落位完整幾何

|項目／來源|最大可用內容|仍缺，不能假裝完成|
|---|---|---|
|AP07 [Agrippa Pantheon／DAR Pantheum](https://www.digitalaugustanrome.org/records/pantheum/)|約27BCE；北向44×20m前廊基礎，南接21.25m寬突出體；La Rocca早期解讀採十前柱、圓形露天部分。DAR是綜述，本輪未讀Beltrami原發掘。|DAR的露天圓院說不能寫成定論；[La Rocca2015原出版社](https://www.cambridge.org/core/books/abs/pantheon/agrippas-pantheon-and-its-origin/093DC3CC4DC2E19B51D95CBFA0D3E7AC)僅可得摘要／書目，另有木屋頂復原線索但未取得可核完整原刊圖。沒有把Hadrian穹頂倒放。尚需北廊/圓院現代足跡控制與具名高度比較。|
|AP08 [Diribitorium／DAR](https://www.digitalaugustanrome.org/records/diribitorium/)|7BCE完成，Saepta之南，有Augustan南/北牆及FUR比對；西界與Saepta齊、東延較遠、NE稍斜；AD14應覆屋，AD80後屋頂不復。|100羅馬尺是梁跨，不能當屋高或全建築寬；未取得並量讀完整牆平面，不用DAR19標籤點作中心。|
|AP09 [Porticus Liviae／DAR](https://www.digitalaugustanrome.org/records/porticus-liviae/)|7BCE，Oppian北坡四面廊，階梯下接Clivus Suburanus；相對Via in Selci垂直的定位保存在現代街屋。|中央長方體可為泉/壇/廟，尚不能選一種當實證；FUR完整平面需要地理套合，沒有用標籤329作中心。|
|AP10 [Agrippa浴場／DAR](https://www.digitalaugustanrome.org/records/thermae-agrippa/)|25BCE始，19BCE供水、12BCE遺贈。南北向與非對稱早期配置可保留；北界及室內相位未定。|現存圓廳與後期圖不等於AD14全室外廓；尚缺原生新方案的同期具名浴場高度/平面比較，保留revise而非假造完整屋群。|
|AP11 [Apollo圖書館／DAR](https://www.digitalaugustanrome.org/records/bibliotheca-latina-graecaque/)|28/23BCE已用，AD12/13拉丁館接待記載；可為一大廳分區或兩空間。|東南雙apsidal halls屬Domitian讀法；早期外廓、高度、與Danaids廊接合未定，本輪不把兩個18×27m後期廳改名。|
|AP12 [Augustus Forum／官方emicicli](https://www.sovraintendenzaroma.it/content/gli-emicicli-1)|原四exedrae；靠西的南一座因Nerva廣場消失，靠西的北一座因Trajan廣場消失。官方年代為97及112–113。|DAR舊文/圖只示兩主要半圓，不能藉鏡像任意補另兩座。須可量新平面及Mars遺存控制；本輪未完成，保留revise。|

上表記第一輪缺口；以下AP13–18及 `ad14_public_delivery.md` 是本片收尾更新。兩份新形制YAML均只做schema檢查，尚未有來源逐形模型視覺驗收／原生clipcheck。

## AP13 Augustus Forum：可量官方平面、四exedrae與定位界線

[Sovraintendenza「La pianta del Foro」](https://www.sovraintendenzaroma.it/content/la-pianta-del-foro-1)的全尺寸圖保存為 `model_reference/ad14_public_augustus_official_plan.jpg`；同組[古今疊圖](https://www.sovraintendenzaroma.it/node/111824)保存為 `ad14_public_augustus_official_overlay.jpg`。圖上50m尺從pixel(428,489)到(583,489)，3.1px/m。官方正文取整數約120×120m、廣場70×50m及半圓直徑40m；**圖面西側小半圓明顯較小，且圖說明寫小半圓為假設**，因此本資料不硬把四座一律畫40m。

`ad14_public_controls.json` 保存比例尺、temple與各半圓採點、OSM node11933283813、舊已核−51°軸。用Temple平台估讀中心(500,113)對齊Mars遺存點；不是DAR標籤中心，也不是多點測地配準，容許約5m或更大位置誤差。主半圓圖讀理想化為沿軸45.16m、突出深18.39m；西小半圓34.84m、突出11.61m。這些是圖讀外廓的橢圓半體代理，不能稱出土精密半徑。

原生候選見 `ad14_public_additional_proposed.yaml`：兩長廊、Mars廟及四半圓；廊10m、半圓10m牆加3m屋頂、廟18m簷／6m基座沿同址具名復原估值。小間、北消防牆的凹凸、Aula del Colosso尚未成形，reservation沿來源保留其範圍。西小半圓中，南座因Nerva97消失，北座因Trajan112–113消失；兩主要東半圓保留。分期依[官方emicicli](https://www.sovraintendenzaroma.it/content/gli-emicicli-1)，形態的不確定性依圖說，兩者並存。

## AP14 Agrippa Pantheon：現代足跡只作同址控制

已保存[OSM relation3374342完整資料](https://api.openstreetmap.org/api/0.6/relation/3374342/full.json)為 `model_reference/ad14_public_pantheon_osm.json`。只取way251373410的圓體側邊點擬合圓，排除前廊和南附屋；原node ids、半徑29.118m、殘差與北廊兩角控制在controls內。這是現代外牆足跡，不是Augustan測繪；DAR記早期圓牆同曲率及44×20m北廊基礎，才支持用它作同址近似套合。theta183.538°使原生前面向北。

候選只選DAR引Tortorici的「圓院周邊低牆」分支；0.61m牆厚、1.65m存高來自DAR所述早期牆片。本形體**僅把1.65m作最低邊界代理，不能宣稱這是原始全高，也不能說AD14是廢墟**。不以未取得原刊的木屋頂說畫出整圓屋頂，也不放Hadrian混凝土穹頂。前廊10柱、44×20m及北伸7.75m有正文依據；其15m簷／13.5m柱與1.5m平台、21.25m寬連接體的8m深度是Apollo/Castor早期廟型比較估值。露天或覆頂學說、圓周上構仍需主代理選擇，故候選／預留區均標conditional，不能默認採用。

## AP15 Jupiter：Sullan／Augustan上部的有界代理

[DAR Iuppiter Optimus Maximus](https://www.digitalaugustanrome.org/records/iuppiter-optimus-maximus-capitolinus-aedes/)已核讀正文，記約62×53m、3.6m高基台，Sullan寺69BCE奉獻，Augustus修復於同基礎；常見復原有三內殿、深前廊三排六柱。現代不同解讀亦被該條目承認。原生候選改用52×61m殿身加各邊0.5m基台，沿原Caffarelli位置／SE正面；17.67m柱高取[Vitruvius4.7.2](https://lexundria.com/vitr/4.7/mg)Tuscan寬的1/3作**理想類型比較**，不是早期實測。19.8m簷、15°屋面仍估值。現有通用前柱廊只畫一排完整前柱及兩側深廊柱，未完整實現三排六柱／三內殿；候選應叫外量體代理。

## AP16 Aemilia：街前線核對，主廳與整體寬度分清

[Platner1904 fig.24](https://commons.wikimedia.org/wiki/File:Forum-Romanum-Platner.jpg)原圖掃描保存為 `model_reference/ad14_public_platner1904_forum.jpg`，Commons註明公版原作、Saikindi整理掃描。用圖上Curia／Julia／Castor／Vesta／Saturn五中心對到既有已配準trace，仿射控制殘差0.56–5.11m。這些控制點含示意量體中心，**不是五個測量釘**。源圖本身是1904混合遺存圖，不能當Augustan施工圖。

但其Forum側長邊轉入Aemilia原local frame，得到(-34.52,+51.87)至(-27.71,-48.71)m，與提案券廊中心x=−30.1m相合至數米。這支持SW街前線位置，不支持十五店等寬／深8m／走道8m已被測得。提案目前真佔用約44.8×99m（含主廳0.6m出檐）；最外街面比主廳SW牆外推17.2m。`extent`對原錨點對稱包絡為61.4m；先前帶deck時68.2m更不是實際寬度。Platner/Ashby的90×27m是**含中廳與側廊的主廳全寬**，native `w_m:27`亦含側廊，不再額外加兩側5m。採用仍由主代理審定，不能為對稱bbox硬留出空地。

## AP17–18 其餘早期平面與本輪停止點

Aemilia候選收尾時移除與店門凹口重疊的十五個實體`long_hall`，以原生`arches through:false`本身的8m深背體承載店列：總高7m，上實牆2.75m，門部4.25m。這避免整廳把凹口填滿；十五間只由門面分格表示，沒有聲稱已畫內室或通入basilica的三條走道。沒有動共享繪圖程式，也尚未看模型。

[AP17 DAR Atrium Vestae](https://www.digitalaugustanrome.org/records/atrium-vestae/)已核讀：西Scalae Graecae、北Sacra Via界牆、東Domus Publica，12BCE後納入後者；南界Via Nova／山坡仍不明。內部以Scott1993 fig.15為重建依據，後期施工大改原貌。未取得該圖，就不能把104×55m後期長院變成AD14代理。

[AP18 DAR Horrea Galbana](https://www.digitalaugustanrome.org/records/horrea-galbana/)已核讀：晚二世紀BCE倉儲，三院不全同，東院建物未知；Lanciani pl.40記零星出土，FUR24a/c部分依舊摹本。未量讀對應早期圖，不把三個同院圈直接當AD14。

本輪Campus z17原DAR瓦片、圖與3857 transform均保存。浴場和Diribitorium只交publisher原圖足跡的reservation：浴場約68×135m示意實塊，Diribitorium約137×46m略斜外廓；兩者都不是整塊同高建築的證據。未取得浴場早期房間分界／高度，Diribitorium100羅馬尺木梁又不等於整館短邊，因此不補無來源屋群。Porticus Liviae此次tile crop未包含院體，不拿錯crop當定位來源；具體缺口及Livia/Augustus宅接續見delivery表。依主代理指示，本片保存到此，不再擴新檢索。

# AD14／64年前：早期帝都配置研究

研究日期：2026-10-29。只供第4步的來源核對與地標小樣規劃；沒有改正式配置、FACTS、作者腳本、113年模型或共用程式。已重讀 AGENTS.md、SKILL.md 與 MODEL.md 全文，停用所有 Superpowers。

**先交 Casa di Livia 西側已見房群的小樣；暫不把兩宅補成一個完整帝宮，更不把113年刪去幾座大樓當成AD14。** 新時期地標樣張經導演看過後，才擴展整城。以下「已知」指來源支持的範圍；「估值」要寫進各物件 basis；「仍缺」不能藉現存遺址包圍矩形或晚期形態補成確定。

## 可直接採用的圖與本機資料

|資料|用途與限制|
|---|---|
|`model_reference/dar_forum_palatine_z17.tif`、同名 `_sources.json`|已配準的 Digital Augustan Rome 局部研究圖，適合核對約AD14的道路、地標與不確定畫法；不能把標籤點當建築中心。圖例分有據／假設街道、約略建成區、無資料區等，描圖時必須保留這些區別。|
|`model_reference/digital_augustan_rome_records.json`、`digital_augustan_rome_features.json`|文字條目及圖例；每條記錄的經緯度只代表定位標籤。DAR是考古研究復原，不是所有細節都實測的AD14地籍圖。|
|`model_reference/lanciani_core.tif`、`lanciani_imperial_fora.tif`、`lanciani_imperial_113.tif`及各自manifest|核對遺存、街道與地理關係。Lanciani混列多個年代，不能直接描出AD14整城。|
|`imperial_completion_layout.geojson`、`imperial_113_placements.yaml`、`imperial_completion_sources.md`|已確認113年版本的對照基準。早期可沿用經核實的錨點及某些估值量體；其中 `period`／`period_ce` 可能是113形態或一次修復的時點，不能當成該場所首次出現日期。|
|[PArCo／Coarelli：Casa di Livia 帶尺平面](https://colosseo.it/sito/wp-content/uploads/2020/11/CASAdiLIVIA_COARELLI_GUIDA.jpg)|已實看；970×1294像素，有北箭與0–5m尺。可供第一件小樣逐牆描繪，僅涵蓋西側已見房群，不是整座兩院宅第。|
|[PArCo：Palatium住宅路線](https://colosseo.it/percorsi/palatium-abitare-sul-palatino-dalla-fondazione-di-roma-all-eta-moderna/)|前項平面的官方發布脈絡；同時說明早期Palatine由多處宅第組成，不能把後世宮城空間整片畫成早期園林。|

這些圖只作研究與模型核對；沒有把參考圖當成已取得上屏授權的影片素材。

## 第一件小樣：Casa di Livia 西側房群

### 平面、位置與尺度

以PArCo帶尺圖為幾何依據。A為入口／通道、B為中央大空間，C在其後方中間、D／E分列兩側，F在圖面右側。圖上的北箭指向左下；**先按圖本身的局部座標做原生landmark，在平地以 `modelview --sheet` 看形體，不必先硬塞進OSM矩形。**

5m尺約213像素，僅供檢查描圖是否失去比例。依此粗讀，西側房群整體約21×24m，B約12×8.5m；這是本輪讀圖估值，沒有取代逐牆描繪。房群並非矩形，亦不能把B的兩個方痕直接補成四柱中庭。

本機OSM relation1860919的整組現存 Casa di Livia 外廓，計算面積約824m²，最小包圍矩形約39.75×23.24m，長邊方向以東為0°約136.66°（反向−43.34°），幾何中心約 `[12.485724,41.889212]`。這些數字只診斷現代映射範圍；**它包括比帶尺圖西側房群更大的範圍，不是完整AD14屋頂平面。** 不把包圍矩形作一棟長廳，也不以它拉伸官方平面。

DAR標籤約 `[12.485770,41.889109]`，可核對「在Augustus住宅北側、隔一條窄巷」的關係，不作西側小樣中心。整城定位仍需把來源平面的已見牆角與現地遺存逐點對照；本輪沒有假稱已完成這項配準。[DAR：Domus Livia](https://www.digitalaugustanrome.org/records/domus-livia/)

### B究竟是什麼；C／D／E／F能不能命名

|平面部位|可用稱呼|確定程度與建模後果|
|---|---|---|
|B|PArCo稱 quadrangular atrium。|不能由「atrium」一詞推出全露天、四柱式或確定compluvium。已讀官方正文沒有給B的屋頂剖面或開口尺寸。小樣如加屋頂／開口，必須另列為同期類比估值。|
|C；D／E；F|按PArCo文字對照圖面，可分別標「傳稱tablinum」「傳稱alae」「傳稱triclinium」。|這是傳統功能解讀，不是房間用途的考古定論；模型及字幕不應把每室功能寫死。|
|A|現存出入走廊／坡道系統。|不把今天參觀入口自動當成AD14唯一正門。|
|圖外的東院與服務房|DAR描述較高的東側院落及相連服務區。|尚缺與本圖一致、可量全外廓的圖，不納入第一件樣張。|

[PArCo官方介紹](https://colosseo.it/mirabilia/la-casa-di-livia/)採上述房名；[DAR](https://www.digitalaugustanrome.org/records/domus-livia/)所採文獻卻把西側中央房稱餐室、另側房稱tablinum，且明說功能缺考古證實。兩種說法不強行合併。[TESS5023](https://tess.beniculturali.unipd.it/web/scheda/?recid=5023)另記一說：真正主中庭／入口在東南，西側應屬宅第後部。因此B屋頂與功能暫列「仍缺」，不能以一個房名反證復原形式。

### 層數與高度

TESS把複合宅第記為兩層，下層接待、上層寢室；DAR把Augustan增層放在較高東院周圍，甚至保留可能第三層的舊說。**這不證明帶尺圖西側四房上方整片都有第二層。** 最小樣張只做西側已見層，上層與東院先不補。[TESS：上層cubicolo8](https://tess.beniculturali.unipd.it/web/scheda/?recid=5054)、[DAR](https://www.digitalaugustanrome.org/records/domus-livia/)

可具名的實測高度類比為：發掘者Carettoni在1961年的原始報告，印刷p.191（PDF第3頁）記鄰近Casa di Augusto「面具室」平面5.12×3.45m、室高3.10m。這可作Livia小房的**同山、同期室內高度類比估值**，不能改寫成Livia實測簷高，也不能把大得多的B一律壓成3.10m；屋架、牆厚、屋脊及不同房間的實際高度仍需分開。[Carettoni，〈Due nuovi ambienti dipinti sul Palatino〉，Bollettino d’Arte1961](https://bollettinodarte.cultura.gov.it/wp-content/uploads/Importer/1483435286830_04_-_Carettoni_189.pdf)

同文p.189松果花環室的2.45m是彩繪上界，不是整室高度；不要拿來壓低外牆。另一可明名的同期比例依據是Vitruvius6.3：中庭梁下高為寬的3/4，屋頂開口寬為中庭寬的1/4–1/3。這是理想設計規則，只能作假設方案；不是證明Livia的B必為該種中庭，也不能把B整塊挖成露天庭園。[Vitruvius6.3，Morgan譯](https://lexundria.com/vitr/6.3/mg)

TESS的41.11m海拔是古地坪記載，不能直接當現代DEM之上的絕對模型z；其3.80×3.10m是某項地坪／房間資料，也不是整宅尺寸。

### 小樣應交什麼

先交西側已見房群的原生landmark樣張：俯視能逐牆對照，低角度能看房群高低及屋頂。實證平面與屋頂／高度估值在basis分列；B不種樹，不冒稱四柱；不補無圖東院或整片第二層。這是一座特殊宅第地標，不必為它新增一種全城通用房型。若後續找到可作通用house type的新形式，仍先交該房型樣張，不能直接鋪全城。

## Casa di Augusto：兩台地可採什麼，還缺什麼

|項目|已知|估值／仍缺|
|---|---|---|
|地理關係|在Livia南側，介於Scalae Caci與Apollo區；不是Flavian Domus Augustana。|DAR標籤約 `[12.485272,41.888851]` 只供尋址；本機未找到名為Casa di Augusto的可靠完整OSM建築外廓。relation1805347是晚期Domus Augustana，不能拿來用。|
|兩台地|DAR據考古文獻記人工上下台地，差7–9m；下台地圍柱庭的東北／東南側較有遺存，上台地僅小中庭等部分。|7–9m是兩個古地坪的相對高差，不是兩層樓高，更不是整片現代DEM再加8m。尚缺可與本機地形核對的完整分期剖面及台地邊線。|
|樓層|下圍柱庭一側有保存的上層小室，傳稱studiolo；亦有通往Apollo區的坡道。|可證明局部上層，不能推出全宅兩層。兩層外立面與Danaid配置另有學說，不作唯一確定復原。|
|面積|條目區分約350m²住宅部分與逾12,000m²綜合區。|兩者範圍不同，不能開平方變成屋身寬深，也不能拿113年85×100m上院套上。|
|園地|有圍柱庭、通道與宗教公共區；整座Palatine原有多處共和宅第。|未找到能把周遭全部指定成Augustus私園的AD14產界；不套Flavian Vigna台基，不把刪宮殿後的洞全種樹。|

以上採[DAR：Domus Augustus](https://www.digitalaugustanrome.org/records/domus-augustus/)的常見研究解讀；該圖以實線表示發掘較確定部分，銀色區亦包含估計範圍。約AD14使用狀態仍須逐相位核對，不能把所有更早／未完工牆線一律放在AD14地面上。

[PArCo Augustus介紹](https://colosseo.it/mirabilia/la-casa-di-augusto/)可核公共／私人區、坡道與studiolo的分區。其[2019清潔標案7B圖](https://colosseo.it/sito/wp-content/uploads/2019/01/7B-1.pdf)可定位今天參觀房間，但圖面含現代木道、玻璃等，正文73m²等是清潔工作量，不是古宅總面積；本輪不把它當帶尺完整復原圖。第一件樣張不為湊成一對而假造Augustus外廓；補齊可量分期平面後再做第二件。

## 尚未興建的113年地標，其所在地不能留成空洞

|晚期場所|早期有據內容|可落實的AD14／64年前做法與缺口|
|---|---|---|
|Trajan浴場／Oppian丘|官方發掘說明：109年浴場平台埋覆早期建築；早期部分建築軸向近南北，與Trajan斜軸不同。Domus Aurea屬64年火災以後。|不能拿334×315m浴場外框當早期街廓。先依DAR有據街道、宅第及園地建骨架；有圖個案沿原平面，無圖部分依同時代復原／習俗補，標示意。官方把下層「Città Dipinta」及「Musa／Filosofo」建築定於AD1世紀後半，不能倒放AD14；64前後的更精確分期仍缺。[官方廊道考古](https://www.sovraintendenzaroma.it/i_luoghi/roma_antica/monumenti/terme_di_traiano/galleria_sudoccidentale)、[官方古建軸向](https://www.sovraintendenzaroma.it/content/colle-oppio-terme-di-traiano-1)|
|Colosseum谷地|DAR記arena下西北角有兩層凝灰岩構成的早期水池基礎，功能不明。東側Ludus所在地另有晚共和／Augustan圍柱庭宅及64年火毀房屋。|住宅／街道可依有據局部另鋪，不是照晚期橢圓場地圍一圈房。不能把未知池放大成Nero人工湖；後者屬火災後。谷地中央的完整早期配置仍缺，須標示意。[谷地池基](https://www.digitalaugustanrome.org/records/vallis-colosseum-building/)、[Oppius宅1](https://www.digitalaugustanrome.org/records/domus-oppius-mons-1/)、[宅2](https://www.digitalaugustanrome.org/records/domus-oppius-mons-2/)|
|Trajan廣場／市場|官方明說開鑿Quirinal與Capitoline間山脊／坡地，可能Domitian已動工；112／113的平地並非先在那裡等建築。|AD14不留已平整的大廣場凹口。早期坡地、既有Caesar／Augustus廣場、連接街道依DAR；缺圖建成區作示意。古山脊高度仍缺剖面，不依現代DEM假稱已復原，不自造一座確切高度土丘。[Mercati官方](https://www.mercatiditraiano.it/it/infopage/foro-di-traiano)|
|Domitian stadium／Navona|Augustan Campus已有公共建築、水景、林地與開放空間；Agrippa林地北／西界不明，前Domitian基礎與林界關係只是推論。|不能整片都補住宅，也不能一律草地；按DAR的建成／開放／園地區別。stadium本身不出現，275×106m晚期外框不能當早期產界；沒有依據把Caesar臨時賽場精確套在同一位置。[DAR：Agrippa林地](https://www.digitalaugustanrome.org/records/nemus-agrippa/)、[Campus](https://www.digitalaugustanrome.org/records/campus-martius/)|
|Castra Praetoria|Soprintendenza記建營20–23年；Tacitus記此前各隊分散城內。官方亦說營地缺系統全面發掘。|AD14沒有整個營區；尚不能把營區前址完整指定成墓地、菜地或住宅。先核DAR與早期道路／城市邊界，仍無資料的局部明列示意，不以後來營牆裁成早期矩形空地。113配置的25年不是來源的精確建營日。[官方Caput Mundi](https://soprintendenzaspecialeroma.it/interventi-ss-abap-caput-mundi/)、[Tacitus Ann.4.1–2](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Annals/4A%2A.html)|

Oppian已知街道另見[DAR的Oppius街](https://www.digitalaugustanrome.org/records/oppius-mons-street/)：實證短段與推測連線必須分開；113年住宅生成的所有小巷不能統一改成AD14。

## 113公共量體逐項分流

「可沿用」均指**核對早期平面後的低細節估值版本**；不等於宣稱113模型所有層數、屋頂或外觀在AD14已完全相同。

|現有物件|AD14處理|來源及需在basis說清的界線|
|---|---|---|
|`basilica_iulia`、`castor_pollux`|可優先沿用早期公共量體。|Julia的Augustan外廓長期保持；Castor已有AD6分期基礎。Julia重奉獻AD12有文獻討論，與「AD14已存在」是兩個問題，不因日期爭論整座刪去。[DAR Julia](https://www.digitalaugustanrome.org/records/basilica-iulia/)、既有S89／S92。|
|`curia_iulia`、`saturn_temple`、`augustus_forum`、`apollo_palatine`、`magna_mater_palatine`、`victoria_palatine`|既有早期位置可保留，分別核早期形態。|排除後世內裝、再用柱材等；立面估值留名。Magna Mater應用AD3火後形態。Apollo廟不能連帶證明現存旁側Domitian圖書館也可早用。|
|`marcellus_theatre`、`balbus_theatre`|可作Augustan量體估值版本。|兩劇場已於Augustan期存在；現有完整中心／軸可沿用，保留尺寸／立面本已標示的估值，不把後世復原細節說成AD14實測。[DAR Marcellus](https://www.digitalaugustanrome.org/records/theatrum-marcelli/)、[Balbus](https://www.digitalaugustanrome.org/records/theatrum-balbus/)|
|`saepta_iulia`|可沿用大外廓、須早期命名。|原建26BC；80年後重建可能沿舊平面。現有81分期是修復形態，不是誕生。310×120m大外廓有來源；北廊／南端處理須核圖，不能默認四面一樣。[DAR Saepta](https://www.digitalaugustanrome.org/records/saepta-iulia/)|
|`pompey_theatre`、`pompey_portico`|劇場朝東及看台輪廓可沿用；舞台須早期版本。|Augustan舞台可用直線估配；FUR上中央矩形加兩側曲形凹殿是80年後Domitian形態。現有模型若只有直台，不必為版本名稱重做，但仍記早期立面估值。花園留用途，種植配置估值。[DAR Pompey](https://www.digitalaugustanrome.org/records/theatrum-pompeium-pompeianum/)|
|`octavia_portico`、`crypta_balbi`|可作早期柱廊大外廓代理。|前者27–23BC時期已有；81是火後修復，不能讓AD14空缺。不複製現存Severan入口；Crypta須核原期與後增建，不把全院細部定死。[DAR Octavia](https://www.digitalaugustanrome.org/records/porticus-octaviae/)、[Balbus](https://www.digitalaugustanrome.org/records/theatrum-balbus/)|
|`augustus_mausoleum`、`aemilia_warehouses`、`fabricius_bridge`、`cestio_bridge`、`portunus_temple`、`hercules_temple`|可保留已核早期位置／基本類型。|Mausoleum不倒放更晚方尖碑；Cestius不套365年／近代橋體；大倉及廟宇仍保留既有造型估值。不得由這些物件推出附近每塊113宅界亦古已有之。|
|`horrea_galbana`|位置、晚共和倉儲用途可早用；三院的早期完整形態仍估值。|三個院落並不完全同形，東院建物未知。現有三個近同單元不能直接宣稱AD14實貌；先比DAR早期圖，必要時只保留有據外廓加示意倉房。[DAR Galbana](https://www.digitalaugustanrome.org/records/horrea-galbana/)|
|`horrea_agrippiana`|可用Agrippan倉庫版本，但層數／細部單獨估值。|矩形、多層有來源；本輪113採三層本已記官方兩／三層說不一，不能轉成AD14三層定論。早期沿用時保留這條限制。[DAR Agrippiana](https://www.digitalaugustanrome.org/records/horrea-agrippiana/)、`imperial_completion_sources.md`。|
|`agrippa_baths`|早期浴場存在，可用經核大外廓估配；現有房量高度要重核。|25BC初建、19BC供水、12BC遺贈；80後修復不等於初建。113模型房量以Trajan浴場作比較，這是較晚類比，若AD14沿用要明列回推限制，不能當早期房間實證。更穩妥採早期同類復原。平面細部仍缺。[DAR Agrippa](https://www.digitalaugustanrome.org/records/thermae-agrippa/)|
|`basilica_aemilia`|不能因22年修復日期讓AD14消失；可保留基本矩形，但需補早期街面。|Augustan已修復；Forum側原有兩層券廊與商舖。現有普通長廳沒有這些，不能宣稱已完整對照早期圖。[DAR Basilica Paulli](https://www.digitalaugustanrome.org/records/basilica-paulli/)|
|`jupiter_capitolinus`|地基位置可保留，AD14立面另標Sullan／Augustan估值。|相同地基不等於Domitian82年上部完全相同；大前廊、三內殿等須按早期圖核。未知立面不得靠把82改成負數解決。[DAR Jupiter](https://www.digitalaugustanrome.org/records/iuppiter-optimus-maximus-capitolinus-aedes/)|
|`vesta_temple`、`atrium_vestae`|圓廟可有早期代理；Vestal住宅必須另做早期平面。|圓廟Augustan基台與後期上部要分開；現有104×55m長院不能直接倒放。早期住宅據Scott復原、南界尚不清楚。[DAR Vesta](https://www.digitalaugustanrome.org/records/vesta-aedes/)、[Atrium](https://www.digitalaugustanrome.org/records/atrium-vestae/)|
|`caesar_forum`|AD14已存在，必須有早期版本，不能只從113開始亮。|保留位置與西北Venus端；按Augustan圖核三面柱廊／店房、北側接合仍估值。113修復神廟不能冒作早期立面。[DAR Forum Iulium](https://www.digitalaugustanrome.org/records/forum-iulium/)|
|`circus_maximus`|**必做早期變體**。|谷地長軸／場址可保留；600×140m、20m整圈現有量體是Trajan103版本，不能無說明搬到AD14。先找Julio-Claudian復原及座席分區；沒有早期高度就標仍缺，不任意減幾層。Augustus首座方尖碑可有，357年第二座不能提前。[Roma考古官方](https://www.sovraintendenzaroma.it/content/circo-massimo-2)、[官方現場解說PDF](https://sovraintendenzaroma.it/sites/default/files/storage/original/application/05a248591eeb54f5e4b3e2884d818696.pdf)|
|`apollo_library_halls`|**不能沿用現有雙apsidal halls作確定AD14版本**。|28BC／23BC已出現，AD12／13有拉丁館接待記載；一大廳分區或兩個空間尚有爭議。FUR20b雙凹殿是Domitian形態。早期樣張可選一說並明列，但無早期尺寸時不能把113兩廳尺寸改名了事。[DAR Bibliotheca](https://www.digitalaugustanrome.org/records/bibliotheca-latina-graecaque/)|
|`domus_flavia`、`domus_augustana_upper/lower`、`palatine_stadium`、`augustana_circus_loggia`、`area_palatina_paving_01`、`domitian_forum_entrance`|AD14排除，原地改用早期有據配置。|現有宮廷及前庭形態屬Flavian；不能只縮小或改時標。Augustus／Livia是不同來源與位置的宅群。|
|`domus_tiberiana`、`vigna_barberini_flavian`、`paedagogium_palatine`|AD14不能用目前113版本。|Tiberiana有早於81的階段，但現有大院是晚期代理；另查建築相位。Vigna台基、服務院現形不能補成Augustus園地。|
|`colosseum`、`basilica_ulpia`、`trajan_column`、`trajan_markets`、`trajan_forum_porticoes`、`trajan_baths`、`domitian_stadium`、`nerva_forum`、`peace_temple`、`vespasian_temple`、`titus_arch`、`ludus_magnus`、`castra_barrack_*`|AD14排除；晚期按事件加入。|排除物件後，按前一節查原地用途，不能留下發光底板空洞。Caesar Forum不在這份排除表裡。|
|`nero_baths`|AD14排除；64年前夕可出現Neronian版。|113估配含227年Severan重建比較的限制；不能無說明把113所有對稱房量直接提前到64。|
|`regola_domitian_warehouses`、`emporium_vaults_east/south`|不能因為「都是倉庫」整組提前。|Regola已明列Domitian；Emporium局部需逐片查初建／重建相位。只把能證明的共和倉區帶入，缺者先保留研究缺口。|
|`forum_civic_paving_01`及園林|可保留早期的場所用途；重核範圍／分期。|不要倒放Flavian紀念物周圍的鋪地切口、113示意院界或晚期園亭。樹群形狀仍從相應時期圖、道路與地形定。|

現有113版沒有把Hadrian萬神殿倒放，這個優點應保留；AD14卻不能因此完全漏掉Agrippa Pantheon。DAR的早期復原是北向前廊接露天圓形部分，尚有分歧；需要獨立早期地標樣張，不能用現今大穹頂。[DAR Pantheum](https://www.digitalaugustanrome.org/records/pantheum/)

早期圖還有不能靠113刪除法得到的個案，擴城時要另列候選；本輪不為此改已通過113版：

|早期候選|可用證據與限制|
|---|---|
|Diribitorium|7BC完成，Saepta南側有Augustan牆基可與FUR核對；80年火後屋頂未恢復。因此AD14應有屋頂的大廳，與113露天狀態相反。梁長100羅馬尺不能當整體屋高；外廓從有據平面描，東北角不是方正矩形。[DAR Diribitorium](https://www.digitalaugustanrome.org/records/diribitorium/)|
|Porticus Liviae|7BC公共四面柱廊，在Oppian北坡、由階梯通Suburanus，周圍商店與住宅。可作早期Oppian公共錨點；中央長方形是泉池、祭壇還是廟仍有爭議，不能直接選一種當發掘事實。[DAR Porticus Liviae](https://www.digitalaugustanrome.org/records/porticus-liviae/)|
|Statilius Taurus圓形競技場|29BC存在，64年燒毀；原址有數說，DAR只放索引號，沒有確定外廓。這說明AD14也有圓形競技場，卻不能把Colosseum縮小移過去便冒稱考古形態；若選一說作示意地標，位置、尺寸、外觀須各列估值並先交樣張。[DAR Taurus](https://www.digitalaugustanrome.org/records/amphitheatrum-statilius-taurus/)|

## 14 → 64 → 80 → 92 → 112 → 113：來源時點

|時點|城市狀態與應用|來源|
|---|---|---|
|AD14|以DAR的Augustan全城為研究起點；已有Caesar／Augustus廣場、Julia、Castor、三劇場、Agrippa公共區、早期Circus及多處宅第。Augustus死後宅第逐步停用／被後建改動，不把它凍結到113。|DAR各場所條目，尤其Domus Augustus。|
|20–23|Castra Praetoria集中營成立。不是25年首次出現；不必為已有配置取整而改史實。|Soprintendenza Caput Mundi；Tacitus Ann.4.1–2。|
|64−／64火災／64+|必分火災前住宅城、受災過程、火後再規劃。Domus Aurea／人工湖是火後工程，不能在火起當天已是完整建成狀態。跨過64後，不保留被確知燒毀的Oppius房屋為同一完整建物。|[PArCo Domus Aurea](https://colosseo.it/en/area/domus-aurea/)、DAR Oppius住宅個案。|
|75|Peace公共區屬Flavian；出現在80版本可以，AD14不可。|既有113來源S98；需按該公共區自身分期入場。|
|80|Colosseum啟用，Titus浴場亦有；同年Campus火災與火後重建須分開。如果鏡頭是開幕典禮，不能同時把後來Domitian完成的修復都預先亮出。|[PArCo Colosseum](https://colosseo.it/area/colosseo/)、[Roma官方Titus浴場](https://www.turismoroma.it/en/places/baths-titus)、DAR Pompey／Saepta火災記錄。|
|81–92（86；92）|Domitian時期公共修復、86年stadium、92年Palatine新宮。宮殿不能出現在80開幕背景。Apollo圖書館現有雙凹殿可於Domitian重建版本使用，但精確落成年不明，不能假造為92年同日完工。|[PArCo官方2019說明，宮殿92年啟用](https://colosseo.it/sito/wp-content/uploads/2019/06/CS-13-giugno-2019.pdf)、[Roma官方stadium資料附圖](https://www.comune.roma.it/web-resources/cms/documents/Allegato_A_Capitolato_tecnico_con_planimetrie.pdf)、DAR Bibliotheca。|
|97；103；109|Nerva Forum、Trajan重修Circus、Trajan浴場分別進入；不能全推到113同時發生。|既有S98；[Circus官方解說PDF](https://sovraintendenzaroma.it/sites/default/files/storage/original/application/05a248591eeb54f5e4b3e2884d818696.pdf)；Roma浴場考古頁。|
|112|Trajan廣場啟用：廣場、Ulpia及相關建築可出現；column尚未啟用，模型應按實際鏡頭時點處理。|[Mercati di Traiano官方](https://www.mercatiditraiano.it/it/infopage/foro-di-traiano)|
|113|Trajan柱與重建Venus Genetrix神廟啟用；銜接已確認113整城。不是Caesar Forum誕生日。|同上。|

「某年已有」與「這套精確形態於某年完成」分開記。沒有確切完工日的建築保留朝代／區間依據，不由既有 `period` 數值倒推史實。

## 最小可落實方案與擴城門檻

1. **先做Livia西側房群的原生landmark小樣。** 有帶尺平面、可辨牆線與房群關係；高度借同山面具室，屋頂／開口是明列估值。交俯視、低角度，導演看過再擴。Augustus兩台地暫留研究，不用Flavian院台湊第二件。
2. 小樣通過後，以DAR早期地圖重建AD14的道路與用地骨架；沿用已核的早期地標錨點，每座按上表選版本。Caesar Forum、早期Circus、Apollo圖書館／Pantheon等新或改形地標，依MODEL先看樣張，不在整城擴展裡默默定型。
3. 住宅仍照「No empty cities」逐區走：考古平面 → 具名復原圖／模型 → 影視 → 同期習俗。113年通過的沿街、院樓、高低變化方法可繼承，**8868塊113宅地與其層數不能整批宣告AD14**。逐區查來源年代及火前／火後街網；可沿用的形體與回推估值各列basis。無早期定量證據，不杜撰一個新的精確房型百分比。
4. 大型晚期地標前址按上表補回有據早期空間。保留園、池、廣場就畫出用途；未知不等於園林，更不等於可以留裸底板。無完整產界時沿有據街道／地形做明列示意，不造幾何產界。
5. 再由獨立早期底圖向64−／64+、80、92、112、113正向替換：火毀房群消失、街網重排、公共區改建有對應來源。每個時期都要可獨立看成一座完整城市；113確認版保持作終點比較。

本輪仍缺的關鍵資料：Augustus可量且可分期的全平面／剖面、B屋頂與開口的直接證據、早期Circus座席上部、Augustan Apollo圖書館確定外廓、部分晚期大工程前址的AD14完整街廓。這些缺口已限定小樣與整城施工範圍，沒有用自造尺寸、住宅排滿或產界多邊形掩蓋。

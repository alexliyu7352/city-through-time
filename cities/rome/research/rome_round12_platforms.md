# Rome round12：殘留高平台的來源判斷

本件只讀11b及round12預編譯輸出，不編譯、不改候選、正式設定或共享程式。比較基線固定為`rome_round11b_all`。新24項已按整合者8.9分鐘預編譯輸出的實際ID逐項核對；舊round10的127項只作來源與先前失敗對照。

## Aemilia：先核位置、外廓與旋向

兩期實際設定已讀`rome_round11b_city_draft.yaml`及11b候選：

|node / ID|位置 lon,lat|旋向／外廓|實際建法|
|---|---|---|---|
|`republic_late_city/aemilia_warehouses`|12.47430,41.88054|43°；487×60m|`rome_round10_sites_aemilia_four_levels`；`site: parts`；`exaggeration: 1.0`|
|`another_centre/rome04_aemilia_warehouses`|同上|同上|同模板、`site: parts`；保留本期原exaggeration|

43°的語義已查`citygen.Builder.frame`與`landmark_site`，並直接呼叫原生API驗算：它是**從UTM東向逆時針**，不是從北順時針的heading。因此local +x是東北，487m長邊是NE–SW；local +y是西北，正是河側。不是把長寬調轉或把桶拱的橫向誤當長軸。

原生`landmarks.bounds`為`(-243.5,-30,243.5,30)`。不含6m街屋避讓的實際外廓四角如下：

|local位置|longitude|latitude|
|---|---:|---:|
|SW、陸側 (−243.5,−30)|12.47246883|41.87880652|
|NE、陸側 (+243.5,−30)|12.47663952|41.88188944|
|NE、河側 (+243.5,+30)|12.47613127|41.88227346|
|SW、河側 (−243.5,+30)|12.47196058|41.87919051|

已實看`本機候選/rome_round10_sites_probe/five_sites_plan_dem.jpg`首列的註冊Lanciani疊圖。原生紅外框沿倉庫長邊、短端與圖示倉廓吻合；其地理配準取既存`model_reference/lanciani_imperial_113.tif`與館藏KML LatLonBox，非本輪手工換算。官方與考古來源也將古建築置於Via Franklin—Via Marmorata之間、Via Vespucci—Via Branca一帶，並支持NE–SW長軸。沒有足夠證據把中心平移、縮成今日殘片或旋轉90°。

[市府官方頁](https://www.sovraintendenzaroma.it/i_luoghi/roma_antica/monumenti/porticus_aemilia)給487×60m、50橫向廳、七縱列兩兩向河遞降；[市府旅遊頁](https://www.turismoroma.it/en/places/porticus-aemilia)的POINT(12.473610364147275,41.88023395048192)是Via Rubattino 34地址。本輪轉入同一原生local frame得到(−64.61,+16.09)m，**位於完整模型內部**，不能拿地址點替換古倉中心。[Stanford Forma Urbis原研究](https://formaurbis.stanford.edu/fragment_23.html)亦記Franklin—Marmorata及Branca—Vespucci的現場界線；其90m深與市府60m不同，本輪保留已批准的官方60m分支，不混成一個新尺寸。

Monte Testaccio參考點12.4759,41.8766轉為local約(−213.35,−404.59)m，距實際外廓約374.59m。**這個487m矩形不碰Testaccio堆積丘**。高差主要在NE／Marmorata端附近，不能以搬離Testaccio為由移址。

### Aemilia的真實剩餘限制

模板已有四片487×15m、0.15m厚floor，local y中心依序+22.5、+7.5、−7.5、−22.5m，各片`site: raised`；每片50個9.74×15m的vault用`atop: 0/1/2/3`共用地坪。四個等深帶與薄floor是明列的示意值。[DAR原研究](https://www.digitalaugustanrome.org/records/porticus-aemilia-emporium/)支持四級朝河下降，但沒有四級精確邊界、各階差或古絕對datum；不能把15m帶深、當前平台或DEM測值稱考古測高。

對**只讀11b未整平地形**直接呼叫`terrainio.load`、`plate_mesh`及原生frame，得到下列數值（都未乘terrain×2）：

|取樣|SW端 x=−243.5|中心 x=0|NE端 x=+243.5|
|---|---:|---:|---:|
|長軸中心線plate relief，m|10.941|14.903|25.579|
|相同位置terrain_true16，m|9.564|14.483|27.073|

中心橫向陸側y=−30到河側y=+30，plate為16.468→13.337m，方向與向河遞降相符。舊round10矩形內網格量到16.94m高差；本輪包含精確邊界的150×20取樣為10.869–28.268m（17.40m）。差別是邊界取樣，不是改了模型或古址。經terrain×2後，34.7m級平台仍是現代plate落地代理。`terrain_true16`來自`terrain.json`記載的Copernicus **DSM** GLO-30（30m），也不能直接當純地面或古地坪；本輪沒有證據把NE端高值全部歸給Aventine自然坡、建物或填積中的任一項。

以`grade.pads`完全相同的12×12矩形內點取樣water.png，Aemilia有效28點、water share=0；不是河水≥10%的排除。**它被排除的確切類別是`site: parts`**。新grade在parent層直接跳過，不遞迴整平四片長floor。這是文件已明列的能力界線，不是本輪發現座標轉換錯誤。

原樣保留`site: parts`會繼續有上述限制。不能只換cut壓掉四級，也不能讓每條9.74m vault獨立取DEM而沿長軸階梯化。root進一步授權評估**共同整地＋明確標估的四級實體terrace**後，已有純設定可行解，見下節；因此不再將此件一概交給shared缺口。

### AEM-R12：可採用的純設定提案

資料在`rome_round12_platforms_aemilia_proposal.yaml`，只更新兩個既有ID：根`kind: parts`維持，`site`改`raised`；原四片floor的`h_m`依河→陸改0.15、1.15、2.15、3.15m，既有四組vault仍`atop: 0/1/2/3`。四片從共同基面向上形成實心terrace，沒有以`z_m`把薄板懸空。1m/級、總3m是**明確標註的外量體示意階差**，來源只證級數與方向，不證這個數字。15m帶深、原8m廳牆、50bay、長軸、中心、外廓、原兩期分期／高度誇張皆保留。

選`raised`是因有據的四級實體台地承托倉廳；不是用新增假幾何掩蓋今日樓。源於現代長軸DEM的34.7m底座由原生grade處理，來源四級則由模型自身表達，不用今日坡度推古地坪。無需改共享碼、另造城市地形或新增模板。

已用原生`landmarks.check`驗證有效鍵值；用`landmarks.build`在記憶體中的共同水平地坪驗證，四組各50廳的native底座分別為0.15、1.15、2.15、3.15m，`atop`確實保留四級共面，外廓仍`(-243.5,-30,243.5,30)`。只讀`grade.measure`對本倉單獨PAD（外廓+10m）量得40,474m²、level relief19.646m、cut/fill各8.8m、margin70.356m；大於1.5m門檻、小於15m深切提示。**這是單獨pad能力核對，不冒充全城合併pad後的編譯結果。** 最終整平後共面／平台米數及新舊畫面仍由整合者一次編譯、片中鏡頭核驗。

## 舊研究可直接重用的來源與決策界線

完整逐ID舊表保留在`rome_round10_sites_table.md`，原basis在`rome_round10_sites_inventory.json`；新清單以實際ID對應，不重跑舊作者腳本。

|來源組／地標類|來源與已支持建法|本輪使用界線|
|---|---|---|
|AEM：Aemilia兩期|上列官方／DAR／註冊圖；四級朝河下降|保留原四級parts，不把現代長軸坡度當古階梯|
|POD：具名神廟|`FACTS.md` S89/S98/S114及逐廟原basis；[DAR Jupiter](https://www.digitalaugustanrome.org/records/iuppiter-optimus-maximus-capitolinus-aedes/)、[Magna Mater](https://www.digitalaugustanrome.org/records/magna-mater-aedes/)、[Victoria](https://www.digitalaugustanrome.org/records/victoria-aedes-palatium/)|有據podium保留raised及模型中明畫基座；殘留30%以上本身不是改cut理由|
|OCT：Metelli／Octavia|[DAR Porticus Octaviae](https://www.digitalaugustanrome.org/records/porticus-octaviae/)記Metelli tufa foundations／podium|保留有據raised；當前平台數字不冒充古podium實高|
|TER：宮殿、浴場台地|`imperial_113_sources.md` S97、`imperial_completion_sources.md`；[PArCo Domus Tiberiana](https://colosseo.it/mosaico/domus-tiberiana/)；[市府Trajan地下廊](https://www.sovraintendenzaroma.it/i_luoghi/roma_antica/monumenti/terme_di_traiano/galleria_sudoccidentale)；[MiC Caracalla](https://soprintendenzaspecialeroma.it/luoghi/terme-di-caracalla/)|有據人工台地保留raised；Caracalla三道台地不等於當前一片platform已精測|
|VEN：Palatine Stadium|[PArCo原文](https://colosseo.it/mirabilia/stadio-palatino/)：161×48m、SW曲端、宮殿東側且約低10m、較可能庭園|原乾地earth／端部grass與古址保留。舊11b相對Flavia只低4.122m（terrain×2前），不能硬加−10m或以池造坑。新grade後須重測，不能照抄舊相對高程|
|CIV：Saepta、市場／廣場|[DAR Saepta](https://www.digitalaugustanrome.org/records/saepta-iulia/)、[Forum Iulium](https://www.digitalaugustanrome.org/records/forum-iulium/)、[Mercati官方](https://www.mercatiditraiano.it/it/infopage/gran-emiciclo)|公共水平庭院、切入山坡有據；若新grade已整平且實際不再吞牆，可將舊「因cut不安全保raised」重新選cut，保留神廟自身podium|
|VES／GRD：Vesta住宅／地上庫房院樓|`ad14_hill_completion_sources.md`；[PArCo Casa delle Vestali](https://colosseo.it/area/foro-romano/la-casa-delle-vestali/)、[DAR Horrea Agrippiana](https://www.digitalaugustanrome.org/records/horrea-agrippiana/)|來源支持地上院樓，沒有整片外露高台證據；古分層／房間樓層不等於可順現DEM拆水平梯田|
|PET：330／800舊聖彼得|[Fabbrica di San Pietro／Zander](https://www.basilicasanpietro.va/it/san-pietro/la-necropoli)：拆墓上部、填平並削坡|原site:cut符合切填建法；前院同理，不能回raised遮今日樓|
|BRI：橋、拱|`FACTS.md` S100及官方古橋冊|保留橋墩、橋台和拱，不添加矩形實心島台；`kind: arches`不整平屬合理類別|
|MOD：近代場館／附屋|逐件1937建築師、1960同期報告與原模板basis|保留有據足跡；cut是否安全按新地形驗證，不用加高或移樓躲檢查|

### Palatine：新合併pad的古層次限制

已讀round12**預編譯**`build/data/terrain.json`：`imperial_height/palatine_stadium`、`domus_flavia`、`domus_augustana_upper/lower`，以及`another_centre`對應版本，被列在同一93,518m² pad，height35.8m、cut/fill各8.6m；該pad共66件地標。來源仍是[PArCo Stadium正文](https://colosseo.it/mirabilia/stadio-palatino/)，它指定庭園約比Flavia-Augustana低10m。

因此新整地不能沿用round10「原分台有相對低位」的驗看結論；同pad會使各根地坪趨近同高，實際模型仍需讀圖。**主線已明確採取重疊pad同高、地形不求逐米復原，本輪保留這個整平契約，約10m深度列為未復原的精度界線，不新增shared需求、不阻擋交件。** 已將數值報root與整合者；只在片中實看退步至穿模、似水池或庭園消失時，再評估現有parts／terrace的最小有據修正。不能挪開古址來避pad相交、不能用假水池造坑，也不能僅因平台清單少了就報古地坪已正確。本件未改共享程式，也未修改鄰宮。

## 新24項實際清單

數值出自`本機候選/rome_round12_all/build/logs/round12_precompile.log:229`起各era行及`clipcheck.json`。米數是**screen**平台／本體，已含當期誇張，不能當古實測尺寸。每行均核現有native模板／實體、`grade.measure`與water mask；1960兩件另經原生`with_trace`解析。

「小切填」指原未整平地形中的本件PAD cut/fill不足1.5m，未啟動自己的整平；附近合格pad的bank仍會改變它腳下的坡度。這類殘留不是漏設`site: parts`。「已在pad」指已被terrain.json的合併pad收進去，仍有plate網格／邊界／基座代理的殘餘，不能假稱未整地。**保raised作代理**不等於來源證明有這麼高的古平台。

|#|node / ID|平台／本體；比例|grade類別|本輪決定與逐件理由／來源|
|---:|---|---|---|---|
|1|`republic_won_and_lost/rome02_early_whole_regia_late6c`|3.8／4.5m；83%|小切填，位於鄰pad的bank|**保raised作代理**。R17／[DAR Regia](https://www.digitalaugustanrome.org/records/regia/)支持梯形院與三房，不支持古3.8m高台；目前cut不再吞屋，但會將同一83%落差轉入牆基，未解腳下畫面，不為消清單改cut。|
|2|`republic_middle_city/rome02_mid_whole_emporium_early_portico_3`|6.5／5.8m；113%|小切填，鄰pad bank|**暫保raised作代理**。`rome02_mid_whole_plan.md` M4／[DAR Aemilia](https://www.digitalaugustanrome.org/records/porticus-aemilia-emporium/)的早期木構沿河廊是8×55m示意，非晚倉四級。單換cut仍是113%牆基；先讓新Aemilia整地進最終編譯觀察此鄰件，不發明早木廊的地下大台。|
|3|`republic_middle_city/rome02_mid_whole_emporium_early_portico_1`|3.7／5.8m；65%|小切填，鄰pad bank|**暫保raised作代理**。同上早期廊來源；cut只把65%平台轉牆基。保原長廊、位置與早期分期，不照晚倉改四級。|
|4|`republic_middle_city/rome02_mid_whole_tabernae_novae`|2.2／4.4m；50%|小切填，鄰pad bank|**保raised作代理**。R01 [Gerding／Dell’Unto原刊圖19b](https://publicera.kb.se/opuscula/article/download/61859/49745/156995)支持Fulvia南側獨立店列與通路，沒有高podium資料；新cut留下50%牆基，保原5m通路及低屋，不增高店屋。|
|5|`republic_middle_city/rome02_mid_whole_largo_c_early`|4.2／10.4m；41%|小切填|**保有據raised**。`rome02_mid_whole_plan.md`、[DAR Area Sacra Temple C](https://www.digitalaugustanrome.org/records/area-sacra-temple-c/)的早C廟tufa podium／Tuscan分支；基座是廟式的一部分，41%不是刪podium的理由。|
|6|`republic_middle_city/rome02_mid_whole_largo_a_early`|4.7／12.2m；39%|本件小切填但被鄰pad併入|**保有據raised**。[DAR Temple A](https://www.digitalaugustanrome.org/records/area-sacra-temple-a/)的早A廟250–225 BCE、四柱與約4m podium分支；不把44年後擴建廟倒入160 BCE。殘餘數字仍不是古台高測量。|
|7|`republic_middle_city/rome02_mid_whole_spes_early`|3.5／9.8m；36%|小切填；water4.3%，未達10%|**保有據raised**。`rome02_mid_whole_plan.md`／[DAR Spes](https://www.digitalaugustanrome.org/records/spes-aedes/)及同址共和廟式；保213火後早分支與podium，不倒用31 BCE以後重修。|
|8|`republic_middle_city/rome02_mid_whole_juno_sospita_194`|3.3／10.1m；32%|小切填|**保有據raised**。[DAR Juno Sospita](https://www.digitalaugustanrome.org/records/iuno-sospita-aedes/)及既有194 BCE早廟分支；32%是低高度誇張與落地代理，不應把廟改成地上無基座屋。|
|9|`republic_late_city/aemilia_warehouses`|34.7／13.0m；266%|`site: parts`|**採AEM-R12共同grade＋四實體級台提案**。完整外廓／旋向已核，上節詳列1m/級是示意階差；保50bay與古址。|
|10|`republic_late_city/domus_publica_republican`|5.3／6.8m；78%|小切填，鄰pad bank|**保raised作代理**。R17／HV的共和pontifical居所用途，不等於古高台；cut轉成78%牆基，保與Vesta分離的pre-12 BCE平面，不能任拆成順DEM樓翼。|
|11|`republic_late_city/regia_republican`|4.0／5.8m；69%|小切填，鄰pad bank|**保raised作代理**。R17／[DAR Regia](https://www.digitalaugustanrome.org/records/regia/)的36 BCE火前院房，不是後來Calvinus版；新cut只是69%牆基，不虛構有據分台。|
|12|`republic_late_city/largo_b`|6.0／10.0m；60%|小切填|**保有據raised**。[DAR Fortuna Huiusce Diei](https://www.digitalaugustanrome.org/records/fortuna-huiusce-diei-aedes/)早圓廟分支，廟的承台保留；不因比例改cut或換更晚pseudo-monopteros直徑。|
|13|`republic_late_city/atrium_vestae_republican`|4.3／8.4m；51%|已在合併pad（單件cut/fill3.3m）|**保raised作代理**。R17／HV支持早聖區住宅、無整片古高台測高；cut仍將51%落差放入牆基。保現有paved限定院地、35m三翼與早期界線，不冒稱後期104×55m長院。|
|14|`republic_late_city/largo_a`|5.6／13.4m；42%|本件小切填但被鄰pad併入|**保有據raised**。Largo原basis／DAR選較早2世紀六柱與podium；保12×19m示意分支，不用50–25 BCE最終擴建消平台。|
|15|`republic_late_city/largo_c`|4.8／14.4m；33%|小切填|**保有據raised**。Largo原basis／DAR的早tufa基座與四前柱代理，並以Portunus作已標明的共和上構比較；33%不是變更原廟式依據。|
|16|`republic_late_city/spes_holitorium`|3.9／12.5m；31%|**water10.3%**先被排除；本件亦小切填|**保有據raised**。[DAR Spes](https://www.digitalaugustanrome.org/records/spes-aedes/)及原source-map估址、2.5m podium比較；古廟不應在河上，這個10.3%是現代water mask與近岸小矩形的近閾值交集，不能把廟挪離古址來啟動grade，也不為31%清單改無台廟。|
|17|`imperial_height/atrium_vestae_early`|6.2／19.0m；33%|已在合併pad（單件cut/fill5.6m）|**保raised作代理**。`ad14_hill_completion_sources.md` HV1–HV3／DAR早聖區描線，原0.15m鋪地及3.6m房高估值保持；cut仍留下33%牆基，沒有新的有據古層高可拆。|
|18|`another_centre/rome04_aemilia_warehouses`|34.7／20.1m；172%|`site: parts`|**採AEM-R12同一四級提案**，保晚古原exaggeration／LA32分期，不說共和屋頂是4世紀實測。|
|19|`another_centre/rome04_lateran_old_cavalry`|5.3／7.0m；75%|小切填；不在新grade zone|**保raised作代理**。LA06／LA32支持312前騎兵營用途，兩個76×12m營房是批准比較，並非完整測繪；目前native cut仍有`terrain_cut 1`，最大穿入2.17m screen。不能吞低屋或移到教堂以外躲坡。|
|20|`another_centre/rome04_fabricius_bridge`|11.0／21.8m；50%|`kind: arches`；water39.3%|**改`site: cut`**，保原兩主拱與橋墩。S100官方古橋冊支持跨河橋，不支持橋外包矩形實心島台；與早期同橋已採cut的建法一致。目前native記憶體診斷terrain_cut0、本體高基礎ratio0。|
|21|`another_centre/rome04_domus_tiberiana`|11.9／24.7m；48%|已在合併pad（單件cut/fill4.3m）|**保有據raised**。S97／[PArCo Domus Tiberiana](https://colosseo.it/mosaico/domus-tiberiana/)的宮殿台地與下層承重有據；此14m環院翼代理不等於完整晚古逐室測高，不刪宮殿台地消比例。|
|22|`rome09_war1943/rome09_fascist_cipressi1937`|2.5／6.0m；41%|已在合併pad（單件cut/fill4.5m）|**保有據raised／retaining support**。`rome09_fascist_whole_basis.md` F01與原1937 Tevere側低看台修訂，只畫190×24m、6m估高東側承重台；不變成1953整碗看台。新2.5m支承量級可作原明列的坡地retaining代理，非1937datum實測。|
|23|`rome11_olympic1960/rome11_olympic_stores_MG_south`|2.3／3.1m；75%|已在合併pad（單件cut/fill2.1m）|**改`site: cut`**。O01同期官方報告PDF236 operating plan支持單層地上庫房，原3.1m是已明列估高，無整片外露podium依據。native記憶體診斷terrain_cut0、本體高基礎ratio0；保實際多邊形與1960分期。|
|24|`rome11_olympic1960/rome11_olympic_D1_compound_east_courts`|11.1／31.2m；36%|`site: parts`|**保parts**。O02同期D1 crocetta相連群／院與既核pilotis，為真實多樓群各自落地，與四片古倉floor有別。不可整群raised而封pilotis、不可改3.1m底層或移走東院。此11.1m是局部支承代理限制，不冒稱歷史地下台高。|

### 兩筆site校正與其餘保留的驗證界線

可套資料是`rome_round12_platforms_site_proposal.yaml`（只含late Fabricius與MG_south兩個ID的`site: cut`）。Aemilia另見自己的proposal；合計本輪建議4個原ID更新。沒有為讓整平啟動縮矩形或移古址。

## 最終編譯驗看

上述4個ID已採用；Aemilia兩期的共同整地與四級台地、Fabricius橋和MG_south庫房均不再列高平台。鄰近的中共和`emporium_early_portico_3`亦隨原生整地退出清單；`early_portico_1`仍為72%，保留上表已說明的落地代理限制。最後原生編譯列19項，逐項理由沿用上表，沒有宣稱這19項都是有據的古代台高。最終geocheck／clipcheck與改動區段camcheck均通過。

整地也令Caesar廣場與Trajan浴場原來由過高平台頂面代替的院地消失。本輪只在既有柱廊／浴場台地範圍補0.15m示意鋪地，避開Venus基座和階梯；厚度是顯示估值，不是古實測值，外框、古址及既有建築本體不變。

針對11個可能換cut的地上建築／橋，已用**目前round12 graded plate**、原生`grade.pads/blocks/zone`與`landmarks.build`在記憶體產生量體，按`tools/clipcheck.py`同一`terrain_cut`與牆基比例規則診斷，未寫模型、未編譯。除Lateran外10項不再觸發terrain_cut，但Regia、早廊、Tabernae、Publica與Vesta仍是原比例的高牆基，證明只換site未解腳下落差；所以不把這些也塞進可套patch。這項局部診斷不是全城clipcheck、不是片中圖片驗收；兩筆安全改法及Aemilia都仍由整合者完成最後一次原生compile／round和新舊鏡頭比較。

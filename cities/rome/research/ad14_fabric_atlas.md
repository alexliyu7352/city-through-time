# AD14 全城住宅與用地來源圖集

這是獨立早期底圖與用途框架，並非113年住宅刪除版。Velabrum已核准32棟／6街巷凍結；新框架先扣除該片與公共代理交付的早期留地。所有普通宅界和層數配置仍是同期習俗示意。沒有生成房屋、編譯或截模型。

## 可直接交給佈局的規約

`ad14_fabric_geography.geojson`以EPSG:4326存用途窗口、道路廊線及開放用地；properties的`id/kind/model/basis/status`與`source_ids/geometry_basis`可直接追索。用途窗口不是古代產界，更不能沿窗口外圈裁碎宅地。`street`是來源支持的命名廊道，仍須逐段區分描圖／示意；`lane`才是補全連接。未知區不能自動種園或留空。

類型採用次序：一／二層完整院宅和二層前鋪已審幾何可重用；三層候選以同期Vitruvius及具名pre79 Insula Orientalis II比較，另列回推限制，不靠Hadrianic Ostia或Severan FUR直接回推。四／五層不作本輪預設，也不是AD14高度上限。無史料支持的全城百分比或固定戶數不設定。

## 本輪已重新核讀的核心原文

|來源ID|來源與定位|原文短摘|直接後果與限制|
|---|---|---|---|
|D01|[DAR Continentia](https://www.digitalaugustanrome.org/records/continentia/)，都市外延、東北及缺圖末段|“large intramural areas … were free of dense urban development”|AD14非均勻外推；Quirinal/Viminal部分牆內亦非密建。DAR白區是缺資料，不能當空地。其built-up類別也不表示同一密度。|
|D02|[DAR Campus Martius](https://www.digitalaugustanrome.org/records/campus-martius/)，six distinct topographic areas與N Central Campus／末段|“Residential housing did not rank prominently here”|北中部保留公共原野；Via Flaminia東側主要Campus Agrippae公共園；南Campus Flaminius與Capitoline腳的建成區獨立處理。不得把113年Campus全區密住配置抄回。|
|D03|[DAR Nemus Agrippa](https://www.digitalaugustanrome.org/records/nemus-agrippa/)，第三段|“its borders to the N and W remain unknown”|Stagnum與Euripus之間林地有據，北／西界不詳；Navona前Domitian基址不等於完整早期園界。|
|D04|[DAR Palatium](https://www.digitalaugustanrome.org/records/palatium/)，住宅與末兩段|“the street system across the hilltop is also unknown”|北坡／西北宅群存在，早期皇室宅與宗教區相鄰；東南資料少，按同期宅群及院園補，不套Flavian平台、宮院或整片園地。|
|D05|[DAR Vicus Patricius](https://www.digitalaugustanrome.org/records/vicus-patricius/)，全文|“following the general course of Via Urbana”|谷地走廊有據；直通Porta Viminalis不是定論，末段不能照晚期Diocletian道路。|
|D06|[Ercolano 官方 LATRINE](https://ercolano.cultura.gov.it/cucinare-v-6_1-latrina-eng/?lang=en)，Palestra樓排污管段|“had three floors with kitchens and latrines”|Insula Orientalis II具名商住樓有三總層比較。封存前79，非AD14已證；商住長樓不是Ostia四翼院樓，不把其palaestra當住宅內院。|
|D07|[DAR Subura](https://www.digitalaugustanrome.org/records/subura/)，本機完整正文`digital_augustan_rome_subura.json`|“Populous and busy district”|Clivus Suburanus谷地、早期貴族宅與商住；引用的Martial/Juvenal屬較晚一世紀／二世紀，不當AD14具體地籍。|

## 逐區採用骨架

|區域|有據內容與14→113差異|可採形制／樓層及配置依據|補全界線|
|---|---|---|---|
|Velabrum／Boarium|S126/S127的商街、倉儲、密居；已核准小片原封保留|主街二層前鋪、深地一／二層院樓；沿商街／後院用途分配|外延宅界示意，32棟樣片不是比例|
|Capitoline西／北腳|D01/D02的Aemiliana建成區|二層前鋪、一／二層院樓；更密街面可另採三層具名比較|Ara Coeli是二世紀，不用其五層當AD14原址|
|Campus Flaminius|D02早期規整公共區／道路，不等於全Campus格網|公共區外街面二／三層商住、深地一／二層院樓|比例隨公共留地和街面而定，無全區配額|
|Regola／Campus西南|早期Via Tecta廊道、河港鄰接；Domitian倉房尚未存在|商街二層前鋪、一／二層工作院／住宅混合|San Paolo一世紀末倉儲不得直接回推；早期工作院是同城Horrea類比|
|Campus南中公共區|Pompey、Agrippa公建、水景、林地|只在來源建成街緣補服務商住；公共園／水／開場優先|不以沒有stadium／Nero浴場為由鋪滿住宅|
|Campus北中／Mausoleum|D02明述仍開放公共field與墓園|公共原野、路、墓旁步道；零一般住宅只是此用途區選擇|原野非密林；不畫矩形晚期Navona場界|
|Campus Agrippae／Flaminia|D02東側公共園、北側葬道|園邊／路邊稀疏服務前屋、低院；建成核心之外逐段收束|不可鋪成113的campus_east高密院樓|
|Subura／Argiletum|D07谷地與Forum入口；沒有Nerva／Peace／Trajan整塊留地|二層前鋪、三層商住候選及一／二層深院，按街面與後巷配置|三層pre79比較，不冒稱本地統計；新巷不直接複製Severan FUR|
|Carinae／Velia|DAR編目有共和／Augustan宅及早期街|一／二層院宅加二／三層商街；依坡腳和小街方向|沒有Maxentius；沒有把1930年代切坡當古地形|
|Oppian／Esquiline內側|早期住宅／街／Porticus Liviae；沒有Trajan浴場／Nero湖|一／二層院樓、二層前鋪；三層只在商街作具名比較|後來浴場外框不是早期街廓；北部街路另描|
|Quirinal／Viminal|D01非全丘密建；DAR宅點與谷／脊路|有據居住帶一／二層院宅與二／三層街面；北端過渡園地|宅點不當足跡；Castra20–23前址不留矩形空地|
|Caelian|DAR早期宅／Clivus Scauri；沒有Claudius神廟|一／二層院宅與二層前鋪；谷口可三層比較|不得拿晚期Celio insula作AD14平面|
|Aventine|DAR住宅／街／神廟；D01未因pomerium外就無人|一／二層院宅與二／三層商街|不能全丘富宅；FUR21d只較晚形態參考|
|Emporium|D01西南倉港外延；共和Porticus／Horrea錨點|一／二層工作院，路邊二層店住|Horrea Agrippiana多層可功能比較；不是24c於AD14原址|
|Transtiberim|D01較小城市外延；2BC Naumachia可容下的大場地|橋頭商住二／三層比較、內側一／二層院與河邊工作院|不要鏡射東岸密度；未知北部不一律空地，西南Naumachia由公建代理定位|
|Palatine|D04皇室多宅／北坡密豪宅，東南平面缺|一／二層完整院宅、獨立服務建物、院園；早期已知公建先扣|不原樣搬Flavian大院，不把Livia全宅兩層當實證|

外圍用途必須與建成帶共同生成：有據園地是園，公共原野是開場，田／墓／稀疏路邊聚落為來源約束示意；沒有全城單一硬邊。地形、台面範圍和倍率保持。

## 已落檔的施工規則與資料界線

- `ad14_fabric_districts.yaml`：16個配置區，每區有`placement_rules`，明分沿商街前屋、接主街的緊湊院、內側／園緣院。這些層數選擇是明列的構圖估配，不宣稱古代「深院必低」或「路邊必高」。一／二層不以交替、亂數或目標比例分配。
- 三層只先提案於`argiletum_pre_nerva`的0基索引1–3段與`vicus_patricius`0–2段臨街完整樓體；其餘商街預設二層。這是具名近時期比較下選擇一組展示多層商住的路段，不是出土層數分布。是否採用由主代理決定。
- `ad14_fabric_types_proposed.yaml`：5個已審幾何別名。三層的**高度**對照Herculaneum Insula Orientalis II，**獨立街屋平面／後院**則為羅馬同期習俗示意；不把Palestra變住宅中院、不按該建築租戶拆屋。W2為同城Horrea Agrippiana多層倉庫的功能／高度比較，兩層是官方兩／三層異說下的簡化選擇，並非AD14小倉庫普查。
- `ad14_fabric_geography.geojson`：用途與街路仍是提案，完整`source_pixels`見同名trace YAML。原始11面是首批交付，後增分類窗和道路另外核採。道路中心線不是路邊地籍，幅寬4.2–8m皆估值；與早期公建／已准樣區的接點須按原物件外形調整，公建優先，調整另記示意。來源不確定線並未升格為考古實證。

追加原文：

|ID|來源與定位|原文短摘|使用限制|
|---|---|---|---|
|D08|[DAR Oppius Mons: Street](https://www.digitalaugustanrome.org/records/oppius-mons-street/)，全文；[Oppius住宅1](https://www.digitalaugustanrome.org/records/domus-oppius-mons-1/)；[住宅2](https://www.digitalaugustanrome.org/records/domus-oppius-mons-2/)|街：“small section … dated … to the Republican period”；住宅2：“destroyed in the Neronian fire of A.D.64”|街的北續段推測，南向谷地有據；不可把完整線全標已發掘。兩住宅只標位置／遺存，不以點造全宅；64火毀不能保留為113同棟。|
|D09|[DAR Clivus Scauri](https://www.digitalaugustanrome.org/records/clivus-scauri/)，全文|“name is preserved only in post-classical sources”|通往Arcus Dolabellae的坡路存在；今天路線大致保留古路，小偏移仍可能。名稱及整段精度不當同期明證。|
|D10|[DAR Velabrum](https://www.digitalaugustanrome.org/records/velabrum/)，兩幹道與末段|“rows of shops and warehouse facilities”|商業／住居有據，兩街之間平面未知，南向Tuscus仍爭議。|
|D11|[DAR Aventinus: Street](https://www.digitalaugustanrome.org/records/aventinus-street/)，末段|“not directly attested … before the Aurelian Wall”|DAR由Cestius墓向及交通推早期中央凹地路；這是作者復原假說。不得把西側山頂示意巷命名成這條已發掘道路。|
|D12|[DAR Horrea Agrippiana](https://www.digitalaugustanrome.org/records/horrea-agrippiana/)，首段；FACTS S120所列官方異文|“rectangular, not trapezoidal”；“multi-storeyed”|同城共和末／Augustan倉庫提供多層比較；W2小工作院平面、精確層高仍習俗示意；晚期FUR42/5a辨識已遭否定。|
|D13|已存463筆DAR catalogue，`model_reference/ad14_fabric_catalogue_context.json`留篩選副本|欄位：“Extant remains of uncertain plan”|目錄有標籤點、類型、URL，`blocks`空、沒有description，不能聲稱全文或完整住宅平面。丘區存在／定位與道路受原配準圖約束；無圖內巷按同期習俗補。|
|D14|[Vitruvius2.8](https://lexundria.com/vitr/2.8/mg)，§17|“provided with floor after floor”|同期羅馬向上增加住宅，不能推平均層數、任一地區比例或固定五層。|

## 地圖登錄與剩餘缺口

DAR官方XYZ z15拼接為1792×1536，EPSG:3857，pixel4.7773142678投影米；羅馬緯度實地像素約3.56m。官方配準沿用，沒有自設控制點。42個索引格中36張可取，6張外側403，以白色缺圖表示並在manifest逐筆記錄；黑／白的圖幅外緣不是歷史開放用地。正文API403與本輪部分正文瀏覽空白已明確區別，不冒稱全部463篇已讀。

手描地圖的棕色／綠色本已是學術復原；即使外框逐像素保留，也不等於測繪精度。z15圖讀的細街／窄公共入口需與公建代理較詳來源核對，圖上約10–20m的局部差不可透過移動已准地標來消除。來源地圖只作研究；公開網站不代表圖可上屏。

仍缺：逐戶AD14地籍／層數、Palatine東南完整早期路網、北園產界、Castra前址逐塊用途、Colosseum谷地完整平面，以及各道路末端與公建原生包絡的精細對接。缺口按本文件與逐件basis作有界線的同期補全，不等待不存在的完整地籍。原生連通、房屋重疊、地形及畫面檢查是後續佈局／模型工作；本件只驗資料幾何與既有type幾何相等，未宣稱模型通過。

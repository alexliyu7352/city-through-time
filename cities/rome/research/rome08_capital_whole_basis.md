# 08首都城市：1866底圖／1870–1871接入準備

完整城市按C02原1866 Censo的連續建成區描，不複製Braschi窗口。C02每區各有源像素輪廓與舊街線，見`rome08_capital_whole_source.yaml`：CampoMarzio—Parione/Regola/Pigna—Monti連續東岸核心，Borgo、西岸Lungara和Trastevere均有獨立源域。七區每個lot的provenance帶各區依據；現代OSM只給仍存地標定位控制，未讀其道路充舊街圖。十九世紀後期Corso、Prati、Esquilino、Testaccio、VialeDelRe均未倒填。

C03的開Corso前地籍在唯一真實位置接回全圖；該窗口優先，廣域街與住宅不再穿過重複。C02有六個地理控制，用native register affine；最後殘差及留一誤差保存在registration.json。相對地籍較精的窗口，C02全城線是約3m/像素的概括圖讀，控制留一最大約21m，不聲稱宅界逐米。

房型僅用已批H01街屋與H02小palazzo。native parcels從不規則街廓切完整地塊，庭院類優先大可用位置、窄沿街類補小位置；14m正面、14–28m進深及17–37m院宅包絡是兩個具名比較的製作取值，不是本地逐棟測量。層數仍為來源比較的[3,3]，沒有無據隨機3–6層，也沒有把所有1871住屋都判成三層。各區比例是實際輸出、未當人口或歷史普查；圖上可辨院落支持保留courtyard形態，不宣稱生成器重建了同一內院。尚未重建個別街道商業開口、內部mezzanines與全城樓層分布。

具名公共量體重用07最後已存在並有來源的同城類型；C02再確認本期存在，包含完成的新聖彼得與柱廊、Vatican院群、Pantheon、Castel、Lateran、SantaMariaMaggiore、SantaMariaTrastevere、Capitoline、Farnese、Quirinale及Massimo。另接回已核07庫中的Titus、Severus、Constantine三座在世拱門，以及Aelius／Fabricius／Cestius的舊橋形制；這裡的Cestius不是1888後加寬新橋。它們不是把現代大灰塊當地標。Braschi與SanPantaleo另外用C03原廓。重用樣板本身的尺寸及簡化限制沿用原basis；本期不以重複升起暗示1871新造。

上輪遠景的田園亮面之間，確有已知開放地用途尚未覆完；本輪已補成沿C02城牆、河岸與舊城外緣的連續源域，而非仍以島狀田塊代表全部未建地。`whole_open_source.geojson`保留原圖讀，`whole_open.geojson`為扣除住宅域、native landmark_site及圖上另留的黑色建物群後的有效地面；沒有重排任何已批住宅。開放地面只描C02可見用途：Pincio、Ludovisi、Quirinale等園地用grass與示意疏林；葡萄園／菜圃及Caelian、Aventine/Testaccio等開放耕地用earth；Navona、聖彼得和SanPantaleo廣場用paved。CastroPretorio軍事空場、1866圖示鐵路開放進場及Caracalla考古地面用gravel，與農地區別；gravel是示意材質，並非當時鋪面材料的測量。形狀均按源圖道路／園牆／地勢彎折，不用規則多邊形充田園。普通住宅院巷留暗底。古蹟區按當時園圃／CampoVaccino留地，不復原帝都全貌。

城牆採C02十九世紀可見東南段的開放curtain pts，城在行進左側，8m高／3.5m厚是低細節估值；towers:false，不把圖讀轉折生造為規則新塔。PortaPia雙門按C06的1851後／1862–68版本，兩面及院深的18×32m包絡與14／16m高是由持續在世的現代定位輪廓作尺度比較的估值；裝飾未復原。門旁城牆以該仍存門作局部位置控制，ViaPia實接內門，不保留地圖概括線造成的短截。

C16補核[國防部2023官方敘事](https://www.difesa.it/primopiano/esercito-italiano-153-anniversario-della-breccia-di-porta-pia/30300.html)明述約30m缺口，原HTML／SHA保存在`portapia_defence30m*`。同一條原生wall pts沿原直線加入該30m範圍的兩端與中點，幾何線不變、不另切工地ID；native region loss只取當地生成段。原生研究at9秒事件只供驗證，正式須綁1870入城原句。不是整牆退出，也不是1849共和守住。後續河牆另採1900洪水前局部資產，不能把1866底圖叫1849實測，也不能把1871封為後期河牆已全線完成。

原生全城編譯先有6個空fabric：4個原窗口lot與2個大圖lot落入後加的具名公共用地／接圖道路；本輪接回Severus拱門的native site又令b017_02無法放入完整房屋（地塊588m²，與該site相交122m²）。只在整城active trace排除這7個，保留原生parcels輸出及核可窗口原trace；沒有縮屋撞宮殿。先前2棟當今凹形建物漏hide的最小案已由主線d4a8563／ab417e4修復；本輪依導演要求刪除兩塊convex hull city.hide補償，由新版原生取樣退讓。舊最小案及舊收據保留供追溯，不保留繞路補丁。

1849在已核故事是賈尼科洛戰事與共和失守；沒有證據支持全城拆掉換模型，本件不造一座相同1849城湊觀察年。1866是本城市幾何觀察年；1870–71沿用在世殼體，政治、用途與局部城牆變化分開。後續河牆資產必須帶自身建造年，正式接入由主代理按原稿排，不改旁白字幕。

Colosseum補件採同址原生06北半20段／40券跨、189×156m／48m高的比較形制，而不是完整帝國競技場。[C17：PArCo官方修復紀錄](https://colosseo.it/restauri/colosseo/)明載東端Stern1805–07、西端Valadier1822–27加固；[C18：米蘭市立攝影檔案VI B69](https://www.lombardiabeniculturali.it/fotografie/schede/IMM-3a130-0019174/)的1860–70原albumen內景已實看，支持殘破低內圈及未清挖的開放arena。以既有北半原生券廊位置與長度的0.86倍、南北鏡像成約163×134m、6m厚／26m高的兩層低券廊，作圖讀估值；它不表示完整座席或測繪殘邊；低廊也用native through arches，避免ring類別的矩形暗窗誤讀為本案的券洞。80券跨／3m上緣同為示意延續，沒有重寫曲面mesh。東端12×5m斜扶壁及西端逐低券廊也是示意尺度，來源只支持型態／年代。另實看[C19：國家目錄0800635803-427](https://catalogo.beniculturali.it/detail/PhotographicHeritage/0800635803-427)的1870後—1899照片作比較，沒有把寬年代相片精確定到1871。圖檔、HTML與SHA見`model_reference/rome08_capital/colosseum_sources_manifest.json`；C18公站憑證鏈失敗後公開圖片以curl --insecure取得，非自行生成圖。

未復原／不得誤當不存在：Diocletian–SantaMariaAngeli重用建物群、Lateran宮殿的精確1871立面、散在Caelian/Aventine及Gianicolo修院群、Caracalla殘牆、Forum／Palatine每座殘柱與殘垣、Montecitorio的Comotto臨時議場；Gianicolo／Vatican外圍城防量體尚未全復原。可辨建物群按C02留出，不塗田；Caracalla等只有考古地面用途，不以地面充作建築。已建主要公共量體清單不能視為全城古蹟逐件清冊。PortaPia本次只主張局部城牆破口與雙門量體存續，不聲稱1868立面細節精復。

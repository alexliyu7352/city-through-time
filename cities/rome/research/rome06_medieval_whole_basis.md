# 中世紀整城：800／1300／1377

本件只做獨立step4來源約束模型。已批Regola形體和已批住宅參數保留；其他普通地塊、樓層分配及非精測外包為製作估配，不是逐戶地籍、戶數或人口。觀察年和建造年分開；1377只保留有據晚中世紀城市及選擇存續／修復分支，不因教廷返回重放整城建造。

## 分期來源與採用

- M18：Robert Coates-Stephens1995博士原論文，UCL原PDF完整取得。https://discovery.ucl.ac.uk/id/eprint/10099990/1/10017236.pdf 。印刷184–201的住宅章及牆、屋頂／前院相關文字已核讀：早期住宅主要利用古宅和公共建物，不可預設800已集中Campus；Via Lata、Forum/Subura、Celio、Esquiline、Aventine、Trastevere及Vatican等有分散居住證據。其資料層級含較舊發掘解讀，不能將每筆都確定在800。一般二層低量體取SS.Apostoli保存下二層與Aemilia晚VIII／早IX兩室改建的比較；它不是850 Nerva宅，也不是800全城層數普查。3m／層、25°屋面、每個lot與屋體比例均為估值。
- M03：Meneghini2017原文284–288。800古主路延續、Velabrum較集中；晚期四座渡橋Aelius、Fabricius、Cestius、S.Maria及Via Pontificalis系列道路。路廊和5m左右路寬為概括連接，不宣稱完整朝聖實測路線。未把113巷道網或住房倒填。
- M17：Étienne Hubert1990，Persée原HTML的摘要、p90、p130已取得並核讀。其研究以文書說明XI世紀中至XII世紀中由分散核轉向結構化城市，宗教地產分割參與城市化；p90明言contra­dae仍有空宅地，不許整個歷史區一律飽和。沒有取得整本PDF，不稱讀完全書。https://www.persee.fr/doc/efr_0000-0000_1990_mon_135_1 。晚期核心選Campus河彎、南Campus—Regola、Velabrum、Trastevere及Borgo；邊線跟河彎、道路及地形的工作窗口是有界估配，沒有把Nolli當1300底圖。模型較外圍仍有居住核，沒有把山丘一鍵清空。
- M01／M04／M13約束1300／1377普通宅：窄街面、深宅、後院、二／三低層及偶有前廊。長連排以二層無廊為主要比較；短排可取二層廊、小窄獨立lot可取三層廊。這是明列的製作分配，來源不提供百分比；每區native parcels的實際棟數另在各report，不外推人口。已批Regola整塊先避讓再加入，寺院墓地／院庭不填住宅。

## 地理與牆

M19由04保存的市府官方Aurelian牆路線原圖LA28縮讀，來源自身是現況衛星＋概括古牆紅線。現況StPeter穹頂、Hadrian陵、Colosseum、Pantheon僅作地理控制，不拿圖上現代房子／路作當期戶界。原生相似配準四控制點，約5.2142m/px；殘差3.71–30.38m，留一5.08–56.21m。這個量級只能支撐整城工作窗口和概括防線，不能代替已批准Regola的局部控制。原圖各地物像素已放大實看，早先誤認法院為Hadrian陵的控制已撤，不使用其百米誤差結果。

Aurelian兩條開放線在Tiber岸端終止，以49e98d2原生`walls.pts/style:curtain`表現，不在河上造閉合牆、不用屋頂塔樓／壕溝／prism。800採M18對Hadrian I等修牆的本期證據，12m幕牆是Honorius加高後繼續使用的展示分支；3.6m厚及29.6m方塔節奏借官方初牆比較，**不是每個塔都確證在800完整留存**。1300/1377沿同一路廊代表維護延續，未畫1157各段砌體差異。門位置借現存具名門作地理錨，沒有文藝復興門立面。

M20：Isa Belli Barsali1976〈Civitas Leoniana e la Giovannipoli〉原掃描PDF已取得；圖208 Prandi假說、209 Lanciani比較、210–211牆體原圖及相關頁實看。https://www.mgh-bibliothek.de/dokumente/a/a147244.pdf 。M21市府牆博物館原HTML支持848–852、6m高／4m基厚、三原門及後來Pius IV改擴。https://museovirtualedellemura.romasitounesco.it/mura-vaticane/ 。1300／1377採舊線走廊、Passetto方向和西丘接線估配，不聲稱精確逐塔圖；沒有直接照今日Vatican外界，也不含Pius IV北擴／星堡。800完全沒有這條新牆。因逐塔當期狀態未核，Leonine不生成平均塔數。

## 公共建物及園地

舊StPeter：已批04五廊／橫廳／apse核心保留，M18的Hadrian屋頂、鋪前院及quadriporticus記錄支持800已維護並有前院。原址以Peter祭壇／今穹頂地點控制，84°地理方向；主屋中心由原生local框放在其東54.5m。Alfarano1590只供新舊位置關係核對，不把全部1590附件提前。66×70m前院及6m柱廊圖式估配；三條原生arches表示覆廊，未重建完整中世紀鐘樓、旁殿、精細屋架或西側殉道祠。樣板只在`rome06_medieval_templates.yaml`寫一次，各期以native template引用。

大殿與前院分作兩個原生site，以各自坡地標高落地，避免把約200m長的兩個建物系統合併整平。保留來源尺寸，採本study統一的原生高度淡化規則；圖中顯示高度受城市地形誇張影響，不能作實測立面。前院內貼地paved，大殿下方及住宅範圍不鋪earth，不生成文藝復興廣場。

正式06／07接續由導演另准大殿改用原生`site: cut`，去掉整個大殿外包的矩形台基，牆下仍落地；前院維持獨立site。原形尺寸與84°方向不改，三個部件加`nave`、`transept`、`apse` ID；各自的程序屋頂／側廊跟隨同一部件退出。獨立小study `rome06_formal_stpeter_cut_v1`為51件，geo／clip0，4.57秒兩向圖及施工足跡近圖實看。07依R03配準的1506 Veronica earth足跡在後殿南側部分可見，餘部仍受舊橫廳實體遮擋；沒有挪足跡、畫7.45m坑或宣稱全露。早期800模型其餘部分維持已批版本。舊西端1506後逐步替換、東中殿至1606–09仍用，前院不隨1506先撤；正式退場必須由原06與07新核心／長殿stage對齊，不能因新增ID便當首石落下時整殿被拆。

M26：市府TurismoRoma〈Basilica di Santa Maria in Trastevere〉原頁明列`POINT (12.470233 41.889348)`；它是殿東側訪客地址定位，不是殿身中心。https://www.turismoroma.it/it/luoghi/basilica-di-santa-maria-trastevere 。另取M27 OSM API原XML的way51368975核對現況外包，殿身中心約12.469455,41.889425，只作地理控制，未將現況附殿全數回填。官方說明InnocentII重建及十二世紀鐘樓，故1300／1377取現址早期殿身比較；800前身的量體、方向及屋面仍為估配，不把十二世紀重建形式稱作800測繪。1702改造廊立面未復原。坡地採原生raised site及城市高度淡化規則，來源估計的17m簷高保留。

StPaul：Basilica自身官方history/nave原文支持390大殿、1823前維持舊配置、19c重建沿原尺寸，以及135×65m／30m高的總尺度。https://basilicasanpaolo.org/en/history/ 、https://basilicasanpaolo.org/en/nave/ 。模型取121m矩形身加apse／橫翼近似這個總長，25m主簷是按30m總高及估配屋坡反算的量級；未照抄現代前院及立面。1300朝聖兩目的地依M06；旁白沒有新增棟數／客流。

Lateran：LA06 Guidobaldi原文支持91m矩形體、55m外寬與早期五廊；800不放13c橫廳。1300加入晚13c橫廳的低細節比較；1377選火災後修復外殼分支，實際屋頂／柱墩進度未定，不冒稱完全同原構。Vatican舊網頁將首次火災寫1307且加冕年也有錯置，本件不採其精確年；M24 Bosman文章及SRSP原刊支持1308／1361（M24舊檔名含guidobaldi，不是作者）。一般教堂只作有據場所的外量體比較，尺寸／屋高不聲稱每座中世紀實測，沒有巴洛克立面。

M10支持EugeneIII／InnocentIII／NicholasIII宮殿及保存房間，晚期模型只取StPeter東北的L形低宮翼，100×20m／76×22m及兩個3m層是有界最低樓層比較，非完整Palazzo測繪。沒有Sistine、Belvedere或現代聖彼得。Santo Spirito早期Schola／1198醫院本件僅留用地與功能來源，沒有把15c長病房當1300；詳細院樓未復原。

M09的1279果園／草地／園地作用在西丘一個有限工作窗；20m樹距、5m樹、2m冠半徑全為估配，不取今日44ha界。外圍田園／墓地／公共開放地用`grounds`合多塊貼地土／草面，水維持真正Tiber；不造藍板空洞、假池或實心鋪地prism。西丘周邊和城外StPaul周邊的grass是有限製作景觀工作窗，概括未密建的開放地，不能讀成每片均為草坪、1279花園或確定產權界；800的景觀邊界不採848–852牆線。依導演最新grounds規則，移除居住工作窗earth及Regola整塊earth，城級grass也扣除完整住宅工作窗與公共建物site；住宅巷弄、私院和縫隙保留暗底板。只以grass作外圍田園背景，另保留Forum公共空地earth、StPeter前院paved與寺院公共園地；沒有資料的個別墟地與田作未逐筆復原。各城ground合計低於原生32槽上限。今日地形不是古代地坪，沒有復原洪水岸線、地下8m或河堤。舊古殼的完整毀損／住宅轉用、Capitol中世紀市政宮、普通塔屋的原高及Schola院樓仍未細復原；不能稱本研究是每個主要古蹟的完整1377狀態。

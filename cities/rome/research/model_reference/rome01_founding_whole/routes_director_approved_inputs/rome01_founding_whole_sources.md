# 建城期整體的來源與估配

窗口為中VIII世紀附近，753BCE仍是傳統紀年。模型180個屋構是製作估配，既非180戶，也非已挖出的180座同期住宅。導演批准四屋path版的整組輸入原樣保留；新增群使用相同已批准外形以控制形制變因，不能據180/180選樣聲稱古代房型100%相同。

## 本輪核讀來源

| 編號 | 原始來源／實讀範圍 | 用途與限制 |
|---|---|---|
| W01 | [Benedetti、Bussaglia、Fulminante、Guidi、Stamerra2019，Origini43，171–208](https://iris.uniroma3.it/handle/11590/381754)，大學原PDF43頁；本輪讀印刷190、194–202、206–208及圖7（印刷195／PDF30） | 提供居住／墓葬／二次材料點及原地貌；個別屋址、群界、地坪與全城戶數未由圖取得。圖7III大窗口含850/825–750/725；不能把其中所有東西當753年並立。 |
| W02 | [Cifani2016原作者PDF，82–84](https://art.torvergata.it/retrieve/e291c0d7-49a7-cddb-e053-3a05fe0aa144/The_fortifications_of_archaic_Rome_socia.pdf) | IX–VIII的Capitoline、Palatine、Quirinal及Velia居住與墓地外移的整體關係；不由其面積學說直接填滿地形。 |
| W03 | [Musei Capitolini：Origins](https://www.museicapitolini.org/en/node/2482)，本輪完整正文 | Giardino Romano及Tabularium的hut／生產痕跡；頁面跨度大，單一工作窗內的具體屋構仍為估配。 |
| W04 | [市府：VIII–VII聚落](https://www.sovraintendenzaroma.it/content/abitato-di-viii-vii-secolo)，本輪完整正文；另核同站[前廣場區](https://www.sovraintendenzaroma.it/content/l%E2%80%99area-prima-dei-fori) | Caesar區生活與儲藏、生產；較早墓地與較晚鍛爐不全部同時重建。 |
| F01/F02/F04 | 既有Pensabene2009 pp5–7圖1–2、PArCo官方A形制、Coarelli平剖，見既有founding/cermalus來源報告 | 已批准A/B/C/E與其不確定保持；不並立跨期出土平面。 |
| N01/N02 | 既有Evans等2019發掘者報告及Samuels等2021圖5A，見rome01_cermalus_evidence_report.md | Gabii複合體：三個屋跡及活動面；僅一、可能二屋可作居住。存跡中心距5.85/10.80/20.41m只作疏密與戶外關係比較，不作Rome密度常數。 |

W01原PDF、文字、圖7原頁渲染、網頁原存檔在`research/model_reference/rome01_founding_whole/`。所有第三方圖只作研究，未取得上屏再製授權。網頁核讀不等於未取得的早期原發掘刊已讀；W01是重新檢查原材料的學術綜合，並非新挖180屋的報告。

## 分期選擇

保留源中已在IIB占居、III延續的居住群以及中VIII附近可支持的生活圖像。北Palatine只示意IIIB1拆除以前的群落；IIIB1後的Domus Regia14、牆／門18、新聖區均不建。Brown’s Regia十或十一hut traces有重建及不同功能解讀，不當同期十／十一戶。Comitium750/700的公共地坪、Capitoline特殊青少年墓與後期favissa建築、晚VII瓦頂屋均不倒放。Quirinal南段的VIII持續占居較弱，引用W02的IX–VIII範圍並明示W01 Pilotta證據屬IIB，未稱III個別屋址。

## 範圍、計數與方向

完整逐屋local_m、路線、來源像素窗與每群count_basis在`rome01_founding_whole_layout.yaml`，朝向由最近活動徑估算，最終theta逐屋存原生trace的model及provenance；trace將依據欄位置於各屋provenance，另由native register回繪。源中的點是出土地點，不是完整住宅外廓；工作窗是沿相同用途點與地貌接合的製作估配，不是已知古村界。

| 群 | 圖7來源點 | 屋構估配 | 計數推導與範圍性質 |
|---|---|---:|---|
| Capitolium–Tabularium | 2、4 | 32 | 三個不等活動口袋19+8+5；選西峰及其東側內緣，留坡與谷，不填整座丘。 |
| Caesar谷地 | 5 | 16 | 兩個不等活動口袋13+3；局限早期炊煮／儲藏點附近，非舊墓地復原。 |
| Forum–Regia生活群 | 10–12 | 18 | 三個不等活動口袋12+4+2；區內兼有生活／祭祀／圈養解讀，模型不給每屋家庭或職能。 |
| 北Palatine | 15、17 | 24 | 三個不等活動口袋15+5+4，沿多個有據生活焦點接成窄窗；保留後來拆除以前的示意。 |
| 東北Palatine | 19 | 24 | 三個不等活動口袋14+6+4，來源有primary hut／terrace，實際地坪不恢復。 |
| 山頂走廊 | 21、22 | 40 | 四個不等活動口袋12+10+12+6；以Vigna Barberini早期primary材料和Flavia區secondary材料間的有界山頂地貌窗連起，非全山蓋滿。 |
| Cermalus北西延伸 | 23–25、F01北及西側痕跡 | 12 | 兩個不等活動口袋10+2；與已批650m²小窗分開，沒有把Gabii四構上限乘滿Palatine。 |
| 南Quirinal | W01 Pilotta、W02 | 10 | 兩個不等活動口袋9+1；證據與定年較弱，留小範圍，遠離北墓地。 |
| 已批Cermalus | F01／原packet | 4 | A/B/C/E及20條path輸入逐欄原樣保存，不重新安排。 |

計數是這些工作窗內不等活動口袋的明列位置數；不是古人路徑長度量測。路線與屋位一起估配，戶外活動比較支持相鄰小構與較大留空，沒有由道路長度推出真實戶數。各群為開放分叉，沒有閉合環路或同心屋圈；分支彎曲、偏置，門向個別朝活動地面估定；每群用同一框只是local座標，不是群內單一朝向。所有新增屋均一層、已批八部件外形；尺寸／上高原有比較估值延續，未新增古代型態／比例主張。

1.2m土徑沿已批約1.23m門洞的出入製作值；不是同期街寬實測。無車轍、硬鋪、院界或格網。新增線只在各群內表示可讀出入關係；群間未取得同期精確路線，不造等寬大道。屋間中心距以原生地理框量測列measurements；Gabii近／疏關係只供量級核對。

## 墓地、空地和未畫區

圖7灰區的Quirinal26–30、Esquiline32–33、Castro Pretorio31按來源輪廓描在研究overlay，模型留空不建屋。它們是概括分布窗，不是古牆、墓界或同步墓葬清冊。圖35的Caelian IIIA墓葬點、34的sporadic bronze belt另在來源地圖保留，不由兩點填成Caelian住宅村；Aventine的較早二次材料不支持本窗口整丘鋪屋。Forum有較早墓地和後期嬰兒墓，不把舊成人墓地與本期生活群同時鋪出。河谷、山坡與各群間留普通地面，既不塗成已證無人區，也不憑空加田界、池或密林。

原生類別不能挖真正地下fossa／骨灰甕坑。地下覆土墓在地表不必可見，本件只保留不建屋及研究overlay的墓地標示，不立無據大碑石，不用path畫墓地線。正式影片若需說清墓地，由主代理後續安排標籤；此件不做旁白或staging。

## 地理與地面限制

native register以圖7全圖與放大圖分別similarity到Cermalus批准點、DAR Tabularium／Caesar定位。DAR點只作同址粗控制，非古hut輪廓；各點殘差／留一誤差載measurements，另保留原圖尺度核對。全圖適合群落與墓地關係，不支持米級宅界；工作窗還有原圖概括化和源點定位未量化的不確定。地形仍是現代DEM×2；site:cut下坡牆到地，並非古代地坪／坡挖填復原。hide僅供study擋開現代樓，不是古城界。

研究圖的主圖以4.2431m/px、放大圖1.3443m/px套合；與主圖0–500m尺約120px／4.17m/px量級相合。逐點殘差約7.0–20.4m，留一誤差約33.0–93.9m；後者顯示控制集中與原圖概括化，不能以小殘差宣稱宅址精準。新增屋的最近中心距約7.62–23.09m，比較的Gabii數字只提供量級，並非各群必須同值。

最後來源邊緣收據把十個未批准估位收回既定工作窗；每項from/to與原因在layout。新增全部實際屋頂／門廊投影在工作窗內，窗口未因模型擴大；不把這個製作窗口升格成古村界。

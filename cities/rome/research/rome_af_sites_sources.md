# 羅馬 A–F：Passetto／Leonine 與十九世紀台伯河堤

## 可直接採用的判定

| 問題 | 查核結果 | 製作界線 |
|---|---|---|
| B2，973／1123秒 | Passetto 是留存 Leonine 北牆上的通道；1565 年的新 Borgo 外線在其北側。舊中古估配北線與後期 Passetto 的交叉是資料不一致。 | 同址只建一份實體；不能增加共線中點冒充端點接合。 |
| B3，1900 高堤 | 1901 原工程圖可辨兩岸已建及待建段，並非今日全線。中央已建部分可取原圖實線；Santo Spirito 至 San Giacomo 右岸約835m為待建。 | `tiber_1900_traced.geojson` 的 `unbuilt` 禁用。 |
| B3，Anguillara | **沒有1900年底已修復的證據。** 1901原報告說約125m已倒，該240.86m河段殘部亦受損需拆。 | `completed_pre_collapse` 只能標「1900年12月洪水前」。若敘述洪水後／1900年底，整條 `right_garibaldi_cestio` 不顯示。 |
| 1925終態 | 資料對概括竣工年有1925／1926差別；官方既核Silvae明列1926，Aventino末段尤其不可倒放1900。 | 以1870→1875→1880年代→1900→1925順序；1925不宣稱全線竣工。 |

## B2：來源與幾何

1. [Roma Capitale，Mura Vaticane](https://museovirtualedellemura.romasitounesco.it/mura-vaticane/)，已實讀。正文第19行列原Leonine牆高6m、底厚4m；第21行列852年啟用；第26行說Pio IV擴界後Passetto位於內部，開拱連接新舊Borghi；第27行指出後來拆去的新外線沿今日Porcari、Alberico II。6／4m是舊牆尺度，不是後期Passetto逐段實測。
2. [市府牆博物館，Itinerario 8](https://museovirtualedellemura.romasitounesco.it/itinerario-8-mura-vaticane/)，已實讀，第19–20、33行。短摘：`il tratto delle mura leonine – conosciuto anche come Passetto di Borgo`。北側Pio IV外線由Risorgimento至Castel，十九世紀末拆除。
3. 既有R33的[文化部原新聞PDF](https://direzionemuseiroma.cultura.gov.it/wp-content/uploads/2024/12/Cs_Passetto.pdf)及[同文HTML](https://direzionemuseiroma.cultura.gov.it/apertura-al-pubblico-del-passetto-di-borgo/)，已以瀏覽工具讀原文。本機下載TLS失敗，未冒稱有本地PDF。歷史段列1277連通Castel、Alexander VI時增覆蓋通道、1565新外線；現入口Torre del Mascherino，終點Bastione San Marco。無10m逐段實測高度。
4. 既有圖：`model_reference/rome07_renaissance/R09_passetto_close_read.jpg`、`R09_borgo_work1050.jpg`、`rome07_renaissance_retained_source.yaml`的 `passetto_retained`／`civitas_pia_outer1565` 兩條像素線。Falda為1667狀態，不能回填為1300外線。其Borgo配準LOO最高約126m；不適合把此線當狹窄牆身的精確現代定位。
5. 既有中古生成器 `rome06_medieval_whole_prepare.py:127` 明稱M20 Prandi假說加M21方向估配；北段像素實掛在M19全城底圖。該估配不是可保留的精確牆身。M20原[Barsali1976掃描](https://www.mgh-bibliothek.de/dokumente/a/a147244.pdf)既有本地PDF，圖208／209見 `model_reference/rome06_medieval/M20_figs-10.png`；本次實看各圖，沒有把它們假作現代實測。

**共享地理線**在 `rome_af_sites_data/osm_source_geometry.geojson`，feature `passetto_shared_centerline`。來源[OSM relation12043626](https://www.openstreetmap.org/relation/12043626)，取既有2026-10-26快取完整牆身輪廓，UTM兩側截面中點，每15m取樣後0.7m簡化，長約750.59m。從 `[12.45658245,41.90340767]` 至 `[12.46556202,41.90340945]`，中段向南彎。原輪廓及members在 `osm_cached_controls.json`；已看 `passetto_osm_centerline.png` 確認中心線在牆身內。**這是現存同址定位，不是1300／1667逐段測量；局部開拱、上層通道未復原。** OSM為ODbL1.0。Leonine西南舊線未在本次重新配準，不能聲稱整圈已核。

## B3：原始工程圖、日期及端點

- [1901，L’Ingegneria civile 27(16)原PDF](https://digit.biblio.polito.it/4740/1/16_ING.CIV.%20ART_IND_1901_N.16.pdf)，PDF18／Tav.XV，題為1901-01-01施工狀態。圖例紅實線為已成河牆及集水道，點線為待建。**只描重紅水岸線；平行的細紅陸側集水道不是第二排堤牆。** 原檔 `rome_af_sites_data/1901_ingegneria_tevere_cont.pdf`；1890px描圖底 `1901_tavola_xv_trace.png`；回疊 `tiber_1900_source_overlay.png`。PDF17／Tav.XIV另有1900年12月工程剖面。
- [1901，27(15)原PDF](https://digit.biblio.polito.it/4739/1/15_ING.CIV.%20ART_IND_1901_N.15.pdf)，印230：Mellini右岸Margherita–Cavour630m；Anguillara240.86m、約125m倒塌；Alberteschi為Cestio–Palatino111.76m且受損。印231記Anguillara1884打基礎。**不能把1884等同所有段同年完工。** 本地 `1901_ingegneria_tevere.pdf`／`.txt`。
- [國家檔案館／TorVergata2020展PDF](https://archiviodistatoroma.cultura.gov.it/wp-content/uploads/2022/11/2020_GEP_ASR_UTV_presentazione-mostra.pdf)既有 `model_reference/rome08_capital/tiber_archive2020.pdf`；1902／1903修復圖已收於同目錄，不足支持1900已修復。
- [Sciolari2020，原文PDF](https://files.supersite.aruba.it/media/18753_5f47f0b4fd94a90219450cf1c50db75013319171.pdf)已實讀PDF4、7–8：初期下游工程1877起，約1886 San Giacomo至島段大致完成，Aventino末段1926。此為研究整理，未把它當每段原工程驗收單。
- [Silvae／Carabinieri，既有S19](https://www.carabinieri.it/media---comunicazione/silvae/la-rivista/rassegna-giuridica-legislativa/acque/alluvioni-in-italia-eventi-storici-e-gestione-del-territorio)已重核，正文終工年1926。[SIGEA2016原刊](https://www.sigeaweb.it/documenti/gda-supplemento-4-2016.pdf)則有1925概括表；不採其表作1900幾何依據。

描線有16段，河流左／右岸均依下游方向命名；端點lonlat及每個來源像素留在 `tiber_1900_traced.geojson`，可直接讀取。以下所列完成時間除Anguillara基礎1884外，僅能證明**至1900已建**；確切逐段驗收年尚未核得。

| 岸 | 原圖所覆已成區間 | 排除／時態 |
|---|---|---|
| 左岸 | Cavour→Umberto→Sant’Angelo→臨時Vittorio→Fiorentini→Sisto→Garibaldi→Fabricio→Palatino，分8段 | 不生成1900尚未啟用的Cavour、今日Vittorio或後來Mazzini橋；橋只作地理錨。 |
| 右岸 | Cavour→Umberto→Sant’Angelo→臨時Vittorio，分3段；San Giacomo→Sisto→Garibaldi，分2段；Cestio→Palatino，1段 | Santo Spirito→San Giacomo約835m為 `unbuilt`。 |
| 右岸Anguillara | Garibaldi→Cestio，1段 | `completed_pre_collapse`；1900洪水前限定，洪水後不可連續顯示。 |
| 原圖外北延 | Margherita→Cavour右岸 | 原文有據，但本次沒有以今日岸線另補幾何。 |

**配準**：重用 `pipeline/register.py`，五個OSM現存橋位錨；殘差1.39–6.60m，LOO2.46–20.39m，見 `tiber_registration.json`、`bridge_control_locations.json`、`tiber_1900_trace.yaml`。橋位來源包含各OSM原way／relation，並非手列猜點。平面位置標約±20m估配，不作逐米原堤基腳。

**現在影片水岸的輔助對位**：`tiber_1900_water_aligned.geojson` 保留原trace另存。讀現有 `build/data/water.png`，逐1m檢查；只把濕中心點向本岸陸側移，最大15.25m，乾點維持原位，沒有全線吸附水邊。對15條已成／崩塌前段重取0.5m樣本，中心線濕樣本0；`unbuilt`不修也不入片。每段變動在 `tiber_1900_alignment_changes.json`。這只核水岸中心線，牆厚、基腳、現有1866房屋與native cross_era仍須由排片者驗證，不能稱整條幾何已過檢查。

## 留待排片者處理

- 若1900畫面敘述洪水後，刪去Anguillara整條；若保留它，字幕明標1900年12月洪水前，不暗示已修。
- 牆身11.5m代表截面沿既有Anguillara史料取值；擴用其他段須標同工程代表估值，不能稱逐段實測。
- 原圖中央範圍以外、1926 Aventino末段和逐段精確驗收年未補造。既有1925終態應按此限制寫字幕。
- 本次下載的Polito掃描館藏標CC BY-NC-SA；本檔僅研究，不把原圖自動加入電影。其他官方網頁圖片未確認開放授權，不作入片圖。

## B2補查：Belvedere兩處舊牆交叉

排片提供的native交叉為 `[-.3811,-.075]`／`[-.3721,-.0753]`，對應 `[12.453831394,41.905825583]`／`[12.454914375,41.905876624]`。兩點在Belvedere北部，**不能把粗略北繞線當852原Leonine牆，再虛設1562拆除事件。**

- 既有M20原[Barsali1976 PDF](https://www.mgh-bibliothek.de/dokumente/a/a147244.pdf)，**印206／PDF5**實看並OCR：北牆可識別兩段為Castel–San Peregrini，以及花園內Fontana delle Torri–Fontana dell’Aquila；Prandi辨認兩者間宮殿區的部分路徑。西側與南側線仍有學術假說分歧。定位看 `rome_af_sites_data/M20_text05.png`／`.txt`；OCR僅索引，以掃描為準。原圖205（PDF9）、209（PDF10）把舊北線放在後來Belvedere長院落南側的走廊，不能從圖讀出橫跨院落北部的舊粗線。局部放大 `M20_fig209_detail.png`。
- **Gibson／Ward-Perkins1979，PBSR47，印35–36**：[原論文轉錄及掃描頁](https://www.academia.edu/60028806/The_Surviving_Remains_of_the_Leonine_Wall)，[出版資料](https://doi.org/10.1017/S0068246200009314)。已讀原文，明分852原牆與1278擴至北方的Nicholas III pomerium圍牆；宮殿區早期牆跡今已不見，花園內舊北牆則延續至近代。Fontana delle Torri往西丘的部分近代才拆，不能概稱1562全拆。其1936說法自身腳註指出1929／1934地圖已有改變，故不取精確拆年。Cambridge下載回應是HTML，已按實際內容存 `.html`，**沒有冒稱取得原PDF**。
- [梵蒂岡國家花園史](https://www.vaticanstate.va/it/altri-organismi/giardini-vaticani?format=html)，正文77–78行，另證1279前後Nicholas III新圍牆內的pomerium／viridarium在今日Belvedere與博物館庭院一帶。這不提供該新圍牆逐米路線，不能拿來替舊粗線改名後照用。
- [Musei Vaticani，Nicchione](https://www.museivaticani.va/content/museivaticani/it/collezioni/musei/museo-gregoriano-egizio/terrazza-del-nicchione/terrazza-del-nicchione.html)只證1562 Ligorio平台及大壁龕替換Bramante較低exedra；**不證兩交叉座標的Leonine拆牆年。**

**可用的北段修正示意**：`rome_af_sites_data/leonine_north_source_bounded.geojson`，只用feature `leonine_north_source_bounded_schematic`。路徑為現存Passetto西端 `[12.45658245,41.90340767]` → Torri地理定位 `[12.45348715,41.90342505]` → 花園存牆東端 `[12.4517852,41.9036427]`，沿現存片段至西端 `[12.4512377,41.9037368]` → 接回舊西線估點 `[12.45090409,41.90360281]`。後一連接約數十米，是舊西線交接的製作估值，未宣稱原牆轉角。

Torri定位取[OSM way111697743](https://www.openstreetmap.org/way/111697743)的現況噴泉輪廓中點（`osm_fontana_torri.xml`）；其Fontana delle Torri／del Sacramento同名關係亦見[梵蒂岡博物館2022目錄地圖](https://www.museivaticani.va/content/dam/museivaticani/pdf/eventi_novita/iniziative/novita_editoriali/39_Scheda_catalogo_giardini_vaticani.pdf)。花園存牆地理形狀取[OSM way111699140](https://www.openstreetmap.org/way/111699140)，原資料在 `leonine_north_osm_reference.json`。後世噴泉只作位置錨，**不生成中古噴泉**；OSM標籤本身不負責原牆年代，年代及路徑選擇依M20和考古論文。

這條是**文獻描述＋現況錨的地理示意，並非已配準的像素描線**。宮殿區Passetto–Torri只能承認約50–100m量級不確定性，花園接線約20–40m、與舊西線交接約40m；以上是製作不確定性估值，不是擬合殘差。只修北繞41.9058的無據映射，西南未核部分維持原本明示估配。後期宮殿覆蓋區不得同時建獨立舊牆和新宮殿兩份實體；來源不能分辨每段拆除／包入年份，應表為簡化同址整合或省略失去輪廓的舊砌體，不造精確拆年，也不在Belvedere割洞來過檢查。

## B3補查：Palazzo di Giustizia粗配與堤線

排片指出 `a_home_lost` 的 `rome09_fascist_palazzo_giustizia`，舊中心 `[12.4703832,41.9038963]`、256×184m粗外包撞到Umberto–Sant’Angelo右岸堤。原公建與真堤都應保留，修正公建的無據定位／尺度。

- [OSM relation325578](https://www.openstreetmap.org/relation/325578)，實取API原始資料 `rome_af_sites_data/osm_palazzo_giustizia.xml`，用原生 `osmgeo.polys` 組合外輪廓及11內院洞。`palazzo_giustizia_osm.geojson` 為完整輪廓，`palazzo_giustizia_osm_raw.json` 留relation原members，`palazzo_giustizia_dimensions.json` 留UTM33測量。
- 現況面積重心 `[12.470429674,41.904174064]`，比舊中心約北31m；最小外包矩形約170.67×159.47m，朝向112.069°的一邊159.47m。外輪廓包絡面積26,480.69m²，扣11內院後21,567.66m²。**外包256×184m的主要問題是過大且偏南；不是新堤該轉彎。**
- 與本次 `tiber_1900_water_aligned.geojson` 的平面最短距離：右岸Umberto–Sant’Angelo38.26m、Cavour–Umberto25.75m。源輪廓不與兩堤重疊；這是平面來源比較，不是native立體檢查通過聲明。
- [最高法院原宮史](https://www.cortedicassazione.it/it/storia_del_palazzo.page)，正文96、102–103行已讀：1889-03-14奠基、1911-01-11啟用、覆地逾27,000m²。[總檢察署宮史](https://www.procuracassazione.it/it/storia.page)亦確認Calderini設計、1889動工、1910完成、1911啟用。這是統一後義大利王國的既有宮殿，**不能因模型id有fascist就稱法西斯新建**。最高法院宮史80–81行的1888刑事／1923民事Cassazione統一是制度史，與建築落成分開。
- 1932可採這座1911既有建築的同址主體輪廓作**平面估用**；未證今見11內院、屋頂和局部附屬物在1932完全不變，也未在本次核高度／雕塑年代。MIT2023相關工程PDF僅找到索引，瀏覽502、本機TLS失敗，未把其未讀航照冒稱同址形制證據。OSM輪廓採ODbL1.0；官方宮史圖片未核授權，不自動入片。

## B4補查：2020背景的兩道文藝復興牆

已看 `cities/rome_af_r5_all/build/review/living/rome_af_prayer2020_ref.jpg`。查核對象是 `made_again` 留到2020的 `rome07_renaissance_civitas_pia_outer1565` 與 `rome07_renaissance_vatican_southern_circuit`，不是已退場的中古Leonine。

| 真實路段 | 2020能否視為仍在 | 舊模型處理界線 |
|---|---|---|
| Piazza Risorgimento／Porta Angelica往Castel Sant’Angelo的Borgo北外線 | **不能**；十九世紀末拆除 | Civitas Pia東支不能留作2020連續長高牆。Passetto是另一條仍存牆，勿連帶刪除。 |
| Risorgimento角向西，經Via Leone IV的Belvedere／Michelangelo堡 | **可以**；仍存，並有後來重修 | 不可因Civitas Pia東支拆除而把西側回折也全刪。依現況走向續留。 |
| 堡角沿Viale Vaticano，經Porta Pertusa，下降到Cavalleggeri舊門址 | **可以**；外圍牆大體存留 | Vatican南西防線不能整道當不存在。舊Falda估配坐標不能當2020逐段牆址。 |
| Porta Cavalleggeri本身 | 原門**不能**；官方記1890拆，殘件移入近旁牆中 | 留牆與移置殘件，不建已拆門樓。 |
| Cavalleggeri至Santo Spirito的南東續段 | 官方敘述有相關防線／殘構；本次沒有完成逐段現況描線 | 不以現有Falda尾段直接聲稱2020連續8m高實牆。不能僅憑美術效果斷言整段拆光。 |

**來源**：[市府牆博物館Itinerario8](https://museovirtualedellemura.romasitounesco.it/itinerario-8-mura-vaticane/)第18行列大體存留外圍牆，第19行列Risorgimento–Castel已拆，第23–29行列移置門件、近代入口和Cavalleggeri拆門。另[同館Mura Vaticane](https://museovirtualedellemura.romasitounesco.it/mura-vaticane/)第27行把消失的Borgo支線定位至今日Porcari／Alberico II。[Carabinieri2019原刊第24頁](https://www.carabinieri.it/Internet/ImageStore/Magazines/NotiziarioStorico/Volume%2080%20storia/files/basic-html/page24.html)實讀：1888景觀畫中往Castel的牆已幾乎拆去，Porta Angelica於1888-05-18拆；不把該門拆除日冒稱整條各段同日拆。[市府Pio XI紋章條目](https://museovirtualedellemura.romasitounesco.it/pin/stemma-di-pio-xi-ratti-1922-1939-1929-post/)亦證Risorgimento現存國界牆角有1929後工程，不能稱1565原砌體完整未動。

**可用現況定位檔**：`rome_af_sites_data/vatican_walls_2020_retained_locators.geojson`；兩條LineString分別為：

- `vatican_angelica_west_return_retained`：Risorgimento角 `[12.4576569,41.9058208]` → 西側堡角 `[12.4554001,41.9073829]`，10點。
- `vatican_west_south_perimeter_retained`：上述堡角 → Viale Vaticano／Pertusa → Cavalleggeri舊門址 `[12.4563573,41.9003889]`，95點。

地理來源為既有OSM快取的[way781938105](https://www.openstreetmap.org/way/781938105)及[way525783139](https://www.openstreetmap.org/way/525783139)，原資料在 `vatican_walls_2020_osm_raw.json`。只取官方敘述的仍存外周；沒有把OSM大way裡的宮殿內牆也一起冒作國界。檔中兩個Point只是Pertusa／Cavalleggeri定位，不是新建門的指令。OSM為2026快取，2022官方步行路線支持現代主體延續；**對2020僅作同址路線估用，不保證2020每個入口／修補縫都與2026相同**。影片不應演成2020新建牆。

既有Falda兩線地理上均有大偏差：Civitas Pia北西端到41.9098，而現存堡牆北界約41.9074；southern circuit西緣僅12.4497，而現存外圍到12.4458。不能把二三百米差異說成原牆整線現存，也不能由其位置偏差推論全牆歷史上不存在。本次只給現況有據保留範圍；舊史圖線與現況定位應分期表達。原8m高／5m厚仍是製作估值，本次未測現存逐段高度、厚度、門洞，不把現況牆補成無開口的完整古防線。

**已拆東支的歷史走廊示意**：`rome_af_sites_data/civitas_pia_demolished_east_schematic.geojson`，只取LineString feature `civitas_pia_demolished_borgo_east_schematic`。22點從同一現況Risorgimento角 `[12.4576569,41.9058208]`，沿官方具名的Porcari／Alberico II走廊，到Castel西北前場街位錨 `[12.4647755,41.9043368]`。現況街道輪廓取OSM ways 22716368、184775522、22912139、118709077、366799280；原資料 `osm_borgo_demolished_corridor.xml`，所用街位留 `civitas_pia_demolished_street_anchors.json`，可用 `borgo_demolished_east_branch.py` 重製。這些拆牆後街道只是地理錨，**不證原牆恰在今日車道中心；這不是原圖配準描線**。街道間缺口以示意連線接合，製作不確定性約30–80m，尤其Risorgimento門區、Porcari至Alberico間隙與Castel接口；這不是擬合殘差。終點不是某堡壘的實測接口，不為模型endpoint joint延到城堡core。

另實讀[市府Porta Castello條目](https://museovirtualedellemura.romasitounesco.it/pin/porta-castello/)第17–22行：Pio IV新圈約1563開門、1565完工，原門在今via di Porta Castello／via Vitelleschi一帶；1883是市政拆門決議，不能冒稱整支牆實際拆畢日。今日同名Passetto拱洞與該外圈原門不同。原址範圍比Alberico II現街軸南約60–80m，故另外只附研究定位Point `[12.46306,41.90420]`，**不把它硬接入東支以虛造精確門洞或歷史轉角**。排片可分為西北現存回折、西南現存外周、十九世紀末退場的東支三段；共同Risorgimento端是現況地理錨，非1565精測門址，三段的高度與局部砌體不能因此宣稱同年同制。

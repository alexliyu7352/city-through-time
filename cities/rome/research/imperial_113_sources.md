# AD113整城模型依據

住宅配置的採用狀態已撤回：20區格網、三種固定宅地、9,455一層院宅／380五層租樓及原先 rental_share 不足以支持城市樣貌。這些數字記錄被退回的模型，不是歷史比例。公共建築、營區、有據街道與×2地形已確認，資料保留；Subura69棟樣區其後已確認；整城新住宅的逐區依據及限制見[imperial_housing_atlas.md](imperial_housing_atlas.md)。以下三種types與住宅數量屬舊版歷史記錄，公共建築資料仍採用。

承接已通過的Forum—Palatine33棟與Julia真開口券廊，原41要素原封合併。整城是來源約束的示意復原；不是113年的逐棟考古普查。住宅仍用已審S84–85/S94三種types，沒有另寫造型程式。具體參數、推定及省略細節分別寫在`imperial_113_landmarks.yaml`、`imperial_113_placements.yaml`的basis。

## 配準與布局（S95）

研究底圖沿用[Digital Augustan Rome約AD14地圖](https://www.digitalaugustanrome.org/)及其[建成區條目](https://www.digitalaugustanrome.org/records/continentia/)，再按年代加入64年後至Trajan的變化。[DAR Subura](https://www.digitalaugustanrome.org/records/subura/)約束谷地入口、街路及密建區。DAR點資料只作標籤位置，沒有把它們當足跡。

整城Lanciani取館藏既有KML配準的level4瓦片47張，EPSG:4326、2048×1536；帝國廣場詳圖level6取40張、2048×1280。`lanciani_imperial_113_sources.json`及`lanciani_imperial_fora_sources.json`逐張記URL、原bounds與SHA-256，未自擬控制點。圖上古代各時期混列，黑色並不自動代表113年。

`model_reference/imperial_osm_anchors.geojson`保留實際採用的OSM遺址參考，包含原id／網址。缺段的multipolygon以原線段polygonize，不取任意凸包當測繪平面。完整復原的包絡／中心有別於局部殘跡中心，分別註明。模型的原生extent包絡只用來避免房屋侵入，不冒充精確建築外牆。

20個分區界線、內巷、宅地與租樓比例都是示意，受Tiber、古街廊道、公共建築、園林及不同丘陵街向約束。`imperial_113_geography.yaml`逐區載依據；`lay_imperial_113.py`只配置完整宅地，原生citygen繪製。未知住宅區照同期習俗連續補足；Forum、宮殿院庭、浴場園庭與horti留白各有用途。現代河線只作保守避讓，不能宣稱古岸完全相同。

## 娛樂公共建築（S96）

- [Roma Capitale Marcellus](https://www.turismoroma.it/it/luoghi/teatro-di-marcello)給130m直徑、半圓cavea與三層外觀；[DAR](https://www.digitalaugustanrome.org/records/theatrum-marcelli/)核對NE–SW軸與河邊舞台。32m高度、37m orchestra、12m舞台深度及券數為同劇場復原的建模推定，不稱實測。
- [DAR Pompey](https://www.digitalaugustanrome.org/records/theatrum-pompeium-pompeianum/)明示朝東、東側quadriportico，並區分80年後Domitian重建與Augustan舞台；150m直徑約讀配準圖，36m高、44m orchestra及14m舞台為[Caen具名復原](https://histoiredesarts.culture.gouv.fr/Toutes-les-ressources/Universite-de-Caen/Le-complexe-pompeien-Plan-de-Rome)比例推定。爭議Venus Victrix外凸廟沒有硬補。模型省略複雜scaenae frons。
- [DAR Balbus](https://www.digitalaugustanrome.org/records/theatrum-balbus/)核朝東與Crypta Balbi。90m直徑約讀圖；其餘按Marcellus同型比較推定。
- Domitian stadium：[市府考古頁](https://sovraintendenzaroma.it/i_luoghi/roma_antica/monumenti/stadio_di_domiziano)寫265×106m，[市府旅遊頁](https://www.turismoroma.it/en/places/stadium-domitian-archaeological-area)及[Caen](https://rome.unicaen.fr/monument/stadedomitien/)寫275×106m；模型採後兩者。高度20m按Circus Maximus比較推定，內場長度服從原生等寬看台帶，不稱193m實測。無spina／方尖碑。原生u的低矮直端封閉量體並非斜向南立面的精細復原。

現成ring的外廊深色開口是矩形簡化，並非Julia的真圓券；三層柱式、舞台雕飾、velarium未復原。Colosseum與Circus沿已審S86/87形制，不增加假精度。

## Palatine（S97）

[PArCo地坪導覽](https://colosseo.it/percorsi/camminare-sulla-storia-mosaici-e-pavimenti-in-marmo-del-palatino/)核Domus Flavia北接見廳、中央peristyle、南宴會廳，東側Domus Augustana私人院庭。[Caen Domus Flavia](https://rome.unicaen.fr/monument/domusflavia/)給Aula37×44m及可能逾27m高。Flavia整件約92×155m、內院與宴廳尺寸按完整遺址／配準圖推定；北Aula不是放在Domus Tiberiana的位置。原已審山丘圖所用Aula錨點只是展示用，整城改用OSM Aula實址與宮殿朝向，不把展示點當測繪。

Flavia整個parts共用一個地坪。Augustana上／下院是來源辨認的不同歷史台地；每院內部共用一面，不是逐翼各自落地。[Domus Tiberiana官方頁](https://colosseo.it/mosaico/domus-tiberiana/)核一世紀宮殿；本輪只取中心院落，不把Hadrian北向延展整張倒放。缺證據的房間分隔、精細柱廊／噴泉不假稱已復原。

[官方Stadium](https://colosseo.it/mirabilia/stadio-palatino/)161×48m、西南曲端、東exedra、三面柱廊及約低宮殿10m。模型取原生u之building帶，不冒作觀眾看台；6m廊帶、7m高推定，東exedra及內柱尚簡化，晚期內橢圓不放113年。現代DEM不能直接當古地坪，因此不手加負10m。

## Forum、神廟與帝國廣場（S98）

[Curia官方](https://colosseo.it/mirabilia/curia-iulia/)給21m內高，也指出現存Diocletian重修；模型用約30×26m外包與推定22m檐高，沒有複製晚期內飾。[Musei Capitolini](https://www.museicapitolini.org/en/sede/campidoglio_antico/tempio_di_giove_capitolino)核約55×60m基座及Domitian重建；其柱高／屋面按該廟復原推定。

其餘殘跡外框來自保留id的OSM／配準圖：Aemilia、Saturn、Vespasian、Vesta、Atrium Vestae。層高等未測值分別按Julia/Ulpia/Castor或Flavian宮殿具名同型比較；圓廟用錐屋面，不任意加半球頂。[Titus arch官方](https://colosseo.it/restauri/arco-di-tito/)核Flavian單券，13.5×4.75×15.4m外包與券比例作同拱門復原估值，無浮雕文字。

[Caesar廣場官方](https://mercatiditraiano.it/it/sede/area_archeologica/foro_di_cesare)、[Augustus區展示](https://mercatiditraiano.it/it/percorsi/sezione-del-foro-di-augusto)、[Minerva／Colonnacce官方](https://www.sovraintendenzaroma.it/content/tempio-di-minerva-e-colonnacce)、[Peace官方](https://www.turismoroma.it/it/node/1053)配合Lanciani全圖約束殿宇與院庭。每件parts包含庭園圍廊及本身神廟，不以空白大地代替廣場，也不灌住宅。長寬與高度的圖讀／推定逐件列明；不是原生類別畫得出就宣稱精確。Peace的後世Forma Urbis牆不當113年細節。

[Trajan Great Hemicycle](https://www.mercatiditraiano.it/it/infopage/gran-hemiciclo)配合原址多邊形保留半圓與Great Hall，沒有拿方盒代替曲線；三層與層高是同建築復原推定，階地及商店分隔簡化。Trajan廣場後方未核年代的皇帝廟排除。Ulpia/Column依S88/91，柱座改準原址。

[Ludus官方](https://sovraintendenzaroma.it/node/2335)核Domitian設施，按完整圖讀約100×85m院及63×42m練習環場，房間／高度推定。[Portunus官方](https://soprintendenzaspecialeroma.it/luoghi/tempio-di-portunus/)核共和港邊廟；Hercules圓廟與Palatine Apollo依古址及[PArCo前28年記錄](https://colosseo.it/percorsi/scoprire-egitto-parco-archeologico-colosseo/)配置。柱式、完整上構與屋頂參數仍推定，不複製教堂改建細節。

## Trajan浴場（S99）

[Roma Capitale](https://www.sovraintendenzaroma.it/cosa_facciamo/didattica/terme_di_traiano)核109啟用。[Padova TESS11902](https://tess.beniculturali.unipd.it/web/scheda/?recid=11902)給逾330×315m，中央本體、外exedra、natatio、雙palestre與長方形三apse caldarium。模型保留圍區、雙開院、軸上高廳與外端半圓。180×110m中央包絡、各室高12/24m及屋頂比例是圖讀／估值；室內溫冷水流程、三apse與水池未全復原，沒有用Caracalla平面代替。

## 河港、柱廊、墓與橋（S100）

[Porticus Aemilia市府](https://www.turismoroma.it/en/places/porticus-aemilia)、[MiC](https://cultura.gov.it/comunicato/porticus-aemilia-diventa-parco-pubblicoprotetto-e-illuminato-dalla-soprintendenza-archeologica-di-roma)給487×60m、50橫向桶拱帶；模型用原生repeat×50，8m高度估值。不把殘存87m牆段當整座。傳統名稱／港倉解釋仍有學術辨識問題，不作旁白定論。294柱墩與逐兩帶地坪落差未做。Horrea Galbana一般位置來自DAR；三院庫房為圖讀／同期示意，不是假稱113年出土全貌。Regola不倒用Severan四層住樓。

[DAR Saepta](https://www.digitalaugustanrome.org/records/saepta-iulia/)核310×120m及Domitian80火災後重建；[Octavia](https://www.digitalaugustanrome.org/records/porticus-octaviae/)／[Caen](https://rome.unicaen.fr/monument/portiqueoctavie/)配合約119×132m圍區。8–10m廊寬／高為同型估值，沒有複製現存Severan門廊。

[市府Augustus mausoleum說明](https://sovraintendenzaroma.it/sites/default/files/scheda%20storica%20Mausoleo.pdf)及87m官方外徑作圓形鼓座／覆土類型，古上構不確定；各段高度與古像明列估值。[Fabricius/Cestius官方冊](https://sovraintendenzaroma.it/sites/default/files/storage/original/application/10ca51a6208eb64e25c4a259d3ff184a.pdf)核共和渡河與兩主券；Fabricius包絡採現址古橋66×8.2m近似，高度／路面厚度估值。[Cestio官方](https://sovraintendenzaroma.it/i_luoghi/roma_antica/monumenti/ponte_cestio)明示365及近代重建；113年版本只作依同時期Fabricius類比的60m單券渡河示意，絕不稱現存81.6m橋原貌。

## 年代排除（S101）

[Pantheon官方歷史](https://direzionemuseiroma.cultura.gov.it/pantheon/cenni-storici/)記80/110損壞、現形118–125。113年留出該公共工地／損壞區，不硬放Hadrian完工大圓頂，也不冒稱已知當年具體施工進度。奧勒良城牆、Venus/Roma、Maxentius殿、Constantine拱、Caracalla/Diocletian浴場、後期宮殿延伸皆排除。

本輪只建獨立113年末景。正式03站-27至113的分期／id群組介面待主線通知，旁白與字幕時間骨架不變。外部底圖、重建圖只研究，未移入影片assets；公開模型須標Schematic。


## 整城自查補項（S102–103）

[Dar Agrippa浴場](https://www.digitalaugustanrome.org/records/thermae-agrippa/)約束Pantheon以南、Saepta以西的位置，不能把公共浴場地填住宅。113年房間與上構簡化為圖讀圍區及同期浴場廳室；沒有拿晚期Ciambella遺構當初建。[Platner/Ashby Nero浴場](https://penelope.uchicago.edu/Thayer/E/Gazetteer/Places/Europe/Italy/Lazio/Roma/Rome/_Texts/PLATOP%2A/Thermae_Neronianae.html)給190×120m、朝北及雙側庭／中廳，並明示227重建。模型以12/18m廳高的同期類比示意113量體，不能聲稱復原確切Neronian室內。

[官方Castra Praetoria研究](https://soprintendenzaspecialeroma.it/intervento/id-241-castro-pretorio-biblioteca-nazionale/)核Tiberius營區約16ha，晚後才併入奧勒良城牆；[TESS13007](https://tess.beniculturali.unipd.it/web/scheda/?recid=13007)給440×360m及76×12m兵舍比較，但地坪包含Hadrian／Severan階段，沒有把它們稱113年逐棟實證。模型營址／朝向約讀館藏配準圖，4.5m低牆與48棟兵舍是示意；兵舍一層4.25m／屋面依已審同期羅馬房屋比較。使用原生無樓塔牆及long_hall，沒有中國門樓、奧勒良高牆或按墓地畫密宅。

自查修正：Marcellus原點在後方看台，改按配準詳圖圓心／舞台軸。13點圈線擬合殘差1.1m不含地圖配準誤差；圖讀直徑約140m與官方130m不符，尺寸採官方，中心仍是示意。記錄在`model_reference/marcellus_anchor_measurement.json`。Flavia院庭放在Aula軸西側，Augustana下院只取其較窄西庭，避免拿完整殘跡包絡同時當兩棟。Augustus兩個主要exedrae應與Mars廟側並列，不能隨意放院中央；Nerva的模型主院110m，不含後方尚簡化的Porticus absidata，原約120m全體不當矩形硬框。新增南接路從既有Vicus Tuscus南端接出，不能斜穿已確認宅地。

Horrea Agrippiana維持S93的二／三層異文待核，不新增上構。新增住宅避其遺址留地，已確認小片的原要素不動。

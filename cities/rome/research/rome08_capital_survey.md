# 08爭取首都：1849–1871模型調查

接續狀態：兩房型及Braschi—SanPantaleo一區已由導演／主線通過；保留以下首件來源記錄。整城輸入、各區依據及日期拆分見`rome08_capital_whole_basis.md`與`rome08_capital_whole_1871.yaml`；後續河牆另見`rome08_capital_tiber_basis.md`，不倒放1871。末段「首件待審」是原首件當時狀態。

交付範圍是step4來源、形制及新房型sheet；正式旁白與字幕保留。不是整城批准，沒有正式鏡頭或站內秒數。主要結論：1871首都應先看既有教堂、宮殿與住宅中的用途改變，不能一變首都就升起後來的整片Prati、Esquilino、政府大廈或現代河牆。

## 來源層級與已讀範圍

| 編號 | 原始來源／本地檔 | 本件實際讀到什麼；建模用途 |
|---|---|---|
| C01 | [Archivio di Stato di Roma，Catasto Urbano](https://imagoarchiviodistatoroma.cultura.gov.it/Urbano/urbano_intro.php)，及[I documenti](https://imagoarchiviodistatoroma.cultura.gov.it/Urbano/urbano_docs.php)；`imago_urban_intro.html`／`imago_urban_documents.html` | 正文已讀。1818測繪、1:1000原圖、1824啟用；原分割與更新附件必須分開。更新系列延至1871但各圖不覆蓋全rione；紅為新增／修改、黃為拆除，不能把附件題名當每張的精確觀察年。這是後續街坊的首選平面／用途依據，尚未下載完整逐頁brogliardi。 |
| C02 | [1866 Direzione Generale del Censo圖影像](https://www.info.roma.it/pianta_di_roma_1866_direzione_generale_censo.asp)；`censo1866_overview.jpg` | 已取原Zoomify瓦片80張，拼成2400×1813全圖並實看。原圖影像19200×14500；下載與SHA256見`censo1866_tiles_manifest.json`。它是1866圖的第三方數位轉載；以C03的國家檔案圖目互證身份，沒有冒稱轉載站是製圖者。沒有投影或地理配準，不能直接匯入宅界。 |
| C03 | [內政部圖書館，Le sedi romane del Ministero dell'Interno tra il 1871 e il 1931](https://www.interno.gov.it/sites/default/files/2022-09/sediromaneministerointerno_22sett2022.pdf)；`ministry_interior_rome.pdf`／`.txt` | 10.6MB原PDF已實際下載，核讀PDF／印刷11–23頁，實看20、22、23頁。12頁1866全圖，20頁Fig5為1871 Braschi地面平面，22頁Fig6為Corso開闢前Parione II，23頁Fig7是其後狀態；後者不能當1871末景。19–21頁含當年房間／夾層用途。 |
| C04 | [ETH，Letarouilly 1826](https://doi.org/10.3931/e-rara-22241)；`letarouilly1826_manifest.json`及各scan | 已讀館目、IIIF清單，實看前16頁及後續73張非空白縮圖；重讀plate1、2、11、14、22大圖。plate11街屋及plate1–2宮邸為本次兩房型，逐鍵估值與不吻合處見`rome08_capital_housing_basis.md`。未取得任何十九世紀全城樓層分布。 |
| C05 | [市立Trastevere博物館，Lelo／Mazzarelli](https://www.museodiromaintrastevere.it/sites/default/files/storage/original/application/e4597ff5ce9d4575f29a83397029a465.pdf)；`trastevere_lelo_mazzarelli.pdf` | 原5頁PDF已開啟，核讀1–3頁。1860年代兩批Mastai工人住宅、廣場直路；1880年代viale del Re與河岸工程後的拆除，不能提前。不是Mastai逐棟樓層／精確完工年的清冊。 |
| C06 | [市府虛擬城牆館：Porta Pia](https://museovirtualedellemura.romasitounesco.it/en/pin/porta-pia-en/)；`portapia_virtual_museum.html` | 正文已讀：內立面1851後重作；1862–68外立面及雙門內院；1870損害，後來交通開口使城門孤立。採此較細分期，不把旅遊網站1869概括完成說混成另一次完整建造。 |
| C07 | [Museo di Roma：Tuminello，AF3328](https://passatoprossimo.museodiroma.it/la-breccia-di-porta-pia/)；`portapia_tuminello_museoroma.html`／`portapia_tuminello_AF3328.jpg` | 館方三張合成照片、1870、門旁破口，正文與500×133圖均實看。解析度只足判牆線與破口相對位置，不能量出精確缺口寬高。館方稱翌日攝製，其他館頁稱當日；本件只標1870年9月20日事件後影像，不定精確曝光日。 |
| C08 | [ICCD，FB007781／1201350186](https://catalogo.beniculturali.it/detail/PhotographicHeritage/1201350186) | 公開館藏正文已透過網頁讀到，原站檔案直接抓取SSL失敗。Altobelli擺拍不能當突入瞬間；此項只核影像性質，不據其士兵位置復原戰線。與C07來源分開。 |
| C09 | [Museo della Repubblica Romana：Porta San Pancrazio](https://www.museodellarepubblicaromana.it/it/museo/porta_san_pancrazio)；`portasanpancrazio_museum.html` | 官方正文支持1849賈尼科洛防守位置；具體戰損平面尚缺原尺寸圖。Lecchi原影像入口遇循環轉址／SSL，只有搜尋線索，未假稱已看原圖。 |
| C10 | [Camera：Palazzo Montecitorio](https://conoscere.camera.it/lamministrazione/le-sedi-della-camera/palazzo-montecitorio)；`montecitorio_chamber.html` | 正文已讀：1871院內Comotto臨時會廳、11月27日開會；後來Basile翼與後立面另期。不能用今日整體OSM外框當1871宮殿。 |
| C11 | [Quirinale：Sala del Regno d'Italia](https://palazzo.quirinale.it/luoghi/pdf/it/sala-regno-italia.pdf) | 原2頁PDF已在網頁工具讀正文；本地抓取403，未存假PDF。1870–71由教廷宮殿轉王室用途，支持保留殼體改功能。 |
| C12 | [Liseo／Teodori，ISTAT 2016](https://www.istat.it/wp-content/uploads/2016/07/3-B.Liseo_M.Teodori.pdf)；`istat_residents_1871.pdf`／`.txt` | 已讀PDF第2頁表：1871年末居民213,633，來源為市統計局1960彙編；不是所有在場人口、牆內人口或逐棟房屋數。模型不按此數倒算房屋。 |
| C13 | [Tor Vergata／Archivio di Stato，Roma150台伯河工程](https://romacentocinquanta.it/wp/percorso/progetto-e-costruzione-dei-muraglioni-del-tevere/)；`tiber_rome150_history.html` | 網頁工具逾時後直接抓原站HTML核讀：1876交專門辦公室、工程跨十九／二十世紀；檔案含工程前與施工中岸線照片／圖。此題是後續河岸變化，不能畫成1871已全線完成。 |

所有本地來源位於`research/model_reference/rome08_capital/`。`sources_manifest.json`列取得狀態、原URL、大小、SHA256，失敗保留error。沒有把查到的搜尋摘要等同原PDF；研究引用和上屏影像權利另分。

附件版本注意：C03 Fig7雖取自同一Catasto系統，畫面已含Corso Vittorio Emanuele，館刊亦標post1871。不能只憑資料庫「更新至1871」的系列名稱，把附件中較晚的改繪統一判成1871已存在；本件只採Fig6為早期街廓線索。

## 已批准敘事的來源重用

重用FACTS S17、S18、S19、S34、S73、S74，不另改旁白。S73市府[城牆門名單](https://www.comune.roma.it/web/it/notizia/le-dieci-porte-del-futuro-sulle-mura-aureliane.page)及S74文資部門[共和國失守](https://www.sovraintendenzaroma.it/content/leredit%C3%A0-morale-della-repubblica-romana-il-sogno-di-una-rivoluzione-sociale)已重新開正文並保存為`portapia_S73_aurelian.html`／`republic_S74_defeat.html`。S74停守與法軍進佔支持共和失守，不推導全城建築被毀。S19的Garibaldi推動經費仍用原已核說法，不改成設計師或私人出資。

## 城市範圍、街廓與應保留的空地

以下是C02全圖直接圖讀的建模分區，不是數位面積統計；沒有把113年布圖轉標1870。1866與1849之間須按C01逐處核增建，不能整張無條件倒推。

| 區域 | 1849／1866–1871應採格局 | 不可提前的形態 |
|---|---|---|
| Campo Marzio、Corso／Tridente至Pantheon–Navona–Regola | 沿既有街道密建，街廓不規則；教堂、宮殿、內院、街屋混合。由地籍實描各街坊方向與深度，不能全區同一朝向同一戶型。 | Corso Vittorio Emanuele的大穿切；以後期大路為邊重排十九世紀前街廓。 |
| Braschi–San Pantaleo | 1871仍有鄰接宅群和窄路，宮殿先換國家用途。C03 Fig5／Fig6可開始一個有形制與故事依據的連續街坊。 | Fig7的開路後清空；把Palazzo Barracco周圍今天的開敞空間回填1849／1871。 |
| Via Pia–Porta Pia–Castro Pretorio | Via Pia是有據長軸；接近城門以園地、栽植、圍地及少量建築為主，不能照今日密宅。牆與門相接，牆內外關係保留。 | 以整個今日Sallustiano／Castro街網填滿；1870一個破口演成兩側城牆全部消失。 |
| Quirinale–Viminale–Termini | 保留宮殿、教堂、浴場遺構、園圃與當時已有鐵道場地。建築版本按1866圖和年代逐件選，不沿今日站舍外框。 | 今日Termini、後來部會、完成的格網與密度；把既有ViaPia軸或1860年代開發全部說成1871新造。 |
| Esquiline、Lateran、Caelian、Aventine及Palatine | 大片園圃、葡萄園、修院／別墅、古蹟與耕作空間並存；古遺址不是全復原帝都，園地不是未來住宅預留格。 | 後來Esquilino密建、Testaccio街廓、二十世紀考古拆清景觀。 |
| Borgo–Vatican | 完成的新聖彼得、柱廊及Borgo既有密宅保留；不讓1671已站立建物在1871重新升起。 | Via della Conciliazione與現代PiazzaPia車道；將Borgo的spina提早拆空。 |
| Trastevere | Lungara／Lungaretta／S.Francesco a Ripa的既有街坊、修院和工坊；Mastai是1860年代可見新變化，應與老宅共存。山麓至Gianicolo轉疏，園地依圖種植而非空底板。 | 1888 viale del Re／Garibaldi橋和因其拆掉的宅群；1950年代改造後的煙草廠側翼。 |
| Prati與牆外地區 | 圖所覆範圍外不外推密建；有據花園、農地、道路和別墅才建。城牆範圍不等於建成範圍。 | 把後來首都的Prati／Salario住宅、司法宮、Vittoriano或二十世紀紀念碑當1871末景。 |

植栽按用途：別墅／修院花園畫園林，葡萄園／菜圃不能都填喬木；廣場和古蹟前留地不是湖。每個街坊的住宅份額與層數由所選原圖／地籍計數，目前沒有足夠證據提出全城院宅／街屋百分比。三層比較只是兩個樣式，不能當本期樓層上限。

人口工作背景採C12的1871年末居民213,633，與其他資料中約244,000的在場人口口徑分開。沒有以人口除平均戶口造出整城棟數。

## 逐件年代／版本與原生建模處理

| 項目 | 史料支持的分開階段 | 可操作處理／仍是估值之處 |
|---|---|---|
| 1849共和防守與失守 | S34／S74與C09；事件落在Gianicolo、San Pancrazio等已核位置。 | 政治／防守結果有據，不等於住宅全面消失。當年門形及局部戰損要查原圖，不能用1850年代重建門倒放。 |
| Porta Pia | C06的1560年代內門、1851後重作、1862–68外門／內院、1870損傷分開；城牆身份S73。 | 原生parts＋arches可表雙門內院。今日位置可用OSM點2140602057校位；點只作位置，不作完整足跡。尺寸未量出，不先寫假米數。 |
| Porta Pia旁破口 | C07照片留大量城牆，門與破口不同位置。 | 待配準後把牆拆為缺口段與保留段，局部退出。原生線型`lose`介面可支持分段，不需要改引擎；精確寬高未獲，先有界估配再標示意。 |
| 1870年12月洪水 | S19與當年洪水記錄；不是拆屋證據。 | 若模型演洪水，先取已測淹水圖，未知水位不一張大水平面灌全城；住宅與城牆保留。 |
| 1871首都與宮殿用途 | S18、C03、C10、C11。 | Quirinale改王室用途；Montecitorio採舊殼及1871院內Comotto會廳，排除Basile後翼；Braschi按1871平面和複雜夾層專作parts，不套整棟三層型。 |
| 1871住宅／街道 | C01／C02＋C04，同期形制與地籍分開。 | 舊街廓存續，據圖新增的才補。兩型sheet先待審，不能以其展示排列填整城。 |
| 後續高河牆 | S19及C13：1876專門辦公室及跨世紀施工。 | 作首都成立後的來源連結變化提案；1871歷史快照保留施工前岸線。不能把敘事提及的後續工程壓成1871全線完工。 |

`rome08_capital_changes.json`把各史實階段分筆，沒有為模型配額合併事件。此表提供版本選擇，不安排正式片的相機與分期。

## 下一樣區的明確選擇

新房型待批准後，先做**Palazzo Braschi—San Pantaleo的一個連續街坊**。理由是C03同時給1871宮殿平面、用途與開路前街廓，直接呈現「政府遷入教堂與宮殿之城」，不必靠把1880年代的新區提前。Porta Pia是另件城牆／門錨點，不強迫在其稀疏園區填一片住宅來湊街坊。

實施時先把C03 Fig6對應C01 Parione原圖II與更新附件；用原生`pipeline/register.py`至少三個實際共同錨點配準，檢視回描overlay後再描街、院、公共足跡。沒有做自己的經緯度換算。可在名義圖讀誤差內採合理分支，不追逐不存在的逐米／逐戶1871普查；普通住屋的未核內部、屋面及層數逐筆標估值。

## 首件狀態、授權及缺口

已交兩個有來源的新房型sheet；其原生檢查、實看圖片與限制見`rome08_capital_review.md`。房型待導演審核，本件停於此；沒有鋪整城、沒有正式影片修改。

後續街坊仍需：所選Parione原圖／更新圖的地理套合與overlay；普通相鄰宅的地籍樓層／商舖抽樣；Porta Pia雙門及缺口原尺度平面與可量測立面；1849 SanPancrazio原門／戰損原圖；若演洪水與後續河牆，須核已淹範圍及選定一段實際施工年代。這些不阻擋本次房型表審查，會阻擋聲稱本期整城已完成。

影像權利：ETH館藏明示Public Domain Mark，請保留作者、館藏與DOI；InfoRoma轉載、Museo di Roma攝影、內政部所刊檔案圖等本件只作研究，未預設可直接上屏。白模是原生示意量體，不是AI生成圖片。

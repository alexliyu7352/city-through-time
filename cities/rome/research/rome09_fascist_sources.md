# 09｜來源、實際核讀範圍與圖像

原始檔皆在 `model_reference/rome09_fascist/`。下載 URL、檔案大小、SHA-256 和失敗記錄見 `rome09_fascist_source_receipts.json`；`rome09_fascist_fetch_sources.py` 可重用。`[OK]` 表示正文／原圖實際已讀；它不等於圖片有影片使用權。

| ID | 原始來源／本地檔 | 已核內容與用途 |
|---|---|---|
| A01 | [Jacobsen等2021，JFA46:1，36–51，Aarhus原PDF](https://pure.au.dk/ws/portalfiles/portal/261962502/00934690.2020.pdf)，`jacobsen_2021_alessandrino.pdf/.txt` | [OK] 正文印刷36–49及圖4–9；17頁含封面。圖4／5為發掘，圖6為歷期疊圖，圖7為AAR拆前街景，圖8為1933大道施工照片，圖9為1820–24地籍。印刷40頁明示本樣區1932年9月至同年拆除；41–42頁給三／四層通常、二層較少。來源圖已實看，沒有把疊圖所有年代一併建成。 |
| A02 | [Sovrintendenza：Via Alessandrina](https://www.sovraintendenzaroma.it/content/alessandrina-1)，`A02_alessandrina.html/.txt` | [OK] 原文短摘：`tra il 1924 e il 1932`。支持官方概括的拆除區間；1584道路、逾400m及後來街區形成。不是逐地塊拆除日期。 |
| A03 | [Sovrintendenza：La distruzione del Quartiere Alessandrino](https://sovraintendenzaroma.it/node/116417)，`A03_avenue.html/.txt` | [OK] 原文短摘：`Il 28 ottobre 1932`。開通日期與A01交叉核對。圖片說明誤寫1835，原始圖說已標問題，不作日期依據。 |
| B01 | [Senato，ANTIQUORUM HABET：Via della Conciliazione](https://antiquorum-habet.senato.it/index.php/poi/via-della-conciliazione/)，`B01_borgo.html/.txt` | [OK] 展覽正文及同頁列出的原件日期：1922空照、1936年10月30日《Il Messaggero》、1937年多份報紙與1950資料。正文區分1936年10月開工和戰後為1950禧年完善。只讀了展覽正文與列件資訊，未取得／讀完所有報紙原版。 |
| W01 | [Mausoleo delle Fosse Ardeatine：Bombardamenti Alleati di Roma](https://www.mausoleofosseardeatine.it/bombardamenti-alleati-di-roma/)，`W01_bombing.html/.txt` | [OK] 原文短摘：`il 19 luglio 1943`、`il 4 giugno 1944`。只採轟炸日期、San Lorenzo與城市解放，不採死傷數或總轟炸次數。 |
| W02 | [Museo Nazionale della Resistenza：Roma sotto le bombe](https://museonazionaleresistenza.it/story/roma-sotto-le-bombe/)，`W02_resistance.html/.txt` | [OK] Mario di Maio回憶與館方圖片說明，包含via dei Reti少年監所、Verano方向及San Lorenzo鐵路目標。個人口述不當作逐棟損失表；不把其中對話添入已確認旁白。 |
| W03 | [Sovrintendenza：I bombardamenti di San Lorenzo del19 Luglio1943](https://www.sovraintendenzaroma.it/content/i-bombardamenti-di-san-lorenzo-del-19-luglio-1943)，`W03_sovraintendenza.html/.txt` | [OK] 同一官方頁列Basilica、Verano的Quadriportico與Pincetto Vecchio，支持具名局部受創，不支持整個墓地或San Lorenzo夷平。 |
| W04 | [館方所載軍事情報空照](https://museonazionaleresistenza.it/wp-content/uploads/2021/07/Museo-Nazionale-Resistenza-Roma-sotto-le-bombe-07.jpg)，`W04_bombing_photo.jpg` | [OK，實看] 圖片下緣自身標記26/7/43，與網頁「19 luglio」概括圖說不同。保守用作轟炸後空照，不稱7月19日投彈瞬間。白色編號／箭頭無已讀配套圖例，不能直接轉成彈坑或精確倒樓清單。 |
| P01 | [Fondazione CDEC：Spizzichino, Settimia](https://digital-library.cdec.it/cdec-opac/person/detail/person-7695/spizzichino-settimia)，`P01_cdec.html/.txt` | [OK] 原文欄位：`16/10/1943`、`11/09/1945`。被捕與回國兩日期；Auschwitz目的地。沒有精確逮捕門牌或回家路徑。 |
| P02 | [ANED，Triangolo Rosso1999：Settimia Spizzichino](https://deportati.it/triangolorosso/1999/settimia_spizzichino/)，`P02_aned.html/.txt` | [OK] 原文短摘：`ritorno in via della Reginella`、`ha iniziato a testimoniare`。支持街道與作證；不是具名宅界或她的逐字口述。 |
| M01 | [Library of Congress：Town plan of Roma，map47000177](https://www.loc.gov/item/map47000177/)，`loc_1944_metadata.json` | [OK，原站JSON另以HTTP取得] 北／南兩幅的館藏記錄、1944美軍AMS版與1943War Office版關係，IIIF與原檔URL可追。網頁工具403不等於JSON也未讀。 |
| M03/M04 | M01的原生IIIF25%下載：`M03_1944_north.jpg`、`M04_1944_south.jpg` | [OK，兩幅實看] 本份圖面明標`SECOND EDITION - AMS 2`，`Scale1:10,000`。北幅邊注已另取`M03_1944_north_margin.jpg`並實看：FirstGSGSEdition1942、Second1943、WarOffice1943、AMS2-44。另一館藏的1:12,000／第三版不能混作本掃描參數。 |
| M02 | [Archivio di Stato di Roma，Guida al Catasto urbano](https://archiviodistatoroma.cultura.gov.it/wp-content/uploads/2023/12/guida-catasto-urbano-roma_2023-12-22.pdf) | [SEC／未取得原PDF] 搜尋摘要提到更新圖及1931細部計畫；HTTP／TLS失敗，不能冒稱讀過原PDF。A01圖9已有地籍原件節圖，首件不依賴M02。 |

## 實看圖件與性質

- `jacobsen_page-06.jpg`：印刷40頁，拆除／發掘說明；`-07.jpg`：印刷41頁的發掘正射圖4；`-08.jpg`：印刷42頁圖5；`-09.jpg`：印刷43頁疊圖6、拆前街景7；`-10.jpg`：印刷44頁1933照片8；`-11.jpg`：印刷45頁地籍9及出土物10。均由本地原PDF以`pdftoppm`輸出，未重繪成假原圖。
- A01圖6同時含古代廣場、1824地籍和現代道路／發掘框，必須逐層判別；圖9是1820–24地籍。二者皆不能整張不分年代地充作1932快照。
- M03/M04為兩幅原圖；綠色樹園、灰建成區、黑色重點建築與道路／鐵路要按原圖圖例讀，不以全台面背景皆建成。原圖格網註明近似，正式落位仍要`pipeline/register.py`和控制點殘差。

## 權利與未採資料

A01是CC BY-NC-ND4.0文章，歷史照片另有AAR／Alinari署名；B01報紙、W04軍情照片未取得各原權利條款，研究可查不等於影片可直接播。M01館藏頁記其地圖可用／再用，應署Library of Congress, Geography and Map Division；如真正上屏仍由主代理留存具體權利頁。這次影片內只產原生白模，來源圖均未貼上影片。

SIMART的相應照片記錄找到但頁面無可讀正文，未以搜尋摘要補造元資料。Roma Sparita／社群轉載／房產廣告只作線索，未用其層數、年代或現代街廓支撐本期模型。未使用影視佈景或AI想像圖：已有本地考古、地籍、原街景，無須越過優先順序。

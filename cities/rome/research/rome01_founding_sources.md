# 建城期來源核讀與可用性

沿用F01–F08及NF01–NF04的原始編號，分別對應 [founding_source_index.json](founding_source_index.json) 與 [founding_next_sources.json](founding_next_sources.json)。本輪重新網搜、開原文及實看原圖；沒有把搜尋摘要或書評當成已讀1951原報告。新檔案雜湊見 [assets](rome01_founding_assets.json)。圖片均研究用，未取得本片上屏影像授權。

| ID | 原始入口／實際核讀範圍 | 本輪使用與限制 |
|---|---|---|
| F01 | [Pensabene2009原刊頁](https://www.persee.fr/doc/efr_0223-5099_2009_act_425_1_9807)；正文p.5、原始p.6圖1與p.7圖2逐圖看；既有p.8時序 | 西南位置、多期序列、北屋相關填土年代；圖1／2混合不同期，不是四屋同期清冊。PDF端點未得，使用公開原頁影像，未稱已讀原PDF |
| F02 | [PArCo官方物件頁](https://colosseo.it/opere/casa-romuli-modellino-di-capanna-e-plastico-del-villaggio/)正文；[Davico1950單屋照片](https://colosseo.it/sito/wp-content/uploads/2020/10/Modellino-della-capanna-A-del-Germalo-1024x683.jpg)實看 | 兩柱小門廊、短邊入口、主體柱洞／面積與具名復原。短摘只留「un piccolo portico sostenuto da due pali」。整村大部自由復原不作同期配置 |
| F03 | [PArCo Palatium官方PDF](https://colosseo.it/sito/wp-content/uploads/2021/02/Abitare-sul-PALATINO.pdf)，現存原PDF與未改嵌入頁1實看 | 山丘占居、單室及門廊、官方位置圖；不是單年地籍。本輪web取PDF逾時，未冒稱新下載成功；本地原PDF可核，其文字層只有換頁符 |
| F04 | [官方Coarelli平剖／復原圖](https://colosseo.it/sito/wp-content/uploads/2020/11/CAPANNA_COARELLI_GUIDA.jpg)原1237×2390px實看 | 柱洞、入口、門廊及5m尺；原書版次／頁未明，不能叫它上部實測圖 |
| F06 | [Guidi2019／2020作者存檔原PDF](https://iris.uniroma3.it/retrieve/e397d80e-568c-b0de-e053-6605fe0a1c76/Origini%20-%20Guidi.pdf)，本輪web成功開原19頁PDF，印刷161–164核讀 | 形成與統合涉及Palatine之外、學說多樣；不把原城市面積概數轉為753年精確外界 |
| F07 | [Stassi2022原書](https://www.editricesapienza.it/sites/default/files/6189_Stassi_Vol_Costruire_violare_placare.pdf)，沿既有已核UT5／UT6摘錄 | 只支持北坡局部牆和重建；這一來源未新增西南防線，亦未重讀490頁全文 |
| NF01 | [Damiani／Roma官方Fidene PDF](https://sovraintendenzaroma.it/sites/default/files/storage/original/application/a595adff7106a6074c58fcf06d66e3f0.pdf)，本地原2頁、p.2正文與剖視圖 | 上部比較；原文明說復原牆「un'altezza massima di m 2,5」。0.40m復原牆與0.30m古牆分開。正文另說門廊未重建，不能借作門廊已復原證據。本輪web取PDF逾時，保留既有原檔讀取 |
| NF02 | [市府Fidene條目](https://sovraintendenzaroma.it/i_luoghi/roma_antica/monumenti/casa_protostorica_di_fidene)，本輪web成功開正文 | 約850–800BCE、較大矩形屋與四內柱，僅限定比較距離，不搬平面／柱數 |
| NF03 | [DAR Casa Romuli](https://www.digitalaugustanrome.org/records/casa-romuli-palatium/)，本輪web與直接HTTP均讀完整正文 | 古典文獻保存聖屋與出土hut分開。短摘「the location of the Casa Romuli cannot be fixed」。DAR點號不作住宅足跡 |
| NF04 | [OSM1860921](https://www.openstreetmap.org/relation/1860921)，重用本地原MultiLineString四角 | 現代遺構控制，不推VIII世紀神廟；ODbL，© OpenStreetMap contributors。四角來自同一件神廟，殘差不能當多個獨立測地控制驗證 |

## 本輪來源檔與取用狀態

- `model_reference/rome01_founding/rome01_founding_dar_casa_romuli.html`：重新直接抓取成功。
- `model_reference/rome01_founding/rome01_founding_pensabene_p6_large.jpg`：請求寬3474端點，伺服器仍回1737×2162原頁；與舊頁雜湊相同。**不是新的高解析掃描。**
- 官方物件頁在web已開正文；直接curl遭TLS錯誤，沒有把失敗檔列為取得。物件頁本地原存檔與圖片保留可核。
- 1951 Puglisi／Davico原篇仍未取得。Cambridge書評／書目與二手引文只作追索線索，沒有補出原報告精確高度或A＝3的文字表。
- `rome01_founding_*grid.png`與`registration_review.jpg`是從上述原頁生成的研究讀圖，藍色格網／彩色點及文字是本輪註記，不是考古原刊標示。

## 原刊與製作判斷分開

本輪新結論是可核的**工作決策**：形制選A與門廊，空間選Cermalus核心、四角分支的有界示意，其他跨期痕跡不並立。23°北向原因、房屋上部實高、完整村界與同期住宅比例仍未知；這些限制都不藏在「示意」一詞內。沒有使用電影／電視布景，也沒有把博物館自由復原村落當考古地圖。

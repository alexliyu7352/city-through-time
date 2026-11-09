# 舊聖彼得博物館頁：來源與模型界線

## 選用的原生模型

`museum/old_st_peters.yaml` → canonical `city.yaml` 的 `people_return` → 兩個既有地標的原生`pieces`：`core = kind: parts / id: rome06_medieval_old_stpeter`（模板`rome07_formal_oldstpeter_lifecycle`），`atrium = kind: parts / id: rome06_medieval_stpeter_atrium`。這是800年前後沿用的五廊／橫廳／西後殿核心和圖式前院；不是1506全部附件的復原。四世紀同址 `another_centre / rome04_old_stpeter` 只有40筆且無label，800版本44筆有可用子件label，採後者而不改模型。

前院的原址`12.455568134748257,41.902128554860646`、方向84°均沿canonical。模板basis仍留早期`raised`說明，正式實例經native checked後為`site:cut`，本頁保留實際實例設定。`pieces`把兩個原有量體依原座標在水平博物館地坪展示，不重新設計它們的高程／尺寸。前院有三條6m高、規則12跨、平拱式的覆廊示意，約66／68×70m與6m高均圖像估值，整件estimated。core正面牆仍無門洞，頁面明示此省略，不用AI硬加新門。1506是新建與拆舊的起點，舊東中殿餘部依Senato說明續用至1609，不稱當年全拆完。

只讀的原生 `museum.find_landmark/build_model` 合成47筆：`core/nave_east:24 / core/nave_west:16 / core/transept:2 / core/apse:2 / atrium:3`。`exaggeration:1`、地坪0下，記錄底部−3m是埋地裙基；最高38.053m，並非直接量得的歷史高度。既有模型名義32.54m檐高、25°坡屋面，實際幾何頂略高於Donadei轉述的37.9m；保留原模型，不為本頁改尺。

分件按first-match：屋面8筆estimated；窗28筆estimated；`main`兩段長殿牆6筆sourced；橫廳牆1筆sourced；後殿牆1筆sourced；`atrium`3筆estimated。sourced表示平面／量體存在有據，註記仍揭露牆厚、立面和尺寸分支中的估值。兩段長殿是影片逐期拆建的接口，不主張800年有中隔牆。

## 實際核讀與轉引

- [Vatican State, Storia](https://www.vaticanstate.va/it/stato-e-governo/storia.html)：本輪重開官方正文。支持4世紀、五廊／橫廳／後殿、前院及朝聖背景；其概述不能給每次前院改建定年。
- [Guidobaldi 2013, Leggere l'architettura costantiniana](https://www.treccani.it/enciclopedia/leggere-l-architettura-costantiniana_%28Enciclopedia-Costantiniana%29/)：核讀本機LA06之Vatican段及註21。內部長體約91m、總內寬約64m、中殿約23m、橫廳約18m；這些是他轉引Krautheimer的分支。66m外寬含估計牆厚。**未直接讀Krautheimer的CBCR原卷**。
- [Silvia Donadei 2021博士論文](https://amsdottorato.unibo.it/id/eprint/9900/1/Donadei_Silvia_tesi.pdf)：本機LA13印刷171–174頁核讀；記五廊、66m寬、37.9m高、90×17m橫廳、墓地用途及中世紀增改，173頁轉載Brandenburg／Krautheimer復原。其長體87m與Guidobaldi91m不混平均；模型沿用既有91m分支。**未讀整部論文、Brandenburg2004或Krautheimer1986原書**。
- [Senato, San Pietro in Vaticano](https://antiquorum-habet.senato.it/index.php/section/section_61_it/)：本輪重開展覽正文，核Alfarano／Bonifacio1590平面、舊新並存、舊中殿使用至1609。1590疊圖不是所有畫上物件同時存在的證明，也不是800年院落測繪。**未直接讀Alfarano全部手稿／1914全文**。
- [Federica Goffi 2010](https://vtechworks.lib.vt.edu/bitstream/handle/10919/29312/GOFFI_F_D_2010_f1.pdf)：只核本機R45之相關圖錄及Alfarano／Grimaldi摘段。圖錄引Grimaldi《Descrizione della basilica antica di S. Pietro in Vaticano》、Barb. lat.2733、Reto Niggl1972編本，及Tasselli–Grimaldi圖冊。**未直接讀Grimaldi手稿、1972整本或Goffi全文**；只支持記錄來源身分，不挪用未核細節。
- [Robert Coates-Stephens 1995](https://discovery.ucl.ac.uk/id/eprint/10099990/)：核本機M18中前院676鋪地、Hadrian I側廊屋樑／屋頂維修與相關院廊段落；與既有 `rome06_medieval_whole_basis.md` 的800版本依據一致。沒有800精確前院尺寸、每根廊柱或附屬建築完整清冊。
- [Vatican, Braccio di Carlo Magno](https://www.vatican.va/content/vatican/it/ra/braccio-carlo-magno.html)：沿FACTS S12既核正文，800年聖誕加冕；本輪未重開其全文。後世查理曼騎馬像不入800場景。
- [Fabbrica, The Basilica](https://www.basilicasanpietro.va/en/san-pietro/the-basilica)及[施工日期FAQ](https://www.basilicasanpietro.va/it/faq/quando-e-stata-costruita-la-basilica-di-san-pietro)：本輪重開正文，1506首石／1626完成與彼得墓共同中心，支持新舊頁互提。

## 相機與場景

真records的保守旋轉包圍框（x、y、z，m）為`[-75.739,120.590] / [-3,38.053] / [-51.752,46.699]`。取`at_m:[22.425,2.527,18]`（east,north,up），三view az120/225/330、el25、fov36。以每個包圍角點投影到相機right/up方向，逐點要求`d >= dot(point-target,eyeDirection) + max(abs(up)/tan18°, abs(right)/(tan18°×16/9))`；必要距離291.644/279.715/252.111m，加至少10%餘量後選330/315/285m。各方向球面夾角超過50°。東南斜角讓四側廊屋面與前院關係可讀，沒有以假入口裝飾掩蓋原模型省略。原生頁面在手機保持16:9參考圖完整框幅；最後仍由root實看desktop／phone。

三張場景都定800年前後、完成使用中的舊殿及示意前院，不畫施工。前院是通行／朝聖空間；側後有墓葬、附屬宗教建築與梵蒂岡坡地，不能一律變成空曠草原或後世Borgo。三條院廊按原量體保留，不加第四條廊、鐘樓／旁殿或入口門洞。場景卡其餘採低資訊地表和局部裁出畫框的環境，不藉AI補成假裝已測繪的完整建築群。若加上現成前院仍不能辨認，退回root的模型／選頁判斷，不偷偷重建立面。

未跑GPU、生成圖片或正式museum build；待root檢視真高度白模是否足以辨認，才做living ref/gen/sheet/adopt及公開圖檢查。

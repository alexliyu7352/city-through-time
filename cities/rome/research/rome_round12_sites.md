# Rome round 12：塔、四座今日灰樓與舊位方尖碑

依 `rome_round12_handoff.md` 查核。此件只交來源與建模界線；未改候選、正式 YAML、共享程式或 git index，未編譯。新來源以原頁／原論文核讀；既有座標與示意尺度保留其原本的不確定性。

## 本輪可採結論

| 對象 | 當期判斷 | 本輪處理 |
|---|---|---|
| Torrione di Niccolò V，約 41.9038,12.4567 | 約1450年代已建，1671與其後存在 | 加同址塔。總高20m、直徑約38m；兩者不是60m高的放大塔。三段高度與收分另明標估值。 |
| 灰樓 41.90371,12.45728，10.6m | 今日Swiss Guards兵營主要為19／20世紀；800與1671無同址早期完整建築輪廓 | 保留今日灰樓，不以兵營或猜測前身填補。 |
| 灰樓 41.90340,12.45363，10.3m | 鄰近Zecca確於1671運作；目前證據不足以給該灰樓足跡的1671輪廓 | 保留今日灰樓。不能把1776改建後的整個今日包絡／凹院倒填成1671鑄幣廠。 |
| 灰樓 41.89803,12.47661，22.3m | 萬神殿南、Agrippa浴場北界／Basilica Neptuni附近；AD14與113年的具體同點上構未定 | 保留今日灰樓，不倒填Hadrian期長廳，也不拉大既有浴場。 |
| 灰樓 41.89490,12.47577，13.7m | DAR的AD14圖落Pompey雙園帶的南帶，不是覆頂柱廊 | 保留今日灰樓，不在有據園庭上加屋。113同點新上構亦未獲證。 |
| 舊聖彼得南側方尖碑 | Caligula時期運至Vatican circus，1586才移廣場 | 330與800加入既有舊位碑規格，再銜接 `made_again` 的 `rome07_formal_obelisk_old`；保持單一物件的時代交接。 |

## 1. Torrione di Niccolò V

### 身分、年代與形制

- **[OK，原學術全文]** Gerardo de Simone，〈Niccolò V committente. Tra dignitas ecclesiae e magnificentia principis〉，2015，印刷p75、fig.10：[作者公開原文](https://www.academia.edu/19805326/Niccol%C3%B2_V_committente_Tra_dignitas_ecclesiae_e_magnificentia_principis_2015)。短摘：`eretto dal Rossellino nel 1452`；`fu arrestato a trenta a seguito di un crollo nel 1454`。圖說1452–54。原文所述100 cubiti是未完成計畫，不能用來復原一座高塔；30 cubiti也不在此未核單位下直接換公尺。
- **[OK，原學術全文]** Lucina Vattuone，〈Mura e torri a Roma fra Tardo Antico e Medioevo: sistemi costruttivi e morfologia urbana〉，印刷pp75–77、fig.5：[原文](https://www.academia.edu/28768338/Mura_e_torri_a_Roma_fra_Tardo_Antico_e_Medioevo_sistemi_costruttivi_e_morfologia_urbana)。形制短摘：`basamento scarpato`；`l’ordine di fuoco con le cannoniere`；`coronamento di forma cilindrica`。支持斜收基座、砲層、上部圓柱冠部三段，非一般細長鐘塔。圖5引用Frutaz1956的Giordani照片。預定連向Castel Sant’Angelo的長牆沒有建成，不由此新增一段假牆。
- **[OK，官方現況身分]** [Vatican News，2021-06-11](https://www.vaticannews.va/it/vaticano/news/2021-06/ior-bilancio-2020-rapporto-annuale.html)的Vatican Media照片標作 `Il Torrione di Niccolò V, sede dello Ior`；[Vatican Museums官方2023國家平面圖](https://m.museivaticani.va/content/dam/museivaticani/pdf/eventi_novita/notizie/2023/144_mappa_stato_vaticano.pdf)第32號為IOR，同一圓塔在宮殿北東側。未把教堂南側Porta Cavalleggeri的另一座同名塔，或含Cappella Niccolina的方塔混入。

### 地理與保守尺寸

**[OK，OSM原資料；只負責現況位置／輪廓／高度]** [OSM way50981047](https://www.openstreetmap.org/way/50981047)，[原XML](https://api.openstreetmap.org/api/0.6/way/50981047/full)：標籤 `name=Torre di Nicolo V`、`man_made=tower`、`tower:type=defensive`、`height=20`。ODbL 1.0。資料於本輪直接讀取，未冒稱高度是考古測量。

- 全輪廓約37.1×42.6m，南側包含與宮殿接合的尖角；**42.6m不是主圓體直徑**。
- 對圓弧18點投影至UTM32633後擬圓，中心約 **[12.456655,41.903792]**，直徑37.81m。這是現況OSM幾何讀值，擬合很整齊只反映資料本身近圓，不代表歷史或測地精度；工作尺寸取 **38m**。與交接約點[12.4567,41.9038]為同址，不另挪塔。
- 最小可落地模型：總高 **20m、exaggeration=1**；斜收基座8m、砲層6m、上部圓柱冠部6m，三段合20m。基座直徑38m向上收至35m；其餘兩段直徑35m。**8/6/6m及35m是為呈現來源三段形制的工作估值，非文獻量測**。可改較簡化的同高圓體，但不能因20m今日塔尚有局部露出而抬高。
- 平頂／小幅水平分界即可；不用無據尖頂、滿圈高齒堞或現代IOR門窗逐格復刻。三段共用同一真實落地基準，不加遮樓平台。

本輪的1506既存背景、1564、1671與後期可採同址保守塔體；不宣稱每期門窗和改用IOR後的室內都相同。800不能提前加入1450年代塔。

## 2. 41.90371,12.45728：Swiss Guards兵營

**[OK，現況定位]** [OSM way661986023](https://www.openstreetmap.org/way/661986023)為 `Caserma degli Svizzeri`，外包約12.456935–12.457582、41.903360–41.903957，目標在此範圍。上述官方國家平面圖亦分第36號軍官樓、第37號兵營。

**[OK，管理／修繕機構原件]** [衛隊官方網站的義大利文兵營修繕手冊](https://schweizergarde.ch/fileadmin/files/Kasernenstiftung/SPENDENBROSCHUERE_SCHWEIZERGARDE_I.pdf)，印刷p14、PDF第14頁。短摘：`sono stati costruiti nella metà del XIX secolo`；`La loro forma risale al 1932`。內文區分19世紀長翼／原憲兵樓1932改用兵營，與庭院另一側1929–1932新建的辦公／軍官住房；[官方2024年報p45](https://schweizergarde.ch/fileadmin/files/Paepstliche_Schweizergarde/Jahresberichte/2025/Jahresbericht2024_i_01.pdf)亦確認兵營樓為19世紀。

**限制／保留理由：** 此證明今日樓不能直接當800或1671兵營；不等於證明當時整片地都沒有建築。既有Leonine／Passetto來源只約束附近牆線，不能替這棟10.6m灰樓補出800年的屋頂。故各前期保留灰樓。

## 3. 41.90340,12.45363：Zecca附近

- **[OK，官方平面圖已實看]** 上述Vatican Museums 2023單頁圖第22號 `PALAZZINA ZECCA` 位於聖彼得北、Fontana delle Torri附近，是本點附近的真實功能建築。
- **[OK，IPZS出版的原學術研究]** Micaela Antonucci，*Palazzo della Zecca in Banchi*，Istituto Poligrafico e Zecca dello Stato，2008，pp102–105：[原書公開全文](https://www.academia.edu/94008463/Palazzo_della_Zecca_in_Banchi)。1634年Belvedere的palazzino作鑄幣廠，1657擴建後暫遷設備；1665年7月起回復為唯一鑄幣廠。fig.100為現況，fig.104為約19世紀初的平面／部分剖面，**後圖不能直接充作1671原貌**。
- **[OK，原始帳目轉錄]** Leandro Ozzola，*L’arte alla corte di Alessandro VII*，1908，Cap.X，印刷pp63–64／PDF零起算p64–65：[原PDF](https://upload.wikimedia.org/wikipedia/commons/1/12/L%27arte_alla_corte_di_Alessandro_VII_%28IA_larteallacortedi00ozzo%29.pdf)。核讀1661年2月–1665年6月24日鑄幣水機工程及1664新鑄幣廠石作帳。短摘：`posta dietro a S. Pietro`。支持1665工程，不提供本點逐室輪廓與樓高。
- **[OK，原研究的後期變化]** Carlo Pietrangeli，1994年 *Strenna dei Romanisti*，pp413–417，尤其p414：[原PDF](https://www.gruppodeiromanisti.it/wp-content/uploads/2014/10/1994-parte-2-pp.-186-540.pdf)。短摘：`Zecca costruita nel 1665`；`rifatta da Pio VI nel 1776`。作者以Roberti原畫觀察本區；近旁服務建築也經後期拆改。

現況[OSM way44529511](https://www.openstreetmap.org/way/44529511)是此處連續服務建築輪廓，但目標約點落其凹口外約6m，OSM又未逐翼標名，不能把整片包絡當成原Zecca。既有Falda1667原圖 `model_reference/rome07_renaissance/R09_falda1667.jpg`確有殿北服務屋群；本輪實看，仍未得到能辨每翼、排除1776與後期改動的1671地面足跡。

**處理：** 1671「本區有鑄幣廠」成立；「這棟10.3m灰樓的完整足跡／上構已可復原」不成立。整合者已採本輪保留灰樓，不畫猜測Zecca，也不以附近噴泉／舊牆作遮擋體塊。

## 4. 41.89803,12.47661：萬神殿南

**[OK，官方位置與概述]** [Roma Capitale，Basilica di Nettuno](https://www.turismoroma.it/it/luoghi/basilica-di-nettuno)提供公眾坐標[12.476740,41.898213]、80年火災後Hadrian重建及16世紀Accademia覆蓋的概述。目標較其解說點南約20m，不能把解說點當完整足跡。

**[OK，原學術地圖的證據界線]** [DAR，Stoa of Poseidon](https://www.digitalaugustanrome.org/records/stoa-of-poseidon/)區分Agrippa的stoa與南側Hadrian期Basilica Neptuni；現存遺構全為2世紀，Agrippan同址前身的範圍與認定有爭論。[DAR，Thermae Agrippa](https://www.digitalaugustanrome.org/records/thermae-agrippa/)又明示浴場北端範圍及性質未清，文藝復興圖的房間布局互異。短摘：`the extent and nature of the northernmost portion ... remains elusive`（省略號為摘錄省字）。

**處理：** AD14與113均不按Hadrian現形加長廳；亦不能用「公共浴場附近」推出正好在這棟灰樓下有一座22m高建築。這是具體上構未明，並非聲稱古時此地全空。保留灰樓，不擴既有 `agrippa_baths`，不加平台。

## 5. 41.89490,12.47577：Pompey園庭

**[OK，原學術地圖／來源已核]** [DAR，Porticus Pompeianae](https://www.digitalaugustanrome.org/records/porticus-pompeianae/)說北、南、東有覆頂廊，南廊外有商店，中部庭園180×135m並有兩條長方園帶。短摘：`two long, parallel rectangles`。不能把南側商店移到園庭中央。

重用既有 `model_reference/ad14_public_dar_campus_z17.png` 與 `ad14_public_dar_campus_sources.json` 的EPSG3857變換，不新設錨。目標換算像素 **(330.04,667.77)**，實看在南半長方園帶內；南覆頂廊在其南方。既有 `rome02_pompey_refine_sources.md`／`rome02_pompey_refine_controls.json`辨東側Curia，亦不把本點當Curia。絕對位置沿原研究約5–10m工作不確定性。

**處理：** AD14沒有在此加屋的理由。113的Domitian修復也沒有給此點新的屋身／高度，故保留13.7m今日灰樓；維持有據園庭用途，不新增遮樓柱廊或樹牆。

## 6. 方尖碑：330 → 800 → made_again → 1586

### 已有來源與可採年代

**[OK，官方原頁重讀]** [Vatican，Obelisk](https://www.vatican.va/content/vatican/en/ra/obelisco.html)：Caligula（37–41 AD）將碑運至其私人circus，1586才移至廣場。現碑身25.36m；現底座8.25m是Fontana新座，**不能倒填到330／800**。短摘：`In 1586`；`the obelisk was moved to the center of the square`。舊頂青銅球在搬移時換成十字架；早期碑不可加1586十字架或1723飾物。

**[OK，公立原件展覽／刻圖]** [Senato，San Pietro in Vaticano](https://antiquorum-habet.senato.it/index.php/section/section_61_it/)展示來源R02/R03及Fontana1590搬遷原著、Gamucci1580圖；原文直接稱搬移前位於殿側。短摘：`sito, fino al 1586, sul fianco della basilica`。同頁舊／新大殿與circo疊圖亦支持舊殿南側的相對關係。

**37單年界線：** 本輪讀到的梵蒂岡primary頁給Caligula37–41在位範圍，未單獨證明搬運恰在37年。330／800有碑不受此差異影響；本輪不加37年的精確字幕或全新事件，不改使用者旁白。`37–1586`可作交接題名，來源陳述保守寫「Caligula時期至1586」。

### 直接重用現有規格

`rome07_formal_spec.yaml` 的 `rome07_formal_obelisk_old`，以及 `rome_round11b_city_draft.yaml` 約590236行，既存參數：

```yaml
kind: column
lon: 12.45427
lat: 41.9014
section: rect
w_m: 2.5
h_m: 25.5
taper: 0.65
pedestal: {w_m: 5, h_m: 5}
exaggeration: 1
```

位置、寬、5m舊座原basis已明列R02/R03/S48的示意估值，不是新發現的測量；25.5m是既有25.36m的概括版本。此輪重用可保持碑身與舊位一致，不擅自更換既有1586搬運線或現座高度。不可把舊側位搬到今天廣場中央，也不把碑放到新大殿北側。

接入界線：330／800各期在舊側位承載同一根碑；跨期原生交接時前一期實體讓位。到 `made_again` 沿用現有 `rome07_formal_obelisk_old`，不再並列一根新的舊位碑。1586保留既有 `obelisk_relocation` lose與新位 `rome07_renaissance_obelisk` 的stage，既有路線[12.45427,41.9014]→[12.4573,41.90225]仍是搬遷示意，不增機具或精確軌跡宣稱。

## 停止界線

塔與方尖碑已足以按來源完成本輪畫面。四處灰樓的保留均有上述具體理由；第二處不是「當時沒樓」，而是已知Zecca存在但該點1671輪廓不足。沒有以搜尋不到來源聲稱空地，也沒有為遮今日灰樓新增不實幾何。第三方圖像／照片僅作研究，未授權直接上屏。

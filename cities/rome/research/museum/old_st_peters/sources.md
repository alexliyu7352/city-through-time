# 舊聖彼得博物館頁：來源與模型界線

## 展示的建築與詳細模型

`museum/old_st_peters.yaml` 的 `people_return` 頁保留兩個電影地標的原址與84°方向：`core = rome06_medieval_old_stpeter`（`rome07_formal_oldstpeter_lifecycle`）及 `atrium = rome06_medieval_stpeter_atrium`。頁面以 `exaggeration: 1` 在水平地坪展示800年前後沿用的五廊、橫廳、西後殿核心及示意前院；不是1506年全部附屬建築的復原。電影與城市資料未改。

頁面現用 `tools/blender/basilica.py` 與 `atrium.py` 的詳細外觀，不能再以電影的47筆原生 primitives 描述展館幾何。已逐段核讀兩模組的 `DEFAULT`、`from_landmark` 和實際建造路徑，並實看提供的 `five_pages.jpg` 模型比較圖。長殿兩段先合建、再依電影分段切開，窗列、瓦垄和檐線連續，並無800年的橫向中隔牆。

- **來源支持的核心尺度**：Guidobaldi註21轉引Krautheimer，長體內長近91m、全內寬近64m、中殿寬逾23m；模型外寬66m包含估計牆厚，並將91m分成57.5／33.5m。橫廳採90×18m；Donadei另述90×17m，長體87m、總長123m及高37.9m，保留口徑差異，不平均。32.54m中殿檐高、16m外側廊牆高、各側廊10.75m分寬、20.8m橫廳牆高與23m後殿外徑均含原模型估配。
- **`basilica`補出的估值**：中殿／橫廳25°坡頂與後殿半錐頂沿原地標；雙側廊分別有14°單坡頂，內側廊高於外側，階差設定1.6m。屋面厚0.3m、牆深1.2m、瓦垄間距0.6m、窗寬占柱跨0.5、牆腳0.62m和檐口0.8m都是製作估值。4.5m窗跨由完成預設的原地標傳入，仍非逐窗考古證據。正面有五個平頂門洞，中央門3.4×5.2m、側門按0.7縮放；三個中殿正面高窗、帶框拱窗、外側廊及橫廳窗，連同窗位、數量、洞深、框線和門楣均為規則化估值。被相鄰房體遮住的窗不造。內部柱列、屋架、祭壇和墓室未建。
- **四面前院**：`atrium.from_landmark` 讀三條電影廊體的邊界、3.5m廊深、6m頂高和12跨基數；頁面明定四面有廊、三面有外牆，靠大殿的一面無獨立背牆並延長0.5m接上正面。從原三條廊體外緣推得 `outer_m: [-34.75, 34.75, -36.75, 35]`，加延長後外包約69.5×72.25m，頁面取整為約70×72m，不稱66×70m精測院落。前側拱門與背側中門對位會調整中央柱跨，不承諾每面都是恰好12跨。
- **`atrium`補出的估值**：20°向院內落水的瓦頂、0.6m出檐、0.25m屋面厚、0.8m外牆、0.26m柱半徑、0.6×0.55m梁、0.3m廊地高差、3.6×4.7m院門與瓦垄、柱頭、門框、牆腳、檐口、鋪地等均是估配。四面廊的存在與逐件800年造型是不同證據層級；不把細模的通用柱頭或屋頂斷面升格為實測。

分件依物件名稱first-match，六組全部estimated。`main`、`transept`、`apse`雖有據的核心布局與主要尺度，但相同物件也含估配牆高、牆腳或檐線，現有labels無法將這些面分開，故不將整件染為有據；note仍保留哪些布局與尺度有來源。詳細模型的物件數與頂點外包應由正式museum build回報，舊生成器的記錄數與38.053m包圍高度不當作詳細模型的檢查結果。

## 實際核讀與轉引

- [Vatican State, Storia](https://www.vaticanstate.va/it/stato-e-governo/storia.html)：本輪重開官方正文，支持4世紀、五廊／橫廳／後殿、四面前院與朝聖背景；官方概述不是800年前院的逐期測繪。
- [Guidobaldi 2013, Leggere l'architettura costantiniana](https://www.treccani.it/enciclopedia/leggere-l-architettura-costantiniana_%28Enciclopedia-Costantiniana%29/)：本輪重讀本機 `model_reference/rome04_lateantique/LA06_constantinian.txt` 的梵蒂岡段和註21。除了上述尺寸，正文記高窗近5m高、約3.2m寬；細模並非按此逐窗復原。**未直接讀Krautheimer的CBCR原卷**。
- [Silvia Donadei 2021博士論文](https://amsdottorato.unibo.it/id/eprint/9900/1/Donadei_Silvia_tesi.pdf)：本輪重讀本機 `LA13_oldpeter_thesis.txt` 印刷171–174頁；支持五廊、磚造、墓葬功能及中世紀核心延續，173頁轉載Brandenburg／Krautheimer復原。**未讀整部論文或其引用原書**。
- [Senato, San Pietro in Vaticano](https://antiquorum-habet.senato.it/index.php/section/section_61_it/)：本輪重開展覽正文。Alfarano／Bonifacio1590疊圖與舊中殿使用至1609有明文。1590圖不是800年每件附件同時存在的證明。**未讀Alfarano全部手稿或1914全文**。
- [Federica Goffi 2010](https://vtechworks.lib.vt.edu/bitstream/handle/10919/29312/GOFFI_F_D_2010_f1.pdf)：沿用前輪核讀本機R45之Alfarano／Grimaldi摘段及圖錄，**本輪未重讀全文，亦未直接讀Grimaldi手稿或1972整本**。只用於說明圖記的來源身分。
- [Robert Coates-Stephens 1995](https://discovery.ucl.ac.uk/id/eprint/10099990/)：本輪重讀本機 `model_reference/rome06_medieval/M18_coates_stephens1995.txt` 關於676鋪前院、Hadrian I側廊屋樑／屋頂維修及quadriporticus瓦頂、鉛材的段落。沒有800年的每根廊柱、精確院界或完整附屬建築清冊。
- [Vatican, Braccio di Carlo Magno](https://www.vatican.va/content/vatican/it/ra/braccio-carlo-magno.html)：本輪重開，核800年聖誕在聖彼得加冕；同頁後世騎馬像不放入800場景。
- [Fabbrica, The Basilica](https://www.basilicasanpietro.va/en/san-pietro/the-basilica)與[施工日期FAQ](https://www.basilicasanpietro.va/it/faq/quando-e-stata-costruita-la-basilica-di-san-pietro)：本輪重開，核1506奠基、1626完成與彼得墓共同中心，支持新舊頁互提。

## 相機與三張場景卡

沿用已批准三機位：`at_m: [22.425, 2.527, 18]`，az120／225／330、el25、fov36、距離330／315／285m。原生成器外包與角點距離計算只記錄原機位的來由，不代替新細模的ref、sheet或desktop／phone實看。

三卡定800年前後的完成使用狀態。保留模型的四面有頂柱廊、前牆院門、大殿五個入口、帶框拱窗、橫廳窗和內高外低的雙側廊；不可再要求保留空白正面、只畫三廊或禁止已有坡屋面。畫面只為現有幾何附上材料與低資訊環境，不另造鐘樓、旁殿、入口附加亭或精測周邊。墓葬／宗教設施的存在不等於每座800年外觀已知；848–852年Leonine牆及後世宮殿、Borgo街網不倒填。

本筆記的查證工作只處理文字與場景卡。後續已由原生流程完成詳細模型建置、三張新圖的ref／gen／sheet／adopt、livingcheck及桌面／手機shots；配準、物件分配與手機構圖均已實看。

# Colosseum：80 CE 博物館頁來源與模型限制

本件只寫 `museum/colosseum.yaml`、本筆記及三張場景卡。沿用 canonical
`imperial_height` 的 `ring / id: colosseum`，沒有修改城市、劇本、影片、共用程式或歷史模型。
本頁是 **80 年啟用時的概括形制**，不是聲稱所有後期構造已於 80 年完工的精密復原。

## 已讀來源與未讀界線

|頁內代碼|本輪實際閱讀|能支持的範圍／限制|
|---|---|---|
|S06|[KCL Art of Making：Colosseum](https://aofm-os.kdl.kcl.ac.uk/explore/monuments/113/) 正文，2026-11-09重新開讀；亦核對 FACTS S06|Titus於80年啟用、約五萬觀眾、外側travertine、三層拱廊與另一層窗牆。條目所列Beste、Coarelli、Cozzo、Lancaster、Pensabene書目未另讀，不能冒稱直接核過那些考古研究。|
|S86|[Roma Capitale官方條目](https://www.turismoroma.it/it/node/1155) 建築介紹正文，2026-11-09重新開讀；亦核對 FACTS S86|外189×156m、高逾48m、arena76×46m、三層各80券、石／大理石座席、覆沙木地板、表演功能、原Nero湖址及三山谷地。這是整座建築概述，不能單憑「80年完成」的旅遊簡述證明全部頂部／後期地下室的同期形態。|
|S86V|[D’Anna／Molari《Il velarium del Colosseo》](https://amsacta.unibo.it/6307/1/Velarium%2007-01-2020%2B.pdf)，實讀封面、印頁3的分期說明及印頁22的幾何描述|只取三層80券及其上實牆的構成。該文場地數字86×54m與市府76×46m不同；不混合兩組數字，不採其完整velarium假說、承載計算或頂部復原。本模型仍用canonical79×46m近似。|
|E07|[PArCo地下設施介紹](https://colosseo.it/mirabilia/i-sotterranei-del-colosseo/)，本輪實讀既有 `research/model_reference/imperial03_events_colosseum_hypogeum.txt` 的兩段歷史正文；既有收據在 `imperial03_events_sources.json` E07|開幕時技術空間為木構，Domitian時期改永久砌體。不能把「本模型沒有畫地下」寫成「80年地下完全空無一物」。不將今天可見走廊數、後期升降機或217年後重建形式倒放80年。|
|E08|[Taylor等2016](https://waters.iath.virginia.edu/Journal9Taylor_et_al.pdf)，本輪實讀既有文字存檔的文章題名及印頁26注29；對照 `imperial03_events_sources.json` E08|該注將80年奉獻／使用與Domitian完成到attic分開，所引古代編年史原文沒有另讀。僅用於頂部完工的保留，不用其較籠統的「地下室未建」說法覆蓋E07所辨的早期木構。|

另已讀 `FACTS.md` S06、S86、`imperial_sample_sources.md` L1、
`imperial03_events_report.md` 的80年分期段、`docs/MUSEUM.md`、
`tools/museum.py` 的matcher／model／part／camera規則和原生 `pipeline/landmarks.py` 的ring實作。
本輪未增加圖像參照；上述來源的照片／圖版不作公開媒體授權。

## 原生模型檢查（CPU，未render）

透過 `uv run --no-sync --offline python -I`，只讀canonical `city.yaml`，呼叫原生
`museum.find_landmark` 與 `museum.build_model`；沒有呼叫整頁build或任何GPU工作。

|項目|結果|
|---|---|
|node|`imperial_height`|
|matcher|`{kind: ring, id: colosseum}`，恰好一件|
|地理錨點|lon12.492269、lat41.890212；theta−22°，完全沿用canonical|
|比例|`exaggeration: 1`，scale0.0001|
|幾何records|241；所有native label都是空字串|
|分件|`openings`優先以 `labels: ['*'], kinds: [dark]` 取240件；`main`以 `labels: ['*']` 取剩餘1個REVOLVE；無漏配、無空part|
|完整模型bounds，m|東−92.54262…92.61159；南−80.78456…80.68456；上−3.00000…48.15000|
|高度解釋|48m是建築名義高度；原生raised地坪另有0.15m，故top48.15m。−3m為自動下埋基腳，非古代地下室復原。|

bounds依native REVOLVE的72段及inset斷面，連同全部開口BOX角點計算；沒有把stand算成建築。
根據原生幾何的透視投影選距離，並用 `museum.apart` 算球面方向夾角：

|卡片／視點|az／el|d_m／fov|at_m [east,north,up]|source16:9圖像的x NDC／y NDC範圍|
|---|---|---|---|---|
|`south`（main）|0°／22°|300m／38°|[0,0,22]|x−0.51907…0.55725；y−0.65994…0.43306|
|`northeast`|120°／38°|310m／38°|[0,0,22]|x−0.52787…0.48444；y−0.80581…0.58551|
|`northwest`|240°／22°|300m／38°|[0,0,22]|x−0.45446…0.46997；y−0.76455…0.45790|

三對球面夾角為97.7404°、106.8283°、97.7404°，均超過50°。
`engine/lib.js frameOf`在直式畫面最多使用1.6倍stage寬的圖，所以整棟須留在來源圖中央62.5%帶內
（x NDC±0.625）；上列三視點都通過。另算了各視點旋轉15°／30°及tones用的
旋轉25°、抬高15°，仍留在此帶內且y NDC在±1內。
這是幾何投影檢查，**不是已看過桌機／手機畫面**；render、乾淨refs、圖片sheet及全尺寸shots由root驗收。

## 為何兩個part都標estimated

外189×156m、概括高48m、三層各80券有來源，但本次必須保留原生模型：

- `main`是一個不可拆的整環：已知外框與估配座席坡度、五帶斷面、4m場邊牆及未分attic上緣共用一件，不能分別著色。整件保守標estimated，而不是把所有座席細節升格成考古測繪。
- 等厚座席環形成79×46m內場，長軸比市府數字多3m；這是類別近似，不新改模型或宣稱新發現。
- 240個外廊標記是矩形深色BOX，沒有凿穿牆體，沒有真正券頂；高度、間距和三層等高分配為估配。因此開口part也標estimated。
- 未建模的頂層實牆、柱式、雕刻、屋頂、velarium不是「已證實缺席」，而是本頁省略的部分；其形態／80年完成狀態不足以由本模型主張。三張卡不補造這些架構。
- 模型內場地面由原生平地呈現，沒有獨立木地板record。卡片的覆沙木地板是有文字依據的表面表現，不聲稱已建出厚度、承重結構、下部房間或升降機。

圖片若將矩形暗標記改成另一套真拱立面、增添完整attic或展開遮陽篷，會破壞模型配準並超過本輪證據範圍；應在sheet檢查退回。
人物、衣色、確切石縫、鋪地紋理、天氣時段及遠景氣氛只作estimated視覺輔助；不是80年活動照片或已測古城市景。
不提前畫81年後Titus拱、Domitian永久hypogeum／Ludus Magnus／完整Flavian宮殿，也不放後來的Venus and Roma廟或Constantine拱。

## 已驗證與待root

已通過：YAML解析、中英欄位、所有cite存在、3張scene card必要欄位、native唯一matcher、241件全部分配、main part存在、三方向夾角及上述投影。
未執行：hant轉換、museum整頁build、native still／ref、生成圖片、sheet／adopt、桌機／手機截圖、CREDITS與web打包。
可先由root轉譯／build本頁，再依 `colosseum/south`、`colosseum/northeast`、`colosseum/northwest` 進入既有living流程。

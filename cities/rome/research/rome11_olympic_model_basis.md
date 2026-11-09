# 11｜基本形制與總圖依據

村總圖採文化部4535的[Planimetria generale](https://censimentoarchitetturecontemporanee.cultura.gov.it/scheda-opera?id=4535)，原檔 `model_reference/rome11_olympic/censimento_plan.jpg`；1958 Variant E只比較方案，未建中央教堂／方案劇院不倒放；另據1960運作圖建立的低長條CINEMA是不同實物。1960實景核對Talamona AR123/124印刷173圖J/K及174圖L/M，原PDF與三跨頁圖沿既有O04保存。正式聲線／字幕未改，1990世界盃仍在12。

| 基本形制 | 住宅層數min/max，不含pilotis | 來源與本次做法 |
|---|---:|---|
| A3單列長樓 | 3/3 | O02主軸東側及O04圖K；逐條源輪廓、整棟同層數，非逐戶row。 |
| A4彎長樓 | 4/4 | O02西側兩個組團；總圖成對線條分別描量體，**不把四條輪廓宣稱四個已核住宅單元**。 |
| B雙列／chiostrine | 5/5 | O02兩長樓及11個梯／井間隔；原圖列井，模型11個6×5m井口為圖讀估值。 |
| C方院四翼 | 4/4 | O02四翼及O04圖M；實際四翼分開圍院，pilotis貫通。sheet顯示一個翼的基本形制，整村圖核四翼關係。 |
| D／D1十字 | 2/2 | D1沿已批32×33.3m十字／兩層＋pilotis，D依圖L改水平窗帶；D1首區17個十字＋原圖底部兩個短條，不把短條冒充十字。源圖和圖J的連接鏈／院保留。 |
| E方樓 | 2/2 | O02西側五方樓；各棟源圖外廓，中央4m梯口估配，非十字複製。 |

23筆源輪廓是上述基本形制的尺寸／位置資料，不是23套新房型。全部用原生 `parts/prism/column/arches`、`landmark_types/template`；每項來源像素、層數及估值在 `rome11_olympic_whole_trace.yaml`／`whole_catalog.json`，只有一份可被native直接讀取的trace，沒有另一份模型鏡像。源輪廓由 `register.outline_landmark` 產生；核可十字幾何不另寫。無臆造街廓，故不以parcels生成與總圖不同的住宅地塊。

四錨native similarity配準1.7836m/px，殘差0.63–4.46m、留一2.66–22.87m；現況Overture只作存留尺度／位置控制，不作1960建造年代。逐項實際用地調 `citygen.landmark_site`，不以extent對稱框避讓。`village_registration_overlay.png`／`whole_registration_overlay.png`已實看。房屋3.1m層高及pilotis、柱寬／網距、0.18–0.25m樓板和窗分格皆估值；彎樓柱列沿各源邊，不以外包矩形在屋外立柱。B井口、E梯口精確尺度、樓梯／乾衣塔與細陽台未取得施工圖。地形×2、建築×3、1:10000不變。

基本形制最新原生sheet：`../build/review/modelview/rome11_olympic_whole_inputs/build/review/modelview/rome11_olympic_basic_forms/sheet.jpg`，研究9.46s；六件各四側及全覽已實看。其 `build/logs/geocheck.log` 正常、`clipcheck.log` 所有適用項0。source窗口原型不是1960整城，也不是已批村區；模型地表找平與D1連接群另以cut/parts實看比較，不能拿本sheet的零值外推全村。

Corso Francia另核文化部1087及Mariano/Milelli1982印刷16（課程PDF第8頁轉載）：雙10.5m車道、間5m、3.5–8m柱、15.97m梁跨。來源原頁已實看；村內中段用native平頭梁／橋面，未以無據全四分岔補出工作窗外交流道。場館尺寸以原報告為主：南Palazzo外122m／穹頂100m／34.5m高；文化部3894將21m／36Y混入之異文保留，不倒用北Palazzetto的形制或1990球場屋頂。

服務區另採完整LA84原報告PDF236實際1960運作圖（`village_report_plan.png`），不與永久住宅圖混做一次fit。四錨native similarity 0.6138m/px、殘差1.35–5.83m、留一4.96–45.73m；疊圖已實看。25件為北6／南4餐廳及另15個原圖接待、影院、公共六角亭、MG四倉、MB行李倉、sauna、兩長商店、醫務體；不宣稱逐一找齊原報告13倉。餐廳36×34m及輕金屬平屋頂有原報告，3.1m檐高／0.25m屋面／柱窗格估值；其餘服務樓高度minmax2.8–3.5m、取3.1m。MG封閉地板倉庫及sauna用原生raised，其餘cut；D1連接群parts各棟隨現地找平，上層／窗皮atop跟本棟，不是1960精確標高復原。義大利餐廳號及逐館賽後拆日未知，不更動導演故事。

df094d8指定重編：D1與六基本形制已正式通過。首區仍原生site:parts，新的同建築／薄台基門檻重編後，120°/15°同鏡位未見薄台基可辨變化，柱腳／透空／上下層保持。CorsoFrancia輸入不改，主線arches對超半拱的隆起段原生抬兩端，本輪整村geo/clip0。Olimpico僅實例site:cut改parts，橢圓ring按預設抬高、牆下接地無方平台，記者席依自身地面找平；部件沒有新增site，來源位置／大小／高度／倍率不變。原場低於道路4.5m有O01原刊依據，依導演決定不開挖，模型未呈現此低場標高，不把現地找平當1960實測；本輪獨立Olimpico geo/clip0。

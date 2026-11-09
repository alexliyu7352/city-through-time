# 14｜世界再聚與台伯河未來：本期城市資料調查

**首件可採用結果：同一現代城市、同一聖彼得廣場保留實體，公共活動光回來；2024已完成步行空間、2025各次聚集、2026閉幕與河流規劃逐項分開。** 這是step4的來源、狀態和地理資料提案，不是新建一座「2025古城」，沒有配置正式鏡頭、秒數或改寫旁白。主線仍為贏得、失去、再起。

## 來源讀取與時間口徑

以下原文已由網頁工具開啟，再由原站HTTP下載存入`research/model_reference/rome14_return/`。回應bytes、類型、URL與SHA-256見`rome14_return_source_receipts.json`；不是把搜尋摘要當正文。RI05已取得原PDF、核`%PDF`、成功pdftotext並實看第5頁。

| ID／既有FACTS | 原始來源及短摘 | 採用與界線 |
|---|---|---|
| RI01／S62 | [Roma Capitale，2024-12-23](https://www.comune.roma.it/web/it/notizia/ecco-la-nuova-piazza-pia-dicembre-2024.page)：`23 dicembre 2024` | Piazza Pia地面步行化，連接聖天使堡和Via della Conciliazione；Lungotevere in Sassia地下道延伸。是已啟用改變，不是全城工程全已完成。未取得工程平面，不猜造地下幾何。 |
| RI02／S55 | [Vatican News，2025-05-08](https://www.vaticannews.va/en/pope/news/2025-05/cardinal-elected-pope-papal-name.html)：`announced to the waiting crowds` | 聖彼得中央露台宣布良十四世當選；同一廣場有等候群眾。沒有精確人數，不說羅馬到這天才重開或一次選舉造成所有復甦。 |
| RI03／S59 | [Vatican News，2026-01-05](https://www.vaticannews.va/en/vatican-city/news/2026-01/jubilee-round-up-fisichella-pilgrims-faithful-hope.html)：`Almost 33.5 million pilgrims`、`from 185 countries` | Fisichella發布的全年朝聖規模與組織回顧。不是同時廣場容量、去重旅客、全市住宿接待或人口數；不與13的住宿下降百分比相除來校準燈光。 |
| RI04／S56 | [Vatican News，2026-01-06](https://www.vaticannews.va/en/pope/news/2026-01/pope-at-epiphany-mass-when-god-appears-nothing-remains-the-same.html)：`the Pope closed the Holy Door` | 當日已發生的閉幕，並非事前預告。約5,800人是大殿內彌撒出席者，不當作廣場或全年人數。關門不代表城市失去活動，不使模型沉下。 |
| RI05／S70 | [Pistilli／Salvati，《L’Osservatore di Strada》37期，印刷／PDF第5頁](https://media.osservatoreromano.va/media/osservatoreromano/pdf/ods/2025/12/ODS_2025_037_0712.pdf)：`era febbraio`、`giorni a Tor Vergata` | 2025年11月於和解大道採訪；34歲羅馬志工Piero分別回憶二月冷雨中的持十字架朝聖，以及Tor Vergata青年禧年的希望。兩段不同事件，不合成五月的聖彼得同日群眾；沒有雨行精確日／路線。 |
| RI06／S23 | [Roma Capitale，2025-07-07](https://www.comune.roma.it/web/it/notizia/approvato-il-piano-strategico-e-operativo-del-tevere-luglio2025.page)：`75 km`、`da Settebagni a Ostia Antica` | 市府發布已批准PSO；涵蓋自然、城市與近郊景觀，連接生態、公共空間與可持續移動。批准的策略／執行計畫並不等於75公里已建成一條公園、車道或步道。 |
| RI07／S71 | [Marevivo，2022-04-09，頁面更新2023-06-14](https://marevivo.it/blue-news/teverevivo-nasce-un-grande-sodalizio-per-il-fiume-storico-di-roma/)：`parte viva e integrante` | Tevere Day倡議者Alberto Acciari希望河流重回城市生活。是較早的倡議者期望，不是2026民調或可游泳／全線通航證明。 |
| RI08 | [RI01附圖原檔](https://www.comune.roma.it/web-resources/cms/images/nuovapiazzapiafontana_d0.jpg) | 已看噴泉近景、鋪地、行人及臨街既有建築；不能以近景推整場尺寸、樹位或地下道入口。 |
| RI09 | [RI03附圖原檔](https://www.vaticannews.va/content/dam/vaticannews/multimedia/2026/gennaio/05/cq5dam.thumbnail.cropped.750.422.jpeg/_jcr_content/renditions/cq5dam.thumbnail.cropped.750.422.jpeg) | 已看和解大道上持十字架的人群向聖彼得行走；圖示沒有可核拍攝日，不當作二月雨行、五月當選現場或2026-01-05實拍。 |

RI08、RI09及PDF照片皆只供研究；未取得上屏授權。RI05的照片不是Piero身分照片，不能自行指認照片人物。

## 逐項建模清冊

| 物件／空間 | 本期位置／平面、形態與年代依據 | 可操作採用分支 |
|---|---|---|
| 聖彼得大殿、穹頂、彎柱廊及斜直連接臂 | 沿07建築分期及13的SI06／SI07；原生OSM大殿way244159210、13的Frame面心12.4537288264,41.9021563887提供現代定位，非2025新建年。 | 13→14使用同一實體和IDs；不用04舊殿、不重新升起大殿。07目前僅形制sheet／直段模組，完整實址柱廊尚待共享，不能稱已完成。 |
| 廣場中央方尖碑 | 13的現代OSM way799694267及原生Frame面心12.4572610255,41.9022401441；S48的1586移置。 | 同址站立，不在2025再移碑；保留柱廊內可通行的空廣場。 |
| 聖彼得公共鋪地、前平台與東側開口 | 13的2020事件照片、SI07平面性質及RI09朝向大殿的視線。 | 保留鋪地與公共用途，不因「人回來」重造街廓；不把1667尚在的Borgo spina複製到2025。 |
| Piazza Pia | RI01具名兩端與地上／地下交通關係；RI08只證局部完成外觀。 | 可以採「已完成步行連接」用途／活動線資料；精確鋪地邊界、噴泉、樹列、梯級和地下入口仍需工程圖。此次不放任意矩形廣場或地下盒子。 |
| Via della Conciliazione上的接待與朝聖 | RI05採訪地、RI09照片；RI01與大殿的街道關係。 | 供主代理綁現有活動光。具名大道不是每次朝聖團GPS路徑；二月回憶不畫未證實的逐轉彎線。 |
| 五月宣布、青年禧年及一月閉幕 | RI02、RI05、RI03、RI04各有不同時間／地點。 | 三個狀態分存。青年禧年記憶在Tor Vergata，無已核座標／邊界便不新增pin或外飛鏡頭；閉幕不等於消滅建築。 |
| 台伯河與沿岸古城／現代城／鄉野 | RI06正文依序列Agro romano、Flaminio、牆內歷史核心、Ostiense-Marconi與河口農業景觀；現代河線用S76 OSM。 | 保留既有河面；來源限定的既有河線提供位置參考，不建立新水道、不拓寬、抽乾、挖池或換DEM。 |
| 75公里PSO | RI06是策略／執行計畫的批准發布，沒有可核逐工程完工圖層或精確路線。 | 本件只交框內既有河線作規劃語境；完整75公里超出台面，不修改全域框。計畫外框、堤岸工程界、連續步道與完工率不補造。 |

## 街廓、住宅、比例、層數、範圍與留地

本期沿用現代底模：S75 Overture 2026-10-21.0原始150,044筆、處理後140,866輪廓；height優先、其次levels×3.2m、缺值9m的既有估算保留。這是當代快照，並非2024／2025／2026各年逐棟普查；此次不提供或推定2020後每棟竣工、拆除、加高或店宅用途變化。住宅形式、比例、院落和樓層直接繼承底模的已知／估算欄位；沒有現代樣區比例資料，便不套古代批准房型，也不以三層街屋鋪整個現代Borgo。**不需新房型sheet。**

城市圖幅保持原box `[12.36,41.80,12.64,42.00]`、原生投影台面area `[12.356,41.797,12.6436,42.003]`；水平1:10000、地形×2、現代建築×3均只讀。全城末景沿此可見城市，不把台面外緣說成2026行政界／建成終點；75公里是另一個規劃尺度。外圍不填古城住宅，既有園地、廣場、道路、水面和其他留地保留其用途。

13的活動退去與14的回升，不構成任何建築幾何增減。Piazza Pia是明確有據的地面交通／公共空間改變，與「聖彼得舊建築保持站立」並不衝突；其精確新表面尚未建模，不能將空的geometry清單誤讀為研究否認工程發生。

## 已備原生資料與規劃界線

- `rome14_return_changes_proposed.yaml`逐項保留2024啟用、二月回憶、五月聚集、青年禧年、全年發布統計、2026閉幕、居民倡議與未來計畫，附各自來源和禁止推論；它是研究清冊，不是新引擎格式。
- `rome14_return_native_fragment.yaml`使用現成`lines`的`src: rivers`／`filter: Tevere`，讓現有河流位置承載規劃語境。它不含相機、正式秒數、grow/reset/lose、night或city，主代理在step5綁時間和圖例。原生filter實查只命中2個Tevere片段，排除Aniene。
- `rome14_return_tevere_reference.geojson`由既有快取原生OSM的2條Tevere河心線，經`pipeline.geo.Frame`投影及現有台面裁切得到；保留way id和原始URL。聯集長41,268.0m僅是**框內現有河線長**，不作75公里計畫的已實施／已畫全比例。這份線沒有驗明PSO的上下游切點，也不把整條被選河線逐米斷定為計畫覆蓋。
- `lines`現版本無虛線欄位，不能寫一個無效的dash鍵。可用TREATMENT已定的計畫綠色加明確`Planned / 规划`標示，另說「河流位置參考、計畫界未繪」。若要逐工程或全75公里邊界，必須先取得官方計畫圖；目前不以畫寬綠帶代替工程實界。
- 活動回來沿13的同一公共活動線／面罩家族，用現成`lines`／`epochs`。顏色、強弱、淡入不是遊客、人流、人口或真實照度；保留普通建築照明。`epochs.buildings_inside:false`不能全面排除歷史構件投光，需在共享實址柱廊核圖。
- 12的`rome12_modern_shared_tool_issue.md`已證明GHS-BUILT-V使用固定2018高度，且grow年線會讓2025預測輪廓溢入14。正式合併必須由主線處理，14不修共用工具、不把26棟預測定年硬改為2020、不以2025／2030當已建年代。2024–2026事件可前進，歷史生長證據仍截止2020。

## 驗證及到此交件

`uv run --no-sync --offline python -I cities/rome/research/rome14_return_inventory.py`實跑exit0：9份來源SHA／bytes、清冊來源引用和幾何保留、原生河線filter合計**失敗0**。日誌`rome14_return_inventory.log`，統計／三張實看圖的尺寸、雜湊與限制在`rome14_return_inventory.json`。已看RI08噴泉近景660×440、RI09朝聖圖750×421及RI05第5頁1072×1600；不是模型樣張。

**未跑modelview／compile／eraview／rangecheck。** 本件沒有新時期幾何；modelview的`NODE_KEEP`不保留lines／epochs，不能用它聲稱已驗活動光。此次可採用資料已完成，沒有為通過模型檢查而複製新古城或自製2025街屋。真正低角度10–15°和遠景依賴07完整實址幾何及Piazza Pia實界，之後主代理用原生rangecheck檢14和鄰站；此件不排正式鏡頭。

本期來源提案無研究阻擋。正式畫面尚需：07實址大殿／全柱廊及廣場地理線；如要做Piazza Pia可辨的表面改變，先取得工程圖或經核現況輪廓；12共用年線預測外溢的主線決定；step5活動及規劃圖例綁定。完整75公里工程幾何不屬此次首件可採用範圍，也不是敘事結尾成立的必要條件。

# Rome round 11：十個 living 的周邊與採用界線

以 `本機候選/rome_round10_all/build/film.json` 的實際十個 ID 為準，逐張讀其 scene、原 PNG、原生 ref，並看 50% blend。舊秒數只用於對照，不能拿來排新配音後的時序。原 ref／PNG／record 都未改。

可套用清單：`rome_round11_living_staging_patch.yaml`。新卡位於 `research/living/rome_round11_*.yaml`。七張保留原 ID 與圖，整合者把新卡內容放到候選原 ID 對應的 scene 路徑；三張有錯的才換新 ID、取最終 native ref、生圖及由整合者 adopt。

| round10 實際 ID／舊入場秒 | ref 空地當時應是什麼 | 原圖與 blend 所見／決定 |
|---|---|---|
| `rome01_founding_legend`／78.12 | Cermalus 茅屋群間的坡地、土徑、低植被與遠丘；非後來石造都市。精確前753植被非已知。 | 原圖接草坡、土徑和遠低林丘；茅屋輪廓貼原 ref，無新水域或都市。保留已批犁界人物。 |
| `restart_lm01`／284.92 | 火前早期帝國街屋間的窄街與院落，上緣為連續屋頂／天空；不是農田。 | 圖維持密建與既有街巷，無錯補河或開闊田野。保留。 |
| `rome_round10_boatmill537`／710.89 | 兩舟周圍是臺伯河；上緣為模型既有前近代河岸建築與狹窄不規則岸腳。船磨位置與岸形為功能示意。 | 河、船、輪與岸上量體對位；未補現代高堤或虛構港口。保留。 |
| `rome_af_jubilee1300`／871.99 | 河道、前近代岸地與模型已留的牆外開地，屋列仍屬居住城。Borgo、舊殿、當期宮殿在其原位，不能從局部開地推全區空無。 | 圖在既有開地續低草、土路；既有屋列仍在，橋上雙向人流保留，未添加近代高堤。此局部圖不證某種作物或完整宅界。保留。 |
| `rome_round10_stpeter_drum1564`／1078.06 | 1563–1564 梵蒂岡建築區：此前已存在的宮殿群、未拆舊殿東前半／前庭、1565之前的 Borgo Vecchio／Nuovo 核心，園丘只在其真方向。 | **重生。** 原圖把大殿四周補為大片田野／孤立教堂；工人於整鼓座全景仍太小。改 native 機位靠鼓座頂工作緣；不可放大人體。新卡已刪舊15–25px驗收敘述。 |
| `rome_round9_flood1870`／1248.73 | 前高堤時代 Via della Fiumara／Ghetto 局部住宅前街道的洪水，不是永久湖岸或全城水面界。 | 圖為靠原屋前的小船及泥色街道洪水，沒有現代堤岸／大浪；沿既批地方母題。保留。 |
| `rome_round10_spina_move1937`／1413.93 | 1936–1937 已清掉的 Spina 走廊，兩側仍存 Borgo 屋列；不是田野，也不是1950完成大道。 | 圖為灰土、少量碎石、兩側剩屋與遠聖彼得；未補回 Spina。保留搬離家庭。 |
| `rome_round10_periphery_home1980s`／1665.61 | 既有外圍公寓間的開放住區地面、草土和簡單通路；非可指認某戶／某社區景觀。 | 圖與 ref 保持公寓／高樓分布與開地；新鮮整潔外牆、家庭及搬家物品保留，無內裝或新庭院。保留。 |
| `rome_round10_prayer2020`／1710.51 | 廣場外為梵蒂岡／Borgo 建成區與協和大道的街地，地面連續；雨使石地濕亮，不使廣場成湖。 | **重生。** `today:sink` 的 ref 取走城市，圖將柱廊外補成整片深反光水域，錯把廣場浮湖。候選改 `today:keep`，以真城區作 ref；保雨、空場、遠祈禱人／臨時蓬。 |
| `rome_round10_piazza_pia2024`／1745.83 | Piazza Pia 步行地面／協和大道入口在街地高程；臺伯河在高石堤下的獨立河槽。 | **重生。** 原圖左下水面直接平貼鋪地、沒有高堤落差。最終 native 若看河側，先使堤頂／垂直關係可判；若只見地面，保持水在畫外。保行人和已批自然石材色。 |

## 來源及精度

- 前四張及1870／1937／1980s沿原 scene 的既核證據：S128／S191與Cermalus模型；S104／S154與AD14來源城；S165／Procopius與船磨功能模型；Dante《地獄篇》XVIII.28–33和 `rome06_medieval_survey.md`；S19／ISPRA2021印216圖13與Roesler Franz後世畫；Senato的Spina拆除與Cecchini2020遷離研究；S68／Macioti2019的部分家庭回顧。沒有重新研究人物或擴大歷史聲稱。
- 工地周邊沿 [Vatican State 官方宮史](https://www.vaticanstate.va/it/stato-e-governo/storia.html)：中世紀宮殿、1477–1483的Sistine及Julius II的Belvedere都早於鼓座工期；[Senato 的 Alfarano／Bonifacio1590 解說](https://antiquorum-habet.senato.it/index.php/section/section_61_it/)說明舊殿部分中殿仍使用、新工地在隔牆另一側。已批 `rome07_renaissance_phases_review.md` 明列1564舊東中殿／前庭與前1565 Borgo核心。這不支持把1589–1590重建宗座宮正立面提前。
- [文化部／國家檔案館 Borgo 說明](https://cultura.gov.it/evento/iorestoacasa-il-rione-borgo-nel-catasto-pontificio-di-roma)區分原有文藝復興住區與1565北側新Borghi；不拿較晚地籍當1564逐戶精確測量。其1500開街教宗錯字不採。
- 疫情儀式仍沿原卡S53／S54與 [Vatican 2020-03-27 講道](https://www.vatican.va/content/francesco/en/homilies/2020/documents/papa-francesco_20200327_omelia-epidemia.html)。[市府旅遊局Borgo頁](https://www.turismoroma.it/it/pagina/rione-xiv-borgo)支持廣場鄰近建成區和協和大道背景，具體可見量體依候選已存現代模型。S54本就要求保房屋；本輪新周邊規則使舊 `sink` 裁定不再適用。原prayer卡的 `sources` 是字串，新卡已改成真正list，避免compile把來源拆成單字元。
- Pia啟用日與地面連接沿 [Roma Capitale 2024-12-23](https://www.comune.roma.it/web/it/notizia/ecco-la-nuova-piazza-pia-dicembre-2024.page)；[Roma Mobilità工程頁](https://romamobilita.it/piani-e-progetti/piazza-pia/)同樣記上方廣場與延伸地下車道。[Roma Capitale旅遊局《Il Tevere》](https://www.turismoroma.it/it/page/il-tevere)明載近代高堤及下於街道的河岸步道，只支持高低分離的定性判斷，沒有借別河段11.5m的模型高度來冒充Pia現場尺寸。

新資料只用於周邊，未取得原圖片上屏授權，也未將上述網頁照片／版畫放進輸出。七張保留圖的無資料樹種、草地邊界、院落雜物仍是低資訊想像；不提升為考古測量。全十張新卡明寫投影紫／白等非真材色。

## 最終 native refs 與三張生成結果

三張新ID：`rome_round11_stpeter_drum1564`、`rome_round11_prayer2020`、`rome_round11_piazza_pia2024`。整合者已固定三shot／當期可見狀態並交原生ref，之後才用內建 `image_gen.imagegen` 的 EDIT 生成；未用舊ref預先生圖，未adopt或改候選。三張PNG均在 `assets/living/<new_id>.png`，逐張看過ref／新PNG／50%blend後交整合者，原圖保留。

- 工地native cam `[-.37908,.01511,-.03454,105,10,.0035,42]`：東偏北看西偏南，鼓身下半裁掉。卡片已明定Borgo和仍在的舊殿前半主要在鏡後，不把它們搬進西背景。可見丘地僅作低資訊的梵蒂岡丘園地；[Vatican State 的 Giardini Vaticani 官方史](https://www.vaticanstate.va/it/altri-organismi/giardini-vaticani?format=html)及既核M09支持1279起果園、草地與園地用途，不支持確切1564樹位、園路或今日花壇。首版工人過大已退回；後續縮回普通尺度，最後一輪針對原生鼓座右緣外漂再作EDIT，使開口／外緣重新貼ref。保三普通工人、小木桅吊架、繩與小石件；所有工人、索具、園路和樹位仍是來源約束的匿名想像。
- Prayer native保現代城市：周邊Borgo／宮殿量體保留，地面為能讀出紋理的濕石地而非湖；雨、空廣場、遠小蓬與單一白袍祈禱人保留。
- Pia native在鋪地內側，cam `[-.29415,.00307,-.03435,90,8,.0065,42]`：臺伯河及高堤都在鏡後，不在圖中。全下半是連續石鋪地、既有兩泉槽與既有樹位，水僅在泉槽內；冬衣行人及自然石材色保留。

工具prompt集：`rome_round11_living_prompts.json`；生成來源、ref SHA1、PNG SHA256和相機記錄：`rome_round11_living_generation.json`。三張新圖檢視sheet及blend在 `本機候選/rome_round11_living_generated/`，原生ref另保存於同目錄作生成時基準。最終clean check與adopt仍由整合者完成；此處不把自審當成全片checks。

原圖檢視sheet：`本機候選/rome_round11_living_scan/<round10_id>_check.jpg`；來源清單含原檔路徑的 `inventory.json` 同目錄。重建命令：`uv run python -I cities/rome/research/rome_round11_living_scan.py`，只寫/tmp。

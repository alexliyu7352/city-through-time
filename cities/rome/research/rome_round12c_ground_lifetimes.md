# Rome round12c：升前／退後場地生命週期掃描

## 目前候選實施及原生驗證

736筆表與原始proposal保留為來源／時序清單；候選由`rome_round12c_edit.py --apply`整合，另包含主線已准的Constantine中性地、成熟樹及937實際可見陸地延續。早期earth合409218.4m²，Constantine source footprint聯集為47260.0m²；937延續區以既有1300 general與55.66ha梵蒂岡自然展示窗相交，與garden合併後有效382345.6m²，並非只有原proposal的161529.8m²選區。沒有提前晚期鋪地。

早期earth的37%住宅覆蓋為真WARN：原住房／lot模型完整保留，中性地形在屋下，原生loss之後才成為開放陸地；不稱44／27BCE考證空地，也不為消警告刪屋、扣回80空場、force或quiet。root已看194.9／261／436，未見抬高底板；最後指定秒及eraview亦已核過。

330七群現採同片北兩古園成熟樹物理估值11m高／4m冠半徑；高看focus0.17以同eye／heading方式處理，原低側面與時間保留。完整來源／估值界線見`rome_round12c_vatican_landscape.md`開首。

主線9e20ddc已合併，grounds marker已從住宅避讓排除、真正水池保留。最新正常round為1801.422秒／361cue，FAULT空、7段checks passed，1871未再列模型變動；已准avoid_eras城一次性填洞／隨機細節。最終模型表5城，root已看完新舊雙look eraview。指定精確秒已新舊並排；drum僅補陸地材質、建物輪廓未動，root准保留PNG更新私有ref／adopt。最後16段原生rangecheck全過，精確圖由正常named_stills刷新stamp；55張range／line sheets、22張精確對照與10個living sheets已實看。全部重活與root最終視覺檢查均已完成，詳細狀態以`rome_round12c_handoff.md`及`rome_round12c_review.md`為準。

## 原始唯讀掃描

唯讀final12b原生film／era／配置及既有來源；未寫候選、共享碼，未compile／render。

逐ID共736筆原生有site地標，含trace中的建國宅群、Cinecittà與Olympic分件；全部匹配compiled building group。地面另逐entry核stage／loss／同era後列預切。逐秒鏡頭投影以原生camera插值／drift計，地高近似.008；表中的鏡內／空窗是保守來源site投影，**不等於已做逐像素遮擋判斷**。真露底採現有有效still核過的Palatine、Oppian及Vatican為主。

## 可直接套用

`rome_round12c_ground_lifetimes_proposal.json`只套`apply_groups`與`tree_updates`。前三組依序是Palatine109713.7m²、Oppian／公共廣場源地增量299504.7m²、Vatican1300既有陸地子區161529.8m²。前兩組共用早於帝國且存續至another_centre的共和earth；Vatican重用仍存續的1300garden ground。無新era；只一個新ground slot。

Palatine只扣437仍站住宅／庭坪3m及街巷1.5m；已退lot不永久挖空。新earth對共和7個已存grounds交集均小於1m²；額外公共區已扣舊grounds，保12b既有院面。首次城級stage與handoff keep見proposal。中性earth是陸地／開放用地示意，不是未來Flavian大理石、未來浴場院坪或假平台。190／261／284須看早期街坊讀法；429–437每秒、449–452、455–461、911／932／937／1083.19須原生新舊並排。

## AD80與北兩橢圓

Augustus宅早版已在：`domus_augustus_surface_proxy`283.381秒站全，64火loss未點名；Apollo為較早`republic_civic_dedications.apollo_palatine`持續站立。兩者來源版本保留。Tiberiana的E09只證64後存在；既有`imperial03_late_entities_proposal.json`已明文拒絕把AD113的100×120m院體當Nero幾何，`postfire_versions_inventory`亦要求早期新形。330 retained模板沒有解出Nero／Domitian逐牆分期，因此本輪不倒放其上構，只補有據山地。

583.6／596.45兩深色橢圓是`rome04_sallustian_garden_use`與`rome04_esquiline_garden_use`；Pincian是更西側另一園帶。兩者已由`rome04_late_garden_ground`覆grass，472.505秒前站全，並有457／371棵原生樹，473.059秒前已升完，不是水池或ground失壽命。最小修法把24m疏距改16m，11m樹高／4m冠半徑保原預設；來源`rome04_lateantique_geography.yaml`／`whole_basis.md`LA32，植栽位置、密度為示意。

## 同類分類及限制

原生部分loss不等於整棟退：屋頂／立面剩餘體已區分；同址下一版本仍站及today_from交回今日也另列。城級升起短掃光和每戶dark figure-ground不一律塗地。標C的Constantine浴場494–504露底依主線最終裁定一併處理：唯一屬於該浴場的`rome_round12b_ground_07_paved`改為275起的全期中性earth，移至`late_capital_275`，region聯集原生templated／checked後的source footprint（landmark_site、apron0），補完整連續陸地，不留未來圓廳／軸廳藍洞。350建築geometry／分期保留，不增加slot、era或平台，也不稱提前完成浴場庭院。495.50已由整合者實看，503.21待本輪原生精確補圖。Diocletian有住宅前身到502.457，首體505.206升，真正清場窗約2.75秒；保其原for前身，不能提前鋪350庭園。

Vatican937藍地原因是1300general ground於911.112退場，而Belvedere三個未來site先前的源陸地覆蓋分別100%／100%／68.19%。新增區完全取既有1300源land，不用1506／1667院坪；已過三個水平院仍在其原stage升。1083.19的主要藍地在大殿後方Belvedere脈絡；Bernini既有gravel1083.741開始、1084.741站全，本來就早於柱廊1085.829，不能將該橢圓砂礫面倒回1506。

|類別|筆數|處置|
|---|---:|---|
|P|7|已確認Palatine升前／舊library退後開地；套早owner中性earth，晚宮院原stage覆上。|
|O|2|已確認Oppian／Trajan浴場升前開地；套來源丘地earth，保當秒住宅／街路。|
|F|6|帝國廣場／Peace清場接新建之間；套來源公共用地earth，既有鋪地不提前或改色。|
|V|5|Vatican源陸地911先退；保1300原開放陸地至新殿／水平院覆上，不提前晚院。|
|R|41|有同址下一版本；只交接版本，不把整個場地重鋪成earth。|
|T|72|原生today_from交還今日；後段由今日模型接，不用古earth續蓋。|
|H|3|只損屋頂／立面／部分構件，餘體仍站；不視為整址空場。|
|W|329|首次城級升起掃光／短清場窗；原stage、原前身及已存地面保留。|
|Q|226|單棟宅地／小尺度縫隙，屬MODEL住宅figure-ground；不鋪整片quarter。|
|B|6|清場前有原生for前身住宅／建物，之後短建設轉換；不以未來院坪提前填。|
|C|1|Constantine的ground07改275起全期中性earth，聯集原生source footprint補圓廳／軸廳空洞；350建物及分期保留。|
|N|38|來源site可能鏡內，未有有效still證實持續湖感；保有據前身／原面，不把site投影當裸底。|

## 全部逐ID表

秒點為final12b；`前`／`後`是未升前／全退後的鏡內來源site區間；H的部分退場不列為整址退。完整來源原文、對應grounds、相交同址繼任者、時序小數及清場精確窗均在同名JSON。

|node／ID|站起區間|可見site區間|前／後空窗|類|來源|
|---|---|---|---|---|---|
|founding_price / `rome01_cermalus_district_A`|26.786–27.986|25–78; 91–108|前25–26; 後93–108|Q|research/rome01_cermalus_evidence_report.md|
|founding_price / `rome01_cermalus_district_B`|27.326–28.526|25–76; 92–107|前25–27; 後93–107|Q|research/rome01_cermalus_evidence_report.md|
|founding_price / `rome01_cermalus_district_C`|25.579–26.779|25–77; 92–108|前25; 後93–108|Q|research/rome01_cermalus_evidence_report.md|
|founding_price / `rome01_cermalus_district_E`|26.478–27.678|25–78; 91–109|前25–26; 後93–109|Q|research/rome01_cermalus_evidence_report.md|
|founding_price / `rome01_founding_whole_capitolium_01`|42.539–43.739|34–77; 91–108|前34–42; 後93–108|R|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_02`|43.052–44.252|34–77; 91–108|前34–43; 後93–108|R|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_03`|42.846–44.046|33–77; 91–108|前33–42; 後93–108|R|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_04`|42.974–44.174|34–78; 91–108|前34–42; 後93–108|R|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_05`|42.605–43.805|33–78; 91–108|前33–42; 後93–108|R|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_06`|42.927–44.127|33–77; 91–108|前33–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_07`|42.621–43.821|34–77; 91–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_08`|43.028–44.228|33–77; 91–108|前33–43|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_09`|42.706–43.906|33–77; 91–108|前33–42|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_10`|43.043–44.243|34–78; 91–108|前34–43|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_11`|42.839–44.039|33–53; 60–78; 91–108|前33–42|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_12`|42.972–44.172|34–52; 61–78; 91–108|前34–42|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_13`|43.146–44.346|33–52; 60–78; 91–108|前33–43|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_14`|43.141–44.341|33–52; 63–78; 91–108|前33–43; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_15`|42.653–43.853|33–52; 64–78; 91–108|前33–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_16`|42.926–44.126|33–52; 66–77; 91–108|前33–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_17`|42.738–43.938|33–52; 66–77; 91–108|前33–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_18`|42.817–44.017|33–52; 66–77; 91–108|前33–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_19`|42.886–44.086|33–52; 66–77; 91–108|前33–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_20`|42.673–43.873|33–76; 92–107|前33–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_21`|42.656–43.856|33–76; 92–107|前33–42|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_22`|42.605–43.805|33–76; 92–107|前33–42|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_23`|42.502–43.702|33–52; 61–77; 91–108|前33–42|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_24`|42.879–44.079|33–52; 62–77; 91–108|前33–42|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_25`|42.721–43.921|33–52; 65–77; 91–108|前33–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_26`|42.683–43.883|33–52; 65–77; 91–108|前33–42|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_27`|43.041–44.241|33–52; 66–77; 91–108|前33–43; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_28`|42.772–43.972|34–78; 91–108|前34–42|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_29`|42.892–44.092|34–78; 91–108|前34–42|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_30`|43.348–44.548|34–54; 59–77; 91–108|前34–43|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_31`|43.208–44.408|34–77; 91–108|前34–43|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_capitolium_32`|42.934–44.134|34–77; 91–108|前34–42|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_01`|43.262–44.462|34–51; 66–77; 92–108|前34–43; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_02`|43.210–44.410|34–51; 66–77; 92–108|前34–43; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_03`|43.362–44.562|34–51; 66–77; 91–108|前34–43; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_04`|43.286–44.486|34–51; 66–77; 91–108|前34–43; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_05`|43.323–44.523|34–51; 66–76; 92–108|前34–43; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_06`|42.963–44.163|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_07`|43.037–44.237|34–51; 66–77; 92–108|前34–43; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_08`|43.097–44.297|34–51; 66–77; 92–108|前34–43; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_09`|42.950–44.150|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_10`|42.884–44.084|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_11`|42.957–44.157|35–51; 66–75; 93–106|前35–42; 後93–106|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_12`|42.937–44.137|35–51; 66–75; 93–106|前35–42; 後93–106|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_13`|42.991–44.191|35–51; 66–75; 93–106|前35–42; 後93–106|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_14`|43.342–44.542|35–51; 66–76; 92–107|前35–43; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_15`|43.375–44.575|35–51; 66–76; 92–107|前35–43; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_caesar_valley_16`|43.043–44.243|35–51; 66–77; 92–108|前35–43; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_01`|42.031–43.231|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_02`|42.237–43.437|34–51; 66–76; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_03`|42.150–43.350|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_04`|42.230–43.430|34–51; 66–77; 91–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_05`|42.444–43.644|34–51; 66–77; 91–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_06`|42.197–43.397|34–51; 66–77; 91–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_07`|42.280–43.480|34–51; 66–75; 93–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_08`|42.139–43.339|34–51; 66–76; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_09`|42.241–43.441|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_10`|42.623–43.823|34–51; 66–77; 92–108|前34–42; 後93–108|R|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_11`|42.697–43.897|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_12`|42.425–43.625|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_13`|42.223–43.423|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_14`|42.621–43.821|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_15`|42.427–43.627|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_16`|42.505–43.705|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_17`|42.239–43.439|34–51; 66–77; 91–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_forum_regia_18`|42.481–43.681|34–51; 66–76; 92–108|前34–42; 後93–108|R|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_01`|41.914–43.114|34–51; 66–76; 92–107|前34–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_02`|42.160–43.360|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_03`|42.324–43.524|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_04`|42.002–43.202|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_05`|42.189–43.389|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_06`|42.210–43.410|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_07`|42.199–43.399|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_08`|42.229–43.429|34–51; 66–76; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_09`|42.528–43.728|34–51; 66–76; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_10`|42.149–43.349|34–51; 66–75; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_11`|42.494–43.694|34–51; 66–75; 93–106|前34–42; 後93–106|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_12`|42.441–43.641|34–51; 66–76; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_13`|42.293–43.493|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_14`|42.731–43.931|34–51; 66–75; 93–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_15`|42.658–43.858|34–51; 66–75; 93–106|前34–42; 後93–106|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_16`|42.083–43.283|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_17`|42.372–43.572|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_18`|42.250–43.450|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_19`|42.762–43.962|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_20`|42.662–43.862|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_21`|42.188–43.388|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_22`|42.494–43.694|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_23`|42.114–43.314|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_north_palatine_24`|42.568–43.768|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_01`|42.437–43.637|34–51; 66–75; 93–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_02`|42.289–43.489|34–51; 66–75; 93–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_03`|42.260–43.460|34–51; 66–75; 93–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_04`|42.895–44.095|34–51; 66–76; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_05`|42.432–43.632|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_06`|42.799–43.999|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_07`|42.839–44.039|34–51; 66–75; 93–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_08`|43.020–44.220|35–51; 66–76; 92–107|前35–43; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_09`|43.056–44.256|35–51; 66–75; 93–107|前35–43; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_10`|42.536–43.736|35–51; 66–76; 92–107|前35–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_11`|42.733–43.933|35–51; 66–76; 92–107|前35–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_12`|42.963–44.163|35–51; 66–76; 92–107|前35–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_13`|43.071–44.271|35–51; 66–75; 93–107|前35–43; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_14`|42.995–44.195|35–51; 66–75; 93–107|前35–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_15`|42.565–43.765|34–51; 66–77; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_16`|42.586–43.786|34–51; 66–76; 92–108|前34–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_17`|43.019–44.219|34–51; 66–76; 92–108|前34–43; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_18`|42.625–43.825|35–51; 66–75; 93–106|前35–42; 後93–106|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_19`|42.563–43.763|34–51; 66–75; 93–106|前34–42; 後93–106|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_20`|42.970–44.170|35–51; 66–76; 92–107|前35–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_21`|42.705–43.905|34–51; 66–76; 92–107|前34–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_22`|42.796–43.996|35–51; 66–76; 92–107|前35–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_23`|42.796–43.996|35–51; 66–76; 92–107|前35–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northeast_palatine_24`|42.958–44.158|35–51; 66–76; 92–107|前35–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_01`|41.476–42.676|25–76; 92–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_02`|41.224–42.424|25–76; 92–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_03`|41.645–42.845|25–76; 92–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_04`|41.401–42.601|25–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_05`|41.061–42.261|25–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_06`|40.945–42.145|25–76; 92–107|前25–40; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_07`|41.480–42.680|25–76; 92–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_08`|40.986–42.186|25–76; 92–107|前25–40; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_09`|41.173–42.373|25–77; 92–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_10`|41.365–42.565|25–54; 63–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_11`|41.538–42.738|25–57; 62–76; 92–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_12`|41.364–42.564|25–76; 92–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_13`|41.395–42.595|25–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_14`|41.721–42.921|25–57; 62–76; 92–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_15`|41.617–42.817|25–52; 66–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_16`|41.472–42.672|25–52; 66–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_17`|41.732–42.932|25–52; 66–75; 93–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_18`|41.325–42.525|25–52; 64–76; 92–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_19`|41.472–42.672|25–52; 64–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_20`|41.293–42.493|25–52; 66–76; 92–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_21`|41.798–42.998|25–52; 66–76; 92–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_22`|41.478–42.678|25–52; 66–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_23`|41.927–43.127|25–52; 66–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_24`|41.642–42.842|33–52; 66–77; 92–108|前33–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_25`|42.162–43.362|33–51; 66–77; 91–108|前33–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_26`|41.606–42.806|33–51; 66–77; 91–108|前33–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_27`|42.066–43.266|33–51; 66–76; 92–107|前33–42; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_28`|41.598–42.798|33–52; 66–76; 92–107|前33–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_29`|41.958–43.158|33–52; 66–76; 92–107|前33–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_30`|41.619–42.819|33–51; 66–76; 92–107|前33–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_31`|42.127–43.327|33–51; 66–77; 92–108|前33–42; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_32`|41.938–43.138|33–51; 66–77; 91–108|前33–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_33`|41.916–43.116|33–51; 66–77; 91–108|前33–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_34`|41.798–42.998|33–51; 66–77; 92–108|前33–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_35`|41.445–42.645|25–76; 92–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_36`|41.537–42.737|25–52; 65–76; 92–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_37`|41.274–42.474|25–52; 66–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_38`|41.538–42.738|25–52; 66–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_39`|41.426–42.626|25–52; 66–76; 92–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_palatine_crown_40`|41.456–42.656|25–26; 33–52; 66–77; 92–108|前25–26; 前33–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_01`|41.074–42.274|25–78; 91–109|前25–41; 後93–109|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_02`|41.168–42.368|25–78; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_03`|40.958–42.158|25–78; 91–108|前25–40; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_04`|41.305–42.505|25–78; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_05`|41.279–42.479|25–77; 92–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_06`|40.851–42.051|25–77; 91–108|前25–40; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_07`|41.293–42.493|25–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_08`|41.255–42.455|25–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_09`|40.978–42.178|25–77; 91–108|前25–40; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_10`|41.402–42.602|25–77; 91–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_11`|41.038–42.238|25–76; 92–107|前25–41; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_northwest_palatine_12`|41.056–42.256|25–77; 92–108|前25–41; 後93–108|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_quirinal_south_01`|45.413–46.613|39–50; 66–76; 92–107|前39–45; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_quirinal_south_02`|44.953–46.153|39–50; 66–76; 92–107|前39–44; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_quirinal_south_03`|45.082–46.282|39–50; 66–76; 92–107|前39–45; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_quirinal_south_04`|45.128–46.328|39–50; 66–76; 92–107|前39–45; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_quirinal_south_05`|45.067–46.267|39–50; 66–76; 92–107|前39–45; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_quirinal_south_06`|45.541–46.741|39–50; 66–75; 93–107|前39–45; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_quirinal_south_07`|45.380–46.580|39–50; 66–75; 93–106|前39–45; 後93–106|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_quirinal_south_08`|45.326–46.526|40–50; 66–76; 92–107|前40–45; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_quirinal_south_09`|45.331–46.531|40–50; 66–76; 92–107|前40–45; 後93–107|Q|research/rome01_founding_whole_sources.md|
|founding_price / `rome01_founding_whole_quirinal_south_10`|45.206–46.406|39–50; 66–75; 93–107|前39–45; 後93–107|Q|research/rome01_founding_whole_sources.md|
|republic_won_and_lost / `rome02_early_quarter_curiae_west_50104`|96.076–97.676|—|—|Q|research/rome02_early_city_plan.md|
|republic_won_and_lost / `rome02_early_quarter_curiae_old_boundary`|95.822–97.422|—|—|Q|research/rome02_early_city_plan.md|
|republic_won_and_lost / `early_capitoline_tuscan`|88.587–90.187|87–195|前87–88; 後146–195|W|research/rome02_formal_prepare_tuscan_sources.md, R08|
|republic_won_and_lost / `rome02_early_whole_regia_late6c`|94.861–96.461|87–195|前87–94; 後193–195|R|research/rome02_early_whole_plan.md|
|republic_middle_city / `rome02_mid_source_domus_curiae_contact`|137.567–139.167|135–146; 157–200|前135–137; 後146; 後157–200|W|research/rome02_mid_source_domus_basis.md, M2, M3, M4|
|republic_middle_city / `rome02_mid_whole_sempronia_169`|136.654–138.254|135–201|前135–136; 後146–201|W|research/rome02_mid_whole_plan.md, R15, R16|
|republic_middle_city / `rome02_mid_whole_fulvia_179`|136.623–138.223|135–201|前135–136; 後146–201|W|research/rome02_mid_whole_plan.md, R15, R16|
|republic_middle_city / `rome02_mid_whole_tabernae_veteres`|136.759–138.359|135–201|前135–136; 後146–201|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_tabernae_novae`|136.562–138.162|135–201|前135–136; 後146–201|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_castor_pre117`|136.878–138.478|135–201|前135–136; 後146–201|W|research/rome02_mid_whole_plan.md, R15, R16|
|republic_middle_city / `rome02_mid_whole_saturn_early`|136.720–138.320|135–201|前135–136; 後146–201|W|research/rome02_mid_whole_plan.md, R15, R16|
|republic_middle_city / `rome02_mid_whole_magna_mater_191`|136.935–138.535|135–145; 158–200|前135–136; 後158–200|W|research/rome02_mid_whole_plan.md, R15, R16|
|republic_middle_city / `rome02_mid_whole_victoria_294`|137.177–138.777|135–145; 158–200|前135–137; 後158–200|W|research/rome02_mid_whole_plan.md, R15, R16|
|republic_middle_city / `rome02_mid_whole_largo_a_early`|135.628–137.228|135–200|前135; 後146–200|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_largo_c_early`|135.314–136.914|135–200|前135; 後146–200|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_apollo_medicus_179`|136.139–137.739|135–145; 157–200|前135–136; 後157–200|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_juno_regina_179`|135.911–137.511|135–200|前135; 後146–200|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_janus_early`|136.419–138.019|135–145; 158–200|前135–136; 後158–200|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_juno_sospita_194`|136.518–138.118|135–144; 158–200|前135–136; 後158–200|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_spes_early`|136.261–137.861|135–144; 158–200|前135–136; 後158–200|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_diana_aventine`|137.543–139.143|135–143; 159–199|前135–137; 後159–199|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_ceres_aventine`|137.095–138.695|135–144; 158–200|前135–137; 後158–200|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_portunus_pre80`|136.698–138.298|140–144; 158–200|後158–200|W|research/rome02_mid_whole_plan.md, R15, R16|
|republic_middle_city / `rome02_mid_whole_largo_d_early_conditional`|135.619–137.219|135–200|前135; 後146–200|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_emporium_early_portico_1`|137.835–139.435|135–142; 160–180; 186–199|前135–137; 後160–180; 後186–199|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_emporium_early_portico_2`|138.030–139.630|135–141; 160–178; 186–199|前135–138; 後160–178; 後186–199|W|research/rome02_mid_whole_plan.md|
|republic_middle_city / `rome02_mid_whole_emporium_early_portico_3`|138.136–139.736|135–141; 160–176; 186–198|前135–138; 後160–176; 後186–198|W|research/rome02_mid_whole_plan.md|
|republic_pompey_observation / `curia_pompeia_east_frontage`|147.613–149.213|146–200; 216–217; 241–259; 276–350; 386–396; 433–447; 466–470|前146–147|W|research/rome02_pompey_refine_sources.md|
|republic_pompey_observation / `rome02_quarter_north_gallery`|147.521–149.121|146–200; 217; 242–258; 277–348; 387–396; 434–446; 466–470|前146–147|W|research/rome02_republic_quarter_sources.md|
|republic_pompey_observation / `rome02_quarter_south_gallery`|147.502–149.102|146–199; 217; 242–259; 277–349; 386–396; 433–447; 466–470|前146–147|W|research/rome02_republic_quarter_sources.md|
|republic_late_city / `pompey_theatre`|190.285–191.885|189–199; 242–258; 277–348; 387–396; 435–446; 466–471|前189–190|W|research/rome02_republic_whole_sources.md, R11|
|republic_late_city / `aemilia_warehouses`|192.560–194.160|189–199; 245–257; 277–343; 467–471|前189–192|W|research/rome_round12_platforms.md, R12, S100|
|republic_late_city / `fabricius_bridge`|190.704–192.304|189–200; 243–259; 276–354; 386–397; 432–447; 466–471|前189–190|W|research/rome02_republic_whole_sources.md, S100|
|republic_late_city / `cestio_bridge`|190.624–192.224|189–199; 243–258; 276–352; 387–396; 435–446; 467–471|前189–190|W|research/rome02_republic_whole_sources.md, S100|
|republic_late_city / `portunus_temple`|191.202–192.802|189–200; 243–259; 276–355; 386–397; 432–447; 466–471|前189–191|W|research/rome02_republic_whole_sources.md, S98|
|republic_late_city / `hercules_temple`|191.066–192.666|189–200; 243–259; 276–354; 386–396; 432–447; 466–468|前189–191|W|research/rome02_republic_whole_sources.md, S98|
|republic_late_city / `jupiter_capitolinus`|190.591–192.191|189–200; 215–217; 242–260; 276–361; 382–397; 412–420; 429–448; 466–471|前189–190|W|research/rome02_republic_whole_sources.md, R08|
|republic_late_city / `magna_mater_palatine`|191.336–192.936|189–200; 243–260; 268–361; 383–397; 412–419; 429–448; 466–471|前189–191; 後281–361; 後383–397; 後412–419; 後429–448; 後466–471|R|research/rome02_republic_whole_sources.md, R08|
|republic_late_city / `victoria_palatine`|191.450–193.050|189–200; 243–259; 268–361; 383–397; 412–419; 429–448; 466–471|前189–191; 後281–361; 後383–397; 後412–419; 後429–448; 後466–471|R|research/rome02_republic_whole_sources.md, R08|
|republic_late_city / `circus_maximus`|191.919–193.519|189–200; 243–259; 276–363; 382–397; 412–420; 428–448; 466–471|前189–191; 後282–363; 後382–397; 後412–420; 後428–448; 後466–471|R|research/rome02_republic_whole_sources.md, R22|
|republic_late_city / `julia_caesarean_working_hall`|191.379–192.979|189–201; 214–217; 242–370; 380–397; 412–421; 427–448; 466–471|前189–191; 後281–370; 後380–397; 後412–421; 後427–448; 後466–471|R|research/rome02_republic_whole_sources.md, R01, R03|
|republic_late_city / `paulli_rebuilding`|191.055–192.655|189–201; 214–217; 242–372; 379–397; 411–421; 427–449; 457–458; 466–471|前189–191; 後281–372; 後379–397; 後411–421; 後427–449; 後457–458; 後466–471|R|research/rome02_republic_whole_sources.md, R04|
|republic_late_city / `castor_metellan`|191.138–192.738|189–201; 214–217; 242–371; 379–397; 411–421; 427–449; 466–471|前189–191; 後281–371; 後379–397; 後411–421; 後427–449; 後466–471|R|research/rome02_republic_whole_sources.md, R15, R16|
|republic_late_city / `saturn_preplancan`|190.929–192.529|189–201; 214–217; 242–267; 275–367; 381–397; 412–420; 428–448; 466–471|前189–190; 後281–367; 後381–397; 後412–420; 後428–448; 後466–471|R|research/rome02_republic_whole_sources.md, R15, R16|
|republic_late_city / `vesta_republican`|191.300–192.900|189–201; 214–216; 242–260; 267–280; 283–371; 379–397; 411–421; 427–449; 466–467|前189–191; 後283–371; 後379–397; 後411–421; 後427–449; 後466–467|R|research/rome02_republic_whole_sources.md, R17|
|republic_late_city / `tabularium_catulan`|190.805–192.405|189–201; 214–217; 242–266; 275–365; 382–397; 412–420; 428–448; 466–471|前189–190|W|research/rome02_republic_whole_sources.md, R07|
|republic_late_city / `forum_iulium_caesarean`|202.278–203.878|189–217; 242–268; 272–370; 381–397; 412–420; 428–471|前189–202; 後281–370; 後381–397; 後412–420; 後428–471|R|research/rome02_republic_whole_sources.md, R10|
|republic_late_city / `regia_republican`|191.556–193.156|189–201; 214–216; 242–260; 267–268; 275–398; 411–421; 426–449; 457; 466–471|前189–191; 後253–260; 後267–268; 後275–398; 後411–421; 後426–449; 後457; 後466–471|W|research/rome02_republic_whole_sources.md, R17|
|republic_late_city / `atrium_vestae_republican`|191.410–193.010|189–201; 214–216; 242–260; 268–372; 378–398; 411–421; 426–449; 466–471|前189–191; 後281–372; 後378–398; 後411–421; 後426–449; 後466–471|R|research/rome02_republic_whole_sources.md, R17|
|republic_late_city / `domus_publica_republican`|191.288–192.888|189–201; 214–216; 242–260; 267–268; 275–398; 411–421; 426–449; 457; 466–471|前189–191; 後281–398; 後411–421; 後426–449; 後457; 後466–471|R|research/rome02_republic_whole_sources.md, R17|
|republic_late_city / `pompey_gallery_north_west`|190.120–191.720|189–199; 242–258; 277–347; 387–396; 444; 466–471|前189–190|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `pompey_gallery_south_west`|190.424–192.024|189–199; 242–258; 277–348; 387–396; 434–446; 466–471|前189–190|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `pompey_gallery_west_cross`|190.352–191.952|189–199; 242–258; 277–347; 387–396; 466–471|前189–190|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `largo_a`|190.100–191.700|189–200; 216–217; 242–259; 276–350; 386–396; 433–447; 466–471|前189–190|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `largo_c`|190.186–191.786|189–200; 216–217; 242–259; 276–351; 386–396; 413–417; 432–447; 466–471|前189–190|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `largo_d`|190.166–191.766|189–200; 216–217; 242–259; 276–351; 386–396; 412–417; 432–447; 466–471|前189–190|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `largo_b`|189.993–191.593|189–200; 216–217; 242–259; 276–350; 386–396; 413; 433–447; 466–467|前189|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `porticus_metelli`|190.389–191.989|189–200; 215–217; 242–259; 276–355; 384–397; 412–419; 430–448; 466–471|前189–190; 後281–355; 後384–397; 後412–419; 後430–448; 後466–471|R|research/rome02_republic_whole_sources.md|
|republic_late_city / `minucia_vetus`|190.068–191.668|189–200; 215–217; 242–259; 276–352; 385–396; 412–418; 432–447; 466–471|前189–190|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `apollo_medicus`|190.425–192.025|189–200; 242–259; 276–355; 385–397; 412–417; 431–447; 466–471|前189–190; 後252–259; 後276–355; 後385–397; 後412–417; 後431–447; 後466–471|R|research/rome02_republic_whole_sources.md|
|republic_late_city / `janus_holitorium`|190.776–192.376|189–200; 243–259; 276–356; 385–397; 431–447; 466–471|前189–190|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `juno_sospita`|190.988–192.588|189–200; 243–259; 276–355; 386–397; 431–447; 466–471|前189–190|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `spes_holitorium`|190.764–192.364|189–200; 243–259; 276–355; 386–397; 432–447; 466–471|前189–190; 後254–259; 後276–355; 後386–397; 後432–447; 後466–471|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `ceres_aventine_schematic`|191.445–193.045|189–200; 243–259; 276–354; 386–396; 432–447; 466–471|前189–191; 後254–259; 後276–354; 後386–396; 後432–447; 後466–471|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `diana_aventine_schematic`|192.156–193.756|189–199; 244–258; 276–350; 390–392; 467–471|前189–192|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `galbana_republican`|192.917–194.517|189–199; 245–257; 278–306; 315–339; 467–471|前189–192|W|research/rome02_republic_whole_sources.md|
|republic_late_city / `servian_corridor_1_1_0`|193.464–195.064|199; 247–250; 257–258; 277–279; 340–361; 386–397; 467|—|Q|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_1_1`|193.383–194.983|199; 247–250; 257–258; 277–279; 339–361; 386–397; 467|—|Q|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_1_2`|193.677–195.277|199; 247–250; 257–258; 277–279; 339–361; 386–397; 467|—|Q|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_1_3`|193.356–194.956|199; 247–250; 256–258; 277–279; 339–361; 386–397; 467|—|Q|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_1_4`|193.515–195.115|199; 246–251; 256–258; 277–279; 338–362; 386–397; 467|—|Q|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_2_0`|193.524–195.124|189–199; 245–258; 277–280; 297–300; 326–362; 386–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_2_1`|193.596–195.196|189–199; 245–258; 277–280; 297–301; 325–362; 386–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_2_2`|193.441–195.041|189–199; 245–258; 277–280; 296–301; 325–362; 386–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_2_3`|193.277–194.877|189–199; 245–258; 277–280; 296–301; 325–363; 386–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_2_4`|193.447–195.047|189–199; 245–258; 277–280; 296–302; 325–363; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_3_0`|193.393–194.993|189–199; 245–258; 277–280; 296–301; 325–363; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_3_1`|193.404–195.004|189–199; 245–258; 277–280; 296–301; 325–364; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_3_2`|193.342–194.942|189–199; 245–258; 277–280; 295–302; 325–365; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_3_3`|193.626–195.226|189–199; 245–258; 277–280; 295–302; 324–365; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_3_4`|193.248–194.848|189–199; 245–259; 277–280; 295–302; 324–365; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_4_0`|193.472–195.072|189–199; 245–259; 277–280; 296–301; 325–365; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_4_1`|193.405–195.005|189–199; 245–259; 277–280; 296–301; 325–365; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_4_2`|193.327–194.927|189–199; 245–259; 277–280; 296–302; 325–365; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_4_3`|193.601–195.201|189–199; 245–259; 277–280; 295–302; 324–365; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_1_4_4`|193.564–195.164|189–199; 245–259; 277–280; 295–302; 324–366; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_1_0`|193.185–194.785|189–199; 245–259; 277–280; 293–304; 322–366; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_1_1`|193.384–194.984|189–199; 245–259; 277–280; 293–304; 322–366; 385–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_1_2`|193.258–194.858|189–199; 245–259; 277–280; 292–304; 322–366; 384–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_1_3`|193.632–195.232|189–199; 245–259; 277–280; 292–304; 322–366; 384–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_1_4`|193.556–195.156|189–199; 245–259; 277–280; 292–304; 321–366; 384–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_1_5`|193.318–194.918|189–199; 245–259; 277–280; 291–304; 321–366; 384–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_1_6`|193.507–195.107|189–199; 245–259; 277–280; 291–304; 321–366; 384–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_2_0`|193.244–194.844|189–199; 245–259; 277–280; 290–304; 320–366; 384–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_2_1`|193.578–195.178|189–199; 245–259; 277–280; 291–304; 320–366; 384–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_2_2`|193.315–194.915|189–199; 245–259; 277–280; 290–304; 319–366; 384–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_2_3`|193.181–194.781|189–199; 245–259; 277–280; 290–305; 319–366; 384–397; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_2_4`|193.159–194.759|189–199; 245–259; 277–280; 290–305; 316–367; 384–397; 452–454; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_2_5`|193.615–195.215|189–199; 245–259; 277–280; 289–305; 315–367; 384–397; 450–454; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_2_6`|193.209–194.809|189–199; 245–259; 277–280; 289–305; 315–367; 384–397; 450–455; 467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_3_0`|193.476–195.076|199; 246–252; 255–259; 277–280; 328–367; 384–397; 450–455; 467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_3_1`|193.465–195.065|199; 246–252; 255–259; 277–279; 328–367; 383–397; 450–455; 467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_3_2`|193.562–195.162|199; 246–259; 277–280; 327–367; 383–397; 450–455; 467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_3_3`|193.260–194.860|199; 246–259; 277–280; 327–367; 383–397; 450–455; 467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_3_4`|193.457–195.057|199–200; 246–259; 277–280; 327–367; 383–397; 449–455; 467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_3_5`|193.283–194.883|199–200; 246–259; 277–280; 326–367; 383–397; 449–455; 467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_4_0`|193.585–195.185|199–200; 246–251; 256–259; 277–279; 328–367; 383–397; 449–455; 467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_4_1`|193.133–194.733|199–200; 246–251; 256–259; 276–279; 328–368; 383–397; 449–455; 467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_4_2`|193.356–194.956|199–200; 246–252; 256–259; 276–279; 328–368; 383–397; 449–455; 467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_4_3`|193.358–194.958|199–200; 246–252; 255–259; 276–279; 327–368; 382–397; 449–455; 467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_4_4`|193.415–195.015|199–200; 246–259; 276–280; 326–368; 382–397; 449–455; 466–467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_2_4_5`|193.486–195.086|199–200; 246–259; 276–280; 326–369; 382–397; 449–455; 466–467|—|N|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_3_1_0`|193.487–195.087|189–200; 244–259; 276–280; 284–307; 314–372; 381–397; 449–455; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_3_1_1`|193.226–194.826|189–200; 244–259; 276–280; 283–307; 314–373; 381–397; 448–455; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_3_1_2`|193.500–195.100|189–200; 244–259; 276–280; 283–307; 314–375; 381–397; 448–455; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_3_1_3`|193.277–194.877|189–200; 244–259; 276–280; 283–307; 314–376; 380–398; 448–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_3_2_0`|193.036–194.636|189–200; 244–259; 276–280; 285–307; 314–377; 379–398; 448–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_3_2_1`|192.991–194.591|189–200; 244–259; 276–280; 285–307; 314–398; 448–456; 466–467|前189–192|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_3_2_2`|193.434–195.034|189–200; 244–259; 276–280; 285–307; 314–398; 413–417; 448–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_1_0`|193.029–194.629|189–200; 244–259; 276–308; 313–398; 412–418; 446–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_1_1`|193.238–194.838|189–200; 244–259; 276–308; 313–398; 412–418; 435–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_1_2`|193.046–194.646|189–200; 244–259; 276–309; 313–398; 412–418; 434–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_1_3`|193.091–194.691|189–200; 244–259; 276–309; 313–398; 412–418; 433–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_1_4`|193.210–194.810|189–200; 244–259; 276–309; 313–398; 412–418; 433–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_2_0`|193.071–194.671|189–200; 244–259; 276–280; 284–308; 313–398; 412–419; 433–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_2_1`|193.199–194.799|189–200; 244–259; 276–280; 284–308; 313–398; 412–419; 432–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_2_2`|193.195–194.795|189–200; 244–259; 276–280; 283–309; 313–398; 412–419; 432–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_2_3`|193.269–194.869|189–200; 244–259; 276–280; 283–309; 313–398; 412–419; 432–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_2_4`|193.243–194.843|189–200; 244–259; 276–280; 283–309; 313–398; 412–419; 432–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_3_0`|193.217–194.817|189–200; 214; 244–259; 276–309; 312–398; 412–419; 431–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_3_1`|193.219–194.819|189–200; 214; 243–259; 276–310; 312–398; 412–419; 431–456; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_3_2`|192.967–194.567|189–200; 214; 243–259; 276–310; 312–398; 412–419; 431–457; 466–467|前189–192|W|research/rome02_republic_whole_sources.md, R21|
|republic_late_city / `servian_corridor_4_3_3`|193.109–194.709|189–200; 214; 243–259; 276–310; 312–399; 412–419; 431–457; 466–467|前189–193|W|research/rome02_republic_whole_sources.md, R21|
|republic_civic_dedications / `curia_iulia`|261.315–262.915|261–268; 275–370; 381–397; 412–420; 428–449; 457–470|前261|W|Approved03 single-building model;dedicated 29BCE,observed together in28BCE;not a claim both built in|
|republic_civic_dedications / `apollo_palatine`|269.561–271.161|269–361; 383–397; 412–419; 429–448; 466–470|前269|W|Approved03 single-building model;dedicated 28BCE,observed together in28BCE;not a claim both built in|
|imperial_height / `nero_valley_lake_schematic`|398.929–400.129|280–457; 466–470|前280–398; 後413–457; 後466–470|R|research/rome03_lake_outline_report.md|
|imperial_height / `colosseum`|413.492–414.692|280–457; 466–470|前280–413|B|research/imperial_sample_sources.md, S86|
|imperial_height / `basilica_iulia`|281.164–282.364|280–371; 380–397; 412–421; 427–449; 458; 466–470|前280–281|W|research/forum_palatine_sources.md, S92, research/early_imperial_sample_sources.md|
|imperial_height / `castor_pollux`|281.350–282.550|280–372; 379–397; 411–421; 427–449; 458; 466–470|前280–281|W|research/imperial_sample_sources.md, S89, research/early_imperial_sample_sources.md|
|imperial_height / `horrea_agrippiana`|281.505–282.705|280–365; 381–397; 412–420; 427–448; 466–470|前280–281|W|research/early_imperial_sample_sources.md, S120|
|imperial_height / `saturn_temple`|281.058–282.258|280–367; 381–397; 412–420; 428–448; 466–470|前280–281|W|research/imperial_sample_sources.md, S89, S98|
|imperial_height / `vesta_temple`|280.765–281.965|280; 283–371; 379–397; 411–421; 427–449; 466–467|前280; 後356–371; 後379–397; 後411–421; 後427–449; 後466–467|R|S98|
|imperial_height / `marcellus_theatre`|282.412–283.612|280–358; 384–397; 412–419; 430–448; 466–470|前280–282|W|S96|
|imperial_height / `balbus_theatre`|282.458–283.658|280–353; 385–397; 412–418; 431–447; 466–470|前280–282|W|S96|
|imperial_height / `augustus_mausoleum`|285.321–286.521|280–345; 466–470|前280–285|W|S100|
|imperial_height / `octavia_portico`|282.255–283.858|280–356; 384–397; 412–419; 430–448; 466–470|前280–282|W|S98, S100|
|imperial_height / `crypta_balbi`|282.392–283.592|280–354; 384–397; 412–418; 431–448; 466–470|前280–282|W|S98, S100, S96|
|imperial_height / `saepta_iulia`|283.374–284.574|280–352; 385–396; 412–418; 432–447; 466–470|前280–283|W|S98, S100|
|imperial_height / `magna_mater_palatine`|281.326–282.526|280–361; 383–397; 412–419; 429–448; 466–470|前280–281|W|S114|
|imperial_height / `victoria_palatine`|281.463–282.663|280–361; 383–397; 412–419; 429–448; 466–470|前280–281|W|S114|
|imperial_height / `circus_maximus`|282.367–283.567|280–363; 382–397; 412–420; 428–448; 466–470|前280–282|W|research/ad14_public_sources.md, AP01, AP04|
|imperial_height / `basilica_aemilia`|281.049–282.249|280–373; 378–398; 411–421; 427–452; 456–458; 466–470|前280–281|W|research/ad14_public_sources.md, AP02, AP05, AP16|
|imperial_height / `caesar_forum`|281.258–282.458|280–370; 381–397; 412–420; 428–470|前280–281|W|research/ad14_public_sources.md, AP03, AP06, S119, S136|
|imperial_height / `augustus_forum`|281.443–282.643|280–398; 411–421; 427–470|前280–281|W|research/ad14_public_sources.md, AP12, AP13, S119, S136|
|imperial_height / `agrippa_baths`|282.694–283.894|280–350; 386–396; 433–447; 466–470|前280–282|W|research/ad14_campus_completion_sources.md|
|imperial_height / `diribitorium`|282.978–284.178|280–352; 385–397; 412–418; 432–447; 466–470|前280–282|W|research/ad14_campus_completion_sources.md|
|imperial_height / `porticus_liviae`|283.149–284.349|280–402; 412–420; 429–457; 466–470|前280–283; 後450–457; 後466–470|O|research/ad14_campus_completion_sources.md|
|imperial_height / `pantheon_agrippa`|283.369–284.569|280–348; 387–396; 435–446; 466–470|前280–283|W|research/ad14_campus_completion_sources.md|
|imperial_height / `naumachia_augusti`|284.373–285.573|280–348; 467–470|前280–284|W|research/ad14_campus_completion_sources.md|
|imperial_height / `atrium_vestae_early`|281.075–282.275|280–374; 376–398; 411–421; 426–449; 457; 466–470|前280–281|W|research/ad14_hill_completion_sources.md|
|imperial_height / `domus_augustus_surface_proxy`|282.181–283.381|280–360; 383–397; 412–419; 429–448; 466–470|前280–282|W|research/ad14_hill_completion_sources.md, HA1, HA4|
|imperial_height / `apollo_library_early_single_hall`|282.093–283.293|280–360; 383–397; 412–419; 429–448; 466–470|前280–282; 後435–448; 後466–470|P|research/ad14_hill_completion_sources.md, HL1, HL4|
|imperial_height / `livia_western_registered`|281.497–282.697|280–361; 383–397; 412–419; 428–448; 466–470|前280–281|W|research/livia_western_sample_sources.md, S125, research/ad14_hill_completion_controls.json|
|imperial_height / `ad14_service_campus_yard_00`|282.431–283.631|280–356; 384–397; 412–419; 430–448; 458–470|前280–282|W|S130, S131|
|imperial_height / `forum_civic_paving_01`|281.371–282.571|280–373; 379–397; 411–421; 427–449; 457–458; 465–470|前280–281|W|S119|
|imperial_height / `augustus_northwest_small_exedra`|281.643–282.843|280–369; 381–397; 412–420; 428–470|前280–281; 後456–470|R|research/ad14_public_sources.md, AP12, AP13, S119, S136|
|imperial_height / `peace_temple`|416.564–417.764|280–398; 409–422; 425–470|前280–398; 前409–416|F|S98, E14|
|imperial_height / `domus_flavia`|438.318–439.518|280–369; 380–398; 411–421; 427–448; 466–470|前280–369; 前380–398; 前411–421; 前427–438|P|S90, S97, S113|
|imperial_height / `domus_augustana_upper`|438.264–439.464|280–367; 381–398; 412–421; 427–448; 466–470|前280–367; 前381–398; 前412–421; 前427–438|P|S97, S113, S120|
|imperial_height / `domus_augustana_lower`|438.724–439.924|280–361; 383–397; 412–419; 429–448; 466–470|前280–361; 前383–397; 前412–419; 前429–438|P|S97|
|imperial_height / `palatine_stadium`|438.640–439.840|280–363; 382–397; 412–420; 428–448; 466–470|前280–363; 前382–397; 前412–420; 前428–438|P|S97|
|imperial_height / `vigna_barberini_flavian`|439.086–440.286|280–452; 456–457; 466–470|前280–439|P|S112|
|imperial_height / `augustana_circus_loggia`|439.046–440.246|280–359; 383–397; 412–419; 429–448; 466–470|前280–359; 前383–397; 前412–419; 前429–439|P|S121|
|imperial_height / `basilica_ulpia`|459.161–460.361|280–367; 382–397; 412–420; 428–449; 456–470|前280–367; 前382–397; 前412–420; 前428–449; 前456–459|F|research/imperial_sample_sources.md, S88|
|imperial_height / `trajan_column`|458.916–460.116|298–361; 383–397; 412–419; 429–448; 457–466|前298–361; 前383–397; 前412–419; 前429–448; 前457–458|F|research/imperial_sample_sources.md, S91|
|imperial_height / `trajan_markets`|460.712–461.912|280–371; 380–397; 412–420; 428–470|前280–371; 前380–397; 前412–420; 前428–460|F|S98|
|imperial_height / `trajan_forum_porticoes`|459.780–460.980|280–371; 380–397; 412–420; 428–470|前280–371; 前380–397; 前412–420; 前428–459|F|S98, S83|
|imperial_height / `augustus_southwest_small_exedra`|281.285–282.485|280–372; 380–397; 412–421; 427–470|前280–281; 後437–470|R|research/ad14_public_sources.md, AP12, AP13, S119, S136, E12|
|imperial_height / `nerva_forum`|441.677–442.877|280–398; 411–421; 427–470|前280–398; 前411–421; 前427–441|F|S98, S144, E13, research/rome_restart_nerva_fix.md|
|imperial_height / `trajan_baths`|450.457–451.657|280–457; 466–470|前280–450|O|S99|
|another_centre / `rome04_basilica_iulia`|469.479–470.679|469–481; 496–518; 525; 560–573; 583–642; 644–657; 703–720|前469|W|research/forum_palatine_sources.md, S92, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castor_pollux`|469.217–470.417|469–481; 496–517; 525; 560–573; 583–657; 704–720|前469|W|research/imperial_sample_sources.md, S89, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_colosseum`|469.920–471.120|469–481; 496–517; 559–573; 583–656; 704–720|前469|W|research/imperial_sample_sources.md, S86, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_circus_maximus`|470.174–471.374|469–481; 496–525; 538–539; 559–572; 583–640; 647–661; 704–720|前469–470|W|research/imperial_sample_sources.md, S87, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_basilica_ulpia`|469.763–470.963|469–481; 495–518; 524–526; 560–573; 583–657; 704–720|前469|W|research/imperial_sample_sources.md, S88, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_trajan_column`|469.676–470.876|481; 495–496; 560–573; 583; 591–625; 638–656; 705–711|—|Q|research/imperial_sample_sources.md, S91, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_domus_flavia`|469.867–471.067|469–481; 496–517; 525; 559–573; 583–641; 646–658; 703–720|前469|W|S90, S97, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_domus_augustana_upper`|469.958–471.158|469–481; 496–517; 525; 559–573; 583–641; 646–658; 704–720|前469|W|S97, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_domus_augustana_lower`|469.873–471.073|469–481; 496–517; 525; 559–572; 583–640; 648–658; 704–720|前469|W|S97, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_domus_tiberiana`|469.584–470.784|469–481; 496–517; 525; 560–573; 583–642; 645–658; 703–720|前469|W|S97, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_palatine_stadium`|470.029–471.229|469–481; 496–517; 525; 559–572; 583–640; 647–658; 704–720|前469–470|W|S97, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_jupiter_capitolinus`|469.304–470.504|469–481; 496–525; 560–572; 583–640; 647–658; 703–720|前469|W|S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_curia_iulia`|469.306–470.506|469–481; 496–517; 525; 560–573; 583–657; 704–720|前469|W|LA30|
|another_centre / `rome04_basilica_aemilia`|469.552–470.752|469–481; 496–517; 525; 560–573; 583–657; 704–720|前469|W|research/imperial_sample_sources.md, S88, S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_saturn_temple`|469.245–470.445|469–481; 496–518; 524–525; 560–573; 583–641; 646–657; 704–720|前469|W|research/imperial_sample_sources.md, S89, S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_vespasian_temple`|469.419–470.619|469–481; 496–518; 523–525; 560–573; 583–641; 645–657; 704–720|前469|W|research/imperial_sample_sources.md, S89, S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_vesta_temple`|469.503–470.703|480–481; 496–498; 516; 560–573; 583–642; 644–657; 704–720|—|N|S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_atrium_vestae`|469.506–470.918|469–481; 496–517; 525; 560–573; 583–657; 704–720|前469|W|S97, S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_titus_arch`|469.467–470.667|481; 496–497; 559–573; 583–657; 704–720|—|Q|S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_trajan_markets`|469.752–470.952|469–481; 495–517; 525–526; 560–573; 583–656; 704–720|前469|W|S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_caesar_forum`|469.276–470.476|469–481; 495–518; 525–526; 560–573; 583–657; 704–720|前469; 後503–518; 後525–526; 後560–573; 後583–657; 後704–720|R|S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_augustus_forum`|469.442–470.642|469–481; 495–517; 525–526; 560–573; 583–657; 704–720|前469|W|S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_nerva_forum`|469.196–470.396|469–481; 495–517; 525; 560–573; 583–657; 704–720|前469|W|S98, S144, E13, research/rome_restart_nerva_fix.md, LA32|
|another_centre / `rome04_peace_temple`|469.525–470.725|469–481; 495–517; 525; 560–573; 583–657; 704–720|前469|W|S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_marcellus_theatre`|469.818–471.018|469–481; 496–525; 537; 560–572; 583–639; 648–659; 680–684; 702–720|前469|W|S96, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_pompey_theatre`|470.421–471.621|469–481; 496–526; 536–537; 561–572; 583–606; 621–639; 649–660; 679–686; 701–720|前469–470|W|S96, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_balbus_theatre`|469.883–471.083|469–481; 496–525; 536–537; 561–572; 583–611; 619–639; 648–658; 702–720|前469|W|S96, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_domitian_stadium`|470.453–471.653|469–482; 495–536; 561–572; 583–604; 622–640; 647–658; 703–720|前469–470|W|S96, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_trajan_baths`|470.376–471.576|469–481; 496–516; 526; 560–573; 582–656; 705–720|前469–470|W|S99, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_augustus_mausoleum`|471.383–472.583|469–534; 561–573; 583–603; 622–656; 705–720|前469–471|W|S100, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_aemilia_warehouses`|471.374–472.574|469–480; 497–516; 560–572; 585–601; 623–636; 655; 706–720|前469–471|W|research/rome_round12_platforms.md, R12, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_fabricius_bridge`|470.016–471.216|469–481; 496–525; 537; 560–572; 583–613; 618–638; 650–659; 680–685; 702–720|前469–470|W|S100, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_cestio_bridge`|469.935–471.135|469–481; 496–525; 537; 561–572; 584–612; 619–638; 651–660; 678–687; 701–720|前469|W|S100, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_pompey_portico`|470.380–471.580|469–481; 496–526; 536–537; 561–572; 583–608; 620–639; 648–659; 681–684; 702–720|前469–470|W|S98, S100, S96, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_octavia_portico`|470.038–471.238|469–481; 496–525; 536–537; 560–572; 583–639; 648–659; 682; 702–720|前469–470|W|S98, S100, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_crypta_balbi`|469.790–470.990|469–481; 496–525; 561–572; 583–613; 618–640; 647–658; 703–720|前469|W|S98, S100, S96, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_saepta_iulia`|469.875–471.101|469–481; 495–526; 535; 561–573; 583–610; 619–658; 703–720|前469|W|S98, S100, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_ludus_magnus`|470.449–471.649|469–481; 496–516; 560–573; 583–656; 705–720|前469–470|W|S97, S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_horrea_galbana`|471.293–472.493|469–480; 497–516; 560–572; 587–598; 623–636; 708–720|前469–471|W|S97, S95, S100, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_emporium_vaults_east`|470.877–472.077|469–480; 497–516; 560–572; 586–600; 623–636; 707–720|前469–470|W|S100, S95, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_emporium_vaults_south`|471.402–472.602|469–480; 498–515; 561–571; 625–635; 709–720|前469–471|W|S100, S95, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_regola_domitian_warehouses`|470.278–471.478|469–481; 496–525; 536–537; 561–572; 584–606; 621–638; 651–660; 677–687; 701–720|前469–470|W|S100, S83, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_portunus_temple`|469.689–470.889|469–481; 496–525; 537–538; 560–572; 583–638; 650–659; 681–683; 703–720|前469|W|research/imperial_sample_sources.md, S89, S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_hercules_temple`|469.930–471.130|479–481; 496–500; 511–525; 537–538; 560–572; 584–638; 650–659; 703–720|—|N|S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_apollo_palatine`|469.645–470.845|469–481; 496–517; 525; 560–572; 583–640; 648–658; 704–720|前469|W|research/imperial_sample_sources.md, S89, S98, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_agrippa_baths`|470.360–471.560|469–481; 495–526; 535; 561–572; 583–608; 620–640; 647–658; 703–720|前469–470|W|S97, S102, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_nero_baths`|470.637–471.837|469–482; 495–527; 534–535; 561–573; 583–606; 621–641; 645–658; 703–720|前469–470|W|S97, S102, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_trajan_forum_porticoes`|469.276–470.476|469–481; 495–518; 525–526; 560–573; 583–657; 704–720|前469|W|S98, S83, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_vigna_barberini_flavian`|469.721–470.921|469–481; 496–517; 525; 559–573; 583–657; 703–720|前469|W|S112, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_victoria_palatine`|469.705–470.905|469–481; 496–518; 525; 560–572; 583–640; 648–658; 703–720|前469|W|S114, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_apollo_library_halls`|470.057–471.257|469–481; 496–517; 525; 560–572; 583–639; 648–658; 704–720|前469–470|W|S115, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_paedagogium_palatine`|469.873–471.073|469–481; 496–518; 525; 538; 560–572; 583–639; 648–658; 704–720|前469|W|S116, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_domitian_forum_entrance`|469.504–470.704|469–481; 496–517; 525; 560–573; 583–641; 646–657; 704–720|前469|W|S117, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_pantheon_hadrian`|470.372–471.572|469–481; 495–526; 534–535; 561–573; 583–607; 620–641; 646–657; 704–720|前469–470|W|research/rome04_lateantique_whole_basis.md, LA14, S101|
|another_centre / `rome04_hadrian_mausoleum`|471.347–472.547|469–482; 495–535; 563–572; 583–596; 624–639; 707–720|前469–471|W|research/rome04_lateantique_whole_basis.md|
|another_centre / `rome04_caracalla_baths`|471.205–472.405|469–481; 497–517; 539–540; 558–572; 583–613; 619–640; 708–720|前469–471|W|research/rome04_lateantique_whole_basis.md, LA15, LA32|
|another_centre / `rome04_caelian_domus`|470.762–471.962|469–481; 496–516; 560–572; 583–651; 707–720|前469–470|W|research/rome04_lateantique_whole_basis.md, LA09, LA22, LA04|
|another_centre / `rome04_venus_roma_hadrian`|469.659–470.859|469–481; 496–517; 559–573; 583–657; 704–720|前469; 後503–517; 後559–573; 後583–657; 後704–720|R|research/rome04_lateantique_whole_basis.md, LA32|
|another_centre / `rome04_castra_barrack_01_1`|471.741–472.941|469–481; 495–515; 574–615; 618–651; 710–720|前469–471; 後503–515; 後574–615; 後618–651; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_01_2`|471.991–473.191|469–481; 496–515; 574–612; 618–650; 710–720|前469–471; 後503–515; 後574–612; 後618–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_01_3`|471.866–473.066|469–481; 496–515; 574–610; 619–650; 710–720|前469–471; 後503–515; 後574–610; 後619–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_01_4`|472.250–473.450|469–481; 496–515; 574–608; 619–650; 711–720|前469–472; 後503–515; 後574–608; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_02_1`|471.633–472.833|469–481; 495–515; 574–615; 618–651; 710–720|前469–471; 後503–515; 後574–615; 後618–651; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_02_2`|472.049–473.249|469–481; 495–515; 574–612; 618–650; 710–720|前469–472; 後503–515; 後574–612; 後618–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_02_3`|471.966–473.166|469–481; 496–515; 574–610; 619–650; 710–720|前469–471; 後503–515; 後574–610; 後619–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_02_4`|472.172–473.372|469–481; 496–515; 574–607; 619–650; 711–720|前469–472; 後503–515; 後574–607; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_03_1`|471.939–473.139|469–481; 495–515; 574–614; 618–650; 710–720|前469–471; 後503–515; 後574–614; 後618–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_03_2`|472.056–473.256|469–481; 495–515; 574–612; 618–650; 710–720|前469–472; 後503–515; 後574–612; 後618–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_03_3`|471.922–473.122|469–481; 495–515; 574–609; 619–650; 711–720|前469–471; 後503–515; 後574–609; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_03_4`|472.225–473.425|469–481; 496–515; 574–607; 619–650; 711–720|前469–472; 後503–515; 後574–607; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_04_1`|471.891–473.091|469–481; 495–515; 574–614; 618–650; 710–720|前469–471; 後503–515; 後574–614; 後618–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_04_2`|472.086–473.286|469–481; 495–515; 574–611; 618–650; 710–720|前469–472; 後503–515; 後574–611; 後618–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_04_3`|472.283–473.483|469–481; 495–515; 574–609; 619–650; 711–720|前469–472; 後503–515; 後574–609; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_04_4`|472.102–473.302|469–481; 495–515; 574–606; 619–650; 711–720|前469–472; 後503–515; 後574–606; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_05_1`|472.055–473.255|469–481; 495–515; 574–613; 618–650; 710–720|前469–472; 後503–515; 後574–613; 後618–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_05_2`|471.848–473.048|469–481; 495–515; 574–611; 619–650; 710–720|前469–471; 後503–515; 後574–611; 後619–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_05_3`|472.144–473.344|469–481; 495–515; 574–608; 619–650; 711–720|前469–472; 後503–515; 後574–608; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_05_4`|471.933–473.133|469–481; 495–515; 574–606; 619–650; 711–720|前469–471; 後503–515; 後574–606; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_06_1`|471.913–473.113|469–481; 495–515; 574–613; 618–650; 710–720|前469–471; 後503–515; 後574–613; 後618–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_06_2`|471.956–473.156|469–481; 495–515; 574–610; 619–650; 710–720|前469–471; 後503–515; 後574–610; 後619–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_06_3`|471.947–473.147|469–481; 495–515; 574–608; 619–650; 711–720|前469–471; 後503–515; 後574–608; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_06_4`|472.190–473.390|469–481; 495–515; 574–605; 619–650; 711–720|前469–472; 後503–515; 後574–605; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_07_1`|471.830–473.030|469–481; 495–515; 574–612; 618–650; 710–720|前469–471; 後503–515; 後574–612; 後618–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_07_2`|472.120–473.320|469–481; 495–515; 574–610; 619–650; 710–720|前469–472; 後503–515; 後574–610; 後619–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_07_3`|472.102–473.302|469–481; 495–515; 574–608; 619–650; 711–720|前469–472; 後503–515; 後574–608; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_07_4`|472.104–473.304|469–481; 495–515; 574–605; 619–650; 711–720|前469–472; 後503–515; 後574–605; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_08_1`|471.693–472.893|469–481; 495–515; 574–612; 618–650; 710–720|前469–471; 後503–515; 後574–612; 後618–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_08_2`|472.012–473.212|469–481; 495–515; 574–610; 619–650; 710–720|前469–472; 後503–515; 後574–610; 後619–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_08_3`|471.970–473.170|469–481; 495–515; 574–607; 619–650; 711–720|前469–471; 後503–515; 後574–607; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_08_4`|472.392–473.592|469–481; 495–515; 574–604; 619–650; 711–720|前469–472; 後503–515; 後574–604; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_09_1`|472.087–473.287|469–481; 495–515; 574–612; 618–650; 710–720|前469–472; 後503–515; 後574–612; 後618–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_09_2`|472.017–473.217|469–481; 495–515; 574–609; 619–650; 710–720|前469–472; 後503–515; 後574–609; 後619–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_09_3`|472.370–473.570|469–481; 495–515; 574–607; 619–650; 711–720|前469–472; 後503–515; 後574–607; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_09_4`|472.087–473.287|469–481; 495–515; 574–604; 619–650; 711–720|前469–472; 後503–515; 後574–604; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_10_1`|471.818–473.018|469–481; 495–515; 574–611; 619–650; 710–720|前469–471; 後503–515; 後574–611; 後619–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_10_2`|472.030–473.230|469–481; 495–515; 574–609; 619–650; 711–720|前469–472; 後503–515; 後574–609; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_10_3`|472.310–473.510|469–481; 495–515; 574–606; 619–650; 711–720|前469–472; 後503–515; 後574–606; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_10_4`|472.251–473.451|469–481; 495–515; 574–604; 620–650; 711–720|前469–472; 後503–515; 後574–604; 後620–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_11_1`|471.872–473.072|469–481; 495–515; 574–611; 619–650; 710–720|前469–471; 後503–515; 後574–611; 後619–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_11_2`|472.137–473.337|469–481; 495–515; 574–609; 619–650; 711–720|前469–472; 後503–515; 後574–609; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_11_3`|471.943–473.143|469–481; 495–515; 574–606; 619–650; 711–720|前469–471; 後503–515; 後574–606; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_11_4`|472.251–473.451|469–481; 495–515; 574–603; 620–650; 711–720|前469–472; 後503–515; 後574–603; 後620–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_12_1`|471.768–472.968|469–481; 495–515; 574–610; 619–650; 710–720|前469–471; 後503–515; 後574–610; 後619–650; 後710–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_12_2`|471.916–473.116|469–481; 495–515; 574–608; 619–650; 711–720|前469–471; 後503–515; 後574–608; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_12_3`|472.204–473.404|469–481; 495–515; 574–605; 619–650; 711–720|前469–472; 後503–515; 後574–605; 後619–650; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_castra_barrack_12_4`|472.399–473.599|469–481; 495–515; 574–603; 620–649; 711–720|前469–472; 後503–515; 後574–603; 後620–649; 後711–720|W|S103, research/rome04_lateantique_survey.md, LA32|
|another_centre / `rome04_horrea_piperataria_proxy`|469.834–471.034|469–481; 496–517; 559–573; 583–656; 704–720|前469; 後503–517; 後559–573; 後583–656; 後704–720|R|research/rome04_lateantique_whole_basis.md, LA17|
|another_centre / `rome04_lateran_old_cavalry`|471.720–472.920|469–480; 497–516; 561–572; 583–647; 708–720|前469–471; 後503–516; 後561–572; 後583–647; 後708–720|R|LA06, LA32|
|another_centre / `rome04_caracalla_natatio`|470.990–472.190|469–480; 497–517; 539–540; 558–572; 583–609; 620–639; 709–720|前469–470|W|LA15, LA18|
|another_centre / `rome04_augustus_circus_obelisk`|469.970–471.170|481; 496; 538; 560–572; 583; 589–625; 637–638; 650–659; 705–712|—|Q|LA31|
|another_centre / `rome04_venus_roma_maxentius`|504.159–505.359|469–481; 496–517; 559–573; 583–657; 704–720|前469–481; 前496–504|B|research/rome04_lateantique_whole_basis.md, LA32|
|another_centre / `rome04_diocletian_baths`|505.206–506.406|469–482; 495–516; 527–534; 563–653; 708–720|前469–482; 前495–505|B|research/rome04_lateantique_whole_basis.md, LA18|
|another_centre / `rome04_basilica_nova_early`|504.029–505.229|469–481; 496–517; 559–573; 583–656; 704–720|前469–481; 前496–504; 後559–573; 後583–656; 後704–720|R|research/rome04_lateantique_whole_basis.md, LA17, LA32|
|another_centre / `rome04_constantine_arch`|504.118–505.318|473–481; 496–508; 510–517; 559–573; 583–656; 704–720|前473–481; 前496–504|N|research/rome04_lateantique_whole_basis.md, LA25|
|another_centre / `rome04_lateran_constantinian`|505.437–506.637|469–481; 497–516; 561–572; 583–647; 707–720|前469–481; 前497–505|B|research/rome04_lateantique_whole_basis.md, LA06|
|another_centre / `rome04_old_stpeter`|518.974–520.174|469–481; 496–533; 584–587; 627–636; 711–720|前469–481; 前496–518|N|research/rome04_lateantique_survey.md, LA06, LA13, S204|
|another_centre / `rome04_constantine_baths`|504.294–505.494|469–482; 494–517; 525–528; 533–534; 561–573; 582–656; 705–720|前469–482; 前494–504|C|research/rome04_lateantique_whole_basis.md, LA06|
|another_centre / `rome04_diocletian_natatio`|505.342–506.542|469–481; 495–516; 573–652; 709–720|前469–481; 前495–505|N|LA15, LA18|
|another_centre / `rome04_caesar_forum_303`|503.760–504.960|469–481; 495–518; 525–526; 560–573; 583–657; 704–720|前469–481; 前495–503|B|S98, research/rome04_lateantique_survey.md, LA32, LA30|
|another_centre / `rome04_constantius_obelisk`|550.860–552.060|481; 496; 538; 559–572; 583–626; 637–639; 650–657; 706–713|前481; 前496; 前538|Q|research/rome04_lateantique_whole_basis.md|
|another_centre / `rome04_basilica_nova`|550.991–552.191|469–481; 496–517; 559–573; 583–657; 704–720|前469–481; 前496–517|B|research/rome04_lateantique_whole_basis.md, LA17, LA32|
|another_centre / `rome_round12_obelisk330`|472.377–473.577|481; 496; 515–533; 585–587; 627–628; 635–636; 711–720|—|Q|R02, R03, S48, research/rome_round12_sites.md|
|another_centre / `rome_round12b_aelius330`|471.624–472.824|469–481; 495–535; 563–572; 583–596; 624–639; 657–659; 706–720|前469–471|W|research/rome_restart_lm02_bridge_audit.md, M03, research/rome_round12b_vatican_context.md|
|the_city_taken / `rome05_sack_janiculum_mill`|662.285–662.985|662–670; 708–720|前662|W|research/rome05_sack_complete_basis.md, M04, M02|
|the_city_taken / `rome_restart_tiber_boat_mill_537`|685.413–686.113|677–688; 700–709|前677–685|Q|research/rome_restart_boat_mill.md|
|people_return / `rome06_medieval_old_stpeter`|721.839–723.039|717–722; 727–797; 803–960; 1025–1057; 1079–1156; 1244–1283; 1308–1332; 1357–1374; 1410–1415; 1427–1433; 1543–1547; 1599|前717–721; 後1042–1057; 後1079–1156; 後1244–1283; 後1308–1332; 後1357–1374; 後1410–1415; 後1427–1433; 後1543–1547; 後1599|R|research/rome06_medieval_whole_basis.md, M18|
|people_return / `rome06_medieval_stpeter_atrium`|721.773–722.973|717–723; 726–797; 803–960; 1025–1057; 1079–1156; 1244–1283; 1308–1332; 1357–1375; 1410–1415; 1427–1433; 1543–1547; 1599|前717–721; 後1042–1057; 後1079–1156; 後1244–1283; 後1308–1332; 後1357–1375; 後1410–1415; 後1427–1433; 後1543–1547; 後1599|T|research/rome06_medieval_whole_basis.md, M18|
|people_return / `rome06_medieval_stpaul`|723.158–724.358|811–826; 1093–1104; 1117–1134; 1144–1155; 1263–1274; 1543–1547; 1557–1558|—|N|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04|
|people_return / `rome06_medieval_lateran`|720.935–722.135|717–746; 790–796; 810–826; 1093–1104; 1117–1134; 1145–1156; 1263–1282; 1375–1386; 1409–1416; 1427–1455; 1514–1517; 1540–1546; 1568|前717–720|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04, LA06|
|people_return / `rome06_medieval_maggiore`|720.210–721.410|717–752; 789–798; 809–828; 1093–1105; 1117–1134; 1145–1161; 1211–1214; 1263–1284; 1300–1306; 1335–1342; 1373–1389; 1392–1399; 1409–1416; 1426–1455; 1477–1494; 1511–1516; 1541–1546; 1573|前717–720|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04|
|people_return / `rome06_medieval_trastevere_church`|719.783–720.983|717–750; 789–802; 809–830; 855–864; 993–1001; 1056–1061; 1071–1079; 1091–1157; 1227–1278; 1332; 1372–1375; 1411–1417; 1427–1433; 1514–1515; 1542–1547|前717–719|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04, M26, M27|
|people_return / `rome06_medieval_s_crisogono`|719.331–720.531|717–750; 789–802; 809–830; 856–861; 1024; 1056–1063; 1068–1079; 1091–1137; 1140–1158; 1227–1282; 1307; 1333; 1356; 1372–1376; 1410–1435; 1455–1476; 1514–1515; 1542–1547|前717–719|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04|
|people_return / `rome06_medieval_s_sabina`|719.724–720.924|717–747; 790–798; 809–829; 1057–1062; 1069–1078; 1092–1113; 1115–1136; 1141–1158; 1228–1244; 1263–1277; 1374–1376; 1410–1418; 1426–1434; 1514–1516; 1542–1547; 1558–1567|前717–719|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04|
|people_return / `rome06_medieval_s_clemente`|720.290–721.490|717–748; 790–797; 810–827; 1059–1061; 1092–1105; 1116–1134; 1144–1158; 1214; 1263–1283; 1301–1306; 1334–1355; 1374–1386; 1409–1417; 1426–1476; 1513–1516; 1541–1546; 1560–1572|前717–720|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04|
|people_return / `rome06_medieval_s_gregorio`|719.664–720.864|717–747; 790–797; 810–827; 1059–1063; 1067–1077; 1092–1106; 1115–1135; 1143–1159; 1263–1283; 1301–1306; 1335–1355; 1374–1385; 1410–1417; 1426–1455; 1513–1516; 1541–1546; 1559–1571|前717–719|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04|
|people_return / `rome06_medieval_s_maria_antiqua`|719.167–720.367|717–749; 790–801; 809–828; 1006–1022; 1058–1078; 1092–1113; 1115–1135; 1142–1159; 1227; 1238–1244; 1263–1283; 1300–1307; 1333–1355; 1373–1385; 1410–1477; 1486–1488; 1513–1516; 1541–1546; 1559–1572|前717–719|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04|
|people_return / `rome06_medieval_colosseum_north`|719.739–720.939|717–749; 790–800; 809–828; 1058–1078; 1092–1109; 1116–1135; 1143–1160; 1214; 1263–1284; 1300–1307; 1334–1355; 1373–1386; 1410–1477; 1482–1487; 1513–1516; 1541–1546; 1559–1572|前717–719|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04, S86|
|people_return / `rome06_medieval_titus_arch`|718.919–720.119|717–749; 790; 796–800; 809; 827–828; 1058–1078; 1092–1093; 1104–1110; 1115–1116; 1134–1135; 1143–1146; 1154–1160; 1278–1284; 1300–1307; 1333–1355; 1373–1374; 1376–1385; 1414–1427; 1434–1477; 1481–1488; 1513–1514; 1559–1572|前717–718|Q|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04, S98|
|people_return / `rome06_medieval_severus_arch`|718.391–719.591|717–750; 789–790; 793–801; 809–810; 826–829; 1006–1023; 1057–1078; 1092–1113; 1115–1117; 1133–1135; 1142–1159; 1210–1211; 1226–1227; 1242–1245; 1262–1263; 1277–1284; 1300–1307; 1333–1356; 1372–1385; 1410–1477; 1481–1489; 1513–1516; 1542; 1559; 1566–1573|前717–718|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04|
|people_return / `rome06_medieval_pantheon`|719.292–720.492|717–755; 788–803; 808–830; 854–863; 1024; 1056–1062; 1069–1079; 1091–1136; 1141–1159; 1194–1210; 1226–1227; 1242–1284; 1300–1345; 1356–1357; 1371–1385; 1410–1436; 1455–1477; 1483–1493; 1512–1515; 1542–1546; 1573; 1599|前717–719|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04, S101|
|people_return / `rome06_medieval_castel`|720.228–721.428|717–798; 802–870; 960–970; 1025; 1055–1057; 1079; 1090–1137; 1140–1157; 1195–1209; 1243–1284; 1307–1333; 1356–1375; 1377–1385; 1410–1416; 1426–1434; 1513–1514; 1543–1547; 1599|前717–720|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04, M21|
|people_return / `rome06_medieval_bridge_aelius`|720.171–721.371|717–790; 792–798; 802–870; 959–971; 1025–1026; 1055–1057; 1079; 1090–1157; 1195–1209; 1243–1275; 1277–1284; 1307–1333; 1356–1360; 1366–1385; 1410–1416; 1426–1434; 1514; 1543–1547; 1599|前717–720|W|research/rome_restart_lm02_bridge_audit.md, M03|
|people_return / `rome06_medieval_bridge_fabricius`|718.955–720.155|717–750; 789–802; 809–829; 856–861; 1004–1024; 1057–1078; 1091–1136; 1141–1158; 1197–1210; 1226–1283; 1301–1307; 1332–1344; 1356; 1372–1385; 1410–1476; 1514–1516; 1542–1547|前717–718|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04|
|people_return / `rome06_medieval_bridge_cestius`|718.834–720.034|717–750; 789–802; 809–829; 856–861; 1004–1005; 1023–1024; 1057–1078; 1091–1136; 1141–1158; 1197–1209; 1227–1282; 1307; 1333–1334; 1356; 1372–1383; 1410–1436; 1443–1449; 1454–1476; 1514–1515; 1542–1547|前717–718; 後1275–1282; 後1307; 後1333–1334; 後1356; 後1372–1383; 後1410–1436; 後1443–1449; 後1454–1476; 後1514–1515; 後1542–1547|T|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04|
|people_return / `rome06_medieval_bridge_s_maria`|718.591–719.791|717–749; 789–801; 809–829; 857–858; 1005–1023; 1057–1078; 1091–1136; 1141–1158; 1198–1209; 1227–1246; 1262–1282; 1301–1307; 1333–1335; 1337–1342; 1356; 1373–1385; 1410–1476; 1514–1516; 1542–1547; 1568|前717–718; 後1096–1136; 後1141–1158; 後1198–1209; 後1227–1246; 後1262–1282; 後1301–1307; 後1333–1335; 後1337–1342; 後1356; 後1373–1385; 後1410–1476; 後1514–1516; 後1542–1547; 後1568|R|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04|
|people_return / `rome_round12_obelisk800`|721.558–722.758|717–722; 728–789; 803–808; 830–831; 863–959; 1025–1057; 1079–1090; 1137–1140; 1244–1246; 1308–1332; 1357–1372; 1415; 1427; 1599|前717–721; 後909–959; 後1025–1057; 後1079–1090; 後1137–1140; 後1244–1246; 後1308–1332; 後1357–1372; 後1415; 後1427; 後1599|R|R02, R03, S48, research/rome_round12_sites.md|
|people_return_late / `rome06_medieval_vatican_palace`|794.530–795.730|791–797; 803–914; 917–960; 1025–1056; 1079–1156; 1244–1283; 1308–1332; 1357–1375; 1410–1415; 1427–1433; 1543–1547; 1599–1600|前791–794|W|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04, M10, research/rome_director_v9_0507_facade_patch.md|
|people_return_late / `rome06_medieval_benedictine_cloister`|791.945–793.145|791–803; 808–830; 854–865; 971–1004; 1023–1024; 1056–1079; 1091–1137; 1139–1158; 1198–1209; 1227–1282; 1307–1308; 1331–1334; 1356; 1371–1376; 1379–1380; 1410–1435; 1455–1476; 1514–1515; 1542–1547; 1599–1600|前791|W|research/rome06_medieval_quarter_basis.md, M13, M04, M01|
|people_return_late / `rome06_medieval_s_benedetto_church`|791.835–793.035|793–803; 808–810; 826–830; 854–865; 971–1004; 1023–1024; 1056–1079; 1091–1117; 1134–1137; 1140–1158; 1198–1209; 1227–1263; 1277–1282; 1307–1308; 1331–1334; 1356; 1371–1382; 1410–1436; 1455–1476; 1514–1515; 1542–1543; 1547; 1599–1600|—|N|research/rome06_medieval_quarter_basis.md, M13, M04, M01|
|people_return_late / `rome_af_passetto_00`|794.208–795.408|795–797; 803–810; 826–855; 870–913; 919–959; 1025–1056; 1079–1090; 1137; 1139; 1244–1262; 1277–1283; 1308–1332; 1357–1373; 1410–1415; 1427–1433; 1543–1544; 1547; 1599–1600|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_01`|794.163–795.363|803–807; 852; 870–912; 920–959; 1025–1055; 1080–1090; 1308–1332; 1357–1370|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_02`|794.446–795.646|803–808; 831–852; 872–912; 921–959; 1026–1055; 1080–1089; 1308–1332; 1357–1370; 1415; 1427|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_03`|794.410–795.610|803–808; 831–852; 871–896; 903–912; 921–960; 1026–1055; 1080–1089; 1308–1332; 1357–1370; 1415; 1427|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_04`|794.192–795.392|803–807; 831–852; 870–895; 904–912; 921–960; 1025–1055; 1080–1089; 1308–1332; 1357–1370|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_05`|794.046–795.246|803–808; 831–853; 870–895; 905–912; 921–960; 1025–1055; 1080–1090; 1308–1332; 1357–1370; 1415; 1427|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_06`|794.380–795.580|803–808; 831–853; 870–894; 905–911; 922–960; 1025–1039; 1053–1055; 1080–1090; 1308–1332; 1357–1370; 1415; 1427|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_07`|794.147–795.347|803–808; 830–854; 868–878; 886–894; 906–911; 922–960; 1025–1036; 1053–1056; 1079–1090; 1137; 1139; 1244–1245; 1282–1283; 1308–1332; 1357–1372; 1414–1415; 1427; 1433; 1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_08`|794.122–795.322|803–808; 830–854; 868–877; 888–893; 906–911; 922–960; 1025–1033; 1053–1056; 1079–1090; 1137; 1139; 1244–1245; 1282–1283; 1308–1332; 1357–1372; 1414–1415; 1427; 1433; 1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_09`|793.999–795.199|803–808; 830–853; 869–876; 906–911; 923–960; 1025–1029; 1053–1055; 1079–1090; 1139; 1244; 1283; 1308–1332; 1357–1371; 1415; 1427; 1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_10`|794.117–795.317|803–808; 830–853; 870–875; 907–910; 923–960; 1025–1029; 1053–1055; 1080–1090; 1244; 1283; 1308–1332; 1357–1371; 1415; 1427; 1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_11`|793.785–794.985|804–807; 834–851; 873–875; 907–910; 924–933; 937–960; 1027–1029; 1053–1054; 1332–1333; 1357–1358; 1360–1369|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_12`|793.910–795.110|797; 803–809; 829–855; 867–874; 907–910; 924–932; 938–969; 1025–1029; 1054–1056; 1079–1090; 1137; 1139–1140; 1244–1247; 1259–1261; 1278–1283; 1308–1333; 1357–1372; 1410; 1413–1416; 1427–1428; 1432–1434; 1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_13`|794.033–795.233|797; 803–809; 829–855; 867–874; 908–909; 924–931; 939–969; 1025–1028; 1054–1056; 1079–1090; 1137; 1139–1140; 1244–1248; 1257–1261; 1278–1283; 1308–1333; 1357–1372; 1410; 1413–1416; 1427–1428; 1432–1434; 1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_14`|793.677–794.877|803–808; 830–854; 869–873; 909; 925–931; 941–969; 1025–1028; 1054–1056; 1079–1090; 1139; 1244–1245; 1283; 1307–1333; 1357–1371; 1415–1416; 1427; 1434; 1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_15`|793.821–795.021|803–808; 830–853; 870–873; 926–931; 942–969; 1025–1028; 1054–1055; 1079–1090; 1244; 1283; 1307–1333; 1357–1371; 1415–1416; 1427; 1434; 1598–1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_16`|793.740–794.940|803–808; 830–853; 870–873; 926–931; 944–969; 1025–1028; 1054–1055; 1079–1090; 1244; 1283; 1307–1333; 1357–1371; 1415–1416; 1427; 1434; 1514; 1598–1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_17`|793.727–794.927|803–808; 830–853; 869–872; 927–930; 944–970; 1025–1027; 1054–1055; 1079–1090; 1244; 1283; 1307–1333; 1357–1371; 1415–1416; 1427; 1434; 1514; 1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_18`|793.639–794.839|803–808; 830–853; 869–872; 927–930; 945–970; 1025–1027; 1054–1055; 1079–1090; 1244; 1283–1284; 1307–1333; 1357–1371; 1415–1416; 1427; 1434; 1514|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_19`|793.900–795.100|803–808; 831–853; 871–872; 928–930; 945–970; 1026; 1054–1055; 1080–1090; 1307–1333; 1357–1358; 1360–1370; 1416|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_20`|793.502–794.702|803–808; 831–853; 871–872; 929; 945–970; 1026; 1055; 1080–1090; 1307–1333; 1357–1358; 1360–1370; 1416|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_21`|793.712–794.912|804–807; 831–852; 871; 946–950; 957–970; 1026; 1055; 1080–1089; 1307; 1332–1333; 1357–1358; 1360–1369|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_22`|793.634–794.834|803–807; 831–853; 870–871; 946–950; 959–970; 1025–1026; 1055; 1080–1090; 1307–1308; 1331–1333; 1357–1370|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_23`|793.544–794.744|804–807; 831–852; 871; 946–950; 959–967; 969–970; 1026; 1055; 1081–1089; 1307; 1332–1333; 1357–1358; 1360–1369|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_24`|793.798–794.998|798; 803–808; 830–854; 869–871; 946–950; 959–970; 1025–1026; 1055–1056; 1079–1090; 1244–1245; 1283–1284; 1307–1333; 1357–1371; 1415–1416; 1427; 1434; 1514|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_25`|793.731–794.931|798; 802–808; 830–854; 870–871; 947–950; 959–970; 1025–1026; 1055; 1079–1090; 1244–1245; 1279–1284; 1307–1333; 1356–1371; 1414–1416; 1427; 1434; 1514; 1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_26`|793.332–794.532|798; 802–808; 829–854; 869–870; 960–970; 1025–1026; 1055; 1079–1090; 1244–1245; 1279–1284; 1307–1333; 1356–1371; 1415–1416; 1427; 1434; 1514; 1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|people_return_late / `rome_af_passetto_27`|793.499–794.699|798; 802–808; 829–854; 869–870; 960–970; 1025–1026; 1055; 1079–1080; 1090; 1244–1245; 1279–1284; 1307–1333; 1356–1371; 1415–1416; 1427; 1434; 1514; 1599|—|Q|S195, S199, research/rome_af_sites_sources.md, R33|
|made_again / `rome07_renaissance_sistine`|908.759–909.759|907–959; 1025–1056; 1079–1093; 1104–1116; 1135–1145; 1154–1156; 1244–1272; 1275–1283; 1308–1332; 1357–1374; 1410–1415; 1427–1433; 1543–1547; 1599–1601; 1652–1653; 1660–1739|前907–908|W|R42|
|made_again / `rome07_formal_obelisk_old`|908.365–909.365|907–959; 1025–1057; 1079–1090; 1137–1140; 1244–1246; 1308–1332; 1357–1372; 1415; 1427; 1599; 1660–1677; 1711–1739|前907–908; 後1040–1057; 後1079–1090; 後1137–1140; 後1244–1246; 後1308–1332; 後1357–1372; 後1415; 後1427; 後1599; 後1660–1677; 後1711–1739|T|R02, R03, S48|
|made_again / `rome07_formal_massimo_old`|973.052–974.052|961–970; 972–1004; 1023–1025; 1056–1062; 1068–1079; 1091–1136; 1140–1158; 1194; 1196–1209; 1227–1283; 1301–1335; 1337–1341; 1356–1357; 1371–1385; 1410–1436; 1455–1476; 1514–1515; 1542–1547; 1599–1609; 1651–1652; 1714–1720; 1725–1801|前961–970; 前972–973; 後990–1004; 後1023–1025; 後1056–1062; 後1068–1079; 後1091–1136; 後1140–1158; 後1194; 後1196–1209; 後1227–1283; 後1301–1335; 後1337–1341; 後1356–1357; 後1371–1385; 後1410–1436; 後1455–1476; 後1514–1515; 後1542–1547; 後1599–1609; 後1651–1652; 後1714–1720; 後1725–1801|R|R12, R14, S64, S65, R30|
|made_again / `rome07_renaissance_massimo`|993.825–994.825|961–970; 972–1004; 1023–1025; 1056–1063; 1068–1079; 1091–1136; 1140–1158; 1194; 1196–1210; 1227–1283; 1301–1335; 1337–1341; 1356–1357; 1371–1385; 1410–1436; 1455–1476; 1514–1515; 1542–1547; 1599–1612; 1650–1652; 1714–1721; 1725–1801|前961–970; 前972–993|N|R12, S65, R21, research/rome_director_v9_0507_facade_patch.md|
|made_again / `rome07_renaissance_newstpeter`|1027.696–1043.060|907–960; 1025–1057; 1079–1156; 1244–1283; 1308–1332; 1357–1374; 1410–1415; 1427–1433; 1543–1547; 1599–1619; 1637–1653; 1660–1739|前907–960; 前1025–1027|V|research/rome07_renaissance_survey.md, R01, R07, research/rome07_renaissance_landmark_types.yaml, research/rome_round9_stpeter.md, R05, research/rome_round10_st|
|made_again / `rome07_renaissance_senatorio`|1008.428–1108.242|1005–1023; 1057–1078; 1091–1135; 1142–1159; 1196–1211; 1225–1246; 1262–1284; 1300–1307; 1332–1356; 1372–1385; 1410–1477; 1486–1491; 1513–1516; 1542–1546; 1568–1573; 1600–1613; 1650–1652; 1726–1801|前1005–1008|H|R16, R32, research/rome_director_v9_0507_facade_patch.md|
|made_again / `rome07_renaissance_conservatori`|1006.783–1016.323|1005–1023; 1057–1078; 1091–1135; 1142–1159; 1196–1211; 1225–1228; 1231–1246; 1262–1284; 1300–1307; 1332–1356; 1372–1385; 1410–1477; 1484–1492; 1513–1516; 1542–1546; 1568–1573; 1600–1613; 1650–1652; 1726–1801|前1005–1006|H|R16, R32, research/rome_director_v9_0507_facade_patch.md|
|made_again / `rome07_renaissance_ligorio_niche`|1029.594–1030.594|907–912; 922–932; 939–950; 1026–1036; 1054; 1079–1136; 1140–1156; 1244–1283; 1308–1332; 1357–1375; 1410–1415; 1427–1433; 1543–1546; 1599–1611; 1644–1654; 1659–1739|前907–912; 前922–932; 前939–950; 前1026–1029|V|R44|
|made_again / `rome07_renaissance_colonnade`|1084.829–1085.829|907–960; 1025–1057; 1079–1156; 1244–1283; 1308–1332; 1357–1375; 1410–1415; 1427–1433; 1543–1547; 1599–1619; 1636–1653; 1660–1739|前907–960; 前1025–1057; 前1079–1084|N|research/rome07_renaissance_colonnade_sources.md, R06|
|made_again / `rome07_renaissance_closed_wing_1`|1081.112–1082.112|907–960; 1025–1057; 1079–1093; 1104–1116; 1135–1145; 1154–1156; 1244–1273; 1275–1283; 1308–1332; 1357–1375; 1410–1415; 1427–1433; 1543–1547; 1599–1601; 1651–1653; 1661–1739|前907–960; 前1025–1057; 前1079–1081|N|research/rome07_renaissance_colonnade_sources.md, R06|
|made_again / `rome07_renaissance_closed_wing_-1`|1081.042–1082.042|907–960; 1025–1056; 1079–1093; 1104–1116; 1135–1145; 1154–1156; 1244–1273; 1275–1283; 1308–1332; 1357–1375; 1410–1415; 1427–1433; 1543–1547; 1599–1601; 1652–1653; 1660–1739|前907–960; 前1025–1056; 前1079–1081|N|research/rome07_renaissance_colonnade_sources.md, R06|
|made_again / `rome07_renaissance_obelisk`|1046.060–1047.060|907–913; 919–960; 1025–1056; 1079–1091; 1111–1114; 1137–1140; 1244–1246; 1308–1332; 1357–1372; 1415; 1427; 1599; 1661–1684; 1703–1704; 1711–1739|前907–913; 前919–960; 前1025–1046|Q|R02, R03, S48|
|made_again / `rome07_renaissance_quirinal_palace_body`|1107.576–1108.576|1059–1062; 1071–1073; 1092–1109; 1115–1135; 1143–1161; 1192–1226; 1245–1285; 1300–1307; 1333–1356; 1372–1386; 1409–1417; 1426–1516; 1542–1546; 1568–1573; 1599–1618; 1638–1653; 1714–1748; 1759–1801|前1059–1062; 前1071–1073; 前1092–1107; 後1208–1226; 後1245–1285; 後1300–1307; 後1333–1356; 後1372–1386; 後1409–1417; 後1426–1516; 後1542–1546; 後1568–1573; 後1599–1618; 後1638–1653; 後1714–1748; 後1759–1801|R|R21, research/rome_director_v9_0507_facade_patch.md|
|made_again / `rome07_renaissance_farnese_palace_body`|1107.980–1108.980|971–1004; 1023–1025; 1056–1079; 1091–1137; 1139–1158; 1198–1209; 1227–1282; 1307–1308; 1331–1334; 1356; 1371–1382; 1410–1435; 1455–1476; 1514–1515; 1542–1547; 1599–1617; 1638–1652; 1725–1801|前971–1004; 前1023–1025; 前1056–1079; 前1091–1107|N|research/rome_director_v9_0507_facade_patch.md|
|made_again / `rome07_renaissance_retained_constantine_arch`|1108.939–1109.939|1058–1078; 1092–1109; 1116–1135; 1143–1160; 1263; 1277–1283; 1300–1307; 1334–1355; 1373–1385; 1410–1476; 1486–1487; 1513–1516; 1541–1542; 1559–1572; 1600; 1726–1801|前1058–1078; 前1092–1108|N|research/rome04_lateantique_whole_basis.md, LA25, R09|
|made_again / `rome07_renaissance_nuovo`|1107.294–1108.294|1005–1023; 1057–1078; 1091–1136; 1142–1159; 1196–1211; 1225–1246; 1262–1284; 1300–1307; 1332–1356; 1372–1385; 1410–1477; 1487–1491; 1513–1516; 1542–1546; 1568–1573; 1600–1612; 1650–1652; 1726–1801|前1005–1023; 前1057–1078; 前1091–1107|N|R16, R32, research/rome_director_v9_0507_facade_patch.md|
|made_again / `rome07_formal_colosseum_inner`|1109.027–1110.027|1058–1078; 1092–1109; 1116–1135; 1143–1160; 1214; 1263–1284; 1300–1307; 1334–1355; 1373–1385; 1410–1477; 1482–1487; 1513–1516; 1541–1546; 1559–1572; 1600–1619; 1637–1651; 1726–1801|前1058–1078; 前1092–1109; 後1120–1135; 後1143–1160; 後1214; 後1263–1284; 後1300–1307; 後1334–1355; 後1373–1385; 後1410–1477; 後1482–1487; 後1513–1516; 後1541–1546; 後1559–1572; 後1600–1619; 後1637–1651; 後1726–1801|R|research/rome06_medieval_whole_basis.md, M03, M18, M13, M17, M01, M04, S86, R09|
|made_again / `rome07_formal_ponte_rotto_west`|1107.998–1108.998|1005; 1023; 1057–1078; 1091–1136; 1141–1158; 1198–1209; 1227–1246; 1262–1282; 1306–1307; 1333–1335; 1373–1385; 1410–1437; 1440–1451; 1454–1476; 1514–1516; 1542–1547; 1600–1601; 1603–1608; 1726–1801|前1005; 前1023; 前1057–1078; 前1091–1107|N|Roma Capitale TurismoRoma, Pons Aemilius: Christmas1598 destroyed three arches/two piers and half th|
|made_again / `rome_round9_belvedere_south`|1028.539–1029.539|907–959; 1025–1056; 1079–1137; 1139–1156; 1244–1283; 1308–1332; 1357–1375; 1410–1415; 1427–1433; 1543–1547; 1599–1615; 1638–1653; 1660–1739|前907–959; 前1025–1028|V|S38, R39, R41, R09|
|made_again / `rome_round9_belvedere_middle`|1028.854–1029.854|907–914; 918–959; 1026–1055; 1079–1137; 1140–1156; 1244–1283; 1308–1332; 1357–1375; 1410–1415; 1427–1433; 1543–1546; 1599–1615; 1638–1653; 1660–1739|前907–914; 前918–959; 前1026–1028|V|S38, R39, R41, R09|
|made_again / `rome_round9_belvedere_north`|1029.419–1030.419|907–913; 921–950; 1026–1039; 1053–1055; 1079–1137; 1140–1156; 1244–1283; 1308–1332; 1357–1375; 1410–1415; 1427–1433; 1543–1546; 1599–1615; 1638–1653; 1659–1739|前907–913; 前921–950; 前1026–1029|V|S38, R39, R41, R09|
|made_again / `rome_round12_torrione_niccolo_v`|909.840–910.840|907–913; 920–959; 1025–1056; 1079–1137; 1139–1156; 1244–1283; 1308–1332; 1357–1375; 1410–1415; 1427–1433; 1543–1547; 1599–1607; 1651–1653; 1660–1739|前907–909|W|S208, research/rome_round12_sites.md|
|a_capital_fought_for / `rome08_formal_colosseum_inner_supports`|1127.966–1129.166|1126–1135; 1143–1160; 1214; 1263–1284; 1300–1307; 1334–1355; 1373–1386; 1410–1477; 1482–1487; 1513–1516; 1541–1546; 1559–1572|前1126–1127|W|research/rome08_capital_whole_basis.md|
|a_capital_fought_for / `rome08_capital_portapia`|1167.250–1168.450|1126–1133; 1146–1193; 1213–1214; 1263–1285; 1373–1386; 1394–1400; 1408–1415; 1427–1454; 1486–1501; 1508–1516; 1541–1544; 1599|前1126–1133; 前1146–1167|N|research/rome08_capital_whole_basis.md|
|a_capital_fought_for / `rome08_capital_braschi`|1127.950–1129.150|1126–1136; 1140–1158; 1194; 1196–1210; 1227–1284; 1300–1335; 1337–1340; 1356–1358; 1370–1385; 1410–1436; 1456–1476; 1513–1515; 1542–1547; 1599|前1126–1127|W|research/rome08_capital_window_basis.md|
|a_capital_fought_for / `rome08_capital_sanpantaleo`|1127.866–1129.066|1126–1136; 1140–1158; 1194; 1196–1210; 1227–1283; 1300–1335; 1337–1340; 1356–1357; 1370–1385; 1410–1436; 1455–1476; 1513–1515; 1542–1547; 1599|前1126–1127|W|research/rome08_capital_window_basis.md|
|rome08_national_capital / `rome_round10_quirinal_manica_lunga`|1213.226–1214.426|1213–1225; 1256–1285; 1300–1307; 1333–1355; 1372–1386; 1409–1417; 1426–1465; 1477–1516; 1542–1546; 1568–1573; 1599|前1213|W|research/rome_round10_quirinal.md, research/rome_round11_models.md|
|rome08_national_capital / `rome_round11_quirinal_1871_core`|1213.717–1214.917|1213–1226; 1245–1285; 1300–1307; 1333–1356; 1372–1386; 1409–1417; 1426–1516; 1542–1546; 1568–1573; 1599|前1213|W|R21, research/rome_director_v9_0507_facade_patch.md, research/rome_round11_models.md|
|a_home_lost / `rome09_fascist_retained_retained_retained_bridge_cestius`|1273.940–1275.140|1274–1282; 1307; 1333–1334; 1356; 1372–1384; 1410–1436; 1442–1450; 1454–1476; 1514–1516; 1542–1547|—|N|research/rome09_fascist_whole_basis.md|
|a_home_lost / `rome09_fascist_vittoriano`|1273.443–1274.643|1274–1284; 1300–1307; 1332–1356; 1372–1385; 1410–1496; 1511–1516; 1542–1546; 1568–1573; 1599|—|N|research/rome09_fascist_whole_basis.md|
|a_home_lost / `rome09_fascist_trajan_column`|1273.516–1274.716|1284; 1300–1307; 1332–1356; 1372–1374; 1416–1426; 1454–1496; 1510–1513; 1568–1573|—|Q|research/rome09_fascist_whole_basis.md|
|a_home_lost / `rome09_fascist_palazzo_giustizia`|1274.691–1275.891|1274–1285; 1299–1300; 1307–1334; 1356–1359; 1369–1385; 1410–1417; 1426–1435; 1488–1496; 1510–1515; 1542–1546; 1574; 1598–1599|前1274|W|research/rome_af_sites_sources.md|
|a_home_lost / `rome09_fascist_santa_maria_angeli`|1274.807–1276.007|1274–1285; 1300; 1373–1399; 1409–1416; 1427–1455; 1477–1516; 1541–1546; 1599|前1274|W|research/rome09_fascist_whole_basis.md|
|a_home_lost / `rome09_fascist_termini_old_headhouse`|1274.731–1275.931|1274–1284; 1373–1399; 1409–1416; 1427–1455; 1478–1516; 1541–1546; 1599|前1274|W|research/rome09_fascist_whole_basis.md|
|a_home_lost / `rome09_fascist_sanlorenzo`|1276.035–1277.235|1274–1283; 1375–1400; 1409–1415; 1427–1454; 1513–1517; 1540–1546|前1274–1276|H|research/rome09_fascist_whole_basis.md|
|a_home_lost / `rome09_fascist_marmi1932`|1291.236–1292.436|1274–1298; 1375; 1410–1413; 1428–1431; 1544–1546; 1576–1589; 1597–1599|前1274–1291|N|research/rome09_fascist_whole_basis.md, F01|
|a_home_lost / `rome09_fascist_palazzoh1932`|1290.662–1291.862|1274–1298; 1375; 1410–1413; 1428–1432; 1544–1546; 1576–1589; 1597–1599|前1274–1290|N|research/rome09_fascist_whole_basis.md, F01|
|a_home_lost / `rome09_fascist_pnf1928`|1293.072–1294.272|1274–1299; 1373–1375; 1409–1415; 1427–1433; 1543–1546; 1575–1591; 1595–1599|前1274–1293; 後1575–1591; 後1595–1599|R|research/rome09_fascist_whole_basis.md, F02|
|rome09_war1943 / `rome09_fascist_cipressi1937`|1380.400–1381.600|1410–1413; 1428–1431; 1544–1546; 1576–1589; 1598–1599|後1576–1589; 後1598–1599|R|research/rome09_fascist_whole_basis.md, F01|
|screen_rome / `rome10_screen_quarter_central_unit`|1520.967–1522.167|1521–1546|—|N|research/rome10_screen_quarter_sources.md|
|screen_rome / `rome10_screen_quarter_stage15`|1521.341–1522.541|1521–1546|前1521|W|research/rome10_screen_quarter_revision_sources.md, R15|
|screen_rome / `rome10_screen_quarter_stage16`|1521.310–1522.510|1521–1546|前1521|W|research/rome10_screen_quarter_revision_sources.md, R16|
|screen_rome / `rome10_screen_quarter_vent22`|1521.178–1522.378|1521–1541|前1521|W|research/rome10_screen_quarter_revision_sources.md, R22|
|screen_rome / `rome10_screen_quarter_lamp60`|1521.073–1522.273|1521–1541|前1521|W|research/rome10_screen_quarter_revision_sources.md, R60|
|screen_rome / `rome10_screen_quarter_power21`|1521.496–1522.696|1521–1546|前1521|W|research/rome10_screen_quarter_revision_sources.md, R21|
|screen_rome / `rome10_screen_whole_1`|1522.193–1523.393|1521–1542|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_2`|1521.958–1523.158|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_3`|1521.575–1522.775|1521–1541|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_4`|1521.567–1522.767|1521–1542|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_6`|1521.248–1522.448|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_7`|1521.406–1522.606|1521–1542|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_8`|1521.776–1522.976|1521–1542|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_9`|1521.924–1523.124|1521–1544|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_10`|1521.682–1522.882|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_11`|1521.328–1522.528|1521–1543|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_12`|1521.609–1522.809|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_13`|1521.388–1522.588|1521–1544; 1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_14`|1521.382–1522.582|1521–1544|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_17_west_south`|1522.076–1523.276|1521–1546|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_17_west_middle`|1521.290–1522.490|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_17_east_south`|1521.818–1523.018|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_17_east_middle`|1521.445–1522.645|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_17`|1521.700–1522.900|1521–1541|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_18`|1522.342–1523.542|1521–1546|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_19`|1521.949–1523.149|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_20`|1521.558–1522.758|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_23`|1521.364–1522.564|1521–1539|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_24`|1522.653–1523.853|1521–1546|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_25`|1522.372–1523.572|1521–1546|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_26`|1522.293–1523.493|1521–1546|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_27`|1521.857–1523.057|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_28`|1521.969–1523.169|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_29`|1521.600–1522.800|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_30`|1521.613–1522.813|1521–1541|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_31`|1522.605–1523.805|1521–1544; 1546|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_32`|1522.204–1523.404|1521–1541|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_33`|1522.403–1523.603|1521–1540|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_34`|1522.255–1523.455|1521–1540|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_35`|1522.263–1523.463|1521–1541|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_36`|1522.221–1523.421|1521–1540|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_37`|1522.634–1523.834|1521–1539|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_38`|1522.595–1523.795|1521–1539|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_39`|1522.677–1523.877|1521–1539|前1521–1522|Q|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_40`|1522.938–1524.138|1521–1539|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_41_east`|1522.935–1524.135|1521–1543|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_41_west`|1523.280–1524.480|1521–1546|前1521–1523|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_42_west`|1523.195–1524.395|1521–1546|前1521–1523|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_42_east`|1523.473–1524.673|1521–1546|前1521–1523|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_43`|1523.120–1524.320|1521–1541|前1521–1523|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_44`|1522.934–1524.134|1521–1546|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_45`|1522.978–1524.178|1521–1544; 1546|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_46`|1523.260–1524.460|1521–1542|前1521–1523|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_47_north`|1523.297–1524.497|1521–1546|前1521–1523|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_47_south`|1523.509–1524.709|1521–1546|前1521–1523|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_48`|1522.658–1523.858|1521–1541|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_49`|1522.572–1523.772|1521–1539|前1521–1522|Q|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_51`|1522.660–1523.860|1521–1540|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_52`|1522.915–1524.115|1521–1539|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_55`|1521.885–1523.085|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_58`|1521.467–1522.667|1521–1543|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_59`|1521.659–1522.859|1521–1541|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_61`|1522.046–1523.246|1521–1542|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_62`|1523.226–1524.426|1521–1539|前1521–1523|Q|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_63`|1522.800–1524.000|1521–1537|前1521–1522|Q|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_64`|1521.768–1522.968|1521–1542|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_65`|1521.783–1522.983|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_66_west`|1522.112–1523.312|1521–1546|前1521–1522|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_66_east`|1521.662–1522.862|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_68`|1523.506–1524.706|1521–1540|前1521–1523|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_69`|1523.534–1524.734|1521–1546|前1521–1523|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_71`|1524.695–1525.895|1521–1542|前1521–1524|W|research/rome10_screen_whole_sources.md, R53|
|screen_rome / `rome10_screen_whole_54`|1521.784–1522.984|1521–1546|前1521|W|research/rome10_screen_whole_sources.md, R53|
|rome11_olympic1960 / `rome11_olympic_corso_francia_east`|1581.413–1583.013|1575–1619; 1636–1657; 1739|前1575–1581; 後1606–1619; 後1636–1657; 後1739|T|O09 Ministry1087:1959–60,110piers3.5–8m,independent carriageways/5m gap,48m footbridges; source-plan|
|rome11_olympic1960 / `rome11_olympic_corso_francia_west`|1581.427–1583.027|1575–1619; 1636–1657; 1739|前1575–1581; 後1606–1619; 後1636–1657; 後1739|T|O09 Ministry1087:1959–60,110piers3.5–8m,independent carriageways/5m gap,48m footbridges; source-plan|
|rome11_olympic1960 / `rome11_olympic_palazzetto1957`|1581.271–1582.871|1575–1608; 1650–1657; 1739|前1575–1581; 後1606–1608; 後1650–1657; 後1739|T|O01 catalogue60/61 printed61/62:78m external,58.5m internal,21m arena-to-top,arena3m below ground; O|
|rome11_olympic1960 / `rome11_olympic_flaminio1959`|1582.615–1584.215|1575–1591; 1595–1617; 1638–1657; 1712; 1727–1732; 1739|前1575–1582; 後1606–1617; 後1638–1657; 後1712; 後1727–1732; 後1739|T|O01 catalogue57/59 printed58/60:181x131m outer,105x70m field,1957 demolition/1959 opening; O05/CONI1|
|rome11_olympic1960 / `rome11_olympic_olimpico1953`|1583.472–1585.072|1576–1589; 1598–1619; 1636–1660|前1576–1583; 後1606–1619; 後1636–1660|T|O01 catalogue57 printed58 outer319x186m,inner205.8x94.4m,field4.5m below road,top20.5m above field=>|
|rome11_olympic1960 / `rome11_olympic_palazzoEUR1960`|1551.228–1552.828|1549–1556; 1618–1635|前1549–1551; 後1618–1635|T|O01 catalogue67/69/71 printed68/70/72:external122m,internal dome100m,arena-to-top34.5m,outer glazed |
|rome11_olympic1960 / `rome11_olympic_rose_basin1960`|1550.085–1551.685|1549–1556; 1618–1634|前1549–1550; 後1618–1634|T|O01 printed75–76:50x25m open basin,1.8–2m depth; Luce FV00176057,1960-07-24 contemporary photo inspe|
|rome11_olympic1960 / `tail_caracalla_202937172`|1561.194–1562.794|1559–1567; 1601–1602; 1611–1613; 1740–1742; 1762–1801|前1559–1561|N|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `tail_caracalla_202937173`|1560.410–1562.010|1559–1567; 1601–1602; 1610–1617; 1638; 1641–1650; 1739–1742; 1762–1801|前1559–1560|W|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `tail_caracalla_202937174`|1561.028–1562.628|1559–1567; 1601–1602; 1611–1613; 1740–1742; 1762–1801|前1559–1561|N|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `tail_caracalla_202938756`|1560.085–1561.685|1559–1567; 1739–1743; 1761–1801|前1559–1560|W|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `tail_caracalla_202938757`|1559.873–1561.473|1559–1567; 1601–1602; 1609–1615; 1650; 1739–1742; 1761–1801|前1559|W|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `tail_caracalla_202938759`|1559.952–1561.552|1559–1567; 1739–1742; 1762–1801|前1559|Q|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `tail_caracalla_202943217`|1560.089–1561.689|1559–1567; 1601–1602; 1607–1619; 1637–1650; 1739–1743; 1761–1801|前1559–1560|W|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `tail_caracalla_202943220`|1560.987–1562.587|1559–1567; 1601–1602; 1608–1610; 1739–1743; 1761–1801|前1559–1560|N|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `tail_caracalla_202943222`|1560.762–1562.362|1559–1567; 1601–1602; 1610–1614; 1739–1742; 1762–1801|前1559–1560|N|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `tail_caracalla_202943223`|1560.785–1562.385|1559–1567; 1739–1743; 1761–1801|前1559–1560|Q|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `tail_caracalla_202944034`|1561.644–1563.244|1559–1567; 1739–1742; 1762–1801|前1559–1561|Q|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `tail_caracalla_359870868`|1559.806–1561.406|1559–1567; 1601–1602; 1609–1611; 1739–1742; 1761–1801|前1559|W|research/rome_tail_r5_sources.md, S189|
|rome11_olympic1960 / `rome11_olympic_A_north`|1582.591–1584.191|1579–1611; 1650–1657|前1579–1582; 後1606–1611; 後1650–1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_A_second`|1582.385–1583.985|1577–1611; 1650–1657|前1577–1582; 後1606–1611; 後1650–1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_A_bent_north`|1582.182–1583.782|1577–1609; 1651–1657|前1577–1582; 後1606–1609; 後1651–1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_A_bent_south`|1582.124–1583.724|1577–1609; 1650–1657|前1577–1582; 後1606–1609; 後1650–1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_A_spine_west`|1582.323–1583.923|1576–1609; 1643–1657|前1576–1582; 後1606–1609; 後1643–1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_A_spine_east`|1582.231–1583.831|1576–1600; 1651–1657|前1576–1582; 後1651–1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_A4_west_north`|1581.038–1582.638|1576–1614; 1642–1658; 1739|前1576–1581; 後1606–1614; 後1642–1658; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_A4_west_south`|1580.777–1582.377|1576–1613; 1642–1658; 1739|前1576–1580; 後1606–1613; 後1642–1658; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_A4_east_north`|1581.320–1582.920|1575–1614; 1644–1657; 1739|前1575–1581; 後1606–1614; 後1644–1657; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_A4_east_south`|1581.020–1582.620|1575–1613; 1647–1657; 1739|前1575–1581; 後1606–1613; 後1647–1657; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_B_west`|1580.764–1582.364|1576–1612; 1649–1658; 1739|前1576–1580; 後1606–1612; 後1649–1658; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_B_east`|1581.118–1582.718|1575–1613; 1646–1657; 1739|前1575–1581; 後1606–1613; 後1646–1657; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_C_north`|1581.974–1583.574|1576–1599; 1655–1657; 1739|前1576–1581; 後1655–1657; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_C_east`|1582.010–1583.610|1576–1598; 1657; 1739|前1576–1582; 後1657; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_C_south`|1582.119–1583.719|1576–1599; 1655–1657; 1739|前1576–1582; 後1655–1657; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_C_west`|1582.087–1583.687|1576–1598; 1657; 1739|前1576–1582; 後1657; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_D1_short_west`|1582.620–1584.220|1579–1598|前1579–1582|N|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_D1_short_east`|1582.791–1584.391|1579–1598; 1657|前1579–1582; 後1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_E_square_1`|1580.797–1582.397|1576–1598; 1658; 1739|前1576–1580; 後1658; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_E_square_2`|1580.834–1582.434|1576–1598; 1658; 1739|前1576–1580; 後1658; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_E_square_3`|1580.665–1582.265|1576–1598; 1658; 1739|前1576–1580; 後1658; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_E_square_4`|1580.694–1582.294|1576–1598; 1658; 1739|前1576–1580; 後1658; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_E_square_5`|1580.594–1582.194|1575–1598; 1657; 1739|前1575–1580; 後1657; 後1739|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_D_01`|1582.680–1584.280|1577–1598; 1657|前1577–1582; 後1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_D_02`|1582.455–1584.055|1577–1598; 1657|前1577–1582; 後1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_D_03`|1582.454–1584.054|1576–1598; 1657|前1576–1582; 後1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_D_04`|1582.182–1583.782|1576–1598; 1657|前1576–1582; 後1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_D_05`|1582.211–1583.811|1576–1598; 1657|前1576–1582; 後1657|T|research/rome11_olympic_survey.md|
|rome11_olympic1960 / `rome11_olympic_D1_compound_north_chain`|1583.522–1585.122|1579–1602; 1651–1657|前1579–1583; 後1651–1657|T|O02 connected D1 chains/courts, checked against retained Overture61660/61700/61703; approved crocett|
|rome11_olympic1960 / `rome11_olympic_D1_compound_isolated`|1583.311–1584.911|1579–1598; 1657|前1579–1583; 後1657|T|O02 connected D1 chains/courts, checked against retained Overture61660/61700/61703; approved crocett|
|rome11_olympic1960 / `rome11_olympic_D1_compound_west_courts`|1583.159–1584.759|1579–1612; 1641–1657|前1579–1583; 後1606–1612; 後1641–1657|T|O02 connected D1 chains/courts, checked against retained Overture61660/61700/61703; approved crocett|
|rome11_olympic1960 / `rome11_olympic_D1_compound_east_courts`|1583.238–1584.838|1579–1607; 1649–1657|前1579–1583; 後1606–1607; 後1649–1657|T|O02 connected D1 chains/courts, checked against retained Overture61660/61700/61703; approved crocett|
|rome11_olympic1960 / `rome11_olympic_restaurant_01`|1581.522–1583.122|1576–1599; 1655–1657; 1739|前1576–1581; 後1589–1599; 後1655–1657; 後1739|T|O01 original1960 report PDF236 full operating plan:restaurant1–10 on both sides ofCorsoFrancia,6nort|
|rome11_olympic1960 / `rome11_olympic_restaurant_02`|1581.596–1583.196|1576–1598; 1656–1657; 1739|前1576–1581; 後1589–1598; 後1656–1657; 後1739|T|O01 original1960 report PDF236 full operating plan:restaurant1–10 on both sides ofCorsoFrancia,6nort|
|rome11_olympic1960 / `rome11_olympic_restaurant_03`|1581.687–1583.287|1576–1598; 1656–1657|前1576–1581; 後1589–1598; 後1656–1657|T|O01 original1960 report PDF236 full operating plan:restaurant1–10 on both sides ofCorsoFrancia,6nort|
|rome11_olympic1960 / `rome11_olympic_restaurant_04`|1581.677–1583.277|1576–1598; 1656–1657|前1576–1581; 後1589–1598; 後1656–1657|T|O01 original1960 report PDF236 full operating plan:restaurant1–10 on both sides ofCorsoFrancia,6nort|
|rome11_olympic1960 / `rome11_olympic_restaurant_05`|1581.700–1583.300|1577–1598; 1656–1657|前1577–1581; 後1589–1598; 後1656–1657|T|O01 original1960 report PDF236 full operating plan:restaurant1–10 on both sides ofCorsoFrancia,6nort|
|rome11_olympic1960 / `rome11_olympic_restaurant_06`|1581.926–1583.526|1577–1598; 1656–1657|前1577–1581; 後1589–1598; 後1656–1657|T|O01 original1960 report PDF236 full operating plan:restaurant1–10 on both sides ofCorsoFrancia,6nort|
|rome11_olympic1960 / `rome11_olympic_restaurant_07`|1581.173–1582.773|1576–1598; 1656–1657; 1739|前1576–1581; 後1589–1598; 後1656–1657; 後1739|T|O01 original1960 report PDF236 full operating plan:restaurant1–10 on both sides ofCorsoFrancia,6nort|
|rome11_olympic1960 / `rome11_olympic_restaurant_08`|1581.206–1582.806|1576–1598; 1656–1657; 1739|前1576–1581; 後1589–1598; 後1656–1657; 後1739|T|O01 original1960 report PDF236 full operating plan:restaurant1–10 on both sides ofCorsoFrancia,6nort|
|rome11_olympic1960 / `rome11_olympic_restaurant_09`|1581.172–1582.772|1576–1598; 1656–1657; 1739|前1576–1581; 後1589–1598; 後1656–1657; 後1739|T|O01 original1960 report PDF236 full operating plan:restaurant1–10 on both sides ofCorsoFrancia,6nort|
|rome11_olympic1960 / `rome11_olympic_restaurant_10`|1581.241–1582.841|1576–1598; 1656–1657|前1576–1581; 後1589–1598; 後1656–1657|R|O01 original1960 report PDF236 full operating plan:restaurant1–10 on both sides ofCorsoFrancia,6nort|
|rome11_olympic1960 / `rome11_olympic_reception_post_J`|1581.026–1582.626|1576–1598; 1657; 1739|前1576–1581; 後1589–1598; 後1657; 後1739|T|O01 originalPDF236 source operating-plan outline; J post/telecommunications; one of the4source recep|
|rome11_olympic1960 / `rome11_olympic_reception_bank_info`|1580.910–1582.510|1576–1598; 1657; 1739|前1576–1580; 後1589–1598; 後1657; 後1739|T|O01 originalPDF236 source operating-plan outline; Ybank/Kreception/Winformation in the central lozen|
|rome11_olympic1960 / `rome11_olympic_reception_K_west`|1580.591–1582.191|1576–1598; 1739|前1576–1580; 後1589–1598; 後1739|T|O01 originalPDF236 source operating-plan outline; K reception west.3.1m single-storey height and fla|
|rome11_olympic1960 / `rome11_olympic_reception_K_east`|1580.496–1582.096|1575–1598; 1739|前1575–1580; 後1589–1598; 後1739|T|O01 originalPDF236 source operating-plan outline; K reception east.3.1m single-storey height and fla|
|rome11_olympic1960 / `rome11_olympic_cinema`|1581.631–1583.231|1576–1599; 1654–1657; 1739|前1576–1581; 後1589–1599; 後1654–1657; 後1739|T|O01 originalPDF236 source operating-plan outline; CINEMA explicitly labelled on the1960 operating pl|
|rome11_olympic1960 / `rome11_olympic_public_hex_C`|1582.102–1583.702|1577–1599; 1654–1657|前1577–1582; 後1654–1657|T|O01 originalPDF236 source operating-plan outline; Hexagonal pavilionC:report glossaryRestRoom; Minis|
|rome11_olympic1960 / `rome11_olympic_stores_MG_north`|1583.219–1584.819|1579–1600; 1653–1657|前1579–1583; 後1589–1600; 後1653–1657|T|O01 originalPDF236 source operating-plan outline; MG central stores outside the housing boundary.3.1|
|rome11_olympic1960 / `rome11_olympic_stores_MG_middle`|1583.037–1584.637|1579–1597|前1579–1583; 後1589–1597|T|O01 originalPDF236 source operating-plan outline; MG central stores outside the housing boundary.3.1|
|rome11_olympic1960 / `rome11_olympic_stores_MG_connector`|1583.159–1584.759|1579–1597|前1579–1583; 後1589–1597|T|O01 originalPDF236 source operating-plan outline; MG central stores small connecting shed.3.1m singl|
|rome11_olympic1960 / `rome11_olympic_stores_MG_south`|1582.774–1584.374|1579–1598; 1657|前1579–1582; 後1589–1598; 後1657|T|O01 originalPDF236 source operating-plan outline; MG central stores outside the housing boundary.3.1|
|rome11_olympic1960 / `rome11_olympic_luggage_MB`|1582.850–1584.450|1577–1597|前1577–1582; 後1589–1597|T|O01 originalPDF236 source operating-plan outline; MB luggage stores single drawn building; open surr|
|rome11_olympic1960 / `rome11_olympic_sauna`|1582.519–1584.119|1577–1599; 1654–1657|前1577–1582; 後1589–1599; 後1654–1657|T|O01 originalPDF236 source operating-plan outline; SAUNA labelled service strip outside the housing b|
|rome11_olympic1960 / `rome11_olympic_shops_west`|1580.737–1582.337|1576–1610; 1650–1658; 1739|前1576–1580; 後1589–1610; 後1650–1658; 後1739|R|O01 originalPDF236 source operating-plan outline; West long shop/service pavilion; numbered openings|
|rome11_olympic1960 / `rome11_olympic_shops_east`|1580.851–1582.451|1575–1612; 1650–1657; 1739|前1575–1580; 後1589–1612; 後1650–1657; 後1739|R|O01 originalPDF236 source operating-plan outline; East long shop/service pavilion, not a row of copi|
|rome11_olympic1960 / `rome11_olympic_infirmary33`|1582.727–1584.327|1579–1598; 1657|前1579–1582; 後1589–1598; 後1657|T|O01 originalPDF236 source operating-plan outline; 33 infirmary explicitly labelled next to the east |
|rome11_olympic1960 / `rome11_olympic_nuoto_main`|1582.943–1584.543|1576–1589; 1597–1599; 1653–1659; 1725–1738|前1576–1582; 後1653–1659; 後1725–1738|T|O01 catalogue64 printed65:main50x25m,diving20x18m,school25x12.5/12.5x4/20x10; O02 Ministry3882 numbe|
|rome11_olympic1960 / `rome11_olympic_nuoto_diving`|1583.326–1584.926|1576–1589; 1597–1598; 1657–1659; 1725–1738|前1576–1583; 後1657–1659; 後1725–1738|T|O01 catalogue64 printed65:main50x25m,diving20x18m,school25x12.5/12.5x4/20x10; O02 Ministry3882 numbe|
|rome11_olympic1960 / `rome11_olympic_nuoto_school25`|1583.189–1584.789|1576–1589; 1597–1598; 1657–1659; 1725–1738|前1576–1583; 後1657–1659; 後1725–1738|T|O01 catalogue64 printed65:main50x25m,diving20x18m,school25x12.5/12.5x4/20x10; O02 Ministry3882 numbe|
|rome11_olympic1960 / `rome11_olympic_nuoto_school_small`|1583.367–1584.967|1576–1589; 1597–1598; 1659; 1725–1738|前1576–1583; 後1659; 後1725–1738|T|O01 catalogue64 printed65:main50x25m,diving20x18m,school25x12.5/12.5x4/20x10; O02 Ministry3882 numbe|
|rome11_olympic1960 / `rome11_olympic_nuoto_school20`|1583.242–1584.842|1575–1589; 1597–1598; 1657–1659; 1725–1738|前1575–1583; 後1657–1659; 後1725–1738|T|O01 catalogue64 printed65:main50x25m,diving20x18m,school25x12.5/12.5x4/20x10; O02 Ministry3882 numbe|
|rome11_olympic1960 / `rome11_olympic_nuoto_west_stand`|1583.094–1584.694|1576–1589; 1597–1601; 1652–1659; 1725–1738|前1576–1583; 後1652–1659; 後1725–1738|T|O02 Ministry3882 transverse section:11.10m footprint and about6.4m rise; plan's two long-side stands|
|rome11_olympic1960 / `rome11_olympic_nuoto_east_stand`|1583.145–1584.745|1576–1589; 1597–1601; 1652–1659; 1725–1738|前1576–1583; 後1652–1659; 後1725–1738|T|O02 Ministry3882 transverse section:11.10m footprint and about6.4m rise; plan's two long-side stands|
|rome11_olympic1960 / `rome11_olympic_nuoto_service`|1583.009–1584.609|1576–1589; 1597–1598; 1659; 1725–1738|前1576–1583; 後1659; 後1725–1738|T|O02 numbered plan central service silhouette;3.2m single-storey service height estimated from contem|
|rome11_olympic1960 / `rome11_olympic_velodrome1960`|1548.464–1550.064|1549–1556; 1618–1635|後1618–1635|T|O05 CONI1957 foundation plan source contours, O01 originalreport printed72–75 and PDF72 construction|
|rome12_walk2024 / `rome12_pia_north_fountain`|1698.297–1699.897|1696–1712|前1696–1698|Q|research/rome12_modern_tail_basis.md|
|rome12_walk2024 / `rome12_pia_south_fountain`|1698.377–1699.977|1696–1712|前1696–1698|Q|research/rome12_modern_tail_basis.md|

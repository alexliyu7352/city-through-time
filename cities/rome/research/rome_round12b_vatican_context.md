# 330年舊聖彼得：河對岸陸地與最小環境配置

本件只提供研究及[純資料提案](rome_round12b_vatican_context_proposal.json)，未改候選、共享程式或正式city/script，未compile／影片render。基線為唯讀`本機候選/rome_round12_all`。

建議先做連續的原生草／土地表，從教堂西北坡接至哈德良陵與橋頭；保留既有長殿、南側碑與先河後殿的鏡頭。另用一條概括通路、小量疏樹交代城外場所。完成這個地形讀法即停，不必為本鏡頭另建全部墓地、競技場或園林建築。**Horti Agrippinae不能整片冒作330年仍完整維護的早帝國花園。**

## 已讀既有契約

- `FACTS.md` S09／S12／S48／S204、`rome04_lateantique_survey.md` LA06／LA07／LA13、`rome04_lateantique_whole_basis.md`、`rome04_lateantique_templates.yaml`。
- `rome06_medieval_whole_basis.md`、`rome06_medieval_templates.yaml`、`rome06_medieval_integration.md`：800已有院、後世園作不能倒放330。
- `rome_round12_sites.md`：碑的舊位、原底座估值及時代交接已核，不重查或重定位。`rome_restart_lm02_bridge_audit.md`：重用已修正的低隆三中央拱橋，不能重用舊五等拱模板。
- `SKILL.md`與`docs/MODEL.md` Landmarks／Open ground：全部地表走原生`grounds`，貼plate並達牆邊；不加抬高的假陸地平台。

## 來源、年代與可表現範圍

2026-11-07直接讀取以下機構／遺址主管原頁。下列年代是各證據的適用年代，不是把來源網頁年份當古物年代。

|代號／原始機構來源|年代、實際支持|330採法與界線|
|---|---|---|
|V01 [Vatican State，Storia](https://www.vaticanstate.va/it/stato-e-governo/storia.html)，正文前13段|帝國期Vatican右岸有別墅、Agrippina園與沿主路墓地；Cornelia往西、Triumphalis往北；君士坦丁新殿施工時尼祿競技場逐步荒廢並取石。|支持河西岸城外景觀、路向與舊競技場地帶。未給330逐宗地用途、單棵樹、完整園界或競技場殘牆高度。|
|V02 [Fabbrica di San Pietro／Pietro Zander，La Necropoli](https://www.basilicasanpietro.va/it/san-pietro/la-necropoli)，正文第1–6段；沿用S204並重讀|二世紀墓屋原在露天地面；四世紀建殿削去墓屋頂部、回填，並削平向西及向南的雙坡。|支持殿四周切填土／開放地與接牆地表；不把今日DEM宣稱古代標高。**不可把已覆埋的殿下墓屋再立在330殿旁或殿內。**|
|V03 [Musei Vaticani，Necropolis of the Via Triumphalis](https://www.museivaticani.va/content/museivaticani/en/patrimonio-naturale-archeologico/aree-archeologiche/necropoli-della-via-triumphalis/necropoli-della-via-triumphalis.html)；[Period 3](https://www.museivaticani.va/content/museivaticani/en/patrimonio-naturale-archeologico/aree-archeologiche/necropoli-della-via-triumphalis/periodo-3.html)|遺址在Vatican丘路旁坡地，墓分台地、路徑及小廣場；第三期為二世紀中葉至四世紀的墓室景觀。|330墓地存在有據，但該北側遺址不能挪到教堂前景。主頁與第三期頁已讀；第三期頁的摺疊全文未取，沒有據此補個別墓屋尺寸。|
|V04 [Musei Vaticani，2013官方地形圖PDF](https://www.museivaticani.va/content/dam/museivaticani/pdf/eventi_novita/iniziative/eventi/2013/MV_8_Via_triumphalis_mappa.pdf)，單頁已實看|在今日建物底圖上以虛線表示Cornelia／Triumphalis，並分開殿下Cornelia墓地、北側Triumphalis墓地與殿南競技場。|只用相對路向及場所拓樸。**北箭指向圖下**，不可按上北下南誤讀。來源是概括導覽圖，未配準成精確330道路／殘牆足跡。|
|V05 [MiC／Soprintendenza Speciale di Roma，Piazza Pia發掘與移置公告](https://lazio.cultura.gov.it/?p=8625)，2024年發掘；正文fullonica及園林段|Piazza Pia右岸發現Augustus至Nero三期園林、河岸擋牆與柱廊基礎，Caligula水管銘文支持Agrippina園定位；其上／同區後有很可能三世紀的fullonica。|支持右岸園林的歷史及Piazza Pia實址，但**不證明330整片仍為完好花園**。不造330園宮／柱廊或洗衣房：本輪未取得其330使用狀態、完整平面與精確位置。|
|V06 [Sovrintendenza Capitolina，Ponte Sant’Angelo](https://www.sovraintendenzaroma.it/content/ponte-santangelo)，橋史正文|121–134建Pons Aelius以接左岸與陵；三座中央大拱與岸側小拱分開，岸拱擴為大拱及消除隆起是十九世紀工程；天使欄為1667後。|330可有橋。重用12基線的已校正橋型／現存軸地理控制；不得加後世天使、鐵欄或今日五等拱。模型跨度、坡道、可見水上段仍保留原E限制。|
|V07 [Museo Nazionale di Castel Sant’Angelo／MiC，Il Castello racconta la sua storia](https://cultura.gov.it/comunicato/il-castello-racconta-la-sua-storia)，2022-04-08展覽公告|陵於139完成；後世堡壘／居所改造使原形復原存不確定性。|330重用既有`rome04_hadrian_mausoleum`，不改成中世紀`rome06_medieval_castel`或星堡，不另補無據上層。尺寸沿既有LA研究，不新增精測聲稱。|

以上來源沒有提供330逐棵植栽或全區地籍。proposal的草面、有限土面、每個地表工作窗、樹距／冠徑及曲折接路均明列為**有界景觀示意**。草面表示可辨識的未密建郊外陸地，不表示每處都是修剪草坪，也不表示古代沒有別墅或其他活動。不上新的園界／古路精測標籤。

## 可直接沿用的實體與ID

|基線owner／ID|現有資料|處理|
|---|---|---|
|`another_centre / rome04_old_stpeter`|`[12.454,41.90215]`，90°，`site:cut`|完整保留已過模型及位置；不借800形制換位置。|
|`another_centre / rome_round12_obelisk330`|`[12.45427,41.9014]`|完整保留；它已足以提示舊競技場地帶，不再造完好的circus。|
|`another_centre / rome04_hadrian_mausoleum`|`[12.46625,41.9031]`，既有89m基座／64m圓核|不新增第二陵。連續地表須到其基座外沿，而非留出一圈藍底。|
|`people_return / rome06_medieval_bridge_aelius`|現有完整`parts`，中點`[12.4664631,41.9018919]`、−88.021425581°、三中央可見拱及兩岸低坡|只從12基線這一整件clone至330另ID`rome_round12b_aelius330`；不clone模板的舊五等拱。不挪橋、不改已校準垂直數字；只更新年代／basis。|
|`another_centre / rome04_vatican_open_approach`|既有gravel前地|保留並讓連續草／土面覆到它的邊界，避免藍縫。它不是完整早期四面柱廊。|
|`another_centre / rome_round12_stpeter330_earth`|孤立的30m外環，還從建築footprint多扣了0.2m|由較完整地表替換；不要把這個環繼續當全區陸地。新土面可直接包含建物footprint，不留0.2m洞。|
|800 trace內`rome06_medieval_borgo_approach`|北橋入口到Vatican方向的四點折線，已校正接岸|只借北橋入口和有限地理連接，新增330通路另ID。不能把M03中世紀名稱／年代直接當330 Cornelia精測。|

## 最小配置與時序

1. 新`rome_round12b_vatican_suburban_land`為一整片貼地`grass`，覆蓋教堂西北坡、東側開放地，連到陵和北橋入口。proposal給有限工作窗並用既有`osmgeo.water`扣影片真正水面；這個邊緣是現有地理展示控制，**不是330岸線復原**。保留河，地面不跨成河中平台。
2. 新`rome_round12b_stpeter_cut_fill_ground`為低細節`earth`。以既有原生殿nave／transept／apse footprint聯集外擴約12m並接既有gravel，不扣建物內洞；包含四周到牆腳的地面。12m為示意切填露土地帶，不是新考古院界。較大的草面已負責連到岸，土面不再負責假裝整個島。
3. 北橋入口經既有接岸點往西到gravel前地的一條5.5m通路，使橋、陵、教堂共享同一岸。proposal提供可落地的點；其西延接教堂部分為估配，名稱用`Vatican access, schematic`。道路東端不止於河中央，西端不斷在距教堂數十米處。若原生道路與gravel重疊，切短到gravel邊緣即可。
4. 兩小片疏樹放在殿西北及前地東北。它們位於Vatican坡／舊園林區的未密建工作窗，避開已知殿、南側碑／circus谷及接路；**不是發掘樹穴**。`h_m:5,r_m:2,step_m:32`沿現有中世紀景觀小樹的顯示尺度作估配，合計約十餘棵而非滿山密林。草面必須超出樹區並到牆腳，不能只在樹底造小斑。
5. 陸地、陵與Aelius橋本來早於新殿，應在`late_capital_275`已有，不跟`old_stpeter330`一同冒出；殿邊切填土及教堂新接路可跟既有330階段。`another_centre.city.until: people_return`會在800交棒；新330橋不加入跨800保留表，沿800原橋接替，避免重影。按整體owner的既有fall交棒驗證，不另造橋變形動畫。

Cornelia西向及Triumphalis北向可用一小段北支線交代；本鏡頭若看不見則省略。沿路墓地與競技場遺構本輪**不另建量體**：前者有據但北側位置不應挪近，後者四世紀損毀有據卻無330殘牆高度／足跡。已存南側碑保留；若之後確需近看競技場，才另作有配準來源的專項，不能為這輪地表補洞擴建。

## 交給整合者的驗收點

提案只驗資料，不替代最終影片實看。檢查330高看河岸時，教堂、陵及北橋頭之間是連續同一塊陸地；低看側面時，草／土到牆、不見藍環、無矩形高台或河岸鋪成石廣場。橋的兩岸低坡沿原型，樹不擋長殿／碑或穿路。維持既有旁白、字幕、碑與先河後殿的已過構圖。

已做唯讀資料檢查：JSON與兩個原生region有效；連續草面約76.91ha，切填土約1.33ha，兩者與影片原生水面交集均0；934.97m通路中線入水長0；兩個樹窗完全在陸地內，離通路分別至少179.66／78.96m。76.91ha是這個廣角的有限地景工作窗，不能作330園產／空地面積統計。首個`late_capital_275`階段原本沒有`select`，新增舊環境可用其預設接入；**不要把首階段改為只選新增ID**而漏掉原有城市。

如廣角外緣仍露窄藍帶，只在同一有據景觀窗內延伸原生地表到可辨識坡折／河岸；不得用虛構住宅、園牆、密林或大灰prism填空。本件未跑候選驗證，影片驗收由integrator集中執行。

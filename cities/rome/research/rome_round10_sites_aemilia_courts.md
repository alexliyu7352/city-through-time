# Aemilia四級floor與本輪開放院地

只延續本輪列出的Aemilia、Saepta、Vesta、Palatine Stadium及已cut的800舊聖彼得前院。原址、外廓、原parent ID與時期不變；不新增地形引擎，不用水池造坑。

## AEM：四個floor＋atop

沿既有已核[DAR Porticus Aemilia (Emporium)](https://www.digitalaugustanrome.org/records/porticus-aemilia-emporium/)正文第1段：487×60m、50個垂直於NE–SW長軸的vaulted naves、四級朝Tiber下降。既有原文在 `model_reference/rome02_republic_whole_evidence/dar_porticus_aemilia_emporium.txt`。DAR不給四級各自邊界或高差；舊模板提及七縱向aisles及兩兩地坪差，但本件未取得可量的原剖面，不能把四等分稱實測。

新庫 `rome_round10_sites_aemilia_templates.yaml`，具體逐ID合併欄位在 `rome_round10_sites_aemilia_patch.yaml`。主體是原生 `kind: parts, site: parts`，先寫4個487×15m、0.15m薄floor，再寫4組各repeat×50、9.74×15m的vault。每組使用原生 `atop: 0/1/2/3` 站在對應floor；floor保留 `level_*` 名稱方便核對，API實際只接受先前部件的數字索引。不存在巢狀parts，也沒有200個vault各自取DEM。

|floor ID／atop索引|local y分界|朝向／高度需求|估值界線|
|---|---|---|---|
|`level_river`／0|+15..+30m|最靠河、四級中最低|15m帶深是示意選擇|
|`level_river_middle`／1|0..+15m|次低|精確階差無來源數字|
|`level_land_middle`／2|−15..0m|次高|精確階差無來源數字|
|`level_land`／3|−30..−15m|內陸側、四級中最高|15m帶深是示意選擇|

原錨12.47430,41.88054、43°方向下，local +y即NW河側。原8m牆高／原vault截面照舊，原50條跨深度的vault被四個地坪帶分成四段；接縫與屋頂隨地坪分級是示意外量體，不宣稱取得四段古屋頂剖面。所有新部件同原parent階段一起升起，不另編四次建造日期；共和ID `aemilia_warehouses` 與晚古 `rome04_aemilia_warehouses` 各自原exaggeration／分期照舊。

原生四單體probe在 `本機候選/rome_round10_sites_aemilia`：兩期各測raised floor與cut floor。geo4件全通過；**raised floor兩期各clip全0**；cut floor兩期各`terrain_cut4`，不採。採用的四floor由native取得四個共用placement datum，50個vault在各級嚴格共面。這些placement高度仍受今天plate約17m的長軸落差支配，只是引擎落地代理，**不是古地坪測高**；`rome_round10_sites_aemilia_floor_requirements.json`把未知絕對datum／古階差寫null，測得的native placement另列。

高基礎限制須保留：新native清單仍是266%／172%，34.7m螢幕基礎（舊273%／177%，35.1m）。這個patch改正一個地坪誤作四級的布局，不可報「巨大基礎已消失」或「古四級台高34.7m」。沒有以縮址、改古座標或私改地形消清單。兩向原生modelview已實看，geo／clip全0；圖 `本機候選/rome_round10_sites_aemilia_parts/1_4.62.jpg`（沿河同舊機位）、`2_4.62.jpg`（陸側），新舊sheet `compare.jpg`。可讀四條依次朝河下降的vault帶及連續50bay節奏；這是有據分級增量，既有長軸DEM限制不冒稱消除。

## 開放院地的actual surface

原生 `grounds` 只給plate／既有平台明確的地表材質，**不切低、不抬平**。本件以它解決「拿掉平台後院內只剩裸藍板」，不把它當真整地。必要的平地若尚未原生可畫，保留原raised或原薄鋪地，不以新薄板穿進坡裡。

`rome_round10_sites_courts_patch.yaml` 的 `nodes.*.grounds_append` 都是原生grounds欄位；`bindings` 是給整合者的階段／來源對照，不能整段複製進city設定。各ground的ID須加進其 `stage_with_landmark` 原升起階段的 **`select.grounds`**，不是`select.landmarks`；原地標整體退出時同退，若city整體until結束則自然同退。檔案另列能直接匹配的原stage／loss ID與從0起的索引（原stage常沒有ID），並給 `select_append: {grounds: [id]}`。不要默認node開場就鋪地。

|範圍／原ID|需要的地面|具體做法／來源界線|
|---|---|---|
|`imperial_height/saepta_iulia`、`another_centre/rome04_saepta_iulia`|paved公共piazza|[DAR Saepta](https://www.digitalaugustanrome.org/records/saepta-iulia/)列開放公共廣場與marble裝飾，採概括硬鋪地，不畫未核石板圖樣。從既有104×294m內窗扣實際廊體；早期另扣原有斜Diribitorium外輪廓，保既批接口，不補一個新矩形南廊。兩期各1筆ground。|
|`republic_late_city/atrium_vestae_republican`|paved住宅聖區院地|`ad14_hill_completion_sources.md` HV1／[DAR Atrium](https://www.digitalaugustanrome.org/records/atrium-vestae/)的早期鋪地院比較；只取原三翼間21×28m bounded院窗。這是原44BCE示意住宅內的地表用途，不能稱取得該年逐塊mosaic或後期大長院。1筆ground。|
|`imperial_height/atrium_vestae_early`|保留既有0.15m鋪地prism|原parts[0]已是HV1–HV3早期聖區鋪地，並已避Vesta圓廟；不加重疊ground／新平板，不把後期16×56m洞倒入早期。此項只有retain指示。|
|`another_centre/rome04_atrium_vestae`|paved peristyle內院|原parts[0].holes_m的16×56m洞，原輪廓原樣使用。已存PArCo官方Vesta冊 `imperial03_postfire_versions_sources/vesta_official.txt` 印6–7記peristyle、早期mosaic與後期三basins／Constantinian變動；本輪只標硬鋪庭院，不新增有相位爭議的池水／八角物／像列。1筆ground。|
|`imperial_height/palatine_stadium`、`another_centre/rome04_palatine_stadium`|earth園庭／步行內場|[PArCo](https://colosseo.it/mirabilia/stadio-palatino/)低宮殿約10m、三面廊及SW曲端；earth只識別開放園地，不稱整場競技砂場。使用現有149×36m u-ring內側及同一曲端，保原座標；兩期各1筆earth。113版另沿既有兩個22×18m植栽窗加grass，不新種樹。依 `imperial03_tree_audit_report.md` TA02／TA15–18及Caen具名復原比較，不將整場變樹林。|
|`people_return/rome06_medieval_stpeter_atrium`|重用既有paved前院|`rome06_medieval_whole_basis.md` M18鋪前院／quadriporticus；原9c已有`rome06_medieval_stpeter_atrium_ground`，原`medieval800`整體階段及loss2已包含。重用原surface與綁定，不新增63×67m窗：新窗全覆原ground會使原生拒絕空面。|

共7筆新增grounds、1筆800前院既有ground重用、1筆AD14既有薄地坪retain。沒有加整片住宅街區ground、無新池、無假河水、無新花壇圖樣；原庭院邊界只是既有量體內窗，不冒稱新考古描線。

## Stadium：含鄰宮的相對低位檢視

最小原生study把原Flavia、Augustana upper/lower與原Stadium一起顯示，只加入上表earth／grass及原兩端樹；沒有改四棟的site、位置、高度、底板或池子。推薦含鄰宮圖：`本機候選/rome_round10_sites_stadium_context/2_4.68.jpg`（az100、el30、d.065）；另一向為`1_4.68.jpg`。兩張已實看，第二張可讀出沿宮殿側邊較低、有乾地及端部植栽的封閉長園，原藍板不再讀成水池；既有廊牆／宮殿分台已提供圍合，毋須另造擋土牆。

本模型原本已有相對低位。原生量體共同地坪值如下（`p[12]/scale`，引擎實畫screen米；**不是海拔或古測高**）：

|地坪|screen米，已含terrain×2|比Stadium高／低|換回terrain×2前|
|---|---:|---:|---:|
|Stadium|80.814|0|0|
|Flavia|89.057|高8.243m|高4.122m|
|Augustana upper|85.864|高5.050m|高2.525m|
|Augustana lower|69.810|低11.004m|低5.502m|

[PArCo Stadium正文](https://colosseo.it/mirabilia/stadio-palatino/)記其低於Flavia-Augustana約10m；文字沒有把更低的Augustana lower court指定為比較地坪。當前DEM放置代理只有上述約4.1／2.5m的未誇張相對差，不能報「已精確復原10m」。本輪可採「原分台＋乾地花園」的可讀畫面，不需新挖坑；精確古高程仍不明，不硬加−10m。

該study原生 `geocheck: every face points out of its piece`、`clipcheck: ok`；含所有鄰宮、兩端樹與3筆earth/grass，`terrain_cut`、`floating`、`paving_under`等全0。原高平台清單仍存在（Stadium141%），未藉材質把數值消掉。數字與來源在 `rome_round10_sites_stadium_levels.json`；可重用規格 `rome_round10_sites_stadium_spec.yaml`。本輪未採會吞牆的Stadium cut，也不需要以不存在的共用真整地卡住可見的乾地修正。

其餘本輪保9c raised的逐ID理由已列於 `rome_round10_sites_table.md`／完整patch的 `deferred_raised`。Stadium本輪採「原分台＋earth／端部grass」，已表達相對低位與乾地花園、native0；真整地未做／官方約10m未校準只列為精度限制。

完整 `rome_round10_sites_patch.yaml` 現只含54個安全cut（含06舊殿明列維持cut）及Aemilia兩個parts替換，共56個原ID；原28個unsafe cut中其他26件本輪保9c raised，不再混入可套節點。

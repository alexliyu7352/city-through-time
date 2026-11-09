# 03園林逐塊來源複核

建議撤銷 `palatine_circus_slope_01` 整坡喬木，以及三筆「宮殿剩餘地＝園林」配置；Stadium改採內院兩端小植栽窗。Peace改低玫瑰灌籬，保留原庭園用途外框。其他有據園地保留；墓園只將喬木顯示窗收至有文獻的墓後，園地外框不動。**沒有改AD14／AD113原spec、住宅、公建、共享程式或正式影片；沒有生成模型或宣稱模型檢查通過。**

完整採用資料在 [proposal](imperial03_tree_audit_proposal.json)、[GeoJSON圈線](imperial03_tree_audit_regions.geojson)、[可供主代理採用的原生樹區及低植栽parts](imperial03_tree_audit_trees_proposed.yaml)。座標是EPSG:4326 `[lon,lat]`；面積及裁線以EPSG:32633計算。JSON保留每區原圈、原ID、原basis、來源ID、決策、建議新圈和已知／估值；不是只有文字待研究。

## 宮前整坡：撤回無據種植，也撤回只為它拆掉的街屋

`add_imperial_landscape.py:218–220` 直接把 `palatine_palace` 保留區扣建築／鋪地後的餘地指定為庭園；234–240又以十點大窗口扣公共模型產生Circus坡地。這兩種操作只能產生**製作空隙**，不能證其古代用途、樹木分布或113園界。

對照 [Lanciani原圖與舊樹圈](imperial03_tree_audit_palatine_before.png)，圈線跨越宮殿周邊、古代房線及多時期坡面；紅色近代Vigna／Orto標示也不能當113園林。圖沒有畫樹並不證古代無樹；本次撤回的是沒有位置證據的整片林地假說。

[Caen總覽01](imperial03_tree_audit_sources/caen_general.jpg)、[自Aventine視圖03](imperial03_tree_audit_sources/caen_aventine.jpg)把朝Circus一面表現為建築、露台與前庭；沒有模型原來的整片坡林。這是具名學術復原比較，不能升格為發掘出的鋪地總圖。現存Severan Schola Praeconum、Septizodium和多期平台也不能倒補至96／113。

取消樹後的用途處理已有可採資料：

- 保留既有 `augustana_circus_loggia`、`paedagogium_palatine`、Circus及街道。`area_palatina_paving_01` 是Flavia北前方既有鋪地，原位保留，不能搬到南坡。
- `proposal.palatine_forecourt_ground_treatment` 提供外廊內開放前庭的薄 `prism`：隨既有外廊錨點 `[12.486029408426244,41.88717492157819]`、方向−46.28°，局部最大80×16m、厚0.15m，沿原模型內弧留距；圖讀形制及尺寸都是估值。只作同一外廊地坪的薄地面處理，不能另造大平台或改DEM，更不能把整坡鋪成廣場。
- Flavian研究片目前把樹區併入 `palace_clear`，故不只種錯樹，還為無據園界移走早期街屋。依原生既有建築bounds與原6m退距重算，清除範圍縮回具名宮殿及已據內園後，原241塊被選宅地降為123塊，**118塊恢復保留**；清除遮罩撤回102,026.99m²。JSON逐ID列出118塊、整段可保留街段與需重新切分街段；GeoJSON附逐塊圈。這些是原先已批准的示意宅地，並不證每棟實際一直存在至96。AD14／AD113原住宅完全不改。

## AD113全部14區與Flavian選取關係

下面「保留」表示保留有來源／已批准的園用途窗及原圈，**不是證成原樹距、密度或樹種**。原生散植主線 `fce7fbc` 已處理，不造新樹點。原8m／6m等通用樹高與16m等間距仍是製作估值。

|原region ID|處理|可採理由與精確限制|
|---|---|---|
|`horti_sallustiani_01`|保留|S123與Dell’Era印刷133／PDF12，古路／谷坡約束；沿已重描圈。北西接線仍示意，不回用後期in Pincis、Aurelian牆或Villa Ludovisi產界。|
|`horti_lucullani_01`|保留|S123、Platner/Ashby268–269：東古路、西坡；北界不詳。原逐點圈保持，不冒作完整113產界。|
|`horti_maecenatis_01`|保留|S111／S118，Mecenate園產及殿室有據；六點圈只是已用園地窗口，非測繪。Lamiani為同城園藝比較，不證本區每處喬木。|
|`horti_lamiani_01`|保留|Masi等原始研究證植穴、花盆、溝槽及混合園藝；fig2為14–41期局部，不能當113全六點區植樹圖。|
|`mausoleum_garden_01`|縮小喬木窗|S111／市府引Strabo支持墓後林／步道，並指出南側入口。園地用途外框保留；種樹圈只取墓體北緣以北，裁線是保守顯示選擇，非古植被界。|
|`esquiline_retained_oval_01`|保留|導演指定的園地，原住宅開口圈不改。明列製作示意，以具名Lamiani比較；沒有已出土園界，不名為Lolliani。|
|`palatine_terrace_gardens_01`|取消|約22,001m²的扣除餘地，不能由Tiberiana廣義庭園功能推出分散宮坡皆花園；不在原來這個圈自造新古園界。|
|`palatine_terrace_gardens_02` ★|替換|刪Stadium外東坡／餘地圈；改 `palatine_stadium_end_ne_garden_01`、`..._sw_...` 兩個內院端部22×18m窗。官方支持Domitian期園庭，Caen2024圖02支持端部樹＋低花壇；矩形邊、6m通用樹、16m間距是估值。|
|`palatine_terrace_gardens_03` ★|取消|Augustana上院南端與下院北端間的小餘隙，不是已證peristyle植栽床；也不藉撤樹推定它一定是水池。|
|`vigna_barberini_flavian_garden_01` ★|保留|S112／Ubelmann2006 pp653–654 fig1支持Flavian廊內花園，隨已批准宮殿定位的原圈保持。跨期圖黑色Severan神廟不能複製；樹位、7m樹高及13m間距估配。|
|`pompey_portico_garden_01`|保留|S106／S122、Stanford39ac文獻支持樹、泉、休憩。圖中點方框常解為柱基，不能認成逐樹；Severan碎片不是113植栽清冊。|
|`peace_court_-1_01` ★|替換低植栽|保留原38×76m用途外框，撤6m喬木；改一組三對低灌籬，詳下段。|
|`peace_court_+1_01` ★|替換低植栽|同上，另一組；不把兩個大喬木島當成已發掘花壇。|
|`palatine_circus_slope_01` ★|取消|取消整坡樹區，實施上列露台／通行前庭及恢復早期街屋方案；不拿「No empty cities」充當林地證據。|

★為現Flavian研究片取用的6筆；其餘也在AD113整城來源中，不能只修Flavian副本。14筆的原圈與改圈可看 [來源圖集](imperial03_tree_audit_ad113_source_atlas.jpg)：紅橙是舊窗，綠是建議植栽；圖集只是來源疊合，不是模型截圖。

Stadium兩窗完全位於既有149×36m內院的保守核心：以其既有錨點、方向−133.2°，局部x為−60..−38及38..60m，y為−9..9m。中央走道／低花壇仍須保持可見；不能將整條院子改成樹林。不是新增公建或改Stadium原外廓。

## Peace：來源比「花壇」更具體

[市府考古專頁〈La piazza e le fontane〉](https://www.sovraintendenzaroma.it/content/la-piazza-e-le-fontane-0)明記長泉共六座、兩組各三、中央留空，並說1998–2000發掘的破口陶器花盆與植物分析支持玫瑰灌木。其[官方復原圖](imperial03_tree_audit_sources/peace_reconstruction.jpg)顯示低灌籬與長泉，沒有兩大片6m樹冠。因此S122泛稱花壇不能支持舊喬木。

提案沿已批准Peace的錨點 `[12.4877,41.89257]`、方向−141°；每側三個泉道中心x為±16、±28、±40m，各側留一條灌籬，形成12條低植栽帶。每帶1.2×60m、y=−35..25m、高0.8m，全部位於原兩個用途窗內；位置、寬高、長度是沿原模型與具名復原估配，不是植穴／古泉實測，也不宣稱各花盆均可精確定至75或113。

`peace_low_planting.parts` 是低植栽符號的原生prism資料，供主代理追加到既有Peace的同一地坪；不改原廊翼／祠廟，不手算獨立z，不造樹點。此次不另建六座泉，以免超出植栽退回範圍；兩組園用途及中央空間均保留。低物件應讀作灌籬，不能當新砌體牆；尚待主代理模型審查。

## AD14原spec的9區來源關係

AD14頂層 `trees` 沒有 `palatine_circus_slope` 或任何三筆Palatine補植區，不能因為AD113刪坡林而改動AD14山上住宅。AD14不是AD113植栽圈的減量版。

|AD14原ID|處理／來源關係|
|---|---|
|`ad14_garden_dar_horti_north`|保留原界；DAR D01／D02、S130的北部聚合園產復原帶，與113 Sallustiani／Lucullani同地理帶但不共享確切園界。|
|`ad14_garden_campus_agrippae`|保留；D02／S131公共園用途，不能外推到北中Campus公共原野。|
|`ad14_garden_mausoleum_public_park`|保留用途外框；與113同步只將喬木窗裁至墓後北側。|
|`ad14_garden_nemus_agrippae`|保留；D03／S131在Stagnum與Euripus間的具名林地，北西界仍未知。|
|`ad14_garden_horti_agrippae_west`|保留；D02／D03的劇場西園產復原窗，非已發掘樹位。|
|`ad14_garden_dar_horti_esquiline`|保留；D01／S130多園產聚合用途帶，不把Masi14–41局部植穴套成AD14或整區清冊。|
|`naumachia_grove_west_1`|保留；CC05／S141的Taylor–DAR復原分支，西坡／ViaAurelia約束，原池外8m退距不動。|
|`naumachia_grove_south_1`|保留；同分支周林南部用途窗，非古代產界。|
|`naumachia_grove_east_1`|保留；同分支東側用途窗，保持原路及水域；不因113示意宅地出現而推池或林早已消失。|

原始採點見 `ad14_fabric_trace.yaml`，Naumachia見 `ad14_city_completion_uses.geojson`／CC05；本件JSON逐區保留原圈和與AD113同位置的ID交叉索引。所有樹高、冠幅、間距、株數仍是示意；用途有據不等於均勻高樹林已證。

## 來源可核性、分期與存取失敗

25筆新下載／嘗試的原URL、取得時間、HTTP狀態、bytes與SHA256在 [downloads.json](imperial03_tree_audit_sources/downloads.json)；既有來源圖、GeoTIFF、控制、原spec及必讀合約的hash在 [input manifest](imperial03_tree_audit_input_manifest.json)。原圖只作研究，不主張取得影片上屏權。

- **TA19／TA24**：[Ubelmann2006原始建築研究](https://www.persee.fr/doc/mefr_0223-5102_2006_num_118_2_10260)，pp653–654、fig1；Flavian廊內庭園有據，圖例分Julio-Claudian／Flavian／Severan。原S112所引David／Fedeli／Villedieu2013 PDF本輪兩個URL均SSL失敗，未冒稱重讀；以本原始研究補核用途。
- **TA02、TA15–18**：[Caen宮殿原頁](https://rome.unicaen.fr/monument/palaisdomitien/)，2024復原圖01總覽、02Stadium、03自Aventine、06總覽。圖中花壇、樹木及完整露台均屬復原比較，不當考古植栽圖。沒有越級使用影視來源，因具名研究／復原已足夠作有限比較。
- **TA20／23**：市府原始考古解說與其復原圖，見Peace段；低灌木、六泉兩組有明示，具體75／113配置仍未由本頁逐穴分期。
- **TA08／21／22**：[Masi等原始植物研究](https://link.springer.com/article/10.1007/s00334-023-00960-y)，fig1為出土範圍，fig2為14–41期植穴。可分植物類別與修剪園藝，不能推出本片整園密度。
- **TA11**：[Dell’Era原章](https://api.unil.ch/iris/server/api/core/bitstreams/ebfa9151-b5d4-468a-a3f2-3b93cacc34d1/content)，印刷133／PDF12；兩Salaria間Sallustiani與400後in Pincis分開。
- **TA12**：Platner/Ashby Luculliani原頁HTTP存檔失敗，瀏覽工具正文讀取成功；其東西約束、北界未知與既存S123一致。失敗保留於downloads，未冒稱原站HTML已存。
- **TA03／04**：PArCo兩頁直接HTTP均SSL失敗；Tiberiana瀏覽正文成功，另有既存 `model_reference/imperial03_events_tiberiana.html` 保留hash。這只支持西北宮殿有花園功能，不能證原三筆任意台地圈。

Caen的分期須限制在其文字真正說到的範圍。原文短段為：

> l’aménagement d’une façade vers Le Grand Cirque et l’installation d’un accès direct à la loge impériale de l’édifice de spectacle

下一句把該項整體改造歸Trajan；本段沒有逐件識別／定年現模型100×28m的半圓外廊。它能限制直通包廂連接不能無條件倒放Flavian，**不能單憑此段斷言半圓外廊本身必非Flavian**。本件保留已批外廊，亦不把Caen晚期完整立面抄成96年建築。這個限制與樹區取消互相獨立。

## 交付驗證及主代理接手

以 `uv run --no-sync --offline python -I cities/rome/research/imperial03_tree_audit_build.py` 完成資料驗證：AD113 14／14、Flavian 6／6、AD14 9／9均有決策；所有圈有效；12低灌籬均在原兩庭園用途窗內；原241塊宮殿轉用宅地可精確重算，提案沒有多拆任何一塊。詳 [validation](imperial03_tree_audit_validation.json)。這不是native模型、clipcheck、geocheck、落地或畫面驗收。

待主代理決定採用Stadium兩端復原比較、Peace低灌籬、墓後保守喬木窗與薄前庭；再將改動同步於AD113研究來源／Flavian副本與相應派生輸出，重切 `palace_clear` 舊街段，接手模型核驗。已批准住宅與公建的原幾何不由本件重做。

# Cermalus第一區：四個屋構的有界估配

採用 **A/B＋C/E四個屋構**，保留已批兩屋的完整位置、朝向與形制，新增兩個用途未定的屋構、相連彎徑及兩處戶外活動面。這可稱「Cermalus第一居住區示意」；不能稱完整Cermalus村落復原、四棟出土住宅或四戶。可執行資料為 [layout.yaml](rome01_cermalus_evidence_layout.yaml)，所有點均同時保存原圖像素、native局部公尺與經緯度。

本件只負責來源與配置依據。正式模型的屋頂、入口、道路及落地驗證由district交件；本件沒有修改正式片、房型模板、既有來源或共享程式。

## 可定位依據與窗口

F01印刷p.5區分「capanne di differente tipologia e cronologia」，北側n.3有中VIII世紀使用相關填土；圖2不是四屋同時的地籍。正文另記Scalae Caci以西、原小屋區以北及Magna Mater以西的相關痕跡，支持居住群不只孤屋，沒有給本期逐戶數或村界。圖1的後期神廟與階梯僅供定位，未移入VIII世紀畫面。[Pensabene2009，pp.5–7、圖1–2](https://www.persee.fr/doc/efr_0223-5099_2009_act_425_1_9807)

選定窗口圍繞圖1a北屋候選A，不擴至整座Palatine、整座Magna Mater聖區或圖1d的地下構造。來源所說的其他延伸痕跡屬存在與方向證據；C/E的實際屋位沒有逐一對應那些痕跡。工作多邊形外包 **26×25m＝650m²**，不規則面積 **523m²**。這是本次審查範圍，沒有考古村界、古地塊、古坡折或產權的意義；17m仍只是不相容定位讀法的工作包絡，不能拿來畫圓形村界。

圖1原檔 `model_reference/founding_pensabene2009_p6.jpg` 為1737×2162px。沿用批准的四個神廟實體牆角及 `pipeline/register.py` 原生similarity，未重開北向分支。此次native殘差0.26–0.97m，留一控制誤差0.51–1.88m，只表示同一構造角點吻合；23.17°印箭頭分歧與17m工作不確定仍保留，不能宣稱米級考古定位。

## 為何由六個收至四個

最初六屋方案只以原pair外加兩組近鄰關係推數，沒有充分的數量／密度比較，已撤回。原六屋註記圖保留為 `model_reference/rome01_cermalus_evidence/initial_source_overlay.png`，不作最終配置或考古證據。最終不保留D/F。

重用Gabii原圖5A與既有原像素線：0–16m尺為[48,779]→[344,779]，18.5px/m。取原圖矩形 **[130,190.75]→[611,653.25]**，正好26×25m、650m²，完整包住下列四個可辨面；這與Rome外包矩形相當，不是與523m²不規則工作面積相等。原圖、框線及逐面數據見 [比較圖](model_reference/rome01_cermalus_evidence/gabii_equal_window_overlay.png)、[比較JSON](rome01_cermalus_evidence_gabii_comparison.json)。

| Gabii圖5A的面 | 完整可見描線面積 | 可支持的計數／功能 |
|---|---:|---|
| D-H1存凹面 | 11.43m² | 主居住屋；出版解讀範圍約45m²，與存凹面界線不同 |
| D-H2 | 9.96m² | 有上部屋構；可能居住，也可能另用；出版約13m² |
| D-H3存凹面 | 3.00m² | 有屋構依據；北界失存、用途未定；出版至少4.2m² |
| Area C東側大面 | 24.72m² | 同期居住／活動構造相關面；不能證為完整獨立房屋或另一戶 |

這是 **三處有屋構依據＋一處大面**，不是四戶。N01校樣印頁21明說“one, possibly two, huts that could function as dwellings”；戶外活動重要，不能將每一坑溝、柱洞、空白或大面都補成屋。Gabii本身是一個多功能複合體；後期H4及石構階段沒有與前三屋並立。N02圖5A採中VIII世紀概括分期，N01對初占居精確年代仍保留，不能說753年的瞬間普查。[Evans等2019原作者校樣，pp.5–13、21–22](https://www.researchgate.net/profile/Laura-Motta-7/publication/334245393_An_Iron_Age_Settlement_at_Gabii_An_Interim_Report_of_the_Gabii_Project_Excavations_in_Area_D_2012-2015/links/622c2594a39db062db95e45d/An-Iron-Age-Settlement-at-Gabii-An-Interim-Report-of-the-Gabii-Project-Excavations-in-Area-D-2012-2015.pdf)

在650m²外包矩形內，Gabii三屋約4.62個屋構／1000m²，連不完整C面上限是4個位置、6.15處／1000m²；Rome四構為6.15，原六屋為9.23個／1000m²。後兩者是製作數值，前者也不是完整古代密度調查。**四個是本次屋構估配的選定上限**：保留兩個已批構，再加兩個，與上述最多四個位置的量級相容；並未判定C面完整有屋。四個批准小型身體合61.70m²，與N01三屋出版約45＋13＋至少4.2m²的總量相近，僅作量級交叉檢查，沒有拿出版解讀面積替換黃色存跡，亦不把49.10m²存跡總面積硬轉成覆屋率。這些資料不能排除古Cermalus較密或較疏，足以讓本次停止在四個有界示意，不支持直接擴成六個獨立住宅。

## 逐屋清冊

以下像素均在F01原圖。朝向是原生theta（自東逆時針），不是頁面角度或出土門向。完整精度以YAML為準。

| ID | 原圖中心pixel | theta | 本地存在／功能 | 落位與方向證據 |
|---|---|---:|---|---|
| A | [984,1173] | 30.15155° | 有考古圖像候選；非已證Romulus宅 | 沿批准點；F04形制／北向工作分支；A＝n.3文字對照仍未證 |
| B | [1077.9216,1212.1070] | 90.15155° | 可能居住伴構；非另一戶實證 | 保留批准比較估配；非F01另一出土屋 |
| C | [905.8809,1305.5386] | 100.15155° | 估配屋構，功能不指定 | 依Gabii非平行近鄰及戶外關係估配；本地位置、門向無實測 |
| E | [865.7078,1099.8435] | 35.15155° | 估配屋構，功能不指定 | 接續同一活動地面；本地位置、門向無實測 |

A/B中心距6.744m、身體淨空約2m不改；A–C中心距10.20m、A–E9.22m、C–E13.89m，身體淨空約5.81／4.21／9.31m。作比較的Gabii存凹面中心距5.85／10.80／20.41m、最近存凹面距1.91／7.46／15.32m，顯示可有緊鄰及較疏關係；後三者不等於完整牆距、檐距或街寬。沒有按羅馬全區套單一平均間距，也未複製Gabii尺寸較大的H1。

四個構均用已批准Capanna A外形，是這個布局與落地審查樣本的 **4/4模板選樣**，不是古Cermalus住宅形制100%的結論。沒有本地同期房型比例；C/E的功能和家庭歸屬不作判定。輪廓和上部的來源層級繼續沿既有F02/F04/NF01，沒有新增考古屋高或層數主張。

## 入口、活動地面及路徑

六條彎徑骨架有共同接點，連A/B/C/E門前；兩處活動面中心在A局部座標[-4.5,-1]、[2.3,4.7]。主體是出入及戶外生活的比較估配，沒有路線遺構、路權、院界或公共廣場證據。步徑1.2m參照已批准門洞約1.23m作單人出入製作值；局部放寬3.0／2.5m只表達活動地面，沒有同期路寬實測。可按門廊及當前地形挪動支線、改局部寬度，需由district記錄；不畫院牆、石鋪、路緣、車轍、牲畜圈或水池。原生路面若呈硬條塊，屬顯示限制，不能由材質反推古硬鋪面。

## Davico年代用語更正與可核來源

先前將「XI–X世紀」稱作Davico村落的整體年代不準確，應停止引用該說法。F02物件頁第一正文段：XI–X出現在Capanna A復原所比較的屋形骨灰甕年代；第二正文段末明說“Il resto del villaggio è stato invece ricostruito liberamente.” F03原PDF **印頁2**，村落照片下第一段圖說將可復原的聚落寫為“dal IX secolo a.C. fino al VII secolo a.C.”，同段說三座未復原輪廓外其餘自由復原；下方單屋模型圖說的XI–X仍修飾骨灰甕。**排除理由是跨期及自由復原，並非村落全屬XI–X。**

| ID | URL／原檔／本輪核讀位置 | 可用範圍 |
|---|---|---|
| F01 | [原刊](https://www.persee.fr/doc/efr_0223-5099_2009_act_425_1_9807)；`model_reference/founding_pensabene2009_p5.jpg`至`...p11.jpg`；本輪逐頁圖讀，p5另重新開web正文 | 圖1a相對位置、圖2跨期序列、北屋年代及其他痕跡；未取得1951原刊 |
| F02 | [PArCo物件頁](https://colosseo.it/opere/casa-romuli-modellino-di-capanna-e-plastico-del-villaggio/)；`model_reference/founding_parco_casa_romuli.html`，兩段正文重新解析核讀 | A形制及自由村落復原界線；本輪web逾時，使用既存官方原HTML |
| F03 | [Abitare原PDF](https://colosseo.it/sito/wp-content/uploads/2021/02/Abitare-sul-PALATINO.pdf)；`model_reference/founding_parco_abitare_palatino.pdf`，印頁1–2原嵌入頁 `founding_parco_abitare_page-000.jpg`／`-001.jpg`實看 | Cermalus位置、占居概述、IX–VII村落圖說及自由復原；未由導覽位置圖推村界 |
| F04 | [Coarelli官方原圖](https://colosseo.it/sito/wp-content/uploads/2020/11/CAPANNA_COARELLI_GUIDA.jpg)；`model_reference/founding_coarelli_capanna_a.jpg`，全幅平剖與北向重看 | 已批形制與門廊；不是逐屋群落普查 |
| N01 | 上述Evans等2019原作者PDF，校樣印頁5–13、21–22，本輪web原PDF重開、功能原段重核 | 三屋、功能及年代限制；校樣頁碼不冒稱正式刊頁 |
| N02 | [作者接受稿](https://eprints.gla.ac.uk/234050/2/234050.pdf)；`model_reference/rome01_neighbors/gabii_samuels2021_aam.pdf`／`.txt`，PDF9–10正文、57頁圖說；[原圖5](https://figures.academia-assets.com/83250028/figure_005.jpg)本地1944×989原圖實看 | phaseA同代比較、C/D較大活動複合體；虛線為後期街道，不作VIII街界 |

所有第三方圖只供研究，未核本片再製上屏授權。原檔雜湊、大小、尺寸保存在 [assets](rome01_cermalus_evidence_assets.json)，舊來源未改寫。

## 未定項與驗證界線

| 項目 | 保留的不確定／本件處理 |
|---|---|
| 年代 | 中VIII世紀窗口，不是753年精確戶籍；四屋跨期圖不並立 |
| 絕對位置／北向 | 選原生四角分支；保留23.17°矛盾與17m工作包絡 |
| 地面 | 今日DEM及site:cut不等於古地坪；不得稱無填墊或古台基實測 |
| 數量／用途 | 四為估配上限；一個來源候選加三個比較構，無四戶或全村密度主張 |
| C比較面 | 未證完整獨立屋，不能作第四戶的考古證明 |
| 房型比例 | 4/4沿批准型僅為本次選樣；本地古代比例未知 |
| 通行／空地 | 全線與寬度估值；活動面非產權／硬鋪界；須由實作核入口接觸與避讓 |

已實際重跑 `uv run --no-sync --offline python -I cities/rome/research/rome01_cermalus_evidence_prepare.py`：四個身體多邊形有效且都在工作窗口內，A/B原像素與朝向保留；Gabii四個可見描線全在比較矩形內。這些是來源幾何／資料驗證，**不是**正式模型geocheck、clipcheck或全片驗收。最終來源註記見 [final_source_overlay.png](model_reference/rome01_cermalus_evidence/final_source_overlay.png)。

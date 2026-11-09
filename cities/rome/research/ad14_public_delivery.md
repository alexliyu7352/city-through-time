# AD14 公共量體：有限研究包交接

本片已依主代理指示停止新增研究。只寫`ad14_public_*`；沒有改正式配置、已過樣區、FACTS或共享程式，沒有compile/capture。以下「可審」指有原生資料與basis可供形制審核，不表示已過模型或整城check。

## 立即可接的資料

- `ad14_public_inventory.json`：107件逐件keep22／revise10／omit75，保留原geometry id、錨點、版本標記及來源。主代理已採19件keep；protected3以原AD14樣區原件為準。
- `ad14_public_keep_proposed.yaml`：22件原生keep拷貝。**不能拿其protected3覆寫已過樣區。**
- `ad14_public_revisions_proposed.yaml`：Circus／Aemilia／Caesar三件；Aemilia仍待主代理對街面採用。
- `ad14_public_additional_proposed.yaml`：Augustus四半圓／Pantheon低邊界假說／Jupiter三件。
- `ad14_public_reservations_proposed.geojson`：七處公共預留區；Polygon是規劃避讓輸入，**不是可塞入native landmark的Point trace**。公開court／track本身也屬公共用地；不以對稱extent代替實際範圍。每件status及basis分開原圖、形體候選與未解形制。
- `ad14_public_controls.json`：Aemilia五點套合與殘差、Augustus帶尺平面採點／Mars錨點、Pantheon現代圓弧擬合／前廊軸。
- `ad14_public_sources.md` AP01–18、`ad14_public_source_index.json`、`model_reference/ad14_public_downloads.json`：來源、讀取狀態、URL／雜湊／權限與失敗下載紀錄。官方圖尚無影片上屏授權；OSM沿ODbL。新FACTS句供主代理選用於`ad14_public_facts_proposed.md`。

## 十件revise逐項採用表

|id|本片最大可用內容|尚需主代理處理／有界缺口|
|---|---|---|
|circus_maximus|621×118m；28m席帶；三席區／12閘；17m估高；原址軸；原生parts與完整公共場地reservation|三區不是三層外拱廊。缺木支架、完整外廊／shops／euripus。10BCE第一方尖碑存在但本候選未加；無永久spina／Titus拱／第二碑。需形制sheet。|
|basilica_aemilia|90×27m含側廊主廳、15店／16券雙層街廊；源圖街前線套合支持x≈−30m；約44.8×99m佔用預留|保持hold至root接受約5m定位誤差與店深／walk估值。61.4m是對稱extent，不是真實佔用寬。非對稱第四廊／三條入口未畫。|
|caesar_forum|同址三邊柱廊＋Venus＋SW店面原生資料，約160×75m來源近似圍區|北接合／Chalcidicum不定。20店面開口是Aemilia店寬比較細分，不是出土店數；Venus上部為早期Castor比較。需sheet。|
|augustus_forum|官方帶50m尺四半圓平面與古今疊圖已存；兩主要／兩西小半圓原生方案和來源outline|小半圓圖說是假設；南小Nerva97拆、北小Trajan112–113拆。Mars點配準仍約5m誤差。source圖讀橢圓半體／高度估值需sheet；小間與不規則消防牆未畫。|
|jupiter_capitolinus|同Caffarelli址、53×62×3.6m基座；17.67m柱按Vitruvius寬1/3估；原生外量體代理|非三內殿／三排六柱完整復原；DAR基礎53×62與其他官方55×60是不同近似，這次選前者需root接受。需sheet。|
|atrium_vestae|早期用途／12BCE Domus Publica與四面地形界線已核|缺Scott1993 fig.15可量平面及南界套合。**不交104×55m後期院的替代bbox，也不把此地標為空地。** 下一個具體動作是取得該圖，先配Vesta廟／Sacra Via／Via Nova。|
|horrea_galbana|晚共和倉儲存在、三院不同與東院未知已核|缺FUR24a/c＋Lanciani pl.40疊圖量讀；既有DAR標籤附近150×180m三同院不是可採早期形體。可保留區域倉儲用途，不能固定原三院。|
|agrippa_baths|DAR早期圖示約68×135m實塊reservation，位Pantheon南／Saepta西；25/19/12BCE分期|此為publisher概略外廓，不是逐室平面；缺早期房間／北界與同期浴場高度比較。未把113版Trajan類比12/18m屋群換年。|
|apollo_library_halls|28/23BCE已存在；一廳分區／兩空間有爭議|早期所在精確footprint與Danaids廊接合不定，不能只刪舊18×27m雙廳的apsis再說早期。下一個動作是取得Apollo區早期分期平面；此片不造新座標。|
|forum_civic_paving_01|用途保留；既有polygon已確認holes=[]，本身沒有後期建物切孔|原44×125m粗估範圍仍需與已過樣區鋪地相減／合併，避開Caesar廟、Rostra等早期紀念物；這屬布局資料整合，**保持已過樣區原鋪地不變**。不需新增建築量體。|

## 五件new_forms_required

|id|可用資料|採用界線／下一個具體缺口|
|---|---|---|
|pantheon_agrippa|北廊44×20m／10柱、北伸7.75m；OSM圓弧／前廊控制；原生候選與precinct|候選選Tortorici低圍牆露天分支；0.61m厚／1.65m是所報早期牆片的存值，僅最低邊界代理，**不是已確定AD14全高**。圓院覆頂／環廊高度尚未解。root應先決定是否採這個最小候選；不得默認為完整復原。|
|diribitorium|已核7BCE覆屋；DAR略斜外廓約137×46mreservation，接Saepta南|100羅馬尺是木梁長度，不能當館高／全短邊。未有分跨／內支承可量圖，不畫一個跨度137m的通用大屋頂。下一個動作是核FUR35碎片及Augustan牆線，再選覆屋代理。|
|porticus_liviae|7BCE四廊院與Via in Selci垂直控制已核|缺FUR平面對現代街廓的採點；這次新下載crop偏北、未含院體，已明列不可用。中央泉／壇／廟未定。先取得含院體的原圖，不能用329 label直接立中心。|
|domus_augustus|沿已保存早期研究：小室有Carettoni實測比較，兩古台地有7–9m相對高差|尚未有完整兩台地源圖→地理控制與可採用建築分件。7–9m不能當DEM+8m；現代參觀路線不能當古整宅外廓。下一個動作是用已保存Coarelli/Carettoni平面配Apollo基台及已知房群；不擴Flavian宮殿到14年。|
|livia_western_registered|既有`livia_western_sample_plan.json`約21×24m西房群、兩native屋頂候選及來源可重用，未改樣區|仍缺官方圖北箭頭／可辨西房群點到OSM的原址配準，不能用39.75×23.24m整宅矩形拉伸。B空間屋頂候選未獲單獨批准；採用需root決定。禁止補完整東院／上層。|

Taurus amphitheatre只保留29BCE–AD64存在記錄；無確定地點。Naumachia不在本片原10revise／5new清單，本片未另擴研究；接既有fabric／來源分工。

## 驗證界線

只跑兩份候選YAML的`landmarks.check`、keep schema、107件清冊計數、七個reservation幾何有效性與id核對。結果存`ad14_public_validation.json`。未測原生clipcheck／modelview／eraview，未生成任何模型或截圖，也未確認全城零衝突。

可再現資料生成順序為`ad14_public_inventory.py`（第一批原清冊）再`ad14_public_finish.py`（收尾來源控制、候選、reservation及19件已採註記）；兩者均只讀既有來源、寫本片prefix。主代理後續採用決定以自己的正式紀錄為準，勿因重跑第一批腳本覆蓋後續採用狀態。

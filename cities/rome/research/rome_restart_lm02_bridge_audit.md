# LM02／1300 Aelius 橋錯置審查

結論：**城市橋軸輸入錯置，並且共享 parcel 工具漏掉真正河面，兩個問題同時存在。** 原生 `arches` 沒有本例所疑的方向／座標轉換錯誤。不能把指定圖上的住宅交給 AI 畫成河。先把河面避讓問題送回主線修復，再在候選修正橋軸與當期橋形，重建受影響的兩個住宅 owner，重新取得 LM02 定格。

已實看指定圖：`本機候選/rome_restart_prefix_v1/build/review/living/lm02_explore/az255_el30_d0.025.jpg`。時刻 527.53s（08:47.53），800 owner `people_return` 與 1300 owner `people_return_late` 同時存在；橋由前者持有，後者沒有另造一座橋。

## 可量驗結果

量測以候選現有 `build/data/model.json`、`water.png`、`era_people_return.json`、`era_people_return_late.json` 為準；沒有 compile、browser 或模型改動。完整數字與逐房群中心、原生記錄在 [量測 JSON](rome_restart_lm02_bridge_measurements.json)。UTM EPSG:32633，模型比例 0.0001，模型 x 向東、z 向南。

| 項目 | 現有 Aelius | 現況 OSM 橋軸控制，僅作位置控制 |
|---|---|---|
| 北端 `[lon,lat]` | `[12.46622,41.90273]` | `[12.4664146,41.9024566]` |
| 南端 | `[12.46685,41.90196]` | `[12.4665116,41.9013272]` |
| 中點 | `[12.466535,41.902345]` | `[12.4664631,41.9018919]` |
| 長度 | 100.250m | 125.720m |
| UTM local x 方向，自東逆時針 | −60.257963° | −88.021426° |
| 自 UTM 北順時針方位 | 150.257963° | 178.021426° |
| 原生水 mask：北端／中點／南端 | 0／145／255 | 15／255／75 |
| 軸線落在 mask≥128 的長度 | 51.538m | 113.488m |

現有中點比控制偏移 50.686m；北／南端分別偏移 34.398／75.698m，軸方向差 27.763°。現有橋不是橫跨整個河面：它從北岸陸地斜向河中，沒有到達南岸。

現有原生橋 deck 是 `era_people_return.json` 記錄 12125：中心 model `[-0.27687,-0.03323]`，rotation `1.0516998rad`（60.257963°）、長 100.250m、寬 7m。其 WGS 外包為 `[12.4661837201,41.9019435545,12.4668856863,41.9027464142]`，四角見 JSON。這與 `landmark_site` 由 from/to 算出的中心、長度、方向一致：`pipeline/citygen.py:1560` 算 UTM theta，`Builder._emit` 將其寫為 model rotation `−theta`，沒有鏡像或再轉一次。

水 mask 是候選真正使用的 4096×3916 檔，每 pixel 約 5.671m；以 ≥128 作幾何量測門檻（渲染邊緣本身是平滑值）。沿 lon=12.4664631 的局部河面緯度界限見 JSON，像素邊界有約一 pixel 的量化誤差，不能當古岸線。檢查 ROI 是以 `[12.4665,41.9019]` 的 UTM 為中心、東西各 180m、南北各 140m；WGS 外包 `[12.4642821347,41.9005924001,12.4687177823,41.9032075629]`。

| 同時在場 owner | ROI 內住宅群 | 與原生水面相交 | 群中心在水中 | 住宅水平投影與水面交集 |
|---|---:|---:|---:|---:|
| 800 `people_return` | 79 | 51 | 47 | 4,667.443m² |
| 1300 `people_return_late` | 111 | 42 | 36 | 3,070.897m² |

住宅群按 native records 的 building pivot `[15,16]` 分組，面積為 `part=FAB` 幾何聯集與水的交集；不是戶數或人口。兩個 owner 不相加成去重城市統計。ROI 內 mask 水面共 36,928.491m²。**房屋確實落在引擎已畫出的河上，並非只有橋放錯使乾地被誤認成河。**

## 來源原文與橋形限制

1. 原始橋位置資料：[OSM way 25752465](https://www.openstreetmap.org/way/25752465)，標記 `bridge=yes`／`name=Ponte Sant'Angelo`／`old_name:la=Pons Aelius`。另有實體外包 way134399943，`man_made=bridge`／`old_name=Pons Aelius`。本輪直接取 OSM map API 原 XML，抽取結果、完整 API URL 與 geometry 留在 [OSM 收據](rome_restart_lm02_bridge_osm.json)。這證現況橋軸，不能把現況長度、岸線、五近等拱當作1300實測。
2. 本地 M03 原文：`cities/rome/research/model_reference/rome06_medieval/M03_streets.txt:219` 明列晚中世紀仍用 Aelius、Cestius、Fabricius、S.te Mariae 四橋，並描述通向 Vatican／Lateran 的道路；**沒有現有 from/to 數字，也沒有五等拱的依據。** 原取得地址與 hash 可追到 `rome06_medieval_source_receipts.json` 的 M03；目前端點的直接作者來源是 `rome06_medieval_whole_prepare.py:100` 手列數值。
3. [羅馬文資局橋史](https://www.sovraintendenzaroma.it/content/ponte-santangelo) 說明三座中央大拱保留、岸側原小拱在十九世紀堤防工程中擴為中央大拱尺度，且原橋面隆起被消除。它也把 Bernini 十天使放在1667後，不能出現在1300。
4. [Cantatore 2012 作者／大學原摘要](https://iris.uniroma1.it/handle/11573/467936) 的義大利文明确原構共八拱、其中五小拱，現況為五近等拱。英文摘要把「其中」誤成「plus」，本報告採義大利文，不作13拱。未取得全文，不把原構八拱都確定為1300仍開放的完整斷面。
5. [Museo di Roma 原物條目](https://www.museodiroma.it/it/opera/testata-di-ponte-elio-scoperta-durante-la-sistemazione-del-lungotevere) 明列1892堤防施工與小拱替換。原物是 Sartorio 1894 的出土橋頭記錄，不能直接當1300河岸復原圖。

來源足以否定現有「100m五等拱／Fabricius類比」作 LM02 近景，但不足以給1300完整岸側小拱的精確長度與開閉狀態。最小正確表現應以三中央大拱＋較短較低岸段的原生 `parts` 示意，將岸段長度、坡度、現況河面明列估值；不要只改 from/to 而保留五等拱，也不要用126m現況外包宣稱古橋全長。可先把軸線改正，但那只是資料修正中間態，不是可生成 living 的完成模型。

## 共享缺陷最小案例

檔案：`raw/cities/rome/osm/water_3db0432b311b.json`。真正橋下河面是 **relation5071**，tags 為 `natural=water,type=multipolygon,water=river`，**無 name**；`pipeline/prep.py:153–170` 能將其 members 接合並畫出水面。相反地：

- `tools/parcels.py:166` → `osmgeo.rings(...,'Tevere')`，`pipeline/osmgeo.py:16` 只選 name 完全相等者。
- `tools/parcels.py:167` 再只留首尾相同的閉環。現有三條 named Tevere geometry 只有一條閉環，而且距橋約1km；本地真正河段只有開放中線 way547426106，且 relation5071沒有名字。
- 800及1300的 Borgo parcel YAML 都已宣告 `water: {osm: Tevere, buffer_m: 18}`，但上述 reserve 在 ROI 內為 **0m²**，橋中點距該 reserve 1,008.534m。這是已宣告避水卻無效，不能以「示意宅」合理化。

重現只讀取快取，不 compile、不開頁面：

```sh
uv run python -I - <<'PY'
import sys, json
from pathlib import Path
sys.path.insert(0, 'pipeline')
import osmgeo
from geo import Frame
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
b = Path('本機候選/rome_restart_prefix_v1/build/data')
m = json.loads((b/'model.json').read_text())
f = Frame(m['box'], m['scale'])
els = osmgeo.elements('本機保留檔/rome', f.area)
rings = osmgeo.rings(els, 'Tevere')
kept = [r for r in rings if len(r)>3 and r[0]==r[-1]]
reserve = unary_union([Polygon([f.to_utm.transform(*p) for p in r]) for r in kept]).buffer(18)
x,y = f.to_utm.transform(12.4665,41.9019)
print('named rings, closed, local reserve area:', len(rings), len(kept), reserve.intersection(box(x-180,y-140,x+180,y+140)).area)
e = next(e for e in els if e['type']=='relation' and e['id']==5071)
print('actual water relation:', e['id'], e['tags'])
PY
```

期望現有輸出：`3 1 0.0`，以及 relation5071 的三個無名河面 tags。這與本報告量測的 native mask 水面有實質矛盾。主線應在共享水幾何解析／選取層修復，讓 parcel 的水域避免與 prep 的已繪河面契約一致；本支線沒有用自寫 mask 裁屋繞過。

## 候選最小修法與歸屬

1. **主線共享修復**：修上述水域 selection／polygon 重建，保留有效 `water` 宣告。重跑受影響 Borgo 800與1300 parcels，並檢查同一產生器的其他河岸區，不可只處理1300可見住宅。公共橋 site 仍用 `citygen.landmark_site`；只移動／捨棄和有據水面及橋址相交的示意 lot，保留其餘住宅。街道在水內的錯誤路段也需改在原兩岸接橋頭，不能保留河底交叉路。
2. **候選城市輸入**：800 owner 的 id `rome06_medieval_bridge_aelius` 是本例真正持有者，先把位置／軸改用 `[12.4664146,41.9024566]→[12.4665116,41.9013272]` 作控制；1300保留引用／存續，不另造重複橋。此 patch 僅修軸，不能作最終橋形採用：

```yaml
# people_return.city.landmarks[id=rome06_medieval_bridge_aelius]
from: [12.4664146, 41.9024566]
to: [12.4665116, 41.9013272]
# 125.720m是現況控制軸長，非1300古橋測繪長。
# 最終近景：改為同軸parts，3中央大拱＋小岸拱／坡道的有界示意；禁五等拱。
```

建議完整 basis：`M03 documents continued medieval use, not coordinates. OSM way25752465 and bridge outline134399943 control the surviving crossing axis only. Sovrintendenza and Cantatore2012 distinguish the three central large arches and smaller approach arches from the nineteenth-century five-nearly-equal-arch bridge. Medieval end spans, approach slope, dimensions and waterline are schematic estimates; present river geometry is retained as a geographic model control, not a reconstructed1300 bank or flood level.`

3. **鏡頭／living 層**：待上述兩項完成，才將 LM02 target 移到正確橋中段，重新取 ref 並審兩岸連接、人流可站橋面及河內無民宅。現有 prompt 說保留 parapets，但現有原生橋只有0.8m deck，沒有欄杆，需當期橋形一起補；AI不應自行發明一座不同的橋。現有錯圖不可 adopt。

本件只新增本報告與兩份 JSON；未改正式 city/script、模板、共享碼或他人 author，未進行 compile／browser。沒有證據需要修 `engine/props.js` 或 `arches` 方向。

## 可採入候選的低隆 replacement

前一個整座12m拱身從現代水面起算的模型已撤回：它雖可編譯、入口貼地，卻把北／南坡造成44%／33.07%。標E不能使錯誤的石橋縱坡成立。當前 [rome_restart_lm02_bridge_landmark.yaml](rome_restart_lm02_bridge_landmark.yaml) 已整件修訂，不可再採舊34.021m deck版本。

`landmarks[0]` 是完整 replacement：整件替換800 owner原 `rome06_medieval_bridge_aelius`，保留 id、stage、persistence，不可 merge到舊 template／arches字典，不在1300新增第二座橋。位置仍以 `[12.4664631,41.9018919]`、UTM local x −88.021425581°作 G 控制；總長137.5m、寬7m、75m中央、北25m／南37.5m接岸段全部仍是 E，非1300精測外包。

這次先以**低隆、連續的橋面**定展示，再決定水面上可見的拱段。中央橋面24.600m world、中央全平；北／南入口23.063／21.622m world。world值是影片模型高度框架，不是取得新的古代海拔／水位。兩端坡道分別只升1.537／2.978m，原生記錄編碼的實際坡度為 **6.148%（3.518°）／7.9413%（4.540°）**，不是把完整半圓高度全部堆在水面以上。

| 位置 | native plate 的水面／岸高world m | deck world m | deck高於當地表面 |
|---|---:|---:|---:|
| 北入口 `[12.4664148772,41.9024533659]` | 22.873696，岸 | 23.063 | 0.189304m |
| 北中央接縫 `[12.4664341665,41.9022287795]` | 20.654921，河面 | 24.600 | 3.945079m |
| 橋中點 | 19.040672，河面 | 24.600 | 5.559328m |
| 南中央接縫 `[12.4664920331,41.9015550204]` | 19.870812，河面 | 24.600 | 4.729188m |
| 南入口 `[12.4665209659,41.9012181408]` | 21.462792，岸 | 21.622 | 0.159208m |

現代河面本來就由原生terrain plate draped，不是同一絕對水位；這個約19.04–20.65m的數值範圍不能拿來反推1300河床或洪水位。E橋面／坡度以該地理展示背景取得低隆且連續的行走面，不聲稱古橋縱坡等於今日DEM。

### 原生表現與實驗證據

當前8個parts、11個primitives，全部用原生 `prism`／`section_m`／`plan_m`／`site:parts`／`site:cut`／`atop`，沒有城市自訂幾何產生器或共享碼修改。中央是單一75m的prism輪廓，三處**可見圓段缺口**之上為連續橋面；圓段由9m半徑、圓心低於該section datum 5.7m的同一圓決定。上露圓段高3.3m、datum處可見開口約13.9298m，圓冠至橋面1.186m。9m半徑／下沉關係與大小均為 E，不把可見圓段冒稱整個18m淨跨都露在水上。下部拱身、河床和岸側小拱仍省略；由原生foundation讓橋墩下伸，不另造假河水遮房屋。

此處沒有把圓壓扁來降低高度：section是同一圓的一段，完整半圓的其餘部分被目前地表／水面展示界限省略。若直接用 `arches`，18m半圓在最小spring0.15與0.94封頂的規則下仍須h≥11.3924m；再從水面加上整個h，必然重回高橋／巨坡。`z_m`也不允許負值、section負y會被歸零，所以沒有用負值偽裝合法資料。原生自由prism可直接表現所需的上露輪廓，**本件不需要向主線申請新幾何類別**。

`site:parts`讓中央site datum=20.114m world、北／南masonry footing datum=22.063／20.972m world；兩個0.1m的薄砌體footing是坡道的基底。各坡道與兩側護欄都 `atop` 同一footing，避免各自取地形、兩欄高差或接縫浮空。中央護欄 `atop` 中央橋身。兩中央接縫的deck差≤4e−15m；三段護欄接頭都為25.700m world，護欄高1.1m、厚0.4m、欄間淨寬6.2m（全E）。PLINTH=0，section多邊形均有效。

以上是 `landmarks.checked`＋單地標 `citygen.build_city` 對既有 `terrain16.png`／原生plate mesh／地形×2 的量測，沒有film compile／browser。量測JSON的 `replacement_low_deck_validation` 包含從**已編碼native prism頂點**回算的坡道端點／坡度；較舊 `replacement_native_validation` 保留作退回版本收據，不能誤當現版本。

### 補讀原物／照片

已實看 [Sovrintendenza官方照片](https://www.sovraintendenzaroma.it/sites/default/files/pontesantangelo_0.png)：它是現況橋面視角，只支持平順的現況中央行走面，不能用其後世天使、鐵欄或現況橋端替代1300。

亦實看 Istituto Centrale per la Grafica原藏 [Piranesi橫剖 S-CL2396_18767](https://www.calcografica.it/stampe/inventario.php?id=S-CL2396_18767) 和 [側圖 S-CL2396_18768](https://www.calcografica.it/stampe/inventario.php?id=S-CL2396_18768)。橫剖明確區分橋體、河床、基礎；側圖說明作者刻意去掉水，露出平時被水覆蓋的橋墩／基礎，故不能把版畫露出的最底部當實際水線，更不能把整個剖面拱高放到模型水面之上。這些是十八世紀的原始觀察，不是1300實測，僅用來校正「水面不等於橋墩底」及可見上段的表現邏輯；現版所有垂直數字仍明標 E。

整合時 prefix author原先用 `aelius['from']`／`['to']` 算 living target，現在應讀 replacement `[lon,lat]`。候選仍待主線水面避讓修復及prefix重編／近景實看；本支線未改或裁住宅trace，未用自製water mask繞過共享缺陷。新定格必須再確認圓段／橋墩無穿地、三段行走面連續與河上無住宅後才生成living。

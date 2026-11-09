# 537台伯河船磨：來源約束功能示意

用途：新版細綱04e，與既有Janiculum陸上磨坊分開。此件不修改正式city、script、TREATMENT或共享程式。

## A15原文與界線

[Procopius，Wars V.19，H. B. Dewing英譯，1919，Gutenberg20298，印本pp191–193](https://www.gutenberg.org/files/20298/20298-h/20298-h.htm)，本輪重開原頁核對。可定位的短摘合計20英文字：

- “two boats side by side and two feet apart”
- “placing two mills on either boat”
- “set the water-wheels between them”

原文敘述：斷引水道後磨坊失去水力，糧食／飼料短缺也阻止牲畜替代。Belisarius將繩索從河的兩岸繃緊，船並列連於其上，置於所述橋下游急流處；每船置兩磨，轉磨的動力機構在船間。更下游依序繫接更多船，水輪也在船間，各輪由水流獨立推動。本文只畫一組雙船與一個共用動力輪，四磨以磨石符號代表；不主張這是完整輪系設計。譯本註102稱橋為Pons Aurelius，但原文不給船磨座標。

此件**不是發掘位置、實測船型或出土機械復原**。船身只是讓浮體與工作空間可讀的六邊形開敞示意，不能據此稱某種羅馬船。未加帆、桅杆、棚屋、外掛陸上磨坊、精確齒輪列、碎屍或漂木。守軍後續攔截漂流物不屬此模組。井與河仍可供飲水；不把引水道中斷寫成全城無水。S11支持Janiculum停磨；S10／S31是410／412語境，不能作537船磨形制的來源。

## 尺度與原生能力

| 項目 | 採用 | 性質 |
|---|---|---|
| 雙船並列、船間有輪、每船兩磨 | 一模組兩船、四磨石、中央直立輪 | A15文字關係 |
| 船間淨距 | 0.61m | 將英譯two feet以現代英尺換算後取整的製作值；不作古代尺制考證 |
| 每船長／寬 | 12×2.4m | 供四磨與輪可讀的生產估值，無考古船型依據 |
| 輪直徑／寬 | 3.1／0.42m | 生產估值；兩側各留約0.095m示意空隙 |
| 輪心／船舷高 | 1.65／1.10m | 生產估值；輪下緣近水面 |
| 磨石直徑 | 下1.4／上1.3m | 生產估值；代表磨而非復原某件出土磨石 |
| 8輪葉、雙輪圈、支承與可見傳動線 | 開敞機能符號 | 生產估值；連通性可讀，不主張齒輪與傳動設計已知 |
| 河上座標／方位 | YAML所載 | 製作錨點；只沿台伯河，非已發掘實址 |

`pipeline/citygen.py`原生`boats`會在指定線旁隨機散佈±25m，船形固定18×5m並帶棚頂／桅杆，無法保持原文雙船間距。此件改用原生`parts`、`prism.plan_m/holes_m`、`prism.section_m`及`revolve`；未加任何共享類別。49個parts作為**同一landmark**，所以輪、軸、船、磨一同升起，沒有把零件各自當獨立建築。

原生landmark不提供水輪連續旋轉或浮力模擬；交付是靜態功能模型。`section_m`能畫直立開輪，不必用平躺轉體冒充。`rome_restart_boat_mill_section.svg`另標水流→輪→磨的關係；不得把其傳動連線當成原典詳圖。若04e一定要輪葉真的旋轉，須主線另核准原生可動部件能力，不能宣稱此候選已達動畫。

## 檔案與接入

- `research/rome_restart_boat_mill.py`：可重建生成器，只輸出資料。
- `research/rome_restart_boat_mill.yaml`：單件modelview city spec。
- `research/rome_restart_boat_mill_landmark.yaml`：可合併`landmarks`記錄，ID `rome_restart_tiber_boat_mill_537`。
- `research/rome_restart_boat_mill_section.svg`：功能剖示圖，非歷史繪圖。
- `build/review/modelview/rome_restart_boat_mill_537_v1/`：獨立study，入口symlink到`本機候選/rome_restart_boat_mill_537_v1`；research、assets正確連回Rome，build/data為副本。

根代理先審15°及60°定點原生圖，再單次合入候選。上屏應標「537 · 台伯河船磨功能示意／非發掘實址」，保留Janiculum陸上磨坊作停磨的另一個既有物件。傳動線及輪葉數不進旁白作考證事實。

## 最終原生檢查與審圖

最終錨點`[12.4741455,41.8909144]`，方位`-25°`。兩船底板的12個頂點與2個中心共14點，在本城已備`water.png`上的值均為250–255；它們位於台伯河水面遮罩，不是岸上工作室。這是製作定位檢查，不是古河道或船磨實址考證。

- `research/rome_restart_boat_mill_15deg.jpg`：定點az335°、el15°、d0.0032、fov42°；已審，雙船與船間直立開輪可讀。
- `research/rome_restart_boat_mill_60deg.jpg`：同定點／距離，el60°；已審，每船兩磨、共四磨、中央輪與橫軸可讀。
- `research/rome_restart_boat_mill_geocheck.log`：49 pieces，every face points out。
- `research/rome_restart_boat_mill_clipcheck.log/json`：各項0，`clipcheck: ok`，今日浮空亦0。
- `research/rome_restart_boat_mill_verification.json`：間距0.61m、整件12×5.41m足跡、14點水面檢查、兩張圖SHA256及正確research/assets連結。

可重建命令（從專案根目錄執行；modelview採原生兩個machine slots之一）：

```sh
uv run python -I cities/rome/research/rome_restart_boat_mill.py
nice -n 10 uv run python -I tools/modelview.py cities/rome rome_restart_boat_mill_537 --spec cities/rome/research/rome_restart_boat_mill.yaml --year 537 --name rome_restart_boat_mill_537_v1 --at 12.4741455,41.8909144,335,15,0.0032 --at 12.4741455,41.8909144,335,60,0.0032
uv run python -I cities/rome/research/rome_restart_boat_mill_verify.py
```

截圖、原生log、配置與來源註已留在research；`/tmp`study只是可重做副本。未跑全片check，未改正式模型、屋型或共享碼。

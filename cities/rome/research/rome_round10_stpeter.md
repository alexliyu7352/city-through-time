# Round 10：聖彼得正立面

只改獨立庫 `rome_round10_stpeter_templates.yaml` 的立面；R9庫、正式城市及9c不改。從R9的25個子部件延伸，原ID與索引全留，新增ID只加入原 `completion1626`。工期、原址、2°方向、單一 `site: cut`、116×45.5m立面及整體bounds `[-94,-63,126,63]`m保留。主穹頂、肋、兩肩小穹頂、燈籠、十字、堂身未改。

## 來源與估值

- [Vatican R07：立面](https://www.vatican.va/content/vatican/it/ra/facciata-basilica.html)，既有全文 `model_reference/rome07_renaissance/R07_facade.txt`：立面116×45.50m；巨柱高27.48m、直徑2.77m；中央山牆30×7.50m；立面由柱與壁柱分節，下層五個入廊口，上層五陽台及四壁龕。只採這些既有來源，不新增建築史。
- 同向比例參考沿用Martin Möller2002年8月夜正面照片 `assets/round_af_pictures/new_st_peters_2002.jpg`，[Commons](https://commons.wikimedia.org/wiki/File:Basilica_di_San_Pietro_front_(MM).jpg)，[CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/)。八圓柱的非等距位置、端壁柱、開口6.4m寬、上下層各16m、attic窗與balcony的細尺度均為照片約束的量體估值，並非測繪復原。照片只作今日形制比對，不將後世時鐘帶進1626。
- 穹頂與分期沿FACTS S38、S174及R9的Vatican R05／Falda1667／Alfarano1590；本輪沒有改動。

## 實際原生接口

`pipeline/landmarks.py` 的 `parts`、`arches`、`column.stages`、`prism.section_m` 已逐欄閱讀。`long_hall.ground_floor: arcade` 實作是暗色矩形與前柱；不將它當本輪的真開口。

- `facade` 改為兩層五跨 `arches(through: true)`，主牆縮在巨柱後；原中央凸段與兩端凸段用同一開口位置，所有重疊前牆都切出洞。中央上層即Loggia，具有實際拱形邊緣及4m深的退入空間；更後方以 `arches(through: false)` 畫有側壁的內室與暗背，避免原中殿的亮色實牆直接貼住前洞。沒有把黑色貼片貼在整塊前牆上。
- 八根巨柱用四對 `column.stages`，採來源柱高與直徑；柱腳／簡化柱頭分量及柱位按照片估。四個端壁柱用 `prism.section_m`，平面薄而立面寬，柱頭與柱身有層次。柱頭只是科林斯式輪廓的量體，不宣稱葉飾重建。
- 原單一山牆、平檐口與平女兒牆留在原ID；attic低平體與小窗另列，沒有整座神殿屋頂。中央balcony小平台與低欄牆留出上方完整洞口。
- 五上層洞口的形狀規則化、八小attic窗的位置均是片中量體節奏；四壁龕、裝飾小柱、雕塑浮雕與精細欄杆不作完整復原。人物依使用者最後指示省略，沒有方盒假雕像。

目前形制所需能力原生可做；沒有需改共享碼的必要缺口。精細科林斯葉飾、人像等不在本件範圍。

## 採用

`rome_round10_stpeter_patch.yaml`：將 `made_again` 的 `rome07_renaissance_newstpeter` 改用新template，移除實例上的舊inline parts，以免覆蓋template；原有select照留，12個新ID追加 `completion1626`。不能重套R9的append；9c已包含它。

`rome_round10_stpeter_build.py` 是本件資料裝配器，可再產生庫、spec與patch，並以原生欄位檢查確認bounds、相同名義top及舊子ID；非立面部件逐項等同R9。原生study及比對sheet完成後列在交件回報。

## 單體結果

Study：`build/review/modelview/rome_round10_stpeter` → `本機候選/rome_round10_stpeter`，原生2slot、nice／OMP2。最終225 primitives；`geocheck: every face points out of its piece`；`clipcheck: ok`，各項0；`dead air: 0 stretch(es)`。原生幾何地基75.202m，最高208.502m，差133.300m；保持R9實際頂高。

`rome_round10_stpeter_comparison_sheet.jpg` 上排依序為R9、R10、2002原照片；兩版模型共用正面92°、眼高約1m的原生固定機位。此低眼位用原生 `render/still.mjs --q cam=…` 拍，沒有改幾何或共享工具。下排依序為正面d=.065、正面d=.08、原片斜俯視105°／55°／d=.08。正面低眼位大圖是 `rome_round10_stpeter_front.jpg`；七張正面尺度與四方位原圖總覽是 `rome_round10_stpeter_views_sheet.jpg`，已全部實看。

正面d=.065–.08可讀到八巨柱的厚度、中央拱形Loggia暗口、山牆和平頂線。原片105°／55°／d=.08仍看得到長立面拱口節奏，但不適合逐一辨認柱頭；需排片保留適度正面段。這是單體幾何驗證，沒有冒稱全片living、時序、cam/read或brightness已通過。舊單體study的外框光是其study設定，正式candidate由主代理用新引擎最終編譯判斷。

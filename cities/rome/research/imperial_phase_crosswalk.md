# 03站公共構件分期對照

依既有研究與已製作模型整理，未新增史實、未改正式配置或旁白。這是分期資料準備，不是分期已完成或模型已獲導演批准。

## 實際對照

|分類|件數|
|---|---:|
|兩端宣告形體一致；不代表火災中未損|21|
|AD14未選該物件；不等於當時不存在|75|
|兩端宣告不同，需分版本差異與估配差異|11|
|AD14另選、舊107件清冊沒有對應|7|

107件逐項ID、來源、兩端形體fingerprint與原版本註記在`imperial_phase_crosswalk.json`。形體fingerprint只比宣告的幾何／參數，不取代原生模型實比。

## 兩端宣告不同的11項

下列舊年份僅是原模型版本標記，不能當成初建或重建證據。正式分期前須另判斷實證版本變化與估配差異；例如Saepta—Diribitorium的估配接口調整，不能直接演成已證實的歷史拆改。

|113清冊ID|AD14對應ID|舊版本標記|
|---|---|---:|
|circus_maximus|circus_maximus|103|
|jupiter_capitolinus|jupiter_capitolinus|82|
|basilica_aemilia|basilica_aemilia|22|
|atrium_vestae|atrium_vestae_early|81|
|caesar_forum|caesar_forum|113|
|augustus_forum|augustus_forum|-2|
|saepta_iulia|saepta_iulia|81|
|horrea_galbana|horrea_galbana_early|81|
|agrippa_baths|agrippa_baths|81|
|apollo_library_halls|apollo_library_early_single_hall|未標|
|forum_civic_paving_01|forum_civic_paving_01|未標|

## 已確認故事的分期入口

|字幕ID|既定事件／來源|模型工作與尚待證據|
|---|---|---|
|r03_01–05|奧古斯都城市，S04／S30|AD14整城提供早期研究終點；不能把所有14年已成物一起說成前27年落成。|
|r03_06–09|64年大火與止火，S63|另描來源約束的概括region／keep；不以兩端形體差異推斷逐棟受災，也不燒103年的Circus版本。|
|r03_10|火後金宮與谷地人工湖，S05|金宮湖範圍與形制尚需專門來源包；沒有可直接使用的湖岸模型，不拿今日競技場橢圓或海戰湖替代。|
|r03_11–14|湖址退去、80年競技場啟用，S05／S06|先核現有競技場量體哪些適用80年，再做同址lose／stages；未指定精確湖面或時間。|
|r03_15|圖拉真廣場112年、柱113年，S07|兩個有來源的年份分開顯示；既有Basilica Ulpia／廣場廊／市場各核自身版本，不由113標記一概定初建。|
|r03_16|113年城市高峰，已確認終點|逐項對回已確認113整城；AD14／113示意宅地沒有一對一損毀身分，不把整座城沉下重升來代替局部火災。|

## 接著處理的證據與整合問題

1. 64年火勢只給概括方向及止火區域，尚未有逐棟損毀清冊。先核region／keep與公共建築版本，保留未知部分；不從模型差集產生假造損毀表。
2. 金宮湖在競技場谷地；Naumachia在河對岸。兩者的位置、來源與生命週期獨立。海戰湖工具修正不代替金宮湖的形狀研究。
3. AD14另選而113清冊沒有畫的物件，需要另核後期狀態，不能直接安排拆除。清單：diribitorium、porticus_liviae、pantheon_agrippa、naumachia_augusti、domus_augustus_surface_proxy、livia_western_registered、ad14_service_campus_yard_00。
4. 兩端形體不同的構件，按初建／重建／來源假說分別定轉換；相同形體也需獨立判斷64年遭遇。只以native id／group選整件，parts內不添選擇鍵。
5. 住宅的兩套示意布局先保留；後續須設計保持存留城區連續的轉換，再編原生lose／stages。不在此資料表先指定城市數量、精確損毀比例或動作秒數。

產生方式：`uv run --no-sync --offline python -I cities/rome/research/imperial_phase_crosswalk_build.py`。輸入hash隨JSON保存。這一步沒有編譯、渲染或啟動子代理。

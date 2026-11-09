# 09接入資料

本件未寫正式city/script。三個研究觀察節點不是要求新增細綱或旁白；正式owner負責把研究節點／研究秒對到現有a_home_lost及後續站的native city、until、avoid_eras。所有新增量體是來源觀察／復原量體，地圖出版年不是逐棟建造年。

| 層 | 源spec | 接入約束 |
|---|---|---|
|1925拆前整城／本期存留|research/rome09_fascist_whole_base_phased.yaml|含全部保留古蹟及公共體、Alessandrino原城自身lose。1932拆除綁r09_02，1943 SanLorenzo.nave_roof綁r09_06；Spina1936–37另時，不冒1932或1950。|
|1932新大道／清出考古場|research/rome09_fascist_whole_1932.yaml|原城先loss；大道與清空地再出，綁r09_03。只開放遺址地，無整座帝國建築復原。|
|後期來源外延及1930s公共體|research/rome09_fascist_whole_1944.yaml|M03/M04各自配準、逐區native parcels；不重長已清區。1944只是觀察年。四個Foro/PNF量體可見template/cat；非宣稱全域1944新建。|

正式圖層延續不能把後期住宅全部收掉換成下一城；各站用自己的city＋until/avoid_eras。09三層與10/11/12新層同站數必須由正式compile核<=8。前期06/07/08與本件的整城比較有重複存留體，正式owner需按已有存留策略選擇retained/avoid與交界，不能雙重站立或把重複模型說成新造。

後續具址接口：`rome09_fascist_future_losses.yaml`，由09原城失去Cipressi1930s量體表達1950改建（10開頭1953觀察前），1953新Olimpico才能接；這是前後量體替換，不主張1950逐件全毀。PNF舊Nazionale於1957-07-01拆除，11已同意綁olympic_return/r11_01後再讓Flaminio1959起。Marmi/H保留。各native地標用地UTM32633在`rome09_fascist_foro_catalog.json:native_landmark_sites`。

SanLorenzo：Jiang原文記1944重建已開始、1946–1950完整修復；1943無頂狀態不能原樣當1953／1960。10需補真實已修復屋面（復原尺寸仍按同一原生平面／原body支撐），並保留09後殿／券柱。該後期模型不在09的1924–45任務內，也不加旁白。來源及原文檔在whole_basis末節。

住宅/library：四型已批；`rome09_fascist_district_types.yaml`。公共庫共享06/07/08/04＋本件`rome09_fascist_public_templates.yaml`、`rome09_fascist_foro_templates.yaml`。Foro/PNF新增供形制審核，不冒已獲正式全城批准。正式camera/read/range尚待一人合併後再跑；本件收據秒僅研究秒。

PNF接入前檢查：頂層`site: parts`，部件不寫site，U看台預設raised、前端體各找平；來源中心／方向／220×120m及高度全保留。b24556a最後grounds版1944整城已重編，三層geo0／clip0，含tall_foundation／terrain_cut／landmarks_overlap／houses_overlap／cross_era等全0。最小案的舊少樣本收據不替代整城判定；詳whole_review及mainline inbox `20261030-rome09-pnf-parts-tall-foundation.md`。native sites按新版原生重算，四個用地與原catalog對稱差均0m²。

逐片開地接入：`rome09_fascist_ground_review.md`為本次全部31個非零ground外塊的用途／來源表，`rome09_fascist_ground_inventory.json`含完整ground id、1起算分片、中心與模型面積。來源校正只縮／刪ground及其樹域，持續1925園田另扣1944已知建成源域；不改住宅、landmark或loss。重新生成研究spec時，原prepare/finalize之後執行`uv run --no-sync --offline python -I cities/rome/research/rome09_fascist_ground_correct.py`，以免原粗讀重新進入成片。

導演已批Parioli近景，遠景暫不判。保留相機`rome09_fascist_far_camera.json`（研究56s，target[-0.08136,0.0114,-0.05699]、az310/el45/d1.85/fov42）；正式09接入後，要含08仍站立背景的同角度圖才判區間空隙。正式owner依既有until/avoid與存留策略避免重複量體，並核<=8；不把本次研究暗藍間隙直接判成真正未建地，不為空隙補假住宅，也不寫正式city/script。

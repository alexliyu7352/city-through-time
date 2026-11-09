# 06正式接入契約

導演已批准三份模型，並批准`rome06_temporal_change_proposal.md`的視覺合併：800一個觀察狀態；1300／1377共用一座連續城市。正式接入用`people_return`承載原`r06_01`–`06`，`people_return_late`承載原`r06_07`–`10`；全部雙語字句及順序保留。晚期不因1377返回另升住宅、宮翼或大殿，也不編返回年份的拆除。Aracoeli階梯留作備選。

800原有宅區及其院巷持續站立；晚期原生parcels以完整800工作窗、公共建物site及牆帶作reserve，在外側增長。這是來源約束的製作估配，不是逐宅建造年代普查。800開放地圖在晚期都市擴展時由原800自己的`lose.at.node`退出，前院鋪地保留；晚期grounds另扣除保留宅區，住宅院巷仍為暗底。共同牆、橋及公共殼不重升。Lateran十三世紀橫廳與S.Maria Antiqua後續狀況未在本段焦點之外另作構件變化。

06住宅、街路和公共物延續至`modern_growth`的既存城市接替點，這是接入期間的背景存續，並非每棟800示意宅存到1975的證據；07局部Vatican模型不能拿走06主城。已核07契約見`rome07_renaissance_06_contract.md`：舊聖彼得西端與東中殿必須分時退出，前院不在1506全撤，舊宮翼沒有整體拆除證據。主線cf467d0已支援子部件退出，共用06模板具備`rome06_medieval_old_stpeter.nave`、`.transept`、`.apse`，各自程序屋面同退；site:cut小study已驗51件、geo／clip0。本次不以全殿先沉再重升繞過，具體替換仍須原06自身的lose與07新核心／長殿stage對齊。

正式目標仍為`people_return`，旁白`r06_01`至`r06_10`保留。原生`city:`輸入已在`rome06_medieval_whole_800_spec.yaml`、`rome06_medieval_whole_1300_spec.yaml`、`rome06_medieval_whole_1377_spec.yaml`；共用樣板以頂層`landmark_types`追加`research/rome06_medieval_templates.yaml`，保留現有library。`trace`所需GeoJSON都在同一research前綴，已批Regola以獨立domain保留，與grounds無關。

| 旁白錨 | 接入內容／鏡頭要求 |
|---|---|
| `r06_01`–`r06_02` | 已批800：河彎聚落與Aurelian城牆同框，讀出居住核相對牆圈縮小；不能只用整片牆內淺地遠景。正式鏡頭尚未在本輪排入。 |
| `r06_04`–`r06_06` | 同一800城市轉舊StPeter。已驗近景目標`[12.4547,41.9022]`，az115、el15、d0.065、fov42。沒有848–852 Leonine牆、850 Nerva宅或晚期宮翼。 |
| `r06_07` | 1300河岸密建、Borgo及舊StPeter；近景`[12.47305,41.89325]`，az35、el15、d0.035、fov42。Leonine防線／晚期宮翼／1279園地只在晚期輸入。 |
| `r06_08`–`r06_10` | 沿用同一晚期城市；連續鏡頭從河岸經跨河構圖至Borgo、舊StPeter及既有宮翼，1377句落在教宗返回之處。 |

獨立study秒數不作影片時間。正式時間、跨期交疊及運鏡以`rome06_formal_review.md`記錄的實際編譯與逐秒圖為準；800批准模型不改。準備腳本`rome06_formal_prepare.py`只改正式06跨度與追加其樣板庫，保存其他節點結構及全部191組雙語字句的既存摘要，不另複製全城bundle。

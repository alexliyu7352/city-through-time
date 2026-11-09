# 02共和：正式合入與有效結果

**主線072321已批准，root授唯一寫鎖後按ID差量正式合入。** 全片native **1249.69s**；02 **105.23s**（43.05–148.28，原提案合計72s、輸入92s）。較封存12基線1198.12s增加51.57s；02自身增加51.63s，另modern_growth原生重算少0.06s。191組英／簡中原字序與已批camera／geometry完全保留，不加quiet、不再壓100。

正式native PID **2110066已結束**，geo／clip全0；exit1僅原07七等待。正式film與已批候選**逐值及bytes相同**、native inputs相同，77個render data檔逐SHA相同，故沿用有效局部cam／read／亮度，不重跑browser檢查。正式89個來源依賴均為/data canonical research／assets，無/tmp引用；新增必要CREDITS，來源庫清單未改。[完整SHA／結果](rome02_formal_results.json) · [ID差量及來源manifest](rome02_formal_merge_manifest.json) · [正式actual plan](rome02_formal_live_plan.json)。

**改動IDs：** `republic_won_and_lost`替換為7節點，新增`republic_middle_city`、`republic_pompey_observation`、`republic_late_city`、`republic_caesar`、`republic_last_wars`、`republic_civic_dedications`；01 `founding_price`與03 `imperial_height`只改自身city生命周期／去重接口，其它欄位不動。其它19node、global／closing、07 today_from-rest／七等待、09 SL3、11、12–14及prepared均按原值保護。[03逐項差異](rome02_threephase_03_owner_review.md)：176160→174516，9個公共render保留02 owner、29／28建物歸02及avoid交棒，不能稱03全數未變。

**本輪交棒人工已過。** d93aed3修正clipcheck按每件`ring_past`計退場後，僅把Q／W既有住宅loss的at延後、from對齊新front、必要群內sweep調至.5–1s；單屋sink仍1.4s，house／site／geometry／growth stages不動。兩城各13loss是既有來源selector群，不按舊16上限改資料。新舊屋隨波前接續，72／107不再整片先空；自己及root已看22核心、兩單圖／兩組連續格，無新修點。[67–74](../build/review/rome02_threephase_core/handoff_ringpast/early_to_middle.jpg) · [101–108](../build/review/rome02_threephase_core/handoff_ringpast/middle_to_late.jpg) · [44far／Curia／01與03接縫](../build/review/rome02_threephase_core/handoff_ringpast/context.jpg)。原四例現在全退71.585／71.684／106.167／106.164s，距最早新觸及.587／.303／.295／.163s，均早於新body；[原生數值](rome02_threephase_ringpast_actual.json)。

|有效範圍|真結果／限制|
|---|---|
|完整native模型|最後compile新geo／clip全0，含houses_overlap／cross_era；[結果](../build/review/rome02_threephase_core/handoff_ringpast/native_results.json)。Q／W／N／L／03 native primitive hash及全部camera／node時刻同前版。|
|W／L各±1 node|**43.05–122.58**，camdump796samples、cam0、read0；80逐秒圖／5sheets全自看，無新視覺修點。[永久native report](../build/review/rome02_threephase_core/handoff_ringpast/range/report.json)。|
|精確局部亮度|同上述約80s：YAVG **66.81**、最低滑動分鐘 **64.08**，`minute_below_60=false`。只報局部，**不稱全片均值80通過**。|
|02文字／空白|02 deadair0；02 copylint原0之native cues／readouts完全同值。01／03未變範圍沿用已批prefix cam/read0，不重跑整個prefix。|
|07指定等待|完整deadair僅原07七段，compile exit1原因原樣保留；[七段原文](../build/review/rome02_threephase_core/handoff_ringpast/native_deadair.txt)，未加quiet掩蓋。|
|08未判遮擋|先前全片cam僅796.70–797.90s達門檻，遮擋10%；baseline小probe READY timeout，沒有同pose圖，**未判舊問題／可讀**，08camera未改。[原始收據](../build/review/rome02_threephase_core/handoff_ringpast/inherited_full_camcheck_before_local.json)。|
|全片read／亮度|**使用者中止、不算失敗、未重啟、未完成**。[中止收據](rome02_all_gates_user_cancelled.json)。今後全片browser gates必先inbox由主線問使用者，不以區段結果冒充全片過。|

**四相當下note已落/data並自看，未新開browser。** 509／160／44取自本次80格純複製：[509 60.05](../build/review/rome02_threephase_core/handoff_ringpast/notes/early509_60.05.jpg) · [160 78.05](../build/review/rome02_threephase_core/handoff_ringpast/notes/middle160_78.05.jpg) · [44 111.05](../build/review/rome02_threephase_core/handoff_ringpast/notes/whole44_111.05.jpg)。[44之後145.28](../build/review/rome02_threephase_core/handoff_ringpast/notes/after44_145.28.jpg)沿用同態：Q／W off加sink與保留尾已在121.89前結束；後期模型、camera／cues／readouts同值，當時只有N／L兩城地面，未受8→9槽修正影響，[理由收據](../build/review/rome02_threephase_core/handoff_ringpast/notes/receipt.json)。每相只寫當相短詞依據，` · `分隔，原章卡延續。

**11新版地面已另行覆核。** fed3822讓native film寫`groundSlots:9`，11原被8槽漏掉的村草地／場芯補出；11 owner單browser7圖與舊核心對照，root看整村／15°pilotis／北南場地四圖，無地面蓋屋、遮pilotis或新幾何回退。[11完整review](rome11_ground_review/review.md)。02與11瀏覽器順序運作，film全程固定SHA **7a92623f…f5784**。

來源／接口保持已核：509為Cifani晚6c約365ha圍合復原學說，住宅密度／7913whole lot為估配，無160 impluvium倒灌；160 source domus／Curiae／3鄰宅66prims與R21約150m量級示意環；44 frozen整城／55 Pompey／Curia／31樹群3步道，36／34／31事件及29／28公共版本按年。01自己原生分批lose。03 **176160→174516**為9公共render保留02owner、29／28歸02及avoid接口，見[逐項差異](rome02_threephase_03_owner_review.md)，不說03全數未變。[逐件分期](rome02_formal_prepare_phasing.md)／[來源總索引](rome02_republic_whole_evidence_decisions.md)保留。

正式永久小核心：[結果與manifest](../build/review/rome02_formal_core/results.json) · [四phase notes](../build/review/rome02_formal_core/notes/receipt.json)；已批交棒連續格保留原/data核心。正式city／script／film／prepared／actual plan完整SHA記於結果，不以/tmp研究輸出作正式引用。[正式jobs／鎖seal](rome02_formal_jobs_seal.json)記錄最後定格與釋鎖狀態。**07等待、08未判遮擋、全片read／亮度未完成仍待最後全片統收，未因本次正式合入豁免。**

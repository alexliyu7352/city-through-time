# 正式04接入準備

本段僅完成獨立模型及接入資料準備。正式10正在寫city／script，依主代理排程不改兩檔；收到followup後由同一代理接入及驗證。導演已批准04房型、Clivus首區、409骨架與刪兩條廣域earth的地面版，不再請求重審模型。

入口為`another_centre`（271–409），旁白`r04_01`至`r04_08`字句保留。top-level `landmark_types`追加`research/rome04_lateantique_templates.yaml`，保留01、10等現有library。03既有`city.until: another_centre`及03各stage／loss保持。從`rome04_lateantique_whole_271_spec.yaml`取早期本城，使用其types、四條整城／首區trace與pre306 trace；分期只以原生stage／loss替換下表具名部分，普通住宅與長期公共件保持站立，不把十份整城依次沉下升起。

| 觀察 | 相對上一狀態的原生spec差異 |
|---|---|
| 271→275 | `rome04_wall_left_bank`、`rome04_wall_transtiberim`由0.35m施工線改6.5m低牆；保留開放pts、城市在左、curtain、29.6m比較塔距。 |
| 303 | `rome04_curia_iulia`及`rome04_caesar_forum`換303重修／封牆版本。 |
| 306 | 前浴場址76宅退出；`rome04_diocletian_baths`、`rome04_diocletian_natatio`及`rome04_diocletian_garden_floor`升起。需用原生loss `for`指浴場，讓早期宅地不被未來建物預清。 |
| 307後／312 | Hadrian `rome04_venus_roma_hadrian`換`rome04_venus_roma_maxentius`；`rome04_horrea_piperataria_proxy`退出，Nova東西軸版本`rome04_basilica_nova`升起。48個`rome04_castra_barrack_*`及`rome04_lateran_old_cavalry`退出。307非已證實完工年。 |
| 315 | 新`rome04_constantine_arch`。 |
| 350 | 新`rome04_constantine_baths`、`rome04_lateran_constantinian`、`rome04_old_stpeter`與`rome04_vatican_open_approach`；350是保守觀察年，不宣稱同年完工。 |
| 357 | 新`rome04_constantius_obelisk`；原Augustus24m碑繼續站立，第二碑不取代第一碑。 |
| 401–403 | 兩岸牆換12mHonorius版；Nova改晚四世紀北apse／南門版本，與312原案分開。 |
| 409 | 與403的模型相同，為末景觀察，不增新建物。 |

每個版本的完整原生值已存`rome04_lateantique_whole_<year>_spec.yaml`，以該檔取值；替換時給前後版本不同id，原生`select`點名、`lose`清前址，勿用list index。前浴場宅地trace已單獨存檔，首區核可parcels不可重跑早期準備腳本覆掉。grounds僅最終八塊及其實際出現時點，禁加`rome04_open_working_ground`／`rome04_domestic_open_ground`。未修改的模板／首區不再重複freeze。

正式排鏡仍須完成：開場低牆成形配`r04_01`，早四世紀新增按來源先後，對岸舊聖彼得配`r04_02`；年線在相應字幕／stage間單調推進，避免線性271–409讓教堂出現在錯年。`r04_03`以後宮廷功能光收斂，白色宮城、街道和紀念建築仍在；`r04_04`拉文納敘事時已近402，不演全城拆除或中世紀收縮。至少一段15°住宅近景、舊聖彼得可讀側景及整城全景；不把獨立審查取景之間的305→140→310插值當正式運鏡。

接入後先compile讀所有警告、geo／clip0，核對03、04、05節點起訖；只對受影響站及前後站跑原生rangecheck，逐張實看。04含局部替換須按MODEL最少必要實際時刻跑兩look，讓被取代的版本亦可見。獨立study的8–9s全通過不代替正式range；正式全站亮度、文字、camera與時序仍待本步。旁白／配音／音樂／render不改，05／06後續城市接入由其代理負責。

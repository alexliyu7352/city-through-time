# 新聖彼得博物館頁：來源與模型界線

## 展示的建築與詳細模型

`museum/new_st_peters.yaml` 的 `made_again` 頁取 `rome07_renaissance_newstpeter`，實例模板為 `rome_round10_stpeter_open_drum`。頁面用 `tools/blender/domed_church.py` 的詳細外觀，在原址、原方向與 `exaggeration: 1` 下展示1626完成建築；不抽取另一個1656–1667柱廊地標。電影、城市與施工接口未改。

本輪逐段核讀 `DEFAULT`、`from_landmark`、`spec_of`、堂身／後殿、鼓座／穹頂／燈亭、小穹頂與立面的建造函式，並實看提供的 `five_pages.jpg` 模型比較圖。37子件／225 primitives及133.450m外包是前一輪電影生成器的結果，不能拿來當詳細模型檢查結果；正式細模物件分配和外包由museum build確認。

- **原地標傳入、已有來源尺寸**：立面116×45.50m（不含頂像）、巨柱27.48m高／2.77m徑、中央山牆30×7.50m；頂球2.50m徑、十字3.33m高／橫臂2.40m；名義總高沿Vatican RA133.30m分支。這些主要尺寸有據，不表示每條輪廓與節點都已測繪。Fabbrica另頁136.57m的基準差沿既有研究保留未解，不平均。
- **原地標仍屬估配的尺度**：堂身42m高、側廊26m高、各房體平面、側翼、後殿、18°屋面、鼓座50m外徑／20m高、主殼46.5m徑／35m升高、16肋及其1.4m寬／0.7m凸出、柱位、燈亭比例、兩個20m小穹頂，均沿既有圖像約束的量體估值。58.90m官方外徑不冒稱為46.5m裸殼徑的直接來源。
- **堂身與後殿的新增細部**：`order`估計9m壁柱跨、2.6m寬／0.5m凸出的巨壁柱、牆腳、柱頭、分層檐線、頂層壁柱帶及三種窗區；窗框與三角／弧形山花、高側窗和屋面斷面都已建。其剖面、位置、比例與密度是依現存外觀的預設，未逐件核為1626形制，不能因更細緻便改成sourced。
- **鼓座與穹頂的新增細部**：成對柱前後有扶壁、柱基、上下基座分層；鼓座窗有交替山花、檐部有逐層凸出及板框。`drum_detail`的2.6m柱基、3.4×2.4m扶壁、窗寬／窗高、2.5m頂層，以及檐口剖面均估值。主殼上三層老虎窗分別以7／17／25m相對高度與2.6／2／1.4m寬生成，窗體、山花和排列的細尺寸是預設；三層的存在有V3明文。燈亭窗、扶壁、柱頭、檐口和頂部小殼比例也估配。
- **鼓座內徑的界線**：`from_landmark`會讀取原地標41.50m內口參數，但本細模的 `crossing` 只建鼓座外觀，`r_in_m`未用來造內壁。頁面已改為說明41.50m是官方穹頂內徑，不再聲稱細模展示這一鼓座內口或有實測壁厚；內部雙殼與登頂通道均未建。
- **立面的新增細部**：八圓柱與端壁柱有分段柱腳、收分柱身、示意科林斯柱頭及卷渦；不是逐葉雕刻。`front_detail`建五個平頂入口、拱頂上層開口、中央祝福陽台、壁龕凹部、端通道、窗框／山花、頂層窗，以及陽台和頂層瓶形欄杆。洞深、位置、欄杆間距、線腳及小構件比例都是預設估值。雕像、浮雕、紋章、銘文與後世時鐘未建；不能再寫「只有薄凸段」「欄杆未復原」或「沒有壁龕」。
- **小穹頂與頂飾**：小穹頂基座有壁柱和窗框，鼓座有窗，主殼有肋，燈亭有窗；其細尺寸沒有逐件1626測繪。頂球下頸部、十字厚度、端部小塊與連接是估值，`cross_bar`合入詳細物件`cross`。來源支持的球徑／十字高，不替這些細部背書。

分件維持first-match：`facade`先取主牆、中央山牆及巨柱，`facade_detail`取其餘`facade_*`；`drum`取鼓座／柱／檐部，`dome`取主殼／燈亭／燈亭柱，`finial`取球與十字，`small_domes`取兩側小穹頂，`main`取堂身／側翼／後殿／下部基座。七組全部estimated：`facade`同一物件含估配柱頭、線腳等；`finial`的十字同一物件含估配杆厚及端部小塊，無法由既有labels把有據尺寸與估細部分開。note仍保留主要尺寸的來源，不以整件有據色調替細部背書。

## 來源與實際閱讀

- [Pietro Zander／Fabbrica, The Basilica](https://www.basilicasanpietro.va/en/san-pietro/the-basilica)：本輪重開，核1506首石、彼得墓共同中心及Maderno完成立面。其1608–1612與Vatican RA1607–1614分口徑保留。
- [Fabbrica施工日期FAQ](https://www.basilicasanpietro.va/it/faq/quando-e-stata-costruita-la-basilica-di-san-pietro)：本輪重開，核1506至1626完成並替代4世紀舊殿。
- [Vatican RA, Cupolone e Lanterna](https://www.vatican.va/content/vatican/it/ra/cupolone-lanterna.html)：本輪重開，並讀本機 `model_reference/rome07_renaissance/R05_dome.txt`。核1564停於鼓座、1590主殼、1593球與十字，以及外高／內外徑、球與十字尺寸、鉛覆面、雙殼、三層帶山花老虎窗、燈亭成對柱。本文沒有給每扇窗及每道檐口的尺寸。
- [Vatican RA, Facciata Basilica](https://www.vatican.va/content/vatican/it/ra/facciata-basilica.html)：本輪重開，並讀本機 `R07_facade.txt`。核立面／頂像年代、主要尺寸、五下層入口、五上層陽台與四小壁龕。頁面亦描述現存裝飾及1667後變動，不能將整段視為1626清單；模型也不完整復原其雕刻。現代圖像只供形式估配。
- [Vatican RA, Colonnato](https://www.vatican.va/content/vatican/it/ra/colonnato-statue-santi.html)：本輪重開，核1656委託、1657起工、1667結束，排除於1626場景。
- [Senato, San Pietro in Vaticano](https://antiquorum-habet.senato.it/index.php/section/section_61_it/)：本輪重開展覽正文，核1590疊圖和舊中殿續用到1609；只透過其說明認識Alfarano，**未讀手稿全本**。該圖不是1626完整竣工圖。
- [Vatican State, Storia](https://www.vaticanstate.va/it/stato-e-governo/storia.html)：本輪重開，核中世紀宮群、Sistine及Belvedere先於1626。西園地與東Borgo的定性環境另沿既有 `rome07_renaissance_survey.md`、FACTS S207，不冒稱每條園路與每個宮翼均有測繪。
- [Falda1667，Emory/Pitts](https://digital.pitts.emory.edu/s/digital-collections/item/6418)：沿既有原圖及R9／R10研究對堂身、小穹頂、宮園和Borgo的圖像約束，**本輪未重看完整原圖**。它晚於1626，且可能含方案，不把全部廣場或住宅布局提前。亦未核讀Grimaldi、Krautheimer等原書，不虛列為細模測繪依據。

## 相機與三張場景卡

沿用已批准 `at_m: [17.29, -0.3, 40]`，az90／210／330、el25、fov36、距離均480m。既有原生成器的角點計算與手機構圖經驗只是機位來由，不代替細模的ref、sheet和desktop／phone檢查。

三卡定1626完成狀態，保留新增壁柱、窗框／山花、扶壁、三層老虎窗、壁龕與欄杆，不將其重新抹成粗略量體，也不讓生成圖把估值變成新的假精測。東面機位朝西丘，北側宮群仍在北，Borgo仍在東；西南／西北機位可在遠東方向帶出低資訊屋頂。前地為通行與禮儀空間，沒有後世橢圓柱廊或和解大道；未抽取的方尖碑／噴泉不搬入原本不可見的位置。

本筆記的查證工作只處理文字與場景卡。後續已由原生流程完成詳細模型建置、三張新圖的ref／gen／sheet／adopt、livingcheck及桌面／手機shots；配準、物件分配與手機構圖均已實看。

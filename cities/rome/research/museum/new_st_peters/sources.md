# 新聖彼得博物館頁：來源與模型界線

## 選用的原生模型

`museum/new_st_peters.yaml` → canonical `city.yaml` 的 `made_again` → `kind: parts / id: rome07_renaissance_newstpeter`，實例使用 `rome_round10_stpeter_open_drum`。保留全部37子件、225 primitives、既有1626完成形制；不改原模型、施工接口或city。博物館只抽此地標，不抽取另一個1656–1667柱廊地標。

輕量直接原生 `citygen.build_city` 的真高度檢查：`exaggeration:1`、地坪0，記錄最低−3m為埋地裙基，最高133.450m。既有R9／R10研究名義頂高133.300m，與此原生生成相差0.150m；如實保留，不偷偷補償或改原模型。官方RA133.30m與Fabbrica另頁136.57m是未解基準差，頁面明列沿用前一分支，不平均。

## 原生museum工具缺口

確切原生子件`drum`、`drum_cornice`、`ball`是`kind: revolve`，原實例未明填`sweep_deg`（`drum`欄位kind,id,atop,sides,profile_m；`drum_cornice`欄位kind,id,atop,profile_m；`ball`欄位kind,atop,sides,profile_m,id,z_m）。museum必須像compile一樣，先透過`landmarks.checked`完成正式預設，再呼叫`citygen.landmark_site`；否則`landmarks.bounds`直接讀`sweep_deg`會失敗。現行主線museum已完成這項初始化，原生`find_landmark/build_model/assign`已驗225筆全分配。writer未改canonical／shared，也未假填default繞過；此處沒有待補的歷史模型。

## 來源與實際閱讀

- [Pietro Zander／Fabbrica, The Basilica](https://www.basilicasanpietro.va/en/san-pietro/the-basilica)：本輪重開正文。1506首石、彼得墓同址中心、Maderno及後來Bernini；正文立面主施工1608–1612，與Vatican RA1607–1614分口徑保留。
- [Fabbrica施工日期FAQ](https://www.basilicasanpietro.va/it/faq/quando-e-stata-costruita-la-basilica-di-san-pietro)：本輪重開，1506至1626完成，替代4世紀舊殿。
- [Vatican RA, Cupolone e Lanterna](https://www.vatican.va/content/vatican/it/ra/cupolone-lanterna.html)：本輪重開，並核既有R05全文。1564至鼓座、1588–1590殼、1593球與十字；133.30m街面至十字頂、58.90m外徑、41.50m內徑、球2.50m／十字高3.33m；鉛覆面、雙殼、燈亭呼應成對柱。58.90m不得當裸殼徑；50m鼓座／35m殼升高／20m分層等均為原模型的量體估值。41.50m鼓座內口為已標示比較，不主張有4.25m實測壁厚。
- [Vatican RA, Facciata Basilica](https://www.vatican.va/content/vatican/it/ra/facciata-basilica.html)：本輪重開並核既有R07全文。1607–1614立面、1612–1614頂像；116×45.50m（不含像）、柱27.48m／直徑2.77m、山牆30×7.50m；五下層入口／五上層陽台／四壁龕。模型的柱位、分層、開口規則化、檐口／欄牆厚度等仍估值。現代照片只用於既有R10形制比對，不拿其後世時鐘與完整雕飾當1626紀實；本頁不附現代照片。
- [Vatican RA, Colonnato](https://www.vatican.va/content/vatican/it/ra/colonnato-statue-santi.html)：本輪重開，1656委託、1657起工、1667結束；1626場景與模型都排除。也不能把其頂像1662–1703全數當1667一次完成。
- [Senato, San Pietro in Vaticano](https://antiquorum-habet.senato.it/index.php/section/section_61_it/)：本輪重開正文；Alfarano／Bonifacio1590疊圖、舊殿餘部至1609、方尖碑1586移置、1623起的Baldacchino至1633等各自分期。**未讀Alfarano手稿全本**，1590圖不是1626完成圖。本輪沒有核讀Grimaldi原稿或Krautheimer全本；其轉引路徑詳舊殿頁sources，不虛列為新殿測繪來源。
- [Vatican State, Storia](https://www.vaticanstate.va/it/stato-e-governo/storia.html)：本輪重開宮史，中世紀宮群、Sistine、Belvedere先於1626存在。西側園地與Borgo的定性環境沿既有 `rome07_renaissance_survey.md`、FACTS S207，不冒稱全部宮翼、每條園路已測繪。
- [Falda1667，Emory/Pitts](https://digital.pitts.emory.edu/s/digital-collections/item/6418)：沿用已有原圖及 `rome07_renaissance_survey.md`／R9／R10研究對堂身、側小穹頂、宮園和Borgo的圖像約束；本輪沒有重新實看完整60MB原圖。它晚於1626，而且可能畫方案，不把其柱廊、廣場或每戶布局提前。量體估值不升格為有尺考古復原。

## 分件與相機

225 records的37個label均由頁面7個parts first-match接住：`facade`34筆先收主立面、中央山牆和四段巨柱；`facade_detail`26筆收其餘`facade_*`；`drum`34筆收鼓座／兩組成對柱／檐口；`dome`35筆收主殼／燈亭與其柱；`finial`3筆收ball/cross/cross_bar；`small_domes`10筆收兩肩小穹頂；`main`83筆收western_body/cross_arm/western_apse/attic/long_nave。維持`main`固定ID以供原生phone shots開note。sourced的立面／頂球十字仍在note區分有據尺寸和估配細節，其餘整組estimated。

真records保守旋轉框（x,y,z，m）`[-94.620,129.198] / [-3,133.450] / [-63.754,64.354]`。取`at_m:[17.29,-0.3,40]`（east,north,up；原生engine把target高度限制40m），az90/210/330、el25、fov36。以與舊頁相同的角點透視公式、16:9參考幅計得必要距離348.749/347.688/347.688m，最初按16:9參考幅選400m，但桌面和手機的展館舞台較窄，原生shots實看時立面下緣被控制列擋住。三view改用480m，重新拍ref並配準生成；不是從城市片中誇張高度照搬鏡距。三方向球面夾角大於100°。最後desktop／phone構圖由root實看。

場景定1626完成外觀。東面機位看向西丘／北側宮群，Borgo在觀者東側，不能把它搬到西後殿背後；西南／西北機位可在遠東方向帶出Borgo低資訊屋頂。廣場是通行與禮儀前地，不是湖、荒野或現代廣闊大道。1586方尖碑／17世紀前期噴泉等未抽入此單體，卡片不胡亂擺一套對稱廣場設施；在畫外時不強行搬入構圖。

writer未跑GPU、生成圖片或正式museum build；只驗原生模型與parts分配。root接手真高度白模檢視和living ref/gen/sheet/adopt；既有電影幾何的辨識度不等於本頁構圖已通過。

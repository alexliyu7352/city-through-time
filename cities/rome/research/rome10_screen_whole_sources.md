# 1953 Cinecittà全廠：逐號清冊與估值

本件承接已批准三棚樣區，擴至1953總圖所示完整功能廠區，含主入口、棚群、製片／管理、剪輯／洗印、工場／材料庫、攝影池、植物供景與西側職工球場；不是1950年代全羅馬，也不是1953新建年表。

## 來源及圖例

- **R53**：*Bianco e Nero*1953年第7期，[CSC原PDF](https://fondazionecsc.b-cdn.net/wp-content/uploads/2019/11/BN_1953_07.pdf)，PDF128廠照及1–71圖例、129全廠平面。既存`model_reference/rome10_screen_quarter/BN_1953_07.pdf`及`bn53_read-128.png`／`bn53_read-129.png`，原頁全看。1–16均為Teatri di posa，17另列化妝／劇場配套。圖是機構同期總平面，沒有逐室上高或逐年可出租普查；圖例與圖上標號不能與1937或今日編號直接相等。
- **R37**：Peressutti1937〈Cinecittà〉，*Cinema*20印刷302–306，[CSC原PDF](https://fondazionecsc.b-cdn.net/wp-content/uploads/2020/04/CN_1937_20.pdf)。只取已核15×30×10.5、20×40×12、中央36×80×16m棚、兩層配套、4m服務室及瀝青道路／調度地作同期形制比較。1953所有新棚長寬依R53，不把1937三尺寸複製成全廠；屋面25°與檐高分支沿已批。鋼桁架不復原，不畫成實心塔或假屋架。
- **R54**：1954年第7期PDF91，[CSC原PDF](https://www.fondazionecsc.it/wp-content/uploads/2019/11/BN_1954_07.pdf)，1947起復建及1950年底十二棚修復是年代橋接，不將十二棚修復統計強套成1953圖上1–16的同時營業清冊。
- **RLOC**：原已核`rome10_screen_quarter_registration.json`五控制點與native Source，.5882m/px，殘差.98–3.41m、入口留一20.98m、絕對工作不確定約15m。沒有重配；局部圖讀約1–3m，離中央控制較遠仍有未量化圖紙變形／外推風險，不將小擬合殘差當全廠測地精度。

## 採用原則與界線

保留樣區25個trace項：六個地標實例、十九通路；90件原生primitives除rise rank外逐值實比。新棚採原生long_hall外包殼，逐棟尺寸各讀；窗、門與鋼架未核，不冒稱新棚內外細節完成。平頂低配套以原生prism沿來源折線，4m與8m分別比1937服務室／兩層配套；21、64、65的6m沿已批工業估配；不是測得立面。42兩翼分開描出，中央入口有真通口，沒有把通口填實；廠照低平頂支持外形，窗位未重建。51只畫低溫室外殼，未復原玻璃和骨架。

54是唯一明標攝影池，依原圖矩形而非園庭誤判；使用原生pool，不指定無據banks_m或把顯示落差當古池深。今日DEM／地形×2／歷史量體×2為顯示條件；來源固定而今日地形不合時才按MODEL改draped並明記。53水塔上部不可讀，沒有實心替身或假基座；50／56／57／67在現圖無法可靠對位，清冊保留未復原，不挪附近無號屋硬對。

園林只沿1953植物符號區畫15個native trees region；6m高、2.6m冠、12–17m間距與逐樹位置皆估配。19開放內院保hole。地表依`rome10_open_ground_evidence_sources.md`的8區／22片接原生grounds：soil對應earth，露天工作地、66院、51園藝土及無號空框合一entry；其餘園地及70主場grass在後覆蓋，共2 ground＋1池＝3／32槽。只按既有功能outline裁候選，不扣landmark_site＋6m，不改建物、通路或樹；19真內院亦有grass。這些土／草材質是具名用途下的估值，不是1953逐塊鋪面測繪；後條目原生扣前條目，工作窗接縫不畫歷史地界。70依原圖保橢圓跑道、主球場界、中線及兩端門區，線材／寬度示意，不加看台。沒有Via Veneto／Ben-Hur後來著名搭景、1959活動新造、現代擴區、1937預留未建計畫倒放。

道路循R53白色通路／裝卸地連成網，瀝青依R37同類用途；路寬、實際門面接合及細支路屬有界估配，非逐路緣測量。北／西未完整畫出法定界線，因此outline只作全廠功能覆蓋窗口，西北缺線以來源可見範圍銜接，沒有造廠牆。hide只是藏當代底模的研究遮罩，不是1953拆遷。來源影像僅研究，未上屏或作材質。

## 逐號清冊

下列每項的完整像素折線、native template差異和basis在`rome10_screen_whole_catalog.json`／單一`rome10_screen_whole_trace.geojson`。同號多件按來源分開；17的四個未標號配套條明列功能比較，不當獨立已證17室。平面尺寸為native Source圖讀約值，上高均比較估值。

| 原圖號／用途 | 採用／估值／排除理由 |
|---|---|
| 1 Teatro1 | 1：圖讀17.1×32.4m，檐高估10.5m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 2 Teatro2 | 2：圖讀21.2×45.3m，檐高估12m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 3 Teatro3 | 3：圖讀18.8×23.5m，檐高估10.5m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 4 Teatro4 | 4：圖讀14.7×32.4m，檐高估10.5m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 5 Teatro5 | approved central unit retained verbatim |
| 6 Teatro6 | 6：圖讀30.0×31.2m，檐高估12m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 7 Teatro7 | 7：圖讀15.9×28.2m，檐高估10.5m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 8 Teatro8 | 8：圖讀15.3×32.9m，檐高估10.5m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 9 Teatro9 | 9：圖讀25.9×31.2m，檐高估12m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 10 Teatro10 | 10：圖讀26.5×72.3m，檐高估12m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 11 Teatro11 | 11：圖讀20.6×32.9m，檐高估10.5m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 12 Teatro12 | 12：圖讀16.5×54.1m，檐高估12m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 13 Teatro13 | 13：圖讀24.1×34.7m，檐高估12m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 14 Teatro14 | 14：圖讀22.4×34.7m，檐高估12m；1953 legend1-16=Teatri di posa;plan dimensions graphically read, height/roof compare1937 named stage sizes;not a1937 size imposed on this footprint. |
| 15 Teatro15 | approved stage15 retained verbatim |
| 16 Teatro16 | approved stage16 retained verbatim |
| 17 Camerini e attrezzature teatro | 17_west_south：來源折線外框，高度估8m；Unnumbered stage-pair support bar;functional comparison with17 and1937 two-storey support. Its exact1953 room allocation is unproved.<br>17_west_middle：來源折線外框，高度估8m；Unnumbered stage-pair support bar;functional comparison with17 and1937 two-storey support. Its exact1953 room allocation is unproved.<br>17_east_south：來源折線外框，高度估8m；Unnumbered stage-pair support bar;functional comparison with17 and1937 two-storey support. Its exact1953 room allocation is unproved.<br>17_east_middle：來源折線外框，高度估8m；Unnumbered stage-pair support bar;functional comparison with17 and1937 two-storey support. Its exact1953 room allocation is unproved.<br>17：來源折線外框，高度估4m；labelled support block |
| 18 Presidenza e Direzione Generale | 18：來源折線外框，高度估8m；management two-storey estimate;not a new1953 building |
| 19 Galleria masse | 19：來源折線外框，高度估8m；group-performer facility;interior court cut by source outline below |
| 20 Ristorante seconda categoria | 20：來源折線外框，高度估4m；restaurant low external volume |
| 21 Centrale elettrica | approved electric building retained verbatim |
| 22 Impianto aerazione quinto teatro | approved ventilation retained verbatim |
| 23 Centralina elettrica | 23：來源折線外框，高度估4m；electrical room between stages4/3 |
| 24 Sale di proiezione | 24：來源折線外框，高度估8m；projection support;two-storey external estimate |
| 25 Tecnofonico | 25：來源折線外框，高度估8m；technical sound facility;two-storey comparison |
| 26 Servizio ottico meccanico | 26：來源折線外框，高度估4m；optical/mechanical service folded plan |
| 27 Cinefonico | 27：來源折線外框，高度估4m；Cinefonico;separate from neighbouring29 and30 |
| 28 Falegnameria | 28：來源折線外框，高度估6m；carpentry workshop;6m industrial working height compares approved21 |
| 29 Fuori opera | 29：來源折線外框，高度估4m；Fuori opera outer footprint;shared block boundary before27 resolved within1-3m graphic uncertainty |
| 30 Scenografia | 30：來源折線外框，高度估4m；scenery workshop;shared block boundary stays west of27 within source graphic uncertainty |
| 31 Magazzino materiali | 31：來源折線外框，高度估4m；material store along Via di Torre Spaccata |
| 32 Garage | 32：來源折線外框，高度估4m；garage long boundary strip |
| 33 Mensa maestranze | 33：來源折線外框，高度估4m；workers canteen boundary strip |
| 34 Fabbri | 34：來源折線外框，高度估4m；smiths workshop |
| 35 Idraulici | 35：來源折線外框，高度估4m；plumbers workshop |
| 36 Spogliatoi | 36：來源折線外框，高度估4m；changing rooms |
| 37 Servizio personale ufficio movimento | 37：來源折線外框，高度估4m；personnel/movement service |
| 38 Spogliatoi maestranze | 38：來源折線外框，高度估4m；workers changing rooms |
| 39 Pronto soccorso | 39：來源折線外框，高度估4m；first aid |
| 40 Magazzini | 40：來源折線外框，高度估4m；boundary store |
| 41 Ristoranti prima categoria | 41_east：來源折線外框，高度估4m；first-category restaurant<br>41_west：來源折線外框，高度估4m；second numbered restaurant volume |
| 42 Uffici produttori | 42_west：來源折線外框，高度估4m；source wing with real central entrance gap;not window-complete<br>42_east：來源折線外框，高度估4m；source wing with real central entrance gap;1953 photo low flat roof |
| 43 Sale di proiezioni | 43：來源折線外框，高度估4m；projection rooms |
| 44 Sale montaggio | 44：來源折線外框，高度估8m；editing facility;two-storey comparison only |
| 45 Taglio negativi | 45：來源折線外框，高度估4m；negative cutting |
| 46 Celle films | 46：來源折線外框，高度估4m；film cells |
| 47 Magazzini mobili | 47_north：來源折線外框，高度估4m；mobile stores<br>47_south：來源折線外框，高度估4m；same source group second bar |
| 48 Centrale termica | 48：來源折線外框，高度估4m；thermal plant |
| 49 Deposito montaggio | 49：來源折線外框，高度估4m；editing store |
| 50 Pompa sollevamento acqua | number50 pump not securely located in the1953 graphic;no invented footprint |
| 51 Serra | 51：來源折線外框，高度估4m；greenhouse roof envelope only;no glass or unsupported frame reconstruction |
| 52 Deposito infiammabili | 52：來源折線外框，高度估4m；inflammable store |
| 53 Torre serbatoio | water tower symbol located near[1161,1050];upper form not readable;no fake solid tower or unproved pedestal |
| 54 Piscina | 54：原圖池外框；原生pool；Only54 is the labelled filming pool;native dug basin unless actual terrain requires draped mode,no invented banks_m. |
| 55 Deposito materiale lavorativo | 55：來源折線外框，高度估4m；working-material store |
| 56 Deposito materiale miniature | number56 miniature-store label not securely resolved;no invented footprint |
| 57 Parcheggio biciclette | number57 bicycle parking not securely resolved;not converted to a roofed store |
| 58 Deposito infissi | 58：來源折線外框，高度估4m；doors/windows store |
| 59 Magazzino | 59：來源折線外框，高度估4m；store |
| 60 Parco lampade numero2 | approved lamp store retained verbatim |
| 61 Spogliatoi comparse | 61：來源折線外框，高度估4m；extras changing rooms |
| 62 Centrale elettrica per esterni | 62：來源折線外框，高度估4m；electrical source for exterior work |
| 63 Deposito pirotecnici | 63：來源折線外框，高度估4m；pyrotechnics store symbol limits external footprint precision |
| 64 Centrale termoelettrica | 64：來源折線外框，高度估6m；thermoelectric plant;low external envelope,no fake equipment |
| 65 Plastica scultura | 65：來源折線外框，高度估6m；sculpture workshop;industrial height estimate |
| 66 Recupero | 66_west：來源折線外框，高度估4m；recovery yard enclosing west strip,not a solid filled yard<br>66_east：來源折線外框，高度估4m；recovery yard enclosing east strip |
| 67 Centrale per esterni | number67 exterior-power label not securely resolved;no invented footprint |
| 68 Depurazione idrica | 68：來源折線外框，高度估4m；water-treatment low building;reservoir garden kept open |
| 69 Edificio dopolavoro | 69：來源折線外框，高度估4m；workers recreation building |
| 70 Campo di football | source obround track,pitch boundary,halfway line and goal areas traced as native thin paths;no stands.Grass/paint/soil not measured |
| 71 Spogliatoi | 71：來源折線外框，高度估4m；football changing rooms;source southern occupied outline,not the unfilled rectangles farther north |

研究片秒數以最終review為準；年線插值不等於建造年；正式10尚未合併。

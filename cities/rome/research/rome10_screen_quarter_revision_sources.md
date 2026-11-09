# 1953中央生產群：編號、形制與估值

本輪擴成5、15、16三棚及配套／道路的連續生產群；中央5的既批16件body、12個parts設定、位置與方向保留。新freeze為`build/review/modelview/rome10_screen_quarter_central_approved_frozen/`，freeze及check均exit0。原62×120m是上一輪研究裁窗，不再限制本輪。新窗口沿1953路廊切成帶缺角區域，排除北邊13／58及西南4／3等下一街廓；不是廠界、地籍或完整1950年代羅馬。

## 原始來源

來源沿上輪Q01–Q06，原PDF與雜湊不重抓、不以今日改裝補空缺。

- **R01** Peressutti1937，《Cinema》20，印刷303總圖、304棚尺寸與服務樓、305剖視。[CSC原PDF](https://fondazionecsc.b-cdn.net/wp-content/uploads/2020/04/CN_1937_20.pdf)。既存`model_reference/rome10_screen/`及`rome10_screen_refine/cn37_p25_250dpi.png`。三個直接尺寸為15×30×10.5、20×40×12、中央36×80×16m；前配套兩層、鋼屋架、覆頂隔廊等是同時期比較。不能把前兩種尺寸硬指定給1953新編15／16。
- **R53** 《Bianco e Nero》1953年第7期，PDF128圖例／廠照、129總平面，[CSC原PDF](https://fondazionecsc.b-cdn.net/wp-content/uploads/2019/11/BN_1953_07.pdf)。本地`model_reference/rome10_screen_quarter/bn53_read-128.png`與`bn53_read-129.png`。本輪重新實看圖例與帶座標裁圖。**1–16均列Teatri di posa；17才列Camerini e attr.-Teatro。**因此16照原圖作狹長攝影棚，不能把它當已證的服務樓。中央5與1937圖24對照沿前輪。
- **R54** 1954年第7期PDF91，[CSC原PDF](https://www.fondazionecsc.it/wp-content/uploads/2019/11/BN_1954_07.pdf)。只作復建既有棚及配套的年代橋接；不將十二棚統計變成1953圖上各號同步可租的普查。
- **RLOC** 上輪已核的今日OSM中央棚四角／入口和後期官方物業圖，只作存留定位。native1953配準.5882m/px、殘差.98–3.41m、入口留一20.98m，完整控制沿`rome10_screen_quarter_registration.json`；小擬合殘差不等於古地籍精度。新圖讀外框通常仍有約1–3m局部估讀和更大的絕對定位不確定。

## 同期編號到模型

| 原圖／模型 | 平面與採用尺寸 | 上部、開口、年代限制 |
|---|---|---|
| **R5：中央5**；`rome10_screen_quarter_central_unit` | 36×80m及36×9前服務樓、3m隔廊全部保留批准件。點坐標原樣保留，未再重配。 | 16m作檐高、25°屋坡、所有門窗／厚度估值沿批准資料，不改八門分配，不補鋼桁架。 |
| **R15：棚15及北配套條**；`rome10_screen_quarter_stage15` | 1953棚身像素約[907,1263]–[958,1368]，native量級30.0×61.8m，採30×62。北條形樓約30×9m，隔廊約4.5m；反向朝北連到上橫路。 | 棚檐12m比較R01中棚20×40×12，不稱本棚實測；北條形樓以R01同類兩層配套比較採2×4m。條形樓未獨立標號／用途，不能命名為已證的17號化妝樓。主棚六門、位置／尺寸、七開間兩排窗、25°屋面及薄牆均估配。 |
| **R16：棚16**；`rome10_screen_quarter_stage16` | 圖例明指攝影棚；像素[966,1240]–[984,1368]量級10.6×75.3m，採約10×75，取圖讀不確定內的整米工作值。 | 檐10.5m比較R01小棚15×30×10.5，不把長寬也套成小棚。雙坡25°、前後各一門／長側各兩門均估值；東側門放在22前後開放處，沒有開向22實體。沒有宣稱何年由服務廊改作棚。 |
| **R21：Centrale elettrica**；`rome10_screen_quarter_power21` | 1953折線外框直接用native`outline_landmark`，約38×34m量級，保留收腰／凸翼平面。 | 6m高取R01 4m服務室至10.5m小棚之間的工業量體工作值，不指定已知層數。平頂外量體；沒有逐窗、門、發電機、煙囪或電纜架復原。 |
| **R22：Impianto Aereaz.5° teatro**；`rome10_screen_quarter_vent22` | 圖上是5棚通風設施；約12×30m外框，位於16東側與5西側通路之間。 | 4m高比較R01的4m服務室尺度，平頂及南向維修孔／北小門估配；沒有用假實心柱冒充風管設備。 |
| **R60：Parco Lampade n.2**；`rome10_screen_quarter_lamp60` | 像素[1040,1196]–[1084,1218]，採約26×13m，位於5後橫路北側。 | 低覆屋存放地是圖上實體外框的量體分支，4m比較同刊服務室；三個處理開口及平頂估配。不宣稱燈具數量或圖是逐室測繪。 |

三棚均是單一高空間，空腔薄牆及真正凹口門孔；兩層只在5、15的配套樓，沒有把大棚分成住宅樓板。21是來源折線量體，沒有冒稱其未復原的窗口已做完。新15、16的第三維是比較估值，不因批准中央5就冒稱三者高度皆已證。

## 道路、工作地與材料

原七通路形狀／尺寸保留，只新增`surface: asphalt`。新加北、南接線，15西側12m工作／通行面，15和16之間約5m窄通道，22北南兩片硬鋪工作地，以及22／60／21接線和21周邊道路。共19個原生street／硬鋪項，全部asphalt。

道路沿1953可見白色路廊／淨空，與批准真門面接合；寬度及細小接門段屬用途重建估值，不能當1953測得的路緣。15／16南側接線在4棚之前的真實空隙內轉接；沒有把原前橫路直接向西拉過4／3。22前後工作面留出其來源外框，60南向接到5的後橫路，21的通路終到其北面。空地不加無據庭園或假片場道具。

R01印刷303左欄末段明說廠路與調度／停車空地鋪瀝青；主幹道植栽的文字不能使每一條棚間工作地都必須種樹。本輪採主線8db0bd2的原生asphalt，沒有土路轍，也沒有把`path:true`改名當瀝青。近圖需實看確認。

## 原生資料與保留證據

六個模板只寫一次於`rome10_screen_quarter_revision_templates.yaml`；同一份`revision_trace.geojson`保原生`properties.model.template`與`provenance`，未展平成另一份模型鏡像。獨立`revision_inputs/city.yaml`登記library，正式city.yaml不改。`register.Source`／`local`／`trace`／`overlay`及`citygen.landmark_site`原生使用；每個地標含原生邊距的用地另存catalog供核對，不自寫bounds避讓器。無住宅fabric或自製packer／mesh。

中央body以新舊native era中同錨點的建築記錄比較，僅忽略rise rank；幾何、原parts與位置均須相等。native geo／clip及兩look、15°多建物關係、整區圖與局部range按本輪最終狀態重跑。今日地形／高度倍率與背景底模仍是顯示條件，不是1953地坪和整城復原。來源影像只作研究，不上屏或作材質。

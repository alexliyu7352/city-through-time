# 03火災、金宮湖與Flavian分期研究交件

本件只交可核的研究／原生配置提案；未改正式`city.yaml`、字幕、旁白、FACTS或已確認兩端模型，未編譯、渲染或拍模型圖。來源正文、原圖及權利見[25項來源索引](imperial03_events_sources.json)。`E##`均對應索引中的直接網址及頁／圖。

## 可採結論

64年的火與拆屋分開演；只移除選中的示意住宅與獨立有據公共構件，其他城區站住。湖選有界的140×120m矩形示意、貼現有地形；現有Colosseum ring可作80年開放的低細節量體。**本件模型提案只承諾湖址→競技場的原址轉換，沒有交出完整Golden House復原。**

### 64年：文字可支持到哪裡

[Tacitus XV.38–43（DCC原典）](https://dcc.dickinson.edu/tacitus-annals/15-38)與S63支持：靠Palatine／Caelian的Circus店鋪起火，沿Circus延燒，從低處上丘、又回向低處；XV.39說Palatine及連往Maecenas園地的宮室受火；XV.40說Esquiline山腳大片拆屋，之後另有復燃。這不是逐時路線或逐區清冊。十四區的損毀概括、模型兩端差集，都不能換成精確燒毀邊界或損失率。

[fire_regions.geojson](imperial03_events_fire_regions.geojson)給三個可審窗口：起火參考點`[12.4890,41.8847]`、連接Circus—Palatine—東側低地／山麓的主示範區、Esquiline／Oppian西南山腳的拆屋候選區。起火點靠既有早期Circus的SE端，窗口延至Porta Capena方向，不指認第一間店；後兩區邊界是依已知場所與地形關係插值的**敘事示意**；拆屋位置仍有數百米歧義，不能命名為已測止火線。

原生做法：主`burn`用主區`region`、拆屋區`keep`；拆屋另用`sink`與同一候選區。只有具名住宅ID進入兩個選材。現有trace下，提案為1101／165個互斥示意block，詳[fire_selection_proposal.json](imperial03_events_fire_selection_proposal.json)；數字不代表歷史戶數。保留區以外的物件不動，也不因此宣稱每一棟均已證實在64年倖存。原生最後仍以實際生成構件中心判斷，須由主代理檢查。

|公共場所|64年可畫／不可畫|
|---|---|
|Vesta圓廟 `vesta_temple`|XV.41明列被焚，可列具名損毀候選；後來重建須用另一時期物件，不能同一被移除實體再升起。|
|Circus `circus_maximus`|火起店鋪及沿場蔓延有據；只能用火前S134版本。文字不量化石看台損失，不能把整個石環沉掉，稱所有石構均被燒毀。|
|Regia、Luna廟、Ara Maxima及Hercules祭所、Jupiter Stator|XV.41點名；現有清冊若沒有可靠獨立幾何，記為文字證據，不加無據地標。**這裡的Hercules祭所不等於現有Hercules Victor圓廟，Jupiter Stator也不等於Capitoline Jupiter。**|
|整座Atrium Vestae、Julia、Castor、Aemilia、兩Forum、各劇場／柱廊|不能由XV.41或本示意區推出逐棟全毀。尤其DCC／DAR的Vesta神廟與住宅區是不同證據；不把圓廟的火擴成全部住宅長院毀滅。|
|Statilius Taurus競技場|既有研究有64火毀記錄，但原址／外形尚有爭議，AD14也未選入；不借Colosseum搬置定位。|

不另造第二起火點；XV.40的Tigellinus Aemilian property沒有本件可採的精確界址。Campus與Agrippa公共建築曾用於收容難民（XV.39），也不能因此把每一個區塊標為整場災害中確定未受損。

### 湖：可直接落原生的保守選擇

主要幾何參照是[Villedieu2010，印刷1090頁圖1](https://www.persee.fr/doc/crai_0065-0536_2010_num_154_3_92993)：有0–200m尺、北箭、具名建築及Nero相關牆線；1089頁注2明說綜合Medri1996圖152及後來發掘／復原研究。另以[D’Alessio／Borghini2020，81頁圖3](https://www.icomos.de/data/pdf/hefte-lxxvii-0413-1447-48.pdf)核對已知遺構；79–80頁將湖域描述為有廊的四邊形。這些是考古綜合圖，**不是完整已測水岸圖**。Ball2003的5頁圖1是具名示意復原，9頁稱水面小於後建競技場；只能約束形式與保守尺度，不能把該總圖當精密尺圖。E03–E06。

|原生鍵|採用提案|
|---|---|
|`id / kind`|`nero_valley_lake_schematic / pool`|
|`lon / lat`|`12.492269 / 41.890212`，既有谷地／競技場址只作地理錨點|
|`theta_deg`|`-22`，近似沿圖上L形兩段的正交方向；不是複製橢圓岸線|
|`w_m / d_m`|`140 / 120`，16,800m²為**模型估配面積**|
|`level`|`draped`；畫面需維持「來源約束示意／非古水位」性質|

估配有明確分工：圖中西側建築前緣約在pool局部`x=-89m`，提案NW水邊取`x=-70m`，留約20m空間；L形長段約在局部`y=-84…-89m`，提案SW水邊取`y=-60m`，留約25m空間。**牆線是湖旁構築的約束，不冒認出土岸石**；20／25m是廊道／台地留距的製作估值。SE與NE兩邊分別取`x=+70m / y=+60m`，是以同谷地中心、具名四邊形復原作的對向估配；不能把對稱說成考古發現。未取得Medri全文；二手引述195×205m為含廊構築外包，未採作水面。

四角順序為`[12.4912271,41.8899244] → [12.4928087,41.8894866] → [12.4933109,41.8904996] → [12.4917292,41.8909374]`。完整原生物件、圖讀控制、配準與岸高抽樣見[lake_controls.json](imperial03_events_lake_controls.json)，另交[lake_region.geojson](imperial03_events_lake_region.geojson)。

配準使用Colosseum址、Tiberiana中央院、Oppius八角廳三個具名錨點，明寫像素y向下轉UTM北向上的反射；擬合殘差13.0／5.6／7.5m，逐一留出預測誤差19.7／45.6／34.1m，與圖尺差3.1%。實務保留約50m／10°定位容差，歷史岸界的不確定性另未量化。**第一版控制手性錯誤，已封存於[lake_controls_wrong_handedness.json](imperial03_events_lake_controls_wrong_handedness.json)，其中映射點禁用。** 修正後L角為`[12.4933296,41.8890678]`，在競技場南側朝Caelius；Oppius錨點在東北，Tiberiana在西，方位已分開核對。

只讀現有`terrain16.png`，以原生`terrainio.load/plate_mesh`沿rim每≤8m抽67點：現代rim為27.56–33.02m，dug預設最低rim−0.3m會形成5.756m最大岸高，尚低於6m門檻。這只說今日plate技術上容許該尺寸，**沒有復原古湖水位、池深或填土面**；仍選draped，不改DEM，不提高`banks_m`掩蓋不明古地形。它與河對岸S141的Augustus Naumachia完全獨立，不共用湖岸、尺寸或生滅。

同框的金宮構件可辨為Oppian翼、Velia西側前庭／廊道、Celio的Claudianum／Nymphaeum及分散園地（E02、E04–06），分別可由現有`parts/prism/long_hall`、`arches`與`trees.region`表現；八角廳另可用多邊形`dome`。但這份有限來源件沒有把它們的外牆／覆屋、高度及共用地坪整理成已可入片的完整native量體，**不新放一整片矩形宮殿區，也不宣稱只顯示湖就復原了Golden House**。可量平面與候選類別留為辨識依據，本輪正式提案只有湖。

### 80年的競技場與後續年代

現有已審ring（外189×156m、內79×46m、三排80開口、48m整體高、無地下構造）**可以作80年開放的量體示意**：原址、橢圓觀眾帶、開敞arena及三層外廊符合主敘事；內場長度較來源多3m、矩形假開口及缺獨立attic等既有限制保留。48m是完整外包的既有概括值，不能宣稱80年每層及全部頂層細節已經完成，也不為改年標任意縮放新高度。S86、E07–08。

[PArCo地下設施介紹](https://colosseo.it/mirabilia/i-sotterranei-del-colosseo/)說開幕時技術空間為木構、Domitian改為永久砌體；故不說80年地下完全空無一物。Taylor等2016的26頁注29據後期《354年編年記》解釋Domitian完成至attic／盾飾層，這是完成階段的研究依據，不能當80年全部外觀的同期測量。現在的ring沒有表現這些後增細部，可繼承為有限量體；**永久砌體hypogeum、晚期廊道與升降機、完整晚期頂層、Domitian的Ludus Magnus、81年後Titus拱不可提前加入80年開幕背景。**

|現有ID／組|事件性質與可用狀態|
|---|---|
|`peace_temple`|75年已有的新Flavian公共區；官方記71–75建設，另一官方年表記74開工、75奉獻，採共同的75即可。不等到92／113才首次出現。E10、E14。|
|`domus_flavia`、`domus_augustana_*`|81起建、92啟用的整合新宮，部分納入早建築；不是80開幕時已完整站立。現有Stadium／Circus-facing廊可列同宮殿時段代理，並不代表每翼同日竣工。E10、既有S97／S121。|
|`domus_tiberiana`|官方首個已見考古期在64火後，之後有Domitian及Hadrian增建。舊`81`是模型版本標記，不是初建證據；113代理也不能倒放完整Hadrian北服務立面。E09。|
|`vigna_barberini_flavian`、`apollo_library_halls`、`paedagogium_palatine`、`domitian_forum_entrance`|依既有S112／115–117分別為Vespasian—Domitian台地、Domitian圖書館假說、磚印年代及入口／坡道；採朝代區間，不新造81或92的精確共同竣工日。|
|`titus_arch`、`ludus_magnus`、`domitian_stadium`|拱為81後；Ludus屬Domitian；Stadium86。三者都不是80開幕景物。E15、既有S98、E23追加官方標案PDF2頁。|
|`nerva_forum`|Domitian時期施工、97由Nerva完成奉獻；不是97才動工。E13。|
|`trajan_forum_porticoes`、`basilica_ulpia`|112廣場啟用；具體房量仍承原估值。`trajan_markets`屬Trajan工程，可列112附近狀態代理，不以標記112證明每室同日啟用。E11、S88／98。|
|`trajan_column`、`caesar_forum`|113柱啟用及Venus Genetrix重建；Caesar廣場早在46BCE已奉獻，不是113新造整座Forum。E11、S124。|
|48件`castra_barrack_*`與營牆|仍依既有20–23建營來源成組處理，25不是精確初建年；兵舍布局／版本層數估值不變。|

### 兩端11項差異與未選物件

這些是版本與估配差異，不能當64年逐棟損毀清冊。

|對照ID|正式分期處理|
|---|---|
|`circus_maximus`|已有早期Circus；103是Trajan修建版本。64只用早期形制，不能燒103形態。|
|`jupiter_capitolinus`|早廟已存在，80後有Domitian重修；清冊82非初建。官方英頁把69火誤印為69BCE，本件不採該錯字，不把它移成64。|
|`basilica_aemilia`|AD22後修標記不等於初建；兩端店面／外廊細節不同，也不全是有據的新建工程。|
|`atrium_vestae`|81尚不能當現有104×55m長院的精確首次完工年；DAR指出早期平面延續一世紀，須分後建與代理估值，不能把圓廟受火擴成全院已證全毀。E22。|
|`caesar_forum`|既有廣場與113修復形態分開。|
|`augustus_forum`|西南小exedra在Nerva施工時拆，西北小exedra在Trajan施工時拆；97及112–113是相應廣場完工標記，非兩次確定拆除日。大兩exedrae仍留，假設小exedrae性質保留。E12。|
|`saepta_iulia`|26BCE已奉獻；80火後Domitian重建，推測大平面未改；介面估配差異不能演成已證拆改。E18。|
|`horrea_galbana`|晚共和已有倉儲；81舊標記沒有提供新建或整組毀後重造證據；三院版本估配不可包成一次已知事件。|
|`agrippa_baths`|早浴場已有，80火後大修；不能把現有113房量和不同早期估配全部定為81一次變形。E19。|
|`apollo_library_halls`|早期圖書館早已存在；雙apse是Domitian形態的學術解讀，沒有精確落成年。|
|`forum_civic_paving_01`|兩端鋪地示意窗口不同，不代表113首次鋪地或64整區地坪消失。|

AD80 Campus大火與64分開：Pompey舞台、Saepta、Agrippa浴場等有火後重建依據；相應Domitian版本可於81–96區間加入，**不通通提前到80開幕，也不全寫成81初建**。Diribitorium在80後屋頂不復、仍有露天空間，不等於全建築消失。Pantheon另有110火損、113不放完工Hadrian穹頂。E16–21、S101。未選AD14清冊的75件並非75件全是新建；另有7件AD14選而113未選，也不能由缺席安排拆除：Porticus Liviae、Naumachia、Livia西群及Campus服務院沒有本件可定的整體拆年；Augustus住宅地表代理不是同一套Flavian宮殿；以已知改建界線處理，未知仍標示意。

### 最小狀態序列與交接限制

`AD14基線 → 64火前狀態 → 64局部火損＋拆屋 → 64後–68金宮湖及街區重建 → 75 Peace → 80競技場開放 → 81–96／92 Domitian工程 → 97 → 103／109 → 112 → 113`。AD14不是把14–64間所有變化凍結；營區等既知新增按自身年代入場。被火拿掉的示意住宅由另一有來源的重建層補回；未被選中的城區保持站立。湖只對`nero_valley_lake_schematic`做一次`lose`，競技場用自己的`stages`；不以沉下整座城來代替湖退。

不預設總城市數。限制是同時站立／輪廓最多8座、每座至多4次loss，同一構件只被loss一次。四邊形金宮湖與Naumachia各自生命週期。Augustus兩小exedrae若目前包在一個`parts`中，不能以parts內新增選擇鍵假裝獨立loss；主代理須依既有原生能力選可分件的配置或版本處理，不能為湊loss次數改史實。

可重跑的輕量驗證：`uv run --no-sync --offline python -I cities/rome/research/imperial03_events_controls.py`（GeoJSON合法、IDs互斥、現有native plate抽樣）；`imperial03_events_source_receipt.py`保存來源雜湊／原文提取。這些結果不等於native模型通過、圖像通過或正式03已完成；歷史精確岸界、古水位及逐棟火災損失仍無可量資料，正式幾何／時間線檢查由主代理完成。

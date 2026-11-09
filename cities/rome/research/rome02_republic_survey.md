# 02 共和羅馬：可建模調查與第一件形制提案

本件只處理 step 4。代表年先用 **44 BCE、三月遇刺以前**；不把整個509–27 BCE畫成同一城，也不修改導演已確認旁白、正式站的鏡頭或時間線。模型均為來源約束示意；1975年前沒有逐棟建造年代資料。

**交付狀態：來源調查、分期清冊及原生形制sheet，待主代理／導演確認；未鋪整城。** 原生modelview共用study路徑問題已由主線修復，本件已用獨立 `rome02_republic_sheet` 執行。資料與原文在 `model_reference/rome02_republic/`；來源識別、原文短摘及讀取範圍見 `rome02_republic_sources.md`。

## 分開建的城市狀態

|狀態|代表年／用途|城市差異|不能提前出現|
|---|---|---|---|
|R0 共和初期|約500 BCE；509僅作傳統政治紀年|Capitoline早期Jupiter、Forum公共空間、Regia及早期聚落。早期城界與住宅只按當期證據|中共和11km城牆的完整現存形制、184/179/169 BCE basilica、Caesar廣場、帝都宮殿|
|R1 征服與公共中心擴張|約160 BCE|獨立的Basilica Sempronia與前方Tabernae Veteres；北側Fulvia；保留其間通街，不能一開始就畫成AD12整棟|78–65 BCE Tabularium、69 BCE重建Jupiter、55 BCE Pompey劇場、Caesar建築|
|R2 晚共和／Caesar|44 BCE遇刺前；本輪優先|Sullan/Catulan Capitol、Caesar新廣場與未確定完工程度的Julia、Paulli重建、龐培劇場—柱廊—議事廳；Forum以北、港倉與Campus南部不再等同R1|已完成Curia Iulia、Divus Julius廟、Augustus廣場／Mars Ultor、Horrea Agrippiana、AD6 Castor、AD12 Julia、Flavian/Trajan建築|
|R3 共和末／Octavian勝出後|29與27 BCE兩個觀察點，非同日完工|29年的Curia Iulia及Divus Julius；28年的Apollo後才納入其殿廊；27的政治轉折不代表全套Augustan都市完成|2 BCE Augustus廣場、7 BCE Livia廊、AD14整城、完成的Hadrian Pantheon|

R0、R1、R2至少三份獨立模型輸入；R3逐件按日期接續，不將晚建部分整包提前。這是模型版本提案，正式站如何表演由主代理在step 5處理。

## 先核Forum：位置、街道與平面

1. **位置錨點與歷史平面分開。** 現代Julia、Castor遺址可控制同址；Lanciani等混合年代圖只協助套位，不提供44 BCE整城地籍。DAR標籤點也不能直接當建築中心或足跡。
2. **Vicus Tuscus的Forum出口確定**在Julia與Castor之間；向南、Horrea旁的古鋪面有遺存，但再往南有不同復原路線。第一樣區只取這段可控制的街廊，不將113年Nova Via、Domitian坡道或現代街網整包搬來。[R09]
3. **南側basilica不是已確認的AD12雙層券廊。** 2022年的原始考古重測明確區分早期Sempronia、併入商鋪的過渡階段與Augustan Julia；過渡階段甚至可能屬晚二世紀／Sullan。不能把「過渡露天院」直接改名為已確證的Caesar 46 BCE平面。44 BCE版本採「已奉獻、仍在改建的南側公共建築」有界示意，保留來源中的較早基礎方向，不承諾已知每段施工進度。[R01、R03]
4. **北側Paulli也在改建。** 約54 BCE重建、34 BCE奉獻、14 BCE火後修復是三件事。十五店、十六券及雙層Augustan前廊不可因同址就提前為44 BCE全部竣工。[R04]
5. **Comitium／Curia不能混為今日大廳。** Hostilia／Cornelia在52 BCE火災及重建後又被Caesar工程取代；Curia Iulia在44年可能始建，29年才主要完成。44年遇刺場景用龐培議事廳，Forum北側僅示改建地，不放已完成的Curia Iulia。[R05、R06]
6. **住宅街廓不能從一張復原圖複製成排。** R01原文印刷175頁註97特別提醒，常見圖中的整排小atrium宅是純假設。圖19也明說多數建築形狀、尺度不確定，主要支持方向。此圖不能當精確描摹後的共和住宅統計。

第一連續街坊的工作窗口建議：Forum西南出口—Vicus Tuscus北段—Palatine西北麓，公共／街道錨點沿上述證據，住宅宅界採同城同時期形式補全。**本輪先交形制sheet spec，未生成這個街坊，更未用無據棟數湊比例。** 源圖尚未做到44 BCE住宅地籍套合；若下一輪按同期習俗完成街坊，必須逐棟列明推定，不能說已恢復出土宅界。

## 建築版本清冊

完整機讀表見 `rome02_republic_inventory.yaml`；下表是可直接指導建模的決策。

|建築|本期平面／位置可用部分|44 BCE採用分支／幾何方法|後期排除與估值|
|---|---|---|---|
|Jupiter Optimus Maximus|Caffarelli基礎，同址約62×53m、3.6m基台|69 BCE奉獻的Catulan版本；原生long_hall＋podium／前廊|不倒用Domitian柱高。三內殿／深前廊有復原依據，但現成外量體不等於完整平面；柱高、屋面採早期具名比較估值 [R08]|
|Tabularium|Capitoline兩峰間的多角基台；Forum側11券廊|78–65 BCE範圍內工程，44時可存在；prism＋arches＋上層屋群|頂層及檔案功能細分有爭議，不能用今日Palazzo Senatorio。未量讀完整平面，不能宣稱已具完整落位spec [R07]|
|Sempronia原期|Julia下的F1/F2、通街與商鋪分開|只在R1；選閉合長側、內支承、兩端處理有不確定的長廳分支|約25m寬是作者假說，完整長度未定；169與170紀年差分列。禁止用AD12五廊外廓當測量 [R01]|
|Julia的Caesar版本|同址公共建築；46 BCE未完奉獻|44選有據公共占地／改建量體，屋頂與露天段待sheet比較|不照貼AD12的101×49m、30m中廳、雙層券廊；過渡院式不能確定專屬Caesar [R01、R03]|
|Fulvia／Paulli|Forum北側，179 BCE前身與54 BCE重建不同|44保留改建中的公共量體及商街用途|34 BCE奉獻、14 BCE修復、AD22後修分開；不將晚期十五店／雙層券廊視作44全件 [R04]|
|Forum Iulium／Venus Genetrix|46 BCE首奉獻，三邊廊、NW廟、SW後店室|以早期三邊開敞廣場作分支；不沿113年Basilica Argentaria／Trajan廟上構|44完成／再奉獻有來源概括差；Chalcidicum／東側雙廊是Augustan增建的解讀，不能提前。北界未知 [R10]|
|Curia Hostilia／Cornelia|Comitium北側，不等同Curia Iulia足跡|R1有；R2列為被改建取代的版本，不與已完成Iulia並立|52火後與44拆建不能合成一次事件 [R05]|
|Curia Iulia|Forum北側，Augustan與後來大廳大致同向同尺度|44只作計畫／可能開工；29版本另建|今日磚外牆及Diocletian內裝不提前；凱撒遇刺不在此 [R05]|
|Pompey劇場|55 BCE；cavea朝東，劇場後接柱廊|保留原建cavea輪廓；舞台採共和晚期平直分支|Severan圖上的中央矩形＋側曲exedrae舞台屬Domitian重建，不倒用；廟突出程度仍有爭議 [R11]|
|Pompey柱廊與庭園|劇場以東，中央開場約180×135m；東側議事廳|四廊與園藝留地，種植位置估配；不得填成住宅|Forma Urbis為較晚比較，不證明44逐樹。兩片園景及噴泉辨識有分歧 [R12]|
|Curia Pompeia|柱廊東側，Largo Argentina B/C廟後tufa基座；約20×24m遺構，官方稱廳逾400m²|原生long_hall矩形廳候選；先sheet核量體，未地理定位為精確足跡|UCO常用復原圖明標phase II（約19 BCE），不能拿來當44。封閉／燒毀及第二階段另列 [R06、R13、R14]|
|Castor|Forum南側，117 BCE Metellus重建先於44|選Metellan版本，原址神廟用途保留|AD6八柱／12.5m柱與晚期單階梯均不可直接回填；本輪未量讀Metellan原刊圖，完整上構待分件研究 [R15]|
|Saturn|Forum西南、Iugarius／Capitolinus路之間|44保留較早寺及可能進入Plancus工程的分支，不稱36 BCE完成|現存上構為晚古代；不能用存柱作共和高度 [R16]|
|Regia|Forum東端，梯形院與三小房群|44保留前36年火災的版本；prism／房群|36火後Calvinus重建及29年Divus Julius旁廊不可提前 [R17]|
|Domus Publica／Atrium Vestae|共和時期宗教／居住區，有早期不同房線|用途留地，不能填普通住宅；待早期原始平面|12 BCE併院及火後長庭不倒用；本輪沒有取得Scott原刊完整室圖，未交假完整spec|
|Horrea Agrippiana|同址晚共和宅的Augustan替換|44排除倉庫版本；新發現domus列來源約束住宅窗|33–12 BCE的工程區間跨27年，不能以區間前端斷言29／27已完成。未將DAR北側domus與2023新宅合為一棟 [R18、R19]|

## 住宅形式、樓層與比例

|形式|共和證據／比較|可操作值與採用界線|
|---|---|---|
|一層院宅|同城Casa di Livia較早期被描述為一層，約75–50 BCE；Vicus Tuscus有晚共和住宅，但一處的定年也可能是Augustan [R19、R20]|第一候選沿用已審 `subura_domus_1` 的原生court外形。3.5m層高、院份額.28、25°、出檐.35m全部保留比較估值；不是Livia原宅／屋頂復原。樣張18×28m不當測繪尺寸|
|樓上出租居住|Plutarch《Sulla》1.4記同一租屋的上下居住，屬較晚作者記共和早期生活；Vitruvius2.8.17為接近時期的垂直增建描述 [R23、R24]|可用二層作**最低可讀的分層示意**，不能說共和城只有二層。固定整院二層沿用已審 `subura_domus_2` 幾何，院形與樓層證據分開；未把Sulla屋址、樓層總數或庭院測出來|
|商鋪range|Tabernae Veteres／Novae及Vicus Tuscus的共和商業證據 [R01、R09]|沿用已審一層完整 `roman_taberna` 量體，4.25m及18×18m只是形制樣張選值。每個range不代表獨立租戶，不把屋頂起伏當宅戶數|
|三至五層院樓|既有Subura類別依Hadrianic Ostia／Severan FUR／早二世紀Ara Coeli|不得作共和形制直接證據。這不等於共和無高樓；本輪未把晚期公寓院平面和全區樓層分配倒用|
|坡地豪宅|PArCo新發現Vicus Tuscus宅有多層／可能分台，至少三期，晚二世紀至晚一世紀BCE [R18]|新宅不能被一個同高court冒稱完整復原。已知室區優先；梯台、洞窟宴廳與未出土外廓另需樣品，不用整片格子填滿|

**比例決策：** 沒有取得44 BCE Forum鄰區院宅／出租樓／商鋪棟數比例、全城層數分布或逐戶街廓；不沿113年9455／380、AD14戶數或晚古代Regionary統計反推。三個候選類型的sheet是等展示量的形制比較，**不是住宅樣本統計**。下一輪一街坊採用途導向的同期習俗補全時，須先列選用類型、可用地面積及逐棟選擇，將數量標為製作估配；不宣稱來源給出一個百分比。

## 城市範圍、街廓與保留空地

|區域|來源支持的分布|本期的可操作處理|
|---|---|---|
|中共和Servian圍區|官方約11km、426ha；大部分存牆屬前四世紀重建 [R21]|作R1／R2歷史防線參考，不能當R0完整現存牆，也不當住宅密建面積|
|晚共和外延|DAR用Caesarian／Augustan文獻區分城外相連聚落；14年圖有更晚增建 [R22]|只採「建成區已越牆」與SW河港、NW Campus方向；不抄DAR棕色帶或113年住宅數作44邊界。外緣沿用途及同期已建地標漸變，標示意|
|Forum—Velabrum|主商道、交通、倉儲與密居並存；兩主道間除Cloaca外資料很少 [R09、R19]|古街可控段作骨架，未知支巷按同期習俗；不得以資料空白畫大片空城，也不得把未來倉庫地清空到44|
|Palatine|晚共和貴族居住、宗教場所和坡道|不放Flavian宮殿；未出土房群以具名共和院宅比較補全，不直接套Augustan東院增層|
|Campus南部|共和廟群、Pompey園廊與公共場所 [R11、R12、R22]|建成公共帶、園景與空場分別畫，不能以民宅塞滿|
|Campus中北部|公共集會、軍事／運動場的早期用途延續 [R22]|保留活動場與步行／稀植用途；不提前種Nemus Agrippae或放完成的Saepta、Agrippa浴場、Pantheon、Augustus陵墓|
|右岸／港倉|共和渡河與港市存在；晚共和精確宅界未定|只用已有同代港倉證據，不放2 BCE Naumachia。不得將113年整城沿河的工作院統計拿來倒填|
|北東園林／墓地|有晚共和園產與道路，但園界跨期|不直接複製113年園界、Hadrian大廳、Augustan Maecenas整片配置；園／墓地先逐件定年，未知處不均鋪住宅|

人口本輪不給單一精確值；人口估算不是住宅棟數與樓層的校準器。道路寬、內巷、未知宅界與樹距需逐件標估值。地形×2、水平1:10000與現代建築×3維持既有設定；古地坪相對今地面埋深不直接扣DEM。

## 第一件原生輸入與檢查界線

`rome02_republic_sheet_spec.yaml` 是可供 `tools/modelview.py --spec --sheet` 的原生資料：三種已審幾何的共和來源採用候選，以及Curia Pompeia的一件外量體候選。它不含完整城市、不含住宅填格、不假裝各形制在示範點有古代屋址。房型逐鍵來源見 `rome02_republic_forms.md`；Curia尺寸與理想高度明標估配。

實際檢查、圖片與指令見 `rome02_republic_tool_report.md`。原生sheet有三張12°住宅形制近圖、四張Curia外量體方向圖及一張展示全景；它們**不是一個已完成的歷史街坊**。主線修復後的這份study原生geocheck／clipcheck已通過，仍不等於來源形制或導演批准。先交主代理審圖，再決定街坊比例及地理套合；不擴整城。

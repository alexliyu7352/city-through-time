# 44 BCE Curia—園廊—南側商住第一區

本件只建一個連續窗口，觀察年為44 BCE遇刺前。批准Curia的24×27m、原錨、方向、全部16個parts和兩翼48m返廊保留。新窗口沿原返廊續向西約70m，取東部園庭，南接一條公共通行巷和兩個小街塊；西緣是研究截窗，劇場與完整庭園尚在窗外，沒有用一堵新西牆把窗界冒作古代庭界。約201×163m外包，不是古代地籍／街坊行政邊界。北側Hecatostylum與東側Largo四廟均不以普通住宅覆蓋。

## 來源與分期逐項

|ID|原件與核讀範圍|採用與界線|
|---|---|---|
|Q01|重用[Monterroso2022原PDF](https://helvia.uco.es/bitstream/handle/10396/24612/17_Monterroso_Checa.pdf?isAllowed=y&sequence=1)，原件`model_reference/rome02_pompey_refine/monterroso_complex_2022.pdf`；本輪加讀印刷292–296，重看300–301、圖17／18A/B|沿已批准Pompeian廳，不採Augustan封堵、後期latrines。292–296明言園廊解讀未定，巨大雙樹園與早期公共活動的相容性有問題；本片不倒用Severan兩長條全配置，亦不復原作者爭論中的中央覆廊。|
|Q02|重用[Marra2021作者稿](https://www.earth-prints.org/server/api/core/bitstreams/360b9464-fa88-42e6-8306-22f1e37bc193/content)，PDF4–5|24×27m近方形獨立Curia，保持批准分支；本作者稿未附Fig1圖像，不冒稱其圖已取得。|
|Q03|[Vitruvius5.9.1–9](https://lexundria.com/vitr/5.9/mg)，本輪全文核讀／歸檔|5.9.1明以Pompey廊作劇場後避雨例；§5及§7談露天綠植與排水步行場，屬近時期公共廊園的一般理想。支持廊、露天公共活動／行走空間不同用途，不證本區44年逐條園路、樹列或鋪材。模型以露天活動場、估配邊緣步行路表其功能，沒有造兩片巨樹園或凱旋門。|
|Q04|[Cassius Dio44.16.1–2](https://lexundria.com/dio/44.16/cy)，本輪核讀／歸檔|原文說角鬥士預置在Pompey劇場，藏在peristyle一房；沒有直接說整個庭中央已是競技場。Q01從這段推論早期需留活動空間，兩者分開記。模型沒有臨時看台、ludus界線或角鬥設施，也不聲稱44年完全沒有樹。|
|Q05|重用[DAR Porticus](https://www.digitalaugustanrome.org/records/porticus-pompeianae/)、[Theatrum](https://www.digitalaugustanrome.org/records/theatrum-pompeium-pompeianum/)、[Campus](https://www.digitalaugustanrome.org/records/campus-martius/)，既存02原HTML/TXT；同址配準圖`model_reference/ad14_public_dar_campus_z17.png`|取可證共和存續的劇場在西、園廊在東、Curia在東端的公共骨架與約135m橫寬。DAR敘述北後Hecatostylum、南後商鋪，但平面依Severan FUR，**不是44年南街逐戶證據**。南商住帶的位置與進巷因此明列生產估配；不把晚期商鋪外廓描成已發掘共和宅界。|
|Q06|既交`rome02_republic_forms.md`／`rome02_republic_sheet_spec.yaml`H1–H3；[DAR Livia](https://www.digitalaugustanrome.org/records/domus-livia/)、[Plutarch Sulla1.4](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Sulla*.html)、[Vitruvius2.8.17](https://lexundria.com/vitr/2.8/mg)|只用既審一／二層完整院樓和一層完整店屋。較早Livia一層作同城共和院宅比較；Sulla上下租住僅支持分層，不供總樓層或院平面；Vitruvius是近時期向上增建文獻。沒有將AD79／Hadrianic公寓平面或Livia後增東院放回44年。|
|Q07|既交`early_velabrum_housing_sources.md`及已批AD14類型的適用性核查|Casa a Graticcio的上下商住屬pre79狀態，無法證已在44；本件不新增其陽台／木構／三層型。AD14的實際地塊和32棟比例亦未搬來Campus。|

來源Q01/Q02及DAR的原檔／SHA繼承原refine、02 manifests；本件新Q03/Q04見本資料夾manifest。原圖只供研究，未授權上屏。本文除短語外為轉述，原典年代與考古分期分列。

## 原生配準與批准形制

`register.Source.geotiff`重用既存DAR的EPSG3857轉換，解析為本城UTM；圖讀約0.8904m/px，絕對位置至少5–10m及尚未量化的圖解差。沒有新控制點擬合或宣稱測地殘差。`register.local`由批准Curia錨和−88.2196214459°提供局部公尺框架。新街／宅帶均保留反投影源像素，但像素不把估配變成考古。`registration_overlay.png`先實看再建。

先執行原生freeze，新名`rome02_republic_quarter_curia_approved_frozen`；當日原生check報每個period city均維持。批准spec不覆寫。從批准資料提取一個原生`landmark_types`樣板，在獨立study citydir宣告，實例只寫template／原錨；沒有重寫批准幾何生成器。輸入解析後的16個parts、原尺寸、方位、定位及exaggeration=1均逐值比較。

新北南續廊各69.6m、18柱、.74m柱徑、5.92m柱高／廊深與15°屋面沿批准廊的比較值；長度與柱數為本窗估配，.4m接縫是保留原件的模型裝配縫。南續廊中央一個4.8m門灣、淨寬4.32m、淨高約5.03m，為令城街—廊—庭通行關係可讀的估配，**不是已出土共和側門**。不改已批主門。新增入口仍用原生flat arches，不新增renderer／mesh。

## 房屋、地塊與數量的估配方法

南側外巷距廊後約7.3m，寬6m；外圍及橫向接巷4.8m。這些是公共建築外側通行比較估值，路線未知，不冠古路名。更南的兩塊工作地，先扣原生`landmark_site`的含6m用地、再由`tools/parcels.py`沿巷落整棟；沒有自製packer或額外buffer。西、東兩端通到研究邊緣，不在空地任意斷頭。

靠廊的約19m淺帶用一層完整店屋，比較共和Forum/Vicus Tuscus商鋪，**並非證明該精確南邊界在44年已有同一店列**。較深約39m帶用完整院宅，16–30m最小／最大工作尺度及320m²下限，是既審18×28m／30×36m型樣周圍的有界量體估配，不是假稱源圖量到的普通宅尺寸。部分接橫巷院宅作二層，其餘一層；上下居住和院形證據分開。固定整院同高，不拆翼成樓層梯田。

沒有取得本區44年房型比例或樓層普查，因此不預設百分比／全城戶數，不以人口反算棟數。地塊工具輸出的棟數、宅界、朝向和兩層配置在完成清冊逐件列明，僅是這個授權窗口的製作清單。窗口外沒有畫的地面不表示古代空城；西側劇場、北百柱廊、東四廟尚未建模，待本區批准另行按原圖建。

高度倍率保持正式地形與住宅×2設定；批准公共件及其續廊×1。今日DEM上的公共廊地坪／基礎不代表古代同高地坪，沒有扣古埋深。中央開放活動地保留模型板表面與貼地步行路，**藍色是模型底板，並非水池或44年地表材料**；實際鋪材與古高程未復原。曾試原生0.1m薄prism，但今日DEM令其自生約12m整平基礎，故撤回而不以無據平台充作地面。沒有噴泉、競技圍場或植樹清冊。研究頁的modern hide範圍延至相機外，僅避開現代底模遮擋，不是古代空地／建成界。

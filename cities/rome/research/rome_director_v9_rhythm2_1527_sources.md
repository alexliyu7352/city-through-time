# 1527-05-06攻入羅馬：可畫範圍與限定

**可用結論：同一句「broke into Rome」內，以一個南側／賈尼科洛方向進入Borgo的示意光線，接Borgo短暫轉色。** Porta Torrione、Santo Spirito和Borgo不是三個已證獨立破口。可據官方衛隊史說Torrione被突破；其他原文把Santo Spirito用作山側、街區或進入方向，不能強行合成逐門戰術。不得畫假洞、城牆倒塌、全城起火、精確軍隊數量或前後波次。

本輪已開讀以下原文（2026-11-02）；JSON保存逐條可支持／不能支持。

| ID／原文與定位 | 短摘 | 可支持／界線 |
|---|---|---|
| A01 [Guicciardini《Storia d’Italia》XVIII.8，1929版V卷印138，原典電子轉錄附頁掃描](https://it.wikisource.org/wiki/Pagina:Guicciardini,_Francesco_%E2%80%93_Storia_d%27Italia,_Vol._V,_1929_%E2%80%93_BEIC_1848561.djvu/144)，正文102–104 | “della banda del monte di Santo Spirito”；“entrorno finalmente nel Borgo” | 5月5日駐Prati、次晨從Santo Spirito山側進攻，最後入Borgo。不是精確門洞、路徑或實測時序；轉錄頁標待校讀，另以A02/A03互證核心事實。 |
| A02 [梵蒂岡／瑞士衛隊Profile](https://www.vatican.va/content/romancuria/en/guardia-svizzera-pontificia/corpo-della-guardia-svizzera-pontificia/profilo.html)，義大利文歷史段41–44 | “sfondarono la Porta del Torrione” | 西班牙傭兵突破Torrione，德意志傭兵進入Borgo S. Spirito與S. Pietro，教宗經Passetto避入城堡。未提供座標、破口大小、三條獨立攻入線；不採本頁其他傷亡／戰利品估數。 |
| A03 [Maria Milvia Morciano，Vatican News，2020-05-06](https://www.vaticannews.va/it/vaticano/news/2020-05/guardie-svizzere-fedeli-al-papa-perche-fedeli-a-cristo.html)，404段 | “Porta Torrione, odierna Porta Cavalleggeri”；“entrare da Santo Spirito” | 支持Torrione＝後稱Cavalleggeri，賈尼科洛一側接近Leonine牆與Santo Spirito進入方向。文句壓縮地理，不足證「今Sangallo門洞於1527首先被攻破」。 |
| A04 [羅馬文資局牆博物館，Itinerario8](https://museovirtualedellemura.romasitounesco.it/itinerario-8-mura-vaticane/)，29–32段 | “In questo punto, nel 1527, entrarono i Lanzichenecchi” | 把進入區域放Cavalleggeri／Gianicolo邊界牆段，並說牆再下行至Santo Spirito。是概括導覽，無法給單一缺口；其Lanzichenecchi概稱與A02兵種細分不同，不據此判誰先入。 |
| A05 [同館，Le Mura Vaticane](https://museovirtualedellemura.romasitounesco.it/mura-vaticane/)，21–27段 | “l’incompiuta porta Santo Spirito” | 舊Santo Spirito門名早已有之；現見未完成門及防禦更新屬Paul III（1534–1549）後期。不能把1667圖上的門立面／新防線倒放進1527。 |

**本地映射。** 已實看R09_borgo_work1050.jpg及R09_continuity_vatican_janiculum_read.jpg：Falda1667可辨“P. Caval. Legier.”，但含1527以後工程。`rome07_renaissance_retained_source.yaml`的`vatican_southern_circuit`明定17世紀態，不可作1527破口。`rome06_medieval_leonine`沒有具名Torrione／Santo Spirito門primitive；`rome06_medieval_whole_basis.md`說它依M20 Prandi假說＋M21方向估配，並非逐段1527測繪。`rome06_medieval_whole_registration.json`只支持概括防線（控制殘差3.71–30.38m、留一最高56.21m），不另賦門洞精度。

可辨的原模型**南側牆廊**僅作整體地理參照：舊線頂點13–15（0-based）為`[12.455859216205688,41.899035635137444] → [12.458864788873628,41.89990038749505] → [12.461497357023324,41.900434037363205]`。這是來源模型已有座標，**不是Torrione實址或軍隊穿牆點**。Borgo以既有`rome07_renaissance_borgo_pre1565.geojson`的住宅載體作辨識；其房屋依較晚圖與房型比較估配，亦非1527逐屋清單。不使用1565外牆、1643Gianicolensi線或Passetto當進攻入口。

**最小原生畫法／同句承載。** 使用既有`routes`／`lines`，在已批准南牆廊外側→Borgo的一個概括方向畫一束短移動光，標「攻入方向（示意）／Entry direction (schematic)」；光到達後，以既有`epochs`／`areas`或可用的現存載體選取，令Borgo局部短暫轉色。兩者共用一個入侵事件，不分三路、不用破壞geometry；片中若只容一件，選方向光而不加精確門pin。箭頭端點、掃光寬及填色工作域由導演按同框可讀性決定，均屬製作示意，不填成史料座標。保留Torrione名稱於來源／FACTS即可。全句可同框看見南側牆、Borgo與梵蒂岡／城堡關係，再由既有Passetto逃亡拍點接下句。

未跑compile、瀏覽器、modelview或其他重job；未改正式city/script、已批模型及shared code。新片中事實僅追加FACTS S181。

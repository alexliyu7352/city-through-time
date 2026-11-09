# Fourfix：凱撒肖像與晚共和工程來源

範圍：149秒首次說 Julius Caesar 的真實肖像，以及177–184秒晚共和城升起的工程辨識。只新增本研究與原圖，未改 `city.yaml`、候選設定、FACTS、CREDITS、模型、聲音，未開 compile／browser／modelview。

基準：`本機候選/rome_director_v9_020507_rhythm2/build/film.json`，已實讀SHA256 `c8245290affe2cbf4ceb440a18f76112496b95eb4afcaddf27cd9b361de3dfc7`。

## 可直接採用的肖像

- 原檔：`assets/restart_sources/rome_fourfix_caesar_tusculum_manttorino2089_marie_lan_tay_pamart.jpg`
- 原圖4592×6888，5,729,368 bytes；SHA256 `81e38d7de006071e4a1800d942f76863c56244d0f0b0abba71bd065338c45f19`。
- [Commons檔案頁](https://commons.wikimedia.org/wiki/File:Head_of_Julius_Caesar_from_Tusculum_MAntTorino_2089_n01.jpg)；[原始JPEG](https://upload.wikimedia.org/wikipedia/commons/e/e5/Head_of_Julius_Caesar_from_Tusculum_MAntTorino_2089_n01.jpg)。2026-11-02取得，原檔未改。
- 攝影：**Marie-Lan Taÿ Pamart（Commons：Jastrow）**；EXIF拍攝日2026-05-14；Commons上傳日2026-07-26。
- 照片：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；雕像本身為public domain。照片仍須署攝影者、列授權連結，若後續裁切或修圖須注明變更，不能只標PD。
- 原頁物件說明：Tusculum出土的Julius Caesar大理石頭像，Commons定年45–44 BCE，館藏Museo di Antichità／Musei Reali di Torino；原頁列Inv.2089。定年與館號為Commons條目資料，本次沒有把它們冒作已讀到的館方逐件編目。
- 已目視下載原檔：完整頭頂、面孔、頸部，近正面略偏，深色背景；輪廓清晰，足供人物初次介紹。不需要AI或另做修補。
- 已存素材搜尋只找到Augustus肖像；原`restart_ip02_caesar.png`是遇刺想像，不能作此人物肖像。

**館方人物認定已交叉核查。** Musei Reali的[2019年展陳計畫原PDF](https://museireali.beniculturali.it/wp-content/uploads/2022/09/PFTE-01_Relazione-generale.pdf)第8頁正文將館藏肖像認為Julius Caesar並說明來自Luciano Bonaparte在Tusculum的發掘；第9頁實看相同頭像，caption為“Cesare di Tusculum”。PDF日期2019-06-07，SHA256 `28f5d48efe9d9562eb895b605b7a0df8d7b60f2a7c2a8f91de5a7b27b4acfa83`。web反覆403後，普通HTTP下載成功，已讀原PDF文字並目視第9頁；館方PDF圖片只作認定，不拿它上屏，也不沿用其照片授權。

最短上屏名：`尤利乌斯·凯撒` / `Julius Caesar`。副名若需要：`图斯库卢姆肖像` / `Tusculum portrait`。不必在149秒附精確雕刻年代，避免把Commons定年當成活人照片的日期。

短credit：`Marie-Lan Taÿ Pamart / Wikimedia Commons · CC BY 4.0`。

建議CREDITS新增完整項（由writer合併；此處未改共檔）：

```text
- Julius Caesar, Tusculum portrait, Museo di Antichità / Musei Reali di Torino.
  Photograph: Marie-Lan Taÿ Pamart (Jastrow), 14 May 2026, Wikimedia Commons.
  CC BY 4.0. Original photograph unmodified.
  https://commons.wikimedia.org/wiki/File:Head_of_Julius_Caesar_from_Tusculum_MAntTorino_2089_n01.jpg
  https://creativecommons.org/licenses/by/4.0/
  Identity cross-check: Musei Reali, Relazione generale di progetto, 7 June 2019,
  PDF pp.8–9, caption "Cesare di Tusculum".
  https://museireali.beniculturali.it/wp-content/uploads/2022/09/PFTE-01_Relazione-generale.pdf
```

若呈現時裁切，將`Original photograph unmodified`換成實際變更說明；不要改寫原JPEG。

## 44 BCE已存模型可辨識的凱撒工程

下表都是既有`republic_late_city`的共和版本，資料沿主線R03／R10／DAR Circus與公共清冊，沒有重做整城研究。坐標是現模型的示意錨點，非新測地精度。`source_year`為有據工程事件，不是把44 BCE觀察態當成建造年。

|最短中英名|原landmark id與[lon,lat]|準確性質與source_year|可用最短狀態字|
|---|---|---|---|
|凯撒广场 / Caesar's Forum|`forum_iulium_caesarean`；[12.4849,41.89392]|凱撒發起，54 BCE已籌備購地；46 BCE首次奉獻。DAR另記Octavian在44 BCE完成／再奉獻，不能將後續收尾全算作凱撒在世建成。`source_year: -46`（首次奉獻）|`凯撒奉献 · 前46` / `Caesar dedicated · 46 BCE`|
|朱利亚会堂 / Basilica Julia|`julia_caesarean_working_hall`；[12.4847834,41.8919606]|凱撒約54 BCE發起替建；46 BCE**未完工奉獻**；後由Augustus完成，首次完成精確年本來源未定。`source_year: -46`（未完奉獻），不是完工年。|`凯撒始建 · 未完奉献` / `Begun by Caesar · dedicated unfinished`|
|大竞技场 / Circus Maximus|`circus_maximus`；[12.48531,41.88592]|既有競技場由凱撒於46 BCE**擴建**，非凱撒初創。DAR保留Augustus可能完成原計畫的解釋。`source_year: -46`（擴建）|`凯撒扩建 · 前46` / `Caesar enlarged · 46 BCE`|

優先用凱撒廣場；朱利亞會堂若標，必須留「未完」狀態。大競技場可作第三項，仍稱擴建。上屏不能統稱為「凱撒建成」的三座新建築。

來源：

1. [Mercati di Traiano官方：Foro di Cesare](https://www.mercatiditraiano.it/it/sede/area_archeologica/foro_di_cesare)：54 BCE籌備，46 BCE廣場與Venus Genetrix廟啟用；該頁配圖明標Trajan時代，不能當46 BCE上構原圖。
2. [DAR Forum Iulium](https://www.digitalaugustanrome.org/records/forum-iulium/)：46 BCE凱撒首次奉獻、44 BCE Octavian完成／再奉獻；三側廊、NW神廟；Augustan東雙廊及北接口假說分開。主線研究R10已採此界線。
3. [DAR Basilica Iulia](https://www.digitalaugustanrome.org/records/basilica-iulia/)：約54 BCE開工、46 BCE未完奉獻、Augustus後完成；火後版本和有爭議AD12再奉獻另列。主線R03與`rome02_formal_prepare_phasing.md`已有此日期，無須新發明完工年。
4. [DAR Circus Maximus](https://www.digitalaugustanrome.org/records/circus-maximus/)：46 BCE凱撒擴建、連續三側看台與防獸水渠；Augustus可能完成的限制另載。主線W03及清冊採Caesarean早版。
5. 本地坐標／版本：`research/rome02_republic_whole_inventory.json`、`research/rome02_republic_whole_sources.md`、`research/rome02_republic_whole_evidence_decisions.md`、`research/rome02_formal_prepare_phasing.md`；FACTS S149–S151、S153。

**需writer處理的既有升起時序：** 基準film的晚共和城`on=177.738`；第一front啟用範圍177.15–183.55秒，只223組，source第一stage`outward_growth`只選`fabric`。上表三個landmarks不在第一stage；它們屬`observed_city`剩餘項，其front啟用範圍183.9–190.3秒、curve自184.3秒開始。故不能僅因177秒整城開始升起，就在177–184秒把三個pin當成已有建築。標名須跟實際建物升起／站穩同步；這份研究沒有擅改stage選擇或其時長。若將標名限定在177–184秒，writer／root須先解決這一已有stage與標名時窗的相容性，不能把pin放空地。

**朱利亞版本界線：** 44模型只可標`julia_caesarean_working_hall`（25.1×73m有界估配、一大廳加低側廊），不能指向帝國AD14／AD12五廊、雙層券廊的`basilica_iulia`；後者在該時窗尚未升起。`curia_iulia`完成廳、Saepta成品、Divus Iulius廟、Marcellus劇場也不能改標成凱撒已建成的44 BCE工程。凱撒廣場只用46早期三邊廊版本，不倒用Trajan Venus／Argentaria。

## FACTS最小新增建議

肖像新事實可加一小段：

> 凱撒人物肖像採Tusculum出土、現藏Musei Reali di Torino／Museo di Antichità的大理石頭像照片。館方2019年展陳原PDF第8–9頁正文與“Cesare di Tusculum”圖說確認人物及來源地；照片由Marie-Lan Taÿ Pamart拍攝、以CC BY4.0發布於Commons，與雕像本身的PD狀態分列。原圖及授權見research/rome_fourfix_caesar_sources.json。

工程日期直接沿R03、R10及DAR Circus；若新增上屏狀態文字，可補一句：凱撒廣場46 BCE首次奉獻；朱利亞會堂同年為未完奉獻、後由Augustus完成；大競技場為凱撒46 BCE擴建。全城升起仍是44 BCE觀察態的展示，不表示每棟都在凱撒執政或44年新建。

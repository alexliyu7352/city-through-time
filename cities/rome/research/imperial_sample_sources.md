# 第4步：帝都房型與地標樣張依據

> 房型已按新版「Choose the form by how the buildings were built」重做，最新為[房型樣張](../build/review/modelview/imperial_houses_form_update/houses_sheet.jpg)及[房型／山丘核對記錄](house_form_hill_review.md)。舊`imperial_samples_113/`中的房型圖不再作本輪交付；六件地標的資料未在本輪變動。

本輪只審 AD113 城市將用的形制，未把樣品街排成歷史街區，也未接入正式03站。使用現成 `tools/modelview.py --sheet`；房型是 `types:` 資料，地標是 `pipeline/landmarks.py` 現有類別。沒有另寫造型或檢視程式。

## 房型

| 樣品 | 有據形制 | 本輪推定與限制 |
|---|---|---|
| H1 `roman_domus`：低層內院住宅 | [Padova TESS，Casa del Poeta Tragico](https://tess.beniculturali.unipd.it/web/scheda/?recid=14866)：前門兩側商鋪、atrium、tablinium及後方peristyle，年代止於79年。是同時代意大利對照，不冒稱羅馬某棟住宅。 | 18×28m樣品地塊、一層4.25m、院佔.22、屋面25°及檐出.35m都是依該具名住宅及H2商鋪高度作的概括推定。通用court只有一個院，不能同時精確復原atrium雨孔與後院；此樣品審低屋面、採光院與街面，不能稱完整domus復原。 |
| H2 `roman_insula`：底商出租樓 | [Caen研究組，Rue bordée d’insulae](https://rome.unicaen.fr/monument/InsulaePompee/)引Vitruvius2.8.17支持共和末期已有多層住宅；討論Trajan的18m限制，約五層、每層3.5m。[市府Ara Coeli](https://sovraintendenzaroma.it/i_luoghi/roma_antica/monumenti/insula_dell_ara_coeli)記底層tabernae與至少五層；[官方兩頁說明](https://sovraintendenzaroma.it/sites/default/files/storage/original/application/38bd9dd7189bec26b1f3329a548b0369.pdf)給二世紀初數十年與商鋪夾層梁高4.25m。 | 改為一棟detached、固定五層、平均3.5m，36×30m是整棟的樣品地塊推定，不是Ara Coeli實測輪廓。完整內院不確定，故不採court。停用12×18m窄戶row與隨機3–5層，不能讓同棟出租樓長成逐戶鋸齒山牆。25°屋面及檐出.35m為依Caen同類復原推定。Ara Coeli不保證113年前建成，只作近時期比較；不倒用晚期柱廊，也不畫今日地下9m。 |
| H3 `roman_taberna`：一體低層鋪房 | H1的具名Pompeii住宅前鋪，及H2的具名Ara Coeli商鋪高度比較。 | 來源只支持住宅內的前鋪，並未支持一條逐戶加層的獨立商住街。改detached、固定一層的完整鋪房量體，18×18m為整座樣品地塊推定；4.25m、25°屋面、檐出.35m同樣為具名商鋪類比的建模推定。停用6×10m窄戶row與一至兩層隨機高度；不斷言另有樓上住宅或夾層。 |

上述地塊是樣品代表值；正式街區須另依有據路軸、地塊尺度與不規則邊界落位，不能把這三排當作古城。房高暫用城市既有×2；尚不是地形倍率結論。

### 按新版House types逐項核對

1. H1：單棟內院住宅、court、固定一層，符合「一次建成的一棟樓」；保留形式及18×28m地塊。
2. H2：舊row把同棟出租樓錯分成高低窄戶，改整棟detached及固定五層；地塊改為整棟尺度36×30m。兩者都是示意型，不冒稱Ara Coeli實測復原。
3. H3：舊row及一至兩層沒有逐戶建造依據，改固定一層的完整鋪房；不再用「商住街屋」名稱暗示已證實上層居住。
4. 三型的25°均為畫面上的25°。新版共用工具已讓斜屋頂保持角度，重編譯即可；未用本城腳本反向補償屋高倍率，也未改共用程式。

### 按新版Hills on the plate核對

`city.yaml`已有`terrain.shade: {k: 1}`，沒有白色`col`覆蓋；預設固定西北光az325°、el25°，用台面`#3a4757`的色相，背光坡面變暗，平地及水面保留原色。新共用shader取代舊白色加亮，本輪只重新編譯／取景。地形×2、150m以下起伏×1、bare earth及地形檔均未改，因此不重跑DEM或prep。

近景以已核S90的Aula Regia作Palatine山頂錨點，並取Forum谷地為對照。`palatine_hill_sample.yaml`的hide多邊形只為收起會擋住地形的現代建築；它是檢視窗，**不是113年城市邊界**。沒有加入舊城布局、假屋群、白色等高線或自訂地形光。×2仍待整座古城落位後驗收，不能以單一地標或平地房型樣品代替整城坡度檢查。

## 地標

| 樣品／類別 | 尺寸及形制依據 | 估值、近似與無法表現的部分 |
|---|---|---|
| L1 Colosseum／`ring oval` | [Roma Capitale](https://www.turismoroma.it/it/node/1155)：外189×156m、高逾48m、arena76×46m；[Bologna velarium研究，p22](https://amsacta.unibo.it/6307/1/Velarium%2007-01-2020%2B.pdf)：三排拱廊、每排80券，上有實牆層。 | 高取48m、arena牆4m推定。現成等厚座席環依短軸46m得到長軸79m，比市府數字長3m。現版本ring的三排開口實畫為深色矩形，未復原圓拱頂；也未精確分出上部實牆層、柱式、velarium。保留此限制，不再用64座塔假扮外牆。 |
| L2 Circus Maximus／`ring u` | [市府](https://www.turismoroma.it/it/luoghi/circo-massimo)約600×140m；[Platner/Ashby](https://penelope.uchicago.edu/Thayer/E/Gazetteer/Places/Europe/Italy/Lazio/Roma/Rome/_Texts/PLATOP%2A/Circus_Maximus.html)：arena長568m、寬75–87m、座席帶27m、spina344m。[Caen具名復原](https://rome.unicaen.fr/monument/cirquemaxime/)作立面比較。 | 採短軸86m保留27m座席帶；等寬U形不能還原漸寬賽道。高度20m、arena牆3m、spina截面8×2m依同場復原推定。現成直段530m，344/530=.649057使spina長約344m。起跑閘概括為低橫體；沒有另造分段塔看台，沒有357年第二方尖碑。 |
| L3 Basilica Ulpia／`parts`中的`long_hall`及半圓端廳 | [Juhana Heikonen博士研究Table I，紙頁238](https://blogs.helsinki.fi/romanhouse/files/2017/08/Heikonen2017.pdf)：中廳約25m寬、25m高、側廊6.5m；[學術建築說明及Packer立面圖](https://penelope.uchicago.edu/encyclopaedia_romana/imperialfora/trajan/basilica.html)：雙端apse、雙側各兩廊、木構屋頂。 | 寬51m=25+4×6.5；長方體長119m、apse半徑25.5m、側檐12.5m、中央屋面22°及檐出.6m是依該建築復原比例簡化推定，整長約170m。初圖的預設半球頂過高，已撤回；端廳改用現成dome的180°、cone屋面，高5m為依具名立面低屋頂的推定；兩端與主體各交疊.1m作整件聯集。通用類別未分出兩端迴廊，中廳畫成連續體量，不能稱表列88m中廳長度已復原；長側入口與全部柱列也未復原。 |
| L4 Castor/Pollux神廟／`long_hall` | [Caen](https://rome.unicaen.fr/monument/templecastorpollux/)：台基約30×50m、柱高12.5m、前8側11柱；Tiberius於AD6重建的形制可作113年對照。 | 類別本體29×49m，預設台基外加1m形成30×50m。台基7m、檐口14.5m、退牆4.5m、15°屋面及.6m檐出為據同廟復原的推定。側柱數由通用間距生成，階梯概括，非逐柱測繪。 |
| L5 Domus Flavia的Aula Regia／`parts` | [Caen](https://rome.unicaen.fr/monument/domusflavia/)：廳外37×44m、室內可能高於27m；前有柱廊。另見FACTS S81。 | 本輪只做接見廳與前柱廊，未聲稱整宮完成。檐28m、22°屋面、.6m檐出；前廊37×6m、檐8m、柱7m、前10柱與4m深皆據同一具名復原推定。廊與主殿交疊.5m由parts合為一體，整件共用地坪；宮殿各區高差待正式布局處理，不再逐翼獨立貼坡。 |
| L6 Trajan Column／`column` | [St Andrews測繪研究](https://arts.st-andrews.ac.uk/trajans-column/the-project/description-and-condition-of-trajans-column/)：柱29.78m、基座5.29m、基座方體寬5.30m、柱徑3.68至3.29m、torus高.855m、abacus寬4.34m、古代總高或約38m。 | taper=.894；基座簡化為方體。用現成stages分出底圈.855m、簡化柱身27.725m、方柱頭1.2m，合計仍29.78m；柱頭高度與底圈寬4.34m按同柱比例推定，27.725m是扣除這兩段的建模餘量，不稱實測柱身長。頂部圓鼓／人像合高2.93m、寬1.2m為依約38m總高的推定。古頂原貌不確定；不是今日聖彼得像。沒有螺旋浮雕、柱頭雕刻；不以額外實心條假裝浮雕。 |

所有地標的經緯度只保留已核遺址錨點；`--sheet`會搬到樣品列並統一方向，供看四面，**不是正式落位／朝向驗收**。外部圖片僅研究參照，未上屏。已留存Caen出租樓與Domus Flavia北立面復原圖於model_reference/，只作形制比較；Heikonen原PDF及文字摘錄同存該目錄。

## 驗收範圍

本輪交付的是房型與地標審形，尚未排成113年古城。**目前有效的交付在 `build/review/modelview/imperial_samples_113/`**；先前兩個單獨樣品資料夾保留比較，其中舊Ulpia半球端頂、未分柱頭的Trajan柱已由本版取代。

- [三款房型近景](../build/review/modelview/imperial_samples_113/houses_sheet.jpg)：由左至右H1低層內院住宅、H2底商出租樓、H3低層商住街屋。俯角35°、距離.018（180m）供審形；[原本片中近景距離.045的對照](../build/review/modelview/imperial_houses_samples_113/sheet.jpg)保留，不能把放大的審形距離冒稱已定正式鏡頭。
- [地標四面對照](../build/review/modelview/imperial_samples_113/landmarks_four_sides.jpg)：由上至下L1競技場、L2 Circus、L3 Ulpia、L4 Castor/Pollux、L5接見廳與前廊、L6 Trajan柱；由左至右方位30°、120°、210°、300°。
- [原色全向檢視](../build/review/modelview/imperial_samples_113/imperial_samples_113_film.jpg)及[白色銳利檢查外觀](../build/review/modelview/imperial_samples_113/imperial_samples_113_check.jpg)：官方eraview輸出，八方向×兩俯角、最大四件地標的四面及整列四向。另有上列modelview的全部六件地標各四面。已看完整對照表，背面屋頂、座席環、柱廊與端廳都有實體；通用類別欠缺的細節按表明列。
- [本版geocheck](../build/review/modelview/imperial_samples_113/evidence/geocheck.log)：786個幾何件，面向錯誤0。
- [本版clipcheck](../build/review/modelview/imperial_samples_113/evidence/clipcheck.log)：房屋與地標／街道、地標互穿、穿牆、現代與古代相交、浮空、地形吃樓、鋪面埋入及高地基均0；現代建築浮空0。樣品高地基比例最高一成約10%，未超30%。
- 先按新版最低地坪規則重跑官方prep，現代建築140,866棟。既定範圍、1:10000及現代建築×3不變；旁白與本機設定雜湊未變。台面改深藍、`era_look.dim:.8`及`terrain.shade.k:1`，樣品沿用真實城市的配色／燈光；沒換成自訂審查色。
- 原點12.385,41.815是DEM選出的平緩樣品場，約1800×220m研究帶在地形×2下坡度第90百分位約2.2%；**不是模型的歷史位置，也不能用它接受Palatine／市中心地形×2**。整城仍待真實落位後依現行坡度規則重驗，並交市中心近景。
- 官方modelview刻意只展示一個年份且沒有旁白；編譯記錄中的「不是2026年」與研究片空白提醒屬這個靜態樣品用途，不能據此宣稱正式影片的時間／閱讀檢查通過。靜幀工具的可選`bundle.json`提示走原有城市資料夾讀取後備路徑，已實看新模型；未新增空manifest壓掉訊息。

可重現資料為本目錄的 `imperial_houses_sample.yaml`、`imperial_landmarks_sample.yaml`；合併後輸入留在 `build/review/modelview/imperial_samples_113_input.yaml`，只合併資料、不產生造型。實際命令：

```sh
uv run --no-sync --offline python -I tools/modelview.py cities/rome imperial_samples_113 --spec cities/rome/build/review/modelview/imperial_samples_113_input.yaml --year 113 --sheet --at 12.385,41.815 --d 0.018 --name imperial_samples_113
```

房型35°近景以官方`render/still.mjs`沿上述三個房型相機目標再拍，未改film.json；對照表使用官方`tools/sheet.py`。完整命令輸出及編譯／渲染記錄在`build/logs/*samples_113.log`與樣品`evidence/`。

正式城市也已重新編譯：816.90秒（13:36.90），14站起訖／年份逐項與本輪前相同，空白段0，191條字幕；旁白及local/config.json雜湊均不變。主片尚無接入的時代城，所以主片geocheck的空集合不能當第4步完成；真正審形的檢查是上列786件樣品。原有29項文案密度提醒仍待畫面逐條處理，沒有宣稱全片檢查通過。核對記錄：[validation.json](../build/review/modelview/imperial_samples_113/evidence/validation.json)。

樣品可旋轉預覽：<http://127.0.0.1:8766/play.html?city=rome&bundle=cities/rome/build/review/modelview/rome/&view>。8765是另一個已在跑、讀不到本目錄樣品的服務；未停止它，另用官方preview工具啟動8766。已核對HTTP200且供應的study film.json與本輪本機檔逐byte相同；看新頁前請重新整理。

# Curia Pompeia：44 BCE入口、議事廳與東柱廊

狀態：單一來源約束示意分支，等待主代理審查；不是已批准共和街區／整城。只處理遇刺以前的廳與相鄰東柱廊局部，不改正式鏡頭、旁白或原02首件。

## 採用分支

採Monterroso團隊的**獨立議事廳、切開東柱廊中央**解釋。廳在劇場對面、柱廊東側，正面朝園庭／劇場方向；以一個有實際通孔的簡單中央入口連接園庭通行面，兩側有覆頂柱廊及短北南返廊。獨立是考古形制結論，不再把它展示為沒有園廊關係的孤立高盒，也不把它黏成一個普通半圓exedra。

44 BCE排除Augustan封堵／背牆6.5m寬至少2m高混凝土塊、後期latrines及廳背兩層房間；沒有外部Pompey巨像、刺殺人物或血戲。未取得完整44年外立面，中央入口數量、寬高、上窗、屋架及柱式不能稱出土復原。本輪只作簡潔矩形門洞、完整覆屋及可讀柱列，不補無據華麗立面。

## 原件與核讀範圍

|ID|原文／原圖|本輪實讀／採用|限制|
|---|---|---|---|
|P01|[Monterroso Checa，Il complesso pompeiano del Campo Marzio. Forma e dibattito，2022，pp.298–301](https://helvia.uco.es/bitstream/handle/10396/24612/17_Monterroso_Checa.pdf?isAllowed=y&sequence=1)|公開原PDF29頁，本輪核讀印刷298–301；實看PDF25頁（印刷301）Fig17A/B與Fig18A/B/C/D；Fig17A把新測Curia覆於FUM，Fig18A明標Pompeian，18B才是Augustan封堵。正文300明言獨立建築，與後添latrines的構造、地坪不同|Fig17／18是考古平面與分期，不給44立面／簷高。Fig16中央廊線屬作者對Severan FUM的爭議解釋；本輪不把該中央長廊倒放44，也不推全園植樹|
|P02|[Marra等，Archaeometry2021作者稿，DOI10.1111/arcm.12740](https://www.earth-prints.org/server/api/core/bitstreams/360b9464-fa88-42e6-8306-22f1e37bc193/content)|原作者PDF16頁；本輪核讀PDF4–5頁與圖說。PDF4明載近方形24×27m、位於東柱廊中央的獨立建築；原期61–55BCE、Augustan及中世紀分開|作者稿未附圖像，只有圖說，不宣稱本稿取得其Fig1原圖。24×27m取代原sheet依較舊DAR的20×24m遺構概數；兩者不平均、不稱同一量測範圍|
|P03|[DAR Curia](https://www.digitalaugustanrome.org/records/curia-pompei-pompeiana/)、[DAR Porticus](https://www.digitalaugustanrome.org/records/porticus-pompeianae/)|重用既有`model_reference/rome02_republic/dar_{curia_pompei,porticus_pompeianae}.{html,txt}`及`model_reference/ad14_public_dar_campus_z17.png`／`ad14_public_dar_campus_sources.json`。Curia同址定位、東廊與劇場相反關係；園庭180×135m是概述尺度|DAR舊exedra解釋與20×24m不壓過P01/P02新分期。14年圖只取存續公共複合體的位置／主軸，廳的Augustan封閉狀態不搬回44；標籤27不當中心|
|P04|[Sovrintendenza官方Curia](https://www.sovraintendenzaroma.it/content/la-curia-di-pompeo/)|重用02既存HTML、5頁原PDF，實看第3頁。大矩形廳逾400m²、B/C神廟背後tufa基座、劇場／園廊整體關係|第3頁油畫不是古立面；右下紅框只為位置提示，不取其框界為精確足跡|
|P05|[Vitruvius5.1.6–9](https://lexundria.com/vitr/5.1/mg)|重用既存`model_reference/ad14_campus_completion_vitruvius_5_1.html`；Fano具名公共／司法會議廳的50 Roman ft整柱＝14.8m、下層20ft＝5.92m作近時期上構比較|Fano是Augustan公共basilica／tribunal，非Curia Pompeia考古高程；本輪14.8m簷高、5.92m廊柱是**跨公共會堂類型的有限估值**，不是量到的原高或共和全城通用值。原sheet22m的Vitruvius5.2理想curia比例不再當作本廳簷高|

P01/P02在本輪新歸檔至`model_reference/rome02_pompey_refine/`。P01先收到211-byte JavaScript cookie轉址頁，按公開頁面的普通cookie轉址再成功取得%PDF；不把第一次HTTP200冒作取得原PDF。下載URL／SHA與重用清單見manifest；所有第三方原圖只供研究，未授權上屏。

## 地理與逐鍵估值

用現成`pipeline/register`讀DAR既有EPSG3857像素變換，製作本件GeoTIFF再描點／畫overlay；不手寫經緯度換算。位置取東廊中斷處的**圖形線條**，非27標籤。原圖約0.89m／pixel；地理精度仍僅約5–10m，並有新舊平面解讀差異，不能宣稱測地精度。

- 廳外包：P02報告24×27m；長軸朝園庭—劇場，短面為西正面。DAR主軸稍偏北，以描到的廊線定方向。P01圖17B／18A支持近方廳及背部結構，沒有足夠證據恢復全部門窗、室內柱位或古地坪。
- 廳簷14.8m：P05的50ft單層公共廳柱比較估值；15°雙坡及0.3m出檐為低坡意大利公共建築覆屋示意，不稱已得此廳屋頂。牆厚1.48m＝比較柱高的1/10工作值；中央門寬4.8m＝廳寬1/5、門高5.92m＝P05的20ft工作值，**全部估值**。入口朝園庭為組織推斷，具體中央單門不是考古發掘結論。
- 門洞用原生`arches`的`arch: flat, through: true`；牆及屋面用`prism`／`long_hall`資料部分，入口後保留空廳，不以實心long_hall堵門。屋頂承於牆頂用`atop`，不用自寫mesh／renderer。
- 東柱廊：只做廳兩側各一段，沿DAR廊線及135m庭寬的同址關係；向西各返48m是清楚標出的**樣片截窗**，不是古廊終點。5.92m柱高、5.92m通行廊深採P05比較；.74m柱徑借Fano2.5ft下層pilaster寬、.9收分、1m背牆、1m承頂橫帶、柱距和14／13柱數均為工作估值。柱廊屋脊順各廊長軸，使用原生column的repeat列與轉90°的long_hall屋面部件，沒有自寫mesh。
- 複合體共用水平地坪；地形沿正式既有DEM，不扣古埋深。廳／廊一件parts使用`exaggeration: 1`呈比較原比例，避免原22m再被城市倍率拉高；正式城市×2設定不動。
- 庭園只表廊前通行面與門外3m短門檻（均估值），不補一條無據的長中央軸道，不重建全部園景、劇場、神廟或後側Largo Argentina；截窗以外空白不是44年無建築的聲明。
- 原生parts的共同整平基礎可能在片窗外包下連成完整淺色展示底座；這是今日DEM上的工具基礎，不能當成整個古庭園已證鋪石或同高台基。考古地坪與坡度未復原。

本輪只交一個source分支與一個原生樣片，無住宅、類型比例或整城複製。

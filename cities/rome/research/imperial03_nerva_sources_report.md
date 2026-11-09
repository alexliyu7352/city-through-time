# Nerva與Augustus主東南半圓：接縫來源核對

**可確定的修正是Nerva北端形制，不是拆除Augustus主半圓，也沒有整區平移的來源理由。** 現`45×110m`直矩形把圍牆一路延至廟後；圖證顯示長牆在廟前側轉接兩翼牆，廟後另接半圓及Porticus Absidata。現Minerva的`21×31m`矩形podium也把較寬前部的寬度套到較窄後部。以下是可追溯的圖讀提案，**尚不足以唯一決定無碰撞的施工座標**。

## 直接圖證

1. [Meneghini，Scienze dell’Antichità21.3(2015)，59–80頁](https://rometheimperialfora19952010.wordpress.com/wp-content/uploads/2017/06/preesistenze_monumentali_al_foro_di_nerv.pdf)：**印刷76頁／PDF21頁Fig16**為作者繪製的最終期復原總平面，直接畫出主半圓、Minerva及兩翼牆的接合；**印刷73頁／PDF18頁Fig15**為Bauer較早的測繪總圖，可辨廟後較窄、前殿較寬及台階。後者圖說明列為近期發掘以前，對面「Janus廟」的舊復原正是本文重新討論的對象；只取本接縫，不複製其他形制／年代。原文及原生嵌圖已存本件前綴，見下方。
2. [Stanford Forma Urbis16a編目及原件](https://formaurbis.stanford.edu/fragment_16a.html)：`ANALYSIS`的Forum Transitorium／Minerva段直接說廟向後推至Augustus**主東南半圓**所容許的位置，廟兩側以微彎牆遮住不等的後部空間；東南側開口通往梯形空間。原件能證接合拓撲，但屬Severan石刻圖，不能獨自證97年每一牆線；編目還指出刻圖的cella後apse與出土矩形空間不符，不能照刻圖補一個已證apse。
3. [市府Gli emicicli](https://www.sovraintendenzaroma.it/content/gli-emicicli-1)末段只把**西側南小座**與Nerva工程相聯；[Minerva官方頁](https://www.sovraintendenzaroma.it/content/tempio-di-minerva-e-colonnacce)第二、末段支持窄長場地、突出柱列及短邊嵌入廟，均不支持現有直矩形北界。小座假設性沿用[官方Augustus平面圖說](https://www.sovraintendenzaroma.it/content/la-pianta-del-foro-1)，不因本件取得新圖而升格。

## 配準與可用座標

Fig16原生嵌圖為`910×639px`。以8個共用Augustus點，對既有`ad14_public_augustus_official_plan.jpg`做保留軸向的圖間最小平方擬合：

`Fig16.x = 0.7718781923 × official.x −78.18909617`

`Fig16.y = 0.7687809854 × official.y +4.037212088`

再沿用原官方圖`3.1px/m`、Mars圖點`[500,113]`、OSM錨`[12.4869456,41.8943657]`及`theta=−51°`；UTM33N轉換與原生`Builder.frame`相同。圖間殘差為0.09–0.69m，**只表示兩張圖近似相合**，不是考古測地精度。Fig16自身50m尺讀作122px，與沿用尺度相差約2–2.4%；採點約±2px（0.8m），原單點錨絕對位置仍約5m以上不確定。既有Lanciani使用未改KML配準，OSM140264246是遺存輪廓；兩者都不能補足此處podium完整外邊的獨立測量。

以下皆在現Nerva錨`[12.486807,41.89348]`、`theta=−51°`的local米座標。**這些是圖讀控制點，沒有牆厚／孔洞／屋面語義，不可整表直接塞成實心prism。** 完整像素、經緯度及轉換見[measurements.json](imperial03_nerva_sources_measurements.json)；供主代理取用的兩翼線段、外包輪廓及前後y範圍另存[proposal.json](imperial03_nerva_sources_proposal.json)。

|要素|Fig16像素|現Nerva local(m)|
|---|---|---|
|西北翼接Augustus廊邊|417,192|−21.5,30.4|
|西北翼接廟側|449,185|−8.1,33.4|
|東南翼接廟側|496,185|11.6,33.4|
|東南翼接長牆|528,197|24.9,28.3|
|廟後西北角|451,138|−7.3,53.1|
|廟後東南角|493,138|10.3,53.1|
|前部西北／東南角|445,219／497,219|−9.8,19.1／12.0,19.1|
|台階最前兩角|445,229／497,229|−9.8,14.9／12.0,14.9|

圖讀後部`y=33.4–53.1`，後緣寬約17.6m、肩部約19.6m；前部`y=19.1–33.4`逐漸擴至約21.7m；階台前投至`y=14.9`。只是外包圖讀，不能把後部數值當成已量的內殿淨寬。本文59頁另述Minerva約22.5m寬，沒有在該句界定所量構件，不能用它硬套整座後部。圖讀廟中心相對現`[0,35]`只差`[+1.1,+1.1]m`，約1.6m；現廟中心與快取OSM遺存圖心約差3.0m，均在現配準誤差內，**不構成搬動整區的證據**。

## 最小資料修正與尚缺證據

- 保留主東南半圓；保留西南小座的具名清除，不擴大loss。
- 只重描Nerva北端：兩側長牆在上表翼牆接點收口，接到廟側；去掉現`y=50`橫穿廟後／半圓的整條矩形邊。兩翼要保留通口，不能把廟前封成橫牆。長邊突出柱列仍與完整portico分開處理。
- Minerva改為較窄後部與較寬前殿／階台的組合，依來源輪廓處理podium、承體及屋面，不能只把底座扣洞而保留穿入半圓的上構。現高13m、podium4m、柱高11m、15°屋面都是原估值，本件沒有新立面測量。
- **仍缺共同測繪控制及清楚區分cella牆、podium外緣的接縫詳圖。** Fig16半圓最外點比已准理想化橢圓內縮約1.75m；原官方圖也只是圖讀橢圓代理。直接採表內廟外包，仍與這個既有橢圓有約15.4m²未縮邊的平面交集（現矩形podium同算法約44.6m²）。這是來源輪廓／代理尚未統一的證據，不能把圖間殘差0.69m當成已解決，亦不能把15.4與交接的原生縮邊33.32m²直接相比。須先核清共牆邊及兩圖這1–2m差，再給可採用的完整native宣告；不建議為過檢查任意平移／截短。

交接所載339對359／360的兩宗原生碰撞，與上述兩種形制問題一致；本件未重新執行原生檢查，不宣稱已消除。97年精確拆除日、後部完整屋面與每段牆厚仍未知，不影響上述最小拓撲判斷。

留存：[PDF](model_reference/imperial03_nerva_sources_meneghini2015.pdf)、[Fig16](model_reference/imperial03_nerva_sources_fig16-000.png)、[接縫放大](model_reference/imperial03_nerva_sources_fig16_junction.png)、[Fig15](model_reference/imperial03_nerva_sources_fig15-000.png)、[FUR16a原件](model_reference/imperial03_nerva_sources_stanford16a.jpg)、[編目HTML](model_reference/imperial03_nerva_sources_stanford16a.html)。只供研究；沒有取得影片使用授權。測量可重跑`uv run --no-sync --offline python -I cities/rome/research/imperial03_nerva_sources_measure.py`；輸入hash及有效多邊形結果在JSON。未改模型、已准輸入或共用程式，未編譯／渲染／執行modelview。

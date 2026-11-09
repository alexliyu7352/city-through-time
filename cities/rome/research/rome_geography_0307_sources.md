# 03–07 地理與動作的來源

- 底圖：Natural Earth 110m land，公有領域。沿用 本機保留檔/ne_110m_land.geojson。https://www.naturalearthdata.com/about/terms-of-use/ 。本批原創地圖圖像採 CC BY 4.0；地理位置著色與方向箭頭是示意，不是精確古國界或行軍路線。
- 圖拉真疆域：UNC Ancient World Mapping Center 的 roman_empire_ce_117_extent，https://github.com/AWMC/geodata/tree/master/Cultural-Data/political_shading/roman_empire_ce_117_extent ，資料 ODbL 1.0，原始檔留在 geography_0307_sources/；Derived database 沿用 ODbL，圖像 CC BY 4.0。分裂地圖以其 CE200 外緣作粗略背景，兩種顏色只講東西地理分區，不冒稱395年邊界測繪；依 Procopius Wars III.1.2–17 的東西分掌地理。https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Procopius/Wars/3A*.html 。圖拉真地圖顯示其統治期最大範圍，不將版圖最大誤定為113年。
- 北非／埃及運糧、271入侵、330君士坦丁堡、402拉文納、535–554東羅馬收復、法蘭克支持、教宗國、查理五世、1849法軍、意大利統一：沿已核FACTS與定稿，不增加新旁白事實。著色只標大致位置；箭頭只表示運糧／進軍方向，沒有精確航線或軍事行程。
- 第二次火災：Tacitus Annals XV.40，https://penelope.uchicago.edu/thayer/e/roman/texts/tacitus/annals/15b*.html 。記火再起於Tigellinus的Aemilian財產，編者註明確址不明。將既有示意焚區的一部分保留到第二次起火，不聲稱該模型街廓就是考古證實的起火點；沒有新增具名起火點釘標。原有第一次火災、蔓延和防火帶保留。沿用原有焚區及保留區；第一次的 keep 再保留第二次起火的部分，第二次沿用原保留區。兩次互斥，不燒原防火帶；原生 for 清地仍補齊後續重建的工地。
- 金宮宮苑範圍：Padova／文化部TESS4957，Angelelli2008，https://tess.beniculturali.unipd.it/web/scheda-stampa/?recid=4957 。正文從Palatine、Velia到Oppio／San Pietro in Vincoli、Sette Sale、Servian牆、Celio／Claudius神廟，回到Palatine，包含Colosseum谷地。畫面邊界是上述地點之間的概括連線，角點是製作估值；不報面積、不冒稱地籍邊界，也不將宮苑整片重造為已考證宮殿。只畫原創輪廓，不複製該頁受CC BY-NC-SA約束的圖片。
- 410入城：羅馬文資局／UNESCO Museo Virtuale delle Mura，https://museovirtualedellemura.romasitounesco.it/pin/porta-salaria/ ，確認Salaria門及410入城、兩種開門傳說；門址在Piazza Fiume，模型對位仍為估值。原典 Procopius Wars III.2.14–24（同上連結）也記此門；不表演奴隸、背叛者等有分歧的細節。箭頭只過已知門址方向，不畫成沿途每條街的實際行軍，亦不虛構全城燒光。
- 1420後修復：沿FACTS中Martin V及教堂／街道修繕的既有來源。以既有教堂、街道上的順序掃光標明修繕示意，不造1420年的某次屋頂倒塌或宣稱某日完工，亦不讓1300年已存在的舊聖彼得消失重升。
- 可選人口比較：Colosseum照片沿CC0 Mattia.masala；不疊奧古斯都城界到1931年，因旁白比較的是人口，不是地理面積。

東西分治與拉文納採用放大字級、簡化標記的定位小卡；其餘新增遠方地圖為半屏圖，與模型變化輪流出現。西班牙與法國的輪廓取 Natural Earth 現代地理輪廓，只定位；神聖羅馬帝國和法蘭克人以位置標記表示，不畫虛構矩形國界。

410方向標記投影到已核可的城牆線上，保留真實門址與概括牆線的配準誤差；不新造破口。修繕光區用原生 landmark_site 取既有示例教堂用地，再轉向街道；這是修繕工作的示意，並不宣稱該教堂在1420年某日修完。


## 退件後的範圍補正（r2）

- 法蘭克：W. R. Shepherd《Historical Atlas》1926版第53頁（PD掃描）：https://commons.wikimedia.org/wiki/File:Growth_of_Frankish_Power,_481-814.jpg 。原圖分714–768年的擴張，故新圖只作8世紀中葉的大致勢力範圍，不聲稱756年逐段邊界已知。布列塔尼、薩克森及查理曼以後的意大利征服不塗入；箭頭表示武力支持的方向，不是一條考證行軍路。
- 初期教宗國：Dawczyk 2019按早期史料研究756年的Rome、Ravenna／Pentapolis與可能的Perugia，https://doi.org/10.12797/Politeja.16.2019.58.05 。以這些地方連成概括的兩部分與狹頸，角點均為製作估值；不把後來歷代聲索全畫成756年的實際控制。新地圖在r04_066到r04_068整句保留。
- 神聖羅馬帝國：IEG-MAPS Kunz《Reichskreise 1512》，https://www.ieg-maps.uni-mainz.de/mapsp/mapp512RKreise.htm ，研究用參考圖存hre1512_reference.gif；只按其低地、德意志、波希米亞、奧地利及帝國意大利的地理分布畫自製概括輪廓，不在片中複製IEG圖，不冒稱逐邦邊界或查理五世所有私人領地。西班牙與帝國分開著色。
- 1861年王國／殘餘教宗國：H. G. Wells《The Outline of History》1921第967頁地圖，https://etc.usf.edu/maps/pages/3600/3684/3684.htm （研究用原圖存italy1861_reference.gif），並核對LOC 1862地圖條目https://www.loc.gov/item/99466752/ 。王國不含Rome一帶殘餘教宗國和奧地利Venetia／Trentino；兩個外緣依歷史地圖概括、不是用今日Italy國界冒稱1861國界。Rome標在點旁，教宗國文字與其色塊相鄰。

這四張新圖（含Rome→Ravenna遷廷箭頭）沿用Natural Earth PD海岸底圖，自製著色與線條CC BY 4.0；歷史邊界是示意，原參考圖不入片。其餘新地圖逐張核對：運糧有來源地著色與海運箭頭；圖拉真、東西分治、意大利／東方帝國有範圍；北方入侵、西征、1849法軍有方向線；意大利統一有半島著色。表示靜態領地的圖不虛構遷移。

# 正式分期第一件早期地標：Livia西側房群

這是MODEL要求的先看形制小樣，不是已完成的AD14整城，也不是把113年宮殿改名成Augustus宮殿。原生modelview sheet把兩種檢視放在平地示範位置；尚未將此圖配準成整宅的原址足跡。

## 有據平面

PArCo提供的[Coarelli平面](https://colosseo.it/sito/wp-content/uploads/2020/11/CASAdiLIVIA_COARELLI_GUIDA.jpg)包含西側B空間、C/D/E後排房群、側房F和出入通道A；不包含整個東院。原檔970×1294px，5m比例尺圖讀約213px。外廓、各房空間、比例尺採點與檔案SHA見[livia_western_sample_plan.json](livia_western_sample_plan.json)。不把OSM較大遺存範圍的39.75×23.24m包圍矩形整填一棟房子；圖中北箭頭也不能用包圍矩形角度取代。

房間字母只沿這張官方圖，不混用TESS的字母。B可稱西側atrium／庭空間；C/D/E/F的功能在官方常用命名與DAR間有不同解讀，不以模型房名宣稱每間用途已證實。圖上的方痕不足以立出四根柱，也不證明B完全露天。

## 樓層與高度

[DAR](https://www.digitalaugustanrome.org/records/domus-livia/)區分西側舊房群與較高的東院，把Augustan增層放在東院周邊。[Padova TESS5023](https://tess.beniculturali.unipd.it/web/scheda/?recid=5023)的全宅兩層描述不能證明圖示西側四房整片都有兩層。因此這件只做圖示西側地面房群；不補東院、不把未知上層疊上去，也不因暫未畫上層就宣稱全宅只有一層。

[Carettoni發掘報告](https://bollettinodarte.cultura.gov.it/wp-content/uploads/Importer/1483435286830_04_-_Carettoni_189.pdf)，印刷191頁，記相鄰Augustus宅面具室5.12×3.45m、室內高3.10m。以這件同山、同期的小房作類比，C/D/E/F等小房外牆取3.6m，包含另估0.5m牆頂／承重餘量；不是Livia測繪簷高。剖開版的B牆頂3.6m是檢查切高，並非斷言原始梁下高。25°屋面與0.25m出檐採已審同期意大利住宅比較，均為估值；屋架、瓦件、門窗、壁畫及室內裝飾未復原。0.15m的B屋面出檐同為估值。

B的候選屋頂另外用[Vitruvius6.3](https://lexundria.com/vitr/6.3/mg)的同期理想比例作比較：中庭寬的3/4為梁下高、開口寬為中庭寬的1/4–1/3。以圖讀B短邊約8.5m，梁下高估6.375m，另加估0.5m構造餘量，模型牆頂6.875m；中央開口約4.0×2.84m。這些數字都不是Livia實測，僅令候選方案有可核對的同期比例；不能以Vitruvius反證B一定是這種屋頂。沒有將小房3.10m套給大得多的B。

## 兩種樣張的意義

- `Livia_west_B_roof_removed`：B屋頂剖開以核房群與中間空間的關係，不能拿這件證明B原本完全露天。C/D/E、F、A的屋頂同樣是形制估配。
- `Livia_west_roof_assumption`：另示一種同期比例假設，B屋頂較高，周邊屋面包著中央開口；開口尺寸、屋架與覆蓋安排並無此宅考古定論。這件是具體可審的估配方案，不把它混進「已知平面」欄，也不據此補四柱。

全部造型使用既有`prism`及`long_hall`，各部分由同一原生地坪承托；不自製網格、材質或檢視器。`make_livia_western_sample.py`只把保存的手描採點轉成原生配置，連接外側通道的缺口用源圖空間相減保留，不用無效的相切洞或假造封牆。

新形制先交樣張，確認之後才依[正式分期計畫](imperial_phasing_plan.md)處理原址配準、Augustus兩台地與完整早期整城。其餘地方的已知／估值／缺圖界線見[早期來源研究](early_imperial_layout_sources.md)。

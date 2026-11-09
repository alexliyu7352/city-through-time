# 12工作範圍內的尾段場域補證

接續已核細綱14a/14b與r14_01–02；不改任何旁白。Piazza Pia在2024-12-23已啟用，2025朝聖者使用此步行空間；不是GHSL的2025預測建築。2020與1975–2020生長窗口不顯示此新鋪地。原14研究文字、時序與來源均沿用；此補證只填先前未有工程平面的缺口。

## 原始來源

- P01：[設計者VIA Ingegneria工程頁](https://via.it/portfolio/piazza-pia-sottovia-e-nuovo-spazio-urbano/)，委託方ANAS／Comune di Roma，列約7000m²廣場，公開總平面、梯級平面／剖面、完成照片及效果圖。頁上2022–2025是專案期間，啟用日依S62與P02，不從上傳路徑的2024/09判定照片拍攝年。
- P02：[FS集團／ANAS，2024-12-23竣工發布](https://www.fsitaliane.it/it/media/comunicati-stampa/2024/12/23/giubileo-anas-ultimati-lavori-piazza-pia.html)。新步行空間與延長地下車道已完成啟用；不由這則文字推定地下構件精確尺寸或逐件施工時間。
- P03：[Roma Servizi per la Mobilità工程頁](https://romamobilita.it/piani-e-progetti/piazza-pia/)，更新2024-12-23；證實地面交通轉入地下、重新鋪地、照明、綠化與兩座中央噴泉。不從現況大道照片重建整場尺度。
- P04：[VIA總平面原圖](https://via.it/wp-content/uploads/2024/09/piazza-pia_-6.jpg)，原檔1920×1611，圖示1:500，存`model_reference/rome12_modern/pia2024/general_plan.jpg`。是設計圖，不聲稱竣工實測地籍。
- P05：[VIA梯級細部平面](https://via.it/wp-content/uploads/2024/09/piazza-pia_09_T00PS00ARCPL04A_Piazza-Lungo-Tevere-Vaticano-Pianta-di-dettaglio.jpg)，圖示1:100。用于核定南側並非一塊平坦矩形、原圖有階梯／緩坡。這輪只畫貼地公共鋪地，不另造階梯或地下箱體。
- P06：既有原生OSM快取`raw/cities/rome/osm/historic_07860ab2efab.json`之[way8035487](https://www.openstreetmap.org/way/8035487)，提供城堡四堡壘現代外框；不是2024新建年。配準控制用native register.fit_circle各擬合堡壘中心，四點在設計者底圖逐點對應。

P01–P05圖片只供建模研究，未取得上屏攝影授權。成片可使用有來源的白模幾何，不直接嵌入這些非CC圖片。來源bytes與SHA在`rome12_modern_tail_sources.json`。

## 每鍵basis

| 原生項目 | 依據與估值 | 限制 |
|---|---|---|
| grounds.region | P04紅線內主要步行面逐折點描圖，排除北側仍為車行下坡的矩形入口；現有建築輪廓外緣保留，沒有填成整片住宅地面 | 主要步行面輪廓，不是整個工程紅線／7000m²官方統計的完整重測。來源圖內小樹池及梯級細紋未逐一復原，不能給鋪地近距離材質特寫 |
| grounds.surface=paved | S62、P02、P03的已鋪砌步行空間；P04平面 | 土地用途，不是新建樓房。貼現有地形，沒有方形平台或抬高整場 |
| 兩座fountain的lon/lat、radius | P04兩圓各取四方位點，由native register/fit_circle得中心及直徑約8.37m | 設計圖估讀與配準誤差，非竣工測量；四點只用量圓，不把菱形當噴泉外形 |
| revolve.profile_m | 槽緣以圓環簡化；高0.45m、厚0.35m依既存S62近景及P01完成照片估讀 | 高與厚明列視覺估值，未取得槽緣斷面。沒有噴水、人物、人數或假施工動畫 |
| 兩圓的水，尺度省略 | P04及P01完成照片確認原圖有水；native register.fit_circle估讀直徑8.37m | 導演定案：1:10000只畫源位置／尺寸的revolve槽緣，不畫水。兩個pool已移除，不增新水表示；不是歷史乾池主張 |
| revolve.sides=64、exaggeration=1 | 64段為顯示精度，曲線保實際比例；不是64塊石料的史實 | 小件在全景讀不到；主要故事仍由廣場鋪地與大道／城堡關係承載 |
| site=cut | 槽緣在原地做小幅場地找平，不設方平台 | 地形為既有DEM／原生plate mesh，不宣稱重建地下車道或歷史絕對標高 |

register為similarity，不額外寫配準程式。四控制最大殘差2.62m、leave-one-out最大5.16m，已實看overlay逐件對回來源；這個尺度只適合場域形制示意，不宜稱公分級工程模型。來源圖與模型有據保留主步行通路和兩個圓形槽緣，沒有把畫面明暗或人口活動當工程證據。

聖天使堡、和解大道、聖彼得大殿／完整柱廊是已存建築，尾段需保留07與10的實址版本；本件不重建另一座大殿。2025聚集／2026聖門閉幕用原敘事與場域鏡頭；不讓同一實體沉下再升起。75公里PSO仍是規劃：沿用14的框內河線reference與明確Planned圖例，不把台面內可見河線稱整條75公里或已完工步道。

## 源圖主樹列補入

P04的沿河兩條主樹列與南北兩端樹群逐線描圖，使用native `trees.pts`／`n`／`offset_m:0`／`both:false`，共33個設計圖符號位置；沒有以`region`把整個廣場填成樹林。兩條沿河列13／10棵、北端3＋2、南西端3＋2，數量和路徑只表示源設計圖的主要樹列。小樹高4.5m、冠半徑1.6m是依P01的完成照片`completed_fountains2.jpg`中新增樹木與人／門尺度估值；不是竣工樹高普查，不宣稱樹種。native tree以通用樹冠示意，沒有把內建kind當植物鑑定。樹池、小坐凳及種植支架未逐件恢復，保持限制。

導演已定案尺度取捨：原圖與完成照片有水，但8.37m圓池小於1:10000全台面水遮罩約11.34m/texel；本件只保留原位、原尺寸的兩個revolve槽緣，不畫水，不增任何替代水表示。兩個kind:pool已從原spec及獨立study移除；33樹／6條pts及鋪地不變。8862f2c會提醒窄於一格的池，不再等待共享水面修補。舊round接口與162015取樣案均已結案，不阻塞正式接入。槽緣部分角度受既有DEM起伏遮少許，不能以clip0聲稱所有視角均完整。

# 08–10 r5 模型與場館補證

## S188｜Olimpico 的場址與看台分期

[羅馬市官方 Turismo Roma](https://turismoroma.it/it/luoghi/stadio-olimpico)正文核讀：1927年開始設計；1932年以 Stadio dei Cipressi 局部啟用；1950年重開施工；1953年5月17日以約十萬人規模開幕；1960年再調整。英文／意大利文分頁有1932／1937不同概稱，採意大利文完整正文，保留階段差別，不把1953整組看台說成1932建成。

1960畫面的大理石體育場（Marmi，1932）與相鄰Olimpico場址可一起承載法西斯時期體育建設的延續，但Olimpico隨前後兩句分別標「1932年場址」和「1953年看台」。Olimpico的1953觀察模型照原樣，未改成1990有頂版本。Flaminio（1959）、Palazzetto（1957）、游泳館（1960）在後一句才起，分別標年，不列入墨索里尼的建築。尺寸、原始圖版與年代詳原有 rome11_olympic_survey.md O01／O05。

1953看台的釘標指向來源中心向東45米、向南120米的東南看台；位於O01的319×186米外橢圓內、場地外。這是指示點的選擇，場館模型沒有移位。完整場景驗讀已確認離場飛行時不碰章名。

## S189｜Caracalla 存留遺構

[文化部官方條目](https://cultura.gov.it/index.php/luogo/terme-di-caracalla)核中央建築216年啟用及現存布局；[文化部文資部門的介紹](https://cultura.gov.it/comunicato/caracalla-aprono-al-pubblico-i-sotteranei-allestiti-con-i-marmi-del-complesso-termale)記存留上構局部高37米。本地已讀官方研究海報 `model_reference/rome11_olympic/caracalla_serlorenzi2026.pdf`／jpg，圖1現況照片與正文同樣記37米；不採圖2完整古代復原作1960外觀。

1960組委會官方報告卷一印刷79頁（本地 report_page078.txt）記體操臨設位於舊牆旁，支柱獨立於古牆；足以支持當時已有立起的遺構，並非只剩地面。原書217年與文化部216年有一年差異，建築標籤採文化部216年，並不改定稿旁白。

平面直接取已下載OSM historic_6fd6ac1c7675.json中的12個 historic=ruins、building=yes封閉way（不是整座遺址公園的外框）。原座標、way id和選定高度保存在 rome_tail_r5_caracalla_ruins.geojson；用共用 register.outline_landmark 轉原生prism，每段砌體各自落地，沒有自寫地理配準或繪屋工具。平面保留拓撲並簡化不超過0.15米，以省略低於影片像素的細碎折點。12、20、25、37米為依官方照片高低關係選的製作估值，37米是整個遺址的最高參考，不宣稱量得某個OSM way就是37米。牆頂、券洞、殘損輪廓省略；不補古代完整屋頂、浴池水面或2024年的新水景。畫面標為存留遺址示意。

遺構在1960場館鏡頭近看，與大競技場和奧勒良城牆同框；其後作現存遺構延續，不隨奧運臨建退場。其他既存古蹟按原模型／標記沿用，不以完整帝國浴場冒充遺址。

## 1577秒偶然外框

位置與 people_return 城的 rome06_medieval_stpaul（12.47688,41.85876）一致，是城外聖保祿大教堂的年代城外框，不是奧運標記。只改這一段的飛行途徑，保留已核可教堂模型。

# Quirinal：僅1871模型snapshot

根因是顯示倍率失配：原院23m、長翼18m、Fuga端21m皆固定×1；相鄰住宅是15m／18m×城市2，螢幕牆高30m／36m。另原院只有一件平頂有洞prism及8片2m立面承體，沒有四翼屋頂或Torrino。不是地址偏移，也不需墊高地基。

`rome_round11_models_patch.yaml`、`rome_round11_models_templates.yaml`由`rome_round11_models_build.py`產生。原院9 parts及長翼3 parts逐值保留，兩棟仍分離`site: cut`；只對1871新snapshot設×2，物理尺寸不變，1671模板不改。院檐23m×2＝46m；長翼檐18m×2＝36m；端部21m×2＝42m。屋頂仍用原生18°hip，不把房子抬離地。

四面翼樓各加一件原生hip屋頂，矩形完全內接原Falda外輪廓與院洞之間的四個翼帶；1m屋頂承體藏在原prism的22–23m頂層，不新添四件薄地基。四翼保原不規則院洞，不蓋平院子。後翼加14×12m、7m高的單層belvedere及7m寬、4m高的原生穿透鐘拱；兩者立於原23m樓頂，鐘拱頂物理34.8m（顯示約69.6m）。此為比例估值，不能當本棟測高或宣稱52m。

依據限定：

- [總統府宮史](https://palazzo.quirinale.it/storia/storia.html)的16–17世紀段，確認Mascarino的1583–1585 villa／Torrino、Fontana向廣場的翼樓及相對樓體、Ponzio園側翼、Maderno街側翼；沒有給測量高度。
- [官方虛擬導覽，西文PDF第1頁](https://palazzo.quirinale.it/visitevirtuali/doc/testi_audio_spa_nuovo.pdf)確認主院經四次建造、Torrino在院底原villa上；原為觀景台，17世紀初加鐘樓和時鐘。本輪只抽取這個輪廓，不加現代旗幟／時鐘細部。
- 既有`R09_continuity_quirinal_read.jpg`（Falda1667）可辨院、四側量體、坡瓦翼頂與後翼塔；Torrino寬用約3個既有4.38m比較窗跨取整14m，層高7m約為保留23m院體的三分一；這些都是圖像約束的量體估值。23m沿原R21 Caprini比較，不新編本棟高度。
- [官方Manica Lunga PDF第1頁](https://palazzo.quirinale.it/luoghi/pdf/it/imperiali.pdf)及[1866 Censo原圖轉載](https://www.info.roma.it/pianta_di_roma_1866_direzione_generale_censo.asp)的既有配準／351.303m軸／14m寬／18m翼身／21m端部照round10保留；未定年的王室加層不倒填1871。

`rome_round11_models_measurements.json`列物理高度與顯示倍率，原／新native bounds逐值相同。新增屋頂與塔均在舊院實體內；長翼平面不改，所以既有round10 reserve／宮園／街外民房不用重產或搬移。

整合入口包含`made_again.city.lose`只選舊院、1871節點的新院instance及長翼template替換。舊院作者是`made_again`，不能把loss加到住宅節點；既有Manica ID／stock stage沿用。這是1871觀察用模型交換，不是1871新建；交換需在宮殿近鏡之前完成，畫面不可表演宮殿拆建。原有default stage須排除另有專屬stage的新院。模型patch之外的readout／locator由staging處理。

原生study：`本機候選/rome_round11_models`（城市modelview目錄同名連結）。沿用round10已核留地的實際來源住宅；住宅／院與長翼分兩era，以免新landmark的apron悄悄清掉比高用的鄰屋。nice10／OMP2，原生675件院體＋塔／屋頂primitives；長翼沿原3 parts生成337件宮翼primitives。

`rome_round11_models_views_sheet.jpg`已逐張實看：220°／25°含現有民房比高，220°／40°含全351m長翼，40°／55°反向院與塔，310°／72°俯看四翼及院洞。院體不再是薄平板，四個屋頂、院口、後翼塔清楚；近景前方民房因透視可顯得更大，不能拿畫面總像素高當實際比高。原生group實測鐘拱頂69.6m、長翼端頂42m，符合各自物理高度×2；院檐46m高於鄰屋牆30–36m。研究sample沿用占位章標、locator，正式成片的文字避讓交整合者。

原生`build/logs/geocheck.log`每面向外；`clipcheck.log`兩era所有相撞／浮空／terrain_cut／tall_foundation皆0、cross_era0，`clipcheck: ok`。沒有改DEM、地址、site或墊高；長翼foundation top tenth由原23%降成12%，是同一地基對較高顯示牆的比例，不能說地基被改平。此無旁白研究study的compile有1項dead-air fault（兩段共7.5s）；它不是正式影片排片的通過結果，模型geo／clip已實際獨立通過，不重編全片消這項研究空白。

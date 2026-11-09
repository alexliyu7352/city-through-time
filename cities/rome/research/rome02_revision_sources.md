# 02地理panel與模型說明來源

本輪新增2段大panel地圖動畫，保留全部33條既有中英VO、全部城市模型、house types、stages/select及既有相機。未增VO、未做native compile/range；片上同時可見與5b遮擋仍須整合驗證。

## 公版底圖的實核

- 底圖是已存在的 `本機保留檔/ne_110m_land.geojson`，不是自畫海岸。
- 上游是Natural Earth共同作者Nathaniel Vaughn Kelso維護的 [natural-earth-vector GeoJSON](https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson)。本輪實際下載後與本機檔逐位元相同；兩者SHA256都是 `9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9`。
- [Natural Earth官方授權](https://www.naturalearthdata.com/about/terms-of-use/)明示全部版本vector/raster在public domain，允許修改及商業使用。並非只在自製credit上自行宣稱公版。
- SVG沿用既有 `rome_restart_document_cards.py` 的字型outline方法及專案字型；新地區wash、地點pin、動畫路線與版面為本專案製作。Pillow僅繪製地圖動畫，沒有修改IP02或其他既有圖片。

## 地理與敘事的限制

意大利半島與地中海定位沿用既有底圖和FACTS S28／`rome_restart_ancient_sources.md` A05；上色與方向皆明標SCHEMATIC / APPROXIMATE。意大利色塊是概括半島定位，不是羅馬佔領的精確國界。地中海以底圖陸地相減後的海域上色，不畫一個年份的領土邊界。007–010向外箭頭概括擴張；011另清除向外箭頭，改為糧食／貢賦／戰利品向Rome流入。

高盧對今日法國的概括對照、凱撒高盧戰爭與49 BCE跨Rubicon的敘事，沿用 `rome_world_ancient_sources_20261101.md` WA04與已批准原VO。高盧色塊是手工概括的地域wash，未使用現代法國邊界，未宣稱古高盧的精確疆域。

Rubicon只定位在現代Savignano附近的河流地域，沒有重建古河道、渡河點或軍隊行軍路：

- [意大利文化部Rubico flumen遺址條目](https://catalogo.cultura.gov.it/detail/ibc/ArchaeologicalProperty/262091)把古記載與現Rubicone相聯，並說明流至Gatteo Mare與Savignano之間的亞得里亞海。
- [官方區域旅遊網站Visit Romagna：Savignano sul Rubicone](https://www.visitromagna.it/en/towns/savignano-sul-rubicone)記當地Rubicon橋、所在地與向Rome進軍的傳統敘事；不採它對古橋穿越的精確認定。
- [意大利官方旅遊網站Italia.it：Savignano sul Rubicone](https://www.italia.it/en/emilia-romagna/savignano-on-rubicone)原頁JSON-LD公開座標是latitude `44.0936826`、longitude `12.4007392`。動畫採四捨五入的 `[12.4,44.1]`，只作河流地域定位。不是任意編造的點，也不是精確古代渡河地點。
- 藍色短劃只是河流地域的圖示，不是地理測繪河線。Gaul→Rubicon→Rome的直線是概括方向，片上標 `Direction only · not an exact march or crossing point.`。
- Civil war用 `Caesar's forces ↔ Roman opponents` 與 `Romans against Romans` 的抽象政治關係。沒有新增對手軍隊的真實坐標、交戰地點、戰術路線或年份。

## 原圖IP02

`assets/imagined/restart_ip02_caesar.png` 保持原檔，SHA256 `25cc0b75ef56f5ab5d069f6855089835e884212d6bda4ad312b484c1bec44ba8`。圖像是3人抬屍、垂臂，並非圍刺；panel標 `IMAGINED · AFTERMATH · 想像图 · 刺杀后果` 與 `After the assassination / 刺杀之后`。來源與完整prompt沿用 `rome_restart_generated_pictures.md` IP02。本輪沒有裁切、重生或改動原圖。

原生panel用cover，直接放16:9原圖會裁掉邊側人物。沿用本專案既有完整入框方法，新增 `rome02_ip02_aftermath_panel.svg/.png` 素材排版容器：完全沿用既有Campo Vaccino／洪水文件容器的3600×3600畫布、8%安全邊（288）、3024×3024內容框與中性紙色 `#e9e2d2`。SVG的image內嵌**逐位元相同**的原PNG，以 `preserveAspectRatio="xMidYMid meet"` 完整入框；不裁人物、不補畫、不生圖、不修飾原圖。PNG是容器的Inkscape輸出，patch引此包裝素材，原素材仍留原路徑。3名抬者與垂臂均保留；最後仍需實際native panel與字幕同框驗證。

## 模型短標籤

509城市與160、44城市觀察態：沿用FACTS S28、S149–153、`rome_world_ancient_sources_20261101.md` WA03與原city各模型basis；住宅仍標估算。509 readout改白話 `Rome · 509 BCE (traditional) · housing estimated / 罗马 · 前509年（传统说法）· 住宅估算`，明示509為傳統說法，沒有把推測年代變成測定城市斷面。原模型依據與不確定性仍全保留。龐培建築群前55年起、議事廳定位沿用 `rome02_pompey_refine_sources.md` P01–P05與原model landmark。公共重建沿用既有civic模型basis：Curia Julia前29奉獻、Palatine Apollo前28奉獻，28–27是並列觀察態，未當作所有建築同年完工。Regia前36火災、Apollo前34後重建、Ceres/Spes前31火災，完全沿用原native loss IDs及來源年，日期pin用原有year timing，不歸因於27年的政治授號。

## 可重做與交件

資產producer：`research/rome02_revision_assets.py`；patch producer：`research/rome02_revision_patch.py`。使用現有Inkscape、fontTools、Shapely、Pillow、FFmpeg，無新依賴、無engine/compile變更。

正式輸出在 `assets/restart_sources/rome02_*`：2段H.264/24fps影片、5張地圖SVG與其PNG、7張動畫關鍵frame，另有1張IP02排版容器SVG與其PNG。21秒G1/G2片段綁007起點，包含011向內供給；23.3秒G3/G4片段綁017起點並跨Pompey/late節點。動畫內12fps繪製、輸出24fps；是示意圖的逐步點亮／畫線，並非真實軍事footage。G4的Rubicon標籤已移到河點右上方並加leader；第一腿158.05–163.40先到河（早於163.45），第二腿164.1–168.6再到Rome，沒有同時畫兩腿的錯覺。

patch僅15–20KB，不是整個城市副本。每個node.set欄位附原field SHA，arrays保留原項（只替換舊過晚的小地圖card），附33條原VO逐字清單及整體hash、所有republic city欄位hash。原生重編後須另核source-period大年份、節點始末、33cue、native模型全保留及畫面遮擋；本來源文件不冒稱已通過。

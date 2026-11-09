# 1953 Cinecittà全廠交付

由批准三棚擴至1953總圖完整功能廠區：**16個不同尺寸攝影棚、管理／製片、剪輯／洗印、工場／材料庫、入口園庭、54攝影池與西側職工球場**；共73個地標、70項通路／場地線、15個來源植栽區、1176件原生primitives。北／西無據寬soil矩形已撤，開放生產地保留未建地形；70按原圖描橢圓跑道、主場界／中線／兩端門區，無看台。

**批准90件全部逐值保留**，只忽略原生rise rank；25個原trace項（含19通路）亦全部相等，缺失0。新native freeze/check、最終modelview、eraview、rangecheck、sheet及收據程式均實際exit0；native geo／clip各適用項全0，含碰撞、缺面、浮空、地形穿入、鋪面埋地、水面穿地與高基礎。最終四圖、兩look各36視角、原圖三區覆圖及range拼版均已實看，未留可見高台、缺面或斷路問題。

所有指定圖為**study 00:06.61**；短range為00:06.61–00:08.61。畫面1954／1955是1953–1959年線插值，**不是建造年，也不是正式片秒數**；正式10尚未合併。range YAVG71.1照錄，readcheck對越出短區段的讀表未判，不冒稱完成正式成片亮度／字幕驗收。

| 審查項 | 完整路徑 |
|---|---|
| 15°棚群近景 | `build/review/modelview/rome10_screen_whole_inputs/build/review/modelview/rome10_screen_whole/1_6.61.jpg` |
| 15°主入口／生產軸 | `build/review/modelview/rome10_screen_whole_inputs/build/review/modelview/rome10_screen_whole/2_6.61.jpg` |
| 棚群、配套與開放地 | `build/review/modelview/rome10_screen_whole_inputs/build/review/modelview/rome10_screen_whole/3_6.61.jpg` |
| 全廠／球場遠景 | `build/review/modelview/rome10_screen_whole_inputs/build/review/modelview/rome10_screen_whole/4_6.61.jpg` |
| 四圖拼版 | `build/review/modelview/rome10_screen_whole_inputs/build/review/modelview/rome10_screen_whole/sheet.jpg` |
| 1953逐號／道路／綠地覆圖 | `research/model_reference/rome10_screen_whole/1953_overlay.png` |
| 建物外框專圖 | `research/model_reference/rome10_screen_whole/1953_buildings_overlay.png` |
| 成片look全向 | `build/review/modelview/rome10_screen_whole_inputs/build/review/modelview/rome10_screen_whole/build/review/eraview/screen_rome_at6.61_film.jpg` |
| 檢查look全向 | `build/review/modelview/rome10_screen_whole_inputs/build/review/modelview/rome10_screen_whole/build/review/eraview/screen_rome_at6.61_check.jpg` |
| 短range拼版 | `build/review/modelview/rome10_screen_whole_inputs/build/review/modelview/rome10_screen_whole/build/review/range_6.61_8.61/sheet_00.jpg` |
| 原生geo／clip／compile logs | `build/review/modelview/rome10_screen_whole_inputs/build/review/modelview/rome10_screen_whole/build/logs/` |
| 命令、exit與SHA收據 | `research/rome10_screen_whole_receipt.json` |
| 90件實比 | `research/rome10_screen_whole_preservation.json` |

來源為1953原刊PDF128圖例／129總圖，沿已核native配準；新棚長寬逐棟圖讀，上構／10.5與12m檐高、低配套4／8m及工業6m均是1937具名同類比較估值。中央5及批准15／16、兩服務樓與21／22／60未改形。約15m絕對定位工作量級、20.98m入口留一誤差與遠端未量化圖紙外推分列，不稱測地實測。

明列的來源／原生界線：53水塔上部不可讀，沒有實心塔或假基座；50／56／57／67尚不能在圖上可靠對位，保留清冊未復原；51僅溫室外殼，新棚未核的門窗／鋼桁架不復原。原生沒有任意多邊形貼地soil地表項，因此北／西開放地只以來源用途點／通路及未建地形表示，沒有虛造矩形鋪地或假池。54採原生dug pool，water_under_plate0，沒有無據banks_m。全廠outline為功能覆蓋窗，西北缺線銜接不當法定廠界。

原生輸入是`research/rome10_screen_whole_spec.yaml`、單一`rome10_screen_whole_trace.geojson`及`rome10_screen_whole_templates.yaml`；library在獨立`rome10_screen_whole_inputs/city.yaml`登記。逐號1–71採用／排除與估值見`rome10_screen_whole_sources.md`，原生用地、道路R編號及逐件像素見`rome10_screen_whole_catalog.json`。FACTS增補僅寫`rome10_screen_whole_FACTS_proposed.md`；正式city／script／FACTS／TREATMENT／film與shared未改。

# 08首件交付：調查＋待審原生房型表

接續狀態：兩型已批，Braschi—SanPantaleo原生一區亦已通過；最新核可圖／限制見`rome08_capital_window_basis.md`。以下是保留的第一輪交付，不表示整城仍停在房型待審。

完成本件的來源調查與兩個新房型提案；停於導演確認前，未鋪歷史街坊或整城，未修改正式city／script／TREATMENT／FACTS、影片與共用程式。研究與圖的秒數皆為獨立study，不是正式08站時間碼。

## 審查入口

- [調查與具體來源](rome08_capital_survey.md)：1866全圖、1849／1870／1871版本、街坊／空地、人口口徑、下一樣區與缺口。
- [兩型逐鍵形制與估值](rome08_capital_housing_basis.md)，輸入[原生sheet YAML](rome08_capital_sheet.yaml)。
- [原生房型表](../build/review/modelview/rome08_capital/sheet.jpg)，實驗時刻**00:04.65**；兩型近景12°、d0.045、fov42，總覽20°。這不是原址、密度或兩型各半的歷史配置，外圍灰色為現代參照底模。
- [已開始的固定距離10圖合頁](../build/review/modelview/rome08_capital_views/contact.jpg)：兩型四向12°、一張35°看院與屋面、一張30°總覽。資料[views YAML](rome08_capital_views.yaml)抽自原生sheet生成的city，沒有改住宅幾何。
- [變化資料](rome08_capital_changes.json)、[FACTS候選](rome08_capital_facts_proposed.md)、[工具問題最小記錄](rome08_capital_tool_note.md)。

首件可以審三層街屋的連續街牆／後園及三主要外層宮邸的院形與尺度差。Palma比較的原生四翼均高，與來源兩層院廊不完全相同，**不能當Palma精確復原**。屋面、等高樓層、簡化後院及名義地塊均見basis；沒有把古代房型清單換成年代標籤。

## 原生實跑與日誌

```sh
uv run --no-sync --offline python -I tools/modelview.py cities/rome rome08_capital --spec cities/rome/research/rome08_capital_sheet.yaml --year 1871 --sheet --at 12.45,41.84 --name rome08_capital
node tools/eraview.mjs cities/rome/build/review/modelview/rome08_capital --eras rome08_capital
```

上述兩個程序實際exit0。最後sheet是在修正原圖平面尺為0–12m、將名義地塊取整為14×26m／27×37m後重編；同目錄`4.72.jpg`是舊尺讀版，**本件只審4.65版**。最後兩次study都編出466構件，沒有拿初次舊圖當最終結果。

| 範圍 | 原生結果 | 日誌 |
|---|---|---|
| `rome08_capital` | `geocheck: every face points out of its piece`；466構件 | `build/review/modelview/rome08_capital/build/logs/geocheck.log` |
| 同上 | houses_vs_walls／houses_vs_streets／walls_through／today_vs_era／floating／terrain_cut／water_under_plate／paving_under／tall_foundation **全部0**，today floating0；地基最高十分位0% | 同目錄`clipcheck.log`及`clipcheck.json` |
| `rome08_capital_views` | modelview程序實際exit0；同466構件，面向正常及上述各項0 | `build/review/modelview/rome08_capital_views/build/logs/` |
| 原生eraview | 程序exit0，film／check各一張合頁已實看 | `research/rome08_capital_eraview.log`；sheet study下`build/review/eraview/` |

完整命令輸出為`rome08_capital_modelview.log`、`rome08_capital_views.log`；10圖合頁是既有圖以原生`tools/sheet.py`排版，exit0，記錄在`rome08_capital_contact.log`，沒有新增渲染或改圖內容。兩study的compile內都明示model study而非正式片；1871不是今年與無旁白空段是此實驗用途的預期提示，不作正式影片通過證據。

自動eraview的12°／35°近景對此小而高的樣表會裁切，只可判局部表面，不能冒稱所有面已完整入鏡；詳工具記錄。已開始的固定450m補圖10張均看過，3／7等背向圖受到現代參照樓遮擋，未為此再改共用隱藏規則或追加拍圖。eraview關閉today的後向／側向圖可對照連續後牆，35°固定補圖可辨屋面與院形。**各項幾何0不等於來源形制已批准。**

## 實看來源及圖片

1866 Censo2400×1813全圖與東北局部；Letarouilly前16頁、73張後續非空白縮圖、plates1／2／11／14／22大圖及兩個比例尺裁圖；內政部原PDF20／22／23頁平面；Tuminello AF3328低解析度1870全景；最終sheet兩張1920×1080近景與合頁；eraview兩種look合頁；固定距離10張合頁。原來源、瓦片清單、雜湊與抓取失敗記錄保存在`research/model_reference/rome08_capital/`。

## 接續與限制

下一樣區選**Braschi—San Pantaleo開Corso以前的一個連續街坊**：有1871用途和平面、有鄰接宅群，直接承載政府遷入舊城。1870Porta Pia近門園地本來稀疏，不為示範住宅而填成後來首都密區。河牆工程延伸到1876以後及二十世紀，1871快照不能全線先建好。

本次房型待批准；下一街坊仍缺原地籍的配準回描、相鄰普通宅層數／商舖抽樣，城牆段仍缺Porta Pia雙門與破口尺寸、1849 SanPancrazio原門／戰損原圖。洪水若演面域，另需已淹圖與水位；後續河牆需選實際有年代的一段。未取得來源影像上屏授權的，只供研究。沒有改旁白、沒有安排step5正式鏡頭、沒有聲稱08或整片已完成。

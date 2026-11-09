# Rome05首件交付檢查

## 交付界線

本件有410–537來源調查、逐區物理狀態與估配規格，及一個**未落位、剖開的磨輪單元比較**；沒有整城、連續住宅樣區、537實址磨坊或正式05鏡頭。下一區選Regola，仍須專址尺度／古街配準。首形制待導演審看，不能視為獲准擴城。

主要文件：

- `cities/rome/research/rome05_sack_survey.md`
- `cities/rome/research/rome05_sack_form_basis.md`
- `cities/rome/research/rome05_sack_facts_proposed.md`
- `cities/rome/research/rome05_sack_sheet.yaml`
- `cities/rome/research/rome05_sack_make_sheet.py`
- `cities/rome/research/rome05_sack_fetch.py`
- `cities/rome/research/rome05_sack_source_receipts.json`
- 原文／原圖：`cities/rome/research/model_reference/rome05_sack/`

## 實際來源檢查

`rome05_sack_sourcecheck.log`：18項HTTP200／正常退出的原檔，3項失敗入口，成功檔SHA-256不符為0。失敗為SA12／17／18；SA12及18由瀏覽原正文核讀，SA17改以SA21同一Dewing公版譯本核讀。沒有把HTTP200但0bytes／逾時當正文。

已實看來源圖：SA02有尺合成平面、SA05西北機構細節與總覽（對應收據SA19／20），SA08 PDF2館方照片／分期說明。SA02是現代調查／Lanciani粗套合；1999模型明說輪數、木構有假說。這些圖未放進正式影片。

關鍵修正：Academy出土棟約400年已停磨；537在用者是下游其他磨坊。Regola猛烈火災早於410；Gaudentius宅至少住到5c中葉；455取屋面不等於沉整廟；537仍有井／河水。全部對應調查與FACTS提案，不改已確認旁白。

## 原生工具與修正紀錄

第一版`rome05_sack_sheet`的native geocheck／clipcheck通過，但標準距離只看見小機件，且537標題容易誤認實址年代，因此不是推薦審圖。保留原始日誌`rome05_sack_modelview.log`作歷史記錄。

第一次細部`rome05_sack_detail`因本件`hide`少一層ring列表而編譯失敗；這是輸入錯誤，已修正自己的資料生成器及YAML，沒有改共享程式。提前啟動的eraview又因該study沒有film.json而退出；`rome05_sack_eraview.log`保留失敗，不能當成功證據。

最終資料將近側槽壁剖切到.65m以看見輪體，此為展示切面，非古壁高度；不改遠側工作層及來源輪徑。最終研究年改350，表示3c建成至約400停用之間的比較觀察年；不是350新建，也不是變更正式05年代。

最終native sheet命令：

```sh
uv run --no-sync --offline python -I tools/modelview.py cities/rome rome05_sack_mill_comparison --spec cities/rome/research/rome05_sack_sheet.yaml --year 350 --sheet --at 12.478,41.903 --name rome05_sack_sheet350
```

`rome05_sack_sheet350.log`及其`build/logs/compile.log`：geocheck每面向外；67構件；clipcheck適用項均0、today floating0、實際高地基0。這是平地實驗室形制，不是Janiculum坡地驗收。末站不是2026、無旁白dead air及文案建議均屬單件無聲研究片的預期提示，不作正式片通過。全域1:10000、地形×2與現代高度×3未動；機構整件倍率1以保持輪形。

## 完成與可審圖

`rome05_sack_detail350.log`：修正後原生編譯、geocheck、clipcheck通過，2.50s定格時本體已於1.4s完成升起。已逐張實看：

| 圖 | 看到什麼／限制 |
|---|---|
| `build/review/modelview/rome05_sack_sheet350/sheet.jpg` | 標準native sheet，四向及總覽；小機件在預設距離仍細小，只供完整性，主審看下列細部。 |
| `build/review/modelview/rome05_sack_detail350/1_2.50.jpg` | az300、12°、d.004；可辨直立輪圈、槳板、切面槽壁及上方磨石，作首要近景。 |
| 同夾`2_2.50.jpg` | az120、12°、d.004；遠側牆遮輪，工作層與石磨仍見；不能以此方向單張驗輪。 |
| 同夾`3_2.50.jpg` | az210、30°、d.004；可同看輪、槽、旁側工作層與磨石，是最清楚的機構層次圖。 |
| 同夾`4_2.50.jpg` | az30、30°、d.004；核另一面支柱、平台與輪圈位置；沒有把左右顛倒。 |
| 同夾`5_2.50.jpg` | az300、12°、d.045的常用街坊近景距離；單輪小到不可辨。這是明確可讀性限制，不靠加倍機件尺寸假裝真實比例。 |

d.004是只審小機件的實驗室距離，**不是已批准的城市低角度鏡頭**；不以它替代未交的連續街坊10–15°及遠景。最終sheet的350標題是比較觀察年，正式05仍是410／537。所有圖均由原生modelview產生，未改調色或鏡頭共用程式。

細部原生日誌：`build/review/modelview/rome05_sack_detail350/build/logs/compile.log`、`geocheck.log`、`clipcheck.log`及`still_1.log`至`still_5.log`。適用穿模項、today floating與高地基均0；平地比較不能證坡地也通過。

## 全向巡檢實際結果

```sh
node tools/eraview.mjs cities/rome/build/review/modelview/rome05_sack_detail350 --d .004
```

`rome05_sack_eraview350.log`正常完成；geocheck為65構件，兩種look均在研究片1.45s檢查，此時本體已升起。下列兩張均已實看：

- `build/review/modelview/rome05_sack_detail350/build/review/eraview/rome05_sack_mill_comparison_film.jpg`
- `build/review/modelview/rome05_sack_detail350/build/review/eraview/rome05_sack_mill_comparison_check.jpg`

另開check的`check_landmark1_el30_az300.jpg`和`check_landmark1_el30_az120.jpg`原尺寸核輪側／平台側。輪圈、槳、軸及側壁保持實體；沒有發現可見反面消失。東側壁／平台擋輪屬剖切方向的遮蔽，沒有為了每方向看輪而拆掉整體支承。

**原生巡檢的限制另報主代理：** 本件只有一個很小的landmark、沒有住宅。eraview的住宅近景兩排沒有對準這件；landmark列與整體列能看到，但其最小d.012使接觸表上的機構細小。這兩張全向表不能替代上列d.004原生modelview細部。`bundle.json`404為有fallback的optional-file提示，圖已生成，不是本件下載缺口。詳`rome05_sack_eraview_issue.md`，本件未改共享工具。

## 本件停止點

18原檔雜湊驗證、最終兩次modelview和全向巡檢均已完成。首形制可供審查，**未批准**；沒有交整城或537實址。最直接缺口是537下游在用磨坊的坐標／平面；可以先做明標山坡功能示意，不可用Academy已停磨棟冒名。連續Regola街坊還需專址有尺平面及古街配準；不以此缺口擴大研究至下一期。

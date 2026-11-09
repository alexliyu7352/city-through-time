# Rome r15 封面交付／導演審閱用

狀態：兩方案、英文／簡體、橫／直式共 8 張母版及 8 張 320px 縮圖已完成。尚未發布、寄信、設為 `dist/poster.jpg` 或變更 approved14g 的影片／來源。

## 檔案

- 全部成品：`cities/rome/assets/covers/r15/final/rome_{A|B}_{en|zh}_{wide|portrait}.jpg`
- 對應手機縮圖：上述檔名加 `_320.jpg`；橫式 320×180，直式 320×427。
- 一次看完 8 張的實際 320px 對照：`cities/rome/assets/covers/r15/review_320_contact.jpg`。
- 排字文字、墨跡邊界、安全範圍、生成原尺寸：`final/layout_manifest.json`。
- 原始白模參考與片內輔助圖：`refs/`；6 次生成原圖（包括棄用修正版本）：`generated/`。
- 每次實際提示詞與生成原路徑：`research/rome_cover_prompts.json`。
- 引用來源、原圖／成品 SHA256：`assets/covers/r15/provenance.json`。
- 可重現排字：`nice -n 10 uv run python cities/rome/research/rome_cover_layout.py`。

## 設計

A「自然建城地景 × 亮燈白模」：左為想像的橄欖綠草坡、自然河岸、僅六間草屋；右接現代象牙白城市模型與金色街燈，鬥獸場保留開放 arena、拱廊及殘存高外牆。時間接縫在草屋東側的陸地，河流不是時間分界。

B「兩時代白模 × 想像氣氛與生活質感」：兩邊都明確使用象牙白微縮建築／地形，左側白色草屋與淺色雕塑丘陵疊半透明植被、藍影、薄霧；右側金色亮燈白模。與 A 的差別是模型本體和地表材質，不只改色調。

直式由內建 imagegen 另作 3:4 重構／延伸，上方保留深藍文字區，下方完整容納河彎、河島、東岸草屋與鬥獸場；沒有把橫圖中央裁成直式。

## 白模攝影與地理確認

白模基線：`cities/rome_round14g_all/build/film.json` 與其 `build/data/model.json`。只建立私有 `research/rome_cover_study/build/film.json`，設定 `drift: 0`、`living: []`、`footage: []`、`prologue: null`；data/assets 連結回原基線，沒有改寫。使用專案 `render/page.mjs` 的 `openFilm()`、`window.render(t)`、`shot()`，1920×1080 PNG、原生 Chrome WebGL。沒有跑 full compile、完整 checks 或影片 render。

以 `cam=tx,ty,tz,az,el,d,fov` 固定相機；753 和 2026 使用同一機位。正常 night 留在 film 中，沒有使用會關 night 的 `clean`，僅以 CSS `#ov{display:none!important}` 隱藏全部 overlay。四張 still 完成即關瀏覽器，已通知主線釋放機器，後續沒有 GPU 拍攝。

| 參考組 | 相機參數 | 753 BCE 秒數 | 2026 秒數 |
| --- | --- | --- | --- |
| cam01（兩方案主要幾何參考） | `-0.135,0.012,0.105,0,48,0.29,42` | 60 | 1785 |
| cam02（補看較低視角及較亮 night） | `-0.135,0.012,0.105,70,28,0.25,42` | 60 | 1770 |

兩個現代時間點在原 yearline 均為 2026。cam01 深夜原圖較暗；AI 增強白模可見度時保留藍河／金燈節點色。

沒有靠灰圓盤猜鬥獸場。由 model 的 EPSG:32633、`crop_utm=[281011.32705384545,304238.9226320042,4630601.598837093,4652809.30608017]`、scale `0.0001`，以 pyproj 從經緯度投影至原生模型座標；x 用 UTM 東向減中心，z 用中心北向減 UTM 北向。用同一 Three.js 透視相機確認：

| 地標 | 經緯度 | 原生 x,z | cam01 螢幕點 | cam02 螢幕點 |
| --- | --- | --- | --- | --- |
| Colosseum | 12.4922, 41.8902 | -0.0679131, 0.1078855 | 1281.8,572.8 | 1104.7,799.1 |
| Palatine | 12.4873, 41.8893 | -0.1088605, 0.1166889 | 1088.0,605.4 | 947.4,660.8 |
| Tiber Island | 12.4770, 41.8904 | -0.1939601, 0.1019656 | 681.0,551.5 | 879.6,445.7 |

螢幕點用地面 y=0.005 作地標定位，非屋頂或建築輪廓的逐點量測。成圖維持河／島在左、Palatine 草屋在河東岸、鬥獸場在右的關係。

額外參考：片內 `assets/living/rome_round12_founding_legend.png` 僅提供草屋／草坡材質；片內 `assets/restart_sources/ph03_colosseum_mattia_masala_2024.jpg`（CREDITS: Mattia.masala，2024-10-31，Wikimedia Commons，CC0 1.0）提供現存外牆及拱廊識別，不套用其地面拍攝機位。

## 實際工具與生成修正

使用 Codex 內建 `tools.image_gen__imagegen`、local `referenced_image_paths` 編輯模式，共 6 次。每張本地參考皆先經 `view_image` 檢視。沒有使用 API、CLI、模型替換、Python 自造景物。實際工具回應沒有模型識別碼，因此不聲稱特定模型版本。

A 初稿把草屋放錯河岸，第二稿仍有古側現代樓；兩次針對性修正後才選用 A_wide。棄用原稿仍保留追溯。A/B 最終白模與自然地景均屬 AI 處理，不應宣稱完全逐像素保留模型。城市街塊、植被和丘陵細節有生成漂移；沒有把本圖當考古測繪。已保留片內真實城市與地標關係，未加入公元前753年的帝國紀念建築。

原生 imagegen 橫圖為 1672×941，直圖 1086×1448。交付橫式以 Lanczos 放大至指定 3840×2160，直式縮至 1080×1440；4K 是交付畫布尺寸，並非宣稱 AI 原生產生 4K 細節。

## 文字與檢查

- 英文：`ROME`、`753 BCE → 2026`；角落標記 `A City Through Time`。
- 簡體：`罗马`、`公元前753 → 2026`；角落標記 `一城春秋`。
- `fonts/Cinzel-VF.ttf` 900 作英文主標；`InterTight-VF.ttf` 850 作英文日期；`NotoSansSC-VF.ttf` 900／850 作簡體標題／日期。以陰影和深藍描邊維持手機可讀性。
- 使用 Pillow 僅作指定畫布尺寸、專案字型精準文字疊印、縮圖及審閱拼圖，沒有用 Python 繪製或重造景物。
- 排字腳本已完整執行：8 母版、8 縮圖；每個文字墨跡 bbox 逐一驗證。橫式所有文字均在 x=480..3360 的中央 4:3 範圍內，主地標也經畫面檢視落在此範圍；直式無文字／鬥獸場裁切。
- 另逐檔讀取影像確認尺寸與數量，保存雜湊。已用 `view_image` 看過包含全部 8 張實際 320px 縮圖的對照 sheet：兩語主標及日期可讀，河彎／河島與鬥獸場可辨，A 的自然地景和 B 的白色模型清楚區分；未見錯字、額外大字或浮水印。

待主線／導演視覺審核後決定使用版本；本交付未改寫 `dist/poster.jpg`。

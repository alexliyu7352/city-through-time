# 出片與交付

## 這一步最常犯的錯

- 漏了簡介、沒清元數據 → 兩樣跟影片一起交。
- 成片太暗 → 出片前量全片亮度，過門檻才交（CHECKS.md「亮度」）。
- 回報了混音的響度 → 取成片量到的數字。

## 出片（用戶在預覽裡點頭之後才做）

`node tools/build.mjs <slug>`（已有資料時加 `--no-data`；已渲染影格時加 `--no-video`）。
`tools/build.mjs` 寫出的 `dist/poster.jpg` 是片中一格的佔位圖；正式封面在發布時做（PUBLISH.md「封面」）。
出片一併交**簡介** `dist/description.md`，片子的語言各一份：
一句話、短簡介（社群貼文）、長簡介（影片平台）、章節時間（取自 `build/export/timeline.json` 的節點；第一個 0:00，每章至少 10 秒）、
怎麼做的與出處授權（CC BY / BY-SA 的作者要寫出來）、AI 生成聲明、作者署名。事實只用旁白和 FACTS.md 裡有的。
交出去的檔案**不帶元數據**：`render/mux.mjs` 合成時就不寫 encoder 標籤、章節和其他 metadata，去掉 x264 寫在影像裡的
參數（只移除 SEI），AAC 不寫 Lavc 字樣；封面用 bitexact 寫出，沒有編碼器註記。手上的舊檔要清：`exiftool -all=`，再用 `strings` 確認。
build 會跑 subcheck、clipcheck、camcheck、readcheck（含：文字不得壓在字幕帶上、兩段文字不得互疊）、motioncheck、黑幀檢查、響度（−14 LUFS）。
全片檢查就在這一步跑，跑之前先問用戶現在能不能佔用電腦。平時只跑了受影響的站、但全片都會動的改動（地形、字型、全片的時間軸），
當時就記下「出片前要跑全片」，到這一步一起補。全片的亮度也在這一步量，門檻見 CHECKS.md「亮度」。
回報的響度、峰值取 `render/mux.mjs` 量的成片數字，不是混音的（兩者會差零點幾 LUFS）。
motioncheck 報「像剪接」時抽幾格看是壞格還是鏡頭轉得快；後者回報用戶，要不要放慢由用戶決定。

## 交付

告訴用戶檔案位置，提醒 CREDITS 列出的第三方資料與授權（CMAB CC BY、OSM ODbL、字體 OFL、取樣庫），以及 FACTS.md 裡標為示意／估算的項目。

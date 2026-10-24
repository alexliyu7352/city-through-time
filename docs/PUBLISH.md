# 發布到入口頁（用戶想公開時才做）

## 這一步最常犯的錯

- 沒問就推送 → 每一次推送、上傳都等用戶當次開口。
- 配音、配樂的條款到發布前才查 → 應該在選定服務時就查（SOUND.md）；到這一步再確認一次。

給用戶看的步驟寫在 `CONTRIBUTING.zh-Hant.md`。倉庫只收文字資料，成片、播放包、海報、圖片、音樂都放在外部：
- 先問用戶要放在哪裡、用哪個帳號，每一步上傳都要用戶自己登入或明確同意（公開了就收不回）；git push 也是上傳，每一次都要用戶當次說；
- 公開之前定好哪些檔能公開：建公開倉庫或第一次推送之前，逐檔掃本機路徑、帳號 ID（例如配音的 voice ID）、信箱、金鑰，非 CC 素材、
  建模參考圖、`local/`、`build/`、`dist/`、內部文件都不進；移出追蹤不等於移出歷史，推上去的第一個 commit 就收不回；
- 成片：用戶上傳到影片網站（YouTube、B 站…），網址寫進 `entry.json` 的 `watch`（發布到幾個網站就填幾個，第一個是入口頁的預設；
  存一般的觀看網址，去掉 `&t=` 這類參數；測試用的影片先確認還在，下架的影片播放器會報一串錯）；也可以另放一份下載（`download`）；
- 網頁播放包：`uv run python -I tools/web.py cities/<slug>` 打包到 `dist/web/`，只收頁面會讀的檔（沒有 WAV、沒有內部測試圖），
  海報 `poster.jpg`（1280 寬）和 `poster_thumb.webp`（640 寬）也在裡面；`bundle.json` 記著每個檔的大小，播放器的載入畫面照它算進度，
  整個資料夾原樣放上去。放的地方要允許網頁跨網域讀取：建議 Hugging Face 資料集
  （免費、大檔沒問題）；或用戶自己的 GitHub 倉庫開 Pages（單檔 100 MB、網站 1 GB 以內）；其他靜態主機要確認有
  `Access-Control-Allow-Origin`。網址寫進 `bundle.url`，大小寫 `bundle.mb`；不做播放包時，海報兩張圖也要放到外部。
  放上去之前確認配音、配樂服務的條款允許公開散布生成的音檔，寫進 CREDITS；不許商用的部分（咸陽：MiniMax 的旁白只限個人、非商業）
  在 `LICENSE-CONTENT.md` 註明不在 CC BY-SA 的授權內，因為 CC BY-SA 允許別人商用；
- `cities/<slug>/entry.json`：`uv run python -I tools/web.py cities/<slug> --entry` 寫出草稿（位置、年代、片長、語言、章節顏色），
  補上五種語言的名字和簡介（en、ja、zh-Hant、zh-Hans、es）、作者、海報和縮圖的 https 網址、AI 生成的部分（`ai`）、`added`；
  `node tools/registry.mjs --check` 檢查欄位（slug 也是城市頁網址，不能和網站自己的資料夾或語言代碼同名）、城市文字檔裡有沒有本機路徑、
  帳號 ID 和金鑰、Markdown 的網址後面有沒有黏著中文標點、`watch` 有沒有帶開始時間；加 `--online` 再問影片網站能不能嵌入、播放包的主機
  准不准別的網站讀（CORS）。入口頁讀的 `cities.json`
  和每座城五種語言的獨立頁面（`https://cities.go5.si/<slug>/`、`/zh-hant/<slug>/`…，帶分享預覽和影片資訊）由 GitHub Actions
  用 `tools/site.mjs` 自動產生，不手改。標準網址、分享圖、sitemap 裡的完整網址是產生網站時寫死的：設好或換了網域要重新部署一次；
  社群網站的分享卡從這裡驗不了，請用戶真的貼一次連結看；
- 本機先試：`node tools/preview.mjs`（會先把網站產生到 `_site/`）後打開 `http://127.0.0.1:8765/<slug>/`，再用
  `play.html?city=<slug>&play=1&bundle=<網址>` 試播放包；
- 交 pull request：只放 `cities/<slug>/` 裡的文字檔（entry.json、city.yaml、script.yaml、CREDITS、各 .md、research/ 的文字筆記、
  assets/README.md 這類素材說明）；圖片、音樂、影片一律不放，PR 的檢查會擋（`tools/registry.mjs --check --base`）。
  例外是本專案的示例城市咸陽：完整保留圖片、海報和網頁播放包（`cities/xianyang/web/`，重打包後複製過去，entry.json 的 bundle 指向它，
  入口頁直接從 GitHub Pages 播放；`.gitignore` 和檢查都對它開例外），建模參考圖和實拍原檔仍不進 git。

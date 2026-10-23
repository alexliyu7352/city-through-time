# 一城春秋 · A City Through Time

給一座城市和一個起始年代，程式代理會查史料、抓建築與地圖資料，把整座城做成白色模型，從最早的聚落到今天，一個時代一個時代地點亮，最後渲染成一部雙語影片。

**入口頁：https://alexliyu7352.github.io/city-through-time/**：轉動地球、挑一座亮著的城市觀看，或者做一部你自己城市的片。

[English](README.md) · 繁體中文

![咸陽，1983 年設市](cities/xianyang/poster.jpg)

## 已經有的城市

| 城市 | 年代 | 片長 | 作者 |
|---|---|---|---|
| 咸陽 | 前 4000 年 – 2026 年 | 12 分 30 秒 | Alex |

完整清單在 [`cities.json`](cities.json)，入口頁就是讀這個檔。每座城的原始資料都在 `cities/<城市>/`，史實出處在它的 `FACTS.md`，第三方素材與授權在它的 `CREDITS`。

## 片子怎麼做出來

做片的是 [Claude Code](https://claude.com/claude-code)，照 [`SKILL.md`](SKILL.md) 這份技能說明一步步做；人負責定方向，並在瀏覽器裡檢查每一步。

1. **研究**：建立這座城的年代表，每條史實都附出處和原文，寫進 `FACTS.md`。
2. **資料**：今天的建築（中國用 CMAB，其他地方用 Overture Maps 加 GHSL 年份）、OpenStreetMap 的水系和路網、Copernicus 地形和衛星影像。
3. **歷代城市**：按考古報告和史料，用程式生成各時代的城（示意模型，不是復原），畫面上標「示意」。
4. **時間軸與文案**：旁白是一條連貫的敘事，畫面跟著句子走；每一站都是這座城自己的轉折。
5. **預覽**：瀏覽器裡即時播放，逐段修改。
6. **旁白、配樂、音效**：先問作者用哪種方式（錄音、線上服務、本機模型；或是程式寫的配樂，當作不用模型的備用選項）。
7. **渲染與交付**：成片、雙語字幕、封面、簡介；合成時不寫任何工具的元數據。

做每座城時都會照固定的檢查跑一遍：模型穿模、鏡頭穿模、字幕寬度、文字停留時間、畫面跳動、黑幀和響度。

## 自己做一部

要準備：Claude Code、Node 20 以上、[uv](https://docs.astral.sh/uv/)、ffmpeg、exiftool，以及一台有顯示卡、裝了 Chrome 的電腦。

```sh
git clone https://github.com/alexliyu7352/city-through-time.git
ln -s "$PWD/city-through-time" ~/.claude/skills/city-through-time   # 讓 Claude Code 認得這個技能
```

然後在 Claude Code 裡說：「用一城春秋做〇〇，從〇〇時代開始」。第一次使用時，它會先問你這台電腦要把資料、模型放在哪裡（預設全部放在專案的 `local/` 下），再裝好環境。

完整教學：[`docs/MAKING.zh-Hant.md`](docs/MAKING.zh-Hant.md)。

## 把你的城市加到入口頁

1. 成片放到 YouTube、B 站或其他影片網站。
2. 想讓大家在入口頁直接播放，就把網頁播放包（`tools/web.py` 打包）放到 Hugging Face 資料集，或你自己的 GitHub Pages。
3. 開一個 pull request：城市資料夾，加上 `cities.json` 裡的一筆資料。

步驟、欄位和審核標準：[`CONTRIBUTING.zh-Hant.md`](CONTRIBUTING.zh-Hant.md)。

## 專案結構

```
index.html, site/   入口頁（讀 cities.json）
play.html, engine/  播放器（three.js）：白模、投影、字幕、片尾
pipeline/           資料與編譯：抓資料、生成歷代城市、排時間軸
render/             渲染：單張、影片、合成成片
audio/              聲音：鋪配樂、程式配樂、混音
tools/              一條命令出片、預覽、各項檢查、網頁播放包、配樂生成
cities/<城市>/       每座城的原始資料（設定、文案、史實出處、研究、素材）
templates/, i18n/   新城市範本；畫面上的字（六種語言）
fonts/              開源字型（SIL OFL）
```

## 授權

- 程式碼：[MIT](LICENSE)。部分程式改自 [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar)（MIT，白模投影風格的出處），清單在 [`NOTICE`](NOTICE)。
- 影片與城市資料：[CC BY-SA 4.0](LICENSE-CONTENT.md)。因為片中用了 CC BY-SA 的實拍，依授權規定成片本身也必須是 CC BY-SA。
- 他人的素材依各自授權，列在每座城的 `CREDITS`：建築與地圖資料（CC BY 4.0、ODbL）、Wikimedia Commons 的實拍與照片、字型（OFL）。
- 入口頁的地球依 [Natural Earth](https://www.naturalearthdata.com/)（公有領域）繪製。

## 關於 AI

研究、程式、渲染都由程式代理完成。片中的旁白、配樂和想像圖是 AI 生成的，畫面和片尾都有標註；每一條史實都要在 `FACTS.md` 找得到出處，示意與估算的畫面上會寫明。

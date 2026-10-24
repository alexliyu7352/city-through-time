# 咸陽 · 配樂

選定：**Stable Audio 3 Medium，本機 CPU 生成**。
以後改配樂照這份檔案的流程做；換模型，改這份檔案並重生全部段落。提示詞只寫在這裡一處。

分工：配樂（下面 11 段，加 2 條獨立音軌）用模型生成。音效、環境聲和最後的混音（旁白出現時壓低配樂、全片音量統一）另外定。

依據：`research/music.md`（各時期的樂器、史料出處、模型的詞彙）。提示詞照研究寫，不憑印象。

## 1. 模型與授權

- 模型：`stabilityai/stable-audio-3-medium`。
  程式庫：https://github.com/Stability-AI/stable-audio-3 （用的版本：77e0398）。
- 本機跑的是官方 CPU 版 `stabilityai/stable-audio-3-optimized` 的 `tflite/`：同一個 Medium 模型（DiT 和 SAME-L 都出自 Medium 的檢查點）
  轉成 int8，DiT 1.7 GB，記憶體約 2 GB，一次最長 380 秒，不用登入。
  - 原版權重 10.4 GB，載入時記憶體估計要 20 GB 上下，而且要登入 Hugging Face。
  - 裝在本機設定的 `stable_audio`（程式，固定在 77e0398，自帶 .venv）和 `hf_cache`（權重），見 `local/config.json`。
  - 實測（Ryzen 3800X，8 執行緒）：30 秒音樂 61 秒生成，記憶體最高 2.2 GB。
  - int8 和 fp32 出來是「不同的一首」，官方說不是比較差。CPU 版的 fp32 在 31 GB 記憶體的電腦上跑不起來，所以只用 int8（`tools/music.py` 只支援 int8）：
    - 開權重快取：5.8 GB 的快取檔驗證失敗（LiteRT 2.3.0、2.2.0 都一樣；int8 的 1.5 GB 快取沒問題），載入後配置記憶體失敗；
    - 關權重快取：載入還沒完就用到 27.3 GB 記憶體。
- 授權：Stability AI Community License。
  - 年營收 100 萬美元以下可以商用；商用要先到 Stability AI 登記。
  - 生成的音樂歸使用者所有。
  - 文字編碼器 T5Gemma 另受 Gemma Terms of Use 約束。
- 訓練資料（官方說法）：AudioSparx 授權曲庫，加上 Freesound 的 CC0、CC-BY、CC-Sampling+ 錄音。
- 署名：CREDITS 加一行 `Music: generated for this film with Stable Audio 3 Medium (Stability AI), Stability AI Community License`。
  片尾畫面也標「AI 生成」（city.yaml `end.credits`）。

## 2. 聲音的設計

城市的聲音是**一個節奏**，不是一件旋律樂器。

- **鼓**：全片貫穿，每個時代都有鼓的實物或記載。
  - 節奏固定成「兩擊一組、間隔很長」的心跳，只換鼓的種類。
  - 秦都、帝都、焚城，鼓是主角（兵馬俑一號坑的鼓與鼓槌、「聞鼓聲而進」為據）。
- **陶塤兩音**：半坡陶塤測得的小三度，是關中最古老的音程。全片只出現三次：
  - 開場；
  - 焚城留白之後（185.37）；
  - 片尾字卡。

  意思是：城毀了，最古老的聲音還在。
- **箏**：李斯說「彈箏」是「真秦之聲」，所以從秦開始當旋律主角。新區以後和代表西安的笙、笛對話。
- **起伏照史料的疏密走**：
  - 帝都史料最響，配樂最滿；
  - 焚城史料一聲不吭，配樂最空；
  - 降為縣城後，本地的弦板腔、秦腔梆子第一次能點名。

| 段 | 主奏 | 心跳由誰打 | 不要出現 |
|---|---|---|---|
| M01 | 小陶塤兩音 | 手拍陶罐 | 金屬、弦樂、和弦 |
| M02 | 戰鼓群齊奏 | 戰鼓（號令） | 鑼、鈸、嗩吶、二胡、琵琶、銅管 |
| M03 | 失序的戰鼓 | 最後只剩一面悶鼓 | 二胡、嗩吶、勝利式收尾 |
| M04 | 漢唐一段：排簫、箏、編鐘起，琵琶、竹笛加入，竹笛送別收 | 建鼓 | 古琴主奏、笙（模型不認得） |
| M05 | 竹笛 | 遠處更鼓、句尾梆子 | 銅管、鼓陣、合成器 |
| M06 | 高音板胡（以 erhu 代） | 梆子與火車軌縫；紡織城段加關中鑼鼓陣 | 電聲、陝北腰鼓當主角 |
| M07 | 合成器琶音、板胡 | 梆子再交給鼓機 | 2000 年後的製作手法、引用老歌旋律 |
| M08 | 手風琴、略走音的鋼琴 | 紗機減速到停，鼓全撤 | 打氣式副歌、鼓組 |
| M09 | 笙與笛（長安）對箏（秦） | 柔和的木琴脈衝 | 硬鼓點、EDM |
| M10 | 板胡呼喚、竹笛遠遠回應 | 遠處一擊或沒有 | 兩個動機齊奏、解決 |
| M11 | 戰鼓群回歸（和 M02 同一措辭） | 地鐵般的低頻脈衝；最後一句說完推到高潮 | 完滿終止（「還在生長」要開放收尾） |

不能寫進提示詞、要用只能另外錄的：「歌呼嗚嗚」的吼聲、涇河號子這類人聲。

## 3. 模型的脾氣（照它寫提示詞）

- 開頭一律寫 `TrackType: Music, VocalType: Instrumental,`，只用英文。
- 寫法是「標籤加一句描述」，40–70 個英文詞（上限 256 個 token）。
- **寫簡單**：樂器 3–4 件、一種織體，不要寫「先怎樣、再加入、推到高潮」的多段劇情（對照試聽：6 件樂器加多段描述聽起來雜亂，只寫 3 件的比較順）。每段最後一行是照這條改寫的版本。
- **CFG 2.0 加負面提示詞**（`tools/music.py` 預設；負面提示詞在下面 `### negative`）：對照試聽比不加順；生成時間約 1.7 倍。
  - `Instruments:` 不超過 6 個；
  - 速度寫 BPM，也寫 AudioSparx 的分級詞（Very Slow、Slow、Medium Slow、Medium）。
- 原版說明寫 Medium **沒有負面提示詞，cfg 也不起作用**（固定 8 步）；這不適用 CPU 版：它有 `--cfg`、`--negative-prompt`、`--apg`，開了會跑條件和無條件兩次，對照試聽後用 CFG 2.0 加負面提示詞（見上一條）。
  - 連「no erhu」這種否定句也別寫。
  - 提示詞裡也不能出現 voice、vocal、choir、chant、chorus、male、female、lyrics 這些人聲字眼。
- 換種子：查到的說法是原版幾乎不變；**CPU 版會變**（實測同一段的種子 1、2：整體音色相近，旋律和起伏完全不同）。
  - 所以候選用換種子出（`--seeds 1,2,3`）；整段方向不對，才改措辭。
  - 鼓的措辭在 M02、M03、M11 一字不改：`huge Chinese war drums struck with heavy wooden mallets`。
  - 心跳的措辭在 M01、M03 一字不改：`slow two-stroke heartbeat`。
- 中國鼓樂在訓練資料裡很少（亞洲鼓類 16 首、日本太鼓 30 首）。寫「中國戰鼓」多半會出太鼓、預告片鼓加上鑼，選候選時用耳朵把關。
- 罕見樂器換成模型認得的詞：

  | 樂器 | 寫成 |
  |---|---|
  | 塤 | ocarina（加 small breathy clay） |
  | 編鐘、鎛 | bronze bells |
  | 石磬 | stone chimes |
  | 梆子 | wooden clapper |
  | 笙 | 模型不認得（sheng 會出成箏一類），不用；西安那條線改由竹笛代表 |
  | 嗩吶 | shawm |
  | 板胡 | erhu（加 bright nasal high register） |
  | 阮 | ruan |
  | 排簫 | pan flute |
- 調性不在模型的資料欄位裡，寫了也不會照做；要對調就後製移調。
- 長度：
  - 由 `tools/music.py` 算：段在時間軸上的長度加 4 秒，最少 30 秒。模型會在要求長度前 3–6 秒自己收尾，這樣收尾剛好落在段尾。
  - 已經選好的條：排上時間軸時自動對齊，讓它的收尾落在段尾（從開頭裁掉多出的秒數），高潮留在段內；最後一段讓音樂和片子一起結束。
  - CPU 版一次最長 380 秒，各段都能一次生成。太短會變成循環，太長容易散成氛圍音樂，聽候選時注意。
  - 接著前一段往下生成（`continue:`）：取前一段在接點前的 20 秒當開頭，從接點往後生成新的（`--init-audio` 加 `--inpaint-range`）。
    新的一段會延續前一段的速度、調性和音色，再轉向自己的寫法；接點前和前一段一模一樣，所以接得上。前一段換了，這段要重生。
- 一次生成一條：4 種寫法就是跑 4 次。
- 精確到秒的點（火起、留白、熄燈）模型做不到，都在剪輯時處理，或用第 6 節的獨立音軌放到準確位置。

### negative 負面提示詞（開 CFG 時用；對照試聽：加了比較不彆扭）

```
vocals, singing, out of tune, dissonant, distorted, chaotic, noisy, muddy
```

## 4. 生成前先試詞

每個詞生成 30 秒試聽（`uv run python -I tools/music.py cities/xianyang test`），確認模型認得哪些詞，再生成 11 段。
認不得的詞，換成第 3 節表裡寫的替代說法再試。

### test 試詞（一行一條）

```
TrackType: Instrument, Instruments: Ocarina, a small breathy clay ocarina playing slow notes, intimate and dry, Tempo: Very Slow, BPM: 56
TrackType: Instrument, Instruments: Taiko Drums, huge Chinese war drums struck with heavy wooden mallets, Tempo: Medium Slow, BPM: 80
TrackType: Instrument, Instruments: Bells, bronze bells struck slowly with a long ring, Tempo: Slow, BPM: 60
TrackType: Instrument, Instruments: Stone Chimes, bright stone chimes struck slowly, Tempo: Slow, BPM: 60
TrackType: Instrument, Instruments: Clapper, a dry wooden clapper keeping time, Tempo: Medium, BPM: 96
TrackType: Instrument, Instruments: Sho, a warm sho drone with slow chord changes, Tempo: Very Slow, BPM: 56
TrackType: Instrument, Instruments: Pan Flute, a breathy pan flute playing a slow melody, Tempo: Slow, BPM: 60
TrackType: Instrument, Instruments: Ruan, a ruan plucking a slow melody, Tempo: Slow, BPM: 64
TrackType: Instrument, Instruments: Erhu, a bright nasal erhu in its high register, Tempo: Medium, BPM: 96
TrackType: Instrument, Instruments: Sheng, a Chinese sheng mouth organ holding bright reedy sustained chords, Tempo: Very Slow, BPM: 56
TrackType: Instrument, Instruments: Harmonium, a soft reedy free-reed organ holding slow sustained chords, Tempo: Very Slow, BPM: 56
TrackType: Instrument, Instruments: Mouth Organ, a bright reedy Chinese mouth organ playing slow chords, Tempo: Very Slow, BPM: 56
```

試詞結果（逐條試聽）：
- 認得：陶塤、戰鼓、編鐘、石磬、梆子、排簫、阮、高音二胡。
- 編鐘只響了一下：試詞寫的是「struck slowly with a long ring」；段落裡要寫出節奏（例如 ring on each downbeat）。
- **笙（sho）不對**：換 10–12 三種說法再試（sheng、harmonium、mouth organ）。
  - 再試的結果：三種都不是笙。sheng 出來像琴（模型多半把 sheng 當成 zheng），harmonium、mouth organ 本身就是別的樂器。
  - 結論：模型不認得笙。用到 sho 的 M04b、M05、M09、M10，那個位置出來的是別的聲音。Wikimedia Commons 上的笙錄音只有一段半音階。
- 提示詞別寫 long silences、sparse、long pauses：模型照字面留出整段靜音（M01 第 1 行，34–41% 的時間低於 -45 dB），聽起來斷斷續續。
  要「空」，寫成一條持續的底（drone）上面只有少數聲音。
- 生成的每段在最後 3–6 秒會自己收尾、變靜音（例：M02 135 秒起、M09 78.6 秒起），所以要多生成幾秒（見第 3 節「長度」）。

## 5. 分段與提示詞

段落邊界就是節點邊界，時間取自 `build/export/timeline.json`（下表的秒數只供參考，以它為準）。
時間軸以後再變，就照節點 id 對齊，不照秒數：每段從哪個節點開始寫在 city.yaml 的 `film.music.cues`，
compile 照它把選中的那條排上時間軸（`audio/lay.py`）：
- 交接：上一段的收尾（最後那次淡出的起點）落在段尾後 0.5 秒；下一段提早 1.5 秒起、至少 2.5 秒淡入，上一段若更早開始收，就從那時起；
  一個淡出、一個淡入，中間不留空。接著上一段生成的（`continue:`）在接點逐取樣交接。
- 旁白每句前後壓低 10 dB，沒有旁白時配樂比旁白的說話音量低 5 dB；
- 旁白的留白（焚城、熄燈前）配樂不停：沒有旁白壓著，配樂自然浮上來（留白無聲聽起來突兀）；片尾最後一句說完應該是高潮，不是無聲。
預覽播放時配樂和旁白一起放，B 鍵開關配樂，M 鍵開關旁白。

| 段 | 節點 | 時間（秒） | 情緒 | 怎麼生成 |
|---|---|---|---|---|
| M01 | 開場、name、neolithic | 0.00–38.72 | wonder | 亮燈前從無聲淡入 |
| M02 | qin、empire | 38.72–168.87 | pride，全片第一個高峰 | 一次 138 秒；起漲對 92.55（掃平六國），用 `offset` 對 |
| M03 | burn | 168.87–191.87 | grief | 接著 M02 的結尾生成；181.37–185.37 旁白留白時配樂浮上來 |
| M04 | han、tang | 191.87–293.25 | 漢唐的鼎盛 | 一段，最後一句竹笛送別（渭城） |
| M05 | ming | 293.25–344.23 | calm | |
| M06 | rail、mills | 344.23–404.31 | hope→pride | 接著 M05 的結尾生成；鑼鼓陣要在 379.02（紡織城）前後進來 |
| M07 | m1975–m1991 | 404.31–492.57 | calm→pride→hope | 一次生成；441.05 起換強拍，466.45 起半速 |
| M08 | m1998 | 492.57–529.39 | grief | |
| M09 | m2005–m2011 | 529.39–606.13 | hope | |
| M10 | m2014 | 606.13–641.63 | wistful（強） | |
| M11 | m2019–today、片尾 | 641.63–749.65 | hope 推到收尾 | 728.30 最後一句說完（730.5），旁白一停配樂就浮上來成為高潮，在片尾字卡（739.15 起）底下收 |

### M01 開場與新石器（第 1 行不用：三到四成時間是靜音、忽大忽小、沒有低音；第 2、3 行底下一直有低沉的持續音）

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Ethereal, Instruments: Ocarina, Indigenous Drums, Moods: Mystical, Earthy, Sparse, Tempo: Very Slow, BPM: 56, documentary underscore, hall reverb. Dawn over a Neolithic river village: a small breathy clay ocarina repeats a two-note minor-third call, soft hands on a clay pot keep a slow two-stroke heartbeat, long silences, full of wonder.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Ethereal, Instruments: Ocarina, Bass Drum, Moods: Mystical, Earthy, Warm, Tempo: Very Slow, BPM: 56, documentary underscore, hall reverb. A continuous low warm drone like wind over a river plain at dawn, a soft deep drum keeps a slow two-stroke heartbeat, and a small breathy clay ocarina answers with a two-note minor-third call, calm and full of wonder, flowing without breaks.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Ethereal, Instruments: Ocarina, Frame Drum, Moods: Mysterious, Earthy, Calm, Tempo: Very Slow, BPM: 56, documentary underscore, hall reverb. An ancient river village before dawn: a deep sustained earthy drone under everything, a hand-played frame drum keeps a slow two-stroke heartbeat, a small breathy clay ocarina repeats a simple two-note minor-third motif, steady and unbroken.
```

### M02 秦都→帝都（第 2 行是 `Subgenre: Chinese Action` 的對照版）

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Regal Chinese, Instruments: Taiko Drums, Big Toms, Bells, Guzheng, Moods: Majestic, Stately, Marching, Tempo: Medium Slow, BPM: 80, documentary underscore, hall reverb. Huge Chinese war drums struck with heavy wooden mallets play disciplined unison accents over clay pot thuds and a plucked guzheng ostinato, then bronze bells ring on each downbeat with bright stone chimes, building to a proud imperial climax.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Action, Instruments: Taiko Drums, Big Toms, Bells, Guzheng, Moods: Majestic, Stately, Marching, Tempo: Medium Slow, BPM: 80, documentary underscore, hall reverb. Huge Chinese war drums struck with heavy wooden mallets play disciplined unison accents over clay pot thuds and a plucked guzheng ostinato, then bronze bells ring on each downbeat with bright stone chimes, building to a proud imperial climax.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Regal Chinese, Instruments: Taiko Drums, Guzheng, Bells, Moods: Majestic, Stately, Proud, Tempo: Medium Slow, BPM: 80, documentary underscore, hall reverb. Huge Chinese war drums struck with heavy wooden mallets in disciplined unison, a plucked guzheng ostinato, bronze bells on the downbeats, stately and proud, slowly building.
```

### M03 焚城（第 1 行不用；第 2 行接著 M02 的結尾生成：同一批戰鼓失序、散掉，底下一直有低沉的持續音，不寫 sparse）

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Taiko Drums, Bells, Guzheng, Ocarina, Moods: Mournful, Sparse, Tempo: Very Slow, BPM: 50, documentary underscore, hall reverb. Huge Chinese war drums struck with heavy wooden mallets lose their order in sparse irregular strokes, one crushing blow, a cracked bronze bell, a snapped guzheng string, then a slow two-stroke heartbeat on a low drum and a lone clay ocarina.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Taiko Drums, Bells, Bass Drum, Moods: Mournful, Dark, Tense, Tempo: Slow, BPM: 64, documentary underscore, hall reverb. The same huge Chinese war drums struck with heavy wooden mallets fall out of time and break apart over a deep rumbling drone like a distant fire, a cracked bronze bell tolls, the drums slow and thin into a slow two-stroke heartbeat on a low drum, grieving.
```

### M04 漢唐（漢唐是中國最鼎盛的兩個朝代，合成一段；第 1 行是只有漢的版本，第 2 行是合併版：莊嚴、豐盛，最後留一句竹笛送別）

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Bamboo Flute, Pan Flute, Guzheng, Ruan, Bass Drum, Moods: Nostalgic, Solemn, Reflective, Tempo: Slow, BPM: 60, documentary underscore, hall reverb. Single deep strokes on a large barrel drum with long gaps, breathy pan flute and sparse plucked guzheng in dry plateau air, then a high bamboo flute leads a slow farewell melody, ruan plucks answering, fading unresolved.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Regal Chinese, Instruments: Bass Drum, Bells, Pan Flute, Guzheng, Pipa, Bamboo Flute, Moods: Majestic, Warm, Glorious, Nostalgic, Tempo: Slow, BPM: 72, documentary underscore, hall reverb. The golden age of Han and Tang: deep barrel drum strokes and bronze bells under a broad stately melody on pan flute and guzheng, growing splendid as a plucked pipa and a bright bamboo flute join, ending on a long tender farewell phrase on the bamboo flute.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Regal Chinese, Instruments: Pan Flute, Guzheng, Pipa, Bass Drum, Moods: Majestic, Warm, Glorious, Tempo: Slow, BPM: 72, documentary underscore, hall reverb. The golden age of Han and Tang: a broad stately melody on pan flute over plucked guzheng and pipa, deep barrel drum strokes, majestic and warm.
```

### M04b 唐（不用：併進 M04）

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Bamboo Flute, Pipa, Guzheng, Sho, Moods: Nostalgic, Reflective, Sparse, Tempo: Slow, BPM: 60, documentary underscore, hall reverb. Farewell at a misty river ferry at dawn: a high bamboo flute leads a slow drawn-out melody, pipa plucked with a wooden plectrum, a soft sho drone, a faint fast two-stick drum flutter far away, slowing down and fading unresolved.
```

### M05 明清縣城

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Folk Ensembles, Instruments: Bamboo Flute, Ruan, Clapper, Sho, Bells, Moods: Meditative, Nostalgic, Earthy, Tempo: Very Slow, BPM: 56, documentary underscore, hall reverb. A quiet walled county town at dusk: a soft bamboo flute in free time settles into a slow pulse, gentle ruan plucks, dry wooden clapper ticks only at phrase ends, a warm sho drone, one low temple bell.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Folk Ensembles, Instruments: Bamboo Flute, Ruan, Clapper, Moods: Calm, Nostalgic, Earthy, Tempo: Very Slow, BPM: 56, documentary underscore, hall reverb. A quiet walled county town at dusk: a soft bamboo flute melody, gentle ruan plucks, a dry wooden clapper at the end of each phrase, calm and nostalgic.
```

### M06 鐵路、解放、紡織城（這段的情緒：火車來了的新奇 → 翻開新的一頁 → 建設的勁 → 紡織城的自豪，溫暖、向上、慢慢鼓起來，不是進行曲。第 1 行和明清那段接不上；第 2 行接著 M05 生成，帶著竹笛、梆子和慢速，聽起來還是老縣城；第 3 行起不接續，照畫面寫；第 4 行簡化過頭，整段一樣大聲；用的是第 6 行）

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Happy, Instruments: Erhu, Clapper, Accordion, Chinese Gongs, Cymbals, Bass Drum, Moods: Hopeful, Rousing, Driving, Tempo: Medium, BPM: 108, documentary underscore, hall reverb. A bright nasal erhu in its high register leads a hopeful tune over a steady train-wheel rhythm of wooden clappers, accordion chords underneath, then a big drum, gongs and cymbals join in a proud festive march.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Folk Ensembles, Instruments: Bamboo Flute, Clapper, Erhu, Accordion, Bass Drum, Chinese Gongs, Moods: Hopeful, Warm, Building, Tempo: Medium Slow, BPM: 76, documentary underscore, hall reverb. The quiet old town wakes to the railway: the bamboo flute melody carries on over a steady train-wheel rhythm of wooden clappers, a bright nasal erhu in its high register takes up a hopeful tune with warm accordion chords, then a big drum and gongs lift it into a proud festive close.
TrackType: Music, VocalType: Instrumental, Genre: Orchestral, Subgenre: Cinematic, Instruments: Strings, Brass, Snare Drum, Accordion, Erhu, Timpani, Moods: Hopeful, Driving, Proud, Uplifting, Tempo: Medium, BPM: 100, documentary underscore, hall reverb. A steam train sets off: low strings and a snare drum drive a steady wheels-on-rails rhythm, a bright erhu plays a hopeful melody above it, then accordion and brass join like a 1950s factory band, building to a proud, optimistic march.
TrackType: Music, VocalType: Instrumental, Genre: Orchestral, Subgenre: Cinematic, Instruments: Strings, Snare Drum, Erhu, Moods: Hopeful, Driving, Tempo: Medium, BPM: 100, documentary underscore, hall reverb. A steady train rhythm on low strings and snare drum, a bright erhu melody full of hope above it.
TrackType: Music, VocalType: Instrumental, Genre: Orchestral, Subgenre: Cinematic, Instruments: Strings, Erhu, Timpani, Moods: Hopeful, Warm, Tender, Uplifting, Tempo: Medium Slow, BPM: 84, documentary underscore, hall reverb. A new day comes to an old town: a gentle steady pulse of low strings like a distant train, a warm erhu melody full of quiet hope, slowly swelling with full strings and soft timpani into a warm, proud close.
TrackType: Music, VocalType: Instrumental, Genre: Orchestral, Subgenre: Cinematic, Instruments: Strings, Brass, Erhu, Moods: Hopeful, Proud, Uplifting, Tempo: Medium, BPM: 96, documentary underscore, hall reverb. The age of building: a steady rhythmic pulse of strings like spinning looms, an erhu melody full of hope, warm brass rising beneath it, growing into a proud, uplifting finale.
```

### M07 1975–1991

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Pop Instr., Instruments: Synthesizer, Drum Machine, Electric Bass, Erhu, Moods: Nostalgic, Rousing, Hopeful, Tempo: Medium Slow, BPM: 96, documentary underscore, hall reverb. Opens calm with warm 1980s analog synth arpeggios and faint tape hiss, a wooden clapper tick on each bar, then a punchy drum machine and bold electric bass lift a bright erhu melody proudly, ending in airy pads.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Pop Instr., Instruments: Synthesizer, Drum Machine, Erhu, Moods: Nostalgic, Hopeful, Tempo: Medium Slow, BPM: 96, documentary underscore, hall reverb. Warm 1980s analog synth arpeggios over a steady drum machine, a bright erhu melody, nostalgic and hopeful.
```

### M08 1998

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Accordion, Piano, Erhu, Moods: Melancholic, Nostalgic, Somber, Tempo: Slow, BPM: 64, documentary underscore, hall reverb. Elegy for a closed textile mill: a soft mechanical loom rhythm slows and stops, a lonely accordion and a slightly detuned upright piano carry a slow minor melody, a low erhu answers, long empty factory hall reverb.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Accordion, Piano, Erhu, Moods: Melancholic, Nostalgic, Tempo: Slow, BPM: 64, documentary underscore, hall reverb. Elegy for a closed textile mill: a lonely accordion and a soft upright piano play a slow minor melody, a low erhu answers.
```

### M09 2005–2011

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese New Age, Instruments: Sho, Bamboo Flute, Guzheng, Marimba, Moods: Hopeful, Reflective, Uplifting, Tempo: Medium Slow, BPM: 92, documentary underscore, hall reverb. Two neighbouring cities begin a dialogue: a warm sho chord and an airy bamboo flute answer a gently plucked guzheng phrase, a soft marimba pulse returns like a heartbeat, light and patient, slowly growing brighter.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese New Age, Instruments: Bamboo Flute, Guzheng, Marimba, Moods: Hopeful, Reflective, Tempo: Medium Slow, BPM: 92, documentary underscore, hall reverb. An airy bamboo flute and a plucked guzheng answer each other over a soft marimba pulse, hopeful, slowly growing brighter.
```

### M10 2014

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Erhu, Bamboo Flute, Sho, Moods: Melancholic, Nostalgic, Sparse, Tempo: Slow, BPM: 60, documentary underscore, hall reverb. A solo erhu calls and a distant bamboo flute replies, taking turns but never meeting in unison, over a low sustained sho drone, long pauses, each phrase left hanging unresolved, deeply wistful and restrained.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Erhu, Bamboo Flute, Strings, Moods: Melancholic, Nostalgic, Tempo: Slow, BPM: 60, documentary underscore, hall reverb. A solo erhu calls and a distant bamboo flute replies over soft sustained strings, wistful and unresolved.
```

### M11 2019–2026 與片尾

```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Action, Instruments: Taiko Drums, Guzheng, Bamboo Flute, Synthesizer, Strings, Moods: Hopeful, Uplifting, Building, Climactic, Tempo: Medium Slow, BPM: 80, documentary underscore, hall reverb. A deep pulsing synth bass like a metro, then huge Chinese war drums struck with heavy wooden mallets return layer by layer, guzheng and bamboo flute finally play one melody in octaves, building to an uplifting peak.
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Action, Instruments: Taiko Drums, Strings, Guzheng, Synthesizer, Moods: Hopeful, Uplifting, Climactic, Tempo: Medium Slow, BPM: 80, documentary underscore, hall reverb. A deep pulsing synth bass like a metro, huge Chinese war drums struck with heavy wooden mallets, soaring strings and guzheng, building to an uplifting peak.
```

## 6. 獨立音軌（各生成一次，全片重複用）

只生成一次、到處重複用，才能保證全片是「同一個心跳、同一個兩音」。

放到準確秒數的功能還沒做（要用時再做）。

### heartbeat 心跳鼓：用在 M03 留白、M05 更鼓、M11 的 736.0 和 737.65 兩擊

```
TrackType: Instrument, Instruments: Bass Drum, a slow two-stroke heartbeat on a low drum with long gaps, dry and close, Tempo: Very Slow, BPM: 56
```

### xun 塤兩音：用在 M01、185.37、片尾字卡

```
TrackType: Instrument, Instruments: Ocarina, a small breathy clay ocarina plays a two-note minor-third call with long silences, intimate and dry, Tempo: Very Slow, BPM: 56
```

## 7. 檔案

- 試詞：`build/audio/music/test/<編號>-<樂器>.wav`
- 候選：`build/audio/music/cand/<段>_<寫法>-<種子>.wav`，旁邊的 .json 記著提示詞、種子、長度、精度、接續。
- 全部是 44.1 kHz 立體聲 WAV；`build/` 不進 git，選中的那條別刪。
- 指令：`uv run python -I tools/music.py cities/xianyang --list` 看各段狀態；`... M02 M03` 生成；`--wordings 1,2 --seeds 1,2` 指定。

選定時，在 city.yaml 那段寫 `take: <寫法>-<種子>`；要從中間開始用，加 `offset: <秒>`；音量加 `gain: <dB>`。
在那一行的註解寫為什麼選它。同一段寫法、同一個種子、同一個精度，重生會得到同一首。

# Stable Audio 3 Medium 提示詞寫法：中國傳統與中國風電影配樂（以鼓為主）

> 研究日期：2026-10-22。本機 repo clone 為 `Stability-AI/stable-audio-3` commit `77e0398`（2026-10-11），位於 （本機的下載副本，未公開）；以下 repo 檔案以 GitHub `main` 路徑引用。
> 標記：**【實證】** = 原始碼、論文或網站頁面上直接看得到的事實；**【社群實測】** = 第三方實際生成後的回報；**【建議】** = 我根據前兩者推論的做法，**未經實際生成驗證**。
> 本文全部提示詞字串、標籤名稱與樂器英文詞都照原樣保留英文，因為模型只吃英文（見 Q2）。

---

## Q1. AudioSparx 的 metadata 詞彙長什麼樣？裡面有哪些中國／亞洲類別與樂器名稱，數量多少？

### Takeaway
AudioSparx 的 metadata 包含：自然語言描述、標題、關鍵字、BPM、genre／subgenre、moods、instruments。中國音樂整個分類只有約 2,144 首，在一個 100 萬首以上的曲庫中很小。中國專屬的鼓樂幾乎沒有（「World | Asian Drums and Percussion」只有 16 首，「Chinese Folk Opera」只有 7 首）。不過中國風動作配樂的曲目描述中，反覆出現「guzheng, dizi, xiao, yangqin, erhu, taiko drums and traditional chinese percussion」這組詞。所以模型最熟的「中國戰鼓」，很可能其實是「taiko + 好萊塢預告片鼓 + 中國鑼」的混合。

### Cited Findings
**訓練資料與 metadata 欄位（論文與模型卡）**
- 【實證】SA3 medium 的訓練資料共 1,278,902 筆錄音：AudioSparx 806,284 筆，Freesound 472,618 筆。Freesound 部分是 266,324 筆 CC-0、194,840 筆 CC-BY、11,454 筆 CC-Sampling+，不含 NC 授權。— [HF 模型卡](https://huggingface.co/stabilityai/stable-audio-3-medium)；[論文 §3.5](https://arxiv.org/html/2605.17991v1)
- 【實證】論文 §3.5 原文：「For AudioSparx tracks, metadata includes natural-language descriptions, titles, keywords, and domain-specific metadata such as BPM, genre, moods, or instruments.」Freesound 則是 titles、tags、natural-language descriptions。論文沒有提到 key（調性）。— [論文 §3.5](https://arxiv.org/html/2605.17991v1)
- 【實證】repo 的 FP8 校準腳本用了一句 metadata 形式的「完整渲染」提示詞，透露了欄位格式：`Genre: House, Subgenre: Deep House, BPM: 122 BPM, Tempo: Medium, VocalType: Instrumental, TrackType: Music, Grade: Neutral`。— [optimized/tensorRT/build/make_dit_fp8_smalldit.py L65-66](https://github.com/Stability-AI/stable-audio-3/blob/main/optimized/tensorRT/build/make_dit_fp8_smalldit.py)
- 【實證】repo 另一支腳本讀取名為 `asx_comma_audio.json` 的 prompt list（asx 應指 AudioSparx），並用 `"tracktype: sfx"` 字串分辨音樂和音效，說明訓練 prompt 是逗號串接的 metadata 字串。— [optimized/tensorRT/quantize/recalib_dec_sames_margin.py](https://github.com/Stability-AI/stable-audio-3/blob/main/optimized/tensorRT/quantize/recalib_dec_sames_margin.py)
- 【實證】官方提示詞指南列出這些標籤：`TrackType: Music, VocalType: Instrumental`、`TrackType: Instrument`、`TrackType: SFX`、`Genre: Funk`（可重複多個 Genre）、`Instruments: Guitar, Saxophone, Bass, Piano`、`Format: Duo`。— [docs/guides/prompting.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md)；[Stability 官網 SA3 Prompt Guide](https://stability.ai/guides/stable-audio-3-prompt-guide)
- 【實證】論文給的 Instruments／Moods 欄位範例：`Instruments: Guitar, Drums, Bass Guitar, Moods: Uplifting`。— [論文 §3.5](https://arxiv.org/html/2605.17991v1)

**AudioSparx 的 Tempo 分級詞（對應 `Tempo:` 欄位）**
- 【實證】AudioSparx 的 BPM 分級：1-59 Very Slow、60-79 Slow、80-104 Medium Slow、105-129 Medium、130-149 Medium Fast、150-169 Fast、170-500 Very Fast。曲目列表顯示成「Slow 67」「Med Fast 130」「Medium 120」「Very Fast 170」這種格式。— [AudioSparx Dramatic genres 頁（BPM 計算器）](https://www.audiosparx.com/sa/links/dramatic-music-genres.cfm)；[AudioSparx Chinese Action 列表](https://www.audiosparx.com/sa/display/sounds.cfm/soundGroup_iid.1792)

**中國與亞洲類別（2026-10 瀏覽頁數字；訓練資料快照時點不明，僅供量級參考）**
- 【實證】Chinese Music 共 2,144 首。子類（數量 / 子類名）：264 Chinese Buddhist Temple、184 Chinese Corporate、77 Chinese Dramatic｜Action, adventure, impact, battle, conflict, intense、66 Chinese Dramatic｜Edgy, dark, tension, suspense, mysterious、367 Chinese Dramatic｜Ethereal, serene, mellow, dreamy, calm、176 Chinese Dramatic｜Happy, Springtime, harvest, joyful、71 Chinese Dramatic｜Sad, somber, sorrowful, longing, lost, defeated、38 Chinese Electronica and Dance、7 Chinese Folk Opera、229 Chinese Folk Traditional｜Ensembles、125 Chinese Folk Traditional｜Solo instrumentals、15 Chinese Hip Hop、20 Chinese Jazz、78 Chinese New Age、153 Chinese New Year Instrumentals、3 Chinese New Year Vocals、163 Chinese Pop、38 Chinese Pop Instrumental、3 Chinese Rock、64 Regal Chinese。— [AudioSparx Chinese Music](https://www.audiosparx.com/sa/display/submain.cfm/soundGroup_iid.4771)
- 【實證】曲目上實際掛的 genre 標籤字串（「Edit Type: Full Track - …」後面那段）是：`Chinese, Chinese Action`、`Chinese, Chinese Edgy`、`Chinese, Chinese Ethereal`、`Chinese, Chinese Happy`、`Chinese, Chinese Sad`、`Chinese, Regal Chinese`、`Chinese, Chinese Folk Ensembles`、`Chinese, Chinese Folk Solo`、`Chinese, Chinese New Years`、`Chinese, Buddhist Temple`、`Chinese, Chinese Folk Opera`、`Chinese, Chinese New Age`、`Chinese, Chinese Electronica`、`Chinese, Chinese Pop Instr.`。— [AudioSparx Chinese Music 各子類列表](https://www.audiosparx.com/sa/display/submain.cfm/soundGroup_iid.4771)（例：[Chinese Action](https://www.audiosparx.com/sa/display/sounds.cfm/soundGroup_iid.1792)、[Regal Chinese](https://www.audiosparx.com/sa/display/sounds.cfm/soundGroup_iid.4792)、[Folk Ensembles](https://www.audiosparx.com/sa/display/sounds.cfm/soundGroup_iid.4788)、[Chinese Sad](https://www.audiosparx.com/sa/display/sounds.cfm/soundGroup_iid.4793)）
- 【實證】Asian Music 共 5,272 首，其中 Asian Contemporary Dramatic 443、Asian music 1,057、Asian New Age 437、Mongolian 41、Tibetan 82、Taiwanese 3，Chinese 以 XREF 計 2,144。— [AudioSparx Asian Music](https://www.audiosparx.com/sa/display/submain.cfm/soundGroup_iid.2495)
- 【實證】整個 Drum Music 類共 4,143 首。子類：Dramatic Drums｜Action intense fast 409、Dramatic Drums｜Action moderate 602、Dramatic Drums｜Chaotic 349、Stomp-Drumming 187、Timpani Drums 86、Military March Drums 70、World｜Indigenous｜Tribal Drums 108、**World｜Japanese｜Taiko Drums 30**、**World｜Asian Drums and Percussion 16**、Folk Drums 16。— [AudioSparx Drum Music](https://www.audiosparx.com/sa/display/submain.cfm/soundGroup_iid.5082)
- 【實證】大類規模：Dramatic Music 99,463 首、Action and Crime 52,912、Military 5,415、Horror 13,713、Drum Music 4,143；全站標示「1,054,000+ Music Tracks Online Including 122,800 Vocal Tracks」。— [AudioSparx Drama genres](https://www.audiosparx.com/sa/links/dramatic-music-genres.cfm)；[Mood 頁](https://www.audiosparx.com/sa/display/displayby.cfm/target.mood)

**樂器詞表（AudioSparx Instrument Search）**
- 【實證】Strings 類有 `Pipa`、`Ruan`、`Guqin`、`Guzheng`、`Koto`、`Zither`、`Erhu`、`Yang Qin`、`Hammered Dulcimer`；Woodwinds 類有 `Bamboo Flute`、`Shakuhachi`、`Dizi / D'Tzu`、`Pan Flute`、`Shawm`、`Sho`、`Ocarina`；Percussion 類有 `Taiko Drums`、`Big Toms`、`Bass Drum`、`Field Drum`、`Indigenous Drums`、`Bells`、`Carillon`、`Handbells`、`Chimes`、`Chinese Gongs`、`Gong`、`Tamtam`、`Temple Blocks`、`Clapper`、`Claves`、`Cymbals`、`Wind Chime`、`Metallophone`。**詞表裡沒有** Xun、Xiao、Sheng、Suona、Banhu、Bianzhong、stone chime、bangzi。— [AudioSparx Instrument Search](https://www.audiosparx.com/sa/display/displayby.cfm/target.instrument)
- 【實證】各樂器頁顯示的曲目數（Erhu 397、Pipa 365、Guzheng 263、Guqin 222、Dizi 259、Shawm 196、Sho 308、Ocarina 327、Taiko Drums 294、Chinese Gongs 373、Clapper 347、Temple Blocks 270、Yang Qin 319）和常見樂器差不多（Piano 441、Violin 403、Flute 451），但全站有 100 萬首以上。所以這些數字**不是**真實出現頻率，只能證明這些詞存在於 metadata 中。— [AudioSparx Erhu 頁](https://www.audiosparx.com/sa/display/search.cfm/instrument_iid.55/instrument.Erhu/aatemp.0)；[Instrument Search](https://www.audiosparx.com/sa/display/displayby.cfm/target.instrument)

**曲目描述用語（模型在訓練時讀到的自然語言）**
- 【實證】Chinese Action 子類的實際描述範例：
  - 「Grand, ceremonial and majestic royalty free chinese folk background with guzheng, dizi, xiao, quanun, strings, chinese traditional percussion, taiko and stomps」（Slow 67）
  - 「Dramatic, epic, adventurous and full of tension … action / trailer movie orchestral tune with Asian Chinese flavor feat. guzheng, dizi, yangqin, xiao, strings, taiko drums and traditional chinese percussion」（Med Fast 130）
  - 「Energetic, adventurous and festive … chinese folk music with Guzheng, Yangqin, Dizi, strings, erhu, taiko and traditional chinese percussion」
  - 「cinematic orchestral asiatic flavour music with strings, horns, dizy, quanum, taiko and traditional chinese percussion」

  描述的結尾會接 genre 標籤字串，例如「Instrumental, Chinese, Chinese Action」。— [AudioSparx Chinese Action](https://www.audiosparx.com/sa/display/sounds.cfm/soundGroup_iid.1792)
- 【實證】Erhu 頁的曲目描述多半是「cinematic piece featuring Erhu」「Strings, Sarod, Bass, Drums, Piano Pad」這類，常和 sarod、sitar 混用；部分新曲標註「assisted with the help of Ai」。— [AudioSparx Erhu 頁](https://www.audiosparx.com/sa/display/search.cfm/instrument_iid.55/instrument.Erhu/aatemp.0)

**Mood 與 Style 詞表**
- 【實證】Mood 詞表的相關詞：Epic、Heroic、Majestic、Regal、Stately、Noble、Grand、Triumphant、Rousing、Stirring、Solemn、Mournful、Melancholic、Tragic、Somber、Ominous、Foreboding、Dark、Booming、Building、Climactic、Driving、Marching、Pulsating、Mechanical、Intense、Explosive、Meditative、Mystical、Ethereal、Earthy、Sparse、Nostalgic、Reflective、Hopeful、Uplifting、Exotic。— [AudioSparx Mood Search](https://www.audiosparx.com/sa/display/displayby.cfm/target.mood)
- 【實證】Production Style 詞表的相關詞：Oriental / Asian（同時出現在 Cultural & Ethnic Style 與 Setting or Scene）、Tribal、World Sorrow、Movie Trailer、Documentary、Section / Opening、Section / Finale、Narrative Cue、History、Military、March、Royal Events、Funeral Procession、Requiem、Tragedy、Romantic Epic、Sci-Fi / Prehistoric、Fanfare、Time-lapse、Slow Motion、Soundscape。— [AudioSparx Style Search](https://www.audiosparx.com/sa/display/displayby.cfm/target.style)

**Freesound 端的參考數字**
- 【實證】2026-10 Freesound 全文搜尋結果數（全部授權 / 只看 CC0）：
  - 弦樂：erhu 133/33、guzheng 53/31、guqin 16/3、pipa 28/6
  - 管樂：dizi 103/32、xiao flute 5/2、**xun 6/0**、ocarina 69/24、**sheng 4/2**、**suona 4**
  - 鐘與石：**bianzhong 0**、bronze bell 240/81、temple bell 233/88、chime stone 12/7、**lithophone 0**
  - 鑼鼓與打擊：chinese gong 245/30、gong 2,575/884、taiko 123/72、chinese drum 203/22、war drum 114/50、chinese percussion 390/33、**bangzi 2**、clapper 104/46、woodblock 167/129
  - 其他：**peking opera 0**、chinese 1,875/948

  SA3 的 Freesound 子集排除了 NC 授權，所以實際進入訓練的數量 ≤ 上述數字。— [Freesound 搜尋（例：erhu）](https://freesound.org/search/?q=erhu)；授權範圍見 [論文 §3.5](https://arxiv.org/html/2605.17991v1)

### Inferences
- 「Chinese Action」「Regal Chinese」「Chinese Folk Ensembles」「Chinese Sad」「Chinese Ethereal」是 AudioSparx 真實的 subgenre 值。寫成 `Genre: Chinese, Subgenre: Chinese Action` 最貼近訓練分佈，但每個子類只有 64–367 首，模型的「中國味」是從很小的樣本學來的，而且明顯偏向**西方作曲家寫的圖庫中國風**（guzheng 加 taiko 加弦樂）。
- 中國特有的鼓樂（關中鑼鼓、威風鑼鼓、秦腔板式）幾乎沒有對應的標籤或樣本。最接近的在分佈內來源是 `Chinese New Years`（153 首，節慶鑼鼓鈸）和 Chinese Action 描述中的 `traditional chinese percussion`。「戰鼓」最可能被模型理解成 `taiko drums` 或 `Dramatic Drums`（好萊塢預告片鼓）。
- `Tempo:` 欄位只要用 AudioSparx 的分級詞（Slow、Medium Slow、Medium、Medium Fast、Fast），就和 BPM 數字互相印證，屬於分佈內寫法。
- Xun、Bianzhong、Suona、Sheng、Bangzi、石磬在兩個資料源都極少或沒有，直接寫原名大概率被忽略，或被 T5 當成未知 token。需要改用替代詞（見 Q5）。

### Gaps
- 無法取得 SA3 實際使用的 AudioSparx metadata 快照或完整欄位清單。HF 上的 `model_config.json` 需要授權（gated，回 401），論文也沒列完整欄位。`Grade: Neutral` 的含義不明，推測是內容分級。`Edit Type`（Full Track / 60sec / Stinger / Bumper / Bed / Loop）是否進了 prompt 無法確認。
- AudioSparx 單一樂器的真實曲目數取不到，樂器頁的數字看起來被截斷在 500 以內。
- 沒有找到 AudioSparx 在 SA3 訓練時點的類別數字，以上全是 2026-10 的數字。

---

## Q2. Repo 的文件與程式碼：提示詞指南、推論參數、Prompt Assistant（reprompt）、文字長度上限

### Takeaway
官方建議所有音樂提示詞都加 `TrackType: Music, VocalType: Instrumental,` 前綴，論文作者也明說「recommend all users」。在 `medium` 這個 post-trained 權重上，**`negative_prompt` 和 `cfg_scale` 都不起作用**，固定 8 步、pingpong sampler。Prompt Assistant 的產出格式是「一句英文長句 + `BPM: X.` + `Length: Y seconds`」，並且會拒收超過 45 個詞或含人聲字眼的輸出。T5Gemma 的文字長度上限是 256 個 token。

### Cited Findings
**前綴與語言**
- 【實證】論文 §5.1 指定音樂用 `TrackType: Music, VocalType: Instrumental,` 前綴、音效用 `TrackType: SFX,`，並寫「We therefore recommend all Stable Audio 3 users to use those prefixes at inference time.」— [論文 §5.1](https://arxiv.org/html/2605.17991v1)
- 【實證】repo 指南說 `TrackType: Music, VocalType: Instrumental` 「tends to produce higher quality, more semantically coherent outputs」；單一樂器或分軌建議以 `TrackType: Instrument` 開頭，多樂器可加 `Format: Duo`。— [docs/guides/prompting.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md)
- 【實證】「Trained on English descriptions; other languages will underperform」。— [docs/guides/model-overview.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/model-overview.md)

**推論參數：negative prompt、CFG、步數**
- 【實證】`cfg_scale` 和 `negative_prompt` 被歸在「**Base models only** … these parameters have no effect on post-trained checkpoints」。`steps` 預設 8，「going higher than 8 doesn't necessarily increase quality」，只有 `-base` 模型才建議 50 步。— [docs/workflows/inference.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/workflows/inference.md)
- 【實證】論文 §4：「Our model does not require classifier-free guidance (CFG) at inference … guidance is baked into the model through distillation」。post-trained 模型用 8 步 PingPong sampler。— [論文 §4、§5.1](https://arxiv.org/html/2605.17991v1)
- 【實證】Gradio 介面對 rf_denoiser（post-trained）把 CFG 預設成 1.0，base 模型才預設 7.0。— [stable_audio_3/interface/diffusion_cond.py L363](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/diffusion_cond.py)

**時長**
- 【實證】`duration` 預設 120 秒。生成時會多算 `duration_padding_sec=6.0` 秒再截回 duration。— [stable_audio_3/model.py](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/model.py)
- 【實證】Python API `model.generate()` 的 `sample_size` 預設是 5292032（約 120.0 秒），而且 `_adapt_sample_size` 會 `return min(target_audio_samples, sample_size)`。直接用 Python API 要超過 120 秒時，必須傳 `sample_size=model.model_config["sample_size"]`；CLI 和 Gradio 都已經會自動帶入 model config 的值。— [stable_audio_3/model.py L87, L429](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/model.py)；[stable_audio_3/cli.py L270](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/cli.py)
- 【實證】GitHub issue #42：CLI 曾經不管 `--duration` 多少都只輸出 2:00，維護者在 2026-06-05 修好。— [Issue #42](https://github.com/Stability-AI/stable-audio-3/issues/42)
- 【實證】medium 的最大時長，資料互相矛盾：
  - `model-overview.md` 寫 medium「~4.75min」、large「~6.3min」。— [model-overview.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/model-overview.md)
  - `prompting.md` 寫 medium 可到 6m20s。— [prompting.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md)
  - 論文 Table 1 寫 medium 和 large 都是 6m20s。— [論文](https://arxiv.org/html/2605.17991v1)
  - ComfyUI 文件寫「up to ~6:20」。— [ComfyUI docs](https://docs.comfy.org/tutorials/audio/stable-audio/stable-audio-3)

**Init audio、Inpainting、Continuation**
- 【實證】`init_noise_level` 範圍 0–1，預設 1.0（完全不參考原音）；0.1 是很接近的變奏，0.5 是一半一半。「as you increase the amount, more lower-level features like melody and rhythm get filtered out, leaving higher-level features like timbre and tonality」。— [inference.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/workflows/inference.md)；[prompting.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md)
- 【實證】timbre transfer 範例的數值兩邊不一致：repo 寫 violin→heavy metal guitar 用 0.4；Stability 官網指南寫同一個例子用 0.82，並說常用範圍是 0.3（幾乎不變）到 0.9（大幅改變）。— [prompting.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md)；[Stability Prompt Guide](https://stability.ai/guides/stable-audio-3-prompt-guide)
- 【實證】Inpainting 用 `inpaint_mask_start_seconds` 和 `inpaint_mask_end_seconds`，可以傳 list 一次修多段。Continuation 的做法是把 mask start 設成原音長度、duration 設成更長。「The audio context matters more than the prompt」；只遮幾秒時，輸出會很接近原音；「Prompts work best when plausible given the surrounding context」。— [inference.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/workflows/inference.md)；[prompting.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md)
- 【實證】論文 §3.2：所有模型都同時訓練生成與 inpainting，mask 比例是 80% 全遮（等於無條件生成）、10% 隨機 1–10 段、10% 因果前綴（continuation）。§5.6：continuation「increases variability in long-range structure」，medium 和 large 的編輯比 small 連貫。— [論文](https://arxiv.org/html/2605.17991v1)
- 【實證】官網 continuation 範例：用 3 秒鳥鳴配上 `TrackType: Music, Lofi hiphop chill beat with melodic synth stabs and pitch-shifted bird song that builds.` 延伸到 55 秒。— [Stability Prompt Guide](https://stability.ai/guides/stable-audio-3-prompt-guide)

**Prompt Assistant（`reprompt.py`）**
- 【實證】Gradio 的 Prompt Assistant 用 `Qwen/Qwen3.5-2B`，參數 `max_new_tokens=128`、`temperature=1.11`、preset 設為 "Auto"。— [diffusion_cond.py L335, L587](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/diffusion_cond.py)
- 【實證】流程：先用 Classifier system prompt 把輸入分成 music_genre、instrument、sound、one_shot 四類；若輸入已含 `TrackType: Music` 加 `VocalType: Instrumental`，直接走 Music 模板。輸出後依類別加前綴：music 加 `"TrackType: Music, VocalType: Instrumental, "`，instrument 加 `"TrackType: Instrument, "`，sfx 加 `"TrackType: SFX, "`。— [stable_audio_3/interface/reprompt.py](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/reprompt.py)
- 【實證】Music 模板的 system prompt 原文：

  > 「You are an expert musician and musicologist and prompt engineer. Transform the user's input into a detailed, vivid music prompt for a full instrumental track. 1. Start with the genre or style and optional adjectives … 2. List the main instruments that define the track. 3. Add supporting elements or layers such as pads, harmonics, effects, or field recordings. 4. Include rhythm or percussion elements … 5. Integrate mood and energy naturally in the sentence … 6. Specify the BPM. 7. Specify the track length as an integer in seconds. Use ranges: energetic/dance 120-180s, pop/rock 180-210s, cinematic/ambient 240-300s. 8. Combine all elements into one natural, fluid sentence. Avoid semicolons.」

  樣板：「Genre/Style with main instruments, supporting instruments/layers, and rhythm/percussion creating mood/energy. BPM: X. Length: Y seconds」。— [reprompt.py L193-205](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/reprompt.py)
- 【實證】Music 模板中與本片最接近的範例：
  - 「Horror cinematic track with dissonant strings, eerie piano stabs, cinematic percussion including taiko and low toms, and synth FX producing suspenseful creepy tension. BPM: 90. Length: 240 seconds」
  - 「Cinematic Sci-Fi score with dramatic horn section, building marcato strings, gliding bassoon, thunderous cymbals, subdued timpani, and subtle synth drones producing awe-inspiring, uplifting, epic intergalactic energy. BPM: 100. Length: 220 seconds」
  - 「Tribal percussion ensemble with congas, djembes, bongos, shakers, and frame drums layered with deep synthetic sub-bass in complex polyrhythms. BPM: 100. Length: 140 seconds」
  - 「Dark ambient track with drones, distant bells, low rumbles, soft wind textures, and synth pads producing eerie immersive tension. BPM: 50. Length: 300 seconds」

  — [reprompt.py](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/reprompt.py)
- 【實證】Instrument 模板的相關範例：
  - 「Timpani hits loop, cinematic, with deep resonant kick-like timpani strikes on beat one, rolling snare-style timpani fills, and no hi-hats for a grand orchestral feel. BPM: 70. Length: 8 seconds」
  - 「Koto plucked motif loop with resonant wooden strings. BPM: 90. Length: 8 seconds」
  - 「Ethnic flute motif for cinematic use. BPM: 80. Length: 30 seconds」
  - 「Ethnic drum ensemble motif loop with booming natural-skin bass drum kicks …」

  — [reprompt.py](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/reprompt.py)
- 【實證】Classifier 的範例樂器清單包含 erhu、koto、shamisen、shakuhachi、pan flute、ocarina、bamboo flute、zither、dulcimer、hammered dulcimer、timpani、gong hit、bell toll、church bell、woodblock；genre 清單包含「Chinese pop, cinematic, soundtrack, orchestral」。— [reprompt.py L44-53](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/reprompt.py)
- 【實證】品質過濾 `_has_artifacts()`：輸出若含 `[ ] * #`、或命中人聲正則 `\b(vocals?|singing|singer|female|male|voice|voices|chorus|rap|rapper|chant(ing)?|lyrics?)\b`、或結尾不是 `. Length: N seconds`、或**超過 45 個詞**，就重抽，最多 5 次。— [reprompt.py L392-406](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/reprompt.py)
- 【實證】Gradio 收到 Assistant 的結果後，會用 `_LENGTH_EXTRACT_RE` 把結尾的 `Length: N seconds` 剝掉，改設成 duration 滑桿的值。也就是說，**送進模型的文字不含 Length**，時長走 `seconds_total` 條件。— [diffusion_cond.py L22, L588-592](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/diffusion_cond.py)

**文字編碼器長度上限**
- 【實證】論文 §2.2：「Text is encoded by a T5Gemma (google/t5gemma-b-b-ul2) frozen encoder into a sequence of 256 embeddings of dimension 768 … Short prompts are padded to 256 with a learned padding embedding, and long prompts are truncated to 256.」— [論文 §2.2](https://arxiv.org/html/2605.17991v1)
- 【實證】repo 的校準腳本寫明 cross-attention 條件是「257-token `cross_attn_cond` (`[t5(256) | seconds(1)]`)」。`conditioners.py` 裡 `max_length=128` 只是 class 的預設值，實際值由 model config 覆蓋。— [optimized/tensorRT/build/make_calib.py](https://github.com/Stability-AI/stable-audio-3/blob/main/optimized/tensorRT/build/make_calib.py)；[stable_audio_3/models/conditioners.py L169](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/models/conditioners.py)

**長度與內容的偏差**
- 【實證】論文 §5.4：「long training examples are predominantly ambient or classical music」，所以「conditioning on long durations can bias the model toward generating ambient or classical music」；同時「most short training samples are loops」。— [論文 §5.4](https://arxiv.org/html/2605.17991v1)

### Inferences
- 【建議】在 `medium` 上要避免人聲質感，**只能靠正面寫法**：加 `VocalType: Instrumental`，並且完全不寫 reprompt 黑名單裡的詞（choir、chant、chanting、voice、vocal、chorus、male、female），也不要寫 `Folk Opera`、`Buddhist Temple`、`Tibetan` 這類容易帶出誦經或戲曲人聲的 subgenre。寫 negative prompt 沒用。
- 【建議】`Length:` 不要寫進送給模型的文字，用 `duration` 參數控制。`BPM: X` 或「X BPM」則應該寫進文字。
- 【建議】鼓樂 cue 的 duration 先設 60–120 秒：更長容易滑向 ambient 或古典（§5.4），太短（30 秒以下）容易生成 loop。需要更長時再用 continuation 往後接。
- 【建議】用 Python API 生成超過 120 秒時，記得傳 `sample_size=model.model_config["sample_size"]`，否則會被默默截在約 120 秒。

### Gaps
- `model_config.json`（gated）讀不到，無法直接確認 `max_length=256` 與 medium 的 `sample_size`。256 這個數字來自論文和校準腳本的雙重證據。
- 官方沒有給 BPM 或調性遵循度的量化評估。

---

## Q3. 社群對 SA3（以及標明的 Stable Audio Open／2.x）在世界樂器、打擊樂、結構、速度、人聲、跨生成一致性方面的發現

### Takeaway
SA3 發佈才 5 個月，社群證據很少。**沒有找到任何針對中國或世界樂器的公開實測。** 少數評測的共同點是：同一提示詞換 seed 的變化很小（節奏幾乎一樣），要變化就得改字；整曲結構和段落發展偏弱；有強烈節奏個性的曲風容易被「平均化」。

### Cited Findings
- 【社群實測】Reddit（u/MFGREBEL，2026-05，ComfyUI）：
  - 「Very coherent but VERY limited in seed variation … running the same prompt on 3 different seeds essentially gives the same output with a SLIGHTLY different melody.」
  - 「Rhythm percussion will pretty much be exact.」
  - 「changing prompt slightly can rearrange the output.」
  - 2:40 長的曲子約 60 秒生成完，約 16GB VRAM。

  — [Reddit 快照](https://reddit.sentinel-team.org/posts/1tjih4x/snapshots/2026-05-21T18%3A20%3A48.87163Z)
- 【社群實測】Dubspot 評測（2026-05-26，Marcus Feld）：
  - 「Ambient drones, foley and SFX, instrumental loops, and atmospheric beds come out well.」
  - 「Song structure and progression are weaker than what the competition delivers at the full-track level.」
  - 鼓打貝斯這類節奏曲風的驚喜感「tends to flatten into the average」。
  - 「the same prompt across multiple seeds often produces near-identical melodies with slightly different decorations.」

  — [Dubspot review](https://blog.dubspot.com/stable-audio-3-review)
- 【實證】GitHub issue #14：Gradio 的 `seed=-1` 曾因字串和整數比對錯誤，變成**固定的決定性 seed**，同提示詞兩次輸出逐 byte 相同。已在 2026-05-07 由 PR #16 修正。— [Issue #14](https://github.com/Stability-AI/stable-audio-3/issues/14)
- 【實證】GitHub issue #50：有使用者問怎麼用提示詞關掉 guitar behind-the-bridge 技法，至今沒有回覆，說明「排除某個元素」沒有官方解法（negative prompt 在 post-trained 無效）。— [Issue #50](https://github.com/Stability-AI/stable-audio-3/issues/50)
- 【社群實測】issue #42 中有使用者用「Bass house, 125 BPM, G minor, Ibiza club anthem.」這種把調性寫進 prompt 的格式，但沒有回報調性是否被遵循。— [Issue #42](https://github.com/Stability-AI/stable-audio-3/issues/42)
- 【實證】HF 模型討論區只有 4 個公開主題（商用授權、binaural、ROCm 等），沒有提示詞討論。— [HF discussions](https://huggingface.co/stabilityai/stable-audio-3-medium/discussions)
- 【實證】ComfyUI 的 Medium 工作流內建「category-aware reprompt template」（Qwen 擴寫），需要 `qwen3.5_2b_bf16.safetensors`。— [ComfyUI docs](https://docs.comfy.org/tutorials/audio/stable-audio/stable-audio-3)
- 【實證／Stable Audio Open，僅供對照】Stable Audio Open（2024）定位是短樣本與音效，「not optimised for full songs, melodies or vocals」，訓練資料是 Freesound 和 Free Music Archive，最長 47 秒。搜尋中沒有找到它在 erhu、guzheng 等中國樂器上的實測。— [Stability：Introducing Stable Audio Open](https://stability.ai/news/introducing-stable-audio-open)

### Inferences
- 「seed 變化小」不是 issue #14 那個 bug 造成的。那個 bug 只影響 Gradio，而且 2026-05-07 已修好；Reddit（ComfyUI，2026-05-21）和 Dubspot（2026-05-26）的回報都在修正之後，Reddit 也不是用 Gradio。所以這比較可能是蒸餾或對抗後訓練模型本身的特性，與論文 §4「guidance baked into the model」相符。
- 【建議】seed 變化小對本片反而是好事：同一個「鼓的措辭」在 11 個 cue 間保持一字不改，有機會得到可辨識的共同節奏身份；旋律樂器的用詞則依時代替換。要多個候選版本時，改提示詞的細節（形容詞、樂器順序），不要只換 seed。
- 【建議】中國鑼鼓那種有特定板式的節奏（例如關中鑼鼓的急急風），很可能被平均成泛用的預告片鼓。期望值要放在「中國色彩的史詩鼓」，不是「道地鑼鼓經」。
- 【建議】結構弱，代表 build-up → climax → ending 這種弧線最好分段完成：先生成主體，再用 continuation 接高潮段、用 inpainting 改寫結尾，不要指望一次提示就出完整敘事弧。

### Gaps
- 沒有找到任何中國、日本或其他非西方樂器在 SA3 上的公開聽測或提示詞分享（Reddit、HF、GitHub、部落格都沒有）。
- 沒有找到 BPM 遵循度、調性遵循度、結尾自然收束的量化或質化評測。
- 沒有找到用 init_audio 維持跨 cue 風格一致的社群經驗分享。

---

## Q4. 標籤格式（`TrackType: …`、`Genre:`、`Instruments:`）比自然語言好，還是混用？建議長度多少？

### Takeaway
兩種寫法都在訓練分佈內，混用也沒問題。訓練時 AudioSparx 的 prompt 有 50% 帶欄位名（`Instruments: …`）、50% 不帶，欄位會隨機抽子集、打亂順序，用逗號串起來，並且 50% 全部轉小寫。前綴 `TrackType: Music, VocalType: Instrumental,` 是官方唯一明確推薦必加的部分。長度方面，Stability 自家 Assistant 把擴寫上限卡在 45 個英文詞，硬上限是 256 個 T5 token。

### Cited Findings
- 【實證】論文 §3.5：「For AudioSparx, with 50% probability, the metadata field identifier is prepended (Instruments: Guitar, Drums, Bass Guitar, Moods: Uplifting) or omitted.」「prompts are constructed by concatenating a random subset of available metadata fields」「with 50% probability, all candidate fields are shuffled or randomly subsampled」「fields are joined with commas and, with 50% probability, the entire prompt is lowercased」。Freesound 則有 50% 機率用 LLM 改寫的 caption。— [論文 §3.5](https://arxiv.org/html/2605.17991v1)
- 【實證】官網指南說 tags 是 optional，「not required in every prompt」，並建議的順序是：genre → 主奏樂器與節奏元素 → mood、編曲與製作質感 → 年代、地點、錄音方式或使用情境等參照。— [Stability Prompt Guide](https://stability.ai/guides/stable-audio-3-prompt-guide)
- 【實證】repo 指南的 Music 範例是 60–90 詞的長段散文，並說「more detail generally means better results」。— [prompting.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md)
- 【實證】Assistant 會拒收超過 45 個詞的輸出，模板要求「one natural, fluid sentence. Avoid semicolons.」— [reprompt.py](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/reprompt.py)
- 【實證】文字上限 256 個 T5Gemma token，超出部分截斷。— [論文 §2.2](https://arxiv.org/html/2605.17991v1)
- 【實證】HF 模型卡的範例用「House music that encapsulates the feeling of being at a festival … 124 BPM」這種「散文 + BPM」的寫法。— [HF 模型卡](https://huggingface.co/stabilityai/stable-audio-3-medium)

### Inferences
- 【建議】推薦的「混合式」骨架如下（大約 40–70 個英文詞，遠低於 256 token）：
  `TrackType: Music, VocalType: Instrumental, Genre: <…>, Subgenre: <…>, Instruments: <3–6 個>, Moods: <2–4 個>, Tempo: <分級詞>, BPM: <數字>, <一句 20–35 詞的散文，描述編曲動態與用途>`
  - 標籤段負責把模型拉到 AudioSparx 的分佈（類別、樂器、情緒、速度）。
  - 散文段負責描述標籤表達不了的東西：誰主奏、何時進鼓、要不要漸強、什麼場景。
- 【建議】最重要的詞放前面。截斷發生在尾端；同時訓練時欄位是打亂的，所以順序本身的語意影響可能有限，主要是避免超長。
- 【建議】Instruments 欄位別列超過約 6 個。列太多時，每個樂器的權重被稀釋，罕見的中國樂器最先被吃掉。

### Gaps
- 沒有官方或社群的 A/B 數據比較「純標籤、純散文、混合」三種寫法的 CLAP 或聽感差異。

---

## Q5. 具體建議：每種樂器該用哪個英文詞、失敗時的備援詞，以及 11 個 cue 的提示詞草案

### Takeaway
在 AudioSparx 詞表內、或常見於 Chinese Action 描述中的詞，應該優先用：guzheng、erhu、pipa、dizi、bamboo flute、yangqin、Chinese gongs、taiko drums、traditional chinese percussion、temple blocks、clapper、shawm、sho、ocarina。不在詞表內的樂器要換成功能相近的替代詞：xun→ocarina；suona→shawm；sheng→sho／free reed mouth organ；bianzhong→bronze temple bells／chimes；bangzi→wooden clapper／woodblock；石磬→stone chimes 加 woodblock 或 gong 的備援。以下全部是根據詞彙存在與否做的**推論，尚未實際生成驗證**。

### Cited Findings
- 【實證】詞表中有的樂器詞與 genre 字串，見 Q1：[AudioSparx Instrument Search](https://www.audiosparx.com/sa/display/displayby.cfm/target.instrument)、[Chinese Music](https://www.audiosparx.com/sa/display/submain.cfm/soundGroup_iid.4771)、[Drum Music](https://www.audiosparx.com/sa/display/submain.cfm/soundGroup_iid.5082)。
- 【實證】Chinese Action 的描述中，guzheng、dizi、xiao、yangqin、erhu、taiko、stomps、traditional chinese percussion 多次並列出現。— [AudioSparx Chinese Action](https://www.audiosparx.com/sa/display/sounds.cfm/soundGroup_iid.1792)
- 【實證】Freesound 搜尋數：xun 6、suona 4、sheng 4、bangzi 2、bianzhong 0、lithophone 0、guqin 16、temple bell 233、bronze bell 240、chinese gong 245、woodblock 167、clapper 104。— [Freesound search](https://freesound.org/search/?q=erhu)
- 【實證】Stability Assistant 的 Classifier 範例樂器包含 erhu、koto、shakuhachi、ocarina、bamboo flute、zither、hammered dulcimer、gong hit、bell toll、woodblock，代表官方預期使用者會輸入這些詞。— [reprompt.py](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/reprompt.py)

### Inferences

#### A. 樂器詞對照表【建議，未經生成測試】

| 樂器 | 首選英文詞 | 依據（AudioSparx 詞表／Freesound 數） | 失敗時的備援詞 |
|---|---|---|---|
| 戰鼓 Chinese war drums | `huge Chinese war drums`、`taiko drums`、`big toms` | Taiko Drums、Big Toms、Bass Drum 在詞表；Taiko 子類 30 首；Dramatic Drums 400–600 首；war drum 114 | `epic trailer drums`、`booming low drums`、`stomps`、`timpani` |
| 關中鑼鼓（鼓加大鑼大鈸） | `traditional chinese percussion`、`Chinese gongs and cymbals`、`Chinese New Year drums` | Chinese Gongs、Cymbals 在詞表；Chinese New Years 153 首；chinese percussion 390 | `lion dance drums, gongs and cymbals`（推測）、`crash cymbals, tam-tam` |
| 梆子 bangzi | `wooden clapper`、`woodblock` | Clapper、Temple Blocks、Claves 在詞表；bangzi 2、woodblock 167 | `temple blocks`、`claves`、`sharp wooden clicks` |
| 塤 xun | `ocarina`（加上 `low breathy clay vessel flute`） | 詞表沒有 Xun，有 Ocarina；xun 6、ocarina 69 | `breathy low flute`、`shakuhachi`（偏日本氣口） |
| 古箏 guzheng | `guzheng` | 在詞表，而且是 Chinese Action 描述的核心詞；53/31 | `Chinese zither`、`koto`（偏日本） |
| 古琴 guqin | `guqin`（加上 `low plucked, harmonics, sparse`） | 在詞表；Freesound 只有 16 筆，可能被當成 guzheng | `low Chinese zither`、`koto` |
| 笛子 dizi | `dizi`、`Chinese bamboo flute` | 詞表有 Dizi / D'Tzu、Bamboo Flute；dizi 103 | `bamboo flute`、`ethnic flute` |
| 簫 xiao | `xiao`（只出現在描述散文中）加 `bamboo flute`、`soft breathy` | 詞表沒有 Xiao；xiao flute 5 | `bamboo flute`、`shakuhachi`、`low flute` |
| 琵琶 pipa | `pipa`、`pipa tremolo` | 詞表有 Pipa、Ruan；Freesound 28 | `Chinese lute`、`lute tremolo` |
| 二胡 erhu | `erhu` | 在詞表，Classifier 範例也有；133/33 | `Chinese fiddle`、`solo violin`（失去中國味） |
| 板胡 banhu | `erhu` 加 `bright, nasal, piercing, high register` | 詞表沒有 Banhu | `erhu`、`fiddle` |
| 笙 sheng | `sho`（日本笙）或 `free reed mouth organ` | 詞表有 Sho，沒有 Sheng；sheng 4 | `reed organ`、`harmonium drone`、`accordion pad` |
| 嗩吶 suona | `shawm`、`Chinese shawm` | 詞表有 Shawm，沒有 Suona；suona 4 | `piercing double reed`、`oboe`（較溫和） |
| 編鐘 bianzhong | `bronze temple bells`、`tuned bronze bells` | 詞表有 Bells、Chimes、Carillon、Handbells；bianzhong 0；bronze bell 240、temple bell 233 | `chimes`、`tubular bells`、`gong`、`bell toll` |
| 石磬 stone chimes | `stone chimes` 加 `resonant struck stone` | chime stone 12；lithophone 0 | `woodblock`、`low gong`、`temple blocks`（質感近似但不準） |
| 揚琴 yangqin（補充） | `yangqin` 或 `Yang Qin` | 在詞表，Chinese Action 描述常用 | `hammered dulcimer` |

**通則【建議】**
- 罕見樂器不要單獨扛主奏。讓 guzheng、erhu、dizi、taiko 這類高頻詞當骨架，再把罕見詞（xun、bells）放進去「染色」。
- 一個 cue 最多 1–2 個罕見樂器詞。
- 一個詞連續失敗兩三次，就直接換備援詞，不要堆更多形容詞。

#### B. 避免人聲與戲曲質感【建議】
- 一律帶 `VocalType: Instrumental`。
- 不寫 choir、chant、chanting、monks、opera、Peking opera、Qinqiang、vocal、voice、chorus。
- 不用 `Buddhist Temple`、`Chinese Folk Opera`、`Tibetan` 當 Subgenre（前兩者是 AudioSparx 真實子類，裡面可能有人聲或誦經）。
- 要「廟宇感」時，改寫 `temple bells, meditative, sparse`。

#### C. 結構控制（起、承、高潮、收尾）【建議】
- 散文段用 AudioSparx 的 Mood 詞與 Style 詞描述弧線：`Building`、`Climactic`、`Section / Opening`、`Section / Finale`；或用 reprompt 範例式的寫法「builds to a thunderous climax」「ends with a final gong hit」。預期只會部分遵循（見 Q3 的「結構弱」）。
- 比較可靠的做法：
  1. 先生成 60–90 秒的主體。
  2. 用 continuation（mask start = 原長度）配上「… that builds to a massive climax」接出高潮段。
  3. 再用 inpainting 把最後 5–10 秒改寫成「final gong hit and long decay」。
  4. 依官方指南的提醒，「先遮大範圍再縮小」。

#### D. 速度與調性【建議】
- BPM 同時寫數字（`BPM: 72`）和 AudioSparx 分級詞（`Tempo: Slow`），兩者互相印證。
- 調性（key）不在論文列的 metadata 欄位中，AudioSparx 曲目列表也沒有 key 欄位，預期遵循度低。需要對調時，在後製用 pitch shift 處理。

#### E. 11 個 cue 之間的一致性【建議】
1. **共用骨架**：前綴、`Genre: Chinese`、鼓的措辭（例如 `huge Chinese war drums, taiko, traditional chinese percussion`）在所有鼓樂 cue 中保持一字不改；只替換 Subgenre、旋律樂器、Moods、Tempo、BPM。
2. **固定 seed**：每個 cue 先選定一個 seed，再微調文字（Q3：seed 影響小、措辭影響大）。
3. **init_audio 傳承母題**：把前一個 cue 中滿意的段落當 `init_audio`，用 0.5–0.7 生成下一個 cue，保留音色與調性、改換節奏與編制。需要大幅換風格時試 0.8 左右（官網 timbre transfer 用 0.82，repo 用 0.4，數值要自己調）。
4. **轉場**：把 cue A 的最後 10–20 秒和 cue B 的開頭拼起來，對中間 4–8 秒做 inpainting，配上描述 B 的提示詞，讓模型自己縫合。

#### F. 11 個 cue 的提示詞草案【建議，全部未經生成測試】
以下長度約 45–70 個英文詞。`duration` 另外設定，不寫進文字。

1. **新石器（半坡、塤、陶鼓）**
   `TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Ethereal, Instruments: Ocarina, Indigenous Drums, Bamboo Flute, Moods: Earthy, Mystical, Sparse, Tempo: Slow, BPM: 66, primitive ritual soundscape with a low breathy clay ocarina melody over soft hand-struck earthen drums and distant wooden clicks, ancient and timeless.`
2. **秦帝國（戰鼓、編鐘、肅殺）**
   `TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Action, Instruments: Taiko Drums, Chinese Gongs, Bells, Shawm, Moods: Epic, Powerful, Stately, Marching, Tempo: Medium Slow, BPM: 90, huge Chinese war drums and traditional chinese percussion drive a disciplined imperial march, bronze temple bells strike on the downbeats, a piercing shawm calls over thunderous toms.`
3. **焚城（混亂、毀滅）**
   `TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Edgy, Instruments: Taiko Drums, Chinese Gongs, Tamtam, Erhu, Moods: Chaotic, Dark, Tragic, Explosive, Tempo: Medium Fast, BPM: 132, frantic Chinese war drums and crashing gongs collapse into chaos, a screaming erhu over roaring low tam-tam swells, a city burning.`
4. **漢（雄渾、莊重）**
   `TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Regal Chinese, Instruments: Guqin, Bells, Bamboo Flute, Big Toms, Moods: Majestic, Noble, Solemn, Tempo: Slow, BPM: 72, dignified Han court music with sparse low guqin, resonant bronze bells, a calm bamboo flute and slow ceremonial drums, grand and restrained.`
5. **唐（華麗、開放）**
   `TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Folk Ensembles, Instruments: Pipa, Guzheng, Dizi, Sho, Moods: Glorious, Festive, Elegant, Tempo: Medium, BPM: 108, cosmopolitan Tang dynasty court ensemble, bright pipa tremolo and guzheng runs, soaring dizi, shimmering sho chords and lively hand drums, golden and confident.`
6. **明清（市井、梆子）**
   `TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Folk Ensembles, Instruments: Erhu, Clapper, Chinese Gongs, Yang Qin, Moods: Lively, Earthy, Nostalgic, Tempo: Medium, BPM: 112, bustling old town street music, nasal bright erhu, sharp wooden clapper rhythms, small gongs and cymbals, rippling yangqin, folksy and warm.`
7. **1936–1958 鐵路與紡織廠**
   `TrackType: Music, VocalType: Instrumental, Genre: Chinese, Instruments: Erhu, Strings, Field Drum, Piano, Moods: Determined, Mechanical, Hopeful, Tempo: Medium, BPM: 116, industrious documentary score, rhythmic mechanical ostinato like looms and train wheels, marching snare, erhu melody over string section, hopeful nation building.`
8. **1975–1991**
   `TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese New Age, Instruments: Dizi, Synthesizer, Piano, Strings, Moods: Hopeful, Reflective, Warm, Tempo: Medium Slow, BPM: 92, 1980s reform era documentary music, soft analog synth pads, gentle piano, dizi melody, warm strings, optimistic and nostalgic.`
9. **1998 衰退**
   `TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Erhu, Piano, Strings, Moods: Melancholic, Lonely, Somber, Tempo: Slow, BPM: 64, quiet elegy for closed factories, lonely erhu over sparse piano and low strings, distant wooden clapper ticks like a clock, bittersweet and empty.`
10. **2005–2014**
    `TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Corporate, Instruments: Guzheng, Piano, Strings, Percussion, Moods: Uplifting, Driving, Inspiring, Tempo: Medium, BPM: 118, modern cinematic build with pulsing strings, guzheng ostinato, piano and light Chinese percussion, a rising city, forward motion.`
11. **2019–2026 終曲（回扣戰鼓）**
    `TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Action, Instruments: Taiko Drums, Chinese Gongs, Bells, Erhu, Synthesizer, Moods: Triumphant, Epic, Climactic, Tempo: Medium Slow, BPM: 90, huge Chinese war drums and traditional chinese percussion return with bronze temple bells, erhu theme over modern synth pulses, builds to a massive final climax and a last gong hit.`

**用法提醒**
- cue 7 故意不寫 Subgenre：AudioSparx 的 Chinese Dramatic 下沒有對應「工業建設」的子類（實際值只有 Chinese Action、Edgy、Ethereal、Happy、Sad）。可以分別加 `Subgenre: Chinese Action` 或 `Subgenre: Chinese Happy` 做對照測試。`Field Drum` 是 AudioSparx 詞表裡的軍鼓類詞。
- cue 2 和 cue 11 刻意共用「huge Chinese war drums and traditional chinese percussion」以及 BPM 90，方便用 init_audio 把 cue 2 的鼓帶到終曲。

### Gaps
- 以上所有樂器詞與 cue 草案都**沒有實際生成驗證**。每個罕見樂器詞（xun、bianzhong、suona、sheng、bangzi、石磬）是否真的被識別，必須小批量實測才知道（例如每詞 3 個 seed、30 秒、`TrackType: Instrument` 單奏）。repo 支援 per-batch 自訂：`prompt` 可以傳 list，搭配 `batch_size=4`，一次呼叫就能比較 4 種措辭（例如 `xun` / `ocarina` / `low breathy clay vessel flute` / `ocarina, low breathy clay vessel flute`）。— [inference.md「Per-batch customization」](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/workflows/inference.md)
- 「lion dance drums」「Chinese New Year drums」能否引出鑼鼓質感，是基於 AudioSparx 有 Chinese New Years 子類（153 首）所做的推測，沒有直接證據。
- 用 LoRA 微調中國鑼鼓或秦腔板式在技術上可行（repo 提供 LoRA 訓練，在 base 上訓練，可套用到 post-trained），但本研究沒有評估資料需求與效果。— [docs/workflows/lora.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/workflows/lora.md)；[model-overview.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/model-overview.md)

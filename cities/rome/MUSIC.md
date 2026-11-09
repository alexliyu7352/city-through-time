# 羅馬配樂候選授權

## 定版：五個樂章與獨立來源

使用者定稿為 **B／A／A／B／B**，gain依次 **−5／−8／−11／−9／−6 dB**。第二、三樂章在14f之上再降2 dB，第四再降3 dB，第一、五不變；全樂章一起降，沒有另加「只在旁白激昂時壓低」的規則。原有剪法、offset、fade與lift_db保留。母帶採用使用者確認的B方式，包含有效的配樂bus壓峰值及修好接縫的旁白。

| Cue／take | 起訖秒數 | gain |
| --- | --- | ---: |
| R14_01 B | 23.270–282.652 | −5 dB |
| R14_02 A | 282.652–472.210 | −8 dB |
| R14_03 A | 472.210–911.112 | −11 dB |
| R14_04 B | 911.112–1492.095 | −9 dB |
| R14_05 B | 1492.095–1808.233 | −6 dB |

六份原始錄音在`assets/audio/music/source/`；全部十個試聽剪輯WAV與配方metadata在`assets/audio/music/cand/`，最終五個剪輯的metadata另在`assets/audio/music/selected_metadata/`。檔案為獨立保存的實體來源，不依賴任何舊候選或暫存目錄。曲目、演奏者、Commons來源頁及公有領域授權記錄保留於本檔下文、`research/music.md`、`research/music_notes/round14_sources.md`和CREDITS；原始錄音與所有剪輯均不進git。

以下逐輪內容是保留的歷史記錄，舊預覽、舊音量和「目前版本」字樣不代表定版，定版以本節及city.yaml為準。收尾僅保存與編譯比對，沒有重混或改變已交付成片。

## 第14f輪：全片配樂降低2 dB（歷史版本）

選曲仍為 **B／A／A／B／B**，剪法、offset、fade與lift_db均不變。五cue的gain依次為 **−5／−6／−9／−6／−6 dB**，各自比14e少2 dB。原生lay重鋪後，PCM整體實測為−2.002 dB；與理想−2 dB波形最大差不到1個16-bit量化階。

[整片預覽](http://127.0.0.1:8766/play.html?city=rome_round14f_all&play=1)｜[五段輕量試聽](http://127.0.0.1:8766/cities/rome_round14f_all/build/audio/music/audition/)。試聽每段12秒，用實際降音量後的score加原旁白，不另正規化；原生audition索引頁只載入音訊、截圖和字幕。

用2秒窗、0.5秒步距，只在有效語音區間比較音樂與旁白的RMS；至少1.2秒有效語音，選不同句且相隔至少30秒的五處。按音樂相對最大聲排序：

| 試聽起訖秒 | 量測窗秒 | 音樂相對旁白 |
| --- | --- | ---: |
| 793.5–805.5 | 798.5–800.5 | -8.99 dB |
| 1065.5–1077.5 | 1070.5–1072.5 | -9.19 dB |
| 1113.5–1125.5 | 1118.5–1120.5 | -9.71 dB |
| 454.5–466.5 | 459.5–461.5 | -10.32 dB |
| 134.5–146.5 | 139.5–141.5 | -12.06 dB |

round對14e：0畫面區段、0模型差異；data、export、旁白及其餘film資料相同，片長1808.233秒。五段的播放、跳轉、字幕及45張圖已用瀏覽器檢查，沒有模型請求；這是播放／量測驗證，未冒稱真人聽審。參數與量測見 `research/rome_round14f_audio_params.json`、`rome_round14f_audio_measure.json`。

舊預覽、試聽混音和未被引用的審查圖已按要求清理；原始錄音、所有剪輯WAV、研究與直接引用的檔案保留。以下是歷史紀錄，舊預覽連結不再作為目前的試聽入口。

## 第14d輪：第4章改用B（歷史版本）

按使用者要求，**R14_04改成B**，目前整片選擇為 **B／A／A／B／B**。[新預覽](http://127.0.0.1:8766/play.html?city=rome_round14d_all&play=1)。第4章仍為911.112–1492.095秒，gain−4 dB、lift_db8、offset0，其他四章維持14c。

以原生lay重鋪音樂，沿用已批准的畫面、字幕與旁白，片長1808.233秒。第4章與其退場交疊範圍外的音樂PCM相同；兩處相鄰交接的原生電平落差仍為3／6 dB。第4章有效有聲半秒窗旁白最小餘量2.90 dB、第5百分位8.80 dB。換曲本身先以原生lay與no-compile檢查確認，畫面未變；其後同輪合併街道穿地標修正，另跑完整 `round.py --against rome_round14c_all`。音樂選擇和參數維持上述設定。

參數與量測：`research/rome_round14d_params.json`、`rome_round14d_measure.json`。以下保留前版紀錄。

## 第14c輪：已選定並鋪入整片

使用者最終選擇 **R14_01 B／R14_02 A／R14_03 A／R14_04 A／R14_05 B**。這份選擇取代較早的A／B／A／A／B，第二章B未採用。

[整片預覽](http://127.0.0.1:8766/play.html?city=rome_round14c_all&play=1)。片長1808.233秒，沿用13d的畫面、字幕、旁白與時軸。五個take已寫入新候選city.yaml的film.music.cues，原生lay產出全片score。

| Cue／take | 起訖秒數 | gain／lift_db |
| --- | --- | --- |
| R14_01 B | 23.270–282.652 | −3／15 dB |
| R14_02 A | 282.652–472.210 | −4／15 dB |
| R14_03 A | 472.210–911.112 | −7／15 dB |
| R14_04 A | 911.112–1492.095 | −4／8 dB |
| R14_05 B | 1492.095–1808.233 | −4／15 dB |

音量沿用14b的弱奏補足及強段設定；五章offset均為0、入場2.5秒，前曲以原生3秒尾韻與後曲交疊。四處交接的原生電平落差約4／1／3／6 dB，未觸發10 dB提示，也未量到持續的數位空白。已選第二章A的尾段完整，音源比章長多6秒，不需換收尾或改剪法。第4章較小補幅為遣送與空房保留層次，第5章疫情窗口仍較復甦窗口輕約9 dB。

整片有效有聲半秒窗的旁白餘量最小2.11 dB、第5百分位9.29 dB，旁白加音樂樣本合峰−5.89 dBFS。這些是量測；真人聽感仍由預覽審定。指定round對13d的結果為0畫面區段、0模型差異，僅score改動。完整參數／精簡量測為 `research/rome_round14c_params.json`／`rome_round14c_measure.json`。

錄音來源與音樂署名已補CREDITS文字檔。片尾畫面保持13d，沒有新增字幕行。原14／14b試聽頁仍保留；以下為前期試聽紀錄。

## 第14b輪：輕量試聽與弱奏補足（試聽紀錄）

[試聽頁](http://127.0.0.1:8766/cities/rome_round14b_music_all/build/audio/music/audition/index.html) 使用897張每2秒一張的圖片、雙語字幕與旁白混音；十版剪法、原始錄音及時軸保持第14輪的版本。十個raw WAV的sha256亦相同。差別說明與24個重點時刻改用原生 `--note`／`--mark`，沒有再套自製的索引頁處理。

| 樂章 | gain | lift_db | 本輪處理 |
| --- | ---: | ---: | --- |
| 1 建城與共和 | −3 dB | 15 | 補足Janiculum長弱奏，保留抒情強段。 |
| 2 帝國與大火 | −4 dB | 15 | 補足原本很輕的低聲推進，不降低整章的強奏。 |
| 3 失去與返城 | −7 dB | 15 | 保留原強段音量，單獨抬高長弱奏。 |
| 4 重建、首都與失去家園 | −4 dB | 8 | 較小的補幅，為遣送與空房保留弱奏層次。 |
| 5 戰後與今天 | −4 dB | 15 | 補足夜曲回聲；所量測疫情窗口仍比復甦窗口低約9 dB。 |

gain均維持第14輪；調整發生在原生lay的長弱奏提升。前三章4秒窗的低位音量約增加5–15 dB。以實際混音聲道量測，有效有聲半秒窗的旁白最小餘量2.15 dB，各版第5百分位最低8.79 dB；十版均未觸發整段峰值縮放。mono旁白轉stereo後兩者同為−27.2 LUFS，總能量不變，採同一聲道口徑比較。完整數據在 `research/rome_round14b_measure.json`。

五cue的take仍未選，offset明寫0.0以保留試聽的start-anchor落點；沒有正式score。第14輪的原試聽頁、音檔及13d影片均保留。新增約221.5 MB，原始WAV相同時安全共用，原生重寫前先解除新候選的共用檔案連結，未寫入舊版。

瀏覽器驗證10個播放、24個重點跳轉、字幕與圖片時間、Copy my picks均通過，未請求模型資源。本機頁面36 ms就緒、點版本81–133 ms起播；這是本機結果，並非其他網路環境的速度承諾。完成的是播放及聲音量測，未宣稱真人聽審。

## 第14輪：雷史畢基／美國海軍陸戰隊樂隊

目前方向是五個樂章、每章兩個剪輯版本，全部待使用者在試聽頁選定；正式片尚未鋪配樂，cue沒有選定take。作曲者為Ottorino Respighi（雷史畢基），演奏者為 **“The President's Own” United States Marine Band**，採用Wikimedia Commons各具體檔案頁的公有領域標示。

《羅馬之松》四樂章來自 *Director's Choice*；頁面日期為2007-08-29，未另列實際錄音日或指揮。《古代舞曲與歌調》第一組曲的可用檔來自 *Web Exclusives*，2010-04-11於美國維吉尼亞州Alexandria的Bishop Ireton High School Auditorium演出，Colonel Michael J. Colburn指揮。本輪剪輯使用其中實際需要的樂章，並非完整組曲原樣播放。

八個檔案頁的逐項核查、下載備援及日期見[本輪來源筆記](research/rome_round14_sources.md)及[JSON](research/rome_round14_sources.json)。依使用者指示，授權核查到Commons頁面標示為止；本輪不延伸作編曲權或地域法律研究。

五章與畫面、旁白的關係見[配樂研究](research/music.md)。短於畫面的錄音會明列回收或重複的片段；第5章在疫情及夜城回收Janiculum，維持同一樂團的聲音。剪接版本、實際來源秒數和量測記在[剪輯表](research/rome_round14_cuts.json)。24kHz來源輸出為48kHz候選，代表符合混音取樣率，沒有因此增加原錄音的頻寬。

### 本輪實際錄音與檔案

以下核查日期均為 **2026-11-07**；作曲者、演奏者與錄音資料見本節開頭。各具體Commons頁均標 **Public domain**，所下載檔案保存在候選的 `build/audio/music/source/`。MP3是同一Commons檔的官方轉碼，雜湊記實際取得的MP3，不冒充原Ogg的雜湊。

| 錄音 | 來源頁／頁面授權 | 實際檔案與秒數 | sha256 |
| --- | --- | --- | --- |
| The Pines of the Janiculum；*Director's Choice* | [Commons](https://commons.wikimedia.org/wiki/File:Respighi_Pines_of_the_Janiculum.ogg) · Public domain | `janiculum.ogg` · 411.672秒 | `d430103b9949f5211417a22896e3d818d2417696330bb2127fa4fb788a11c1e6` |
| The Pines of the Appian Way；*Director's Choice* | [Commons](https://commons.wikimedia.org/wiki/File:Respighi_Pines_of_the_Appian_way.oga) · Public domain | `appian_way.oga` · 319.536秒 | `f3f56ad2749bba88963b9975dda7f5eb7229bdc4b94eea8a924969948007812c` |
| Pines Near a Catacomb；*Director's Choice* | [Commons](https://commons.wikimedia.org/wiki/File:Respighi_Pines_near_a_catacomb.ogg) · Public domain | `catacomb.ogg` · 379.680秒 | `8bd96ea2936b8ac9ecdd3c61d3cf0cdc6fcbbe9e6ba28cafa9180ed5be56e49d` |
| The Pines of Villa Borghese；*Director's Choice* | [Commons](https://commons.wikimedia.org/wiki/File:Respighi_Pines_of_Villa_Borghese.ogg) · Public domain | `villa_borghese.mp3` · 159.723秒 | `49c165a4f7319c32f7493f4f93d0a5e98b0ead879ed52d3f62da09cd02e374b5` |
| Ancient Airs and Dances, Suite No.1: I. Balletto detto Il conte Orlando；*Web Exclusives* | [Commons](https://commons.wikimedia.org/wiki/File:Balletto_detto_Il_conte_Orlando.ogg) · Public domain | `ancient_airs_1.mp3` · 179.515秒 | `92ad24b98785104e03fe9c58de28133ef440369d5956be0fa6c10628ffe1a76e` |
| Ancient Airs and Dances, Suite No.1: III. Villanella；*Web Exclusives* | [Commons](https://commons.wikimedia.org/wiki/File:Villanella.ogg) · Public domain | `ancient_airs_3.mp3` · 292.413秒 | `42f409c73e0a21d785700fa1872ff4c44fdfbaca540d1b730d6309cd08080ea6` |

組曲II、IV僅核對頁面作備選，本輪沒有使用或下載，不列虛構的檔案雜湊。原始錄音全部保留；需跨樂章或重複樂句時，城市專屬腳本先組成可追溯的無損工作音源，再交原生audition工具剪輯和試配。工作音源的暫存FLAC可刪，原檔、組接配方及48kHz WAV候選保留；重建方式在 `research/rome_round14_music.py`，並非新的共享配樂程式。

### 試聽時要留意的地方

原生量測保留了原錄音的弱奏：Janiculum兩版的silent為18%／17%、gap為6.1／12.3秒；Appian Way為52%／38%、gap為46.8／20.3秒；Catacomb A為34%、gap為20.5秒。這些門檻把非常輕的聲音計作silent；候選沒有100ms的數位全零段，也沒有音源用盡。這是保留大動態的剪輯，並未宣稱靜音門檻全部通過，聽選時要比較弱奏在旁白下是否仍有作用。

第5章B的原生低頻能量為1.6%，保留no low end提示；沒有加入原錄音沒有的低音。各版有效半秒旁白窗的聲音高於配樂，最小差3.30dB，各版第5百分位最低9.74dB；旁白與配樂相加的樣本合峰不高於−2.91dBFS。這些是量測，不能代替人對剪接、音色、底噪及清晰度的聽審。使用者選定以前不寫入take，也不輸出正式score。

## 先前候選（保留研究，非本輪選曲）

以下13組各2首及《羅馬之泉》的試聽紀錄已由上述第14輪方向取代，尚未採用。

### M00_a

- 曲名：Volatile Reaction。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Volatile Reaction](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400039)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`ced1148df201a6c69062a96b7ef49c49924572ca5023c2ac5a2d6c5828ecb218`。

### M00_b

- 曲名：The Descent。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[The Descent](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1200094)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`f097d51700b970efffc62499473ea3a31e09aad4172e787978bc9c2a644d53a2`。

### M01_a

- 曲名：Temple of the Manes。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Temple of the Manes](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100053)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`21774c909751472f4fb6621e4cb5d0ac29ae535c4768392d13d2917f7107bcbf`。

### M01_b

- 曲名：Vulcan。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Vulcan](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100525)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`e6291d744dd23a7f5c51a02fa1f6992a69f2816cb998c6709fd29d9060eaa69a`。

### M02_a

- 曲名：Crowd Hammer。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Crowd Hammer](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500064)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`c60cff055f57caf5bf5662ac4c2ad3279e130ddf309c044bd1123ea9eea33556`。

### M02_b

- 曲名：The Pyre。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[The Pyre](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100846)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`3333c6b26dbe96a275051bb4d9089a803e664aefd317c1b5a8118c16fb533179`。

### M03_a

- 曲名：Colossus。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Colossus](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100358)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`34321b47eeac3a181a5cde7f2b28d499d78b22df6cc784272513f82d53cd5c0c`。

### M03_b

- 曲名：All This。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[All This](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1300001)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`15aa40f76bf114748e23452e4659fed30cfb88745efa5d13c7279ea2fc370f12`。

### M04_a

- 曲名：Heavy Heart。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Heavy Heart](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1600002)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`9df6b71e50acc477b37fff31463816cc67f5234a3fdcdc5d02101f33c38b458d`。

### M04_b

- 曲名：Metaphysik。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Metaphysik](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400056)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`e6d3d7993b42b9c0ed948e9683652bbf883f636a9f7496a27279e8c2415a2186`。

### M05_a

- 曲名：Teller of the Tales。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Teller of the Tales](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400020)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`320b37a09fc37ec5962c975563541bee9bcbf1208b0181789248780286f4c1d4`。

### M05_b

- 曲名：Village Consort。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Village Consort](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1700007)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`53861c78cb4c788f83b563d47fb4fa73bf4c66a8786d61215750738d856a8fd2`。

### M06_a

- 曲名：Toccata 3。
- 作者：Girolamo Frescobaldi (1583–1643)。
- 演奏者／錄音製作：Sylvia Kind（大鍵琴）。
- URL：[Toccata 3](https://commons.wikimedia.org/wiki/File:Girolamo_Frescobaldi_-_Toccata_3.ogg)。
- 頁面license：開放授權；錄音[CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/)；作品公有領域（作者逝世已逾100年）。
- 核查日期：2026-11-06。
- 原錄音sha256：`6c2d4e6ec5f66689bcf9f2ee2074397b6046dab02c81e0c1a27db45ba7e8e608`。

### M06_b

- 曲名：Danse Morialta。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Danse Morialta](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1200026)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`8f49ab8553a58269332201269db43ee46c09a49dac348a72fa8cc7834b32424e`。

### M07_a

- 曲名：Americana。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Americana](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1200092)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`664880bb7368b8b85e362a5dae28338de4e4741205991a0817ceeaabe7366153`。

### M07_b

- 曲名：String Impromptu Number 1。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[String Impromptu Number 1](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1300004)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`ef3867bf115a62f54fff88bdcc59d22e44197e5acc505174b04e6087964dda9b`。

### M08_a

- 曲名：Lost Time。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Lost Time](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500032)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`c6c06198854392d729d965fc531cff8b3580c177944a1f7c8542b99edf3f7f65`。

### M08_b

- 曲名：Anguish。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Anguish](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400047)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`b1750903a90c2cfe88445196e78181a9093c0a3bc08f8bed39993d969fe0d268`。

### M09_a

- 曲名：Easy Lemon。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Easy Lemon](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1200076)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`2486b8ecfe4575f9ab31613a2c03c2ee45e6e5280301d05b4dd7237c9e1c2531`。

### M09_b

- 曲名：Happy Bee。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Happy Bee](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1300014)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`06f7dfd763a0bcc33fdf29ecf904c23753deaf392c8c7686902bfb943ba99576`。

### M10_a

- 曲名：Dream Culture。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Dream Culture](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1300046)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`f12cbb52bd4b92bd6cf8a343645567c119627e9cbf98108a3eb6ac2cc275ee46`。

### M10_b

- 曲名：Almost New。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Almost New](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1800008)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`3cb29102881aa9cb56292753dfa6c92004eddf4e0ad367e979c7292b0e1ac1a0`。

### M11_a

- 曲名：Colorless Aura。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Colorless Aura](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400008)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`c77e124a944f0974358d2676f0dab5c866fc64ec4e4f22f52d59fb91991b2711`。

### M11_b

- 曲名：Stages of Grief。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Stages of Grief](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100408)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`e0d15b852a9a6fc5c0bbd56f3f7c1363edcc1779bb54d1eed18f563b9941a82d`。

### M12_a

- 曲名：Pride。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Pride](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100106)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`2b8ddb507118c417a856d5a1d9b85f4e3773afe2724c2f4f8f5875bfc39508ae`。

### M12_b

- 曲名：Dreams Become Real。
- 作者：Kevin MacLeod。
- 演奏者／錄音製作：Kevin MacLeod（錄音原頁署名；未另列個別演奏者）。
- URL：[Dreams Become Real](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500027)。
- 頁面license：開放授權；錄音[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；作品CC BY 4.0。
- 核查日期：2026-11-06。
- 原錄音sha256：`a8ea5df5f969ed8d898af7fe07eb4712233f03e9d83f7ebcc88d1c851f3171b0`。

### 《羅馬之泉》另一版試聽（未採用）

- 曲名：Fontane di Roma／《羅馬之泉》。
- 作曲：Ottorino Respighi。
- 演奏：Czech Philharmonic Orchestra／Antonio Pedrotti；原廠記1961-02-19於Rudolfinum錄音完成、首發1961。IA所附1991是重發版年。
- URL：[IA具體錄音頁](https://archive.org/details/lesgeniesduclassique_vol4no19)。
- 頁面授權：上傳者標Public Domain Mark 1.0；[原廠逐曲頁](https://www.supraphonline.cz/album/233649-antonio-pedrotti-in-prague?trackId=2780351)另列(P) 1961 SUPRAPHON。保留作試聽比較，不宣稱已取得原廠影片許可，不混入配樂。原廠有[同步授權窗口](https://www.supraphon.com/licensing)，尚未詢價或寄信。
- 核查日期：2026-11-06。
- 下載FLAC sha256：`6d00e0f23ccb12519157c5909187a59b8a8cbfb80705b96f7a502daa8597fce6`。

原始FLAC保留於`cities/rome_music_trial_r2_all/build/audio/music/source/fountains_pedrotti.flac`，44.1 kHz雙聲道，887.467秒。前段25–85秒轉成48 kHz WAV，僅頭尾各0.3秒淡化，沒有降噪、EQ或改變中段動態；原生量測：silent 0%、gap 0.1秒、low 7%，無警告。這只證明該樣本通過這三項量測，沒有代替人聽底噪、音色及演奏。

另測735–795秒：silent 39%、gap 9.2秒、low 1%，不交作可用配樂樣本；不能據一段弱奏的門檻結果判整份錄音音質。數據與來源時間見`research/rome_fountains_pedrotti_samples.json`，尚未主觀聽審。原片、現有配樂與配音均不變。

其他新線索及未取得的來源見`research/rome_fountains_open_recordings.md`、`research/rome_fountains_official_recordings.md`。另查HALIDON Respighi逐曲授權目錄，17軌沒有《泉》；Classicals.de可讀目錄未找到Respighi。不能把通用影片授權頁當成已找到此曲。

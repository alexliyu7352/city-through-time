# Rome voice

英文旁白由使用者選擇的 Muse 助理線上生成。片尾及 CREDITS 署名固定為「Voice: Muse Assistant」及「配音：Muse 助理」，不加網址。

定版配音稿保存於 `assets/audio/voice/rome_voice_en.md`，共 27 段連續 takes。數字、年份與序號按稿中讀法念出；標點及分段表示停頓，不念出停頓指令。影片的 361 句英文、中文字幕及 line ID 保留原文。

使用 `audio/voicecut.py` 對已知文字做強制對齊，從每個連續 take 切出每句 FLAC，並產生 `takes.json`。原始 takes 與切句分別保存在 `assets/audio/voice/original/raw/`、`assets/audio/voice/original/en/`，不另裁切、去靜音或重錄。同 take 的相鄰行依 manifest 連續播放；跨站半句放在同一敘事站，不另外插入尾巴或間隔。

已切句的 Muse 合成接縫以原生 `audio/seams.py` 在24 kHz原採樣率修補：前後各10 ms平滑，不寫回原始來源。361句中242句改變，共487次原生接縫修補，`--check`剩0。所有句檔的sampleframes、聲道、採樣率及PCM16格式不變，`takes.json`、字幕與時軸不變。**定版361個FLAC與takes.json在`assets/audio/voice/en/`**，重建時連到`build/audio/voice/en/`；使用原生voice組軌與take-level音量規則產生48 kHz單聲道track，再依已選B方式混音。音樂、旁白文字和署名不變；原始檔與歷次記錄保留，不從舊候選讀取。往後由新版voicecut切take前也會自動修補接縫。

Muse 助理的服務條款網址尚未由使用者提供，目前也尚未查到可核對的條款。公開散布與商業用途的授權條件尚未核實，不據此推定授權；不填寫虛構條款或網址。

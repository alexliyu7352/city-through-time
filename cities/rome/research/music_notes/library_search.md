# 錄音篩選過程

核查日：2026-11-06。先讀每首自身頁面，再下載該頁連的原始錄音。Incompetech 原頁由頁內 JavaScript 依 ISRC 載入 `pieces.json`，在該曲作者與下載按鈕旁顯示 CC BY 4.0；保存逐曲頁、逐曲資料列，另以原生瀏覽器讀實際渲染的該曲文字。這裡採用的是逐曲明列的 CC BY，並非因網址含 royalty-free 即接受。

頁面存檔只整理行尾空白；音訊原檔逐byte保存並校驗，WAV轉檔另列sha256。

所有進候選的 Incompetech 原創作品，作曲／錄音製作均由原頁署名 Kevin MacLeod；原頁沒有逐一列出取樣或演奏樂手，因此不另捏造一份人員名單。候選表把製作者與未列個別演奏者的限制一起寫出。

已先排除：

| 曲／線索 | 原因 |
|---|---|
| Ancient Rite，USUAN1900048 | 原頁配器有 Choir；即使CC BY仍排除 |
| Angevin／Angevin B，USUAN1200110／111 | 原頁有 Choir |
| Deliberate Thought，USUAN1100261 | 原頁與作者文章明說有 choir |
| Arcadia，USUAN1100326 | 多組choirs |
| At Rest，USUAN1100748 | Voice、Choir |
| Intrepid，USUAN1500062 | 標準下載有人聲；另售no-vocals不能直接當本檔 |
| Lost Frontier，USUAN1300039 | Choir |
| Long Road Ahead，USUAN1100588 | Choir |
| Heart of Nowhere，USUAN1400045 | Choir |
| Ever Mindful，USUAN1700033 | Choir |
| Ascending the Vale，USUAN1600064 | Choir |
| Rites，USUAN1100722 | Voice；標題像儀式並不豁免 |
| Porch Swing Days - slower，USUAN1100715 | Voice，描述說有airy chorus |
| Respighi / US Marine Band《Il conte Orlando》 | 原頁為現場演出；且是1917現代改編，不能當1599原樣。未以PD跳過噪音與時代判斷 |
| Commons《Prose de la musique Pontus de Tyard》 | 說話朗讀，不是可用lute器樂 |
| Michael Levy／WHE影片中的lyre | 查到具名演奏，未找到逐曲明示可供本片使用的授權，不因訪談文章開放而使用音樂 |

首輪既有量測另淘汰四個take：M05_a Virtutes Instrumenti、M06_b／M12_a Enchanted Journey、M11_b Measured Paces；低於150Hz能量未達 `tools/music.py.said` 的2%門檻。這不等於原曲有錯，而是未通過本案沿用的候選量測條件；不加EQ或混入低音掩蓋。原檔留在source，原WAV移到cand/rejected，測值保留在 `rejected_candidates.json`。改找Teller of the Tales、Danse Morialta、Pride、Stages of Grief。

使用者最終採不盈利使用；頁面明列PD／CC／royalty-free等允影片即可，非開放曲另標例外。本名單仍全部使用開放授權，無商業歌、電影原聲或授權不明曲。

**試聽能力限制**：以 `functions.audio` 輸入 Volatile Reaction 原錄音的20秒，工具回覆 `audio content omitted because you do not support audio input`。本代理無音訊輸入能力，未能主觀實聽。配器清單只作先行淘汰；「沒有寫vocal」不能證明全曲無哼唱、場噪或嘶聲。`tools/music.py.measure` 也不判斷這些。依使用者最新裁定，完成頁面器樂篩選、量測與可播放檔即交候選，全部明標：**模型不能主觀試聽，雜音／人聲仍待使用者試聽確認**。

保留原檔不剪、不混；48kHz WAV 僅格式／取樣率轉換。任何裁切、loop、開始落拍與影片中動態，均待使用者選定後依新 timeline 處理，不在本候選階段假稱已混音驗收。

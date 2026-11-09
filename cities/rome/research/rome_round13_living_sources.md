# Rome round 13：三個 living 的來源與場景界線

交付整合者的研究片；只讀12c及既有模型，未改候選、旁白、正式場景卡或共享碼。三張均在整合者固定片中機位並提供最後 native ref後才生成。生成工具為 Codex 內建 `image_gen.imagegen`；先 `view_image` 看 ref，再 EDIT，不用 CLI／API。共用風格沿既有 Rome living：節制自然色、可讀自然光、寫實歷史重現與極輕筆觸；白／紫／金投影色不當真材色。

## 排片及原生位置

| ID／旁白 | 具體一刻與年代 | 可用模型／鏡位工作點 | 排片界線 |
|---|---|---|---|
| `rome_round13_republic_assembly`／`r02_004–006`，優先綁`r02_005` | 早共和公民集會中，官員在聽眾前發言，旁邊侍從將束棒放低；動作借李維2.7，任期規則借2.1，**不是捏造交接棒儀式或509當日現場** | 僅`republic_won_and_lost`早城。既有`rome02_early_whole_comitium_public`工作域內，target **[12.48349,41.89241]**。Hostilia鏡外；若ref看見未知立面，先換方向。 | 早城生長前沿最遲100.362；最終native圖on為103.072，圖出110.572前收完，不蓋前面城長。 |
| `rome_round13_emporium_arrivals`／`r02_011` | 約160 BCE，一名搬運者從河來方向扛沉重袋糧，另一人扶接，第三人整理既有裝卸空院的待運糧袋 | 已核loading reservation內活動點 **[12.4756,41.88085]**，原生1920 × 1080投影約x714、y727。背景**保原有closed-atrium宅列**，不要求工作廊入鏡，不開牆或增廊。朝東南陸地，河留鏡後。 | 整合者最終原生全中城134.944已起完、圖135.640入；不蓋中城生長。 |
| `rome_round13_holiday1953`／`r09_003–004` | 1953電影中的羅馬遊街想像：一男一女共騎小摩托，背向鏡頭；幾輛同期小轎車及少量路邊旁觀者，競技場是現存古蹟 | **Colosseum外道路**，已核真實Vespa取景地。只用1953當期現代城市／已存在地標，`today:keep`；由整合者選路面低近機位，不把完好AD 80競技場倒用。 | 最終native圖on為1499.342；跟r09_003–004，圖出1507.342，返回段至1508.842；原2021階梯panel由整合者移除。 |

座標為已存原生模型工作位置，**不是考古測量或原片攝影機點**。早Comitium domain原始幾何見`rome02_early_whole_source_geography.geojson`，範圍12.4829908–12.4841080／41.8920608–41.8927345；港區見`rome02_mid_whole_source_geography.geojson`之`open_emporium_loading`。真正畫面以最後ref為準。

## 共和集會：已核來源

- 既有`FACTS S03/S28`、`rome02_early_whole_plan.md`、`rome02_early_whole_review.md`及`rome02_republic_sources.md R08/R17`：早城保較早Tuscan Capitol、晚六世紀Regia及早期公共用途；早Hostilia完整立面缺資料，不能畫Curia Julia、帝國basilica、497 Saturn或484 Castor。今DEM、地坪鋪材和公共場外廓皆有估值。
- [Livy 2.1、2.7–8，拉丁原文](https://www.thelatinlibrary.com/livy/liv.2.shtml)，本次讀第1及7–8節。2.1以一年任期的官員描述新政體；2.7記Valerius召集人民、將fasces放低後發言；2.8另記補選同僚。這些是幾百年後的文學追述，不是事件照片或現存交權禮儀。畫面只借**公開集會＋放低權力標誌**，旁白保原文，不能新增「每年都在此做同一動作」的說法。
- [Margarita Gleba，*Textiles and Dress*，2017，作者稿印488–490](https://www.research.unipd.it/bitstream/11577/3454499/2/gleba2017.pdf)，本次讀PDF 3–6頁。六世紀中義大利衣著有長短tunics、矩形／半圓披衣的圖像與織物比較；不是Rome 509服裝普查。採素色短衣、簡單披衣和普通鞋，不複製早得多的Verucchio墓服尺寸，也不把一世紀Aulus Metellus的長大toga、clavi或帝國禮服前置。
- [Met，*The Roman Republic*](https://www.metmuseum.org/essays/the-roman-republic)，本次讀正文：早共和權力有階級限制。畫中為少量成年男性公民聽眾；不畫男女老少人人投票或現代議會席、選票箱、口號牌。匿名人數及站位屬想像。

**四周應有什麼：** 古公共開地、通Forum的既有通路、附近已模低矮屋頂、坡地及遠處古山丘；不是露天石造圓劇場、帝國紀念廣場或農田。既有裸地只續作此公共用地；不可因ref缺Hostilia就自由補一座大殿。地面不畫看似考古實測的規整花紋、座席或柱廊。

## 糧貨入城：已核來源

- 既有`rome02_mid_whole_plan.md`、`rome02_mid_whole_review.md`及`rome02_mid_whole_spec.yaml`：160港區只有早期裝卸場／工作廊的有界代理；**不是現存487 × 60 m、50橫拱大倉**。三條的數量、位置、外廓及3.5 m高是工作估配，不升格為193原廊實測。
- [Livy 41.27.8，拉丁原文](https://www.thelatinlibrary.com/livy/liv.41.shtml)，本次讀27節：174 BCE在Porta Trigemina外鋪Emporium石地、圍以木樁，修Aemilia廊並設通台伯河的階。這支持公共裝卸用途和通河關係，沒有給完整碼頭形狀、階高或本鏡周邊房戶。
- [Digital Augustan Rome，Porticus Aemilia (Emporium)](https://www.digitalaugustanrome.org/records/porticus-aemilia-emporium/)，本次全文重讀：早二世紀廊可能用較不耐久材料；現存大倉的名稱、年代有爭論，部分研究將其定至Sulla期。採現有160代理，不能把後世混凝土拱倉外觀補進空地。
- [Livy 33.42](https://www.thelatinlibrary.com/livy/liv.33.shtml)及[37.2](https://www.thelatinlibrary.com/livy/liv.37.shtml)，本次讀相應節：196有Sicilians把小麥送到Rome；190有向Sicily／Sardinia徵雙份糧什一稅、Sardinia其中一部分送Rome。只支持二世紀遠方糧與徵收糧入城；**不稱畫中匿名袋糧就是這兩次任一船貨，不添加160某日貨單、來源國旗或精確數量**。
- [Ostia考古園，Grain and Bread](https://ostiaantica.cultura.gov.it/en/trails/grain-and-bread/)，本次讀原正文（首次open逾時，後搜尋工具已取得全文）：糧主要用植物纖維袋、扛卸，並有河運轉運。所舉扛夫俑、船壁畫、馬賽克多是後世證據，因此只借保守功能和普通袋／短衣，不複製後世職業制服、帝國Annona官員、船型、倉儲及Ostia後半二世紀公共區。

**四周應有什麼：** 已模工作廊／服務院、裝卸通路與靠Aventine的低層住居；空地是工作場，不是空曠沙漠、草原或新造碼頭。此鏡朝陸，河在鏡後，圖不加水；穀物搬運就能具體表現該句，不必用一張圖虛構同船同日兼具糧稅與掠奪品。可有幾個無字小包和普通陶容器，不能將它們指認為戰利品。

最後ref選既有宅列前的空服務院；原生point-in-reservation已由整合者核對活動中心，**不用三條早期廊入鏡，也不因名為港區就把宅牆改成開廊**。真loading場的依據是已存原生reservation，不由生成後畫面反推考古用途。

**凱旋備選未採：** [Plutarch *Aemilius* 32–34](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Aemilius*.html)本次讀相關三節，記167 BCE凱旋的沿街觀眾及分日的雕像、武器、金銀等；具體物品分日，不能一股混成一張。同日景若採用須重新對167建築版本、路線及當期ref；現中城是160觀察態，不能直接聲稱完全相同。本輪採匿名糧運，無需再造凱旋隊伍、俘虜或軍服。

## 《羅馬假日》：取景、物件與權利

- 沿`FACTS S50/S194`及`rome_holiday_picture_sources_20261104.md`的電影年份、取景與授權分開原則；**原2021階梯照片不再代替騎車場面**。
- [VisitLazio官方Cinema：Roman Holiday](https://www.visitlazio.com/en/roman-holiday/)，本次讀正文：明列Corso Vittorio Emanuele、Colosseum、Piazza Venezia為二人騎Vespa場景。可選競技場旁道路，不能搬到無取景證據的任意古蹟。此來源沒有給原片精確路線／每一轉角。
- [BFI取景比對](https://www.bfi.org.uk/features/roman-holiday-rome-locations-audrey-hepburn-gregory-peck)，本次讀Piazza della Trinità dei Monti段：騎行起於台階上方、繞Sallustiano方尖碑，附近有Hotel Hassler。它是另一個有據取景選項，**不能用下方西班牙台階吃冰淇淋的空間拼成摩托車穿越台階**。本輪不取其電影畫面或當代攝影入片。
- [Piaggio官方WIDE，2023-08](https://wide.piaggiogroup.com/en/articles/events/happy-70th-birthday-roman-holiday/index.html)，本次讀正文與原圖說：本片車為1951 Vespa 125 *faro basso* mod. 51。生成只需小車圓潤早期外形、低位頭燈、簡單單色鈑身；不畫現代踏板車、大擋風玻璃或塑膠車殼。文章內檔案照片只研究，不入片。

**人物與1953環境：** 二人小而可讀，從背面或遠側背面離去；女子淺襯衫、過膝／小腿裙，男子襯衫長褲，都是匿名戲劇人物，**不要赫本／派克臉或肖像相似度**。路邊少量普通行人看車經過，幾輛1950年代以前的圓弧小轎車；不增加電影沒有研究過的撞車或追警事件。普通配角服裝、車數及位置為有界時代想像，無特定車款主張。

**四周應有什麼：** 1953已建羅馬街地、當時存續的道路與房屋，競技場是有缺損的古蹟；不是完整古競技場，也不是今日觀光專用步道與人潮。以候選現代城市作同址量體約束，僅保來源能支持到1953的可見物；若ref有明顯1953後建物或今日設施，交整合者先調機位，不能在生成時任意搬樓。無新湖、河、空曠鄉野、當代公交車、SUV、手機、護欄、路面字或電動滑板車。

最後Colosseum ref的前低金色兩層券廊與後高白色廊，依`rome08_capital_whole_basis.md C17–19`及`rome08_formal_templates.yaml`是**同座古蹟的19世紀低內圈supports（26 m估值）與北半殘殼（48 m同址尺度比較）**，不當成兩座競技場，也不因此補完整南高殼。整合者原生核camera eye在189 × 156 m外橢圓之外，外道路活動工作點[12.4912,41.8892]亦在外輪廓外；畫中摩托與車人僅在前方街面。此為示意殘壁形制，無逐塊殘邊或1953逐戶精測聲稱。

**1953預告輕量備案：** [Commons：ROMAN HOLIDAY – Trailer 1953.webm](https://commons.wikimedia.org/wiki/File:ROMAN_HOLIDAY_%E2%80%93_Trailer_1953.webm)，本次核檔案頁、Summary、Licensing、history。頁稱美國1931–1977間無copyright notice發布，標PD-US-no-notice；原檔960×720、2 m 6 s、27.4 MB，來源為2016 Vimeo、2018上傳Commons。這個授權聲稱**僅及該預告檔案，不及整部電影、其他劇照或修復版**；頁另提示其他司法區未必公版。未下載或抽格，未另核原預告首尾notice，因此它目前只是備案入口，不能把本研究稱為已獨立證明全球PD或已選好可用鏡頭。若living成功，完全不需用預告。

## 交付檔

- `rome_round13_living_republic_assembly.yaml`
- `rome_round13_living_emporium_arrivals.yaml`
- `rome_round13_living_holiday1953.yaml`

三張最終native ref已先由整合者固定，再逐張`view_image`核讀，使用內建`image_gen.imagegen`之EDIT。新PNG僅存`research/rome_round13_assets/<ID>.png`，沒有寫正式assets。原生ref、原生prompt、實際`_imagegen_prompt.txt`、後續縮尺EDIT prompts、未採v1/v2及`_generation.json`均保留同目錄。共和修人物尺度一次；港區修尺度／黑星空，再縮尺一次；Holiday修全部人車尺度／無據樹葉，再縮尺一次。原模型的自然材色與主要輪廓逐張目視對照；未做自訂幾何或重畫模型。

三張是可交整合者的PNG，自審不等於native adopt／sheet／check通過。整合者承接候選資產、來源卡同步與原生投影檢查。人物像素尺寸為目視檢查，不冒稱逐人的3D測高；若主觀畫面仍需更近，須改原生機位再重生，不能把人放大遮掩。

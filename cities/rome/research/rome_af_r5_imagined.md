# A–F候選的新增想像圖片

工具為內建imagegen，未回傳可核的底層型號。以下是作者提示詞與事實界線，不是原件文獻。疫情living另有原生機位與來源卡 `living/rome_af_prayer2020.yaml`，成圖必須經ref/adopt/check。

## 返家背影

成圖 `assets/round_af_pictures/cesare_homecoming_imagined_v2.png`。輸入是本片既有AI空房 `assets/imagined/restart_ip05_empty_room.png`；房間、機位與材料保留，只新增一位背向鏡頭、沒有可辨臉孔的男人。據CDEC1955證詞（FACTS S160），不作Cesare本人肖像，不造地址與家人物件。全圖以panel上屏並標史料想像。

實送提示詞：

Use case: historical-scene. Asset type: documentary imagined panel for A City Through Time, Rome. Edit the attached empty-room image into a restrained imagined homecoming in Rome after World War II, 1945. Preserve exactly the room, walls, floor, windows, plain sky beyond the windows, doorway, camera, framing, natural warm light and realistic film-still style. Add one small adult male figure standing at the threshold at the far left edge, seen only from behind in a plain worn 1940s civilian jacket and trousers, looking silently into the empty room. Keep the room the main subject and show no face. This is a symbolic illustration based on Cesare Di Segni's 1955 testimony that he returned to the rooms once shared with his children and found them empty; do not create a purported portrait, identifiable address, exact likeness, archival photograph, invented family belongings or emaciated spectacle. Keep hands unobtrusive; no luggage required. No other people, no uniforms, no badges, no writing, no labels, no text, no logos, no border. The image must remain a full 16:9 composition.

## 1943停戰廣播

成圖 `assets/round_af_pictures/armistice_radio_imagined.png`。依9月8日Badoglio廣播宣告（FACTS S198），人物與房間是未具名想像；無授權來源不明的原照片、原聲、臉孔或報紙字樣。

實送提示詞：

Use case: historical-scene. Asset type: imagined documentary panel for A City Through Time, Rome. Primary request: a restrained visual evocation of Italy's September 1943 armistice announcement, clearly an illustration imagined from historical accounts. Scene: a modest Italian civilian room in 1943, three adults viewed from behind or in distant side profile, seated quietly listening to a single small wooden valve radio on a plain wooden table. The radio has no readable writing. Plain plaster walls, one shuttered window with fading daylight, worn modest civilian clothes typical of wartime Italy, simple chair silhouettes. Faces are not identifiable and are not portraits of named historical people. No celebratory gestures, no soldiers, no violence, no flags, no newspaper text, no identifiable address or famous monument. Style: natural materials, muted warm earth colours, restrained documentary film-still realism, like the project's empty-room imagined panel; wide 16:9 composition, human figures small, enough light to see the room. No words, captions, logos, border or watermarks.

祈禱living已用內建imagegen從原生白模ref生成並adopt；初稿雨夜、空廣場、亮燈棚子與遠處小白衣人影已實看，但B4梵蒂岡牆線查核後須以新模型ref再次check並視需要更新。初稿原生adopt相機與ref保存在 `research/living/rome_af_prayer2020_pre_b4.json`／`_ref.jpg`；最終圖以候選的 `build/review/living/rome_af_prayer2020_*` 為準。初稿使用原生prompt全文如下：

Use your built-in image generation in EDIT mode on the attached image, and save the result as rome_af_prayer2020.png in the current directory (16:9, the same framing). Do not write code.

This is an edit, not a new picture. Keep exactly as they are in the attached image: the camera position, the lens and the framing (nothing moves, nothing is cropped or zoomed); the horizon line at the same height in the frame; every building, wall, gate, tower and street at the same place, the same size and the same outline in the frame.

The attached image is a plain white 3D model of St Peter's Square, Rome, looking west towards the basilica from the empty square, the rainy evening of 27 March 2020. Some of it only helps the model stand and is not a building: square slabs under monuments are the ground they stand on, dark bands at the foot of walls are shadow, flat grey strips are streets. The empty dark ground and the black sky are to be filled.

Change only the surfaces and fill the empty ground and the sky with the real place at that moment, as the sources describe it:
Preserve the reference model's exact view, perspective, horizon, basilica silhouette,
colonnades, the obelisk and all paving and street geometry. Turn the white-model
surfaces into the actual warm travertine and wet stone of St Peter's Square.
Rain at dusk, dark blue-grey sky, the broad square empty of crowds, wet paving
reflecting restrained warm lights. At the distant basilica entrance put a small
lit temporary canopy and one very small white-robed figure at prayer beneath it.
The figure is seen at a distance without a face or identifiable portrait detail.
A restrained documentary film still with natural materials, no theatrical spectacle.

Do not show: crowds, a packed audience, close-up faces, invented medieval structures,
modern vehicles, news logos, lettering, captions, watermarks, changed architecture,
a different camera, cropped or zoomed framing, a bright sunny sky.
Look: natural colours, documentary realism, like a well-lit film still; people small in the frame, nobody posing, no close-up faces; nothing modern unless the sources name it; no text, no watermark, no border.


返家圖為原生panel的中央裁取再做一次位置修正；只移動想像人物，不改房間。最終背影在中間一半，避免被panel左側漸隱／裁切吞掉。實送修正詞：

Use case: precise-object-edit. This documentary imagined panel is displayed with its middle portion visible. Change only the placement and scale of the one man. Remove him from the far left edge and place him as a smaller full-body back-view figure in the middle of the room, near the centre of the image (about 52 percent across its width), standing on the floor and looking towards the empty doorway on the right. His full silhouette must be entirely inside the middle half of the composition, with space around him. His height should be around 45 percent of the image height. Keep the same plain worn 1940s civilian jacket and trousers and no identifiable face. Keep the room, walls, floor, windows, doors, sky, framing, camera, light, materials, style and overall aspect ratio exactly unchanged. One person only. No invented belongings, no text, no symbols, no logo, no watermark. This is an imagined survivor homecoming based on testimony, not a portrait or known address.


## 收尾定稿

祈禱圖在B4牆線修正後更新一次定稿。使用新白模為唯一幾何基準，初稿只作雨夜材質／光線參考；外牆依新ref現存周界，棚下白衣人影縮小，不畫臉。原生成檔exec-0dfb33c3-b49e-48ab-87bf-282544940147.png。

原生check另報船磨／1300禧年兩張舊圖分別10.6／12.4每像素偏差。兩個新版本使用各自新原生ref與既有來源卡生成，ID為rome_af_boatmill537／rome_af_jubilee1300，舊已批資產不覆寫。船磨保留兩個敞口船身、一輪、磨石與軸，僅添普通小工人；不造棚屋與額外機械。禧年保留橋三拱、城堡圓筒與城屋輪廓，只添來源支持的兩向小朝聖者，不造分隔欄或貝尼尼雕像。各新原生prompt及ref保存在候選build/review/living，場景卡在research/living。

# 模型研究參考檔

Subura住宅重做：`lanciani_subura_rework`（66瓦片、2816×1536）及`lanciani_subura_east`（48瓦片、2048×1536）沿用館藏KML配準，逐瓦片URL／bounds／SHA見各自`*_sources.json`；兩張`*_detail.png`只是檢視裁圖，不能當獨立配準影像。`caen_insulae_street_1/2.jpg`供學術復原比較，原網址為Caen「Rue bordée d’insulae」頁中的2026/04圖片，未放入assets。FUR10g照片只在記憶體中作研究瀏覽，未落地保存或加入影片；`forma_10g_text.html`是214-byte動態網址403錯誤回應，不能當內容來源，採用的是可讀的`https://formaurbis.stanford.edu/fragment_10g.html`靜態研究正文。住宅來源、年代、放置與比例限制見[住宅依據](../subura_housing_basis.md)。

本資料夾供研究與建模核對，不是電影assets，不代表已取得公開上映／商用圖片授權。主要結論及年代界線見[model_sources.md](../model_sources.md)。

2026-10-28小樣補充：`lanciani_core.tif`使用Rumsey／Stanford原有KML的EPSG:4326配準，20張局部瓦片，未另擬控制點；每張來源與雜湊見`lanciani_core_sources.json`，用`fetch_lanciani_core.py`重取。`dar_forum_palatine_z17.tif`為9張既有XYZ瓦片，EPSG:3857；原網址、XYZ編號、仿射轉換及雜湊見`dar_forum_palatine_z17_sources.json`。這些是可用的局部配準研究圖，不改下列735-byte入口KMZ本身仍只有NetworkLink的說明。現在OSM城市快取也已含古街短段；下文「局部查詢未取得」只記錄當時那次失敗的查詢。

- Lanciani圖：Rodolfo Lanciani，1893–1901，University of Virginia Aquae Urbis Romae提供掃描；各種古代年代混列，非113年快照。只供地理對位與形制研究。
- Lanciani配準KMZ：David Rumsey Historical Map Collection / Stanford；館藏記錄載1901原圖、1990 Quasar縮印版。此檔只有KML NetworkLink，不包含整幅離線影像。掃描的使用條件與古圖原作分開，沒有預設可入片。
- Digital Augustan Rome：約AD14；University of Arizona Archaeological Mapping Lab，David Gilman Romano主持，Mark Davison作圖；地圖署名Parrhasian Heritage Foundation。API／網頁／程式bundle保留作來源與座標系核對；未見CC／PD上屏許可。bundle只是研究時定位其公開tiles／API，未複用或修改其程式。
- Trajan Forum重建圖：Mercati di Traiano Museo dei Fori Imperiali官方頁；圖片未見獨立作者及開放授權，僅研究參考。
- San Paolo alla Regola PDF：Sovrintendenza Capitolina官方說明；考古分期、剖面和平面研究參考，未視為開放入片圖。
- augustan_location_candidates.geojson：從官方463筆公開記錄選出有經緯度的住宅、商倉及少數定位錨點。座標只代表原圖標籤點，不是足跡、量測中心或113年實貌。用同資料夾的make_location_candidates.py重建；保留原來源分類與逐筆網址。

重建衍生候選點：

```sh
uv run --no-sync --offline python -I cities/rome/research/model_reference/make_location_candidates.py
```

下載成功檔如下；沒有保存Stanford Forma Urbis碎片照片／模型，公園2020三張圖因本機TLS連線失敗未存，局部OSM路線查詢亦未取得。

| 檔名 | 來源 | Bytes | SHA-256 |
|---|---|---:|---|
| augustan_location_candidates.geojson | 本資料夾衍生／重現程式 | 33575 | `d489302f033858d1e744a19626980ec9be0be3b14185f2bbf5e82d286f7c3306` |
| dar_z13_4379_3043.png | [原始網址](https://phf-cms-prod.s3.us-west-2.amazonaws.com/maps/digital-augustan-rome/13/4379/3043.png) | 9392 | `1d46462edd1dc942979f3d2f3f27f12cd132bb4b026cf97a2f586d2eb3f359c1` |
| dar_z13_4379_3044.png | [原始網址](https://phf-cms-prod.s3.us-west-2.amazonaws.com/maps/digital-augustan-rome/13/4379/3044.png) | 23158 | `85efae697b58b8ece9ee1eba7a73bd1af0127bb1a2281bca967f2862d30d82a9` |
| dar_z13_4380_3043.png | [原始網址](https://phf-cms-prod.s3.us-west-2.amazonaws.com/maps/digital-augustan-rome/13/4380/3043.png) | 18737 | `8f1c6f199a3145f7ea393e68940fceafd4fbbf965ea60acecb963c9e6278f2b4` |
| dar_z13_4380_3044.png | [原始網址](https://phf-cms-prod.s3.us-west-2.amazonaws.com/maps/digital-augustan-rome/13/4380/3044.png) | 41266 | `6549642604fe26012c35ecc71ccafe0d05b04a3c88d532e5af6626c163a27c69` |
| digital_augustan_rome_app.js | [原始網址](https://www.digitalaugustanrome.org/static/dag/app/js/app.3737041b.js) | 407850 | `69496cb598c3ae16ab9f2c39508d41c6a745c9daaf5e66a696797331d5482186` |
| digital_augustan_rome_credits.json | [原始網址](https://www.digitalaugustanrome.org/api/pages/?slug=credits&type=generic.TextPage&fields=body) | 1574 | `3a5710cfc95f72e434e5ff8a6bc32ce2ebb33c9c8b94c2b8f9f9d433201a82e1` |
| digital_augustan_rome_features.json | [原始網址](https://www.digitalaugustanrome.org/api/dag/features/) | 878 | `fe04a9a6a4d68f8bf45f1ec723aa88f0245e2d188d2240aae34e87921d4ef7ec` |
| digital_augustan_rome_index.html | [原始網址](https://www.digitalaugustanrome.org/) | 2675 | `cea14b48872ad79f93abeb7428af8ef6d164d75da617d68a37e8ee1968406579` |
| digital_augustan_rome_intro.json | [原始網址](https://www.digitalaugustanrome.org/api/pages/?slug=introduction&type=generic.TextPage&fields=body,authors(*)) | 2112 | `085c0fae4735e9408eac0dc1f14d1d4ab207f3b079bca44081d8a934a6a206c5` |
| digital_augustan_rome_records.json | [原始網址](https://www.digitalaugustanrome.org/api/dag/records/) | 156592 | `07121f59802322321b1ed6685ab55bb6da05e8487322548e0b388ea3f7171b16` |
| digital_augustan_rome_subura.json | [原始網址](https://www.digitalaugustanrome.org/api/dag/records/subura/) | 5987 | `67a692ac44cfa95b4ffd0c05533219a8fa1e0b34865dd2830ee4c50047f39d48` |
| lanciani_22_forums.jpg | [原始網址](https://waters.iath.virginia.edu/forma/forma22.jpg) | 325389 | `58639e616f8da72b2a8555c710a65ff47227d2a8697964b74e9d94418f83fc16` |
| lanciani_29_forum_palatine.jpg | [原始網址](https://waters.iath.virginia.edu/forma/forma29.jpg) | 331768 | `c8abf517c4c5759d471d4d31e6a403a04ad30b29b6840c56497142e8edc54954` |
| lanciani_30_oppian_colosseum.jpg | [原始網址](https://waters.iath.virginia.edu/forma/forma30.jpg) | 251119 | `cadaf82bad9da7b582b658df882d6f01e9d22d4182217ec7514e0e6fa6d67b54` |
| lanciani_35_circus_palatine.jpg | [原始網址](https://waters.iath.virginia.edu/forma/forma35.jpg) | 273937 | `01d47ce940ad39cd0099d70a95c02c291191b549ca36e25c5c56a9f63773b4fc` |
| lanciani_georeference.kmz | [原始網址](https://rumsey3.s3.amazonaws.com/Rome%20Historical%20Lanciani.kmz) | 735 | `ac6cc60dcabdcd988df133bf462813378782173ca673288f2a3d5fce986bdd49` |
| make_location_candidates.py | 本資料夾衍生／重現程式 | 1704 | `9eeab2344123f50ca6cc3a921c2a052f2ceca7bb51a4c646b6f8c92eacb33b17` |
| san_paolo_alla_regola.pdf | [原始網址](https://sovraintendenzaroma.it/sites/default/files/storage/original/application/a9988a934e4e3ce05849c97fb8c5cce7.pdf) | 831847 | `486c057e539c61a19e975fcf73d8b59da38adfaa8f653649eeee2e6a5104dfb8` |
| trajan_forum_reconstruction.jpg | [原始網址](https://mercatiditraiano.it/sites/default/files/f_infopage/foro%20di%20traiano.jpg) | 178205 | `af8202376fe99ac86a0e426fbac2d25861b262eecfa5ef0559434908aff7595d` |

整城擴展：`lanciani_imperial_113.tif/png`為館藏level4既有配準47瓦片、2048×1536；`lanciani_imperial_fora.tif/png`為level6詳圖40瓦片、2048×1280。各自`*_sources.json`逐張列URL／bounds／SHA-256。`imperial_osm_anchors.geojson`為已核古址的原快取衍生；不等於113年上構。

整城定位詳圖另有`lanciani_campus_core`（16張、1024×1024）及`lanciani_praetoria`（81張、2304×2304），同樣沿館藏KML既有配準，各自manifest記錄逐張來源與雜湊。`marcellus_anchor_measurement.json`只量圖上圓線，不重配準；1.1m圈線殘差不等於古址定位精度。

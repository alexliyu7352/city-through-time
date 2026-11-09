# 12與必要尾段場域：正式接入索引

本件交原生配置提案，正式`city.yaml`／`script.yaml`全程只讀；191條已核雙語旁白不改。正式07仍有唯一寫鎖。來源、檢查與圖見`rome12_modern_review.md`，最短合併路徑如下。

| 接入位置 | 可重用原生輸入 | 精確接口／條件 |
|---|---|---|
| `modern_growth` | `rome12_modern_native_fragment.yaml`；獨立全城示例`rome12_modern_input/city.yaml` | `reset.year:1975`、`grow.mono:true`／warm4／6bands；維持歷史年線1975–2020。不開taller，不把未定年0改成1975。示例camera是研究鏡頭；正式由主線排 |
| 同一12站的1990一句 | `rome12_modern_worldcup1990_site.geojson`；全城study pins配置 | 球場中心`[12.4547821634,41.9339461952]`，pin `with:r12_05`／`until:r12_06`。不另設tour，不飛球場；研究19.8s≈1990，標籤19.8–26.05s是native讀時自動延長，正式需同時看yearline，不誤稱整段計數均停在1990 |
| 12連續近區的資料樣張 | `rome12_modern_input/window.yaml`、`rome12_modern_window_selection.json` | 原生follow_change windows1／900m格挑出`[12.455834494,41.819858271]`後固定az305/el35/d.16/fov42。已用9771d57新正式prepared重編；38.8／39.8／40.3／41.3s同cam四圖分次起升，d6cc2b2僅在資料差異核對無影響後沿用。明標5-year epoch estimates；中間高度只是動畫起升過程 |
| 2024步行化／14開場 | `rome12_modern_pia_spec.yaml`、`rome12_modern_pia_templates.yaml`、`rome12_modern_pia_trace.yaml`／`.geojson`、`rome12_modern_tail_basis.md` | 接在`world_returns`的獨立小場域city或已有當代場域城中。兩圓槽緣可改成top-level模板＋同ID實例；ground及trees直接用spec。平面是設計圖估讀；2020不得已有此新鋪地，不表示全城重建 |
| 2025聚集／2026閉幕 | 既有`rome13_silent_changes_proposed.yaml`、`rome14_return_changes_proposed.yaml`及source receipts | 同一大殿、柱廊、方尖碑、廣場保持站立；活動層由主線step5綁r13/r14。青年禧年與五月當選不是同日同場，閉門不使建築沉下。07/10的現代實址版本按native until/avoid_eras保留，不能把1667 Borgo街廓搬到2025 |
| 尾段河流規劃 | 既有`rome14_return_native_fragment.yaml`及`rome14_return_tevere_reference.geojson` | 只取框內既有Tevere河線作位置參考，明標`Planned / 规划`與全計畫75km、僅顯示局部。沒有重建整條工程界、假步道或新河道 |

**正式prepared與推估期語義**：本輪依9771d57及d6cc2b2明確授權重跑正式native prep，沒有改正式city/script或共享。最新正式model SHA256 `93800ea1ad15336255282dcc1172e540648d4494de96ed143ab03ba4692b5677`，核對UTC2026-10-30 16:28:14；僅3筆原2030顯示年變動，其餘records、幾何、高度與stats不變，見`rome12_modern_observed_validation.json`。窗口副本仍7abab0，依2005實際不變的逐件核對與主線授權沿用四圖，不以舊copy冒稱新prepared全片。GHSL2025／2030均為推估；依最新DATA第5點，這些現況輪廓的顯示年統一分散在2020–2025，原epoch分類／stats保留。2020.29本身符合2020後估算，不稱實測新建年。保留5-year epoch estimates／現況足跡／未定年背景註記。shader提前半年的起升行為未自行修改；正式年線與估算語義由主線一致處理。全城舊baseline本輪未重編，不能當新prepared全城驗收。

**11版本接口**：1990僅同構圖定位，本件不改1953／1960Olimpico露天量體，不需lose11部件。若日後做1990屋頂近景，先與11 owner按`rome11_olympic_integration.md`定出原11自身loss的部件ID；後城不能帶走前城。保留10電影城／11施設背景時，各城用自己的node planner及native直到／避讓，正式編譯核同時站立／輪廓≤8、每城lose≤16；本件Pia小城本身只需一個channel，不為限總數併歷史。

**Pia尺度取捨（已定案）**：原圖／完成照片有水；1:10000僅畫兩個源位置、直徑8.37m的revolve槽緣，不畫水。兩個kind:pool已移除，無專有stage選取；鋪地、6條pts／33樹及兩槽緣均保留，沒有新水表示／放大／移位。原round接口與162015取樣案不再待主線修，已依導演尺度決策結案，不阻塞接入。部分角度槽緣受DEM遮少許仍列限制，不抬高或造平台；最新版同機位近圖見一頁交件。

正式合併後只驗受影響的11–14相鄰範圍；本件獨立study的讀時／近遠圖不是正式全片鏡頭驗收，不為硬15分動旁白、燈光或加速。

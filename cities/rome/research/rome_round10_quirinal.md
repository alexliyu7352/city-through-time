# Round 10：1871奎里納萊長翼

獨立交件，不改1671庫、正式城市、candidate、旁白或共享碼。原主院9個parts逐值保留；只追加351.303m長、14m寬的兩主層長翼、與原主院共邊的短銜接、Fuga端部，共3件。原主院及新翼分開建的native study跨landmark交疊為0，沒有雙蓋主院，也不讓它在1871下沉重升。

## 來源及估值

- [總統府宮史](https://palazzo.quirinale.it/storia/storia.html)，「Il Seicento」「Il Settecento」：舊瑞士衛隊住區是長翼早期核心；Fuga完成長翼及端部的Segretario delle Cifre小宮。
- [總統府：La Manica Lunga e gli Appartamenti Imperiali，PDF1](https://palazzo.quirinale.it/luoghi/pdf/it/imperiali.pdf)：長翼是宮殿南側，Sixtus V時期開建；Bernini於1656–1659延長，Specchi續建，Clement XII（1730–1740）時由Fuga完成。王室時期其後加高與封閉部分花園側loggia，原文未給這些改造確年；1871不倒填今日整段加層。
- [憲法法院官方宮史冊，Appendici / Breve storia del Palazzo](https://www.cortecostituzionale.it/documenti/download/pdf/Cc_Checosa_2016.pdf)：長翼約360m。
- 平面用既有C02，[1866 Direzione Generale del Censo原圖的數位轉載](https://www.info.roma.it/pianta_di_roma_1866_direzione_generale_censo.asp)，本地 `model_reference/rome08_capital/censo1866_overview.jpg`；原生 `register.source` 沿用 `rome08_capital_whole_source.yaml` 的6點affine，2.7327m/px，最大控制殘差11.84m、留一20.99m。長翼軸線像素[1346,608]→[1441,523]，端部四角及轉換存 `rome_round10_quirinal_source.yaml`。這是粗圖源化示意，不是逐米地籍。

18m翼身、21m端部、兩主層、18°低hip屋頂與14m寬是圖像／保留23m主院約束的量體估值；4.38m窗跨沿原主院的具名Farnese比較，不稱本棟實際窗數。主院仍保原Falda不規則院洞。細分房間、內部瑞士人窄院、後來王室加層及精細窗飾不作完整復原。Censo僅研究比對，不把未核權的轉載圖放入成片。

## 直接交整合者

- `rome_round10_quirinal_templates.yaml`：首選純翼template `rome_round10_quirinal_manica`；另有保9件主院再加3件的完整比較snapshot `rome_round10_quirinal_1871`。後者不能替換1671庫，也不能與原主院同時加進城市；共享整體site會重算地坪，正式整合以分離翼部為準。
- `rome_round10_quirinal_patch.yaml`：`landmarks_append`和`new_parts_only`兩種入口；原主院不動。純翼全局錨點 `[12.486696,41.900361]`、θ−51.031°。追加ID `rome_round10_quirinal_manica_lunga`。標籤用「長翼 · 16–18世紀建成 · 1871年前既有」，不是1871新建。確切node/stage由整合者按既有stock時序放置。
- `rome_round10_quirinal_site.geojson`是原生6m apron的大bbox，**不是清屋範圍**。實際留地與trace整合改讀 `rome_round10_quirinal_reserve_patch.yaml` 及 `rome_round10_quirinal_reserve.md`：物理翼身＋Censo宮園，街外近鄰保留。

## 原生結果與實看

`本機候選/rome_round10_quirinal`（project同名modelview連結），nice／OMP2／原生2slot；990 primitives。`geocheck: every face points out of its piece`；clip的landmarks_overlap、walls_through、floating、terrain_cut等均0，**tall_foundation為8**。這8件已依checker的ground BOX／group top定位，全部是保留主院的8個舊薄立面承體，新翼不觸發；沒有tall_platform。不為壓數字改舊主院。無旁白單體study末段另有5.2s dead air，不是正式影片排片結果。

`rome_round10_quirinal_comparison_sheet.jpg`／`rome_round10_quirinal_views_sheet.jpg`已實看；前者含Censo綠色原院、藍色長翼軸線、黃色端部。兩方向220°／45°與130°／40°／d=.055，另有d=.035局部近圖。220°橫看可同時讀長翼與院洞；130°沿翼看有明顯縮短，不宜作長翼全貌唯一機位。各根據自己的DEM切填，接頭無空隙；這不是古地坪測繪。原生study已退出，沒有長工具／browser留跑。

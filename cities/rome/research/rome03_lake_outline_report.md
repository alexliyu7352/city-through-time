# Nero 湖：來源輪廓有限複核

**四邊形本身有來源；現有 140×120m 的四個角點沒有照來源描出。** [Ball 2003，印刷5頁圖1](https://assets.cambridge.org/97805218/22510/sample/9780521822510ws.pdf)的 `Lake` 確實以四段近正交直線圍起，並非自然曲岸。其圖說明標為 schematic map，四條實線不能當成出土岸石。舊提案則由周邊建築留距及對向對稱補成，應稱「有來源形式約束的估配矩形」，不能稱「四岸描測」。若此次要求輪廓照圖，建議改採本件來源四邊比例／方向候選；不為增加頂點數憑空造彎岸。

## 原圖到底畫了什麼

|圖／段落|可判讀的線|不能推出的結論|
|---|---|---|
|Ball 2003 p5 fig1|`Lake` 的 A→B、B→C、C→D、D→A 四條水側線均為黑色實線式的示意描繪；D→A 西側鄰接另一條廊道／建築線，本件取靠 `Lake` 內部的一側，未描廊道外包。|圖上沒有用岸線實線／復原虛線作考古證據分級；沒有比例尺。局部筆觸、線寬及小缺口不是已測岸形。|
|[Villedieu 2010 p1090 fig1、p1089 n2](https://www.persee.fr/doc/crai_0065-0536_2010_num_154_3_92993)|`LAC` 附近紅色 L 形兩臂及西側前庭／建築線；注2說明圖綜合 Medri 1996 fig152 與後續研究。|紅線沒有閉合成四岸，也未被圖文明確認定為四條水岸。本件仍分類為湖旁構築／擋土相關線，不能拿 L 形任意延長成已出土完整岸界。|
|[D’Alessio／Borghini 2020 pp79–81 fig3](https://www.icomos.de/data/pdf/hefte-lxxvii-0413-1447-48.pdf)|79–80頁文字支持四邊形、有廊道的湖域；81頁圖3明題為「已知遺構平面」，歸於 Medri 1996，仍只見局部湖旁線。|不提供完整測得水線，也沒有本件可採的精確水面長寬。未取得 Medri 1996 原章全文，不宣稱已直接核讀其四岸復原。|
|Ball 2003 p9|正文把湖置於後來競技場所在區，並說其較小、形式規整。|這段文字不能為無尺總圖提供精密尺度，更不能讓含廊外包成為水面。|

原圖檔：

- `research/model_reference/imperial03_events_ball2003_p5.png`
- `research/model_reference/imperial03_events_villedieu2010_fig1.png`
- `research/model_reference/imperial03_events_icomos77_p83.png`

## 描線、定位與原生候選

Ball 原圖為1700×2200px。四個圖讀線心依序為 A `[876,745.5]`、B `[902,761.5]`、C `[881,796]`、D `[852,779]`；逐點資料與來源網址保存在 `rome03_lake_outline_trace.yaml`、`rome03_lake_outline_trace.geojson`。

座標換算重用 `pipeline/register.py` 及既有修正手性的 Villedieu 三錨點配準，未使用 `imperial03_events_lake_controls_wrong_handedness.json`。程式逐點核對既有係數，差小於0.000001m；Tiberiana在西、Oppius八角廳在東北、L角在南三項方向檢查均通過。

Ball 與 Villedieu 之間只有兩個**圖形對接點**：Tiberiana中央院符號，以及將 Ball 湖圖形中心對到後來競技場中心的既有定位假設。後者不是新發現的古岸控制點。兩點擬合必然吻合，沒有獨立殘差可證明精度；不得將它與既有三個地理錨點混為一談。

無尺 Ball 總圖經這兩點對接，原始四邊圖形約23,060m²、規整矩形約134.7×171.3m，幾乎等同競技場外橢圓面積。**這是示意總圖間距導出的圖形數值，不採作古湖尺寸。** 原始描線與未縮放規整結果完整保留在 controls.json，供主代理審查。

本件建議的最少假設做法：保留舊提案明標估配的16,800m²展示面積，從 Ball 四段線取長寬比例與方向，統一縮放，不獨立重選四個岸邊留距。原圖四邊近正交，矩形規整化的最大角點差約5.4m（相當約1.3來源像素）；不把筆觸歪斜當成古岸細節。原生 pool 目前僅有 `w_m/d_m` 矩形支援，故交真正可讀的矩形鍵，未加入無效 `ring` 欄位。

候選 `rome03_lake_outline_pool_candidate.yaml`：

```yaml
id: nero_valley_lake_schematic
kind: pool
lon: 12.4924032
lat: 41.8902717
theta_deg: -34.699
w_m: 114.943
d_m: 146.16
level: draped
```

這是**來源形態示意**，不是精密描測。相對舊矩形，展示面積保留，方向約差12.7°、兩者輪廓最大距約34m；後一數字是模型間差異，不是考古誤差或證明新界線正確。約50m／10°只描述既有 Villedieu 工作容差，Ball 的示意方向、比例及古岸位置仍加上未量化的不確定性。古水位、池深及填土面未復原，保留 `level:draped`，畫面仍須標「來源約束湖址示意／非古水位」。

## 交付與檢查

- 對照圖：`research/model_reference/rome03_lake_outline/source_comparison.png`。左為原岸四點，中為來源描線與幾何規整，右為其正規化原生候選對照舊矩形及局部 L 線。
- 控制／全部數值：`research/rome03_lake_outline_controls.json`。
- 原始描線：`research/rome03_lake_outline_trace.yaml`、同名 `.geojson`。
- 原生候選：`research/rome03_lake_outline_pool_candidate.yaml`，內含完整 basis。
- 重跑：`uv run --no-sync --offline python -I cities/rome/research/rome03_lake_outline_prepare.py`。

已實跑輕量資料檢查：來源與候選多邊形合法、修正配準再現、三個方向成立；並查看輸出對照圖。未編譯、未檢查原生時間線／碰撞，未修改正式設定或既有研究原檔；由主代理審查候選後自行合併與原生檢查。

Ball/Cambridge、Villedieu/Persée及D’Alessio／Borghini/ICOMOS圖像均未核得成片重製授權。原圖及本件衍生標點對照只作內部研究，不作已授權的成片插圖；幾何提案亦不宣稱取得新的實測岸界。來源雜湊保存在 controls.json。

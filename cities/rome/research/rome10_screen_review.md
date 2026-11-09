# 10｜第一件交付：攝影棚形制比較

**已交本期來源調查和三個原生棚殼比較；尚未鋪一區，也未合併正式影片。** 調查覆蓋三個已核1953外景區、Cinecittà的同期尺寸／修復來源、1957保守宮的存留狀態與1959的資料界線。沒有1945底城可直接繼承，本件沒有製造一個。

## 可直接審看的圖

- [native sheet：三尺度各四面＋同尺度總覽](../build/review/modelview/rome10_screen_sheet/sheet.jpg)。研究片00:05.72，不是正式10站時間碼；角落1954是既有1953–1959年數在此研究秒數的插值，**不是棚建造年或已完成1954模型**。展示位置、排列與道路由sheet工具產生，非Cinecittà歷史布局。
- [中棚原圖近景](../build/review/modelview/rome10_screen_sheet/5_rome10_screen_stage_20x40_az30_5.72.jpg)、[中央大棚](../build/review/modelview/rome10_screen_sheet/9_rome10_screen_central_stage_36x80_az30_5.72.jpg)。白模僅殼體，可比較跨度、長寬與雙坡覆屋；沒有窗、隔音門、混凝土肋、鋼桁架或兩層服務翼，不能當完整建築立面復原。
- [film巡檢](../build/review/modelview/rome10_screen_sheet/build/review/eraview/screen_rome_film.jpg)、[check巡檢](../build/review/modelview/rome10_screen_sheet/build/review/eraview/screen_rome_check.jpg)。兩張均實看；地標行包含各棚多側，屋面與牆體閉合，未見反面缺失。**前兩行自動近景取到展示道路和棚間空地，有些角度裁掉棚身**，因此不宣稱所有自動近景均合格，也不把它當一區10–15°近景。三棚完整的四面比較以native sheet為準。

原生棚殼看得出單一高空間及尺度差，但外牆目前很概括；本件可審的是量體分支。來源第三維的高度未明說檐／淨／總高，目前取檐高、屋面另起，這是必須交導演判斷的估值，不把原生檢查通過當歷史尺寸已定。

## 實際執行與結果

```sh
uv run --no-sync --offline python -I tools/modelview.py cities/rome screen_rome \
  --spec cities/rome/research/rome10_screen_sheet.yaml --year 1953 \
  --sheet --at 12.478,41.903 --name rome10_screen_sheet

node tools/eraview.mjs cities/rome/build/review/modelview/rome10_screen_sheet \
  --eras screen_rome --quality low
```

兩個命令退出0，均走原生slots。modelview的檢查輸出：

```text
geocheck: every face points out of its piece
ok era screen_rome: 17 pieces
screen_rome houses_vs_walls 0 houses_vs_streets 0 landmarks_overlap 0
walls_through 0 today_vs_era 0 floating 0 terrain_cut 0
water_under_plate 0 paving_under 0 tall_foundation 0
today floating 0
clipcheck: ok
```

源資料有3個`long_hall`、沒有`fabric`；變化清冊12項，`baseline_1945_available: false`。這些是模型結構及研究資料核讀，沒有加鏡像實作的自製測試。

日誌：

- `cities/rome/research/rome10_screen_modelview.log`
- `cities/rome/research/rome10_screen_eraview.log`
- `cities/rome/build/review/modelview/rome10_screen_sheet/build/logs/compile.log`
- 同目錄的 `geocheck.log`、`clipcheck.log`

compile唯一warning是獨立歷史研究片止於1959、不是2026；這個study本來只含本期，已記錄，不改正式結尾。eraview的可選`bundle.json`404使用既有fallback，兩種look均實際產出。自動近景偏取點是本次使用限制，沒有另造巡檢腳本或修改共用工具。

`clipcheck`平坦展示地的地基值為0%，不能作Cinecittà實址或整座1950年代城市地形倍率驗收。此次沒有實址棚區、池水或住房，因此相關零值不證明那些未建物件已驗證。沒有跑正式rangecheck、全片截圖、文字排程或鏡頭驗收，因為沒有變更正式站。

## 已讀圖與來源留存

1937原刊PDF第24–28頁的五張完整PNG、1954原刊PDF第91頁及五張1953電影畫格均實看。對照索引為：

- `cities/rome/research/model_reference/rome10_screen/cn37_read-24.png` 至 `cn37_read-28.png`
- `cities/rome/research/model_reference/rome10_screen/bn54_read-91.png`
- `cities/rome/research/model_reference/rome10_screen/bfi_1953_locations_contact.jpg`

原始掃描PDF均已下載。來源目錄manifest記11個成功檔案的URL／雜湊，3個HTTP原檔抓取失敗也保留；其中L03、T02的web正文另已核讀，L04的WMF原PDF未讀到，不冒稱已讀。來源縮圖拼版只是尋頁索引，不代替上述原頁核讀。圖片均僅研究，沒有加入影片或拿作材質。

## 下一區與阻擋項

首選中央棚—前方兩層服務樓—相接橫路的連續生產街廓，留出工場通行、裝卸及有據園地。本次完成線停在待審棚殼sheet。後續一區需要：

1. 導演確認棚型和高度解讀，必要時只改本研究資料。
2. 用`pipeline/register.py`配準原圖，核實1937→1953具名存留；原刊方案的預留部分不能混入已建。
3. 補服務樓外框與屋高的本地比較；再交10–15°近景、遠景及實址地基檢查。

沒有1945整城、1950年代逐棟年表或全城住宅份額，不是改用今日模型／113填格的理由。正式10與11的疊城、鏡頭與分期由主代理處理。

## 交付清單

- `cities/rome/research/rome10_screen_survey.md`
- `cities/rome/research/rome10_screen_stage_basis.md`
- `cities/rome/research/rome10_screen_sheet.yaml`
- `cities/rome/research/rome10_screen_changes.yaml`
- `cities/rome/research/rome10_screen_facts_proposed.md`
- `cities/rome/research/rome10_screen_review.md`
- `cities/rome/research/rome10_screen_fetch_sources.py`及兩個fetch日誌
- `cities/rome/research/model_reference/rome10_screen/`
- `cities/rome/build/review/modelview/rome10_screen_sheet/`

所有新增都在本件前綴／來源子目錄／獨立study內；沒有編輯正式city、script、TREATMENT、FACTS、旁白、共享程式或其他代理檔案。

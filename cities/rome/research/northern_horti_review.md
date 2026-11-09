# 113年北側兩園重描

Sallustiani、Lucullani不再使用原來的六角形保留區。新植栽沿配準圖的道路、階地與Vallis Sallustiana谷坡展開；圖上沒有完整113年產界的部分，明列為示意接線。不是將六角形加角或平滑外框；改的是原生植栽region本身。

[整城遠景](../build/review/modelview/imperial_northern_horti/whole_southwest.jpg) · [另一方向](../build/review/modelview/imperial_northern_horti/whole_northeast.jpg) · [俯視](../build/review/modelview/imperial_northern_horti/whole_plan.jpg)

![整城遠景](../build/review/modelview/imperial_northern_horti/whole_southwest.jpg)

[Sallustiani近景](../build/review/modelview/imperial_northern_horti/sallustiani_film.jpg) · [Lucullani近景](../build/review/modelview/imperial_northern_horti/lucullani_film.jpg) · [兩園近景／俯視組圖](../build/review/modelview/imperial_northern_horti/gardens_sheet.jpg)

![兩園](../build/review/modelview/imperial_northern_horti/gardens_sheet.jpg)

[來源與逐段對照](northern_horti_sources.md) · [原圖疊合](model_reference/northern_horti_after_overlay.jpg) · [採點GeoJSON](northern_horti_boundaries.geojson)

## 保留與檢查

- **8868棟住宅與所有公共建築、道路的輸入完全相同；實際196377個非樹構件逐件比對相同。** 沒有新增住宅移除；之前的9筆來源優先移除紀錄不變。[比對數據](../build/review/modelview/imperial_northern_horti/evidence/preservation_audit.json)。
- 只改兩筆保留區。Sallustiani現有1620棵、Lucullani321棵；樹點均在原生外框內或原生8m簡化所用的10m檢查容差內。外框在指定遠景及近景已實看，不只檢查有沒有被納入。
- 原生共用隨機序列使後續個別樹位與冠形略變。已重看Pompey、Peace、Vigna及其他已通過園地：Pompey院內61棵、Peace27棵，廊牆內0；Vigna台面35棵，台面以下超過0.3m者0，最大顯示地坪誤差0.037m。[實際數據](../build/review/modelview/imperial_northern_horti/evidence/garden_audit.json)。
- 最終209700個primitive。原生geocheck面向正常；clipcheck各項0，包括樹根／平台、牆體、公共建築、道路、地形與地基。[clipcheck](../build/review/modelview/imperial_northern_horti/evidence/clipcheck.json)。
- 原生eraview兩種look共72張已巡看：[成片](../build/review/modelview/imperial_northern_horti/eraview_film.jpg)／[檢查](../build/review/modelview/imperial_northern_horti/eraview_check.jpg)。另外拍18張指定視角；Vigna及兩處內庭仍讀得出園林，未見退回台面下或長在牆內。
- 14項正式檔案雜湊未變，房型、地形×2、比例、正式旁白和13:36.90文字骨架保留。此處是113年模型驗收，不宣稱其他時期、第5步或全片已完成。
- modelview研究片停在113年、20秒無旁白的提示依其用途保留；沒有無人讀取的設定鍵，也沒有把研究用途提示當正式影片通過。

## 預覽

北園模型另存固定預覽資料夾，不會被後續正式分期的模型研究蓋掉。[開啟並重新整理](http://127.0.0.1:8766/play.html?city=rome&view&eras=imperial_complete_113&bundle=cities/rome/build/review/modelview/imperial_northern_preview/)。HTTP film已與本輪磁碟檔比較一致，並以原生VIEW重拍遠景確認。[服務核對](../build/review/modelview/imperial_northern_horti/evidence/preview_http.json)。

後續依已授權順序：先做03正式分期，再逐站做其餘時期；不能把113年末景放在前27年開場，也不能以本頁通過代替那些時期的模型與鏡頭驗收。

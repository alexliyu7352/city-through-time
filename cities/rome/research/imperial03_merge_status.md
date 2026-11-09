# 正式03：Nerva與來源湖形已合併，待本輪預覽確認

正式片目前 **913.62秒／15:13.62**，03為 **01:36.65–04:27.62**。相對已批准的14:55.67版本增加17.95秒，來自Nerva清地、升起、觀察與原生hold；旁白、191條英中字幕文字完全相同。這個數字尚未低於15分鐘，不以舊13:36.90純字幕時間代替成片排程。後續各站畫面仍須控制總長，不回寫導演旁白。

## 本輪寫入與保留

- 導演批准的Nerva97研究片併入正式03。AD14本城使用第九批原生loss；`keep`直接點名Augustus主體等地標，不再靠部件錨點的自製保護框。225.67–228.92秒拿走16組示意住宅及西南小座，共17組；230.37–233.01秒Nerva升起，之後銜接112廣場與113柱。85–97是來源建設／奉獻區間，逐件建設是示意，非每件精確定年。
- Peace西牆外細條是 `ad14_block_0404_building_006` 的兩組完整街屋；native footprint與Nerva工區交集均0，最近距0.342／3.068m。保留，不為消掉畫面物件任意放大工區。完整證據見 [收據](rome03_nerva_receipt_report.md)。
- Nero湖採Ball2003圖1四段水側線的比例與方向，原生規整為114.943×146.16m、−34.699°；16,800m²仍是展示面積估值。四邊形本身有來源，不造自然曲岸；沒有完整出土岸線／古水位證據，保留`level:draped`和示意標籤。見 [來源輪廓](rome03_lake_outline_report.md)。
- 新湖址與一塊火後示意宅地 `rebuilt_early_ad14_block_0321_building_012` 相交，依有來源建物優先規則省去該候選；原批准AD14／AD113輸入不動。另省去native點名的43塊未生成任何屋的宣告，不縮lot或改來源形狀湊過檢查。清冊見 [合併收據](imperial03_nerva_lake_merge_receipt.json)。
- 正式trace改為 `research/imperial03_nerva_lake_formal_trace.geojson`。03以外各站source設定不變，04以後段長不變、整體後移17.95秒；聲線和字幕字句不變。
- 日期維持 **27 BCE – 113 CE**。109年浴場繼續**待補**；原224–248秒那塊暗地，現因Nerva插入移到約242–266秒，不改成園地。

## 本輪實際驗證

正式compile為exit0，176,150件時期構件；geocheck每面向外、clipcheck通過。原生footprint複核前址問題0；批准AD14初期住宅118,040件非樹構件實比相同，差集雙向0；批准兩城輸入SHA不變。不是只比總棟數。日誌 [compile](imperial03_nerva_lake_formal_compile.log)、[native audit](imperial03_nerva_lake_native_audit.log)。

`tools/rangecheck.py cities/rome --stations imperial_height` 實跑 **43.05–304.27秒（02–04）**，camdump、camcheck、readcheck及逐秒圖成功。262張圖、17張native sheet已由主代理全部實看；順序為整城→火災→拆屋→重建→湖→Peace→湖退→競技場→宮城→Nerva→Trajan。此範圍平均YAVG87.0，最低一分鐘66.6，未當作全片亮度／手機實機驗收。見 [report.json](../build/review/range_43.05_304.27/report.json)。

正式eraview三個真實時刻122.95、183.72、256.85秒，film/check共六張合頁亦已全部實看；早期／湖與晚期競技場不再疊成一個不存在的模型。部分極低角度被真實前景遮擋，形制由其他側及已審定點圖交叉核對，不將遮擋說成缺件。

完整收據 [delivery_receipt.json](imperial03_nerva_lake_delivery_receipt.json) 列段長差、旁白／字幕同一性、原生檢查及範圍。03之外沒有重跑整部影片GPU檢查。8766預覽HTTP的film SHA與磁碟相同，range逐秒圖已實看新版，交件後請重新整理。

## 尚未完成與下一步

其他時期的首批調查全部收齊，形制／一區／整城的真實狀態見 [period_cities.md](period_cities.md)。01／02與04以後正式城市仍未接入，compile的12個static-picture提醒列為這些站的明確待辦；本次檢查通過不等於那些站畫面完成。02尚有線性年線對不上凱撒句子的問題，於該站正式模型／排鏡頭時綁定，不為預覽前95秒另改工作順序。

Nerva形制已批准，新的正式03排時仍交本輪預覽。103年Circus、109浴場、110 Pantheon、113其他版本界線仍在後續清冊，沒有因本次合併而宣告全部113端點完成。未製作配音、音樂或成片。

先前四段合併、植栽與字幕密度處理的完整歷史紀錄保存在 [archive](archive/imperial03_merge_status_before_nerva_lake.md)，其中舊片長、八loss容量等待及舊eraview問題不作現況。

# 113年整城住宅：逐區依據

Subura樣區69棟已確認。其來源、宅界、房型、朝向和層數凍結在`build/review/modelview/approved_subura/`；整城直接合併，不重跑小片的地塊配置。主線91a506a只增加院門兩側原先漏畫的店面，另存同角度近景。Forum—Palatine先前確認的33棟也保留為小片；兩片的比例都不外推整城。

## 採用順序與共同界線

按MODEL「No empty cities」依序查考古平面、具名復原圖／模型、影視、同期習俗。每區下表分開列出：有實證的地理／結構，使用何種復原比較，以及資料缺口如何示意補全。已有考古與學術復原比較，不另以影視覆蓋。14年DAR、203–211年Forma Urbis及四世紀Caen模型都不是113年快照；只採適用的早期建物或明列為較晚形制比較。

底圖：館藏既有KML配準的Lanciani（全城、Campus、Forum及Subura詳圖）。黑色也混合古代各期，紅色近代路不當113年街道。DAR已存463筆記錄及選出的公開定位點；`Extant remains of uncertain plan`只支持住宅存在／大致位置，標籤點不能變成測繪足跡。新增DAR逐筆API本輪回覆403，沒有把未讀到的正文當證據，採用範圍限已存目錄欄位與既有研究。公開來源索引另列於配置的`basis`。

未有連續古代地籍的部分：已確認主街、公共建築、河線、園林是固定約束，街廓按本區的街形／院落比較補全。接縫作為連續城市處理，概括分區界不拿來裁整格宅地。新支巷和宅界標「同期習俗示意」；房屋以原生types生成，整座院樓同高。未知比例不寫成歷史人口或產權統計。

| 區 | 考古平面／當地資料先查 | 具名復原及補全方式 | 採用的形制／估值 |
|---|---|---|---|
| Velabrum／Boarium | [FUR18bc](https://formaurbis.stanford.edu/fragment_18bc.html)的Vicus Tuscus、Julia／Castor關係；已確認6條小片街／巷與Lanciani | 保留小片33棟；未發掘地塊採羅馬同時期商住院落、Pompeii低宅與Ostia院樓比較 | 既有小片不改；外延以3／4層院樓、2／3層臨街單體混合，分配估值 |
| Capitoline西麓 | 市府[Ara Coeli](https://sovraintendenzaroma.it/i_luoghi/roma_antica/monumenti/insula_dell_ara_coeli)早二世紀多層商住樓；Lanciani坡腳街廊 | Ara Coeli只作高樓比較，完整內院仍按Ostia／FUR具名比較，不硬稱原址平面 | 緊密3／4層院樓與臨街單體；不把高度上限當平均五層 |
| Campus Flaminius | [FUR31系列索引](https://formaurbis.stanford.edu/plate_62.html)的劇場、柱廊與街廓；已核公共量體 | [Caen龐培附近住宅街](https://rome.unicaen.fr/monument/InsulaePompee/)的多層連續街牆作較晚復原比較 | 商住院樓沿公共院落外側與轉折街向連接；3／4層選擇估值 |
| Regola河岸 | [市府San Paolo](https://sovraintendenzaroma.it/content/il-complesso-archeologico-di-san-paolo-alla-regola-0)：一世紀末倉房，三世紀才改居住；既存官方PDF平面 | 保留Domitian商倉性質，參照[FUR24c](https://formaurbis.stanford.edu/fragment_24c.html)工作院；不把Severan居住層倒放113年 | 2層工作／倉儲院與小型店住單體；朝向隨河岸和自身街廓，倉院不是domus統計 |
| Campus西部 | Lanciani、龐培劇場及Domitian stadium外廓；[FUR39ac](https://formaurbis.stanford.edu/fragment_39ac.html)區分柱廊、園池與街路 | Caen龐培住宅街比較；劇場、柱廊、浴場及園池留地保留 | 3／4層商住院樓，街道繞公共留地，精確宅界估值 |
| Campus東部／Via Lata | DAR已核Via Lata廊道、Saepta／浴場位置；Lanciani | [Martial1.108、1.117](https://www.thelatinlibrary.com/martial/mart1.shtml)只支持早期羅馬多層居住；Caen／Ostia補形制 | 多層商住與較深住宅院混合；不據詩人的位置爭議畫精確住宅點 |
| Campus北部 | DAR建成區、Augustus墓公共留地及Lanciani街廊 | 無連續113年住宅平面，按早期羅馬商住與低層院宅比較補全，非四世紀全城密度 | 2層住宅院與3層院樓，沿廊道過渡至園地；確切數量估值 |
| Flaminia北緣 | DAR建成區及Via Flaminia沿線墓葬目錄；Mausoleum園地 | 只支持城市外延／道路與葬地界線，住宅配置採同期習俗；Domus Flaminia不因名稱而當Via Flaminia住宅 | 2／3層混合；田／園／墓地保留，沒有均勻鋪滿整個北緣 |
| Subura西 | [FUR10f、10g、10lm](https://formaurbis.stanford.edu/fragment_10g.html)、DAR谷地；已確認69棟 | 已確認片不移；其他街廓按相同本區考古形態及具名Ostia比較補全 | 完整院樓3／4層為主；小片的5層高樓保留，非普遍配置 |
| Subura東 | [FUR10lm](https://formaurbis.stanford.edu/fragment_10lm.html)與Porticus Liviae／Trajan浴場周邊的公寓、店面與斜交街廓 | 當地較晚平面作形態比較；配合已確認Clivus／Vicus Patricius廊道 | 多層院樓、巷內店住單體；避開園林、浴場留地 |
| Viminal | DAR `Domus: Viminalis1–4`目錄、Vicus Patricius與Lanciani | 遺址平面不完整；按本區谷地／丘脊街向補連接巷，低宅按Pompeii、多層院樓按Ostia比較 | 2層住宅院與3／4層院樓混合；每棟分配為估值 |
| Quirinal | DAR Atticus宅等目錄、Alta Semita與Lanciani；點位不當足跡 | 住宅存在與丘脊街廊有據，完整街廓未知；採同期混合住宅習俗 | 較深2層院宅、沿街3／4層院樓；不畫成全丘別墅或全丘Subura |
| Esquiline | DAR Horti Maecenatis／Lamiani及住宅目錄，既有園林留地 | 已核園林保留；無資料宅界按鄰近Subura東部及Pompeii／Ostia比較 | 2層住宅院與多層街坊相鄰，園林不補成住宅 |
| Oppian | [FUR10lm](https://formaurbis.stanford.edu/fragment_10lm.html)的Trajan浴場周邊密集院樓；109年浴場已完成 | 地標及公共留地保留，附近街廓依本區斜向關係示意延展 | 3／4層院樓、2／3層前鋪；不復活Domus Aurea湖 |
| Caelian | DAR `Domus: Caelius Mons1–4`目錄、Clivus Scauri與Lanciani | 整片113地籍未存；以本區住宅／聖所位置及早期羅馬住宅比較補全；不把後世Celio教堂或晚期insula原樣倒放 | 2層住宅院與3層院樓沿坡地街向混合；樓高／戶界估值 |
| Carinae／Velia | DAR `Carinae: Streets`、`Domus: Carinae`、Scaurus宅目錄及Sacra Via | 保留已採街路，較晚公共大殿不進113年；以本區狹長地形及具名院宅／院樓比較補全 | 緊湊2層院宅與3／4層商住；不是只留一排空院牆 |
| Aventine | [FUR21d](https://formaurbis.stanford.edu/fragment_21d.html)斜交兩排店面、窄巷、樓梯；DAR Aventine住宅目錄 | 21d支持有上層但未給全區確切層數；院宅比較用Pompeii，非全丘豪宅比例 | 2層住宅院，店街較高3層院樓／2層商住單體，未知分配估值 |
| Emporium | [FUR24c](https://formaurbis.stanford.edu/fragment_24c.html)的工作院、斜交街、2層樓梯證據；[25a](https://formaurbis.stanford.edu/fragment_25a.html)商倉 | 主要商倉量體已通過，僅補周邊工作／店住肌理；不把所有空院都叫住宅 | 2層工作／商倉院為主，較小店住單體；精確房間及戶界示意 |
| Transtiberim北 | [FUR28a](https://formaurbis.stanford.edu/fragment_28a.html)、[27a](https://formaurbis.stanford.edu/fragment_27a.html)（倉庫辨識有爭議，Rickman傾向商店／insulae）：右岸港口／商住空間；Lanciani河岸 | 河邊工作院與較內側店住區分開；全區113年密度未知，按本區資料及同期院宅比較 | 河岸2層工作院、內側2／3層商住院，Janiculum園地保留 |
| Transtiberim南 | [FUR138bcde](https://formaurbis.stanford.edu/fragment_138bcde.html)、[574ab](https://formaurbis.stanford.edu/fragment_574ab.html)：平行主／支街、稍彎街、倉院、店面與樓梯 | 只是較晚形態比較，該路與一世紀Via Portuensis是否相同仍未知；不照搬為113原址街廓 | 2層工作院、內側2／3層商住；本區沿河主線與支線相接 |

## 生成時哪些是估值

- 住宅城市範圍承接已核地理窗口，補合分區間窄接縫後，仍扣除Tiber、所有已核公共建築／營區、Forum、Palatine及園林。概括區界只用來查依據，不作一排排宅地的截斷線。
- 有據主街原封合併。新區連接巷及較大街廓內的支巷以各區形態比較補全；每條都標習俗示意。支巷連到既有路／街廓界，精確位置、彎折與4–6m寬度不是測繪。
- 沿每塊街廓自身長邊放完整院樓，再沿其街面補較小單體；臨街方向選最近街道。宅地長寬隨可用深度調整，沒有三種固定宅地或全區一個朝向。港口工作院可以較大，山丘與市中心各依本區比較，參數上限均為量體估值。
- 各棟從具名比較允許的層數選擇固定值；2層工作院有24c的樓梯／上層比較，3／4層院樓有Diana／Soffitto Dipinto比較，2層低宅有Amanti比較。確切分配為示意，模型棟數不是古代租戶、domus／insulae比例或人口。
- 使用共用court／row；院樓不拆成高低窄戶。主線91a506a使court底商可見。新資料不使用有院牆而宣告shops／arcade的detached或compound組合。

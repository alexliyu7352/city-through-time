# Subura 住宅重做：採用依據與界線

本輪只做 Subura 樣區。113 年整城的公共建築、Julia／Castor、營區、已採用的有據街道及地形 ×2 已通過，保留原資料；9,835 塊住宅的配置被退回。`imperial_113_layout.geojson` 保留作對照，不將新方法套到其他區。

## 撤回的判斷

9,455 棟一層院宅與 380 棟五層租樓不是歷史比例。原生成器的 `rental_share` 是嘗試放置大租樓的機率；大宅地更容易被避讓範圍扣掉，所以最後的比例連原先的示意機率也不能代表。院宅有內院，不等於它是一戶低層 domus。三種固定尺寸、每區一個方向、65×79m 巷網和整格裁邊均停用於本樣區；不以改光邊掩蓋布局。

## 按 MODEL.md 的來源順序核讀

| 層級、來源 | 能支持的畫面 | 不能支持的斷言 |
|---|---|---|
| 考古平面：[Stanford，Tina Najbjerg／Jennifer Trimble，碎片 10g](https://formaurbis.stanford.edu/fragment_10g.html)，及 [10f](https://formaurbis.stanford.edu/fragment_10f.html)、[10h](https://formaurbis.stanford.edu/fragment_10h.html)、[10lm](https://formaurbis.stanford.edu/fragment_10lm.html) | 曲折街道與窄巷；三角、梯形、菱形的建築群；臨街店面、工作院、多層住宅與小浴場相鄰。10lm 的開放內院及街道入口支持「公寓」，不是看見內院就判 domus；10f 的六間前鋪共用後方工作／生活空間。 | 圖刻於 203–211 年，不能當 113 年逐棟平面；樓梯支持有上層，沒有給每棟確切層數。不能由房間數直接算產權、出租戶或人口比例。 |
| 文獻與地理：[DAR，Elisha Ann Dumser，Subura](https://www.digitalaugustanrome.org/records/subura/)；館藏既有配準的 Lanciani | Clivus Suburanus 谷地、Madonna dei Monti 入口及相鄰的公共留地；商住混合且密建。既有街道作不移動的約束；地圖可見街界和折向逐段記錄，不以全區方格代替。 | Lanciani 混合古代各期及近代，紅色近代路不直接宣稱古路；DAR 約 14 年，也不是 113 年地籍。空白不是空地。 |
| 同時期文學：[Martial 1.117.7 拉丁原文](https://www.thelatinlibrary.com/martial/mart1.shtml)；[Juvenal 3.198–202，Fordham 所收譯文](https://sourcebooks.web.fordham.edu/ancient/juv-sat3eng.asp) | Martial 描述住處要走三段高樓梯；Juvenal 的失火場面有第三層及更高處的住戶，支持早期帝都已有多層公寓。 | 不是 Subura 的抽樣統計，樓梯段數不直接等於整棟總層數。Juvenal 的樓層解讀另見 [Hudson-Williams](https://www.cambridge.org/core/journals/greece-and-rome/article/abs/note-on-juvenal-3-198202/358450081E6F90D48C984E7EB78BB599)，不以一句詩定每棟三層。 |
| 具名復原／考古比較：[Ostia 官方 Casa di Diana](https://ostiaantica.cultura.gov.it/en/educational-panels-and-maps/the-central-area-and-the-official-complexes/casa-di-diana/)；[Insula del Soffitto Dipinto](https://ostiaantica.cultura.gov.it/en/educational-panels-and-maps/larea-a-servizio-del-fiume/insula-del-soffitto-dipinto/) | 前者有中央內院、底商，官方推定原有四層；後者官方給三或四層。採用整座院樓，不拆成高低窄戶。 | 兩者是 Hadrian 時期，僅作接近時期的形制／層數比較，不能把該建築搬到 113 年 Subura。 |
| 羅馬遺址比較：[市府 Ara Coeli](https://sovraintendenzaroma.it/i_luoghi/roma_antica/monumenti/insula_dell_ara_coeli)；[官方說明 PDF](https://sovraintendenzaroma.it/sites/default/files/storage/original/application/38bd9dd7189bec26b1f3329a548b0369.pdf) | 早二世紀多層商住樓，五層的高樓比較。底層夾層梁約 4.25m，不能當每一層都 4.25m。 | 不確證已在 113 年建成；不能推成所有租樓固定五層，或用 36×30m 當遺址實測外框。 |
| 低層住宅比較：[Pompeii 官方 Casa degli Amanti 說明](https://pompeiisites.org/wp-content/uploads/Pompei_18_Febbraio_cartella_brochure.pdf)；既有 S84 Casa del Poeta Tragico | 一至二層院宅均有具名比較；Amanti 的上層圍廊保留，不應把所有院宅壓成一層。 | Amanti 只有部分上層保存，整座等高二層院宅仍是簡化，不宣稱每翼皆為考古復原。 |
| 學術復原：[Caen，Rue bordée d’insulae](https://rome.unicaen.fr/monument/InsulaePompee/) | 底商、上層居住、連續街牆；Trajan 約 18m 限高只作檢查上限。 | 限高不是常見樓高，更不是平均五層。該組復原的全城時點為四世紀，沒有拿它的全城數量反推 113 年。 |
| 影視 → 同期習俗推定 | 上列已提供形制比較，不需用影視代替。平面缺失處才以同區上述混合商住、工作院和窄巷作示意補全。 | 補全的宅界、層數分配、屋面坡角、檐出及小巷寬度均不是實測。 |

## 比例如何決定

目前沒有可核的「113 年 Subura：domus／租樓棟數比例」。不以四世紀 Regionaries 的 insulae／domus 數、Ostia 全城統計或住宅人口去換算。**樣區不設全區的抽籤比例**：先按街界和可辨識的內院／店面群逐塊配置，再列實際模型數；沿商業主街以帶底商的多層建築為主，低層院宅放入較深地塊，工作院保留在店面之後。這個方向由 10f／10g／10lm 的商住混合與密建支持；確切數量仍是明列的復原選擇，不是出土統計，也不外推整城。

形制與社會用途分開：`court` 只說一棟圍繞內院的樓；不能據此把模型數量都列為「私人院宅」。未能由入口判定的樓不強稱 domus 或已知產權。沿巷獨立門面的單體才用 `row`；同一座院樓各翼始終同高。

## 層數與每個 type 的估值

- 帶院商住樓：三層、四層分別宣告固定層數的 type，依 Soffitto Dipinto 三／四層與 Diana 四層比較；五層只作 Ara Coeli 型的少量高樓比較，不整排複製。每棟等高，不能把同一樓拆成逐戶隨機高低。
- 巷內較小商住單體：二層，對應有樓梯、前鋪與後方生活／工作空間的低端復原選擇；確切二層是估值，平面只確證多層。相鄰單體不是來源所稱的一次建成的大院樓。
- 低層院宅：一、二層分開宣告，沿用 S84 與 Amanti 比較；全院等高是原生類型的量體簡化。
- 平均層高取 3.5m 作原生量體估值（Caen 用於約五層／18m 的比較），不是實測每層。屋頂 25°、檐出 0.35m 延續已審類型的具名復原估值，均寫入 `basis`；地塊長寬依各街廓可用深度配置，不再只有三個尺寸。內院份額由具名院樓比較估讀，不能宣稱逐棟精確復原。

## 樣區驗收

實作平面補充：`subura_sample_plan.yaml` 記錄 10g 研究檢視圖上的逐點描線，保留主街折向、交叉街及巷的拓撲；沒有再設 65×79m 網格。碎片本身不是已配準的 113 年街區，這裡採用的是**較晚考古平面的形態轉用**：每像素 0.42m、旋轉與放置均為示意，按既有 Subura 廊道配置；不宣稱是 10g 在羅馬的精確配準或其上每棟樓的原址。Lanciani 瓦片仍沿原館藏配準，沒有以新擬控制點改動它。已通過道路另外保留為固定約束，因此本樣區不能當作精確重建那塊碎片的地理版本。

屋宅生成順序改為先放完整院樓，再沿街廓的各段臨街面補獨立門面的商住房，避免先塞小格把大樓位置切碎。每塊原生宅地的尺寸適應其街界；院樓同棟同高，變化在樓與樓之間。確切住宅分類、戶界與樓高分配是復原選擇。這一版用來確認密度、街形及多層商住輪廓，**不是已有史料可支持的 113 年租樓／domus 定量復原**；該比例仍無確證，不能因樣片通過就升格為整城史實。

交低角度 10–15°近景與能看完整樣區邊界的遠景；另附俯視、來源疊圖、房型 sheet 與原生兩種光照各面。查：連續街牆、各街廓自己的方向、區邊沒有整格鋸齒、無用途不明的大楔形空地；層數變化發生在不同樓體之間。原生 geocheck／clipcheck 重新檢查本樣區。未確認前不改整城住宅配置。

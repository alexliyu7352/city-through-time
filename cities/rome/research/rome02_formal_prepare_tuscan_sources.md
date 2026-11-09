# 早期Capitol公共場域：Tuscan比較候選

狀態：獨立研究，**不是已批准509BCE復原、不是整座早共和城**。完整基址與早期三室形制一同交看；69BCE Catulan、44整城、Pompey組群均未改。資料以原生`parts`／`stepped`／`prism`／`arches`／`column.repeat`／`long_hall`宣告，不自寫mesh。

|ID／原件|本輪實讀／實看|採用與界線|
|---|---|---|
|T01：既存R08，[Musei Capitolini](https://www.museicapitolini.org/it/node/2488)與[DAR Jupiter](https://www.digitalaugustanrome.org/records/iuppiter-optimus-maximus-capitolinus-aedes/)|重讀`model_reference/rome02_republic/{jupiter_official,dar_jupiter}.txt`，核官方傳統509奉獻、Tuscan三室／中央較寬、深前廊與三側柱廊；DAR基址約62×53m／3.6m、83BCE火／69BCE重奉獻|位置／135°方位沿同址控制；使用早期類型描述，不複製69模型。官方約55×60m與DAR約62×53m不平均；各層基礎定年有爭，3.6m不是已測509全體高。階梯存在有據但具體形制未存。|
|T02：[Michetti，2010，Deliciae Fictiles IV，96–106](https://elearning.uniroma1.it/mod/resource/view.php?id=637160&lang=de)|公開原PDF19頁（含前置頁）；核正文96–98，實看印刷97的圖1／2，及98談坡度原文。圖1是Colonna／Foglia1993復原，轉引Colonna2008，圖明18.38×18.38m、三室、中央寬5.337m／兩旁4.4475m、牆厚／柱徑模數約.89m；98由acroterial底座斜緣算12°屋坡。|具名同期Portonaccio的三室平面／屋坡比較。圖是學術復原，不冒作本輪讀到Colonna2008全書或509Capitol發掘圖；圖2只是現址部分虛擬復原照片。18.38m不拿來取代Capitol基址。|
|T03：[Garagnani、Gaucci、Gruška，2016，VAR7(15)，77–86，DOI10.4995/var.2016.5846](https://cris.unibo.it/handle/11585/567634)，[出版PDF](https://cris.unibo.it/bitstream/11585/567634/1/5846-23164-2-PB.pdf)|原刊PDF10頁全文已取得；核78–80的年代／平面／上構論證與圖2。Uni（Kainua／Marzabotto）定晚6世紀，作者由寬19.14m及Vitruvius推柱約6.4m、下徑.9m／上徑.67m；明言上構未存。80列Portonaccio12°及其他同期廟，Uni選16°。|取6.4m柱高及.9／.67m徑作**具名同期建築復原的絕對模數比較**；它本身仍是作者依較晚Vitruvius的推定，不是出土柱高。Capitol遠較寬，沒有把柱高按53/19.14放大成17.7m，也沒有證明這個6.4m選值適用整座Capitol結構。這一低上構只是待導演看形的有限比較分支。|
|T04：[ETRU原出土／館藏敘述](https://www.museoetru.it/never-seen-before/the-statues-of-apollo-and-hercules)、[Sapienza發掘團隊](https://dipantichita.web.uniroma1.it/en/excavations-and-research-veii-sanctuary-portonaccio)|兩正文已開；ETRU為約510BCE三室Tuscan廟，Sapienza作約500BCE，年代量級相合；核Vulca工作坊／Capitol屋頂裝飾比較。|只是時期、類型與藝術聯繫比較；不把Portonaccio雕像或水池搬到Capitol。ETRU約12m是高處acroteria敘述，不當柱高。|

原件均用`rome02_formal_prepare_`前綴歸檔；PDF不是第三方上屏素材。部分原站（UPV）憑證／反機器人頁無法取原文，未繞過驗證，改用作者所屬Bologna大學公開出版PDF；第一次失敗不當成功。SHA與大小見`rome02_formal_prepare_sources_manifest.json`。

## 資料如何成為本輪候選

|部位|值與依據|仍是估值／尚未表現|
|---|---|---|
|整體基址|53×62m、3.6m，T01選DAR報告分支；位置12.48185,41.89232、135°為既有同址控制|不宣稱509單層精確尺寸／古標高；今日DEM上的原生整平不是古地坪。|
|三室|42×28m合計後部範圍，13:16:13室寬、中央較寬；T01類型＋T02中央寬於兩側|42×28及各房位置／1.6m牆厚均為本輪有界工作估值，不是把18.38m小廟等比放大成Capitol實測。|
|前廊／側廊|3列各6柱，前後24m範圍；兩側各再2柱。T01三排深前廊與三側colonnade類型|6前柱為DAR通行Tuscan復原比較；22根總數、9.6m／12m間距、兩側柱數與位置都不是出土清冊。大跨距承載、古木架並未工程驗證。|
|柱／壁上高|6.4m，柱下徑.9m、頂.67m，T03作者推定模數|只有一個低上構比較分支，不稱原高；沒有同時加高到69版。土坯／木構材質在白模中不作精細復原。|
|覆屋|51×60m共有雙坡、12°坡T02；原生屋頂支承於柱頂，再加1m水平承頂量體|1m承頂、.6m出檐與屋面全外廓為工作估值；不繪無據的pediment雕塑、四馬車、逐瓦／木架。T03提醒大尺度出檐不能機械照Vitruvius比例擴大，因此不用1/4屋長。|
|入口／階梯|3個真正通孔入口；階寬7.8m，取T02約2.7m階寬／18.38m廟寬的比值乘53m，作類型比較|通孔寬／高、階數與位置均估值；T01說Capitol階梯無存，不能稱為考古測繪。|
|公共地面與街坊|本輪不鋪Capitol整山草地，不造早期街坊|已批44草地是44用途窗，不能回填509；周邊暗plate是研究未建部分，不主張509空無一物。|

native研究分三段：0秒起基址證據、6秒起三室／柱廊、12秒起覆屋；都標同一來源觀察對象。4／10／15秒三張圖是研究揭示，**不是509年先裸露基礎、隨電影秒數歷史施工完成的主張**。正式片只在導演確認後按敘事場景取用。

## 原圖對照與仍需批准之處

- 原刊圖1保留三室且中央較寬、前廊與後室相分；本候選保留這個關係。Portonaccio本身只有兩個明確前廊柱位，沒有照搬成Capitol22柱；Capitol三排／三側廊另據T01。
- 原刊圖2是局部現址架構，不能當完整屋脊、柱高或外立面測圖。12°取的是原文計算，非透視照片量高。
- 小廟的6.4m推定模數與更大Capitol結合後會顯得很寬低；這正是本輪需給導演判斷的形制分支，不宣稱考證已定。若改上高，應以Capitol更專門的早期復原立面或同期大廟補證，不能默默換回69版。
- 83BCE毀、69BCE重建來源已核；本候選各part具穩定id，將來可由同城native `lose.select`只退上構並`keep`基址，再上69版本。此生命周期本輪未寫正式，也未把一個509比較模型延用到44冒充同上構。

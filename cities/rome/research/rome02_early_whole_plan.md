# 509早期整城：逐區來源及執行入口

房型221731、6c道路／Curiae西側最小窗223452均已批，按此輸入生成全城。Capitol164417、160整城215047、44全城保持。觀察509為傳統紀年，native揭示不等於每屋509新施工。

|區域|依據／範圍|有界補全與具體缺口|
|---|---|---|
|全城範圍／七丘防線|既有W02原作者Cifani2016pp84–88、fig1的晚6c具名復原；按500m尺原生描得370.47ha，作者約365ha|只作重建分支，不當實測建成界；單近似山丘錨不偽造殘差，位置與一般化程度未獨立驗精。沒有照搬160R21四世紀route/body，也未按面積硬湊住宅。|
|Capitol|R08基址＋164417已批Tuscan三室／深廊|原模型整件沿用；未用69Catulan／Tabularium。公共聖區邊界與earth材質估值。|
|Forum／Comitium—Regia／Vesta|R09／R17早期公共中心；Regia晚7c遺構、晚6c三室／梯院關係|Regia2.7m單層屋頂僅早期具名比較，室寬／深／偏移估值；Vesta／Hostilia完整早立面仍缺，不用29／Severan替代。497Saturn、484Castor、431Apollo不在509升。|
|Palatine北東—Velia|Capys2021p53fig25的6c界牆／道路，p88早臨街房；已審小型窗|保護原街曲線、碎牆、三lot及真正聖區ground；新parcels不切入。圖外數量／宅界／街延伸仍比較估配，無160集水院或360/350平台。|
|Palatine／Velia其餘住居|Cifani七丘古地形、早期街居與同期中義大利房院比較|丘谷間大街連通有據場址，未發掘支巷交native parcels。住宅為可讀地面層代理，不宣稱一層百分比、完整戶界／人口。|
|Quirinal／Viminal／北Esquiline|Cifani晚6c擴圍分支及古地形谷／脊關係，86–87考古／墓地分布論證|道路與地塊為有界示意，不倒填帝國浴場／Sallust園或160宅體；外墓地不填住宅。源圖不能給區內屋數／店舖比例。|
|Caelian／Carinae|同一具名七丘復原分支的南東坡／谷交通|房院比較補全，朝向沿native各街面，不全城同一bearing／grid；未確定公共專用地不自創大廣場。|
|Aventine／Boarium|Cifani84／88把Aventine及谷底防線納晚6c學說；R09早河渡／交通用途比較|河側住居／工作院採同一低層比較形制，沒有193港倉／晚2cGalbana；道路寬／宅界均估值。Diana傳統位置約300m分歧仍不冒作精確屋址。|
|Circus谷地|既有DARCircus早期賽場用途／傳統與谷地關係|只earth開場及估計周界，不是46Caesarian看台／33海豚／10方尖碑；不把所有未知住宅空隙鋪ground。|

普通屋用221731核可native detached實頂／單門型；San GiovenaleB/C小體量與外院、Period3建築傳統，以及同時期AreaF長屋11.3×5.8／12.3×5.1／15×6.35m作具名尺度比較。9–16m工作lot及native比例變幅、房戶分隔、間距／占用與製作件數不當古代統計。2.7m／22°／.25m保持估值；不把Kc空白當已證庭院，不前置impluvium。模型不暴露已確定的內室，也不宣稱Rome全城一層。

防線採來源路線＋4m高／2m寬的參照身與無普通轉角／定距塔列；這兩尺寸及native parapet是製作估值，不是四世紀40×12magger或160牆身回填。作者6c防線包含削坡／擋土／谷底牆，模型概括形體須標示意，不聲稱每米同構。門位／早期上構仍有具體缺口，不能把後期拱門畫進509。

原生入口`rome02_early_whole_build.py`（只author資料），`rome02_early_whole_spec.yaml`、`...trace.yaml`、`...streets.geojson`、`...domain.geojson`、`...reserves.geojson`、`...parcels.yaml`。住宅只由native`tools/parcels.py`生成，公建真site用`citygen.landmark_site`；同一連續source域內切街坊，避免分工作域造成假大縫。研究／core留/data，重做候選沿既有/tmp alias，同hashprepared不重做prep。

尚未鋪早期整城／統編三相。早期整城審後再按最新原話原生統編完整三相72s提案、量實秒／增量、做01/03接縫。固定191文字不改，phase／public生命周期沿`rome02_formal_prepare_phasing.md`；01必由其自身native lose分批退，03正式保持，無寫鎖不合併。

# 用鼓與塤串起咸陽六千年的配樂

咸陽各時期的聲音，**越古越有實物，越近越靠慣例**：仰韶有關中出土、測過音的陶塤（一件只吹得出兩三個音，半坡那件是一個小三度）；秦有李斯親口說的「擊甕叩缶、彈箏搏髀」本土聲，有秦公鐘鎛、石磬，還有兵馬俑坑裡的戰鼓；焚城那一夜《史記》沒寫任何聲音，全靠推想；漢唐的音樂史料幾乎都寫對岸的長安，咸陽（當時叫渭城縣）本身只有很薄的陵墓樂俑紀錄；明清以後，今天咸陽轄下的涇陽、三原是秦腔標準音所在，弦板腔也在乾縣、禮泉、咸陽一帶成形，聲音是梆子、二弦、板胡和鑼鼓陣；1936 年以後換成汽笛、紗機、鑼鼓與手風琴；1975 年以後沒有在地樂種可依，只能借西北風、錄音機、地鐵這類時代質感。能貫穿全片的是**鼓**：從秦到今天，每個時代在關中都找得到鼓的實物或記載，也正合導演「秦都、帝都、焚城以鼓為主」的要求；再用**半坡陶塤的兩音**當片頭片尾的記憶，用**箏**（「真秦之聲」）當秦以後的旋律身份。Stable Audio 3 Medium 對中國鼓樂所知極少（AudioSparx 的亞洲鼓類只有 16 首、日本太鼓 30 首），寫「Chinese war drums」多半會得到太鼓加預告片鼓加鑼；medium 上 negative_prompt 和 cfg 都不起作用，不要的東西只能靠「不寫」再「挑候選」；換 seed 幾乎不變，要變就改措辭；每次生成 60–120 秒，更長用 continuation 接，所有精準到秒的火起、留白、熄燈都在剪輯時做。照這些結論，現行 `cities/xianyang/MUSIC.md` 草稿有六處要改：負面提示詞與「調高 cfg」無效；「每段換 3 個 seed 出候選」幾乎沒有差別，要改成換措辭；共用句裡的 "voice" 會招來人聲；簫與古琴當城市聲音缺乏關中證據；M02 的銅管是時代錯置；M03 用二胡既是時代錯置，也違背焚城以鼓為主的要求。下文用【實證】（出土實物或原典明文）、【推論】（由實證推出或屬設計）、【現代慣例】（今人復原、舞台包裝或配樂習慣）三級標記。

## 秦以前有實物可依，焚城的聲音全靠推想

關中仰韶文化唯一有測音數據的樂器是**陶塤**：西安半坡、臨潼姜寨、淳化黑豆嘴都有出土【實證】。半坡那件測得兩個相差 **300 音分的小三度**，姜寨二孔塤是 la–ti–re，黑豆嘴是 sol–do–re，每件只有 1 到 3 個音，音區很高（[史珊 2008，引呂驥 1978《文物》](https://ks3-cn-beijing.ksyun.com/attachment/fdf5c06fcffe4d249a10593218554cd3)）。換算成頻率大約 1.5–1.8 kHz，聽起來像哨子或鳥鳴【推論】。說法有衝突：China Daily 寫半坡塤能吹 G4 到 C5 四個音（[China Daily](https://govt.chinadaily.com.cn/s/202302/09/WS63e4c953498ea274927af597/neolithic-period-7000-1700-bc.html)），中文維基卻說這時期的塤沒有按音孔（[維基百科](https://zh.wikipedia.org/zh-tw/埙)），找到呂驥原文前只能並列。今天常見的八、九孔低音塤是現代改良品【現代慣例】，比原物低一到兩個八度、暖得多。陶鼓、骨笛、石磬在關中仰韶遺址都查無可靠紀錄；《呂氏春秋·古樂》說遠古「冒缶而鼓之，乃拊石擊石」，那是戰國末的傳說（[維基文庫](https://zh.wikisource.org/wiki/呂氏春秋/卷五)），所以開場的手拍陶罐、踏地只能算合理想像的聲景【推論】，整段不該有任何金屬或弦樂。

秦的本土聲音有原典明文。李斯〈諫逐客書〉說：「夫擊甕叩缶彈箏搏髀，而歌呼嗚嗚快耳者，真秦之聲也」（[《史記·李斯列傳》](https://zh.wikisource.org/wiki/史記/卷087)）：敲陶甕陶缶、彈箏、拍大腿、放聲呼喊，四項裡三項是節奏【實證】。東漢《風俗通義》說缶是「秦人鼓之以節歌」，箏則「或曰秦蒙恬所造」，後者只是傳聞（[維基文庫](https://zh.wikisource.org/wiki/風俗通義/6)）；澠池之會上藺相如逼秦王「擊缻」，可見在外人眼裡缶是秦的鄉土樂（[《史記·廉頗藺相如列傳》](https://zh.wikisource.org/wiki/史記/卷081)）。同一篇〈諫逐客書〉也承認秦宮廷已「棄擊甕叩缶而就鄭衛」，所以秦聲分兩層：粗、直、熱的本土層，和外來的宮廷層【推論】。秦代的箏沒有實物，弦數不明，今天的 21 弦箏屬【現代慣例】，配樂宜少用弦、多用低音撥奏。「歌呼嗚嗚」的吼聲在本片提示詞規則下不能寫，要用只能另外錄。

禮樂層同樣有實物。寶雞太公廟 1978 年出土秦武公鐘 5 件、鎛 3 件，最大的鎛高 75.1 公分、重 62.5 公斤，在合奏中負責「定節奏」（[新華網](https://www.news.cn/culture/20240524/1c6b1ba38de94a44845d0f11b7f59da4/c.html)）；鳳翔秦景公大墓的石磬殘銘寫著「**百樂咸奏，允樂孔煌**」（[史語所集刊](https://www1.ihp.sinica.edu.tw/Publications/Bulletin/979/Article/424)）；始皇陵出土一件紐上刻「樂府」的錯金銀鈕鐘，音準清亮（[秦始皇帝陵博物院藏品頁](http://qshdlbwy.fractaltest.cn/impor_collections/423.html)）【實證】。帝都的聲音本身就是六國的戰利品：始皇「收天下兵，聚之咸陽，銷以為鐘鐻」，又把「所得諸侯美人鐘鼓，以充入之」（[《史記·秦始皇本紀》](https://zh.wikisource.org/wiki/史記/卷006)）。這給 M02 一條有根據的結構：先是本土的缶、拍腿、一把箏，再一層層疊進六國的鐘鼓，最後收攏到同一個鼓點【推論】。

導演要的鼓，證據最硬。兵馬俑一號坑第三次發掘清理出「**鼓 2 處、鼓槌 1 處**」，歸為指揮設備（[中新網 2023](https://www.chinanews.com.cn/cul/2023/01-12/9933826.shtml)）；將軍俑旁常有鉦和鼓的遺跡（[香港政府新聞網](https://www.info.gov.hk/gia/general/201207/08/P201207060607_photo_1039718.htm)）【實證】。戰國兵書寫明了用法：「聞鼓聲而進，聞金聲而退」（[《荀子·議兵》](https://zh.wikisource.org/wiki/荀子/議兵篇)），「擊鼓而進……擊金而退……金鼓俱擊而坐」（[《尉繚子》](https://zh.wikisource.org/wiki/尉繚子/全覽)）。所以秦鼓是號令，不是旋律：整齊、齊奏、有命令感，再用一記鉦（手持的青銅打擊器）切斷鼓聲【推論】。秦相呂不韋在咸陽編的《呂氏春秋》批評「大鼓鐘磬……以鉅為美，以眾為觀」是亡國之樂（[維基文庫](https://zh.wikisource.org/wiki/呂氏春秋/卷五)），高峰最後幾拍的鼓若「大到過頭」，正好預告焚城。鑼、鈸、嗩吶、二胡、琵琶、銅管和太鼓的典型節奏型都不屬於秦；「大秦戰鼓」一類是今天的舞台包裝【現代慣例】。

焚城完全沒有聲音紀錄。《史記》只有一句「屠咸陽，殺秦降王子嬰，燒秦宮室，火三月不滅」（[《史記·項羽本紀》](https://zh.wikisource.org/wiki/史記/卷007)）【實證】。楚軍的聲音只能從楚人自己的文字推：巨鹿之戰「楚兵呼聲動天」；〈國殤〉「援玉枹兮擊鳴鼓」寫的正是與「挾秦弓」者的戰鬥；〈東皇太一〉「揚枹兮拊鼓，疏緩節兮安歌」給出稀疏、緩慢的楚鼓性格（[《九歌》](https://zh.wikisource.org/wiki/九歌)）。所以 M03 合理的做法是：**同一批鼓失去秦式秩序**，變成稀疏、不規則的哀鼓，最後只剩一面悶鼓的心跳【推論】。有兩個常見錯誤要避開：「四面楚歌」是約四年後垓下的事，不是焚城現場；阿房宮前殿考古沒有火燒痕跡，也根本沒建成（[新京報・劉瑞](https://news.sina.cn/2021-12-06/detail-ikyamrmy7172433.d.html)），被燒的主要是渭北的咸陽宮室。

## 漢唐的史料都在長安：鐘磬退場，鼓吹和送別笛聲接手

漢代起，咸陽降為渭城縣，咸陽原成了帝陵區，音樂史料幾乎都寫對岸的長安宮廷。漢哀帝罷樂府時留下的鼓員仍有「**凡鼓十二，員百二十八人**，朝賀置酒陳殿下，應古兵法」（[《漢書·禮樂志》](https://zh.wikisource.org/wiki/漢書/卷022)）【實證】，可見漢代宮廷的骨架還是鼓。行進樂分兩種：簫加笳叫「鼓吹」，鼓加角叫「橫吹」，後者「減為中鳴，尤更悲矣」，史料已點出角聲帶悲意（[《樂府詩集》卷二十一](https://zh.wikisource.org/wiki/樂府詩集/021卷)）；俗樂相和歌用笙、笛、節、琴、瑟、琵琶、箏七種樂器，「絲竹更相和」（[《樂府詩集》卷二十六](https://zh.wikisource.org/wiki/樂府詩集/026卷)）。學者周楊指出，武帝以後「樂鐘制度」式微，鐘磬讓位給鼓吹（[周楊文](https://www.sinoss.net/c/2025-03-03/647718.shtml)），正好當作秦都退場的音樂隱喻【推論】。咸陽原本地的證據很薄：漢陽陵出土的男性樂伎俑，手中樂器已朽（[維基百科引《文博》2009](https://zh.wikipedia.org/wiki/汉阳陵)）；楊家灣漢墓的樂俑只見媒體轉述，不採用。

唐代長安是胡漢混編。立部伎「自《破陣舞》以下，皆雷大鼓，雜以龜茲之樂，聲振百里」（[《舊唐書·音樂志二》](https://zh.wikisource.org/wiki/舊唐書/卷29)），坐部伎則是曲項琵琶、箜篌、篳篥、笙這類細樂【實證】。篳篥「其聲悲」；曲項琵琶「本出胡中」，舊時用木撥彈。玄宗愛羯鼓，稱它「八音之領袖」，說它的聲音「焦殺嗚烈……宜高樓晚景，明月清風，破空透遠」，他卻「酷不好琴」（[南卓《羯鼓錄》](https://zh.wikisource.org/wiki/羯鼓錄)）。《羯鼓錄》還記了一個現成的配樂意象：安史之亂後，李琬在長安務本里夜裡聽到羯鼓，鼓工說祖傳的曲子因「父沒河西」失了結尾，夜夜在找；李琬答「意盡即曲盡，又何索尾焉」。一首沒有結尾、在餘音中淡出的曲子，可以直接借來當唐段的收法【推論】。

送別段的〈渭城曲〉在唐代確實有人唱。《樂府詩集》說它「本《送人使安西詩》，後遂被於歌」（[《樂府詩集》卷八十](https://zh.wikisource.org/wiki/樂府詩集/080卷)）；白居易寫唱法是「**高調管色吹銀字，慢拽歌詞唱渭城**」（[〈南園試小樂〉](https://zh.wikisource.org/wiki/南園試小樂)），又寫「且遣琵琶送一杯」（[〈對酒五首〉](https://zh.wikisource.org/wiki/對酒五首)）【實證】。也就是高音管樂領奏、拖得很慢、琵琶在席間伴奏，不是古琴。蘇軾考出唐本「三疊」是第一句不疊、後三句各唱兩遍，共 7 個樂句（[《仇池筆記》](https://zh.wikisource.org/wiki/仇池筆記)），可以拿來排樂句【推論】。今天通行的古琴《陽關三疊》是明代琴歌，最早見於明代中期琴譜，研究者明說沒有證據顯示唐代旋律就是這首（[silkqin](https://silkqin.com/02qnpu/09zysz/zy13ygsd.htm)）【現代慣例】；旋律雖屬公有領域，片中不能宣稱是唐音。笛在關中也有本地根：茂陵人馬融〈長笛賦〉寫終南山竹，又寫在「客舍逆旅」聽人吹笛「甚悲」（[〈長笛賦〉](https://zh.wikisource.org/wiki/長笛賦)），和王維的「客舍青青」在地理與情緒上相合。

漢唐同段最大的陷阱，是把唐代樂器放進漢代。曲項琵琶、五弦、羯鼓、篳篥、方響、拍板、銅鈸只屬唐段，豎箜篌到東漢靈帝才流行（[《舊唐書·音樂志二》](https://zh.wikisource.org/wiki/舊唐書/卷29)）【實證】；大鼓、排簫、笳、角、笙、笛、瑟、箏、臥箜篌、直項圓體的「秦漢子」（阮類）兩段都可用，其中「漢代琵琶是直項」屬學界通說。二胡、嗩吶、揚琴、三弦、秦腔板式則兩段都不該出現【推論，年代屬一般音樂史常識，筆記未逐條找原典】。

## 明清到 1950 年代，咸陽本地的聲音是梆子、二弦和鑼鼓陣

明清是咸陽第一次有「本地樂種」可以點名。秦腔元明之際形成於關中，明清之際傳遍全國，文場以板胡為主，武場用干鼓、暴鼓、戰鼓、勾鑼等（[中國非遺網・秦腔](https://www.ihchina.cn/project_details/13165.html)）；它用棗木梆子擊節，所以叫「梆子腔」，**標準音以涇陽、三原、高陵為準**（[維基百科・秦腔](https://zh.wikipedia.org/wiki/秦腔)），而涇陽、三原今天都屬咸陽【實證】。秦腔分歡音和苦音：苦音音階裡微升的 4 和微降的 7 一直在游移，聽來深沉哀婉，歡音則接近大調（[華音網](https://www.huain.com/article/guzheng/2023/0827/2148.html)）。這給全片一條調式弧線：古代與失落段帶苦音色彩，希望段轉歡音【推論】。不過板胡是明末清初才和梆子腔一起成長的（[華音網](https://www.huain.com/article/erhu/2024/0117/2505.html)），南路秦腔原本以二弦主奏（[中國非遺網・漢調桄桄](https://www.ihchina.cn/project_details/13170.html)），清代以前的聲音比今天的大樂隊乾硬得多。

比秦腔更貼近「靜的縣城」的是**弦板腔**：清初在乾縣、禮泉、咸陽一帶形成，只有二弦、三弦和兩種木板（俗稱「呆呆」），牛車當舞台、一盞燈映皮影，二胡要到道光、咸豐年間才加入（[中國非遺網 11287](https://www.ihchina.cn/project_details/11287.html)；[中國非遺網 13400](https://www.ihchina.cn/project_details/13400.html)）【實證】。寺觀、文廟的氛圍可以借關中鼓樂的吹管：笛領奏、笙依笛定調，再加管子和雲鑼（[中國非遺網 10319](https://www.ihchina.cn/project_details/10319.html)）。但西安鼓樂的流布區是西安城區與長安、周至、藍田，沒有咸陽；它自稱的「唐代遺音」是聲望包裝，最早的抄本是 1689 年，實際面貌更接近明末到清代（[Wikipedia](https://en.wikipedia.org/wiki/Xi%27an_guyue)；[Stephen Jones](https://stephenjones.blog/ritual-life-around-xian/)）【現代慣例】。渭河咸陽段的船工號子查無紀錄，最近的在地依據是涇陽的涇河號子（陝西省級名錄）（[陝西第二批省級名錄](http://www.minwang.com.cn/mzwhzyk/674771/682705/765186/sjfwzwhycml/765300/766496/index.html)）；號子是人聲，本片提示詞寫不了，要用只能另錄。明清縣學文廟的祭孔樂舞規模也查不到，所以文廟鏡頭不要寫成編鐘大合奏。

1936 年咸陽站在隴海線上開辦（[Wikipedia](https://en.wikipedia.org/wiki/Xianyang_railway_station)）。1949 年 5 月 18 日中午，國民黨部隊正要炸咸陽紡織廠時，解放軍二軍趕到，在此之前渭河鐵路大橋和渡口浮橋已被炸斷（[咸陽發布](https://finance.sina.cn/2023-05-17/detail-imyuayws5426646.d.html)）；第六軍靠當地船工帶路，20 日拂曉搶渡渭河；隔天西安入城時，市民「敲鑼打鼓、燃放鞭炮」，部隊唱〈三大紀律八項注意〉（[騰訊新聞](https://news.qq.com/rain/a/20240520A03RGI00)）【實證】。要注意，**鑼鼓鞭炮是西安的紀錄**，咸陽本身沒有群眾歡迎的描寫，秧歌、腰鼓更無證據。咸陽本地的鑼鼓陣可以參考省級名錄裡秦都區東南坊的牛拉鼓（大鼓、大鑼、鐃鈸、牛角號，陣容龐大）（[中國非遺網 25167](https://www.ihchina.cn/project_details/25167.html)）和乾縣蛟龍轉鼓（「八鑼八鼓十六鐃鈸二馬號」）（[張靜 2017](https://lishiwenhua.snnu.edu.cn/__local/4/C9/57/EEBCD2A1E4FC16849E7DED55403_EC5E2E53_813A0.pdf?e=.pdf)），但牛拉鼓「可追溯到秦朝」只是傳說【現代慣例】。1951 年建廠、1952 年開工的西北國棉一廠是紡織城的起點（[贏商網](https://m.winshang.com/news740116.html)）；1950 年代全國的文工團、宣傳隊靠手風琴下鄉（[The World of Chinese](https://www.theworldofchinese.com/2019/05/the-peoples-squeezebox/)）。M06 的在地做法因此是：板胡在歡音上領奏，梆子推著二六板走，火車軌縫與紗機節奏當底，手風琴墊和弦，高點才進關中鑼鼓陣【推論】。

## 1975 年以後沒有在地樂種，只剩時代質感與兩城對話

1980 年代最像「陝西」的流行聲音是西北風，但它是全國性的想像。1986 到 1988 年間，創作者拿北方民歌音調，加上搖滾配器和「喊唱」，1988 年中就退潮（[虎嗅・金兆鈞](https://www.huxiu.com/article/4889527.html)）；合輯《西北風》的歌手來自遼寧、北京、上海，「罕有真正的西北人」（[鈦媒體](https://www.tmtpost.com/6150038.html)）【實證】。站在咸陽人自己的角度，1980 年代的日常聲音是四喇叭錄音機、翻錄卡帶和鄧麗君（[搜狐](https://m.sohu.com/a/252366286_114988)；[天下雜誌](https://www.cw.com.tw/article/5121658)）。M07 可以借西北風的強拍、兇猛貝斯和錄音機帶噪，但不引任何旋律（這些歌都有版權），也不必假裝那是咸陽本地的聲音【推論】。1980 年代電子琴、合成器在中國普及到什麼程度，這次查無可靠資料，用合成器琶音純屬設計選擇。

1998 年前後的下崗記憶，最有代表性的聲音是央視再就業公益廣告的主題歌〈從頭再來〉，但出處只有彙整站，年份還有 1997、1998 兩說（[maigoo](https://m.maigoo.com/top/424910.html)）。它是副歌上揚、「打氣」式的官方聲音，觀眾一聽就對號入座；M08 要的是悲傷與念舊，應該反其道而行【推論】。用手風琴喚起工廠懷舊，目前只有電影《鋼的琴》（2010）一例：主角是手風琴手，和幾個下崗的朋友組樂隊（[Wikipedia](https://en.wikipedia.org/wiki/The_Piano_in_a_Factory)）。咸陽紡織廠本身有沒有廠歌或廣播站錄音，這次沒查到。

21 世紀的陝西融合有兩個大型範例。2016 年央視春晚的《華陰老腔一聲喊》被形容為「黃土與搖滾、電聲與弦樂的碰撞」，老腔本身的核心是一人領、眾人和、驚木拍板凳（[中國非遺網](https://www.ihchina.cn/news_1_details/10269.html)）；2021 年西安全運會開幕式則把千人鼓陣、千人秦腔、原創新秦腔和裸眼 3D 投影疊在一起（[澎湃](https://m.thepaper.cn/baijiahao_14535012)）【實證】。後者「鼓從少到多、再疊上光影」的結構，和本片白模投影逐層點亮的語彙相合，M11 可以只借結構。地理要分清楚：安塞腰鼓、信天游屬陝北，華陰老腔屬渭南，威風鑼鼓屬山西臨汾，都不是咸陽本地的聲音；《河西走廊》那種 duduk 加新世紀弦樂（[維基百科](https://zh.wikipedia.org/zh-cn/%E6%B2%B3%E8%A5%BF%E8%B5%B0%E5%BB%8A_(%E7%BA%AA%E5%BD%95%E7%89%87))）則是絲路紀錄片的通用聲，咸陽片應避開。咸陽湖、029 區號、西咸新區、兩城合而未合，音樂上沒有任何既有作品可依；用「秦聲」（箏、板胡）和「長安聲」（笙、笛，借西安鼓樂的音色）兩個動機的對話來表現，是純設計【推論】。

## 鼓當脈搏、塤當記憶、箏當秦聲

跨越全片的城市聲音，證據最強的是鼓：秦有一號坑的鼓與鼓槌，漢有 128 名鼓員，唐有「樂工齊擊，聲震城闕」的太常大鼓（[《舊唐書·音樂志一》](https://zh.wikisource.org/wiki/舊唐書/卷28)）和羯鼓，清以後有秦腔武場和咸陽的牛拉鼓、蛟龍轉鼓，2021 年有千人鼓陣。每個時代在關中都找得到鼓【實證，但漢唐的紀錄在長安】，它也正合導演的要求。問題是「鼓」太通用，觀眾要認的是一個節奏，而不是一種鼓。建議定一個「**兩擊一組、間隔很長**」的心跳型，全片不改節奏、只換鼓【推論】：

| 段 | 心跳由誰打 | 證據等級 |
|---|---|---|
| M01 | 手拍陶罐 | 推論（關中仰韶無鼓的實物） |
| M02 | 戰鼓群齊奏，把心跳放大成號令 | 實證 |
| M03 | 失序後只剩一面悶鼓 | 推論 |
| M04 | 漢：建鼓單擊；唐：遠處羯鼓碎點 | 實證（長安） |
| M05 | 遠處更鼓，句尾的梆子 | 實證（梆子自明末清初起） |
| M06 | 火車軌縫與紗機節奏，高點交給鑼鼓陣 | 推論 |
| M07 | 梆子每小節一下，再交給鼓機 | 推論 |
| M08 | 紗機減速到停，鼓全撤 | 推論 |
| M09 | 柔和的木琴脈衝回來 | 推論 |
| M10 | 只剩遠處一擊，或完全沒有 | 推論 |
| M11 | 地鐵般的低頻脈衝，戰鼓層層回歸；736.0、737.65 兩擊收在熄燈 | 推論 |

塤的兩音是第二個貫穿元素，但只該出現三次：M01 開場、M03 留白之後（185.37）、M11 片尾字卡。理由是它是關中唯一有仰韶出土、測過音的旋律樂器，小三度是關中能測到的最古老音程【實證】；漢以後關中卻沒有塤的本地證據，唐代只在雅樂登歌裡列名（[《新唐書·禮樂志十一》](https://zh.wikisource.org/wiki/新唐書/卷021)），全片一直吹反而失真。首尾出現，意思是「城毀了，最古老的聲音還在」。箏則是秦以後的旋律身份：李斯把「彈箏」列為真秦之聲，唐人說「箏，本秦聲也」（[《舊唐書·音樂志二》](https://zh.wikisource.org/wiki/舊唐書/卷29)）【實證】；它也是 SA3 詞表裡最常見的中國樂器詞之一。從 M02 開始用，到 M09–M11 當「秦聲」，和代表西安的笙、笛對話。

現行 MUSIC.md 以**簫和古琴**當城市聲音，這份研究不支持。古琴不是唐代宮廷的主角（玄宗「酷不好琴」），〈渭城曲〉在唐代實際用管樂和琵琶伴奏，古琴《陽關三疊》是明代的傳承；簫在五份筆記裡都找不到咸陽的在地依據，又不在 AudioSparx 的樂器詞表裡，Freesound 也只有 5 筆，模型很可能認不出來【推論】。另外，片中若要說「這是秦國的鼓聲」，只能用「關中鑼鼓相傳」一類措辭，不能寫成史實。

## Stable Audio 3 Medium 只懂圖庫中國風，提示詞要遷就它

SA3 medium 的訓練資料是 AudioSparx 806,284 首加 Freesound 472,618 筆（[HF 模型卡](https://huggingface.co/stabilityai/stable-audio-3-medium)）。AudioSparx 的中國音樂總共約 2,144 首，放在百萬首的曲庫裡很小；「亞洲鼓與打擊」**只有 16 首**、「日本太鼓」30 首、「中國戲曲」7 首（[AudioSparx Chinese Music](https://www.audiosparx.com/sa/display/submain.cfm/soundGroup_iid.4771)；[AudioSparx Drum Music](https://www.audiosparx.com/sa/display/submain.cfm/soundGroup_iid.5082)）【實證，2026 年 10 月的頁面數字，訓練當時的快照不明】。中國風動作配樂的描述一再寫「guzheng, dizi, xiao, yangqin, strings, taiko drums and traditional chinese percussion」（[AudioSparx Chinese Action](https://www.audiosparx.com/sa/display/sounds.cfm/soundGroup_iid.1792)），所以模型心中的「中國戰鼓」多半是太鼓加好萊塢預告片鼓加中國鑼【推論】。這帶來三個後果：秦段若寫 traditional chinese percussion 或用 Chinese Action 類別，可能自動帶出秦代沒有的鑼鈸；Genre: Chinese 本身也可能帶出古箏、二胡，新石器段要特別聽；關中鑼鼓或秦腔板式那種特定鼓點，大概會被平均成通用的史詩鼓。期望值要放在「有中國色彩的大鼓」，選候選時用耳朵把關。

罕見樂器的名字要換成模型認得的詞，一段最多放一兩個罕見詞，讓 guzheng、erhu、taiko 這類常見詞撐骨架（[AudioSparx 樂器詞表](https://www.audiosparx.com/sa/display/displayby.cfm/target.instrument)；[Freesound](https://freesound.org/search/?q=erhu)）【詞表與筆數是實證，對照是推論，未實測】：

| 要的聲音 | 首選寫法 | 失敗時改用 | 為什麼 |
|---|---|---|---|
| 塤 | ocarina，加 small breathy clay | breathy low flute | 詞表無 Xun；Freesound 只有 6 筆、CC0 0 筆 |
| 戰鼓 | huge Chinese war drums；標籤 Taiko Drums、Big Toms | epic trailer drums、timpani | 太鼓在詞表，Dramatic Drums 類有數百首 |
| 編鐘、鎛 | bronze bells；標籤 Bells | chimes、bell toll | bianzhong 0 筆 |
| 石磬 | stone chimes | woodblock、low gong | lithophone 0 筆 |
| 梆子 | wooden clapper；標籤 Clapper | woodblock、temple blocks | bangzi 2 筆 |
| 笙 | sho | free reed mouth organ | sheng 4 筆 |
| 嗩吶 | shawm | piercing double reed | suona 4 筆 |
| 板胡、二弦 | erhu，加 bright nasal high register | fiddle | 詞表無 Banhu |
| 箏 | guzheng | Chinese zither | 中國風描述的核心詞 |
| 秦漢子、阮、月琴 | ruan | Chinese lute | 詞表有 Ruan |
| 排簫 | pan flute | bamboo flute | 詞表有 Pan Flute |

medium 是蒸餾過的權重，官方文件寫明 `cfg_scale` 和 `negative_prompt` 對 post-trained 權重沒有作用，固定 8 步（[inference.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/workflows/inference.md)；[論文 §4](https://arxiv.org/html/2605.17991v1)）【實證】。所以 MUSIC.md 那串負面提示詞和「不照提示詞走就調高 cfg」都是白費；有人在官方 repo 問怎麼排除某種彈法，至今沒有答案（[Issue #50](https://github.com/Stability-AI/stable-audio-3/issues/50)）。不要的東西只能「不寫」，再從候選裡挑。官方建議所有音樂提示詞都以 `TrackType: Music, VocalType: Instrumental,` 開頭，而且模型只用英文描述訓練（[論文 §5.1](https://arxiv.org/html/2605.17991v1)；[model-overview.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/model-overview.md)）。官方的提示詞助手只要輸出含 vocals、singing、male、female、voice、chorus、chant、lyrics 等字，就整句退回重寫（[reprompt.py](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/interface/reprompt.py)），可見這些字是人聲的開關【推論】，而 MUSIC.md 共用句裡的 "a narrator's voice" 正好命中。我的推論是連 "no erhu" 這種否定句也別寫，因為文字編碼器照樣收到 erhu 這個詞【推論，未實測】；也不要用 Buddhist Temple、Chinese Folk Opera、Tibetan 當類別，這些類別裡可能有誦經或戲曲人聲。

格式上，訓練時 AudioSparx 的提示詞一半帶欄位名、一半不帶，欄位隨機抽取、打亂，半數全轉小寫（[論文 §3.5](https://arxiv.org/html/2605.17991v1)），所以「標籤加一句散文」的混合寫法在分佈內；文字上限是 256 個 T5Gemma token，官方助手把擴寫限在 45 詞以內。速度要同時寫 BPM 數字和 AudioSparx 的分級詞（Very Slow 1–59、Slow 60–79、Medium Slow 80–104、Medium 105–129）（[AudioSparx](https://www.audiosparx.com/sa/links/dramatic-music-genres.cfm)）。調性不在 metadata 欄位裡，MUSIC.md 寫的 D 小調、F 大調大概不會被遵守，要對調就後製移調【推論】。Instruments 欄位不要超過 6 個，列太多時罕見樂器最先被吃掉。

換 seed 幾乎沒用：社群實測同一提示詞換三個 seed「essentially gives the same output」，打擊節奏「pretty much exact」，反而改一點措辭就會整首重排（[Reddit](https://reddit.sentinel-team.org/posts/1tjih4x/snapshots/2026-05-21T18%3A20%3A48.87163Z)；[Dubspot](https://blog.dubspot.com/stable-audio-3-review)）【實證，社群回報】。所以 MUSIC.md 的「每段出種子 1、2、3」要改成每段固定一個 seed，靠改措辭（形容詞、樂器順序、類別）出候選；`prompt` 可以傳 list，配 `batch_size=4` 一次比四種寫法（[inference.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/workflows/inference.md)）。反過來說，這個特性也是好事：鼓的措辭在 M02、M03、M11 一字不改，就有機會得到同一個節奏身份【推論】。

長度方面，預設是 120 秒；用 Python API 想超過 120 秒，必須傳 `sample_size=model.model_config["sample_size"]`，否則會被默默截斷，CLI 則會自動帶入（[model.py](https://github.com/Stability-AI/stable-audio-3/blob/main/stable_audio_3/model.py)）。很長的生成會偏向環境音樂或古典，很短的多半是 loop（[論文 §5.4](https://arxiv.org/html/2605.17991v1)），所以每次生成 60–120 秒最穩，太短的段落多生成一些再剪【推論】。SA3 的整曲結構偏弱（[Dubspot](https://blog.dubspot.com/stable-audio-3-review)），起承轉合要分段做：先生成主體，再用 continuation（遮罩起點設在原長度、duration 拉長）接出高潮，最後用 inpainting 改寫結尾；官方提醒 "The audio context matters more than the prompt"（[prompting.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md)）。跨段要一致，可以把前一段滿意的片段當 init_audio，`init_noise_level` 設 0.5–0.7，保留音色、換掉節奏；轉場則把 A 段最後 10–20 秒接上 B 段開頭，只 inpaint 中間 4–8 秒【推論，未實測】。

最後，模型不會在指定的秒數重擊或停住。177.07 的火起重擊、181.37 的硬切、185.37 的回來、732–736 的留白、737.65 的熄燈，都要在剪輯時處理：剪斷、淡出，或另外生成一小段「心跳鼓」和「塤兩音」的獨立音軌，放到時間線上的精確位置。火聲、汽笛、地鐵這些音效也不要寫進配樂提示詞，照 MUSIC.md 的分工另外做。

## 結論

這份研究把 MUSIC.md 的樂器階層倒過來了：城市的聲音不該是一件旋律樂器（簫、古琴），而是一個**節奏**。這樣做剛好同時躲開了史料與模型兩邊的弱點：史料上，從秦到今天只有鼓在每個時代都留下紀錄，旋律樂器則一路斷層；模型上，SA3 最認不得的正是罕見的中國旋律樂器，大鼓卻在訓練資料裡很多，而它「換 seed 不變」的脾氣，反而讓固定措辭能生出穩定的鼓。塤只在首尾與焚城後出現，箏只從秦開始，兩者的稀少本身就是敘事：最古老的聲音只在城生與城毀時響起。

證據的分布也在替旁白說話：帝都最盛時史料最響（鐘鎛、石磬、戰鼓），城毀那一夜史料一聲不吭，等咸陽降為縣城，它自己的聲音（涇三高的秦腔、乾縣禮泉的弦板腔）反而第一次能被點名。配樂可以照這個疏密走，有實證的地方滿，靠推論的地方空。實際動工前最該先做的，是用 `TrackType: Instrument` 每個罕見詞跑 3 個 seed、30 秒的小批量試聽（ocarina、bronze bells、stone chimes、wooden clapper、sho），確認模型認得哪些詞，再生成 11 段；若中國鼓始終被平均成預告片鼓，官方 repo 提供 LoRA 微調（[lora.md](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/workflows/lora.md)），可以拿關中鑼鼓錄音訓練，但所需資料量與效果都還沒評估。

## 11 段配樂設計表

時間取自 `build/export/timeline.json`（全片 749.65 秒，8.0 秒亮燈）。

| 段（時間・情緒） | 主奏 | 輔助 | 節奏／速度 | 音色 | 要避開的時代錯置 |
|---|---|---|---|---|---|
| **M01** 開場與新石器 0–38.7（wonder） | 小陶塤（ocarina 代），吹半坡式兩音小三度 | 手拍陶罐的心跳、踏地、擊石；極低的持續音可有可無（現代慣例） | 自由無拍，約 56 BPM 的心跳感；長留白 | 高、氣聲、空心、乾、近 | 任何金屬（鐘、鑼、鈸）、任何弦樂、完整五聲旋律與和弦、管弦樂鋪底；不能把現代九孔低音塤的暖厚音色當原聲 |
| **M02** 秦都→帝都 38.7–168.9（pride，全片第一高峰；92.05 入帝國，92.55 起漲到最高） | 戰鼓群：重木槌、厚皮、齊奏重音 | 前段：缶（陶罐悶擊）、拍腿、低音箏撥奏；92.55 後：青銅鎛與編鐘落在每小節第一拍、石磬亮點；收尾一記鉦斷鼓 | 4/4 進行，約 80 BPM，前疏後密 | 低頻厚皮、乾木槌、青銅長尾音、石磬短脆、陶土悶響 | 鑼、鈸、嗩吶、二胡、琵琶、橫笛、西洋銅管（含 MUSIC.md 的 horns 與 low brass）、太鼓典型節奏型、安塞腰鼓花點 |
| **M03** 焚城 168.9–191.9（grief；177.07 火起；181.37–185.37 留白） | 同一批戰鼓失序：稀疏不規則（楚式「疏緩節」），最後剩一面悶鼓心跳 | 177.07 一記最重的擊；走音墜落的青銅鐘、斷弦的箏；185.37 後一支陶塤吹 M01 的兩音 | 約 50 BPM，rubato，鼓擊之間長空白；181.37 硬切 | 悶、遠、空殿殘響、裂銅 | 英雄進行曲、大調勝利收尾、二胡（MUSIC.md 現用）、嗩吶、鈸；「四面楚歌」意象（前 202 年垓下事）；旁白不說燒阿房宮 |
| **M04** 漢→唐 191.9–293.3（wistful；漢 191.87–254.6，唐 254.6–293.25） | 漢：建鼓低頻單擊加排簫；唐：高音竹笛「慢拽」式拖長 | 漢：笳、箏或瑟的長餘音、偶爾一聲石磬；唐：曲項琵琶木撥、笙持續音、遠處羯鼓碎點、句尾稀疏拍板 | 漢約 50–56 BPM、鼓點稀疏；唐散板開頭再進 60–66 BPM，7 個樂句（第一句不疊）；結尾漸慢、不解決 | 漢：黃土的乾燥空間、氣聲、鼻音簧；唐：晨雨濕潤、木撥清脆 | 漢段：曲項琵琶、五弦、羯鼓、篳篥、方響、拍板、銅鈸、豎箜篌；兩段：二胡、嗩吶、揚琴、三弦、秦腔板式；古琴當主奏；把《陽關三疊》琴歌當唐音 |
| **M05** 明清縣城 293.3–344.2（calm：城門、文廟、鐘樓、咸陽古渡） | 竹笛（寺觀吹管）的長音旋律 | 阮撥奏（代三弦、月琴）、梆子只在句尾、笙持續音、鐘樓一記低鐘、遠處更鼓（獨立音軌） | 散板開場，再進慢板約 56 BPM | 木質、乾、清、遠、竹管氣聲、銅器餘韻 | 現代二胡的濃厚音色與揚琴主奏、銅管與馬號、「大秦戰鼓」式鼓陣、安塞腰鼓、信天游、山西威風鑼鼓、合成器 pad、編鐘大合奏 |
| **M06** 1936 鐵路→1949→1950 年代紡織城 344.2–404.3（hope→pride；mills 379.02 起） | 板胡（erhu 代）在高音區明亮領奏，歡音 | 梆子推二六板、火車軌縫般的節奏、手風琴和弦；mills 段加大鼓、大鑼、鐃鈸的關中鑼鼓陣 | 2/4，約 104–112 BPM，漸緊 | 亮、脆、尖、木頭爆點、銅器光 | 1958 年以後的歌、電聲樂器、搖滾鼓組、安塞腰鼓萬人方陣、把信天游或陝北秧歌當咸陽主聲、交響化的秦腔大樂隊 |
| **M07** 1975–1991 404.3–492.6（calm→pride→hope；彩管廠 417.85、設市 441.05、機場 466.45） | 1975 段板胡或笛在中低音獨奏；1983 起板胡在高音區「喊」出秦聲動機 | 錄音機帶噪、做舊合成器琶音、梆子每小節一下再交給鼓機；1983 段架子鼓強拍、突出的電貝斯；1991 段半速、長音 pad | 約 96 BPM，1991 段半速感 | 1980 年代類比合成器、卡帶頻寬、暖 | 2000 年以後的製作（trap 踩鑔、EDM drop）、引用西北風或鄧麗君的旋律、把信天游或安塞腰鼓當咸陽聲音、絲路 New Age 套路 |
| **M08** 1998 紡織城的轉折 492.6–529.4（grief） | 手風琴，或略走音的立式鋼琴 | 紗機節奏由慢到停；低音板胡（erhu 代）拉秦聲動機的慢速小調版；最後只留空間殘響和一聲梆子 | 約 64 BPM，鼓全撤 | 空廠房殘響、木頭、略走音 | 〈從頭再來〉式副歌上揚的打氣搖滾、任何鼓組與重擊 |
| **M09** 2005–2011 咸陽湖、029、西咸新區 529.4–606.1（hope） | 笙（sho 代）加竹笛＝長安聲；箏撥奏＝秦聲，兩邊對話 | 柔和的木琴脈衝帶回心跳；輕的電子脈衝 | 約 92 BPM | 溫、透、輕、漸亮 | 企業宣傳片式的硬鼓點、EDM、太鼓 |
| **M10** 2014 西咸新區交西安代管 606.1–641.6（wistful，強） | 板胡（erhu 代）獨奏呼喚，竹笛遠遠回應，始終不同時 | 低音笙持續音（同一片土地）；鼓只剩遠處一擊，或完全沒有 | 約 60 BPM，長停頓，樂句停在懸置處 | 孤、空、遠 | 兩個動機齊奏、解決到主和弦、任何節奏組 |
| **M11** 2019–2026 641.6–749.65（hope 推到收尾；728.30「這座城，還在生長」；732–736 留白；737.65 熄燈；739.15 起片尾字卡） | 戰鼓群回歸（與 M02 同一措辭），從少到多層層疊上 | 地鐵般的低頻脈衝；箏與竹笛第一次同度或八度齊奏；736.0、737.65 兩擊心跳；片尾字卡回到陶塤兩音 | 約 80 BPM（與 M02 相同），半速感加電子脈衝 | 厚、亮、暖，最後只剩一面鼓和一支塤 | 完滿的終止式（「還在生長」要開放收尾）、安塞腰鼓當主角、威風鑼鼓、duduk 加新世紀弦樂 |

### 提示詞草稿

以下 12 段（M04 另附唐段續接版）都已機械檢查：以規定前綴開頭、58–68 個英文詞、Instruments 不超過 6 個、不含 vocal、voice、male、female、chorus、choir、chant、lyrics、opera 等字，也不含 "no" 否定句。鼓的措辭 "huge Chinese war drums struck with heavy wooden mallets" 在 M02、M03、M11 一字不改，心跳措辭 "slow two-stroke heartbeat" 在 M01、M03 相同。全部**未經生成驗證**。

M01 開場與新石器
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Ethereal, Instruments: Ocarina, Indigenous Drums, Moods: Mystical, Earthy, Sparse, Tempo: Very Slow, BPM: 56, documentary underscore, hall reverb. Dawn over a Neolithic river village: a small breathy clay ocarina repeats a two-note minor-third call, soft hands on a clay pot keep a slow two-stroke heartbeat, long silences, full of wonder.
```

M02 秦都→帝都（另用同一句的 Subgenre: Chinese Action 版本放進同一個 batch 對照）
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Regal Chinese, Instruments: Taiko Drums, Big Toms, Bells, Guzheng, Moods: Majestic, Stately, Marching, Tempo: Medium Slow, BPM: 80, documentary underscore, hall reverb. Huge Chinese war drums struck with heavy wooden mallets play disciplined unison accents over clay pot thuds and a plucked guzheng ostinato, then bronze bells ring on each downbeat with bright stone chimes, building to a proud imperial climax.
```

M03 焚城
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Taiko Drums, Bells, Guzheng, Ocarina, Moods: Mournful, Sparse, Tempo: Very Slow, BPM: 50, documentary underscore, hall reverb. Huge Chinese war drums struck with heavy wooden mallets lose their order in sparse irregular strokes, one crushing blow, a cracked bronze bell, a snapped guzheng string, then a slow two-stroke heartbeat on a low drum and a lone clay ocarina.
```

M04 漢→唐（只用漢唐兩代都合理的樂器，可一次生成整段）
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Bamboo Flute, Pan Flute, Guzheng, Ruan, Bass Drum, Moods: Nostalgic, Solemn, Reflective, Tempo: Slow, BPM: 60, documentary underscore, hall reverb. Single deep strokes on a large barrel drum with long gaps, breathy pan flute and sparse plucked guzheng in dry plateau air, then a high bamboo flute leads a slow farewell melody, ruan plucks answering, fading unresolved.
```

M04b 唐段續接版（254.6 秒起用 continuation 接，才加入曲項琵琶和羯鼓）
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Bamboo Flute, Pipa, Guzheng, Sho, Moods: Nostalgic, Reflective, Sparse, Tempo: Slow, BPM: 60, documentary underscore, hall reverb. Farewell at a misty river ferry at dawn: a high bamboo flute leads a slow drawn-out melody, pipa plucked with a wooden plectrum, a soft sho drone, a faint fast two-stick drum flutter far away, slowing down and fading unresolved.
```

M05 明清縣城
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Folk Ensembles, Instruments: Bamboo Flute, Ruan, Clapper, Sho, Bells, Moods: Meditative, Nostalgic, Earthy, Tempo: Very Slow, BPM: 56, documentary underscore, hall reverb. A quiet walled county town at dusk: a soft bamboo flute in free time settles into a slow pulse, gentle ruan plucks, dry wooden clapper ticks only at phrase ends, a warm sho drone, one low temple bell.
```

M06 鐵路、解放、紡織城
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Happy, Instruments: Erhu, Clapper, Accordion, Chinese Gongs, Cymbals, Bass Drum, Moods: Hopeful, Rousing, Driving, Tempo: Medium, BPM: 108, documentary underscore, hall reverb. A bright nasal erhu in its high register leads a hopeful tune over a steady train-wheel rhythm of wooden clappers, accordion chords underneath, then a big drum, gongs and cymbals join in a proud festive march.
```

M07 1975–1991
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Pop Instr., Instruments: Synthesizer, Drum Machine, Electric Bass, Erhu, Moods: Nostalgic, Rousing, Hopeful, Tempo: Medium Slow, BPM: 96, documentary underscore, hall reverb. Opens calm with warm 1980s analog synth arpeggios and faint tape hiss, a wooden clapper tick on each bar, then a punchy drum machine and bold electric bass lift a bright erhu melody proudly, ending in airy pads.
```

M08 1998
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Accordion, Piano, Erhu, Moods: Melancholic, Nostalgic, Somber, Tempo: Slow, BPM: 64, documentary underscore, hall reverb. Elegy for a closed textile mill: a soft mechanical loom rhythm slows and stops, a lonely accordion and a slightly detuned upright piano carry a slow minor melody, a low erhu answers, long empty factory hall reverb.
```

M09 2005–2011
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese New Age, Instruments: Sho, Bamboo Flute, Guzheng, Marimba, Moods: Hopeful, Reflective, Uplifting, Tempo: Medium Slow, BPM: 92, documentary underscore, hall reverb. Two neighbouring cities begin a dialogue: a warm sho chord and an airy bamboo flute answer a gently plucked guzheng phrase, a soft marimba pulse returns like a heartbeat, light and patient, slowly growing brighter.
```

M10 2014
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Sad, Instruments: Erhu, Bamboo Flute, Sho, Moods: Melancholic, Nostalgic, Sparse, Tempo: Slow, BPM: 60, documentary underscore, hall reverb. A solo erhu calls and a distant bamboo flute replies, taking turns but never meeting in unison, over a low sustained sho drone, long pauses, each phrase left hanging unresolved, deeply wistful and restrained.
```

M11 2019–2026
```
TrackType: Music, VocalType: Instrumental, Genre: Chinese, Subgenre: Chinese Action, Instruments: Taiko Drums, Guzheng, Bamboo Flute, Synthesizer, Strings, Moods: Hopeful, Uplifting, Building, Climactic, Tempo: Medium Slow, BPM: 80, documentary underscore, hall reverb. A deep pulsing synth bass like a metro, then huge Chinese war drums struck with heavy wooden mallets return layer by layer, guzheng and bamboo flute finally play one melody in octaves, building to an uplifting peak.
```

### 生成長度與剪輯點

| 段 | 生成長度 | 做法 |
|---|---|---|
| M01 | 50 秒 | 一次生成；0–8 秒還沒亮燈，從無聲淡入 |
| M02 | 先 65 秒，再 continuation 到 140 秒 | 第二次用同一句提示詞接續，起漲對 92.55；超過 120 秒用 CLI，或在 Python API 傳 `sample_size` |
| M03 | 40 秒，或接在 M02 尾巴用 continuation | 177.07 對齊最重的一擊；181.37 硬切；185.37 疊上「塤兩音」與悶鼓的獨立音軌 |
| M04 | 先 70 秒，再以 M04b continuation 到 110 秒 | 接點對 254.6（漢轉唐） |
| M05 | 60 秒 | 一次生成；更鼓用獨立心跳音軌 |
| M06 | 70 秒 | 鑼鼓陣若沒在 379.02 前後出現，用 continuation 改寫後半 |
| M07 | 先 50 秒，再 continuation 到 100 秒 | 441.05 起換強拍，466.45 起半速 |
| M08 | 45 秒 | 紗機「慢到停」若模型做不出來，在剪輯時減速與淡出 |
| M09 | 85 秒 | 一次生成 |
| M10 | 45 秒 | 一次生成 |
| M11 | 120 秒，另加約 15 秒片尾音軌 | 用 M02 的鼓段當 init_audio（0.5–0.7）帶回同一批鼓；732.0 硬切；736.0、737.65 兩擊心跳與片尾字卡的塤用獨立音軌 |

獨立音軌各生成一次、全片重複使用，才能保證「同一個心跳、同一個兩音」（未實測）：

```
TrackType: Instrument, Instruments: Bass Drum, a slow two-stroke heartbeat on a low drum with long gaps, dry and close, Tempo: Very Slow, BPM: 56
```

```
TrackType: Instrument, Instruments: Ocarina, a small breathy clay ocarina plays a two-note minor-third call with long silences, intimate and dry, Tempo: Very Slow, BPM: 56
```

// The entry page's words in its five languages (English, Japanese, Traditional and Simplified Chinese, Spanish). A city's own
// words (its name and summary) come from cities.json; a language missing there falls back to English.
export const LANGS = [['en', 'English'], ['ja', '日本語'], ['zh-Hant', '繁體中文'], ['zh-Hans', '简体中文'], ['es', 'Español']];

// the browser's languages -> one of ours
export function pick(list) {
  for (const l of list || []) {
    const s = l.toLowerCase();
    if (s.startsWith('zh')) return /hant|tw|hk|mo/.test(s) ? 'zh-Hant' : 'zh-Hans';
    for (const [k] of LANGS) if (s.split('-')[0] === k) return k;
  }
  return 'en';
}

const T = {
  en: {
    subtitle: 'A City Through Time',
    lede: 'Each film builds one city as a white model and lights it era by era, from its first settlers to today.',
    hint: 'Drag the globe. Choose a lit city.',
    citiesTitle: 'Cities on the plinth',
    citiesNote: 'Each bar is a film: its chapters in the colours they have on screen.',
    emptyTitle: 'Your city',
    emptyText: 'This plinth is empty. Make the film of a city you know and add it here.',
    emptyLink: 'How to make one',
    years: 'Years', length: 'Length', narration: 'Narration', subtitles: 'Subtitles', by: 'Made by',
    watch: 'Watch', watchOn: 'Watch on {site}', play: 'Play in your browser', playNote: 'Loads about {mb} MB, best on a computer.',
    download: 'Download the film', source: 'Sources and credits',
    pending: 'The film is being published. Its sources are already open.',
    ai: 'Made with AI: {list}. Every historical claim is sourced in FACTS.md.',
    aiNarration: 'the narration', aiMusic: 'the music', aiImagined: 'the imagined scenes (labelled on screen)',
    close: 'Close', chapters: "The film's chapters",
    makeTitle: "Make your city's film",
    makeLede: 'A coding agent does the research, the model and the render; you direct it and check every step.',
    step1: 'Make it', step1Text: 'Install Claude Code and this project as a skill, then name a city and the era to start from. It finds the sources, builds the model and renders the film while you review it in the browser.',
    step2: 'Publish it', step2Text: 'Put the film on YouTube, Bilibili or any video site. To let people play it here too, publish its web bundle on a Hugging Face dataset or your own GitHub Pages.',
    step3: 'Add it here', step3Text: "Open a pull request with your city's folder and its entry in cities.json. We check the sources, the licences and the film.",
    makingGuide: 'Making guide', submitGuide: 'Submitting guide',
    footLicence: 'Code under the MIT licence. Films and city material under CC BY-SA 4.0; material by others keeps its own licence (each city lists it in CREDITS).',
    footEarth: 'The earth is drawn from Natural Earth.', footSource: 'Source on GitHub',
    noGL: 'This browser cannot draw the globe; the cities are listed below.',
  },
  ja: {
    subtitle: '街の時をたどる',
    lede: '一本の映画で一つの街を白い模型に組み上げ、最初の集落から今日まで、時代ごとに光を当てていく。',
    hint: '地球儀はドラッグで回せます。光っている街を選んでください。',
    citiesTitle: '展示台の街',
    citiesNote: '一本の帯が一本の映画です。各章を、画面に出る色で並べています。',
    emptyTitle: 'あなたの街',
    emptyText: 'この展示台はまだ空いています。よく知っている街の映画をつくって、ここに加えてください。',
    emptyLink: 'つくり方',
    years: '年代', length: '長さ', narration: 'ナレーション', subtitles: '字幕', by: '制作',
    watch: '観る', watchOn: '{site}で観る', play: 'ブラウザで再生', playNote: '約 {mb} MB を読み込みます。パソコン向けです。',
    download: '映画をダウンロード', source: '資料とクレジット',
    pending: '映画は公開準備中です。資料はすでに公開しています。',
    ai: 'AI で生成したもの：{list}。史実にはすべて FACTS.md に出典があります。',
    aiNarration: 'ナレーション', aiMusic: '音楽', aiImagined: '想像図（画面に明記）',
    close: '閉じる', chapters: '映画の章',
    makeTitle: 'あなたの街の映画をつくる',
    makeLede: '調査も模型も書き出しもコーディングエージェントが行い、あなたは方向を決めて一つずつ確かめます。',
    step1: 'つくる', step1Text: 'Claude Code とこのプロジェクトをスキルとして入れ、街の名前と始まりの時代を伝えます。出典を調べ、模型を組み、映画を書き出します。途中の各段階はブラウザで確かめられます。',
    step2: '公開する', step2Text: '映画を YouTube や Bilibili などに載せます。ここでも再生できるようにするには、ウェブ用パッケージを Hugging Face のデータセットか自分の GitHub Pages で公開します。',
    step3: 'ここに加える', step3Text: '街のフォルダと cities.json の項目を入れたプルリクエストを送ってください。出典、ライセンス、映画を確認します。',
    makingGuide: 'つくり方ガイド', submitGuide: '投稿ガイド',
    footLicence: 'コードは MIT ライセンス。映画と街の資料は CC BY-SA 4.0。他者の素材はそれぞれのライセンスに従います（各街の CREDITS に記載）。',
    footEarth: '地球は Natural Earth をもとに描いています。', footSource: 'GitHub のソース',
    noGL: 'このブラウザでは地球儀を描けません。街は下に並んでいます。',
  },
  'zh-Hant': {
    subtitle: 'A City Through Time',
    lede: '每部影片把一座城做成白色模型，從最早的聚落到今天，一個時代一個時代地點亮。',
    hint: '拖動地球儀，選一座亮著的城。',
    citiesTitle: '展台上的城市',
    citiesNote: '一條色帶就是一部影片：各章依序排開，顏色和畫面上一樣。',
    emptyTitle: '你的城市',
    emptyText: '這個展台還空著。為你熟悉的城市做一部片，放到這裡。',
    emptyLink: '怎麼做',
    years: '年代', length: '片長', narration: '旁白', subtitles: '字幕', by: '作者',
    watch: '觀看', watchOn: '在 {site} 觀看', play: '在瀏覽器裡播放', playNote: '約需載入 {mb} MB，建議用電腦觀看。',
    download: '下載影片', source: '資料與出處',
    pending: '影片正在上架。這座城的資料已經公開。',
    ai: '用 AI 生成的部分：{list}。每一條史實都在 FACTS.md 列出出處。',
    aiNarration: '旁白', aiMusic: '配樂', aiImagined: '想像圖（畫面上已標註）',
    close: '關閉', chapters: '影片的章節',
    makeTitle: '為你的城市做一部片',
    makeLede: '查資料、搭模型、渲染都由程式代理完成；你負責決定方向、檢查每一步。',
    step1: '製作', step1Text: '安裝 Claude Code，把這個專案裝成技能，告訴它城市和起始年代。它會查史料、搭模型、渲染影片，每一步都可以在瀏覽器裡預覽。',
    step2: '發布', step2Text: '把影片放到 YouTube、B 站或其他影片網站。想讓大家在這裡直接播放，再把網頁播放包放到 Hugging Face 資料集或你自己的 GitHub Pages。',
    step3: '加到這裡', step3Text: '開一個 pull request，放進城市資料夾和 cities.json 裡的一筆資料。我們會核對出處、授權和影片。',
    makingGuide: '製作教學', submitGuide: '提交教學',
    footLicence: '程式碼採 MIT 授權。影片與城市資料採 CC BY-SA 4.0；他人的素材依各自授權（每座城的 CREDITS 有列）。',
    footEarth: '地球依 Natural Earth 資料繪製。', footSource: 'GitHub 原始碼',
    noGL: '這個瀏覽器畫不出地球儀；城市列在下面。',
  },
  'zh-Hans': {
    subtitle: 'A City Through Time',
    lede: '每部影片把一座城做成白色模型，从最早的聚落到今天，一个时代一个时代地点亮。',
    hint: '拖动地球仪，选一座亮着的城。',
    citiesTitle: '展台上的城市',
    citiesNote: '一条色带就是一部影片：各章依次排开，颜色和画面上一样。',
    emptyTitle: '你的城市',
    emptyText: '这个展台还空着。为你熟悉的城市做一部片，放到这里。',
    emptyLink: '怎么做',
    years: '年代', length: '片长', narration: '旁白', subtitles: '字幕', by: '作者',
    watch: '观看', watchOn: '在 {site} 观看', play: '在浏览器里播放', playNote: '约需加载 {mb} MB，建议用电脑观看。',
    download: '下载影片', source: '资料与出处',
    pending: '影片正在上架。这座城的资料已经公开。',
    ai: '用 AI 生成的部分：{list}。每一条史实都在 FACTS.md 列出出处。',
    aiNarration: '旁白', aiMusic: '配乐', aiImagined: '想象图（画面上已标注）',
    close: '关闭', chapters: '影片的章节',
    makeTitle: '为你的城市做一部片',
    makeLede: '查资料、搭模型、渲染都由编程代理完成；你负责定方向、检查每一步。',
    step1: '制作', step1Text: '安装 Claude Code，把这个项目装成技能，告诉它城市和起始年代。它会查史料、搭模型、渲染影片，每一步都可以在浏览器里预览。',
    step2: '发布', step2Text: '把影片放到 YouTube、B 站或其他视频网站。想让大家在这里直接播放，再把网页播放包放到 Hugging Face 数据集或你自己的 GitHub Pages。',
    step3: '加到这里', step3Text: '提交一个 pull request，放进城市文件夹和 cities.json 里的一条记录。我们会核对出处、授权和影片。',
    makingGuide: '制作教程', submitGuide: '提交教程',
    footLicence: '代码采用 MIT 许可。影片与城市资料采用 CC BY-SA 4.0；他人的素材依各自许可（每座城的 CREDITS 有列）。',
    footEarth: '地球依 Natural Earth 数据绘制。', footSource: 'GitHub 源代码',
    noGL: '这个浏览器画不出地球仪；城市列在下面。',
  },
  es: {
    subtitle: 'Una ciudad a través del tiempo',
    lede: 'Cada película construye una ciudad como maqueta blanca y la ilumina época por época, desde sus primeros pobladores hasta hoy.',
    hint: 'Arrastra el globo. Elige una ciudad iluminada.',
    citiesTitle: 'Ciudades en la maqueta',
    citiesNote: 'Cada barra es una película: sus capítulos, con los colores que tienen en pantalla.',
    emptyTitle: 'Tu ciudad',
    emptyText: 'Este pedestal está vacío. Haz la película de una ciudad que conozcas y súmala aquí.',
    emptyLink: 'Cómo hacerla',
    years: 'Años', length: 'Duración', narration: 'Narración', subtitles: 'Subtítulos', by: 'Autoría',
    watch: 'Ver', watchOn: 'Ver en {site}', play: 'Reproducir en el navegador', playNote: 'Descarga unos {mb} MB; mejor en un ordenador.',
    download: 'Descargar la película', source: 'Fuentes y créditos',
    pending: 'La película se está publicando. Sus fuentes ya son públicas.',
    ai: 'Hecho con IA: {list}. Cada dato histórico tiene su fuente en FACTS.md.',
    aiNarration: 'la narración', aiMusic: 'la música', aiImagined: 'las escenas imaginadas (señaladas en pantalla)',
    close: 'Cerrar', chapters: 'Capítulos de la película',
    makeTitle: 'Haz la película de tu ciudad',
    makeLede: 'Un agente de programación investiga, construye la maqueta y renderiza; tú lo diriges y revisas cada paso.',
    step1: 'Hazla', step1Text: 'Instala Claude Code y este proyecto como skill, y dile una ciudad y la época por la que empezar. Busca las fuentes, construye la maqueta y renderiza la película mientras la revisas en el navegador.',
    step2: 'Publícala', step2Text: 'Sube la película a YouTube, Bilibili o cualquier sitio de vídeo. Para que también se pueda reproducir aquí, publica su paquete web en un dataset de Hugging Face o en tu propio GitHub Pages.',
    step3: 'Súmala aquí', step3Text: 'Abre un pull request con la carpeta de tu ciudad y su entrada en cities.json. Revisamos las fuentes, las licencias y la película.',
    makingGuide: 'Guía para hacerla', submitGuide: 'Guía para enviarla',
    footLicence: 'Código bajo licencia MIT. Películas y material de las ciudades bajo CC BY-SA 4.0; el material de terceros mantiene su licencia (cada ciudad lo detalla en CREDITS).',
    footEarth: 'La Tierra se dibuja con datos de Natural Earth.', footSource: 'Código en GitHub',
    noGL: 'Este navegador no puede dibujar el globo; las ciudades están abajo.',
  },
};

// a film's languages, named in the page's language
const LANG_NAMES = {
  zh: { en: 'Chinese', ja: '中国語', 'zh-Hant': '中文', 'zh-Hans': '中文', es: 'chino' },
  en: { en: 'English', ja: '英語', 'zh-Hant': '英文', 'zh-Hans': '英文', es: 'inglés' },
  ja: { en: 'Japanese', ja: '日本語', 'zh-Hant': '日文', 'zh-Hans': '日文', es: 'japonés' },
  es: { en: 'Spanish', ja: 'スペイン語', 'zh-Hant': '西班牙文', 'zh-Hans': '西班牙文', es: 'español' },
  ko: { en: 'Korean', ja: '韓国語', 'zh-Hant': '韓文', 'zh-Hans': '韩文', es: 'coreano' },
  fr: { en: 'French', ja: 'フランス語', 'zh-Hant': '法文', 'zh-Hans': '法文', es: 'francés' },
};

// the guides on GitHub, by language (a language without its own falls back along the list)
export const GUIDES = {
  making: { 'zh-Hant': 'docs/MAKING.zh-Hant.md' },
  submit: { 'zh-Hant': 'CONTRIBUTING.zh-Hant.md' },
};

export function words(lang) {
  const t = T[lang] || T.en;
  const fmt = (k, v = {}) => (t[k] ?? T.en[k]).replace(/\{(\w+)\}/g, (_, x) => v[x] ?? '');
  const join = list => list.join(lang.startsWith('zh') || lang === 'ja' ? '、' : ', ');
  const year = n => {
    if (lang === 'en') return n < 0 ? `${-n} BCE` : `${n}`;
    if (lang === 'es') return n < 0 ? `${-n} a. C.` : `${n}`;
    if (lang === 'ja') return n < 0 ? `紀元前${-n}年` : `${n}年`;
    return n < 0 ? `前${-n}年` : `${n}年`;
  };
  const span = ([a, b]) => `${year(a)} – ${year(b)}`;
  const length = s => {
    const m = Math.floor(s / 60), r = Math.round(s % 60);
    return lang === 'ja' || lang.startsWith('zh') ? `${m}分${r}秒` : `${m} min ${r} s`;
  };
  const langName = c => (LANG_NAMES[c] || {})[lang] || c;
  const guide = kind => { const g = GUIDES[kind]; return g[lang] || g.en || g['zh-Hant']; };
  const of = obj => (obj && (obj[lang] || obj.en || Object.values(obj)[0])) || '';
  return { t: k => fmt(k), fmt, join, year, span, length, langName, guide, of };
}

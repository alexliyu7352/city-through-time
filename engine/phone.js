// The player (?play) and the walk-round (?view&free) on a touch screen. The film is made for a wide screen: on a phone it is
// watched in full screen and held sideways, or nothing on it can be read. Nothing here runs where the main pointer is a mouse.
// A page that goes full screen (Android's Chrome, a tablet's Safari; never an iPhone's Safari, which has no full screen for a page)
// does so on a tap (the gesture a browser asks for before it goes full screen or plays sound), and a phone's picture then turns
// sideways where the browser allows (screen.orientation.lock: Android's Chrome, in full screen only). Where it did not turn, a
// cover asks a phone held upright to turn sideways and says a computer shows it best, with a way to stay upright.
// phone({ words, start, onUpright }) -> null on a desktop, else { fullscreen, full(on), isFull(), start(label, go) }
//   start: the page waits for a tap on its start button (the player: its sound needs the tap too), so before it the cover stays
//   away where that tap can turn the picture itself; onUpright: told when the cover comes (the player pauses)
export const touch = matchMedia('(pointer: coarse)').matches;

const CSS = `.ph-start,.ph-turn{position:fixed;inset:0;display:grid;place-items:center;padding:24px max(24px,env(safe-area-inset-right)) 24px max(24px,env(safe-area-inset-left));
  color:oklch(0.955 0.006 85);font:15px/1.5 system-ui,-apple-system,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif;text-align:center;-webkit-tap-highlight-color:transparent}
  .ph-start{z-index:8;background:oklch(0.13 0.01 255 / .45)}.ph-turn{z-index:12;background:#050607}.ph-start[hidden],.ph-turn[hidden]{display:none}
  .ph-go{display:inline-flex;align-items:center;gap:12px;min-height:56px;padding:0 26px 0 20px;border:0;border-radius:999px;background:oklch(0.865 0.115 80);
    color:oklch(0.22 0.035 75);font-family:inherit;font-size:17px;font-weight:600;line-height:1;cursor:pointer;touch-action:manipulation}
  .ph-go svg{width:22px;height:22px;flex:none}.ph-go:focus-visible,.ph-stay:focus-visible{outline:2px solid oklch(0.955 0.006 85);outline-offset:3px}
  .ph-note{margin:14px 0 0;color:oklch(0.955 0.006 85 / .7);font-size:13px}
  .ph-turn .ph-in{max-width:340px}.ph-turn svg.ph-icon{width:64px;height:64px;color:oklch(0.865 0.115 80)}
  .ph-turn h2{margin:14px 0 8px;font:600 20px/1.35 "Noto Serif TC","Songti TC","Noto Serif SC",Georgia,serif;letter-spacing:.04em}
  .ph-turn p{margin:0 0 8px;color:oklch(0.955 0.006 85 / .75)}
  .ph-acts{display:flex;flex-direction:column;align-items:center;gap:10px;margin-top:18px}
  .ph-stay{min-height:44px;padding:0 18px;border:1px solid oklch(0.955 0.006 85 / .3);border-radius:999px;background:none;color:inherit;font:inherit;cursor:pointer;touch-action:manipulation}
  @media (prefers-reduced-motion:no-preference){.ph-turn svg.ph-icon{animation:ph-turn 2.4s cubic-bezier(.65,0,.35,1) infinite}}
  @keyframes ph-turn{0%,25%{transform:rotate(0)}55%,100%{transform:rotate(-90deg)}}`;
const PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 4.5v15l13-7.5z"/></svg>';
export const FULL = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>';
const TURN = '<svg class="ph-icon" viewBox="0 0 64 64" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="3"><rect x="20" y="6" width="24" height="52" rx="5"/><path d="M29 51h6"/></svg>';

export function phone({ words: Wd, start = false, onUpright = () => {} }) {
  if (!touch) return null;
  document.head.appendChild(Object.assign(document.createElement('style'), { textContent: CSS }));
  const el = document.documentElement, req = el.requestFullscreen || el.webkitRequestFullscreen, exit = document.exitFullscreen || document.webkitExitFullscreen;
  const isFull = () => !!(document.fullscreenElement || document.webkitFullscreenElement);
  const fullscreen = !!req;
  async function full(on) {
    try {
      if (!on) { if (isFull()) await exit.call(document); return; }
      if (!isFull()) await req.call(el);
      if (screen.orientation && screen.orientation.lock) await screen.orientation.lock('landscape');   // (refused outside Android's Chrome: the cover asks instead)
    } catch { /* not allowed here: the cover asks to turn the phone */ }
    show();
  }
  // a phone held upright: its short side across (a tablet upright still shows the whole picture)
  const upright = matchMedia('(orientation: portrait) and (max-width: 600px)');
  let started = !start, stayed = false, was = false;
  const cover = document.createElement('div'); cover.className = 'ph-turn'; cover.hidden = true; cover.setAttribute('role', 'dialog'); cover.setAttribute('aria-modal', 'true');
  cover.innerHTML = `<div class="ph-in">${TURN}<h2 id="ph-turn-t">${Wd.t('turnTitle')}</h2><p>${Wd.t('turnText')}</p><p>${Wd.t('turnComputer')}</p>
    <div class="ph-acts">${fullscreen ? `<button class="ph-go" type="button" data-full>${FULL}<span>${Wd.t('walkFull')}</span></button>` : ''}<button class="ph-stay" type="button">${Wd.t('turnStay')}</button></div></div>`;
  cover.setAttribute('aria-labelledby', 'ph-turn-t');
  document.body.appendChild(cover);
  cover.querySelector('.ph-stay').onclick = () => { stayed = true; show(); };
  if (fullscreen) cover.querySelector('[data-full]').onclick = () => full(true);
  function show() {
    const on = upright.matches && !stayed && (started || !fullscreen);   // (before its start a page that can go full screen lets its start button turn it)
    cover.hidden = !on; const fb = cover.querySelector('[data-full]'); if (fb) fb.hidden = isFull();
    if (on && !was) onUpright(); was = on;
  }
  upright.addEventListener('change', show); document.addEventListener('fullscreenchange', show); document.addEventListener('webkitfullscreenchange', show);
  show();
  return {
    fullscreen, full, isFull,
    start(label, go) {   // a big button over the page; its tap goes full screen where it can, then go()
      const s = document.createElement('div'); s.className = 'ph-start';
      s.innerHTML = `<div><button class="ph-go" type="button">${PLAY}<span>${label}</span></button>${upright.matches || Math.min(innerWidth, innerHeight) <= 600 ? `<p class="ph-note">${Wd.t('turnComputer')}</p>` : ''}</div>`;
      document.body.appendChild(s);
      s.querySelector('button').onclick = () => { s.remove(); started = true; if (fullscreen) full(true); else show(); go(); };
      return s;
    },
  };
}

// A film on a video site as a player inside a page (the entry page's player; tools/site.mjs, for the city pages' video data):
// YouTube (privacy-enhanced: no cookies before play) and Bilibili; null for any other site, which is linked instead.
export function embed(url, autoplay = true) {
  let u; try { u = new URL(url); } catch { return null; }
  const h = u.hostname.replace(/^(www|m)\./, '');
  const yt = h === 'youtu.be' ? u.pathname.slice(1) : h === 'youtube.com' ? (u.searchParams.get('v') || (u.pathname.match(/^\/(embed|shorts|live)\/([\w-]{11})/) || [])[2]) : null;
  if (yt && /^[\w-]{11}$/.test(yt)) return `https://www.youtube-nocookie.com/embed/${yt}` + (autoplay ? '?autoplay=1&rel=0&playsinline=1' : '');
  const bv = h === 'bilibili.com' && (u.pathname.match(/\/video\/(BV\w+)/) || [])[1];
  if (bv) return `https://player.bilibili.com/player.html?bvid=${bv}` + (autoplay ? '&autoplay=1&high_quality=1&danmaku=0' : '&autoplay=0');
  return null;
}

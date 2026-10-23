// This machine's settings for the Node tools: local/config.json (not in git; the keys are in pipeline/local.py, the file is written
// at first use, SKILL.md 第一次使用). Read only when a key is asked for.
import fs from 'fs'; import os from 'os'; import path from 'path'; import { fileURLToPath } from 'url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
let cfg = null;
export function local(key) {
  if (!cfg) {
    const f = path.join(ROOT, 'local', 'config.json');
    if (!fs.existsSync(f)) { console.error("no local/config.json: copy templates/local.json there and set this machine's paths (SKILL.md 第一次使用)"); process.exit(2); }
    cfg = JSON.parse(fs.readFileSync(f, 'utf8'));
  }
  if (!(key in cfg)) { console.error(`local/config.json has no "${key}" (templates/local.json lists every key)`); process.exit(2); }
  return cfg[key];
}
// a path key: relative to the project root, ~ for the home folder, '' stays ''
export function localPath(key) {
  const v = local(key);
  return v ? path.resolve(ROOT, v.replace(/^~(?=$|[\\/])/, os.homedir())) : '';
}
// a city's folders, as pipeline/layout.py lays them out
export const cityDir = (slug, ...p) => path.join(ROOT, 'cities', slug, ...p);
export const buildDir = (slug, ...p) => cityDir(slug, 'build', ...p);

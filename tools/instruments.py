"""The sample libraries of the code score (film.music.source: code; audio/sampler.py) into this machine's `instruments` folder
(local/config.json).
usage: python -I tools/instruments.py [vsco2ce] [vcsl] [--force]      both when none is named (about 700 MB); a library already
       there is kept unless --force; a broken download resumes where it stopped.
VS Chamber Orchestra: Community Edition and the Versilian Community Sample Library (Versilian Studios, CC0 1.0), with the sampler's
index of them (index.json), as lemo-opuscar packed them: the packs come from its GitHub release (only the host: the samples are CC0),
are checked against their SHA-256 and unpacked here."""
import hashlib, os, shutil, sys, tarfile, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline'))
import local

URL = 'https://github.com/lemomo-ai/lemo-opuscar/releases/download/assets/'
PACKS = {'vsco2ce': ('instruments-vsco2ce.tar', 413911040, '231297103cb4a3123707ddb7b284e5ea3aed0b8d77c0b891360b4d3efe8b586f'),
         'vcsl': ('instruments-vcsl.tar', 284682240, '3ed8f753500e629485e323fc7f883b35aca6a77a1ab04522d1d47037d503f6e1')}
PREFIX = 'core/audio/instruments/'   # where the packs put their files (lemo-opuscar's layout)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()


def download(url, tmp, size):
    have = lambda: os.path.getsize(tmp) if os.path.exists(tmp) else 0
    if have() > size: os.remove(tmp)   # not a part of this pack
    while have() < size:
        req = urllib.request.Request(url, headers={'Range': f'bytes={have()}-'} if have() else {})
        with urllib.request.urlopen(req, timeout=60) as r:
            append = have() > 0 and r.status == 206   # a server that ignores Range sends it all again
            with open(tmp, 'ab' if append else 'wb') as f:
                done = f.tell()
                while chunk := r.read(1 << 20):
                    f.write(chunk); done += len(chunk); print(f'\r  {os.path.basename(url)} {done / size * 100:5.1f} %', end='', flush=True)
    print()


def unpack(tmp, dest):
    """the pack's files under PREFIX, without it, into dest (tarfile's data filter: nothing outside dest, no devices)"""
    with tarfile.open(tmp) as t:
        ms = []
        for m in t.getmembers():
            if not m.name.startswith(PREFIX) or m.name == PREFIX: continue
            m.name = m.name[len(PREFIX):]
            if m.islnk() and m.linkname.startswith(PREFIX): m.linkname = m.linkname[len(PREFIX):]
            ms.append(m)
        t.extractall(dest, members=ms, filter='data')


def main():
    args = [a for a in sys.argv[1:] if a != '--force']; force = '--force' in sys.argv
    libs = args or list(PACKS)
    bad = [l for l in libs if l not in PACKS]
    if bad: raise SystemExit(f'instruments: no library {", ".join(bad)} (there are: {", ".join(PACKS)})')
    dest = local.path('instruments'); os.makedirs(dest, exist_ok=True)
    for lib in libs:
        name, size, sum_ = PACKS[lib]
        if not force and os.path.isdir(os.path.join(dest, lib)) and os.path.exists(os.path.join(dest, 'index.json')):
            print(f'{lib}: already in {dest}'); continue
        tmp = os.path.join(dest, name + '.download')
        need = int(size * 2.2) - (os.path.getsize(tmp) if os.path.exists(tmp) else 0)
        if shutil.disk_usage(dest).free < need: raise SystemExit(f'instruments: {name} needs about {need / 1e9:.1f} GB free in {dest} while it downloads and unpacks')
        try: download(URL + name, tmp, size)
        except OSError as e: raise SystemExit(f'instruments: the download stopped ({e}); run the same command again to resume')
        if sha256(tmp) != sum_: os.remove(tmp); raise SystemExit(f'instruments: {name} does not match its checksum; run again')
        unpack(tmp, dest); os.remove(tmp)
        print(f'{lib}: in {dest}')


if __name__ == '__main__':
    main()

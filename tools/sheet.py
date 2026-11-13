"""Contact sheet for review (adapted from lemo-opuscar core/render/sheet.py, MIT; see NOTICE):
usage: python -I tools/sheet.py out.jpg img1 img2 ... [--cols 4] [--w 480] [--fit stretch|contain|cover]
The first image sets the tile aspect; contain letterboxes and cover crops centrally without changing proportions.
Each still has its file name above it."""
import os, sys
from PIL import Image, ImageDraw, ImageOps
args = sys.argv[1:]; cols = 4; w = 480; fit = 'stretch'
if '--cols' in args: i = args.index('--cols'); cols = int(args[i + 1]); del args[i:i + 2]
if '--w' in args: i = args.index('--w'); w = int(args[i + 1]); del args[i:i + 2]
if '--fit' in args: i = args.index('--fit'); fit = args[i + 1]; del args[i:i + 2]
if fit not in ('stretch','contain','cover'): raise SystemExit('sheet: --fit stretch, contain or cover')
out, files = args[0], args[1:]
im0 = Image.open(files[0]); h = w * im0.height // im0.width; rows = (len(files) + cols - 1) // cols
S = Image.new('RGB', (cols * w, rows * (h + 22)), (20, 20, 24)); d = ImageDraw.Draw(S)
for k, f in enumerate(files):
    im = Image.open(f).convert('RGB')
    if fit == 'cover': im = ImageOps.fit(im,(w,h),method=Image.Resampling.LANCZOS)
    elif fit == 'contain': im = ImageOps.pad(im,(w,h),method=Image.Resampling.LANCZOS,color=(20,20,24))
    else: im = im.resize((w,h))
    x, y = (k % cols) * w, (k // cols) * (h + 22)
    S.paste(im, (x, y + 22)); d.text((x + 6, y + 5), os.path.basename(f), fill=(230, 230, 230))
S.save(out, quality=88); print(out, S.size)

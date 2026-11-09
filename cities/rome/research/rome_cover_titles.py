"""Exact title variants on approved A artwork; CPU typography only."""
import json
import shutil
from PIL import Image, ImageDraw
from rome_cover_layout import BASE, font, draw_label


OUT = BASE / 'titles_v2'
OUT.mkdir(parents=True, exist_ok=True)
VARIANTS = [
    ('zh1', '2800年城市兴衰', '公元前753年到公元2026年', '永恒之城'),
    ('zh2', '30分钟看完2800年', None, '3D还原'),
    ('zh3', '百万之城为何只剩5万人？', None, None),
]


def fit(text, filename, max_size, width, weight=900):
    for size in range(max_size, 15, -1):
        face = font(filename, size, weight)
        if face.getlength(text) <= width:
            return face, size
    raise ValueError(f'Text does not fit: {text}')


records = []
for ident, sub, date, badge in VARIANTS:
    title = '罗马'
    for shape, size in [('wide', (3840, 2160)), ('portrait', (1080, 1440))]:
        portrait = shape == 'portrait'
        source = BASE / 'generated' / f'A_{shape}.png'
        image = Image.open(source).convert('RGBA').resize(size, Image.Resampling.LANCZOS)
        max_width = 960 if portrait else 2780
        title_max = 320 if portrait else 680
        face_file = 'NotoSansSC-VF.ttf'
        title_face, title_size = fit(title, face_file, title_max, max_width)
        title_top = 100 if portrait else 80
        stroke = 5 if portrait else 17
        shadow = (2, 7, 5) if portrait else (6, 18, 13)
        title_box = draw_label(image, title, title_face, size[0] / 2,
                               title_top, '#ffda42', stroke, shadow)
        sub_file = 'NotoSansSC-VF.ttf'
        sub_face, sub_size = fit(sub, sub_file, 86 if portrait else 205,
                                 max_width, 900)
        sub_top = title_box[3] + (30 if portrait else 48)
        sub_box = draw_label(image, sub, sub_face, size[0] / 2,
                             sub_top, '#fff9e9', 3 if portrait else 8, shadow)
        boxes = [title_box, sub_box]
        last_box = sub_box
        if date:
            date_face, _ = fit(date, sub_file, 65 if portrait else 160, max_width, 850)
            last_box = draw_label(image, date, date_face, size[0] / 2,
                                  last_box[3] + (24 if portrait else 36),
                                  '#fff9e9', 2 if portrait else 6, shadow)
            boxes.append(last_box)
        if badge:
            badge_face = font(sub_file, 55 if portrait else 126, 900)
            badge_w = badge_face.getlength(badge)
            pad_x, pad_y = (22, 12) if portrait else (52, 26)
            badge_top = last_box[3] + (30 if portrait else 44)
            badge_h = badge_face.getbbox(badge)[3] - badge_face.getbbox(badge)[1]
            rect = [size[0] / 2 - badge_w / 2 - pad_x, badge_top - pad_y,
                    size[0] / 2 + badge_w / 2 + pad_x, badge_top + badge_h + pad_y]
            ImageDraw.Draw(image).rounded_rectangle(rect, radius=8 if portrait else 18,
                                                    fill='#762b22', outline='#ffda42',
                                                    width=2 if portrait else 5)
            boxes.append(draw_label(image, badge, badge_face, size[0] / 2,
                                     badge_top, '#fff0bc', 1 if portrait else 3, shadow))
        mark = '一城春秋'
        mark_face = font(sub_file, 30 if portrait else 70, 850)
        mark_w = mark_face.getlength(mark)
        mark_x = 68 if portrait else 540
        mark_box = draw_label(image, mark, mark_face, mark_x + mark_w / 2,
                              1364 if portrait else 2014, '#fff9e9',
                              1 if portrait else 3, shadow)
        name = f'rome_A_{ident}_{shape}'
        image.convert('RGB').save(OUT / f'{name}.jpg', quality=96, subsampling=0)
        image.convert('RGB').resize((320, round(size[1] * 320 / size[0])),
                                    Image.Resampling.LANCZOS).save(
                                        OUT / f'{name}_320.jpg', quality=95, subsampling=0)
        safe = [0, size[0]] if portrait else [480, 3360]
        boxes.append(mark_box)
        for box in boxes:
            assert safe[0] <= box[0] < box[2] <= safe[1], (name, box)
            assert 0 <= box[1] < box[3] <= size[1], (name, box)
        records.append(dict(id=ident, shape=shape, file=f'{name}.jpg',
                            thumbnail=f'{name}_320.jpg', title=title, subtitle=sub,
                            date=date, badge=badge, title_size=title_size,
                            subtitle_size=sub_size, bounds=boxes, size=list(size)))

# The original English date artwork remains byte-for-byte unchanged.
for ident, part, subtitle in [('en_date', 'en', '753 BCE → 2026'),
                              ('en_time', 'en_time', '2,800 years in 30 minutes')]:
    for shape in ['wide', 'portrait']:
        name = f'rome_A_{part}_{shape}'
        for suffix in ['.jpg', '_320.jpg']:
            shutil.copyfile(BASE / 'titles' / f'{name}{suffix}', OUT / f'{name}{suffix}')
        records.append(dict(id=ident, shape=shape, file=f'{name}.jpg',
                            thumbnail=f'{name}_320.jpg', title='ROME', subtitle=subtitle))

# A literally 320-pixel-wide sheet; each item uses its exact delivered thumbnail.
order = ['zh1', 'zh2', 'zh3', 'en_date', 'en_time']
records.sort(key=lambda r: (order.index(r['id']), r['shape'] == 'portrait'))
label_face = font('InterTight-VF.ttf', 17, 850)
thumbs = [(r, Image.open(OUT / r['thumbnail'])) for r in records]
sheet = Image.new('RGB', (320, sum(im.height + 30 for _, im in thumbs)), '#101a2c')
draw = ImageDraw.Draw(sheet)
y = 0
for record, thumb in thumbs:
    draw.text((9, y + 5), f"A / {record['id']} / {record['shape']}",
              font=label_face, fill='white')
    sheet.paste(thumb, (0, y + 30))
    y += thumb.height + 30
sheet.save(OUT / 'review_320_contact.jpg', quality=96, subsampling=0)
(OUT / 'layout_manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'covers': len(records), 'thumbnails': len(records), 'sheet': str(OUT / 'review_320_contact.jpg')}, ensure_ascii=False))

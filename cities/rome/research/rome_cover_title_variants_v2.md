# A 封面排字第二版：用户定稿

最终选用简体1、英文年月；英文时长仅作YouTube Test & Compare。简体2、简体3及英文时长直式不交付。所有选用母版均来自本页的`titles_v2/`，日期使用“到”。最终交付时将英文年月横式复制为`dist/poster.jpg`，另将以下五张复制到`dist/covers/`：

- `rome_A_zh1_wide.jpg`、`rome_A_zh1_portrait.jpg`：B站。
- `rome_A_en_wide.jpg`、`rome_A_en_portrait.jpg`：英文主封面；横式也用于网站入口。
- `rome_A_en_time_wide.jpg`：YouTube Test & Compare。

封面与成片最后一起交付；2K重出仍待总表审核，不单独发信。

采用主线看过B站同类影片后给出的新文案，取代上一版三组举例。仅排字，沿用已选A画面，没有重新生成、没有GPU任务，也没有改动正式poster或影片。

总表：`assets/covers/r15/titles_v2/review_320_contact.jpg`，宽320像素；十张缩图各自也都是320像素宽。

| 版本 | 文案 | 横式母版 | 直式母版 |
| --- | --- | --- | --- |
| 简体1 | 罗马／2800年城市兴衰／公元前753年到公元2026年；标签“永恒之城” | `rome_A_zh1_wide.jpg` | `rome_A_zh1_portrait.jpg` |
| 简体2 | 罗马／30分钟看完2800年；标签“3D还原” | `rome_A_zh2_wide.jpg` | `rome_A_zh2_portrait.jpg` |
| 简体3 | 罗马／百万之城为何只剩5万人？ | `rome_A_zh3_wide.jpg` | `rome_A_zh3_portrait.jpg` |
| 英文年月 | ROME／753 BCE → 2026 | `rome_A_en_wide.jpg` | `rome_A_en_portrait.jpg` |
| 英文时长 | ROME／2,800 years in 30 minutes | `rome_A_en_time_wide.jpg` | `rome_A_en_time_portrait.jpg` |

所有文件在`assets/covers/r15/titles_v2/`。同名加`_320.jpg`是缩图。横式3840×2160、直式1080×1440；横式文字均在中央4:3范围内。

简体采用Noto Sans SC 900，城市名金黄、深色描边、阴影。横式城市名字号680像素，较第一版扩大；副标白色粗体。逐一查看六张简体320像素缩图，并核对文字、尺寸和安全范围。英文四张母版及对应缩图直接从上一版复制，字节未变。

可重现：`.venv/bin/python cities/rome/research/rome_cover_titles.py`，仅Pillow排字与输出尺寸处理。

## description.md 标题

简体部分已改成主线给的三条候选；英文改为指定的YouTube候选。源文件`research/rome_round14g_description.md`与现有交付`description.md`同步，新交付时复制。

1. 罗马城的3D历史演变，从公元前753年到2026年，30分钟看完永恒之城2800年兴衰｜一城春秋
2. 一口气看完罗马2800年：从台伯河边的茅屋，到百万人口的帝都，再到今天｜一城春秋
3. 曾经百万人口的罗马，为何一度只剩5万人？3D还原永恒之城2800年｜一城春秋

YouTube：Evolution of Rome, 753 BCE to 2026: 2,800 Years on One Map | A City Through Time

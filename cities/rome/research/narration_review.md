# 羅馬：導演確認稿與重新估時

[導演確認英文稿](../NARRATION_DRAFT_EN.md)／[中文對照](../NARRATION_REVIEW_ZH.md)／[細綱](detailed_outline.md)。

2026-10-26，導演直接修改並確認旁白；以現行英文檔為製作依據。本輪補第08站的兩點來源S73、S74，沒有改動確認稿。改前文字已由導演存於[archive](archive/narration_before_director_edit_EN.md)。

## 重新估時

以下保留導演確認稿的文字估時。第3步已完成正式雙語字幕，主線修正為僅按英文旁白計時後，compile排為13:36.90；原14:16仍只是文字估計，新規則與逐站時間見[script_review.md](script_review.md)。旁白本身未改動。

| 項目 | 結果 |
|---|---:|
| 英文正文 | **1,638詞** |
| 正常估算語速 | 2.5詞／秒 |
| 字面朗讀 | 655.2秒／10:55 |
| 加換氣、片頭片尾與必要觀看 | 826.05秒／13:46 |
| 專名、年份和數字發音餘量 | 30秒 |
| **合計** | **856.05秒／約14:16** |

沿用既有測量腳本及55秒必要觀看、H01／H02各4秒、20秒片頭、2秒片名、18秒片尾。沒有提高語速或增加靜默。本次第08站125詞，基礎估時約0:55。這是文字估時，正式雙語字幕和配音排程可能延長，尚非成片時長。

```sh
uv run --no-sync --offline python -I cities/rome/research/measure_narration.py
```

## 各站基礎估時

不含全片30秒發音餘量，不是鎖定節點秒數。

| 節點 | 詞數 | 字面朗讀 | 本站估時 |
|---|---:|---:|---:|
| P · Prologue | 24 | 0:10 | 0:20 |
| 01 · A name on a hillside | 58 | 0:23 | 0:29 |
| 02 · Winning the sea, losing the republic | 108 | 0:43 | 0:49 |
| 03 · The imperial city rises | 158 | 1:03 | 1:21 |
| 04 · The court moves away | 77 | 0:31 | 0:38 |
| 05 · The city is taken | 86 | 0:34 | 0:43 |
| 06 · A smaller city draws people back | 88 | 0:35 | 0:42 |
| 07 · Making Rome again | 279 | 1:52 | 2:28 |
| 08 · A capital fought for | 125 | 0:50 | 0:55 |
| 09 · War and a way home | 93 | 0:37 | 0:42 |
| 10 · Rome makes pictures | 70 | 0:28 | 0:31 |
| 11 · The world comes to Rome | 106 | 0:42 | 0:47 |
| 12 · A larger Rome | 126 | 0:50 | 1:06 |
| 13 · Waiting for the next guest | 76 | 0:30 | 0:38 |
| 14 · Rome looks ahead | 164 | 1:06 | 1:20 |
| E01片尾 | 0 | 0:00 | 0:18 |

## 確認狀態與下一步

旁白已確認，世界盃仍在12站1990生長畫面上一句帶過。01、03、07、10、13、14站的導演感受句修改和第08站新文是保留基線，不回套先前稿件。

第2步底模及範圍審查已通過，完整area資料已重跑；第3步已建立script.yaml及十四站文字排程。歷代城市、逐站預覽及聲音尚未完成，新時間結果見script_review.md。第4步地形倍率及市中心山丘近景另按MODEL規則驗收。

確認稿SHA-256：`b106e072a961d6181c7447dfe62fb42f1cbce8097e838f91fae2c406b8113353`。

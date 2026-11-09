# Rome 畫面文字核查

本檢查器只讀並提出建議；已授權畫面文字修正另見 rome_graphic_text_spacing_receipt.json。字幕及旁白來源未改。

## 根因

- Initial builder literals contained about50,000, ·75, the113, native403 and readout ·113. These source spacing defects are corrected; the before/after receipt records exact originals.
- Builder read/write uses yaml CSafeLoader/CSafeDumper without copy-space transformation. compile.py tx substitutes placeholders only; overlay.js txt passes text directly to measureText/fillText.
- subtitle_helper.normalize and apply_alignment.normalized remove whitespace only for equality checks. Slices preserve internal whitespace and use strip() only. These comparisons cannot detect space-only damage; exact per-id comparison below can.

## formal

畫面欄位 201；問題 0；字幕 360 組，逐 id 雙語完全相等：True。

## candidate

畫面欄位 154；問題 0；字幕 185 組，逐 id 雙語完全相等：True。

## persistent_draft

畫面欄位 154；問題 0；字幕 185 組，逐 id 雙語完全相等：True。

## compiled_overlay

畫面欄位 133；問題 0。

來源 SHA256 與完整逐項核查見同名 JSON。
A/LM/S 數字代碼不當英文詞拆分；中文詞與數字不要求加空格。

# 第一次使用：本機設定與環境（每台電腦一次）

每台電腦的硬碟安排不一樣，所以本機的路徑和設定都不寫在程式和提交的檔案裡，只放在 `local/config.json`（不進 git，`pipeline/local.py`
讀它；範本 `templates/local.json`）。沒有這個檔時先做這一步，再開始任何城市：
1. **建議全部集中放在專案的 `local/` 下**：範本就是這樣（`local/raw`、`local/ref`、`local/models/...`、`local/instruments`），整個資料夾
   被 .gitignore 擋住，搬家、備份、清掉都只動一處。相對路徑從專案根目錄算，Linux、macOS、Windows 都一樣。只有用戶自己另有安排時
   （例如硬碟不夠，大檔要放別顆硬碟）才逐項改成絕對路徑，`~` 可用。
2. **逐項問用戶**（AskUserQuestion，先講建議值和大約大小）：
   - `raw`：下載的原始資料（OSM、CMAB、Overture、GHSL），一座城約 1–2 GB；
   - `ref`：實拍與照片的下載原檔（各城 `assets/footage/make.sh` 從這裡剪片段）；
   - `stable_audio`、`hf_cache`：選了 Stable Audio 3 配樂才要（程式約 2.5 GB、權重約 3.2 GB）；
   - `instruments`：選了程式配樂才要（取樣庫約 670 MB）；
   - `chrome`：Playwright 自帶的 headless shell 裝不上時（例如 Ubuntu 20.04），改用系統 Chrome 的路徑；空字串＝用 Playwright 自帶的；
   - `workers`：同時渲染幾頁；邊用電腦邊渲染給 2。
3. 照回答寫 `local/config.json`，建好資料夾。
4. 檢查工具：uv、Node 20 以上、ffmpeg、exiftool（出片清元數據）。`npm ci` 裝 three 和 playwright-core（版本固定在 `package-lock.json`）；`uv sync` 建 Python 環境：uv 照 `.python-version` 自己下載 Python 3.12，
   照 `uv.lock` 裝套件（`pyproject.toml` 列依賴，新增套件用 `uv add`）。
之後所有 Python 指令都用 `uv run python -I …`，不要用系統的 `python`（可能是別的版本，例如 2.7）。之後換電腦或改路徑，只改 `local/config.json`。

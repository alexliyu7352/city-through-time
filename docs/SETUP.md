# First use: local settings and environment (once per computer)

Every computer arranges its disks differently, so local paths and settings are not written in code or in committed files. They live only in `local/config.json` (not in git; `pipeline/local.py`
reads it; template `templates/local.json`). When this file is missing, do this step first, before any city:
1. **Put everything under the project's `local/`** (recommended): the template does exactly this (`local/raw`, `local/ref`, `local/models/...`, `local/instruments`), and the whole folder
   is blocked by .gitignore, so moving, backing up and clearing touch one place only. Relative paths count from the project root and work the same on Linux, macOS and Windows. Change an entry to an absolute path only when the user has their own arrangement
   (for example the disk is too small and big files must go on another drive); `~` is allowed.
2. **Ask the user about each entry** (AskUserQuestion; state the suggested value and the approximate size first):
   - `raw`: downloaded raw data (OSM, CMAB, Overture, GHSL), about 1–2 GB per city;
   - `ref`: the original downloads of footage and photos (each city's `assets/footage/make.sh` cuts clips from here);
   - `stable_audio`, `hf_cache`: needed only if Stable Audio 3 is chosen for the music (program about 2.5 GB, weights about 3.2 GB);
   - `instruments`: needed only if the code score is chosen (sample library about 670 MB);
   - `chrome`: when Playwright's own headless shell cannot be installed (for example Ubuntu 20.04), the path of the system Chrome to use instead; an empty string means Playwright's own;
   - `workers`: how many pages to render at once; give 2 if the user keeps using the computer while it renders.
3. Write `local/config.json` from the answers and create the folders.
4. Check the tools: uv, Node 20 or newer, ffmpeg, exiftool (clears metadata when rendering). `npm ci` installs three and playwright-core (versions pinned in `package-lock.json`); `uv sync` builds the Python environment: uv downloads Python 3.12 itself according to `.python-version`
   and installs packages according to `uv.lock` (`pyproject.toml` lists the dependencies; add a package with `uv add`).
After that, run every Python command as `uv run python -I …`; do not use the system `python` (it may be another version, such as 2.7). To move to another computer or change a path, change only `local/config.json`.

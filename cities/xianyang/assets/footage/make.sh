#!/bin/sh
# Regenerates the footage clips (mp4 is git-ignored). Sources live outside the repo, in this machine's ref folder (local/config.json).
# Only CC / public-domain sources (the non-CC Bilibili clips stay in the ref folder and never reach the film).
set -e
cd "$(dirname "$0")"
ROOT=$(cd ../../../.. && pwd); REF=$(uv run --project "$ROOT" python -I "$ROOT/pipeline/local.py" ref)
COM="$REF/commons"                                            # Wikimedia Commons originals (see CREDITS for file names)
enc() { nice -n 10 ffmpeg -v error -y -ss "$2" -t "$3" -i "$4" -vf "$5,fps=24,eq=saturation=0.85:contrast=1.03" -an -c:v libx264 -preset veryfast -crf 20 -g 1 -pix_fmt yuv420p "$1"; echo "$1"; }
enc weihe_skyline_commons.mp4   2 7 "$COM/qindu_weihe_bridge_4k.webm" "scale=1600:900"
enc longhai_bridge_commons.mp4  4 6 "$COM/weicheng_longhai_bridge_river_4k.webm" "scale=1600:900"
# Commons 4K clips added in v5 (Liuxingy, CC BY-SA 4.0); originals in <ref>/commons/pick/
P="$REF/commons/pick"
enc4k() { nice -n 10 ffmpeg -v error -y -ss "$2" -t "$3" -i "$4" -vf "scale=1920:1080,fps=24" -an -c:v libx264 -preset veryfast -crf 19 -g 1 -pix_fmt yuv420p "$1"; echo "$1"; }
enc4k xixian_aerial_commons.mp4   1   9   "$P/于秦都区沣西大道上向西俯瞰西咸新区、创新港、渭河与鄠邑区.webm"
enc4k longhai_train_commons.mp4   2   9   "$P/渭城 SS7E-0117牵引客车通过陇海铁路渭河桥.webm"
enc4k metro5_commons.mp4          0.5 8.5 "$P/秦都 地铁五号线上跨丰联路与天元路十字.webm"
enc4k fuxing_commons.mp4          0.5 9.5 "$P/秦都 复兴号动车组下行通过徐兰高铁渭河桥.webm"

#!/usr/bin/env bash
# Builds the home hero background video from one or more source clips.
# Usage: tools/make-hero-video.sh clip1.mp4 [clip2.mp4 ...]
# Output: assets/video/hero.mp4 (H.264) and assets/video/hero.webm (VP9), 1920x1080, no audio.
# Clips are cropped to 16:9, trimmed to 6 s each and joined. Aim for a total of 12-20 s.
set -euo pipefail
[ "$#" -ge 1 ] || { echo "Usage: $0 clip1 [clip2 ...]"; exit 1; }
command -v ffmpeg >/dev/null || { echo "ffmpeg is required (brew install ffmpeg)"; exit 1; }
cd "$(dirname "$0")/.."
mkdir -p assets/video
inputs=(); filt=""; i=0
for f in "$@"; do
  inputs+=(-t 6 -i "$f")
  filt+="[$i:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,setsar=1[v$i];"
  i=$((i+1))
done
concat=""; for ((j=0;j<i;j++)); do concat+="[v$j]"; done
filt+="${concat}concat=n=$i:v=1:a=0[out]"
ffmpeg -y -loglevel error "${inputs[@]}" -filter_complex "$filt" -map "[out]" -an \
  -c:v libx264 -preset slow -crf 27 -pix_fmt yuv420p -movflags +faststart assets/video/hero.mp4
ffmpeg -y -loglevel error "${inputs[@]}" -filter_complex "$filt" -map "[out]" -an \
  -c:v libvpx-vp9 -crf 36 -b:v 0 -row-mt 1 assets/video/hero.webm
ls -lh assets/video
echo "Target: each file under ~4 MB. If larger, raise -crf (28-30) or use shorter clips."

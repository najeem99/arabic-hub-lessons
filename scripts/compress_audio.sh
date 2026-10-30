#!/usr/bin/env bash
# Shrink WhatsApp voice notes (320 kbps) to small mono MP3s for the web page.
#   scripts/compress_audio.sh path/to/AUD-*.mp3     -> docs/audio/<same name>.mp3
set -euo pipefail
OUT="$(cd "$(dirname "$0")/.." && pwd)/docs/audio"; mkdir -p "$OUT"
for f in "$@"; do
  name="$(basename "${f%.*}").mp3"
  ffmpeg -nostdin -loglevel error -y -i "$f" -ac 1 -ar 22050 -b:a 48k "$OUT/$name"
  echo "$OUT/$name"
done

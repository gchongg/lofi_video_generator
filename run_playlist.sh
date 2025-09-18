#!/usr/bin/env bash
set -e

# Defaults
IMAGE_FOLDER="./image"
MP3_FOLDER="./spotify"
TIME_LIMIT=120
OUTPUT_FOLDER=""

# Usage info
usage() {
  echo "Usage: $0 <playlist_url> [--image_folder <folder>] [--mp3_folder <folder>] [--time_limit <minutes>] [--output_folder <folder>]"
  exit 1
}

# Parse args
if [ $# -lt 1 ]; then
  usage
fi

PLAYLIST_URL="$1"
shift

while [[ $# -gt 0 ]]; do
  case $1 in
    --image_folder)
      IMAGE_FOLDER="$2"
      shift 2
      ;;
    --mp3_folder)
      MP3_FOLDER="$2"
      shift 2
      ;;
    --time_limit)
      TIME_LIMIT="$2"
      shift 2
      ;;
    --output_folder)
      OUTPUT_FOLDER="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# Ensure folders exist
mkdir -p "$IMAGE_FOLDER" "$MP3_FOLDER"

# Step 1: Download playlist
echo "Downloading playlist from $PLAYLIST_URL..."
spotdl "$PLAYLIST_URL" --output "$MP3_FOLDER"

# Step 2: Build command for create_image_audio_videos.py
CMD=(python3 create_image_audio_videos.py "$IMAGE_FOLDER" "$MP3_FOLDER" "$TIME_LIMIT")
if [ -n "$OUTPUT_FOLDER" ]; then
  CMD+=("$OUTPUT_FOLDER")
fi

echo "Running: ${CMD[*]}"
"${CMD[@]}"
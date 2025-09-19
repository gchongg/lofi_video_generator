#!/usr/bin/env bash
set -euo pipefail

# Defaults
IMAGE_FOLDER="./images"
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

# Prefer tools from a local virtualenv if available
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${VENV_DIR:-"$SCRIPT_DIR/.venv"}"

# Choose spotdl
if [[ -x "$VENV_DIR/bin/spotdl" ]]; then
  SPOTDL="$VENV_DIR/bin/spotdl"
elif [[ -x "$VENV_DIR/Scripts/spotdl.exe" ]]; then
  SPOTDL="$VENV_DIR/Scripts/spotdl.exe"
elif command -v spotdl >/dev/null 2>&1; then
  SPOTDL="spotdl"
else
  echo "spotdl not found. Activate your venv or run scripts/setup_venv.sh" >&2
  exit 1
fi

# Choose python
if [[ -x "$VENV_DIR/bin/python" ]]; then
  PY="$VENV_DIR/bin/python"
elif [[ -x "$VENV_DIR/Scripts/python.exe" ]]; then
  PY="$VENV_DIR/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  echo "Python not found. Please install Python 3.x or create a venv." >&2
  exit 1
fi

# Ensure folders exist
mkdir -p "$IMAGE_FOLDER" "$MP3_FOLDER"

# Step 1: Download playlist
echo "Downloading playlist from $PLAYLIST_URL..."
"$SPOTDL" "$PLAYLIST_URL" --output "$MP3_FOLDER" --user-auth

# Step 2: Build command for create_image_audio_videos.py
CMD=("$PY" create_image_audio_videos.py "$IMAGE_FOLDER" "$MP3_FOLDER" "$TIME_LIMIT")
if [ -n "$OUTPUT_FOLDER" ]; then
  CMD+=("$OUTPUT_FOLDER")
fi

echo "Running: ${CMD[*]}"
"${CMD[@]}"

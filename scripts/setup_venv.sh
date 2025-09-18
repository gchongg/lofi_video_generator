#!/usr/bin/env bash
set -euo pipefail

# Simple cross-platform-ish (POSIX shell) virtualenv setup
# Creates .venv and installs requirements.txt

VENV_DIR="${VENV_DIR:-.venv}"
REQ_FILE="${REQ_FILE:-requirements.txt}"

usage() {
  echo "Usage: VENV_DIR=.venv REQ_FILE=requirements.txt $0" >&2
  echo "Environment variables:" >&2
  echo "  VENV_DIR   Target venv directory (default: .venv)" >&2
  echo "  REQ_FILE   Requirements file path (default: requirements.txt)" >&2
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ ! -f "$REQ_FILE" ]]; then
  echo "Requirements file not found: $REQ_FILE" >&2
  exit 1
fi

# Pick a Python interpreter
PY_BIN="python3"
if ! command -v "$PY_BIN" >/dev/null 2>&1; then
  if command -v python >/dev/null 2>&1; then
    PY_BIN="python"
  else
    echo "Python not found. Please install Python 3.x." >&2
    exit 1
  fi
fi

echo "Creating virtual environment in $VENV_DIR ..."
"$PY_BIN" -m venv "$VENV_DIR"

# Find the python inside the venv (handles Unix and Windows Git Bash)
if [[ -x "$VENV_DIR/bin/python" ]]; then
  VENV_PY="$VENV_DIR/bin/python"
elif [[ -x "$VENV_DIR/Scripts/python.exe" ]]; then
  VENV_PY="$VENV_DIR/Scripts/python.exe"
elif [[ -x "$VENV_DIR/Scripts/python" ]]; then
  VENV_PY="$VENV_DIR/Scripts/python"
else
  echo "Could not locate python inside the venv at $VENV_DIR" >&2
  exit 1
fi

echo "Upgrading pip/setuptools/wheel ..."
"$VENV_PY" -m pip install --upgrade pip setuptools wheel

echo "Installing dependencies from $REQ_FILE ..."
"$VENV_PY" -m pip install -r "$REQ_FILE"

echo
echo "✅ Virtual environment ready: $VENV_DIR"
if [[ -d "$VENV_DIR/bin" ]]; then
  echo "Activate it with: source $VENV_DIR/bin/activate"
  echo "Deactivate with:  deactivate"
else
  echo "On Windows PowerShell, activate with: .\\$VENV_DIR\\Scripts\\Activate.ps1"
  echo "On cmd.exe, activate with:         .\\$VENV_DIR\\Scripts\\activate.bat"
fi


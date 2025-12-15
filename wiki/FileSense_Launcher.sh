#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "[*] Starting FileSense..."

PYTHON_CMD=""

if [[ -x "env/bin/python3" ]]; then
    PYTHON_CMD="env/bin/python3"
    echo "[+] Using virtualenv python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
    echo "[+] Using system python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
    echo "[+] Using system python"
else
    echo "[!] Python not found"
    exit 1
fi

exec "$PYTHON_CMD" scripts/launcher.py

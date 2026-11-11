#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
[ -x .venv-mac/bin/python ] || { echo "Run ./setup-mac.sh first"; exit 1; }
exec ./.venv-mac/bin/python sds100_monitor.py "$@"

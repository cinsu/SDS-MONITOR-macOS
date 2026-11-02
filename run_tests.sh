#!/usr/bin/env bash
# Runs SDS100 Monitor's automated tests. Takes a few seconds; nothing touches your real data,
# settings or scanner (every test uses its own throw-away home folder).
#   bash run_tests.sh          summary
#   bash run_tests.sh -v       every test by name
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"
if ! /usr/bin/python3 -c "import PyQt6.QtWidgets, serial" 2>/dev/null; then
  echo "Note: python3-pyqt6 or python3-serial isn't installed, so the real-Qt test is skipped."
fi
exec /usr/bin/python3 -m unittest discover -s tests -t tests "$@"

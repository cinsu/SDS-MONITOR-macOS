#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/SDS100Monitor-1.1.84"
if [[ "$SOURCE" == "$(realpath -m "$DEST")" ]]; then
  echo "This copy is already installed at $DEST." >&2
  echo "Run install.sh from the extracted download folder instead." >&2
  exit 1
fi
mkdir -p "$DEST" "$HOME/.local/share/applications"
cp -a "$SOURCE"/. "$DEST"/
chmod +x "$DEST/launch.sh"
cat > "$HOME/.local/share/applications/sds100-monitor-1.1.84.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=SDS100 Monitor v1.1.84
Exec="$DEST/launch.sh"
Terminal=false
Categories=Utility;
Icon=$DEST/sds100-monitor.svg
EOF
if [[ -f "$DEST/plasma-widget/metadata.json" ]]; then     # the Plasma 6 widget (1.1.84), for you only
  WIDGET="$HOME/.local/share/plasma/plasmoids/com.github.jmlynchjr.sds100monitor"
  rm -rf "$WIDGET" && mkdir -p "$(dirname "$WIDGET")" && cp -a "$DEST/plasma-widget" "$WIDGET"
fi
echo "Installed SDS100 Monitor v1.1.84 at $DEST"
echo "Requires python3-pyqt6 and python3-serial. Install with: sudo apt install python3-pyqt6 python3-serial"
echo "Macro keypad (optional, once): sudo bash $DEST/install_keypad_rule.sh"

#!/usr/bin/env bash
# One-time setup for the macro keypad: sudo bash install_keypad_rule.sh
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Run with sudo: sudo bash $0" >&2; exit 1; }
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install -m 644 "$HERE/70-sds100-keypad.rules" /etc/udev/rules.d/70-sds100-keypad.rules
# An older minikeyboard rule numbered 99 has no effect; the new one replaces it.
rm -f /etc/udev/rules.d/99-minikeyboard.rules
udevadm control --reload-rules
udevadm trigger --subsystem-match=input --subsystem-match=hidraw
echo "Keypad rule installed. Unplug and replug the keypad."

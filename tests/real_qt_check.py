# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Runs the real program on the real Qt, off screen, in a throw-away home folder.

Run by test_real_qt.py (it is skipped when PyQt6 isn't installed). It builds the main window,
triggers every menu command, opens every window and dialog, switches themes with them open, and
closes everything. Any Python error anywhere, including inside Qt's own event handling, fails it.
Nothing is shown on screen, no scanner is opened, nothing on the network is used, and pop-up
questions are answered automatically.
"""
import importlib.util
import json
import os
import re
import sys
import tempfile
import time
import traceback
from pathlib import Path

HOME = tempfile.mkdtemp(prefix="sds100-monitor-realqt-")
os.environ["HOME"] = HOME
os.environ.pop("XDG_CONFIG_HOME", None)
os.environ["QT_QPA_PLATFORM"] = os.environ.get("SDS100_TEST_PLATFORM", "offscreen")
PROGRAM = Path(os.environ.get("SDS100_MONITOR_PROGRAM", Path(__file__).resolve().parent.parent / "sds100_monitor.py"))
SKIP = re.compile(r"quit|exit|install|program keypad|keypress protocol", re.I)

errors, opened, triggered, skipped = [], [], [], []


def excepthook(kind, value, tb):
    errors.append("".join(traceback.format_exception(kind, value, tb)))


sys.excepthook = excepthook

if os.environ.get("SDS100_STUB_CHECK"):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import qt_stub  # noqa: F401  (checks this script itself without Qt)
import serial  # noqa: E402
import serial.tools.list_ports  # noqa: E402


class NoScanner:
    def __init__(self, *args, **kwargs):
        raise serial.SerialException("no scanner during tests")


serial.Serial = NoScanner
serial.tools.list_ports.comports = lambda *a, **k: []

from PyQt6.QtCore import QUrl  # noqa: E402,F401
from PyQt6.QtGui import QDesktopServices  # noqa: E402
from PyQt6.QtWidgets import (QApplication, QDialog, QFileDialog, QInputDialog, QMessageBox,  # noqa: E402
                             QWidget)

app = QApplication.instance() or QApplication([sys.argv[0]])


def pump(ms=30):
    end = time.monotonic() + ms / 1000
    while time.monotonic() < end:
        app.processEvents()


answers = []
QMessageBox.question = staticmethod(lambda *a, **k: answers.append(("question", a[2:3])) or QMessageBox.StandardButton.No)
for _name in ("information", "warning", "critical"):
    setattr(QMessageBox, _name, staticmethod(lambda *a, _n=_name, **k: answers.append((_n, a[2:3])) or QMessageBox.StandardButton.Ok))
QInputDialog.getText = staticmethod(lambda *a, **k: ("", False))
QInputDialog.getInt = staticmethod(lambda *a, **k: (0, False))
QInputDialog.getItem = staticmethod(lambda *a, **k: ("", False))
QFileDialog.getSaveFileName = staticmethod(lambda *a, **k: ("", ""))
QFileDialog.getOpenFileName = staticmethod(lambda *a, **k: ("", ""))
QFileDialog.getExistingDirectory = staticmethod(lambda *a, **k: "")
QDesktopServices.openUrl = staticmethod(lambda url: answers.append(("openUrl", str(url))) or True)


def fake_exec(self):
    """A dialog opened with exec(): show it, let it draw, then cancel it."""
    opened.append(type(self).__name__)
    self.show()
    pump(40)
    self.reject()
    pump(10)
    return 0


QDialog.exec = fake_exec
QMessageBox.exec = lambda self: answers.append(("box", self.text()[:60])) or QMessageBox.StandardButton.No

spec = importlib.util.spec_from_file_location("sds100_monitor", PROGRAM)
mon = importlib.util.module_from_spec(spec)
sys.modules["sds100_monitor"] = mon


def step(label, func):
    try:
        func()
    except Exception:
        errors.append(f"{label}:\n{traceback.format_exc()}")
    pump()


def menu_actions(menu, path=""):
    for action in menu.actions():
        if action.isSeparator():
            continue
        name = f"{path} → {action.text()}" if path else action.text()
        if action.menu() is not None:
            yield from menu_actions(action.menu(), name)
        else:
            yield name, action


def main():
    spec.loader.exec_module(mon)
    assert str(mon.DATA_DIR).startswith(HOME)
    from PyQt6.QtCore import QSettings
    mon.monitor_settings().setValue("adsb/enabled", "false")   # not this PC's readsb
    window = mon.Monitor()
    window.show()
    pump(200)
    for name, action in list(menu_actions(window.menuBar())):
        if SKIP.search(name) or not action.isEnabled():
            skipped.append(name)
            continue
        triggered.append(name)
        step(f"menu {name}", action.trigger)
    if not os.environ.get("SDS100_STUB_CHECK"):
        def pdf_report():
            path = Path(HOME) / "report-check.pdf"
            mon.save_report_pdf(mon.daily_report_html(mon.daily_report_data("2001-01-01")), path)
            if path.read_bytes()[:5] != b"%PDF-":
                raise AssertionError("the daily report PDF was not written")
        step("save a daily report as PDF", pdf_report)
    tops = [w for w in app.topLevelWidgets()
            if w is not window and type(w).__module__ == "sds100_monitor"]     # the program's own windows
    for widget in tops:
        if isinstance(widget, QDialog):
            continue
        step(f"show {type(widget).__name__}", widget.show)
        opened.append(type(widget).__name__)
    for group, key in (("mode", "light"), ("accent", "green"), ("size", "large"), ("mode", "night"),
                       ("mode", "dark"), ("accent", "blue"), ("size", "normal")):
        step(f"theme {group}={key}", lambda g=group, k=key: window.set_theme_option(g, k))
    pump(200)
    for widget in app.topLevelWidgets():
        from PyQt6 import sip
        if widget is not window and not sip.isdeleted(widget) and widget.isVisible():
            step(f"close {type(widget).__name__}", widget.close)
    step("close main window", window.close)
    pump(200)


try:
    main()
except Exception:
    errors.append("main:\n" + traceback.format_exc())
print(json.dumps({"errors": errors, "triggered": len(triggered), "skipped": skipped,
                  "opened": sorted(set(opened)), "answers": len(answers)}))
sys.stdout.flush()
os._exit(1 if errors else 0)

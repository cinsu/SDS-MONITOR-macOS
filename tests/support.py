# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Shared set-up: load sds100_monitor.py on the Qt stand-in, inside a throw-away home folder.

HOME points at a temporary folder before the program is loaded, so nothing a test does can touch
your real reception history (~/SDS100Monitor), settings or data.
"""
import atexit
import importlib.util
import os
import shutil
import sys
import tempfile
from pathlib import Path

PROGRAM_DIR = Path(__file__).resolve().parent.parent
# SDS100_MONITOR_PROGRAM lets the tests be pointed at another copy (for example an older version).
PROGRAM = Path(os.environ.get("SDS100_MONITOR_PROGRAM", PROGRAM_DIR / "sds100_monitor.py"))

_home = tempfile.mkdtemp(prefix="sds100-monitor-tests-")
atexit.register(shutil.rmtree, _home, True)
os.environ["HOME"] = _home
os.environ.pop("XDG_CONFIG_HOME", None)
HOME = Path(_home)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qt_stub  # noqa: E402,F401  (installs the stand-ins)

_spec = importlib.util.spec_from_file_location("sds100_monitor", PROGRAM)
mon = importlib.util.module_from_spec(_spec)
sys.modules["sds100_monitor"] = mon
_spec.loader.exec_module(mon)
assert str(mon.DATA_DIR).startswith(_home), "tests must never use the real data folder"


class Settings(dict):
    """QSettings stand-in."""

    def __init__(self, *args):
        super().__init__()

    def value(self, key, default=None, **kwargs):
        return self.get(key, default)

    def setValue(self, key, value):
        self[key] = value

    def remove(self, key):
        self.pop(key, None)

    def contains(self, key):
        return key in self

    def sync(self):
        pass


mon.QSettings = Settings


class Signal:
    """Records emit() calls, like a connected Qt signal."""

    def __init__(self):
        self.calls = []

    def emit(self, *args):
        self.calls.append(args)

    def connect(self, *args):
        pass


_monitor = None


def monitor(fresh=False):
    """The main window built on the stand-in (shared unless fresh=True)."""
    global _monitor
    if _monitor is None or fresh:
        _monitor = mon.Monitor()
    return _monitor


def edition():
    return mon.TEN_CODE_EDITION

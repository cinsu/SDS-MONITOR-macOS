# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""The real program on the real Qt (off screen). Skipped where PyQt6 isn't installed.

This is the test that sees what the Qt stand-in can't: Qt calling into the program (event
handlers, dialogs closing), real widget methods and real styling.
"""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def qt_available():
    probe = subprocess.run([sys.executable, "-c", "import PyQt6.QtWidgets, serial"], capture_output=True)
    return probe.returncode == 0


def run_check(stub=False):
    env = dict(os.environ)
    if stub:
        env["SDS100_STUB_CHECK"] = "1"
    result = subprocess.run([sys.executable, str(HERE / "real_qt_check.py")], capture_output=True, text=True,
                            env=env, timeout=300)
    lines = [l for l in result.stdout.splitlines() if l.startswith("{")]
    report = json.loads(lines[-1]) if lines else {"errors": [result.stdout[-3000:] + result.stderr[-3000:]]}
    return result.returncode, report


class RealQtTests(unittest.TestCase):
    def test_check_script_runs(self):
        """The check script itself (on the stand-in, so it runs everywhere)."""
        code, report = run_check(stub=True)
        self.assertEqual(report["errors"], [], "\n".join(report["errors"]))
        self.assertEqual(code, 0)

    @unittest.skipUnless(qt_available(), "PyQt6 (python3-pyqt6) or pyserial isn't installed")
    def test_every_menu_command_and_window_on_real_qt(self):
        code, report = run_check()
        self.assertEqual(report["errors"], [], "\n\n".join(report["errors"]))
        self.assertEqual(code, 0)
        self.assertGreater(report["triggered"], 30, report)


class RealExitTests(unittest.TestCase):
    @unittest.skipUnless(qt_available(), "PyQt6 (python3-pyqt6) or pyserial isn't installed")
    def test_the_program_starts_and_closes_without_crashing(self):
        """Starts sds100_monitor.py itself (off screen, own home folder), closes it after 3 s.
        v1.1.47/48 crashed here with a segmentation fault while Python shut down."""
        import tempfile
        home = tempfile.mkdtemp(prefix="sds100-monitor-exit-")
        env = dict(os.environ, HOME=home, QT_QPA_PLATFORM="offscreen", SDS100_MONITOR_TEST_CLOSE_MS="3000")
        env.pop("XDG_CONFIG_HOME", None)
        program = Path(os.environ.get("SDS100_MONITOR_PROGRAM", HERE.parent / "sds100_monitor.py"))
        result = subprocess.run([sys.executable, "-X", "faulthandler", str(program)], cwd=program.parent,
                                env=env, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, f"exit code {result.returncode}\n{result.stderr[-4000:]}")
        self.assertNotIn("Traceback", result.stderr, result.stderr[-4000:])
        self.assertNotIn("Destroyed while", result.stderr, result.stderr[-4000:])
        self.assertTrue((Path(home) / ".config" / "SDS100Monitor" / "Monitor110.conf").exists(),
                        "settings were not saved on exit")


if __name__ == "__main__":
    unittest.main()

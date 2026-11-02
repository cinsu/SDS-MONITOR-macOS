# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""install.sh, cleanup_old_installs.sh and the version number, run in a throw-away home folder."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import PROGRAM_DIR, mon

VERSION = mon.VERSION


def run(script, home, *args, answer=None):
    env = dict(os.environ, HOME=str(home))
    return subprocess.run(["bash", str(script), *args], input=answer, capture_output=True, text=True,
                          env=env, timeout=60)


class VersionTests(unittest.TestCase):
    def test_version_is_the_same_everywhere(self):
        self.assertRegex(VERSION, r"^\d+\.\d+\.\d+(-personal)?$")
        install = (PROGRAM_DIR / "install.sh").read_text()
        self.assertIn(f'DEST="$HOME/SDS100Monitor-{VERSION}"', install)
        self.assertIn(f"sds100-monitor-{VERSION}.desktop", install)
        self.assertIn(f"Name=SDS100 Monitor v{VERSION}", install)
        self.assertIn(f"(v{VERSION})", (PROGRAM_DIR / "transcribe_worker.py").read_text())
        readme = (PROGRAM_DIR / "README.md").read_text()
        self.assertTrue(readme.startswith("# SDS100 Monitor\n"), readme[:60])
        changes = (PROGRAM_DIR / "CHANGELOG.md").read_text()
        base = VERSION.removesuffix("-personal")
        newest = re.search(r"^## v(\S+):", changes, re.M).group(1)
        self.assertEqual(newest, base, "the newest CHANGELOG entry is for this version")

    def test_licence_and_project(self):
        self.assertIn("GNU GENERAL PUBLIC LICENSE", (PROGRAM_DIR / "LICENSE").read_text()[:200])
        source = (PROGRAM_DIR / "sds100_monitor.py").read_text()
        self.assertIn("SPDX-License-Identifier: GPL-3.0-or-later", source[:200])
        self.assertTrue(mon.PROJECT_URL.startswith("https://github.com/"))
        self.assertNotIn("OWNER", mon.PROJECT_URL, "set the GitHub owner before publishing")

    def test_exits_directly_after_saving(self):
        main = (PROGRAM_DIR / "sds100_monitor.py").read_text().split('if __name__ == "__main__":')[-1]
        self.assertLess(main.index("window.settings.sync()"), main.index("os._exit(code)"))
        self.assertNotIn("sys.exit(app.exec())", main)

    def test_qt_audio_backend_is_chosen_before_qt_loads(self):
        """Qt 6.10's PipeWire audio backend crashed the Monitor at start (v1.1.54)."""
        source = (PROGRAM_DIR / "sds100_monitor.py").read_text()
        choice = source.index('os.environ.setdefault("QT_AUDIO_BACKEND", "pulseaudio")')
        self.assertLess(choice, source.index("from PyQt6"))
        self.assertEqual(os.environ.get("QT_AUDIO_BACKEND"), "pulseaudio")     # set when the program loaded
        probe = subprocess.run([sys.executable, "-c",
                                "import os; os.environ['QT_AUDIO_BACKEND']='pipewire'\n"
                                "os.environ.setdefault('QT_AUDIO_BACKEND', 'pulseaudio')\n"
                                "print(os.environ['QT_AUDIO_BACKEND'])"], capture_output=True, text=True)
        self.assertEqual(probe.stdout.strip(), "pipewire")                     # your own choice wins

    def test_scripts_parse(self):
        for script in PROGRAM_DIR.glob("*.sh"):
            result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"{script.name}: {result.stderr}")


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.home, True)

    def test_install_copies_the_program_and_adds_a_launcher(self):
        result = run(PROGRAM_DIR / "install.sh", self.home)
        self.assertEqual(result.returncode, 0, result.stderr)
        dest = self.home / f"SDS100Monitor-{VERSION}"
        self.assertTrue((dest / "sds100_monitor.py").is_file())
        self.assertTrue(os.access(dest / "launch.sh", os.X_OK))
        desktop = (self.home / ".local/share/applications" / f"sds100-monitor-{VERSION}.desktop").read_text()
        self.assertIn(f'Exec="{dest}/launch.sh"', desktop)
        self.assertIn(f"Icon={dest}/sds100-monitor.svg", desktop)
        again = run(dest / "install.sh", self.home)                     # from the installed copy
        self.assertNotEqual(again.returncode, 0)
        self.assertIn("already installed", again.stderr)


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.home = h = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, h, True)
        apps = h / ".local/share/applications"
        apps.mkdir(parents=True)
        for name in ("SDS100Monitor-1.1.44", "SDS100Monitor-1.1.46-personal", "SDS100Monitor-1.1.46",
                     "SDS100Monitor-1.1.47-personal", "SDS100MonitorV24", "SDS100Monitor", "SDS100MonitorData",
                     "SDS100Monitor-notes"):
            (h / name).mkdir()
            (h / name / "keep.txt").write_text("x")
        for name in ("1.1.44", "1.1.46-personal", "1.1.47-personal"):
            (apps / f"sds100-monitor-{name}.desktop").write_text("[Desktop Entry]\n")
        (apps / "other.desktop").write_text("x")
        self.script = PROGRAM_DIR / "cleanup_old_installs.sh"

    def test_preview_removes_nothing(self):
        result = run(self.script, self.home)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PREVIEW ONLY", result.stdout)
        self.assertTrue((self.home / "SDS100Monitor-1.1.44").exists())

    def test_delete_keeps_the_newest_and_all_data(self):
        result = run(self.script, self.home, "--delete", answer="DELETE OLD VERSIONS\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        left = sorted(p.name for p in self.home.iterdir() if p.name != ".local")
        self.assertEqual(left, ["SDS100Monitor", "SDS100Monitor-1.1.47-personal", "SDS100Monitor-notes",
                                "SDS100MonitorData"])
        apps = sorted(p.name for p in (self.home / ".local/share/applications").iterdir())
        self.assertEqual(apps, ["other.desktop", "sds100-monitor-1.1.47-personal.desktop"])

    def test_package_installed_makes_every_folder_install_old(self):
        deb = self.home / "opt-sds100-monitor"
        deb.mkdir()
        (deb / "sds100_monitor.py").write_text("")
        env_run = lambda *a, **k: subprocess.run(["bash", str(self.script), *a], input=k.get("answer"),
                                                 capture_output=True, text=True, timeout=60,
                                                 env=dict(os.environ, HOME=str(self.home), SDS100_MONITOR_DEB_DIR=str(deb)))
        preview = env_run()
        self.assertIn("installed as a package", preview.stdout)
        env_run("--delete", answer="DELETE OLD VERSIONS\n")
        left = sorted(p.name for p in self.home.iterdir() if p.name not in (".local", "opt-sds100-monitor"))
        self.assertEqual(left, ["SDS100Monitor", "SDS100Monitor-notes", "SDS100MonitorData"])

    def test_keep_and_cancel(self):
        result = run(self.script, self.home, "--delete", "--keep", "1.1.44", answer="no\n")
        self.assertIn("Cancelled", result.stdout)
        self.assertTrue((self.home / "SDS100Monitor-1.1.46").exists())
        run(self.script, self.home, "--delete", "--keep", "1.1.44", answer="DELETE OLD VERSIONS\n")
        self.assertTrue((self.home / "SDS100Monitor-1.1.44").exists())
        self.assertFalse((self.home / "SDS100Monitor-1.1.46-personal").exists())


if __name__ == "__main__":
    unittest.main()

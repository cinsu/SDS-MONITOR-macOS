# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Check for Updates: versions, .deb files in Downloads, GitHub releases, installing."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import mon, monitor

PKG = mon.PACKAGE_NAME


def release(*names, body="What's new"):
    return json.dumps({"tag_name": "v9", "body": body, "assets": [
        {"name": n, "browser_download_url": f"https://github.com/x/y/releases/download/v9/{n}"} for n in names]})


class VersionTests(unittest.TestCase):
    def test_order(self):
        k = mon.version_key
        self.assertLess(k("1.1.53"), k("1.1.54"))
        self.assertLess(k("1.1.99"), k("1.1.100"))
        self.assertEqual(k("1.1.53-personal"), k("1.1.53"))
        self.assertLess(k("0.0.9f"), k("0.0.9g"))
        self.assertLess(k("0.0.9g"), k("0.0.10"))
        self.assertLess(k("0.0.9"), k("0.0.9a"))

    def test_deb_names(self):
        self.assertEqual(mon.deb_version(f"{PKG}_1.1.60_all.deb"), "1.1.60")
        other = "sds100-monitor" if PKG.endswith("personal") else "sds100-monitor-personal"
        self.assertIsNone(mon.deb_version(f"{other}_1.1.60_all.deb"))       # the other edition
        self.assertIsNone(mon.deb_version("sds100-manager_0.0.9g_all.deb"))
        self.assertIsNone(mon.deb_version(f"{PKG}_1.1.60_all.deb.part"))


class LocalTests(unittest.TestCase):
    def test_newer_debs_in_downloads(self):
        folder = Path(tempfile.mkdtemp())
        for name in (f"{PKG}_1.1.50_all.deb", f"{PKG}_1.1.60_all.deb", f"{PKG}_1.1.70_all.deb",
                     "sds100-manager_0.0.20_all.deb", "notes.txt"):
            (folder / name).write_text("x")
        found = mon.local_updates("1.1.55", folder)
        self.assertEqual([v for v, _p in found], ["1.1.70", "1.1.60"])
        self.assertEqual(mon.local_updates("1.1.70", folder), [])
        self.assertEqual(mon.local_updates("1.1.55", folder / "missing"), [])

    def test_install_command_uses_an_absolute_path(self):
        argv = mon.install_command("x.deb")
        self.assertEqual(argv[:4], ["pkexec", "/usr/bin/apt-get", "install", "-y"])
        self.assertTrue(argv[4].startswith("/"))


class GitHubTests(unittest.TestCase):
    def test_latest_release(self):
        got = mon.github_latest("jl/sds100", fetch=lambda url: release(
            f"{PKG}_1.1.60_all.deb", f"{PKG}_1.1.61_all.deb", "sds100-manager_0.0.9g_all.deb", "source.zip"))
        self.assertEqual(got[0], "1.1.61")
        self.assertTrue(got[1].endswith(f"{PKG}_1.1.61_all.deb"))
        self.assertEqual(got[2], "What's new")

    def test_bad_repositories_and_releases(self):
        self.assertIsNone(mon.github_latest("not a repo", fetch=lambda u: release()))
        self.assertIsNone(mon.github_latest("", fetch=lambda u: release()))
        self.assertIsNone(mon.github_latest("a/b", fetch=lambda u: release("other_1.0_all.deb")))
        bad = json.dumps({"assets": [{"name": f"{PKG}_9.9.9_all.deb", "browser_download_url": "http://x/y"}]})
        self.assertIsNone(mon.github_latest("a/b", fetch=lambda u: bad))          # https only


class DefaultsTests(unittest.TestCase):
    def test_public_edition_checks_the_project_releases(self):
        if mon.TEN_CODE_EDITION == "personal":
            self.assertEqual(mon.DEFAULT_GITHUB_REPO, "")              # not published on GitHub
        else:
            self.assertEqual("https://github.com/" + mon.DEFAULT_GITHUB_REPO, mon.PROJECT_URL)
            w = monitor(fresh=True)
            with mock.patch.object(mon.threading, "Thread") as thread:
                w.updates.check()
            self.assertEqual(thread.call_args.kwargs["args"], (mon.DEFAULT_GITHUB_REPO,))


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.w = monitor(fresh=True)
        self.downloads = Path(mon.Path.home()) / "Downloads"
        self.downloads.mkdir(exist_ok=True)
        for f in self.downloads.glob("*.deb"):
            f.unlink()
        self.results = []
        self.w.updates.found.emit = self.results.append
        self.w.settings.setValue("updates/github_repo", "")          # never reach the real GitHub in tests

    def test_nothing_newer(self):
        self.w.updates.check()
        self.assertEqual(self.results, [None])

    def test_local_update_and_skipping(self):
        (self.downloads / f"{PKG}_99.0.0_all.deb").write_text("x")
        with mock.patch.object(mon, "deb_notes", return_value="- Faster"):
            self.w.updates.check(quiet=True)
        self.assertEqual(self.results[-1]["version"], "99.0.0")
        self.assertEqual(self.results[-1]["notes"], "- Faster")
        self.w.settings.setValue("updates/skip_version", "99.0.0")
        self.w.updates.check(quiet=True)
        self.assertIsNone(self.results[-1])                       # skipped at startup…
        self.w.updates.check(quiet=False)
        self.assertEqual(self.results[-1]["version"], "99.0.0")   # …but shown when asked

    def test_github_newer_than_downloads(self):
        (self.downloads / f"{PKG}_99.0.0_all.deb").write_text("x")
        self.w.settings.setValue("updates/github_repo", "jl/sds100")
        with mock.patch.object(mon, "deb_notes", return_value=""), \
                mock.patch.object(mon.threading, "Thread") as thread:
            self.w.updates.check()
        self.assertIsNone(self.results[-1] if self.results else None)
        self.w.updates._github_result(("99.1.0", "https://x/a.deb", "notes", f"{PKG}_99.1.0_all.deb"))
        self.assertEqual((self.results[-1]["version"], self.results[-1]["source"]), ("99.1.0", "GitHub"))
        self.w.updates._github_result({"error": "offline"})
        self.assertEqual(self.w.updates.github_error, "offline")

    def test_dialog_install_flow(self):
        dialog = mon.UpdateDialog(self.w)
        deb = self.downloads / f"{PKG}_99.0.0_all.deb"
        deb.write_text("x")
        deb.chmod(0o600)                                          # like a file in your home folder
        dialog.show_result({"version": "99.0.0", "source": "Downloads", "path": deb,
                            "notes": "n", "name": deb.name})
        started = []
        with mock.patch.object(mon.shutil, "which", return_value="/usr/bin/pkexec"), \
                mock.patch.object(mon, "QProcess") as proc:
            proc.return_value.start.side_effect = lambda prog, args: started.append([prog] + args)
            dialog.install()
        self.assertEqual(started[0][:3], ["pkexec", "/usr/bin/apt-get", "install"])
        staged = Path(started[0][-1])
        self.assertNotEqual(staged.parent, self.downloads)        # a copy apt's "_apt" user can read
        self.assertEqual(staged.stat().st_mode & 0o777, 0o644)
        self.assertEqual(staged.parent.stat().st_mode & 0o777, 0o755)
        self.assertEqual(staged.read_text(), "x")
        dialog.process = None
        dialog.installed(126)                                    # password dialog cancelled
        self.assertIn("cancelled", dialog.result.text())


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Web pages open in a browser that isn't a snap (the snap Firefox may not be installed, or may not
reach pages served on this computer). v1.1.50's OPEN IN BROWSER used KDE's default and failed
with "couldn't find /snap/firefox" on a PC with the apt Firefox."""
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import PROGRAM, mon


class BrowserTests(unittest.TestCase):
    def fake_path(self, scripts):
        folder = Path(tempfile.mkdtemp())
        for name, body in scripts.items():
            f = folder / name
            f.write_text(body)
            f.chmod(0o755)
        return str(folder)

    def run_open(self, path_dir, browser_env=None):
        launched = []
        real_access = os.access
        env = {"PATH": path_dir}
        if browser_env:
            env["BROWSER"] = browser_env
        with mock.patch.dict(os.environ, env, clear=False), \
                mock.patch.object(mon.os, "access", lambda p, m: False if p == "/usr/lib/firefox/firefox" else real_access(p, m)), \
                mock.patch.object(mon.subprocess, "Popen", lambda argv, **k: launched.append(argv)), \
                mock.patch.object(mon.QDesktopServices, "openUrl", lambda url: launched.append(["KDE default"]) or True):
            os.environ.pop("BROWSER", None) if not browser_env else None
            mon.open_in_browser("file:///home/x/daily_report_2026-10-20.html")
        return launched

    def test_skips_a_snap_firefox(self):
        path = self.fake_path({"firefox": "#!/bin/sh\nexec /snap/bin/firefox \"$@\"\n",
                               "chromium": "#!/bin/sh\nexec /usr/lib/chromium/chromium \"$@\"\n"})
        launched = self.run_open(path)
        self.assertEqual(Path(launched[0][0]).name, "chromium")
        self.assertEqual(launched[0][1], "file:///home/x/daily_report_2026-10-20.html")

    def test_uses_an_apt_firefox(self):
        path = self.fake_path({"firefox": "#!/bin/sh\nexec /usr/lib/firefox/firefox \"$@\"\n"})
        self.assertEqual(Path(self.run_open(path)[0][0]).name, "firefox")

    def test_falls_back_to_the_desktop_default(self):
        self.assertEqual(self.run_open(self.fake_path({})), [["KDE default"]])

    def test_browser_variable_wins(self):
        path = self.fake_path({"firefox": "#!/bin/sh\n"})
        self.assertEqual(self.run_open(path, "my-browser --new-tab")[0][:2], ["my-browser", "--new-tab"])

    def test_web_links_never_go_to_kde_default(self):
        """Links and browser buttons go through open_in_browser, not Qt/KDE's default handler."""
        source = PROGRAM.read_text(encoding="utf-8")
        self.assertNotIn("setOpenExternalLinks(True)", source)
        for m in re.finditer(r"QDesktopServices\.openUrl\(\s*([^\n]*)", source):
            line = m.group(1)
            self.assertTrue("fromLocalFile" in line or line.startswith("QUrl(url))"),
                            f"web address opened with KDE's default: {m.group(0)}")
        report = source[source.index("class DailyReportWindow"):source.index("class Monitor(QMainWindow)")]
        self.assertNotIn("QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))", report)


if __name__ == "__main__":
    unittest.main()

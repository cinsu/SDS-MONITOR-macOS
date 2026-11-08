# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Edit in Manager (v1.1.52; in both editions since 1.1.76)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import mon, monitor

ROW = ["2026-10-30 10:00:00", "2026-10-30 10:00:09", "9.0", "Palmetto 800", "Greenville County",
       "Ops 51 (GFD)", " 859.262500MHz", "TGID:44353", "-52"]


class Socket:
    """QLocalSocket stand-in: a Manager is running when `running` is True."""
    running, sent = False, []

    def connectToServer(self, name):
        self.name = name

    def waitForConnected(self, ms):
        return Socket.running

    def write(self, data):
        Socket.sent.append((self.name, data))

    def __getattr__(self, name):
        return lambda *a: True


class ManagerLinkTests(unittest.TestCase):
    def setUp(self):
        Socket.running, Socket.sent = False, []
        self.network = mock.patch.dict("sys.modules", {"PyQt6.QtNetwork": mock.MagicMock(QLocalSocket=Socket)})
        self.network.start()
        self.addCleanup(self.network.stop)
        self.home = Path(tempfile.mkdtemp())

    def install(self, version):
        folder = self.home / f"SDS100DatabaseFavoritesManager-{version}"
        folder.mkdir()
        (folder / "launch.sh").write_text("#!/bin/bash\n")
        return folder / "launch.sh"

    def test_request_from_a_reception(self):
        req = mon.manager_request(dict(zip(mon.HEADERS, ROW)))
        self.assertEqual(req, {"system": "Palmetto 800", "department": "Greenville County",
                               "channel": "Ops 51 (GFD)", "frequency": "859.262500MHz", "tgid": "44353"})
        self.assertEqual(mon.manager_request({"Channel": "—", "Talkgroup": "—"})["channel"], "")

    def test_newest_install(self):
        self.assertIsNone(mon.newest_manager_launcher(self.home))
        self.install("0.0.9e")
        newest = self.install("0.0.10")
        self.install("0.0.9f")
        self.assertEqual(mon.newest_manager_launcher(self.home), newest)

    def test_sends_to_a_running_manager(self):
        Socket.running = True
        text = mon.edit_in_manager(mon.manager_request(dict(zip(mon.HEADERS, ROW))))
        self.assertIn("Sent", text)
        name, data = Socket.sent[0]
        self.assertEqual(name, mon.MANAGER_SERVER)
        self.assertEqual(json.loads(data.decode())["tgid"], "44353")

    def test_starts_the_newest_manager(self):
        launcher = self.install("0.0.9f")
        started = []
        with mock.patch.object(mon, "newest_manager_launcher", return_value=launcher), \
                mock.patch.object(mon.subprocess, "Popen", lambda argv, **k: started.append(argv)):
            text = mon.edit_in_manager({"tgid": "44353", "frequency": "", "system": "P800", "department": "",
                                        "channel": ""})
        self.assertEqual(started[0][:3], ["/bin/bash", str(launcher), "--open-entry"])
        self.assertEqual(json.loads(started[0][3])["system"], "P800")
        self.assertIn("0.0.9f", text)

    def test_not_installed_and_nothing_to_find(self):
        with mock.patch.object(mon, "newest_manager_launcher", return_value=None), \
                mock.patch.object(mon.QMessageBox, "information") as info:
            self.assertIn("not installed", mon.edit_in_manager({"tgid": "1"}))
        info.assert_called_once()
        self.assertIn("Nothing", mon.edit_in_manager({"tgid": "", "frequency": ""}))

    def test_menus(self):
        w = monitor(fresh=True)
        w.last_heard = None
        w.edit_current_in_manager()                          # nothing heard yet: just a message
        w.last_heard = dict(zip(mon.HEADERS, ROW))
        with mock.patch.object(mon, "edit_in_manager", return_value="ok") as edit:
            w.edit_current_in_manager()
        self.assertEqual(edit.call_args[0][0]["tgid"], "44353")
        actions = []
        menu = mock.MagicMock()
        menu.addAction.side_effect = lambda title, *a: actions.append(title)
        mon.add_copy_actions(menu, ROW)
        self.assertIn("Edit in Manager…", actions)


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""1.1.84: the Plasma widget — what the Monitor shares with it, and the widget package."""
import json
import os
import re
import stat
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from support import mon, monitor

WIDGET = Path(mon.__file__).resolve().parent / "plasma-widget"


class WidgetServerTests(unittest.TestCase):
    def setUp(self):
        self.w = w = monitor(fresh=True)
        w.info_values = {"Channel": "Sheriff South", "Frequency": "853.862500MHz", "System": "Palmetto 800",
                         "Mode": "Scan"}
        self.srv = w.widget_server
        self.srv.shutdown()
        self.srv.start()
        self.addCleanup(self.srv.shutdown)
        self.calls = []
        w.control = self.calls.append
        # The stub's signals don't deliver; in Qt this hands the press to the GUI thread.
        self.srv.control_requested = type("Signal", (), {"emit": staticmethod(self.srv.control)})()

    def url(self, path, token=None):
        info = json.loads(mon.WIDGET_FILE.read_text())
        return f"http://127.0.0.1:{info['port']}{path}?t={token or info['token']}"

    def test_file_has_the_address_and_only_you_can_read_it(self):
        info = json.loads(mon.WIDGET_FILE.read_text())
        self.assertEqual(info["port"], self.srv.httpd.server_address[1])
        self.assertEqual(stat.S_IMODE(os.stat(mon.WIDGET_FILE).st_mode), 0o600)

    def test_state_has_the_panel_lines_and_plain_values(self):
        with urllib.request.urlopen(self.url("/api/state"), timeout=5) as r:
            state = json.loads(r.read())
        self.assertEqual(state["values"]["Channel"], "Sheriff South")
        self.assertIn("Sheriff South", [line["text"] for line in state["lines"]])
        self.assertIn("CHANNEL", [line["label"] for line in state["lines"]])
        self.assertFalse(state["receiving"])

    def test_wrong_key_is_refused(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(self.url("/api/state", token="nope"), timeout=5)
        self.assertEqual(cm.exception.code, 403)

    def test_buttons_reach_the_monitor_without_its_question(self):
        req = urllib.request.Request(self.url("/api/control") + "&a=avoid", method="POST", data=b"")
        urllib.request.urlopen(req, timeout=5).read()
        self.assertEqual(self.calls, ["avoid_now"])
        bad = urllib.request.Request(self.url("/api/control") + "&a=reboot", method="POST", data=b"")
        with self.assertRaises(urllib.error.HTTPError):
            urllib.request.urlopen(bad, timeout=5)
        self.assertEqual(self.calls, ["avoid_now"])

    def test_turning_sharing_off_stops_it(self):
        self.srv.set_enabled(False)
        self.assertIsNone(self.srv.httpd)
        self.assertFalse(mon.WIDGET_FILE.exists())
        self.srv.set_enabled(True)
        self.assertIsNotNone(self.srv.httpd)


class WidgetPackageTests(unittest.TestCase):
    def test_metadata(self):
        meta = json.loads((WIDGET / "metadata.json").read_text())
        self.assertEqual(meta["KPlugin"]["Id"], mon.WIDGET_ID)
        self.assertEqual(meta["KPackageStructure"], "Plasma/Applet")
        self.assertEqual(meta["KPlugin"]["Version"], mon.VERSION.removesuffix("-personal"))

    def test_qml_files_are_balanced_and_use_the_right_actions(self):
        for qml in WIDGET.rglob("*.qml"):
            text = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*', "", qml.read_text())
            for a, b in ("{}", "()", "[]"):
                self.assertEqual(text.count(a), text.count(b), f"{qml.name}: {a}{b}")
        main = (WIDGET / "contents/ui/main.qml").read_text()
        for action in re.findall(r'root\.control\("(\w+)"\)', main):
            self.assertIn(action, mon.WIDGET_ACTIONS)
        self.assertIn("SDS100Monitor/widget.json", main)
        self.assertEqual(mon.WIDGET_FILE.name, "widget.json")
        config = (WIDGET / "contents/config/main.xml").read_text()
        for key in re.findall(r"cfg_(\w+?)(?:Default)?\b", (WIDGET / "contents/ui/configGeneral.qml").read_text()):
            self.assertIn(f'name="{key}"', config)


if __name__ == "__main__":
    unittest.main()

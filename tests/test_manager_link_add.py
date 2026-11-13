# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Add to Favorites List in Manager, and reloading SDS-Manager's names when they change (v1.1.73)."""
import json
import unittest

from support import mon, monitor


class AddRequestTests(unittest.TestCase):
    def test_requests(self):
        values = {"System": "Close Call Hits", "Department": "—", "Channel": "453.1500MHz",
                  "Frequency": " 453.150000MHz", "Talkgroup": "—", "Modulation": "nfm"}
        request = mon.add_request(values)
        self.assertEqual((request["action"], request["modulation"], request["tgid"], request["department"]),
                         ("add", "NFM", "", ""))
        self.assertEqual(mon.add_request(dict(values, Modulation="P25"))["modulation"], "AUTO")
        self.assertNotIn("action", mon.manager_request(values))
        self.assertIn("Nothing to add", mon.edit_in_manager({"action": "add", "tgid": "", "frequency": ""}))


class RadioReferenceSearchTests(unittest.TestCase):
    def test_the_request_sds_manager_gets(self):                       # 1.1.81
        self.assertEqual(mon.rr_frequency_request("154.2500MHz"), {"action": "rr_freq", "frequency": "154.250000"})
        self.assertIsNone(mon.rr_frequency_request("—"))
        self.assertIsNone(mon.rr_frequency_request("5"))

    def test_from_the_window(self):
        w = monitor(fresh=True)
        sent, shown = [], []
        old = mon.edit_in_manager
        mon.edit_in_manager = lambda request, parent=None: sent.append(request) or "Starting the Manager…"
        try:
            w.statusBar = lambda: type("S", (), {"showMessage": lambda self, t, ms=0: shown.append(t)})()
            w.last_heard = {"Frequency": "460.0250MHz"}
            w.search_frequency_in_rr()
            self.assertEqual(sent, [{"action": "rr_freq", "frequency": "460.025000"}])
            mon.QInputDialog.getText = staticmethod(lambda *a, **k: ("xyz", True))
            w.search_frequency_in_rr(ask=True)
            self.assertEqual(len(sent), 1)
            self.assertIn("isn't a frequency", shown[-1])
        finally:
            mon.edit_in_manager = old
        del w


class OneMonitorTests(unittest.TestCase):
    def test_its_own_name_and_one_copy(self):                        # 1.1.82
        self.assertEqual(mon.APP_ID, "sds100-monitor")
        self.assertTrue(mon.INSTANCE_SERVER.startswith("sds100-monitor-"))
        source = open(mon.__file__, encoding="utf-8").read()
        self.assertIn("QApplication.setDesktopFileName(APP_ID)", source)
        self.assertIn("bring_forward_running()", source)


class ReloadTests(unittest.TestCase):
    def test_names_reload_when_the_file_changes(self):
        w = monitor(fresh=True)
        calls = []
        w.fill_number_tags = lambda: calls.append("tags")
        w.scanner_tools = type("T", (), {"reload_manager_keys": lambda self: calls.append("tools")})()
        mon.MANAGER_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
        mon.MANAGER_KEYS_FILE.write_text(json.dumps({"lists": []}))
        w.manager_keys_changed()
        self.assertEqual(calls, ["tags", "tools"])
        mon.MANAGER_KEYS_FILE.unlink()


if __name__ == "__main__":
    unittest.main()

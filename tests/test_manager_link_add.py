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

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""The scanner out-of-date warning (v1.1.74). Made-up data in the layout SDS-Manager 0.1.20 writes."""
import json
import unittest

from support import mon, monitor


def data(state=None):
    shared = {"version": 1, "configuration": "Lakeside SDS100",
              "lists": [{"name": "Lakeside County", "systems": []}, {"name": "Highway Patrol", "systems": []}]}
    if state:
        shared["scanner"] = {"state": state, "how": "exported", "when": "2026-11-07T10:00:00",
                             "saved": "2026-11-07T15:20:31"}
    return shared


class ScannerSyncTests(unittest.TestCase):
    def test_saved_but_not_exported(self):
        text = mon.scanner_sync_warning(data("changed"), "FL", "Lakeside County")
        self.assertIn("Scanner out of date: Lakeside SDS100", text)
        self.assertIn("(2026-11-07 15:20)", text)
        self.assertEqual(mon.scanner_sync_warning(data("exported"), "FL", "Lakeside County"), "")
        self.assertEqual(mon.scanner_sync_warning(data(), "FL", "lakeside county"), "")    # older SDS-Manager

    def test_a_list_the_configuration_does_not_have(self):
        text = mon.scanner_sync_warning(data("exported"), "FL", "Hill County")
        self.assertIn('playing Favorites List "Hill County"', text)
        for kind, name in (("FullDb", "—"), ("SWS", "Close Calls"), ("FL", ""), ("FL", "—")):
            self.assertEqual(mon.scanner_sync_warning(data("exported"), kind, name), "")
        self.assertEqual(mon.scanner_sync_warning({}, "FL", "Hill County"), "")

    def test_the_banner_shows_hides_and_stays_hidden(self):
        window = monitor()
        mon.MANAGER_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            mon.MANAGER_KEYS_FILE.write_text(json.dumps(data("changed")))
            window.sync_list = ("FL", "Lakeside County")
            window.update_sync_warning()
            self.assertIn("Scanner out of date", window.sync_banner.text())
            window.dismiss_sync_warning()
            window.update_sync_warning()
            self.assertEqual(window.sync_dismissed, window.sync_banner.text())
            mon.MANAGER_KEYS_FILE.write_text(json.dumps(data("exported")))
            window.update_sync_warning()
            self.assertEqual(window.sync_banner.text(), "")
        finally:
            mon.MANAGER_KEYS_FILE.unlink()


if __name__ == "__main__":
    unittest.main()

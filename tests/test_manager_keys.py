# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Quick key names, number tags and scan profiles from SDS-Manager's shared file (v1.1.68).
The data is made up; the layout is what SDS-Manager 0.1.12 writes."""
import json
import unittest

from support import HOME, mon, monitor



def sample():
    on = [True] * 100
    storm_dept = list(on)
    storm_dept[1] = False
    storm_sys = list(on)
    storm_sys[3] = False
    lists = [
        {"name": "Lakeside County", "filename": "f_000001.hpd", "key": 0, "tag": 1, "monitor": True, "systems": [
            {"name": "Lakeside Trunk", "key": None, "tag": None, "departments": [{"name": "Fire", "key": 0}],
             "channels": []},
            {"name": "Lakeside", "key": 1, "tag": 2,
             "departments": [{"name": "City Fire", "key": 0}, {"name": "City Police", "key": 1},
                             {"name": "Harbor", "key": 1}],
             "channels": [{"name": "PD Events", "tag": 121, "detail": "460.0750 MHz", "department": "City Police"},
                          {"name": "PD Dispatch", "tag": 120, "detail": "460.0250 MHz",
                           "department": "City Police"}]}]},
        {"name": "Highway Patrol", "filename": "f_000002.hpd", "key": None, "tag": None, "monitor": True,
         "systems": [{"name": "Statewide", "key": 3, "tag": None, "departments": [], "channels": []}]},
        {"name": "Hill County", "filename": "f_000003.hpd", "key": 1, "tag": None, "monitor": False,
         "systems": [{"name": "Hill", "key": 3, "tag": 5, "departments": [{"name": "Sheriff", "key": 2}],
                      "channels": []}]}]
    return {"version": 1, "configuration": "Home", "written": "2026-11-07T01:00:00", "lists": lists,
            "profiles": {"Home": {"fl": on, "sys": {"f_000001.hpd": on, "f_000003.hpd": on},
                                  "dept": {"f_000001.hpd|Lakeside": on}, "monitor": {}},
                         "Storm": {"fl": on, "sys": {"f_000001.hpd": on, "f_000003.hpd": storm_sys},
                                   "dept": {"f_000001.hpd|Lakeside": storm_dept}, "monitor": {}}}}


class ManagerKeysTests(unittest.TestCase):
    def test_reading_the_file(self):
        path = HOME / "keys.json"
        path.write_text(json.dumps(sample()))
        self.assertEqual(mon.load_manager_keys(path)["configuration"], "Home")
        path.write_text("not json")
        self.assertEqual(mon.load_manager_keys(path), {})
        self.assertEqual(mon.load_manager_keys(HOME / "missing.json"), {})

    def test_names_per_level(self):
        data = sample()
        self.assertEqual(mon.manager_key_names(data, "FQK"), {0: "Lakeside County", 1: "Hill County"})
        self.assertEqual(mon.manager_key_names(data, "SQK", 0), {1: "Lakeside"})
        self.assertEqual(mon.manager_key_names(data, "DQK", 0, 1),
                         {0: "City Fire", 1: "City Police + Harbor"})
        self.assertEqual(mon.manager_key_names(data, "DQK", 0, 9), {})

    def test_number_tag_choices(self):
        choices = mon.manager_tag_choices(sample())
        self.assertEqual([tags for _label, tags in choices],
                         [(1, None, None), (1, 2, None), (1, 2, 120), (1, 2, 121)])
        self.assertEqual(choices[2][0], "1/2/120 — PD Dispatch (Lakeside)")

    def test_profile_steps_and_merge(self):
        steps = mon.profile_steps(sample(), sample()["profiles"]["Storm"])
        self.assertEqual([(code, read) for code, read, _p, _w in steps],
                         [("FQK", "FQK"), ("SQK", "SQK,0"), ("DQK", "DQK,0,1"), ("SQK", "SQK,1")])
        current = [0] * 100
        current[1] = current[2] = 2
        current[3] = 1
        wanted = steps[2][3]
        merged = mon.merged_quick_keys(current, wanted)
        self.assertEqual(merged[:4], [0, 1, 2, 2])          # unassigned stays 0; key 1 Off; key 3 On


class ProfileRunTests(unittest.TestCase):
    def test_applying_a_profile_reads_then_sets_each_set(self):
        w = monitor(fresh=True)
        tools = mon.ScannerTools.__new__(mon.ScannerTools)
        sent = []
        tools.monitor = type("M", (), {"connected": True})()
        tools.send = lambda command: sent.append(command) or True
        tools.status = object()
        shown = []
        old = mon.set_text
        mon.set_text = lambda label, text: shown.append(text)
        try:
            tools.manager_keys = sample()
            tools.profile_choice = type("C", (), {"currentText": lambda self: "Storm"})()
            tools.apply_scan_profile()
            self.assertEqual(sent, ["FQK"])
            all_on = ",".join(["2", "2"] + ["0"] * 98)
            tools.handle_quick_keys("FQK", all_on)         # nothing to change for list keys
            self.assertEqual(sent[-1], "SQK,0")
            tools.handle_quick_keys("SQK", "0," + ",".join(["0", "2"] + ["0"] * 98))
            self.assertEqual(sent[-1], "DQK,0,1")
            tools.handle_quick_keys("DQK", "0,1," + ",".join(["2", "2"] + ["0"] * 98))
            self.assertEqual(sent[-1], "DQK,0,1," + ",".join(["2", "1"] + ["0"] * 98))
            tools.handle_quick_keys("DQK", "OK")
            self.assertEqual(sent[-1], "SQK,1")
            tools.handle_quick_keys("SQK", "1," + ",".join(["0", "0", "0", "2"] + ["0"] * 96))
            self.assertEqual(sent[-1], "SQK,1," + ",".join(["0", "0", "0", "1"] + ["0"] * 96))
            tools.handle_quick_keys("SQK", "OK")
            self.assertIsNone(tools.profile_run)
            self.assertEqual(sent[-1], "FQK")                # read back for the display
            self.assertIn("Storm applied: 2 set(s)", shown[-1])
        finally:
            mon.set_text = old
        del w


if __name__ == "__main__":
    unittest.main()


class ToolsWindowTests(unittest.TestCase):
    def test_the_window_builds_with_and_without_the_file(self):
        w = monitor(fresh=True)
        tools = mon.ScannerTools(w)
        self.assertEqual(tools.manager_keys, {})
        mon.MANAGER_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
        mon.MANAGER_KEYS_FILE.write_text(json.dumps(sample()))
        try:
            tools.reload_manager_keys()
            self.assertEqual(tools.key_names("FQK")[0], "Lakeside County")
            statuses = [2, 1] + [0] * 98
            tools.qk_status["FQK"] = statuses
            tools.redraw_quick_keys()
            first = tools.qk_buttons["FQK"][0]
            first.setText.assert_called_with("00  Lakeside County")
        finally:
            mon.MANAGER_KEYS_FILE.unlink()

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
    def run_tools(self):
        tools = mon.ScannerTools.__new__(mon.ScannerTools)
        sent, shown, asked = [], [], []
        tools.monitor = type("M", (), {"connected": True})()
        tools.send = lambda command: sent.append(command) or True
        tools.status = object()
        tools.manager_keys = sample()
        tools.profile_choice = type("C", (), {"currentText": lambda self: "Storm"})()
        return tools, sent, shown, asked

    def test_reads_all_shows_the_changes_sets_and_checks(self):     # 1.1.79; 1.1.80: all at once
        w = monitor(fresh=True)
        tools, sent, shown, asked = self.run_tools()
        old, question = mon.set_text, mon.QMessageBox.question
        mon.set_text = lambda label, text: shown.append(text)
        mon.QMessageBox.question = staticmethod(lambda *a: asked.append(a[2]) or mon.QMessageBox.StandardButton.Yes)
        try:
            tools.apply_scan_profile()
            self.assertEqual(sent, ["FQK", "SQK,0", "DQK,0,1", "SQK,1"])       # every read sent together
            # replies may come in any order; they are matched by their key numbers
            tools.handle_quick_keys("SQK", "1," + ",".join(["0", "0", "0", "2"] + ["0"] * 96))
            tools.handle_quick_keys("FQK", ",".join(["2", "2"] + ["0"] * 98))
            tools.handle_quick_keys("DQK", "0,1," + ",".join(["2", "2"] + ["0"] * 98))
            self.assertEqual(asked, [])
            tools.handle_quick_keys("SQK", "0," + ",".join(["0", "2"] + ["0"] * 98))
            self.assertEqual(len(asked), 1)
            self.assertIn("Department keys", asked[0])
            self.assertIn("Off: 01", asked[0])
            self.assertEqual(sent[4:], ["DQK,0,1," + ",".join(["2", "1"] + ["0"] * 98),
                                        "SQK,1," + ",".join(["0", "0", "0", "1"] + ["0"] * 96)])
            tools.handle_quick_keys("DQK", "OK")
            tools.handle_quick_keys("SQK", "OK")
            self.assertEqual(sent[6:], ["DQK,0,1", "SQK,1"])                    # read back to check
            tools.handle_quick_keys("DQK", "0,1," + ",".join(["2", "1"] + ["0"] * 98))
            tools.handle_quick_keys("SQK", "1," + ",".join(["0", "0", "0", "1"] + ["0"] * 96))
            self.assertIsNone(tools.profile_run)
            self.assertEqual(sent[-1], "FQK")                                   # display refreshed
            self.assertIn("Storm applied: 2 set(s)", shown[-1])
            self.assertNotIn("Didn't take", shown[-1])
        finally:
            mon.set_text, mon.QMessageBox.question = old, question
        del w

    def test_a_reply_that_never_comes(self):
        w = monitor(fresh=True)
        tools, sent, shown, asked = self.run_tools()
        old = mon.set_text
        mon.set_text = lambda label, text: shown.append(text)
        try:
            tools.apply_scan_profile()
            tools.handle_quick_keys("FQK", ",".join(["2", "2"] + ["0"] * 98))
            tools.handle_quick_keys("SQK", "0," + ",".join(["0", "2"] + ["0"] * 98))
            tools.handle_quick_keys("DQK", "0,1," + ",".join(["2", "1"] + ["0"] * 98))   # already as wanted
            run = tools.profile_run
            tools.profile_timeout((run["name"], run["phase"], run["serial"]))          # SQK,1 never answers
            self.assertIsNone(tools.profile_run)
            self.assertIn("already matches", shown[-1])
            self.assertIn("SQK,1 (no answer)", shown[-1])
        finally:
            mon.set_text = old
        del w

    def test_warns_when_the_scanner_is_out_of_date(self):
        w = monitor(fresh=True)
        tools, sent, shown, asked = self.run_tools()
        tools.manager_keys["scanner"] = {"state": "changed"}
        old, question = mon.set_text, mon.QMessageBox.question
        mon.set_text = lambda label, text: shown.append(text)
        mon.QMessageBox.question = staticmethod(lambda *a: asked.append(a[2]) or "no")
        try:
            tools.apply_scan_profile()
            for reply in ("FQK", ",".join(["2", "2"] + ["0"] * 98)), \
                         ("SQK", "0," + ",".join(["0", "2"] + ["0"] * 98)), \
                         ("DQK", "0,1," + ",".join(["2", "2"] + ["0"] * 98)), \
                         ("SQK", "1," + ",".join(["0", "0", "0", "2"] + ["0"] * 96)):
                tools.handle_quick_keys(*reply)
            self.assertIn("aren't on the scanner yet", asked[0])
            self.assertIsNone(tools.profile_run)                         # answered No: nothing set
            self.assertFalse(any("," in c and c.count(",") > 50 for c in sent))
        finally:
            mon.set_text, mon.QMessageBox.question = old, question
        del w

    def test_never_switches_every_list_off(self):
        w = monitor(fresh=True)
        tools, sent, shown, asked = self.run_tools()
        tools.manager_keys["profiles"]["Storm"]["fl"] = [False] * 100
        old, warning = mon.set_text, mon.QMessageBox.warning
        warned = []
        mon.set_text = lambda label, text: shown.append(text)
        mon.QMessageBox.warning = staticmethod(lambda *a: warned.append(a[2]))
        try:
            tools.apply_scan_profile()
            for reply in (("FQK", ",".join(["2", "2"] + ["0"] * 98)),
                          ("SQK", "0," + ",".join(["0", "2"] + ["0"] * 98)),
                          ("DQK", "0,1," + ",".join(["2", "2"] + ["0"] * 98)),
                          ("SQK", "1," + ",".join(["0", "0", "0", "2"] + ["0"] * 96))):
                tools.handle_quick_keys(*reply)
            self.assertIsNone(tools.profile_run)
            self.assertIn("nothing to scan", warned[0])
            self.assertFalse(any(c.startswith("FQK,") for c in sent))
        finally:
            mon.set_text, mon.QMessageBox.warning = old, warning
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

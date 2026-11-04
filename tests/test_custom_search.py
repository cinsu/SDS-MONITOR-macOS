# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Custom Search window (v1.1.64) and the reorganized Tools menu."""
import inspect
import unittest

from support import mon, monitor

BANKS1 = ('<GLT><CS_BANK Index="1" Name="Public Safety" Lower="150.000000MHz" Upper="160.000000MHz" '
          'Mod="AUTO" Step="AUTO" Off="Off"/><Footer No="1" EOT="0"/></GLT>')
BANKS2 = ('<GLT><CS_BANK Index="2" Name="Air" Lower="118.000000MHz" Upper="137.000000MHz" '
          'Mod="AM" Step="8.33kHz" Off="On"/><Footer No="2" EOT="1"/></GLT>')


def event(freq="154.430000MHz", bank="Public Safety", units=()):
    return {"info": {"System": "Custom Search", "Department": bank, "Channel": freq, "Frequency": freq,
                     "Talkgroup": "—"}, "units": list(units)}


class CustomSearchTests(unittest.TestCase):
    def setUp(self):
        self.w = monitor(fresh=True)
        self.sent = []
        self.w.queue = lambda c: self.sent.append(c) or True
        self.w.connected = True
        self.s = mon.CustomSearchWindow(self.w)

    def test_avoid_uses_afreq_in_100_hz_units(self):
        self.assertEqual(mon.search_avoid_command(406.0, 1), "AVD,AFREQ,4060000,,1")
        self.assertEqual(mon.search_avoid_command(154.43, 2), "AVD,AFREQ,1544300,,2")

    def test_hits_are_combined_by_frequency(self):
        self.s.add_hit(event(units=["UID:12"]), ["2026-11-03 21:00:00", "", "4.5", "", "", "", "", "", "-70"])
        self.s.add_hit(event(units=["UID:13"]), ["2026-11-03 21:05:00", "", "2.0", "", "", "", "", "", "-60"])
        self.s.add_hit(event("462.562500MHz", ""), ["2026-11-03 21:06:00", "", "1.0", "", "", "", "", "", "-999"])
        hit = self.s.hits["154.430000MHz"]
        self.assertEqual((hit["count"], hit["seconds"], hit["rssi"]), (2, 6.5, -60.0))
        self.assertEqual(hit["units"], ["UID:12", "UID:13"])
        self.assertEqual((hit["first"], hit["last"]), ("2026-11-03 21:00:00", "2026-11-03 21:05:00"))
        self.assertIsNone(self.s.hits["462.562500MHz"]["rssi"])          # -999 means no reading
        self.assertEqual([h["frequency"] for h in self.s.shown_hits()], ["462.562500MHz", "154.430000MHz"])
        self.s.clear_hits()
        self.assertEqual(self.s.hits, {})

    def test_banks_arrive_in_parts(self):
        self.s.load_banks()
        self.assertEqual(self.sent, ["GLT,CS_BANK"])
        self.s.handle_list(BANKS1)
        self.assertEqual(self.sent, ["GLT,CS_BANK", "GLT,CS_BANK"])     # asks for the next part
        self.s.handle_list(BANKS2)
        self.assertEqual([b["Name"] for b in self.s.banks], ["Public Safety", "Air"])

    def test_start_retries_with_index_zero(self):
        self.s.start_search()
        self.assertEqual(self.sent, ["JPM,CTM_MODE,"])
        self.s.route("REPLY: JPM,NG")
        self.assertEqual(self.sent[-1], "JPM,CTM_MODE,0")
        self.s.route("REPLY: JPM,OK")
        self.assertIsNone(self.s.pending)

    def test_listen_and_avoid(self):
        tuned = []
        self.w.tune_frequency = tuned.append
        hit = {"frequency": "154.430000MHz"}
        self.s.listen(hit)
        self.assertEqual(tuned, [154.43])
        self.s.avoid(hit, 2)
        self.assertEqual(self.sent[-1], "AVD,AFREQ,1544300,,2")

    def test_bank_keys_only_while_searching(self):
        keys = []
        self.w.send_key_sequence = lambda codes, what: keys.append(codes)
        self.s.banks = [{"Index": str(i)} for i in range(10)]
        self.s.fill_banks()
        self.s.selected_bank = lambda: (9, self.s.banks[9])
        self.s.toggle_bank()
        self.assertEqual(keys, [])                                      # not searching
        self.s.gsi("Custom Search", "Public Safety", "154.430000MHz", "1000000000", "0")
        self.s.toggle_bank()
        self.assertEqual(keys, [("9",)])                                # bank 9 is key 9
        self.s.selected_bank = lambda: (0, self.s.banks[0])
        self.s.toggle_bank()
        self.assertEqual(keys[-1], ("0",))                              # bank 0 is key 0

    def test_banks_are_numbered_0_to_9(self):
        self.s.banks = [{"Index": str(i), "Name": f"B{i}"} for i in range(10)]
        self.assertEqual(self.s.bank_numbers(), list(range(10)))
        self.s.banks = [{"Index": "4294967295"}, {"Index": "77"}]       # handles, not numbers
        self.assertEqual(self.s.bank_numbers(), [0, 1])

    def test_on_off_comes_from_the_status_report(self):
        self.assertEqual(self.s.bank_state(0), "?")
        self.s.gsi("Custom Search", "Air", "120.000000MHz", "1010000001", "2")
        self.assertEqual([self.s.bank_state(n) for n in (0, 1, 2, 9)], ["On", "Off", "On", "On"])
        self.assertEqual(self.s.current_bank, "2")
        self.s.gsi("Custom Search", "Air", "120.000000MHz", "garbage", "2")
        self.assertEqual(self.s.bank_status, "1010000001")              # bad reports are ignored

    def test_monitor_feeds_the_window(self):
        self.assertIn("self.custom_search.add_hit(event, row)", inspect.getsource(mon.Monitor.finish_event))
        self.assertIn("self.custom_search.gsi(", inspect.getsource(mon.Monitor.process_xml))
        self.assertIn('"search": self.custom_search', inspect.getsource(mon.Monitor.glt_target))

    def test_tools_menu_groups(self):
        src = inspect.getsource(mon.Monitor)
        for sub in ('addMenu("Scanner")', 'addMenu("Alerts")', 'addMenu("Maps")', 'addMenu("Macro Keypad")'):
            self.assertIn("tools_menu." + sub, src)
        self.assertIn('tools_menu.addAction("Custom Search…"', src)


if __name__ == "__main__":
    unittest.main()

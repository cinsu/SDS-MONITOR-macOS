# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""1.1.83: SAME group names in Modes → Weather, and Weather Alert Priority."""
import time
import unittest
import xml.etree.ElementTree as ET

from support import mon, monitor


def wx(same):
    return ET.fromstring(f'<ScannerInfo Mode="WX Alert" V_Screen="wx_alert"><WxMode Mode="Weather Alert" '
                         f'SAME="{same}"/><WxChannel Name="GRVL" Freq=" 162.550000MHz" CH_No="1"/>'
                         '<Property Mute="Mute"/></ScannerInfo>')


WX_MENU = ('<MSI Name="Weather Operation" Index="1" MenuType="TypeSelect" Value="" Selected="0">'
           '<MenuItem Name="Weather Scan" Index="0" Value=""/>'
           '<MenuItem Name="Weather Alert Priority" Index="1" Value="Off"/>'
           '<MenuItem Name="Weather Alert" Index="2" Value=""/><Footer No="1" EOT="1"/></MSI>')
ON_OFF = ('<MSI Name="Weather Alert Priority" Index="2" MenuType="TypeSelect" Value="Off" Selected="0">'
          '<MenuItem Name="Off" Index="0"/><MenuItem Name="On" Index="1"/><Footer No="1" EOT="1"/></MSI>')


class SameNameTests(unittest.TestCase):
    def setUp(self):
        self.w = w = monitor(fresh=True)
        self.sent = []
        w.queue = lambda c: self.sent.append(c) or True
        w.connected = True
        self.m = w.modes_window

    def run_group(self, key, same):
        self.m.start_wx(key)
        self.m.same_started -= 5          # past the moment old reports can still arrive
        self.m.gsi(wx(same), False)

    def test_name_is_learned_and_shown(self):
        self.run_group("SAME_1", "GRVL")
        self.assertEqual(mon.same_names(self.w.settings), {1: "GRVL"})
        self.assertEqual(mon.same_label(self.w.settings, "SAME_1", "SAME 1"), "SAME 1 – GRVL")
        texts = {}
        for key, action in self.w.wx_mode_actions.items():
            action.setText = lambda t, k=key: texts.__setitem__(k, t)
        self.w.weather_menu_shown()
        self.assertEqual(texts["SAME_1"], "Weather Alert: Same 1 – GRVL")
        self.assertEqual(texts["SAME_2"], "Weather Alert: Same 2")

    def test_placeholder_is_not_a_name(self):
        self.run_group("SAME_2", "SAME 2")
        self.assertEqual(mon.same_names(self.w.settings), {})

    def test_report_from_before_the_change_is_not_used(self):
        self.m.start_wx("SAME_3")
        self.m.gsi(wx("GRVL"), False)     # straight away: could be the old mode
        self.assertEqual(mon.same_names(self.w.settings), {})

    def test_another_groups_name_is_not_copied(self):
        self.run_group("SAME_1", "GRVL")
        self.run_group("SAME_2", "GRVL")
        self.assertEqual(mon.same_names(self.w.settings), {1: "GRVL"})
        self.m.gsi(wx("PICK"), False)
        self.assertEqual(mon.same_names(self.w.settings), {1: "GRVL", 2: "PICK"})

    def test_typed_name_is_kept(self):
        mon.set_same_name(self.w.settings, 1, "Greenville Co.", typed=True)
        self.run_group("SAME_1", "GRVL")
        self.assertEqual(mon.same_names(self.w.settings)[1], "Greenville Co.")
        mon.set_same_name(self.w.settings, 1, "", typed=True)   # cleared: learned again
        self.run_group("SAME_1", "GRVL")
        self.assertEqual(mon.same_names(self.w.settings)[1], "GRVL")

    def test_not_started_here_is_not_learned(self):
        self.m.gsi(wx("GRVL"), False)
        self.assertEqual(mon.same_names(self.w.settings), {})


class PriorityTests(unittest.TestCase):
    def setUp(self):
        self.w = w = monitor(fresh=True)
        self.sent = []
        w.queue = lambda c: self.sent.append(c) or True
        w.connected = True
        self.p = w.wx_priority

    def test_turn_on_through_the_weather_menu(self):
        self.p.set("on")
        self.assertEqual(self.sent[-1], "MNU,WX,")
        self.assertTrue(self.p.route("REPLY: MNU,OK"))
        self.assertEqual(self.sent[-1], "MSI")
        self.p.handle_xml(WX_MENU)
        self.assertTrue(self.sent[-1].startswith("MSV,") and self.sent[-1].endswith(",1"), self.sent)
        self.p.route("REPLY: MSV,OK")
        self.p.handle_xml(ON_OFF)
        self.assertTrue(self.sent[-1].endswith(",1"), self.sent)      # "On"
        self.p.route("REPLY: MSV,OK")
        self.assertTrue(self.sent[-1].startswith("MSB,"), self.sent)
        self.p.route("REPLY: MSB,OK")
        self.assertFalse(self.p.busy)
        self.assertEqual(self.p.state, "on")
        checked = []
        self.w.wx_pri_action.setChecked = checked.append
        self.w.weather_menu_shown()
        self.assertEqual(checked, [True])

    def test_check_reads_the_value_without_changing_it(self):
        self.p.check()
        self.p.route("REPLY: MNU,OK")
        self.p.handle_xml(WX_MENU)
        self.assertTrue(self.sent[-1].startswith("MSB,"), self.sent)
        self.assertFalse(any(c.startswith("MSV") for c in self.sent), self.sent)
        self.p.route("REPLY: MSB,OK")
        self.assertEqual(self.p.state, "off")

    def test_missing_item_fails_cleanly(self):
        self.p.check()
        self.p.route("REPLY: MNU,OK")
        self.p.handle_xml('<MSI Name="Weather Operation"><MenuItem Name="Weather Scan" Index="0"/></MSI>')
        self.assertFalse(self.p.busy)
        self.assertIn("Couldn't find", self.p.message[0])


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Scanner Menu: long menus that the SDS100 sends in parts (Select Lists to Monitor, v1.1.59)."""
import unittest

from support import mon, monitor

# A real SDS100 reply to one MSI: 30 entries in two parts, 3 ms apart.
PART1 = '<MSI Name="Select Lists to Monitor" Index="4293074200" MenuType="TypeSelect" Value="Full Database       :Off" Selected="0" >   <MenuItem Name="Full Database" Index="0" Value="Off" />   <MenuItem Name="Search with Scan" Index="1" Value="Off" />   <MenuItem Name="Greenville County" Index="2" Value="Off" />   <MenuItem Name="SC Highway Patrol" Index="3" Value="Off" />   <MenuItem Name="SC State Misc." Index="4" Value="Off" />   <MenuItem Name="Military" Index="5" Value="Off" />   <MenuItem Name="Amateur Radio" Index="6" Value="Off" />   <MenuItem Name="Aviation" Index="7" Value="On" />   <MenuItem Name="CB/FSB/GMRS" Index="8" Value="Off" />   <MenuItem Name="Federal Law Enforcement" Index="9" Value="Off" />   <MenuItem Name="Disaster Operations" Index="10" Value="Off" />   <MenuItem Name="Rail" Index="11" Value="Off" />   <MenuItem Name="Spartanburg County" Index="12" Value="Off" />   <MenuItem Name="Pickens County" Index="13" Value="Off" />   <MenuItem Name="Anderson County" Index="14" Value="Off" />   <MenuItem Name="Oconee County" Index="15" Value="Off" />   <MenuItem Name="NC - Henderson County" Index="16" Value="Off" />   <MenuItem Name="NC-Polk County" Index="17" Value="Off" />   <Footer No="1" EOT="0"/> </MSI>'
PART2 = '<MSI Name="Select Lists to Monitor" Index="4293074200" MenuType="TypeSelect" Value="Full Database       :Off" Selected="0" >   <MenuItem Name="NC-Transylvania County" Index="18" Value="Off" />   <MenuItem Name="NC Viper - Federal Law Enforcement Statewide" Index="19" Value="Off" />   <MenuItem Name="NC Viper - Federal Military Statewide" Index="20" Value="Off" />   <MenuItem Name="NC Viper - Emergency Managment Statewide" Index="21" Value="Off" />   <MenuItem Name="NC Viper - Forest Service Statewide" Index="22" Value="Off" />   <MenuItem Name="NC Viper - NCDOT Statewide" Index="23" Value="Off" />   <MenuItem Name="NC Viper - NCSHP Statewide" Index="24" Value="Off" />   <MenuItem Name="NC Viper - NCNG Statewide" Index="25" Value="Off" />   <MenuItem Name="NC Viper - NC State Law Enforcement Statewide" Index="26" Value="Off" />   <MenuItem Name="NC Amateur Radio" Index="27" Value="Off" />   <MenuItem Name="Prisma Health DMR" Index="28" Value="Off" />   <MenuItem Name="Greenville Businesses" Index="29" Value="Off" />   <Footer No="2" EOT="1"/> </MSI>'
ERROR = '<MSI MenuType="TypeError" >   <Footer No="1" EOT="1"/> </MSI>'


class MenuPartsTests(unittest.TestCase):
    def setUp(self):
        self.w = monitor(fresh=True)
        self.shown = []
        self.w.scanner_menu.handle_xml = self.shown.append
        self.w.close_call.handle_xml = lambda xml: None

    def test_footer(self):
        self.assertEqual(mon.menu_footer(PART1), (1, False))
        self.assertEqual(mon.menu_footer(PART2), (2, True))
        self.assertEqual(mon.menu_footer("<MSI/>"), (1, True))
        self.assertEqual(mon.menu_footer("not xml"), (1, True))

    def test_merged_menu_has_every_list(self):
        menu = mon.parse_menu(mon.merge_menu_parts([PART1, PART2]))
        names = [i["name"] for i in menu["items"]]
        self.assertEqual(len(names), 30)
        self.assertEqual(names[0], "Full Database")
        self.assertEqual(names[17], "NC-Polk County")
        self.assertEqual(names[18], "NC-Transylvania County")
        self.assertEqual(names[-1], "Greenville Businesses")
        self.assertEqual([i["index"] for i in menu["items"]], [str(n) for n in range(30)])
        self.assertEqual(menu["name"], "Select Lists to Monitor")
        self.assertEqual([i["name"] for i in menu["items"] if i["value"] == "On"], ["Aviation"])

    def test_monitor_waits_for_the_last_part(self):
        self.w.handle_menu_xml(PART1)
        self.assertEqual(self.shown, [])
        self.w.handle_menu_xml(PART2)
        self.assertEqual(len(self.shown), 1)
        self.assertEqual(len(mon.parse_menu(self.shown[0])["items"]), 30)

    def test_single_part_menus_pass_straight_through(self):
        self.w.handle_menu_xml(ERROR)
        self.assertEqual(self.shown, [ERROR])

    def test_a_new_first_part_starts_over(self):
        self.w.handle_menu_xml(PART1)
        self.w.handle_menu_xml(PART1)
        self.w.handle_menu_xml(PART2)
        self.assertEqual(len(mon.parse_menu(self.shown[-1])["items"]), 30)

    def test_a_missing_last_part_still_shows_what_came(self):
        self.w.handle_menu_xml(PART1)
        self.w.flush_menu_parts()
        self.assertEqual(len(mon.parse_menu(self.shown[-1])["items"]), 18)

    def test_the_window_lists_all_thirty(self):
        win = mon.ScannerMenuWindow(self.w)
        win.handle_xml(mon.merge_menu_parts([PART1, PART2]))
        self.assertEqual(len(win.menu["items"]), 30)
        self.assertEqual(win.menu["items"][-1]["name"], "Greenville Businesses")

    def test_a_switched_list_shows_its_new_value(self):
        """SELECT switches a list On or Off; the reply has the same entries with a new value."""
        class Items:
            def __init__(self):
                self.rows, self.current = [], -1
            def clear(self):
                self.rows = []
            def addItem(self, entry):
                self.rows.append(entry)
            def currentRow(self):
                return self.current
            def setCurrentRow(self, row):
                self.current = row
            def verticalScrollBar(self):
                class Bar:
                    def value(self):
                        return 0
                    def setValue(self, _v):
                        pass
                return Bar()
        texts = []
        real_item = mon.QListWidgetItem
        mon.QListWidgetItem = lambda text: texts.append(text) or type(
            "E", (), {"setForeground": lambda self, c: None})()
        try:
            win = mon.ScannerMenuWindow(self.w)
            win.items = Items()
            win.handle_xml(mon.merge_menu_parts([PART1, PART2]))
            win.items.setCurrentRow(22)
            texts.clear()
            win.handle_xml(mon.merge_menu_parts([PART1, PART2.replace(
                'Forest Service Statewide" Index="22" Value="Off"',
                'Forest Service Statewide" Index="22" Value="On"')]))
        finally:
            mon.QListWidgetItem = real_item
        self.assertEqual(len(texts), 30)
        self.assertTrue(texts[22].endswith("—  On"), texts[22])
        self.assertEqual(win.items.current, 22)

    def test_exit_menu_closes_the_window_once_the_scanner_has_left(self):
        win = mon.ScannerMenuWindow(self.w)
        sent, closed = [], []
        self.w.queue = lambda c: sent.append(c) or True
        win.close = lambda: closed.append(True)
        win.rsv = ""
        win.exit_menu()
        self.assertEqual(sent, ["MSB,,RETURN_PREVOUS_MODE"])
        win.route("REPLY: MSB,NG")                   # the first spelling refused: retried, still open
        self.assertEqual(sent[-1], "MSB,0,RETURN_PREVOUS_MODE")
        self.assertEqual(closed, [])
        win.route("REPLY: MSB,OK")
        self.assertEqual(closed, [True])

    def test_back_keeps_the_window_open(self):
        win = mon.ScannerMenuWindow(self.w)
        closed = []
        self.w.queue = lambda c: True
        win.close = lambda: closed.append(True)
        win.rsv = ""
        win.back()
        win.route("REPLY: MSB,OK")
        self.assertEqual(closed, [])


if __name__ == "__main__":
    unittest.main()

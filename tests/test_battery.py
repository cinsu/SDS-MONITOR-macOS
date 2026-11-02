# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Battery status: GCS first, then the voltage on the scanner's screen (GST) when GCS is refused."""
import unittest

from support import mon, monitor

GST = ("REPLY: GST,00001010100000000,              Nov.1  1:40 ..  ,,F0:012345678- P25             ,,"
       "S0:01--------   VOL: 7 SQL: 2 ,,D0:0---------   Tag:--.--.--- ,,Palmetto 800            ,,"
       "Greenville County             ,,Greenville County       ,,Greenville County Simulc    ,,"
       "Ops 51 (GFD)            ,,TGID:44353                    ,,Fire-Tac        P25 NAC:1DBh  ,,"
       "Sys ID: 1D9h     859.262500MHz,,RFSS ID: 2      Site ID: 23   ,,WACN: BEE00h    Batt:4.21V    ,,"
       "UID:3238410     RSSI: -52dBm  ,,N                           ,, SYSTEM      DEPT     CHANNEL ,"
       "********* ********** *********,0,OFF,3,,,,,,,,,")


class BatteryTests(unittest.TestCase):
    def setUp(self):
        self.w = w = monitor(fresh=True)
        self.shown = {}
        self.saved = mon.set_text
        mon.set_text = lambda widget, text: self.shown.__setitem__("label", text) if widget is w.battery_label else None
        w.battery_label.setToolTip = lambda tip: self.shown.__setitem__("tip", tip)
        self.sent = []
        w.queue = lambda c: self.sent.append(c) or True
        w.connected, w.thread = True, None
        w.gcs_failures, w.screen_battery = 0, None

    def tearDown(self):
        mon.set_text = self.saved

    def test_gcs_refused_twice_then_reads_the_screen(self):
        w = self.w
        w.poll_battery()
        self.assertEqual(self.sent, ["GCS"])
        for _ in range(2):
            w.route_reply("SENT: GCS")
            self.assertTrue(w.route_reply("REPLY: ERR"))
        self.sent.clear()
        w.poll_battery()
        self.assertEqual(self.sent, ["GST"])
        self.assertTrue(w.route_reply("SENT: GST"))          # not shown in the console
        self.assertTrue(w.route_reply(GST))
        self.assertEqual(self.shown["label"], "Battery 4.21 V ≈ 100%")
        self.assertIn("estimate", self.shown["tip"])

    def test_voltage_to_percent(self):
        w = self.w
        w.gcs_failures = 5
        for volts, label in ((4.05, "84%"), (3.85, "56%"), (3.62, "13%"), (3.30, "0%")):
            w.route_reply(GST.replace("4.21V", f"{volts:.2f}V"))
            self.assertTrue(self.shown["label"].endswith(label), (volts, self.shown["label"]))

    def test_screen_without_battery_keeps_the_last_reading(self):
        w = self.w
        w.gcs_failures = 5                        # GCS already refused
        w.route_reply(GST)
        w.route_reply(GST.replace("Batt:4.21V", "          "))
        self.assertEqual(self.shown["label"], "Battery 4.21 V ≈ 100%")


if __name__ == "__main__":
    unittest.main()

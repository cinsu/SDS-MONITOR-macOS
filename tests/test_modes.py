# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Weather and Tone-Out: alerts from the scanner's status reports, and the mode commands."""
import csv
import unittest
import xml.etree.ElementTree as ET

from support import mon, monitor

TONE = ('<ScannerInfo Mode="Tone-Out" V_Screen="tone_out"><ToneOutChannel Name="Station 5" Index="1" '
        'CH_No="0" Freq=" 154.430000MHz" ToneA="1135.5Hz" ToneB="832.5Hz"/><Property Mute="Mute"/></ScannerInfo>')
WX = ('<ScannerInfo Mode="WX Alert" V_Screen="wx_alert"><WxMode Mode="Weather Alert" SAME="SAME 1"/>'
      '<WxChannel Name="NWS Greenville" Freq=" 162.550000MHz" CH_No="1"/><Property Mute="Mute"/>'
      '<ViewDescription><OverWrite Text="Weather Alert"/></ViewDescription></ScannerInfo>')


class ModesTests(unittest.TestCase):
    def setUp(self):
        self.w = w = monitor(fresh=True)
        self.notes, self.sent = [], []
        w.notify = lambda title, text, cat="alert": self.notes.append((cat, title, text))
        w.queue = lambda c: self.sent.append(c) or True
        w.connected = True
        if w.modes_window is None:
            w.modes_window = mon.ScannerModesWindow(w)
        self.m = m = w.modes_window
        m.tone_alert_box.setChecked(True)
        m.wx_alert_box.setChecked(True)

    def test_tone_out_alerts_once_per_cooldown_and_is_logged(self):
        tone = ET.fromstring(TONE)
        self.m.gsi(tone, False)
        self.assertEqual(self.notes, [])
        self.m.gsi(tone, True)
        self.m.gsi(tone, True)
        self.m.gsi(tone, False)
        self.m.gsi(tone, True)
        alerts = [n for n in self.notes if "Station 5" in n[1] + n[2]]
        self.assertEqual(len(alerts), 1, self.notes)
        logs = list(mon.MODE_ALERT_DIR.glob("mode_alerts_*.csv"))
        self.assertEqual(len(logs), 1)
        with logs[0].open(encoding="utf-8") as f:
            rows = list(csv.reader(f))
        self.assertTrue(any(r[1] == "Tone-Out" and r[2] == "Station 5" for r in rows[1:]), rows)

    def test_weather_alert_only_when_the_scanner_shows_one(self):
        wx = ET.fromstring(WX)
        self.m.gsi(wx, False)
        self.assertEqual(self.notes, [])
        alert = ET.fromstring(WX)
        alert.find("ViewDescription").append(ET.fromstring('<PopupScreen Text="TORNADO WARNING"/>'))
        self.m.gsi(alert, True)
        self.assertTrue(any("TORNADO WARNING" in n[1] + n[2] for n in self.notes), self.notes)

    def test_the_alert_method_does_not_replace_qt_event_handling(self):
        self.assertFalse("event" in vars(mon.ScannerModesWindow),
                         "ScannerModesWindow.event would replace Qt's event handler")

    def test_mode_commands(self):
        self.m.start_wx("SAME_2")
        self.assertTrue(any(c.startswith("JPM") for c in self.sent), self.sent)
        self.sent.clear()
        self.m.start_tone_out()
        self.assertTrue(any(c.startswith("JPM") for c in self.sent), self.sent)


if __name__ == "__main__":
    unittest.main()

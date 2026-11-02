# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Reception history: a transmission seen in status reports is written to the day's CSV file.
Also the transcript files the Transcription window reads."""
import time
import unittest
from datetime import datetime

from support import mon, monitor


def report(channel, mute="Unmute", tgid="44353", rssi="-52"):
    return (f'<ScannerInfo Mode="Trunk Scan" V_Screen="trunk_scan"><System Name="Palmetto 800" Index="1"/>'
            f'<Department Name="Greenville County" Index="2"/><Site Name="Greenville Simulcast" Index="3"/>'
            f'<TGID Name="{channel}" Index="4" TGID="TGID:{tgid}" UID="UID:3238410" Mod="NFM" '
            f'SvcType="Fire Dispatch" Freq=" 859.262500MHz"/>'
            f'<Property Mute="{mute}" Rssi="{rssi}" Sig="4" Att="Off" Rec="Off" Key_Lock="Off" P25Status="None"/>'
            f'</ScannerInfo>')


class ReceptionLogTests(unittest.TestCase):
    def test_a_transmission_is_logged_once_with_its_details(self):
        w = monitor(fresh=True)
        w.check_alerts = lambda *a, **k: False
        today = datetime.now().strftime("%Y-%m-%d")
        before = len(mon.read_reception_day(today))
        w.process_xml(report("Ops 51 (GFD)"))
        w.process_xml(report("Ops 51 (GFD)"))
        self.assertIsNotNone(w.reception)
        w.process_xml(report("Ops 51 (GFD)", mute="Mute"))
        rows = mon.read_reception_day(today)
        self.assertEqual(len(rows), before + 1)
        row = rows[-1]
        self.assertEqual(row[3:6], ["Palmetto 800", "Greenville County", "Ops 51 (GFD)"])
        self.assertIn("859.2625", row[6])
        self.assertIn("44353", row[7])
        self.assertEqual(w.last_heard["Channel"], "Ops 51 (GFD)")

    def test_a_channel_change_starts_a_new_reception(self):
        w = monitor(fresh=True)
        w.check_alerts = lambda *a, **k: False
        today = datetime.now().strftime("%Y-%m-%d")
        before = len(mon.read_reception_day(today))
        w.process_xml(report("Ops 51 (GFD)"))
        w.process_xml(report("Fire Dispatch", tgid="44002"))
        w.process_xml(report("Fire Dispatch", tgid="44002", mute="Mute"))
        self.assertEqual(len(mon.read_reception_day(today)), before + 2)

    def test_damaged_history_files_are_skipped(self):
        path = mon.daily_log_path(datetime(2020, 1, 2))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not,the,right,header\n1,2,3\n")
        self.assertEqual(mon.read_reception_day("2020-01-02"), [])
        self.assertEqual(mon.read_reception_day("not a date"), [])


class TranscriptFileTests(unittest.TestCase):
    def test_save_and_read_back(self):
        audio = ["2026-10-30 10:00:00", "2026-10-30 10:00:09", "9.0", "Palmetto 800", "Greenville County",
                 "Ops 51", " 859.262500MHz", "TGID:44353", "Simulcast", "UID:1", "NFM", "-52", "8.7",
                 "100000_Ops_51.mp3"]
        row = mon.make_transcript_row(audio, "Engine 12 10-23", "small.en")
        mon.save_transcript(row)
        got = mon.read_transcripts("2026-10-30")
        self.assertEqual(got["100000_Ops_51.mp3"][8], "Engine 12 10-23")
        row2 = list(row)
        row2[8] = "Engine 12 10-23 corrected"
        mon.save_transcript(row2)
        self.assertEqual(mon.read_transcripts("2026-10-30")["100000_Ops_51.mp3"][8], "Engine 12 10-23 corrected")
        self.assertEqual(mon.read_transcripts("1999-01-01"), {})


if __name__ == "__main__":
    unittest.main()

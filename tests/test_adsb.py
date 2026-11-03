# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Aircraft from readsb: reading aircraft.json, emergency and watch alerts, spoken callsigns and matching."""
import csv
import json
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

from support import mon, monitor

HOME = (34.85, -82.39)                       # the receiver


def aircraft(hex_id, flight="", reg="", typ="", squawk="1200", alt=4000, gs=210, lat=34.95, lon=-82.30,
             seen=0.5, emergency="none"):
    return {"hex": hex_id, "type": "adsb_icao", "flight": f"{flight:<8}" if flight else None, "r": reg, "t": typ,
            "alt_baro": alt, "gs": gs, "track": 45.0, "squawk": squawk, "emergency": emergency, "lat": lat,
            "lon": lon, "seen": seen, "seen_pos": seen, "rssi": -20.0, "messages": 100}


def doc(*planes, now=None):
    return json.dumps({"now": now or time.time(), "messages": 12345, "aircraft": list(planes)})


RECEIVER = json.dumps({"version": "readsb", "refresh": 1000, "history": 120, "lat": HOME[0], "lon": HOME[1]})


class Helpers(unittest.TestCase):
    def test_airband_and_compass(self):
        self.assertTrue(mon.is_airband(" 120.750000MHz"))
        self.assertTrue(mon.is_airband("251.0"))
        self.assertFalse(mon.is_airband(" 859.262500MHz"))
        self.assertFalse(mon.is_airband(""))
        self.assertEqual(mon.compass(34.85, -82.39, 35.85, -82.39), "N")
        self.assertEqual(mon.compass(34.85, -82.39, 34.95, -82.27), "NE")

    def test_parse(self):
        got = mon.parse_aircraft_json(doc(aircraft("A1B2C3", "DAL1234", "N123DL", "A321", seen=2.0), now=1000.0))
        seen, a = got[0]
        self.assertEqual((seen, a["hex"], a["flight"], a["r"]), (998.0, "a1b2c3", "DAL1234", "N123DL"))
        self.assertEqual(mon.parse_aircraft_json('{"aircraft": [{"nohex": 1}, 5]}'), [])
        with self.assertRaises(ValueError):
            mon.parse_aircraft_json("not json")


class SpokenCallsigns(unittest.TestCase):
    def values(self, text):
        return [(c["kind"], c["value"]) for c in mon.spoken_callsigns(text)]

    def test_airlines(self):
        self.assertEqual(self.values("Delta twelve thirty-four, descend and maintain 4000"), [("airline", "DAL1234")])
        self.assertEqual(self.values("Southwest 2 2 1 1 contact approach"), [("airline", "SWA2211")])
        self.assertEqual(self.values("American four seventy heavy"), [("airline", "AAL470")])
        self.assertEqual(self.values("FedEx 1 2-34"), [("airline", "FDX1234")])
        self.assertEqual(self.values("Blue Streak fifty one oh two"), [("airline", "JIA5102")])
        self.assertEqual(self.values("United two thousand"), [("airline", "UAL2000")])
        self.assertEqual(self.values("Delta 0045"), [("airline", "DAL45")])

    def test_general_aviation(self):
        self.assertEqual(self.values("November one two three alpha bravo, runway two two"),
                         [("registration", "N123AB")])
        self.assertEqual(self.values("Cessna four five alpha, traffic"), [("suffix", "45A")])
        self.assertEqual(self.values("Cirrus 7 3 7 tango romeo"), [("suffix", "737TR")])
        self.assertEqual(self.values("cessna, say again"), [])
        self.assertEqual(self.values("N123AB cleared to land"), [("registration", "N123AB")])
        self.assertEqual(self.values("November 123AB"), [("registration", "N123AB")])

    def test_not_callsigns(self):
        self.assertEqual(self.values("climb and maintain one zero thousand, the delta wing"), [])
        self.assertEqual(self.values("Delta Delta twelve 34"), [("airline", "DAL1234")])
        self.assertEqual(len(self.values("Delta 12 34 ... Delta 12 34")), 1)


class Matching(unittest.TestCase):
    planes = [{"hex": "a1", "flight": "DAL1234", "r": "N123DL", "t": "A321"},
              {"hex": "a2", "flight": "N123AB", "r": "N123AB", "t": "C172"},
              {"hex": "a3", "flight": "", "r": "N9845A", "t": "C182"},
              {"hex": "a4", "flight": "SWA0045", "r": "N7716A", "t": "B737"}]

    def test_matches(self):
        said = mon.spoken_callsigns("Delta 1234 and November 123AB and Cessna 4 5 alpha and Southwest 45 and United 9")
        got = {(s["value"], a["hex"] if a else None, how) for s, a, how in mon.match_callsigns(said, self.planes)}
        self.assertEqual(got, {("DAL1234", "a1", "callsign"), ("N123AB", "a2", "registration"),
                               ("45A", "a3", "end of registration (only match in range)"),
                               ("SWA45", "a4", "callsign"), ("UAL9", None, "not seen by ADS-B")})

    def test_ambiguous_suffix_is_not_guessed(self):
        planes = self.planes + [{"hex": "a5", "flight": "", "r": "N1145A", "t": "PA28"}]
        (s, a, how), = mon.match_callsigns(mon.spoken_callsigns("Cessna four five alpha"), planes)
        self.assertIsNone(a)
        self.assertIn("2 aircraft", how)


class FeedTests(unittest.TestCase):
    def setUp(self):
        self.w = monitor(fresh=True)
        self.feed = self.w.adsb
        self.notes = []
        self.w.notify = lambda title, text, cat="alert": self.notes.append((cat, title, text))
        self.w.settings.setValue("adsb/enabled", "true")

    def test_receiver_position_and_distance(self):
        self.feed.ingest(doc(aircraft("a1", "DAL1234", lat=34.95, lon=-82.27)), RECEIVER)
        self.assertEqual(self.feed.receiver, HOME)
        self.assertEqual(self.feed.where(self.feed.current["a1"][1]), "10 mi NE")
        self.assertEqual(self.feed.status, "ok")

    def test_emergency_squawk_alerts_once_per_half_hour(self):
        now = 1_000_000.0
        plane = aircraft("a7", "DAL1234", "N123DL", "A321", squawk="7700")
        self.feed.ingest(doc(plane, now=now), RECEIVER, now=now)
        self.feed.ingest(doc(plane, now=now + 5), now=now + 5)
        self.assertEqual(len(self.notes), 1)
        cat, title, text = self.notes[0]
        self.assertEqual((cat, title), ("aircraft", "Squawk 7700 (emergency)"))
        self.assertIn("DAL1234 N123DL A321", text)
        self.assertIn("4,000 ft", text)
        self.feed.ingest(doc(plane, now=now + 1900), now=now + 1900)
        self.assertEqual(len(self.notes), 2)
        log = mon.adsb_alert_path(datetime.fromtimestamp(now).strftime("%Y-%m-%d"))
        rows = mon.read_csv_rows(log, mon.ADSB_ALERT_HEADERS)
        self.assertEqual(rows[0][1:4], ["Squawk 7700 (emergency)", "a7", "DAL1234"])

    def test_emergency_field_distance_limit_and_off(self):
        now = 2_000_000.0
        self.feed.ingest(doc(aircraft("b1", emergency="lifeguard", squawk="1200"), now=now), RECEIVER, now=now)
        self.assertEqual(self.notes[-1][1], "Emergency: medical (lifeguard)")
        self.notes.clear()
        self.w.settings.setValue("adsb/alert_miles", "5")
        self.feed.ingest(doc(aircraft("b2", squawk="7600", lat=35.5), now=now), now=now)      # ~45 mi away
        self.assertEqual(self.notes, [])
        self.w.settings.setValue("adsb/alert_miles", "0")
        self.w.settings.setValue("adsb/emergency_alerts", "false")
        self.feed.ingest(doc(aircraft("b3", squawk="7500"), now=now), now=now)
        self.assertEqual(self.notes, [])

    def test_watch_list(self):
        now = 3_000_000.0
        self.w.settings.setValue("adsb/watch", "N911*\nrch*, A1B2C3\n")
        self.assertEqual(self.feed.watch_list(), ["N911*", "RCH*", "A1B2C3"])
        self.feed.ingest(doc(aircraft("c1", reg="N911LF"), aircraft("c2", "RCH871"), aircraft("a1b2c3"),
                             aircraft("c4", "DAL1"), now=now), RECEIVER, now=now)
        self.assertEqual(sorted(t for _c, t, _x in self.notes),
                         ["Watched aircraft (A1B2C3)", "Watched aircraft (N911*)", "Watched aircraft (RCH*)"])
        self.feed.ingest(doc(aircraft("c1", reg="N911LF"), now=now + 60), now=now + 60)
        self.assertEqual(len(self.notes), 3)                     # not again within two hours

    def test_old_aircraft_and_history_are_dropped(self):
        now = 4_000_000.0
        self.feed.ingest(doc(aircraft("d1", seen=120), aircraft("d2"), now=now), now=now)
        self.assertEqual(set(self.feed.current), {"d2"})
        self.feed.ingest(doc(aircraft("d3"), now=now + 4000), now=now + 4000)
        self.assertNotIn("d2", self.feed.tracks)

    def test_reads_the_file_readsb_writes(self):
        folder = Path(tempfile.mkdtemp())
        (folder / "aircraft.json").write_text(doc(aircraft("e1", "SWA2211")))
        (folder / "receiver.json").write_text(RECEIVER)
        with mock.patch.object(mon, "ADSB_SOURCES", [str(folder / "missing.json"), str(folder / "aircraft.json")]):
            self.w.settings.setValue("adsb/enabled", "auto")
            self.assertTrue(self.feed.enabled())
            self.assertEqual(self.feed.source(), ("file", str(folder / "aircraft.json")))
            self.feed.poll()
        self.assertIn("e1", self.feed.current)
        self.assertEqual(self.feed.receiver, HOME)
        with mock.patch.object(mon, "ADSB_SOURCES", [str(folder / "missing.json")]):
            self.assertFalse(self.feed.enabled())
            self.w.settings.setValue("adsb/source", "http://192.168.1.20/tar1090/data/aircraft.json")
            self.assertEqual(self.feed.source()[0], "url")

    def test_unreadable_file(self):
        folder = Path(tempfile.mkdtemp())
        (folder / "aircraft.json").write_text("{broken")
        self.w.settings.setValue("adsb/source", str(folder / "aircraft.json"))
        self.feed.poll()
        self.assertEqual(self.feed.status, "error")


class TranscriptTests(unittest.TestCase):
    def setUp(self):
        self.w = monitor(fresh=True)
        self.feed = self.w.adsb
        self.w.settings.setValue("adsb/enabled", "true")
        self.start = datetime.now().replace(microsecond=0)
        self.day = self.start.strftime("%Y-%m-%d")

    def recording(self, name, freq, text):
        stamp = self.start.strftime("%Y-%m-%d %H:%M:%S")
        audio = [stamp, stamp, "6.0", "Airband", "Approach", "GSP Approach", freq, "", "", "", "AM", "-60", "5.5", name]
        path = mon.audio_index_path(self.start)
        path.parent.mkdir(parents=True, exist_ok=True)
        fresh = not path.exists()
        with path.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if fresh:
                w.writerow(mon.AUDIO_HEADERS)
            w.writerow(audio)
        return audio, mon.make_transcript_row(audio, text, "small.en")

    def test_callsigns_matched_at_the_time_of_the_call(self):
        t = self.start.timestamp()
        self.feed.ingest(doc(aircraft("f1", "DAL1234", "N123DL", "A321", alt=6000, lat=34.95, lon=-82.27), now=t),
                         RECEIVER, now=t)
        audio, row = self.recording("call1.mp3", " 120.750000MHz",
                                    "Delta twelve thirty four descend and maintain four thousand, United 9 contact")
        rows = self.feed.transcript_added(row)
        self.assertEqual([(r[5], r[6], r[14]) for r in rows],
                         [("DAL1234", "f1", "callsign"), ("UAL9", "", "not seen by ADS-B")])
        line = mon.heard_line(rows[0])
        self.assertIn("DAL1234", line)
        self.assertIn("6,000 ft", line)
        self.assertIn("10 mi NE", line)
        self.assertIn("call1.mp3", mon.heard_by_file(self.day))
        tw = mon.TranscriptionWindow(self.w)
        tw.days.addItem(self.day)
        tw.days.setCurrentText(self.day)
        tw.load_day()
        self.assertIn("call1.mp3", tw.heard)

    def test_not_airband_or_too_old(self):
        _a, row = self.recording("call2.mp3", " 859.262500MHz", "Delta 1234")
        self.assertEqual(self.feed.transcript_added(row), [])
        self.w.settings.setValue("adsb/airband_only", "false")
        self.assertEqual(len(self.feed.transcript_added(row)), 1)
        old = list(row)
        old[0] = "2020-01-01 10:00:00"
        self.assertEqual(self.feed.transcript_added(old), [])
        self.w.settings.setValue("adsb/match", "false")
        self.assertEqual(self.feed.transcript_added(row), [])

    def test_window(self):
        self.feed.ingest(doc(aircraft("g1", "DAL1", squawk="7700")), RECEIVER)
        win = mon.AircraftWindow(self.w)
        win.refresh()
        self.assertIn("1 aircraft", win.status.text())
        win.watch.toPlainText = lambda: "N911*"
        win.save_watch()
        self.assertEqual(self.w.settings.value("adsb/watch"), "N911*")
        win.save()
        self.assertEqual(self.w.settings.value("adsb/source"), "auto")


if __name__ == "__main__":
    unittest.main()

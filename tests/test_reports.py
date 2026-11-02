# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Incident summaries and the daily report, from a made-up day of history files."""
import csv
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

from support import mon, monitor

DAY = "2026-10-20"
LOCAL = {"id": "local", "name": "Local", "source": "test", "enabled": True, "agencies": ["Greenville"],
         "area": None, "codes": [{"code": "10-50", "meaning": "Motor vehicle accident", "details": "B. Personal injury"},
                                 {"code": "10-8", "meaning": "In service", "details": ""},
                                 {"code": "10-23", "meaning": "Arrived on scene", "details": ""}]}


def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def make_day():
    """An accident on Fire Dispatch with Engine 12 and Medic 4, a quiet call, places, an alert."""
    base = datetime(2026, 10, 20, 14, 0, 0)
    calls = [  # (seconds after 14:00, length, channel, tgid, units, transcript)
        (0, 8, "Fire Dispatch", "44002", ["3100001"], "Engine 12 respond 10-50 B Wade Hampton at Pleasantburg"),
        (40, 5, "Fire Dispatch", "44002", ["3100001"], "Engine 12 10-8 en route"),
        (300, 6, "Ops 51 (GFD)", "44353", ["3100001", "3200004"], "Medic 4 <b>10-23</b>, two patients"),
        (420, 4, "Ops 51 (GFD)", "44353", ["3200004"], "Medic 4 transporting"),
        (7200, 3, "Public Works", "45000", ["3900009"], ""),
    ]
    receptions, units, transcripts = [], [], []
    for offset, length, channel, tg, uids, text in calls:
        start = base + timedelta(seconds=offset)
        end = start + timedelta(seconds=length)
        s, e = start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")
        receptions.append([s, e, f"{length:.1f}", "Palmetto 800", "Greenville County", channel,
                           " 859.262500MHz", f"TGID:{tg}", "-52"])
        for u in uids:
            units.append([(start + timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"), f"UID:{u}", "",
                          "Palmetto 800", "Simulcast", "Greenville County", channel, f"TGID:{tg}", "859.2625"])
        if text:
            transcripts.append([s, "Palmetto 800", "Greenville County", channel, f"TGID:{tg}",
                                "; ".join(f"UID:{u}" for u in uids), str(length), f"{offset}.mp3", text,
                                "small.en", s])
    write_csv(mon.daily_log_path(base), mon.HEADERS, receptions)
    write_csv(mon.unit_log_path(base), mon.UNIT_HEADERS, units)
    write_csv(mon.transcript_path(DAY), mon.TRANSCRIPT_HEADERS, transcripts)
    write_csv(mon.unit_log_path(base - timedelta(days=3)), mon.UNIT_HEADERS,
              [["2026-10-17 09:00:00", "UID:3100001", "", "Palmetto 800", "", "", "Fire Dispatch", "", ""]])
    place = ["", "Palmetto 800", "Greenville County", "Fire Dispatch", "TGID:44002", "UID:3100001",
             "Wade Hampton at Pleasantburg", "intersection", "34.8526", "-82.3940", "Wade Hampton Blvd",
             "found", "0.mp3", "…"]
    place[0] = receptions[0][0]
    write_csv(mon.places_path(DAY), mon.PLACE_HEADERS, [place])
    write_csv(mon.MODE_ALERT_DIR / f"mode_alerts_{DAY}.csv", mon.MODE_ALERT_HEADERS,
              [["2026-10-20 15:10:00", "Tone-Out", "Station 5", "154.4300", "1135.5/832.5 Hz", ""]])


def decoder():
    lists = mon.builtin_ten_code_lists("release") + [LOCAL]
    return lambda text, heard: mon.decode_ten_codes(text, mon.rank_ten_code_lists(lists, None, heard))


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        make_day()

    def test_routine_codes(self):
        self.assertTrue(mon.code_is_routine("In service"))
        self.assertTrue(mon.code_is_routine("Arrived on scene"))
        self.assertTrue(mon.code_is_routine("Affirmative (OK)"))
        self.assertFalse(mon.code_is_routine("Motor vehicle accident"))
        self.assertFalse(mon.code_is_routine("Shooting"))

    def test_report_data(self):
        data = mon.daily_report_data(DAY, decode=decoder())
        self.assertEqual(data["calls"], 5)
        self.assertEqual(data["hours"][14], 4)
        self.assertEqual(data["hours"][16], 1)
        self.assertEqual(data["busiest_hour"], 14)
        self.assertEqual(data["talkgroups"][0][1][0], 2)
        self.assertEqual(len(data["incidents"]), 1)
        inc = data["incidents"][0]
        self.assertEqual(len(inc["members"]), 4)
        headline = inc["summary"]["headline"]
        self.assertTrue(headline.startswith("10-50B Motor vehicle accident — B. Personal injury"), headline)
        self.assertIn("Wade Hampton at Pleasantburg", headline)
        self.assertIn("UID:3100001", headline)
        self.assertTrue(headline.endswith("7 min"), headline)
        self.assertEqual([c for c, _m, _n in inc["summary"]["codes"]], ["10-50B", "10-8", "10-23"])
        self.assertEqual(len(inc["summary"]["places"]), 1)
        self.assertEqual({c for c, _m, _n, _l in data["codes"]}, {"10-50B", "10-8", "10-23"})
        self.assertEqual({u for u, _t, _n in data["new_units"]}, {"3200004", "3900009"})   # 3100001 heard before
        self.assertTrue(data["had_history"])
        self.assertEqual(len(data["alerts"]), 1)

    def test_headline_without_codes_uses_what_was_said(self):
        data = mon.daily_report_data(DAY, decode=None)
        self.assertTrue(data["incidents"][0]["summary"]["headline"].startswith("“Engine 12 respond"))

    def test_html_is_complete_and_escaped(self):
        html = mon.daily_report_html(mon.daily_report_data(DAY, decode=decoder()), "1.2.3")
        for section in ("Summary", "Activity by hour", "Busiest talkgroups", "Incidents (1)", "Ten codes heard",
                        "Most active radios", "Radios not heard", "Places mentioned", "Weather and Tone-Out"):
            self.assertIn(section, html)
        self.assertIn("Tuesday, October 20, 2026", html)
        self.assertNotIn("<b>10-23</b>", html)                     # transcript text is never HTML
        self.assertIn("openstreetmap.org/?mlat=34.8526", html)
        self.assertTrue(html.rstrip().endswith("</html>"))

    def test_empty_day(self):
        html = mon.daily_report_html(mon.daily_report_data("2001-01-01"))
        self.assertIn("No receptions", html)

    def test_saving_html_and_automatic_reports(self):
        w = monitor(fresh=True)
        saver = w.report_saver
        due = lambda today: [d for d in saver.due(today=today) if d[0] == DAY]
        self.assertEqual(due("2026-10-25"), [])                        # off by default
        w.settings.setValue("report/auto_html", "true")
        self.assertEqual(due("2026-10-25"), [(DAY, ["html"])])
        self.assertEqual(due(DAY), [])                                 # not before the day is over
        for path in mon.REPORTS_DIR.glob("*") if mon.REPORTS_DIR.exists() else []:
            path.unlink()
        for day, _k in saver.due(today="2026-10-25"):                  # other tests' days: done already
            if day != DAY:
                mon.save_report_html("x", mon.report_path(day, "html"))
        with mock.patch.object(mon, "datetime", wraps=datetime) as fake:
            fake.now.return_value = datetime(2026, 10, 25, 9, 0)
            saver.check()
        self.assertTrue(mon.report_path(DAY, "html").exists())
        self.assertIn("Daily report", mon.report_path(DAY, "html").read_text())
        self.assertEqual(due("2026-10-25"), [])
        w.settings.setValue("report/auto_pdf", "true")
        for day, _k in saver.due(today="2026-10-25"):
            if day != DAY:
                mon.save_report_html("x", mon.report_path(day, "pdf"))
        with mock.patch.object(mon, "save_report_pdf") as pdf, \
                mock.patch.object(mon, "datetime", wraps=datetime) as fake:
            fake.now.return_value = datetime(2026, 10, 25, 9, 0)
            saver.check()
        self.assertEqual(Path(pdf.call_args[0][1]).name, f"daily_report_{DAY}.pdf")

    def test_windows(self):
        w = monitor(fresh=True)
        w.ten_codes.lists = mon.builtin_ten_code_lists("release") + [LOCAL]
        win = mon.DailyReportWindow(w)
        win.reload()
        win.days.setCurrentText(DAY)
        self.assertIn("Incidents (1)", win.html)
        inc_win = mon.IncidentsWindow(w)
        inc_win.reload()
        inc_win.days.setCurrentText(DAY)
        inc_win.recompute()
        self.assertEqual(len(inc_win.incidents), 1)
        inc_win.current = lambda: inc_win.incidents[0]
        inc_win.show_incident()
        self.assertIn("Motor vehicle accident", inc_win.detail.text())
        self.assertIn("Wade Hampton", inc_win.places_note.text())


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Ten codes: finding them in transcripts, choosing the list by agency and location, the files."""
import tempfile
import unittest
from pathlib import Path

from support import Settings, edition, mon, monitor

GREENVILLE = (34.85, -82.39)
COLUMBIA = (34.00, -81.03)
ATLANTA = (33.75, -84.39)
PERSONAL = edition() == "personal"


def keys(text):
    return [k for k, *_ in mon.find_ten_codes(text)]


class FindingCodes(unittest.TestCase):
    def test_written_and_spoken_forms(self):
        self.assertEqual(keys("Engine 4 is 10-23, 10-50 with injuries"), ["10-23", "10-50"])
        self.assertEqual(keys("ten four, ten-fifty, ten twenty-three"), ["10-4", "10-50", "10-23"])
        self.assertEqual(keys("go signal 4 now, signal twelve"), ["signal 4", "signal 12"])
        self.assertEqual(keys("10–7 and 10 8"), ["10-7", "10-8"])

    def test_sub_letters(self):
        f = mon.find_ten_codes
        self.assertEqual(f("10-50B on Main")[0][:2], ("10-50", "B"))
        self.assertEqual(f("10-50 B on Main")[0][:2], ("10-50", "B"))
        self.assertEqual(f("10-50 bravo")[0][:2], ("10-50", "B"))
        self.assertEqual(f("10-4 I copy")[0][:2], ("10-4", ""))
        self.assertEqual(f("10-8 a unit")[0][:2], ("10-8", ""))

    def test_numbers_that_are_not_codes(self):
        self.assertEqual(keys("1050 Main Street, $10 50 cents, 10.50, 10:50, 10,500"), [])

    def test_repeats_once(self):
        self.assertEqual(keys("10-4 10-4 10 4"), ["10-4"])

    def test_keys_and_order(self):
        self.assertEqual(mon.ten_code_key("10 - 50"), "10-50")
        self.assertEqual(mon.ten_code_key("Signal 04"), "signal 4")
        codes = ["Signal 2", "10-10", "10-2", "Code 3", "signal 10"]
        self.assertEqual(sorted(codes, key=mon.ten_code_sort_key), ["10-2", "10-10", "Signal 2", "signal 10", "Code 3"])


class ChoosingLists(unittest.TestCase):
    def test_editions(self):
        ids = [l["id"] for l in mon.builtin_ten_code_lists()]
        self.assertEqual(ids, ["apco-1974", "sc-highway-patrol", "greenville-sc"] if PERSONAL else ["apco-1974"])

    def test_apco_anywhere(self):
        r = mon.rank_ten_code_lists(mon.builtin_ten_code_lists(), ATLANTA, ())
        self.assertEqual(r[0][0]["id"], "apco-1974")
        self.assertEqual(mon.decode_ten_codes("10-33!", r)[0][2], "Help me quick")
        self.assertEqual(mon.decode_ten_codes("10-50", r), [])          # APCO stops at 10-34

    def test_own_list_by_agency_and_area(self):
        own = {"id": "x", "name": "Mine", "source": "", "enabled": True, "agencies": ["Pickens"],
               "area": {"lat": 34.88, "lon": -82.70, "range_mi": 20}, "codes": [{"code": "10-50", "meaning": "Wreck", "details": "B. Injuries"}]}
        lists = mon.builtin_ten_code_lists("release") + [own]
        heard = mon.rank_ten_code_lists(lists, ATLANTA, ("P800", "Pickens County Sheriff", "Disp"))
        self.assertEqual((heard[0][0]["id"], heard[0][1]), ("x", 0))
        near = mon.rank_ten_code_lists(lists, (34.88, -82.70), ())
        self.assertEqual((near[0][0]["id"], near[0][1]), ("x", 1))
        far = mon.rank_ten_code_lists(lists, ATLANTA, ())
        self.assertEqual([t for l, t, _ in far if l["id"] == "x"], [3])
        self.assertEqual(mon.decode_ten_codes("ten fifty bravo", heard)[0][1:3], ("10-50B", "Wreck \u2014 B. Injuries"))
        own["enabled"] = False
        self.assertNotIn("x", [l["id"] for l, *_ in mon.rank_ten_code_lists(lists, (34.88, -82.70), ())])

    def test_unknown_location(self):
        own = {"id": "x", "name": "Mine", "enabled": True, "agencies": [], "codes": [],
               "area": {"lat": 1, "lon": 1, "range_mi": 5}}
        r = mon.rank_ten_code_lists(mon.builtin_ten_code_lists("release") + [own], None, ())
        self.assertEqual([(l["id"], t) for l, t, _ in r], [("apco-1974", 2), ("x", 3)])



class Files(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def test_first_run_edit_delete_and_new_builtins(self):
        f = self.dir / "t.json"
        lists, removed = mon.load_ten_code_lists(f)
        builtin = [l["id"] for l in mon.builtin_ten_code_lists()]
        self.assertEqual([l["id"] for l in lists], builtin)
        lists[0]["codes"][0]["meaning"] = "edited"
        lists.append({"id": "mine", "name": "Mine", "codes": [{"code": "10-1", "meaning": "x"}]})
        mon.save_ten_code_lists(lists[:1] + lists[-1:], set(builtin[1:]), f)
        again, _ = mon.load_ten_code_lists(f)
        self.assertEqual([l["id"] for l in again], ["apco-1974", "mine"])                # deleted stays deleted
        self.assertEqual(again[0]["codes"][0]["meaning"], "edited")
        f.write_text('{"lists": [], "removed_builtins": []}')
        self.assertEqual([l["id"] for l in mon.load_ten_code_lists(f)[0]], builtin)        # a newer build adds lists

    def test_bad_files(self):
        f = self.dir / "t.json"
        f.write_text('{"lists": [{"name": ""}, 5, {"name": "x", "area": {"lat": 999, "lon": 0, "range_mi": 1},'
                     ' "codes": [{"code": ""}, {"code": "10-1", "meaning": "a"}]}]}')
        x = [l for l in mon.load_ten_code_lists(f, "release")[0] if l["name"] == "x"][0]
        self.assertIsNone(x["area"])
        self.assertEqual(len(x["codes"]), 1)
        f.write_text("not json")
        self.assertEqual(len(mon.load_ten_code_lists(f, "release")[0]), 1)

    def test_csv(self):
        c = self.dir / "c.csv"
        mon.write_ten_code_csv(c, [{"code": "10-1", "meaning": "a, b", "details": "B. x; C. y"}])
        self.assertEqual(mon.read_ten_code_csv(c), [{"code": "10-1", "meaning": "a, b", "details": "B. x; C. y"}])
        c.write_text("10-5,Enroute\n\n10-6\n")
        self.assertEqual([x["code"] for x in mon.read_ten_code_csv(c)], ["10-5", "10-6"])


class Windows(unittest.TestCase):
    def test_window_editor_and_transcription_decoding(self):
        mon.TEN_CODES_FILE = Path(tempfile.mkdtemp()) / "ten.json"
        w = monitor(fresh=True)
        own = {"id": "g", "name": "Local", "source": "test", "enabled": True, "agencies": ["Greenville"],
               "area": None, "codes": [{"code": "10-50", "meaning": "Wreck", "details": "C. Hit and run"}]}
        w.ten_codes.lists = mon.builtin_ten_code_lists("release") + [own]
        w.last_heard = {"System": "P800", "Department": "Greenville County Sheriff", "Channel": "Disp"}
        w.gps.last_fix, w.gps.scanner_location = None, GREENVILLE
        win = mon.TenCodesWindow(w)
        win.refresh()
        self.assertEqual(win.which.currentData(), "auto")
        rows = win.rows()
        ten50 = [l["id"] for c, l, best in rows if c["code"] == "10-50"]
        self.assertEqual(ten50, ["g"])                               # the agency heard has it
        self.assertEqual(len({mon.ten_code_key(c["code"]) for c, l, b in rows}), len(rows))
        win.which.setCurrentIndex(win.which.findData("applies"))
        self.assertEqual(len(win.rows()), len(rows) + 0)            # APCO has no 10-50, so no extra rows
        win.search.setText("wreck")
        win.fill()
        dialog = mon.TenCodeListsDialog(w)
        dialog.save()
        self.assertTrue(mon.TEN_CODES_FILE.exists())
        tw = mon.TranscriptionWindow(w)
        tw.decode_codes.setChecked(True)
        audio = ["2026-11-01 10:00:00", "", "", "P800", "Greenville County Sheriff", "Disp"] + [""] * 8
        self.assertEqual(tw.codes_for(audio, "ten fifty charlie")[0][1:3], ("10-50C", "Wreck \u2014 C. Hit and run"))
        tw.decode_codes.setChecked(False)
        self.assertEqual(tw.codes_for(audio, "ten fifty"), [])

    def test_location_sources(self):
        w = monitor(fresh=True)
        w.gps.last_fix, w.gps.scanner_location = None, None
        w.settings = Settings()
        self.assertEqual(w.ten_codes.position(), (None, ""))
        w.settings.setValue("tencodes/lat", "34.5")
        w.settings.setValue("tencodes/lon", "-82.5")
        self.assertEqual(w.ten_codes.position()[0], (34.5, -82.5))
        w.gps.scanner_location = GREENVILLE
        self.assertEqual(w.ten_codes.position(), (GREENVILLE, "scanner's location setting"))


if __name__ == "__main__":
    unittest.main()

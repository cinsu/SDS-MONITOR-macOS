# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Alerts, ignore lists, search, unit numbers, quiet hours and file names."""
import unittest

from support import mon


class AlertTests(unittest.TestCase):
    values = {"System": "Palmetto 800", "Department": "Greenville County", "Channel": "Ops 51 (GFD)",
              "Talkgroup": "TGID:44353", "Unit ID": "Engine 12 (UID:3238410)"}

    def test_contains_and_is(self):
        am = mon.alert_matches
        self.assertTrue(am({"field": "Channel", "text": "ops 51"}, self.values))
        self.assertFalse(am({"field": "Channel", "text": "ops 51", "match": "is"}, self.values))
        self.assertTrue(am({"field": "Channel", "text": "OPS 51 (GFD)", "match": "is"}, self.values))
        self.assertTrue(am({"field": "Any field", "text": "palmetto"}, self.values))
        self.assertFalse(am({"field": "Channel", "text": "ops 51", "enabled": False}, self.values))
        self.assertFalse(am({"field": "Channel", "text": "  "}, self.values))

    def test_unit_rules_match_by_number_after_naming(self):
        rule = {"field": "Unit ID", "text": "UID:3238410", "match": "is"}
        self.assertTrue(mon.alert_matches(rule, self.values))
        self.assertFalse(mon.alert_matches(rule, dict(self.values, **{"Unit ID": "UID:3238411"})))


class IgnoreAndSearchTests(unittest.TestCase):
    def test_ignore_list(self):
        wi = mon.watch_ignored
        self.assertTrue(wi(["44353"], "P800", "TGID:44353", "Ops 51"))
        self.assertTrue(wi(["TGID:44353"], "P800", "TGID:44353", "Ops 51"))
        self.assertFalse(wi(["4435"], "P800", "TGID:44353", "Ops 51"))             # IDs match exactly
        self.assertTrue(wi(["dispatch"], "P800", "TGID:1", "County Dispatch"))
        self.assertFalse(wi(["", "  "], "P800", "TGID:1", "County Dispatch"))

    def test_search_terms(self):
        terms = mon.search_terms('Engine 12 "structure fire"')
        self.assertEqual(terms, ["engine", "12", "structure fire"])
        self.assertTrue(mon.terms_match("engine 12 reports a structure fire", terms))
        self.assertFalse(mon.terms_match("engine 12 reports a fire in a structure", terms))


class SmallHelperTests(unittest.TestCase):
    def test_ids(self):
        self.assertEqual(mon.uid_key("Engine 12 (UID:3239937)"), "3239937")
        self.assertEqual(mon.uid_key("UID:3239937"), "3239937")
        self.assertEqual(mon.units_in("Engine 12 (UID:1); UID:2"), ["1", "2"])
        self.assertEqual(mon.plain_id("TGID:44002"), "44002")
        self.assertEqual(mon.plain_id("None"), "")

    def test_frequencies(self):
        self.assertEqual(mon.parse_mhz(" 162.550000MHz"), 162.55)
        self.assertIsNone(mon.parse_mhz("Weather"))

    def test_quiet_hours_wrap_past_midnight(self):
        q = mon.in_quiet_hours
        self.assertTrue(q(23, 22, 6) and q(5, 22, 6) and q(10, 8, 17))
        self.assertFalse(q(12, 22, 6))

    def test_safe_file_names(self):
        name = mon.safe_file_part('Ops 51 / GFD: "Tac"')
        self.assertNotRegex(name, r'[/:"\\]')
        self.assertLessEqual(len(mon.safe_file_part("x" * 500)), 60)


if __name__ == "__main__":
    unittest.main()

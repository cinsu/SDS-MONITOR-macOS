# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""GPS sentences, distances and when to tell the scanner where it is."""
import functools
import operator
import unittest

from support import mon


def nmea(body):
    return f"${body}*{functools.reduce(operator.xor, body.encode(), 0):02X}"


class GpsTests(unittest.TestCase):
    def test_rmc_and_gga(self):
        rmc = mon.parse_nmea(nmea("GPRMC,123519,A,3451.1560,N,08223.6400,W,010.0,084.4,011126,,"))
        self.assertTrue(rmc["valid"])
        self.assertAlmostEqual(rmc["lat"], 34.85260, places=4)
        self.assertAlmostEqual(rmc["lon"], -82.39400, places=4)
        self.assertAlmostEqual(rmc["speed_mph"], 11.5078, places=3)
        self.assertEqual(rmc["utc"], "2026-11-01 12:35:19")
        gga = mon.parse_nmea(nmea("GNGGA,123519,3451.1560,N,08223.6400,W,1,08,0.9,545.4,M,46.9,M,,"))
        self.assertTrue(gga["valid"])
        self.assertEqual(gga["sats"], 8)

    def test_bad_sentences(self):
        good = nmea("GPRMC,123519,A,3451.1560,N,08223.6400,W,010.0,084.4,011126,,")
        self.assertIsNone(mon.parse_nmea(good[:-1] + ("0" if good[-1] != "0" else "1")))   # checksum
        self.assertFalse((mon.parse_nmea(nmea("GPRMC,123519,V,,,,,,,011126,,")) or {"valid": False})["valid"])
        self.assertIsNone(mon.parse_nmea("garbage"))
        self.assertIsNone(mon.parse_nmea(""))

    def test_gpsd(self):
        fix = mon.parse_gpsd('{"class":"TPV","mode":3,"lat":34.85,"lon":-82.39,"speed":10}')
        self.assertTrue(fix["valid"])
        self.assertAlmostEqual(fix["speed_mph"], 22.3694, places=3)
        self.assertFalse(mon.parse_gpsd('{"class":"TPV","mode":1}')["valid"])
        self.assertIsNone(mon.parse_gpsd('{"class":"SKY"}'))
        self.assertIsNone(mon.parse_gpsd("not json"))

    def test_distance_and_scanner_format(self):
        self.assertAlmostEqual(mon.miles_between(34.85, -82.39, 34.00, -81.03), 97.2, places=1)
        self.assertEqual(mon.miles_between(1, 2, 1, 2), 0)
        self.assertEqual(mon.lcr_number_format("34.852600"), 6)
        self.assertEqual(mon.lcr_values(34.85261, -82.394, 5.0, [6, 6, 1]), ["34.852610", "-82.394000", "5.0"])

    def test_when_to_send_the_location(self):
        fix = {"valid": True, "lat": 34.85, "lon": -82.39}
        su = mon.should_update
        self.assertTrue(su(None, fix, 0, 0.5, 10, 300))
        self.assertFalse(su(None, {"valid": False}, 0, 0.5, 10, 300))
        self.assertFalse(su((34.0, -82.39, 0), fix, 5, 0.5, 10, 300))           # too soon
        self.assertTrue(su((34.0, -82.39, 0), fix, 20, 0.5, 10, 300))           # moved far
        self.assertFalse(su((34.85, -82.39, 0), fix, 400, 0.5, 10, 300))        # not moving
        self.assertTrue(su((34.851, -82.39, 0), fix, 400, 0.5, 10, 300))        # creeping (0.07 mi)
        self.assertFalse(su((34.8505, -82.39, 0), fix, 400, 0.5, 10, 300))      # GPS jitter (0.03 mi)


if __name__ == "__main__":
    unittest.main()

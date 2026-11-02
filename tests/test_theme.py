# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Themes: modes, accents, text sizes, KDE's light/dark scheme and live switching."""
import unittest
from pathlib import Path

from support import mon, monitor

CSS = "QWidget { background:#171b22; color:#e9eef5; font-size:14px; } QPushButton {background:#1b8a5a; color:white;}"


def channels(hexcolour):
    return tuple(int(hexcolour.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


class ThemeTests(unittest.TestCase):
    def tearDown(self):
        mon.THEME = mon.Theme("dark")

    def test_dark_blue_is_the_original_look(self):
        mon.THEME = mon.Theme("dark")
        self.assertIn("#171b22", mon.th(CSS))
        self.assertIn("font-size:14px", mon.th(CSS))

    def test_light_turns_background_light_and_text_dark(self):
        mon.THEME = mon.Theme("light")
        bg, fg = mon.THEME.colour("#171b22"), mon.THEME.colour("#e9eef5")
        self.assertGreater(sum(channels(bg)), 600)
        self.assertLess(sum(channels(fg)), 300)
        self.assertGreaterEqual(mon.contrast(mon._rgb(fg), mon._rgb(bg)), 4.5)

    def test_night_is_red_only(self):
        mon.THEME = mon.Theme("night")
        for key in ("#171b22", "#e9eef5", "#1b8a5a", "#7ee3a5", "#2167b1"):
            r, g, b = channels(mon.THEME.colour(key))
            self.assertGreaterEqual(r, max(g, b), key)

    def test_accents_and_sizes(self):
        blue, red = mon.Theme("dark", "blue"), mon.Theme("dark", "red")
        self.assertNotEqual(blue.colour("#2167b1"), red.colour("#2167b1"))
        large = mon.Theme("dark", size="large")
        mon.THEME = large
        self.assertNotIn("font-size:14px", mon.th(CSS))

    def test_bad_saved_values_fall_back(self):
        t = mon.Theme("purple?", "pink", "huge")
        self.assertEqual((t.mode, t.accent, t.size), ("dark", "blue", "normal"))

    def test_kde_scheme(self):
        config = Path.home() / ".config"
        config.mkdir(parents=True, exist_ok=True)
        kde = config / "kdeglobals"
        try:
            kde.write_text("[General]\nColorScheme=BreezeDark\n\n[Colors:Window]\nBackgroundNormal=32,35,38\n")
            self.assertTrue(mon.system_is_dark())
            kde.write_text("[Colors:Window]\nBackgroundNormal=239,240,241\n")
            self.assertFalse(mon.system_is_dark())
        finally:
            kde.unlink()
        self.assertEqual(mon.Theme("system", system_dark=False).mode, "light")

    def test_live_switching_from_the_menu(self):
        w = monitor(fresh=True)
        for group, key, expect in (("mode", "light", "light"), ("accent", "red", "light"),
                                   ("size", "large", "light"), ("mode", "night", "night")):
            w.set_theme_option(group, key)
            self.assertEqual(mon.THEME.mode, expect)
        self.assertEqual((mon.THEME.accent, mon.THEME.size), ("red", "large"))


if __name__ == "__main__":
    unittest.main()

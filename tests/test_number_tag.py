# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Go to Number Tag (v1.1.67): says that number tags are not quick keys, and opens Quick Keys."""
import unittest

from support import mon, monitor


class NumberTagTests(unittest.TestCase):
    def setUp(self):
        self.w = monitor(fresh=True)
        self.shown = []
        self.w.jnt_label = object()
        self._set_text = mon.set_text
        mon.set_text = lambda label, text: self.shown.append(text)

    def tearDown(self):
        mon.set_text = self._set_text

    def test_a_refusal_explains_number_tags_and_quick_keys(self):
        self.w.pending_jnt = "1/—/—"
        self.w.handle_jnt_reply("ERR")
        self.assertIn("nothing with number tag 1/—/— (ERR)", self.shown[-1])
        self.assertIn("quick key 1 is not number tag 1", self.shown[-1])
        self.w.pending_jnt = "1/2/3"
        self.w.handle_jnt_reply("OK")
        self.assertEqual(self.shown[-1], "✓ Scanner went to number tag 1/2/3.")

    def test_the_hint_names_both(self):
        self.assertIn("not the quick key", mon.Monitor.JNT_HINT)
        self.assertTrue(callable(mon.Monitor.open_quick_keys))


if __name__ == "__main__":
    unittest.main()

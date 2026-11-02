# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Checks on the source itself."""
import ast
import unittest

from support import PROGRAM, mon


class SourceTests(unittest.TestCase):
    def test_no_top_level_name_is_defined_twice(self):
        """v1.1.46 defined a second NUMBER_WORDS for ten codes, which silently replaced the call-sign
        table (so "Engine niner" was no longer recognised)."""
        seen = {}
        for node in ast.parse(PROGRAM.read_text(encoding="utf-8")).body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                names = [node.name]
            elif isinstance(node, ast.Assign):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            else:
                continue
            for name in names:
                seen.setdefault(name, []).append(node.lineno)
        twice = {k: v for k, v in seen.items() if len(v) > 1}
        self.assertEqual(twice, {}, "defined more than once (name: lines)")


class CallSignTests(unittest.TestCase):
    def test_call_signs_in_transcripts(self):
        words = mon.callsign_words(mon.CALLSIGN_WORDS_DEFAULT)
        self.assertEqual([c for _i, c in mon.find_callsigns("engine niner to medic twenty one copy", words)],
                         ["Engine 9", "Medic 21"])
        self.assertEqual([c for _i, c in mon.find_callsigns("Battalion 2, Ladder 14 on scene", words)],
                         ["Battalion 2", "Ladder 14"])


if __name__ == "__main__":
    unittest.main()

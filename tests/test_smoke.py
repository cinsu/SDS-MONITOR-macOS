# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""The main window and every window and dialog can be built (on the Qt stand-in)."""
import ast
import inspect
import unittest

from support import PROGRAM, mon, monitor


def window_classes():
    tree = ast.parse(PROGRAM.read_text(encoding="utf-8"))
    return [n.name for n in tree.body if isinstance(n, ast.ClassDef)]


class SmokeTests(unittest.TestCase):
    def test_main_window_builds(self):
        w = monitor(fresh=True)
        self.assertIsNotNone(w.ten_codes)

    def test_every_window_and_dialog_builds(self):
        w = monitor()
        built, failed = [], []
        for name in window_classes():
            cls = getattr(mon, name)
            if not isinstance(cls, type) or not issubclass(cls, mon.QWidget) or name == "Monitor":
                continue
            params = [p for p in inspect.signature(cls.__init__).parameters.values()][1:]
            required = [p for p in params if p.default is p.empty and p.kind == p.POSITIONAL_OR_KEYWORD]
            if not required or required[0].name not in ("monitor", "parent", "main", "window", "owner"):
                continue
            try:
                cls(*([w] * len(required)))
                built.append(name)
            except Exception as exc:                       # report every failure at once
                failed.append(f"{name}: {type(exc).__name__}: {exc}")
        self.assertEqual(failed, [], "\n".join(failed))
        self.assertGreater(len(built), 20)


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""The transcription engine process: started on demand, never left running when the program closes.

v1.1.47 and earlier could crash on exit ("QProcess: Destroyed while process … is still running",
then a segmentation fault): the last call, saved while the window was closing, was queued for
transcription and started a new engine after the engine had been stopped.
"""
import unittest
from unittest import mock

from support import mon, monitor


class TranscriberTests(unittest.TestCase):
    def setUp(self):
        self.w = monitor(fresh=True)
        self.t = self.w.transcriber
        patcher = mock.patch.object(mon, "transcribe_engine_python", return_value="/fake/engine/bin/python")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_starts_on_demand(self):
        self.assertTrue(self.t.ensure_worker())
        self.assertIsNotNone(self.t.proc)
        self.t.shutdown()
        self.assertIsNone(self.t.proc)

    def test_no_new_engine_once_closing(self):
        self.t.shutdown()
        self.assertFalse(self.t.ensure_worker())
        self.assertIsNone(self.t.proc)

    def test_closing_the_window_stops_the_engine_for_good(self):
        self.t.ensure_worker()
        self.w.closeEvent(mon.QEvent())
        self.assertIsNone(self.t.proc)
        self.assertFalse(self.t.ensure_worker())        # e.g. the last call's MP3 finishing late
        self.assertIsNone(self.t.proc)


if __name__ == "__main__":
    unittest.main()

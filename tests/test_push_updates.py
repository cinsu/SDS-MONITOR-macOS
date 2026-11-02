# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""The serial thread against a simulated SDS100 on a simulated clock (runs in well under a second).

Covers push updates (PSI): reports arriving keep push on; silence gets one retry, then a fallback
to polling; a refusal switches push off. v1.1.42 got this wrong: its check for arriving reports
compared Qt signal objects, which are new on every access, so push always "stopped arriving".
"""
import types
import unittest

from support import mon

REPORT = (b'\r<?xml version="1.0" encoding="utf-8"?>\r<ScannerInfo Mode="Scan Mode">'
          b'<Property Mute="Mute"/></ScannerInfo>\r')


class Clock:
    def __init__(self):
        self.now = 1000.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class Recorder:
    def __init__(self):
        self.items = []

    def emit(self, value):
        self.items.append(value)


class FakeScanner:
    """Answers GSI, and pushes reports after PSI,<ms> unless told to go quiet or refuse."""

    def __init__(self, clock, behaviour, stop_after, thread):
        self.clock, self.behaviour, self.stop_at, self.thread = clock, behaviour, clock.now + stop_after, thread
        self.writes, self.pending, self.push_ms, self.last_push = [], b"", 0, 0.0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def reset_input_buffer(self):
        pass

    def flush(self):
        pass

    def write(self, data):
        for cmd in data.decode().split("\r"):
            if not cmd:
                continue
            self.writes.append((round(self.clock.now - 1000, 2), cmd))
            if cmd.startswith("PSI,"):
                if self.behaviour == "refuse":
                    self.pending += b"PSI,NG\r"
                else:
                    self.push_ms = int(cmd[4:])
            elif cmd == "GSI":
                self.pending += b"GSI,<XML>," + REPORT

    def read(self, size):
        self.clock.sleep(0.05)
        if self.clock.now >= self.stop_at:
            self.thread.running = False
        if (self.behaviour == "push" and self.push_ms
                and self.clock.now - self.last_push >= self.push_ms / 1000):
            self.last_push = self.clock.now
            self.pending += b"PSI,<XML>," + REPORT
        out, self.pending = self.pending, b""
        return out


def run(behaviour, seconds, push_ms=250, poll_ms=500):
    clock = Clock()
    saved_time, saved_serial, saved_users = mon.time, mon.serial.Serial, mon.port_users
    mon.time = types.SimpleNamespace(monotonic=clock.monotonic, sleep=clock.sleep, time=clock.monotonic)
    signals = {n: Recorder() for n in ("message", "xml_received", "command_result", "list_received",
                                      "analyze_received", "menu_received", "graph_received")}

    class Thread(mon.ScannerThread):
        pass

    class Bound:
        """Like Qt's bound signal: a new object on every attribute access."""

        def __init__(self, rec):
            self.emit = rec.emit

    for name, rec in signals.items():
        setattr(Thread, name, property(lambda self, rec=rec: Bound(rec)))
    thread = Thread("/dev/fake", 115200, poll_ms)
    thread.push_ms = push_ms
    scanners = []
    mon.serial.Serial = lambda *a, **k: scanners.append(FakeScanner(clock, behaviour, seconds, thread)) or scanners[-1]
    mon.port_users = lambda port: []
    try:
        thread.run()
    finally:
        mon.time, mon.serial.Serial, mon.port_users = saved_time, saved_serial, saved_users
    sent = [c for _t, c in scanners[0].writes]
    return thread, signals, sent


class PushTests(unittest.TestCase):
    def test_reports_arriving_keep_push_on(self):
        thread, sig, sent = run("push", 10)
        self.assertIn("PUSH:ON", sig["message"].items)
        self.assertNotIn("KAL", sent)                                # never thought reports stopped
        self.assertNotIn("PUSH:FALLBACK", sig["message"].items)
        self.assertEqual(sent.count("GSI"), 0)                       # no polling while pushed
        self.assertGreater(len(sig["xml_received"].items), 30)       # ~4 a second for 10 s
        self.assertEqual(sent[-1], "PSI,0")                          # push stopped on disconnect

    def test_silence_retries_once_then_falls_back_to_polling(self):
        thread, sig, sent = run("silent", 8)
        self.assertIn("KAL", sent)
        self.assertEqual(sent.count("KAL"), 1)
        self.assertIn("PUSH:FALLBACK", sig["message"].items)
        self.assertEqual(thread.push_ms, 0)
        self.assertGreater(sent.count("GSI"), 3)                     # polling again
        self.assertGreater(len(sig["xml_received"].items), 3)

    def test_refused_switches_push_off(self):
        thread, sig, sent = run("refuse", 2)
        self.assertIn("PUSH:REFUSED", sig["message"].items)
        self.assertEqual(thread.push_ms, 0)
        self.assertGreater(sent.count("GSI"), 1)

    def test_polling_only(self):
        thread, sig, sent = run("push", 3, push_ms=0, poll_ms=500)
        self.assertNotIn("PSI,250", sent)
        self.assertTrue(5 <= sent.count("GSI") <= 7, sent.count("GSI"))
        self.assertIn("CONNECTED", sig["message"].items)
        self.assertEqual(sig["message"].items[-1], "DISCONNECTED")


if __name__ == "__main__":
    unittest.main()

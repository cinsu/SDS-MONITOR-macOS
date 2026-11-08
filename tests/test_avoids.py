# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Scanner Tools → Avoids (v1.1.77). The lists are made up, in the GLT layout of remote spec V2.00."""
import unittest
from collections import deque

from support import mon


class Box:
    def __init__(self, on=True, text=""):
        self.on, self.value = on, text

    def isChecked(self):
        return self.on

    def text(self):
        return self.value

    def setEnabled(self, _on):
        pass


REPLIES = {
    "GLT,FL": '<GLT><FL Index="0" Name="Lakeside County" Monitor="On" Q_Key="0"/><Footer No="1" EOT="1"/></GLT>',
    "GLT,SYS,0": '<GLT><SYS Index="10" Name="Lakeside Trunk" Avoid="Off" Type="P25 Trunk"/>'
                 '<SYS Index="11" Name="Lakeside" Avoid="Avoid" Type="Conventional"/><Footer No="1" EOT="1"/></GLT>',
    "GLT,DEPT,10": '<GLT><DEPT Index="20" Name="Fire" Avoid="T-Avoid"/><Footer No="1" EOT="1"/></GLT>',
    "GLT,SITE,10": '<GLT><SITE Index="30" Name="North" Avoid="Off"/><Footer No="1" EOT="1"/></GLT>',
    "GLT,DEPT,11": '<GLT><DEPT Index="21" Name="City Police" Avoid="Off"/><Footer No="1" EOT="1"/></GLT>',
    "GLT,TGID,20": '<GLT><TGID Index="40" Name="Fire Dispatch" TGID="44358" Avoid="Off"/>'
                   '<Footer No="1" EOT="1"/></GLT>',
    "GLT,CFREQ,21": '<GLT><CFREQ Index="41" Name="PD Main" Freq="460.0250MHz" Avoid="On"/>'
                    '<Footer No="1" EOT="1"/></GLT>',
}


class AvoidTests(unittest.TestCase):
    def test_states_and_children(self):
        self.assertEqual([mon.avoid_state(v) for v in ("Off", "", "T-Avoid", "Avoid", "On", None)],
                         ["Off", "Off", "Temporary", "Permanent", "Permanent", "Off"])
        self.assertEqual(mon.avoid_children("SYS", "Conventional"), ("DEPT",))
        self.assertEqual(mon.avoid_children("SYS", "P25 Trunk"), ("DEPT", "SITE"))
        self.assertEqual(mon.avoid_children("DEPT", "P25 Trunk"), ("TGID",))
        self.assertEqual(mon.avoid_children("DEPT", "Conventional", leaves=False), ())

    def tools(self):
        tools = mon.ScannerTools.__new__(mon.ScannerTools)
        sent, asked = [], []
        tools.monitor = type("M", (), {"connected": True, "command_reply": lambda self, t: None,
                                       "request_glt": lambda self, owner, c: asked.append(c) or True})()
        tools.send = lambda command: sent.append(command) or True
        tools.status = tools.avoid_count = object()
        tools.glt_pending = deque()
        tools.avoid_read = tools.avoid_stop = Box()
        tools.avoid_leaves, tools.avoid_only, tools.avoid_search = Box(), Box(False), Box()
        tools.avoid_kinds = {k: Box() for k in mon.AVOID_GROUPS}
        tools.avoid_rows, tools.avoid_scanning = [], False
        tools.render_avoids = lambda *a: None
        return tools, sent, asked

    def test_reading_the_whole_tree_and_changing_avoids(self):
        tools, sent, asked = self.tools()
        old, question = mon.set_text, mon.QMessageBox.question
        shown = []
        mon.set_text = lambda _label, text: shown.append(text)
        try:
            tools.scan_avoids()
            while tools.glt_pending:
                tools.handle_list(REPLIES[tools.glt_pending[0][0]])
            self.assertEqual(sorted(asked), sorted(REPLIES))
            rows = {r["name"]: r for r in tools.avoid_rows}
            self.assertEqual(set(rows), {"Lakeside Trunk", "Lakeside", "Fire", "North", "City Police",
                                         "Fire Dispatch", "PD Main"})
            self.assertEqual(rows["Fire Dispatch"]["where"], "Lakeside County › Lakeside Trunk › Fire")
            self.assertEqual((rows["Fire"]["avoid"], rows["Lakeside"]["avoid"]), ("Temporary", "Permanent"))
            self.assertIn("7 item(s) read, 3 avoided", shown[-1])
            avoided = mon.avoid_filter(tools.avoid_rows, set(mon.AVOID_GROUPS), True)
            self.assertEqual({r["name"] for r in avoided}, {"Fire", "Lakeside", "PD Main"})
            self.assertEqual(len(mon.avoid_filter(tools.avoid_rows, {"TGID"}, False, "dispatch")), 1)
            tools.send_avoids([rows["Fire Dispatch"], rows["North"]], 2)
            self.assertEqual(sent, ["AVD,TGID,40,,2", "AVD,SITE,30,,2"])
            self.assertEqual(rows["North"]["avoid"], "Temporary")
            mon.QMessageBox.question = staticmethod(lambda *a: mon.QMessageBox.StandardButton.Yes)
            tools.clear_temporary_avoids()
            self.assertEqual(sorted(sent[2:]), ["AVD,DEPT,20,,3", "AVD,SITE,30,,3", "AVD,TGID,40,,3"])
            self.assertEqual(tools.send_avoids([rows["City Police"]], 3), 0)     # nothing to remove
        finally:
            mon.set_text, mon.QMessageBox.question = old, question

    def test_an_error_reply_and_stop_still_finish(self):
        tools, _sent, _asked = self.tools()
        old = mon.set_text
        mon.set_text = lambda *_a: None
        try:
            tools.scan_avoids()
            tools.handle_list(REPLIES["GLT,FL"])
            tools.stop_avoid_scan()
            self.assertTrue(tools.glt_pending)
            tools.handle_list_error("NG")
            self.assertFalse(tools.glt_pending)
            self.assertFalse(tools.avoid_scanning)
        finally:
            mon.set_text = old


if __name__ == "__main__":
    unittest.main()

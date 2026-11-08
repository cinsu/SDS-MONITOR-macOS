# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""The customizable Scanner Information panel (v1.1.71): lines, colours, conditional colours, presets."""
import unittest
import xml.etree.ElementTree as ET

from support import HOME, mon, monitor

VALUES = {"System": "Palmetto 800", "Department": "Greenville County - Fire", "Channel": "Fire Dispatch",
          "Service Type": "Fire Dispatch", "RSSI": "-62", "Talkgroup": "—", "Recording": "On"}


class LayoutTests(unittest.TestCase):
    def test_default_is_the_old_panel(self):
        layout = mon.default_info_layout()
        self.assertEqual([l["field"] for l in layout["lines"]], list(mon.DEFAULT_INFO_FIELDS))
        self.assertEqual(layout["lines"][0]["label"], "SYSTEM")
        self.assertEqual(mon.info_styles(layout, VALUES), ("", [("", "")] * 9))

    def test_cleaning_bad_settings(self):
        self.assertEqual(mon.clean_info_layout("junk"), mon.default_info_layout())
        layout = mon.clean_info_layout({"lines": [{"field": "Channel", "fg": "red", "bg": "#112233", "size": 900},
                                                  {"field": "Nope"}],
                                        "rules": [{"field": "RSSI", "op": "explode"}], "panel_bg": "#000000"})
        line = layout["lines"][0]
        self.assertEqual((line["fg"], line["bg"], line["size"]), ("", "#112233", 300))
        self.assertEqual((len(layout["lines"]), layout["rules"], layout["panel_bg"]), (1, [], "#000000"))

    def test_custom_lines(self):
        line = mon.default_info_line("Custom")
        line["template"] = "{System} › {Department} ({Nonsense})"
        self.assertEqual(mon.info_text(line, VALUES), "Palmetto 800 › Greenville County - Fire ({Nonsense})")
        self.assertEqual(mon.info_text(mon.default_info_line("Site"), VALUES), "—")

    def test_conditions(self):
        rule = {"field": "Service Type", "op": "contains", "value": "fire", "target": "line", "fg": "", "bg": ""}
        self.assertTrue(mon.rule_matches(rule, VALUES))
        for op, value, expected in (("is", "fire dispatch", True), ("is not", "Law", True),
                                    ("starts with", "Law", False), ("is empty", "", False),
                                    ("is not empty", "", True)):
            self.assertEqual(mon.rule_matches(dict(rule, op=op, value=value), VALUES), expected, op)
        self.assertTrue(mon.rule_matches(dict(rule, field="RSSI", op="number ≥", value="-70"), VALUES))
        self.assertFalse(mon.rule_matches(dict(rule, field="RSSI", op="number ≤", value="-70"), VALUES))
        self.assertTrue(mon.rule_matches(dict(rule, field="Talkgroup", op="is empty"), VALUES))
        self.assertFalse(mon.rule_matches(dict(rule, field="Talkgroup", op="contains", value="1"), VALUES))
        self.assertFalse(mon.rule_matches(dict(rule, field="RSSI", op="number ≥", value="abc"), VALUES))

    def test_colours_after_rules(self):
        layout = mon.default_info_layout()
        layout["lines"].append(mon.default_info_line("Service Type"))
        layout["lines"][3]["fg"] = "#aaaaaa"                      # Channel line
        layout["rules"] = [
            {"field": "Service Type", "op": "contains", "value": "Fire", "target": "line",
             "fg": "#ffffff", "bg": "#b3261e"},
            {"field": "Recording", "op": "is", "value": "On", "target": "panel", "fg": "", "bg": "#5a4300"},
            {"field": "Channel", "op": "contains", "value": "Dispatch", "target": "line", "fg": "#ffff00", "bg": ""}]
        panel, styles = mon.info_styles(layout, VALUES)
        self.assertEqual(panel, "#5a4300")
        self.assertEqual(styles[3], ("#ffff00", ""))              # later rule wins, background unchanged
        self.assertEqual(styles[-1], ("#ffffff", "#b3261e"))      # the Service Type line
        self.assertEqual(styles[0], ("", ""))
        self.assertIn("background:#b3261e", mon.info_line_css("#ffffff", "#b3261e", True))

    def test_saving_and_presets(self):
        path = HOME / "info.json"
        settings = mon.load_info_settings(path)
        self.assertEqual(settings["current"], mon.default_info_layout())
        big = mon.default_info_layout()
        big["lines"][3]["size"] = 200
        settings["presets"]["Large print"] = big
        mon.save_info_settings(settings, path)
        again = mon.load_info_settings(path)
        self.assertEqual(again["presets"]["Large print"]["lines"][3]["size"], 200)

    def test_extra_fields_from_the_scanner(self):
        root = ET.fromstring(
            '<ScannerInfo Mode="Trunk Scan"><MonitorList Name="Greenville County" Index="0" ListType="FL" '
            'Q_Key="0" N_Tag="1" DB_Counter="3"/><System Name="Palmetto 800" SystemType="P25 Trunk" Q_Key="0" '
            'N_Tag="2" Hold="Off"/><Department Name="Greenville County" Q_Key="4"/>'
            '<TGID Name="Fire Dispatch" TGID="44358" SvcType="Fire Dispatch" N_Tag="120" Avoid="Off" Hold="On"/>'
            '<Property VOL="7" SQL="2" Sig="4" Att="Off" Rec="Off" P25Status="NAC:1DB" Rssi="-62"/></ScannerInfo>')
        extras = mon.gsi_extras(root, root.find("System"), root.find("Department"), root.find("TGID"),
                                root.find("Property"))
        self.assertEqual((extras["Service Type"], extras["System Quick Key"], extras["System Number Tag"],
                          extras["Department Quick Key"], extras["Channel Number Tag"], extras["P25 Status"],
                          extras["Hold"], extras["Volume"], extras["Modulation"]),
                         ("Fire Dispatch", "0", "2", "4", "120", "NAC:1DB", "On", "7", "—"))
        self.assertEqual((extras["Favorites List"], extras["Favorites List Quick Key"],
                          extras["Favorites List Number Tag"]), ("Greenville County", "0", "1"))
        self.assertEqual(extras["Site Quick Key"], "—")
        with_site = ET.fromstring('<ScannerInfo><System Name="Palmetto 800" Hold="Off"/>'
                                  '<Site Name="Caesars Head" Avoid="Off" Q_Key="7" Hold="On"/></ScannerInfo>')
        extras = mon.gsi_extras(with_site, with_site.find("System"), None, None, None)
        self.assertEqual((extras["Site Quick Key"], extras["Hold"]), ("7", "On"))       # 1.1.78
        full = ET.fromstring('<ScannerInfo><MonitorList Name="Full Database" Index="4294967295" ListType="FullDb" '
                             'Q_Key="None" N_Tag="None" DB_Counter="3"/></ScannerInfo>')
        extras = mon.gsi_extras(full, None, None, None, None)
        self.assertEqual((extras["Favorites List"], extras["Favorites List Quick Key"]), ("Full Database", "—"))


class PanelTests(unittest.TestCase):
    def test_the_panel_follows_the_layout(self):
        w = monitor(fresh=True)
        self.assertEqual(len(w.info_rows), 9)
        layout = mon.default_info_layout()
        layout["lines"] = [mon.default_info_line("Channel"), mon.default_info_line("Custom")]
        layout["lines"][1]["show_label"] = False
        layout["rules"] = [{"field": "Channel", "op": "contains", "value": "Fire", "target": "line",
                            "fg": "#ffffff", "bg": "#b3261e"}]
        w.build_info_rows(layout)
        self.assertEqual(len(w.info_rows), 2)
        self.assertIsNone(w.info_rows[1][1])                       # no label on the custom line
        shown, css = [], []
        old_text, old_css = mon.set_text, mon.set_css
        mon.set_text = lambda label, text: shown.append((label, text))
        mon.set_css = lambda widget, style: css.append((widget, style))
        try:
            w.info_values = dict(w.info_values, Channel="Fire Dispatch", System="Palmetto 800",
                                 Department="Greenville")
            w.render_info()
        finally:
            mon.set_text, mon.set_css = old_text, old_css
        texts = {label: text for label, text in shown}
        self.assertEqual(texts[w.info_rows[0][2]], "Fire Dispatch")
        self.assertEqual(texts[w.info_rows[1][2]], "Palmetto 800 › Greenville")
        styles = {widget: style for widget, style in css}
        self.assertIn("#b3261e", styles[w.info_rows[0][2]])
        self.assertIn("Service Type", w.fields)                    # every field keeps its latest value
        self.assertIn("Unit ID", w.fields)


if __name__ == "__main__":
    unittest.main()

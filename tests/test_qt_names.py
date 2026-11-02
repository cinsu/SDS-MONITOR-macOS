# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Window classes must not accidentally replace Qt's own methods.

Qt calls some methods itself (event handlers, a dialog's done()/reject(), a thread's run()). A
method or attribute that reuses one of those names takes Qt's place:
  * v1.1.42–1.1.46: the Weather and Tone-Out window had event(kind, channel, …), which replaced the
    handler Qt calls for every event the window gets (show, paint, resize).
  * the Database & Favorites Manager's firmware window had done(result, error) and couldn't close.
The Qt stand-in used by the other tests can't see this, so this test reads the source.
"""
import ast
import unittest

from support import PROGRAM

# Qt base classes → the methods Qt itself calls on them (name → number of arguments after self).
OBJECT = {"event": 1, "eventFilter": 2, "timerEvent": 1, "childEvent": 1, "customEvent": 1,
          "connectNotify": 1, "disconnectNotify": 1}
WIDGET = dict(OBJECT, **{n: 1 for n in (
    "paintEvent", "resizeEvent", "moveEvent", "showEvent", "hideEvent", "closeEvent", "changeEvent",
    "keyPressEvent", "keyReleaseEvent", "mousePressEvent", "mouseReleaseEvent", "mouseMoveEvent",
    "mouseDoubleClickEvent", "wheelEvent", "enterEvent", "leaveEvent", "focusInEvent", "focusOutEvent",
    "contextMenuEvent", "dragEnterEvent", "dragMoveEvent", "dragLeaveEvent", "dropEvent", "actionEvent",
    "inputMethodEvent", "tabletEvent", "setVisible", "heightForWidth", "inputMethodQuery",
    "focusNextPrevChild")}, sizeHint=0, minimumSizeHint=0, hasHeightForWidth=0)
DIALOG = dict(WIDGET, done=1, accept=0, reject=0, exec=0, open=0)
THREAD = dict(OBJECT, run=0)
QT_VIRTUALS = {"QObject": OBJECT, "QThread": THREAD, "QWidget": WIDGET, "QDialog": DIALOG,
               "QMainWindow": WIDGET, "QFrame": WIDGET, "QLabel": WIDGET, "QGroupBox": WIDGET,
               "QTableWidget": WIDGET, "QListWidget": WIDGET, "QTabWidget": WIDGET, "QDockWidget": WIDGET,
               "QPushButton": WIDGET, "QLineEdit": WIDGET, "QComboBox": WIDGET, "QTextEdit": WIDGET,
               "QPlainTextEdit": WIDGET, "QScrollArea": WIDGET, "QSplitter": WIDGET, "QProgressBar": WIDGET,
               "QSlider": WIDGET, "QTreeWidget": WIDGET, "QMessageBox": DIALOG}
# Plain methods that are easy to hide by assigning self.<name> = …
COMMON = {"show", "hide", "close", "update", "repaint", "layout", "font", "style", "parent", "window",
          "size", "width", "height", "resize", "move", "pos", "rect", "geometry", "palette", "children",
          "isVisible", "setLayout", "deleteLater", "setParent", "raise_", "activateWindow", "setEnabled",
          "isEnabled", "setFocus", "windowTitle", "setWindowTitle", "statusBar", "menuBar", "sender"}
# Meant to be this way: (class, name): why
INTENDED = {
    ("ScannerScreen", "screen"): "its own screen buffer; QWidget.screen() is never needed",
}


def problems():
    tree = ast.parse(PROGRAM.read_text(encoding="utf-8"))
    classes = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}

    def qt_bases(node, seen=()):
        found = set()
        for b in node.bases:
            name = b.id if isinstance(b, ast.Name) else getattr(b, "attr", "")
            if name in QT_VIRTUALS:
                found.add(name)
            elif name in classes and name not in seen:
                found |= qt_bases(classes[name], seen + (name,))
        return found

    out = []
    for cls in classes.values():
        bases = qt_bases(cls)
        if not bases:
            continue
        virtuals = {}
        for b in bases:
            virtuals.update(QT_VIRTUALS[b])
        common = COMMON if bases - {"QObject", "QThread"} else set()
        for item in cls.body:
            if isinstance(item, ast.FunctionDef) and item.name in virtuals:
                args = item.args
                positional = len(args.posonlyargs) + len(args.args) - 1
                required = positional - len(args.defaults)
                want = virtuals[item.name]
                if not (required <= want <= positional or args.vararg):
                    out.append(f"{cls.name}.{item.name}() takes {positional} argument(s) but Qt calls it "
                               f"with {want}: it replaces Qt's {item.name}() (line {item.lineno})")
        for sub in ast.walk(cls):
            if (isinstance(sub, ast.Attribute) and isinstance(sub.ctx, ast.Store)
                    and isinstance(sub.value, ast.Name) and sub.value.id == "self"
                    and (sub.attr in virtuals or sub.attr in common)
                    and (cls.name, sub.attr) not in INTENDED):
                out.append(f"{cls.name} sets self.{sub.attr}, hiding Qt's {sub.attr}() (line {sub.lineno})")
    return sorted(set(out))


class QtNameTests(unittest.TestCase):
    def test_no_window_replaces_a_qt_method_by_accident(self):
        found = problems()
        self.assertEqual(found, [], "\n".join(found))

    def test_the_check_catches_the_old_mistakes(self):
        import tempfile, pathlib
        import support
        bad = ("from PyQt6.QtWidgets import QWidget, QDialog\n"
               "class Modes(QWidget):\n    def event(self, kind, channel):\n        pass\n"
               "class Firmware(QDialog):\n    def done(self, result, error):\n        pass\n"
               "class Main(QWidget):\n    def __init__(self):\n        self.event = None\n"
               "class Fine(QDialog):\n    def done(self, code):\n        super().done(code)\n"
               "    def paintEvent(self, event):\n        pass\n")
        path = pathlib.Path(tempfile.mkdtemp()) / "bad.py"
        path.write_text(bad)
        saved = support.PROGRAM
        try:
            globals()["PROGRAM"] = path
            found = problems()
        finally:
            globals()["PROGRAM"] = saved
        self.assertEqual(len(found), 3, found)
        self.assertTrue(any("Modes.event()" in f for f in found))
        self.assertTrue(any("Firmware.done()" in f for f in found))
        self.assertTrue(any("self.event" in f for f in found))


if __name__ == "__main__":
    unittest.main()

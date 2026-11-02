# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""A stand-in for PyQt6 (and pyserial) so the program's logic can be tested without a display.

Every Qt class, method and constant becomes a do-nothing object that accepts any call. That proves
the logic runs (no misspelt names, wrong arguments or broken control flow) but says nothing about
how windows look or behave; test_real_qt.py checks that with the real Qt when it is installed.
Importing this module installs the stand-ins.
"""
import sys
import types


class _Meta(type):
    def __getattr__(cls, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return Stub

    def __or__(cls, other):
        return cls

    def __ror__(cls, other):
        return cls


# Qt's methods are camelCase (setText, addWidget) or one of these plain words. On the program's own
# windows any other missing name is a real mistake (an attribute used before it is set, a typo), so
# it raises AttributeError like real Qt instead of quietly returning a stand-in.
QT_WORDS = {
    "show", "hide", "close", "update", "repaint", "resize", "move", "raise_", "lower", "layout", "parent",
    "window", "font", "palette", "style", "size", "width", "height", "pos", "rect", "geometry", "children",
    "scroll", "grab", "render", "screen", "x", "y", "sender", "thread", "event", "exec", "open", "accept",
    "reject", "done", "result", "text", "clear", "data", "find", "actions", "cursor", "locale", "mask",
    "start", "stop", "wait", "quit", "exit", "terminate", "run", "emit", "connect", "disconnect", "tr",
    "destroyed", "finished", "started", "timeout", "toggled", "clicked", "pressed", "released", "triggered",
    "changed", "accepted", "rejected", "value", "title", "icon", "item", "model", "count", "widget",
    "menu", "selected", "activated", "focus", "property", "contains", "remove", "sync", "kill", "write",
    "read", "error", "state", "close", "flush", "reset", "readAll", "metaObject", "inherits", "deleteLater",
}


class Stub(metaclass=_Meta):
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        if type(self).__module__ != __name__ and not (name[:1].islower() and "_" not in name
                                                     and name != name.lower()) and name not in QT_WORDS:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return Stub()

    def __call__(self, *args, **kwargs):
        return Stub()

    def __or__(self, other):
        return self

    def __ror__(self, other):
        return self

    def __iter__(self):
        return iter(())

    def __bool__(self):
        return True

    def __int__(self):
        return 0

    def __index__(self):
        return 0

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return Stub()

    def __format__(self, spec):
        return "stub"

    def __float__(self):
        return 0.0


for _op in ("mul", "rmul", "add", "radd", "sub", "rsub", "truediv", "rtruediv", "floordiv", "mod", "neg"):
    setattr(Stub, f"__{_op}__", lambda self, *a: self)
for _op in ("lt", "le", "gt", "ge"):
    setattr(Stub, f"__{_op}__", lambda self, other: False)


class Signal:
    """A signal that really calls what is connected to it (for the widgets below)."""

    def __init__(self, owner):
        self.owner, self.slots = owner, []

    def connect(self, slot, *args):
        self.slots.append(slot)

    def disconnect(self, slot=None):
        if slot is None:
            self.slots.clear()
        elif slot in self.slots:
            self.slots.remove(slot)
        else:
            raise TypeError("not connected")

    def emit(self, *args):
        if getattr(self.owner, "_blocked", False):
            return
        for slot in list(self.slots):
            try:
                slot(*args)
            except TypeError as exc:
                if "positional argument" not in str(exc):
                    raise
                slot()                       # Qt also calls slots that take fewer arguments


class _Smart(Stub):
    """Keeps real values and sends the signals real Qt sends when they change."""
    SIGNALS = ()

    def __init__(self, *args, **kwargs):
        self._blocked = False
        for name in self.SIGNALS:
            setattr(self, name, Signal(self))

    def blockSignals(self, on):
        was, self._blocked = self._blocked, bool(on)
        return was

    def signalsBlocked(self):
        return self._blocked


# A few widgets keep real values, so logic that reads them back is tested properly.
class QComboBox(_Smart):
    SIGNALS = ("currentIndexChanged", "currentTextChanged", "activated", "textActivated")

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._items, self._index = [], -1

    def _changed(self):
        self.currentIndexChanged.emit(self._index)
        self.currentTextChanged.emit(self.currentText())

    def addItem(self, *args):
        args = [a for a in args if not isinstance(a, Stub)]        # (icon,) text, data
        self._items.append((str(args[0]) if args else "", args[1] if len(args) > 1 else None))
        if self._index < 0:
            self._index = 0
            self._changed()                  # Qt selects (and announces) the first item added

    def addItems(self, texts):
        for t in texts:
            self.addItem(t)

    def insertItem(self, index, text, data=None):
        self._items.insert(index, (str(text), data))
        if self._index < 0:
            self._index = 0
            self._changed()
        elif index <= self._index:
            self._index += 1

    def clear(self):
        had = self._index >= 0
        self._items, self._index = [], -1
        if had:
            self._changed()

    def count(self):
        return len(self._items)

    def currentIndex(self):
        return self._index

    def setCurrentIndex(self, index):
        index = index if 0 <= index < len(self._items) else -1
        if index != self._index:
            self._index = index
            self._changed()

    def currentText(self):
        return self._items[self._index][0] if self._index >= 0 else ""

    def setCurrentText(self, text):
        self.setCurrentIndex(self.findText(text))

    def currentData(self, *args):
        return self._items[self._index][1] if self._index >= 0 else None

    def itemText(self, i):
        return self._items[i][0] if 0 <= i < len(self._items) else ""

    def itemData(self, i, *args):
        return self._items[i][1] if 0 <= i < len(self._items) else None

    def findText(self, text, *args):
        return next((i for i, (t, _d) in enumerate(self._items) if t == text), -1)

    def findData(self, data, *args):
        return next((i for i, (_t, d) in enumerate(self._items) if d == data), -1)

    def removeItem(self, i):
        if 0 <= i < len(self._items):
            del self._items[i]
            index = min(self._index, len(self._items) - 1)
            if i <= self._index:
                self._index = index
                self._changed()


class _Checkable(_Smart):
    SIGNALS = ("toggled", "clicked", "stateChanged", "checkStateChanged")

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._checked = False
        self._text = next((a for a in args if isinstance(a, str)), "")

    def isChecked(self):
        return self._checked

    def setChecked(self, on):
        if bool(on) != self._checked:
            self._checked = bool(on)
            self.toggled.emit(self._checked)

    def text(self):
        return self._text

    def setText(self, text):
        self._text = str(text)


class QCheckBox(_Checkable):
    pass


class QRadioButton(_Checkable):
    pass


class _Text(_Smart):
    SIGNALS = ("textChanged", "textEdited", "editingFinished", "returnPressed", "linkActivated")

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._text = next((a for a in args if isinstance(a, str)), "")

    def text(self):
        return self._text

    def setText(self, text):
        if str(text) != self._text:
            self._text = str(text)
            self.textChanged.emit(self._text)

    def clear(self):
        self.setText("")


class QLineEdit(_Text):
    pass


class QLabel(_Text):
    pass


class QTabWidget(_Smart):
    SIGNALS = ("currentChanged", "tabBarClicked", "tabCloseRequested")

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._tabs, self._index = [], -1

    def addTab(self, widget, *label):
        self._tabs.append(widget)
        if self._index < 0:
            self._index = 0
            self.currentChanged.emit(0)      # Qt announces the first tab as soon as it's added
        return len(self._tabs) - 1

    def insertTab(self, index, widget, *label):
        self._tabs.insert(index, widget)
        if self._index < 0:
            self._index = 0
            self.currentChanged.emit(0)
        return index

    def count(self):
        return len(self._tabs)

    def currentIndex(self):
        return self._index

    def setCurrentIndex(self, index):
        if 0 <= index < len(self._tabs) and index != self._index:
            self._index = index
            self.currentChanged.emit(index)

    def currentWidget(self):
        return self._tabs[self._index] if self._index >= 0 else None

    def setCurrentWidget(self, widget):
        if widget in self._tabs:
            self.setCurrentIndex(self._tabs.index(widget))

    def widget(self, index):
        return self._tabs[index] if 0 <= index < len(self._tabs) else None

    def indexOf(self, widget):
        return self._tabs.index(widget) if widget in self._tabs else -1


class QSpinBox(_Smart):
    SIGNALS = ("valueChanged", "editingFinished", "textChanged")

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._value, self._low, self._high = 0, 0, 99

    def setRange(self, low, high):
        self._low, self._high = low, high
        self.setValue(self._value)

    def setMinimum(self, low):
        self.setRange(low, max(low, self._high))

    def setMaximum(self, high):
        self.setRange(min(self._low, high), high)

    def value(self):
        return self._value

    def setValue(self, value):
        value = min(max(value, self._low), self._high)
        if value != self._value:
            self._value = value
            self.valueChanged.emit(value)

    def minimum(self):
        return self._low

    def maximum(self):
        return self._high


class QDoubleSpinBox(QSpinBox):
    pass


SMART = {c.__name__: c for c in (QComboBox, QCheckBox, QRadioButton, QLineEdit, QLabel, QSpinBox,
                                 QDoubleSpinBox, QTabWidget)}


def _module(name):
    module = types.ModuleType(name)

    def getattr_(attr):
        if attr.startswith("__") or attr.startswith("QtMultimedia"):
            raise AttributeError(attr)       # behave as if Qt Multimedia isn't installed
        if name == "PyQt6.QtWidgets" and attr in SMART:
            return SMART[attr]
        return Stub

    module.__getattr__ = getattr_
    sys.modules[name] = module
    return module


_pyqt = _module("PyQt6")
for _sub in ("QtCore", "QtGui", "QtWidgets"):
    setattr(_pyqt, _sub, _module("PyQt6." + _sub))
sys.modules["PyQt6.QtCore"].pyqtSignal = lambda *a, **k: Stub()
_serial = _module("serial")
_tools = _module("serial.tools")
_ports = _module("serial.tools.list_ports")
_serial.tools, _tools.list_ports = _tools, _ports
_serial.SerialException = type("SerialException", (Exception,), {})

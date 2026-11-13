#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE.
"""Build the .deb: python3 packaging/build_deb.py [out folder]  (needs dpkg-deb)

Installs the program to /opt/sds100-monitor, the launcher /usr/bin/sds100-monitor, a menu entry
and icons. The tests are packaged too (bash /opt/sds100-monitor/run_tests.sh).
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
NAME = "sds100-monitor"
SKIP = shutil.ignore_patterns("__pycache__", "*.pyc", ".git", ".github", "packaging", "dist", "*.deb")


def notes(version):
    text = re.sub(r"<!--.*?-->\n?", "", (SRC / "CHANGELOG.md").read_text())
    m = re.search(rf"^## v{re.escape(version)}\b[^\n]*\n(.*?)(?=^## v|\Z)", text, re.M | re.S)
    body = re.sub(r"`([^`]*)`", r"\1", re.sub(r"\*\*(.+?)\*\*", r"\1", m.group(1).strip())) if m else ""
    return [l.rstrip() for l in body.splitlines()]


def main(out):
    source = (SRC / "sds100_monitor.py").read_text()
    for py in sorted(SRC.rglob("*.py")):
        compile(py.read_text(encoding="utf-8"), str(py), "exec")
    version = re.search(r'^VERSION = "([^"]+)"', source, re.M).group(1)
    personal = version.endswith("-personal")
    deb_version = version.removesuffix("-personal")
    package = "sds100-monitor-personal" if personal else "sds100-monitor"
    other = "sds100-monitor" if personal else "sds100-monitor-personal"
    root = Path(tempfile.mkdtemp(prefix="deb-"))
    shutil.copytree(SRC, root / "opt" / NAME, ignore=SKIP)
    launcher = root / "usr/bin" / NAME
    launcher.parent.mkdir(parents=True)
    launcher.write_text(f"#!/bin/sh\nexport PYTHONDONTWRITEBYTECODE=1\nexec /usr/bin/python3 /opt/{NAME}/sds100_monitor.py \"$@\"\n")
    apps = root / "usr/share/applications"
    apps.mkdir(parents=True)
    (apps / f"{NAME}.desktop").write_text(
        "[Desktop Entry]\nType=Application\nName=SDS100 Monitor\n"
        "Comment=Monitor and control a Uniden SDS100 scanner\n"
        f"Exec=/usr/bin/{NAME}\nIcon=/usr/share/icons/hicolor/scalable/apps/{NAME}.svg\n"
        "Terminal=false\nCategories=Utility;\n")
    svg = root / "usr/share/icons/hicolor/scalable/apps"
    svg.mkdir(parents=True)
    shutil.copy(SRC / "sds100-monitor.svg", svg / f"{NAME}.svg")
    for png in sorted((HERE / "icons").glob("*.png")):
        size = png.stem
        dest = root / f"usr/share/icons/hicolor/{size}x{size}/apps"
        dest.mkdir(parents=True)
        shutil.copy(png, dest / f"{NAME}.png")
    widget = SRC / "plasma-widget"                     # 1.1.84: the Plasma 6 widget
    if widget.is_dir():
        widget_id = __import__("json").loads((widget / "metadata.json").read_text())["KPlugin"]["Id"]
        shutil.copytree(widget, root / "usr/share/plasma/plasmoids" / widget_id, ignore=SKIP)
    doc = root / "usr/share/doc" / package
    doc.mkdir(parents=True)
    for f in ("README.md", "CHANGELOG.md"):
        shutil.copy(SRC / f, doc / f)
    (doc / "copyright").write_text("SDS100 Monitor\nCopyright (c) 2026 J. Lynch. Developed with the help of AI "
                                   "(Anthropic's Claude).\nLicence: GPL-3.0-or-later\n\n" + (SRC / "LICENSE").read_text())
    root.chmod(0o755)
    for p in root.rglob("*"):
        p.chmod(0o755 if p.is_dir() or p.suffix == ".sh" or p == launcher else 0o644)
    size = sum(p.stat().st_size for p in root.rglob("*") if p.is_file()) // 1024
    (root / "DEBIAN").mkdir(mode=0o755)
    what = [f"What's new in {deb_version}:", ""] + (notes(deb_version) or ["See CHANGELOG.md."])
    description = "Live monitoring and control for the Uniden SDS100 scanner" + (" (personal build)" if personal else "")
    description += "".join("\n ." if not l.strip() else "\n " + l for l in what[:80])
    (root / "DEBIAN/control").write_text("\n".join([
        f"Package: {package}", f"Version: {deb_version}", "Architecture: all", "Maintainer: J. Lynch",
        f"Installed-Size: {size}", "Depends: python3 (>= 3.10), python3-pyqt6, python3-serial",
        "Recommends: python3-pyqt6.qtmultimedia, ffmpeg", f"Conflicts: {other}", f"Replaces: {other}",
        "Section: hamradio", "Priority: optional", "Description: " + description]) + "\n")
    refresh = ("#!/bin/sh\nset -e\ntouch /usr/share/icons/hicolor 2>/dev/null || true\n"
               "if command -v gtk-update-icon-cache >/dev/null 2>&1; then gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true; fi\n"
               "if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database -q /usr/share/applications || true; fi\n"
               "exit 0\n")
    for script in ("postinst", "postrm"):
        (root / "DEBIAN" / script).write_text(refresh)
        (root / "DEBIAN" / script).chmod(0o755)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    deb = out / f"{package}_{deb_version}_all.deb"
    subprocess.run(["dpkg-deb", "--root-owner-group", "-Zxz", "--build", str(root), str(deb)], check=True)
    shutil.rmtree(root)
    print(deb)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else SRC / "dist")

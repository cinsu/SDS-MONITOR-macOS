// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (c) 2026 J. Lynch. See LICENSE.
// SDS100 Scanner: the Monitor's Scanner Information panel as a Plasma 6 widget (SDS100 Monitor 1.1.84).
// The Monitor keeps the scanner's port, so this asks the Monitor. Its address and key are in
// ~/SDS100Monitor/widget.json, written by the Monitor while it runs.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    property var scanner: null            // the Monitor's last answer
    property string endpoint: ""
    property string token: ""
    property bool reachable: false
    property bool asking: false
    property bool readingFile: false
    property int failures: 0
    property bool avoidArmed: false

    readonly property bool onDesktop: Plasmoid.location === PlasmaCore.Types.Floating
                                      || Plasmoid.formFactor === PlasmaCore.Types.Planar
    readonly property bool vertical: Plasmoid.formFactor === PlasmaCore.Types.Vertical
    readonly property bool connected: reachable && scanner !== null && scanner.connected === true
    readonly property bool receiving: connected && scanner.receiving === true
    readonly property string fileCommand: 'cat "$HOME/SDS100Monitor/widget.json" 2>/dev/null; echo'

    preferredRepresentation: onDesktop ? fullRepresentation : compactRepresentation
    Plasmoid.icon: "sds100-monitor"
    Plasmoid.backgroundHints: PlasmaCore.Types.DefaultBackground | PlasmaCore.Types.ConfigurableBackground
    toolTipMainText: i18n("SDS100 Scanner")
    toolTipSubText: compactLine()

    Plasmoid.contextualActions: [
        PlasmaCore.Action {
            text: i18n("Open SDS100 Monitor")
            icon.name: "sds100-monitor"
            onTriggered: root.startMonitor()
        }
    ]

    function value(key) {
        if (!scanner || !scanner.values) return ""
        const v = scanner.values[key] || ""
        return v === "—" ? "" : v
    }

    function statusText() {
        if (!reachable) return i18n("SDS100 Monitor isn't running")
        if (!scanner.connected) return i18n("Scanner not connected")
        if (scanner.special_mode) return scanner.special_mode
        return receiving ? i18n("Receiving") : (value("Mode") || i18n("Scanning"))
    }

    function compactLine() {
        if (!connected || scanner.special_mode) return statusText()
        let t = Plasmoid.configuration.compactText || "{Channel} • {Frequency}"
        t = t.replace(/\{([A-Za-z ]+)\}/g, (m, key) => root.value(key))
        t = t.replace(/(\s*[•|·]\s*)+/g, " • ").replace(/^\s*[•|·]\s*|\s*[•|·]\s*$/g, "").trim()
        return t || statusText()
    }

    function dotColor() {
        if (!reachable) return Kirigami.Theme.disabledTextColor
        if (!connected) return Kirigami.Theme.negativeTextColor
        return receiving ? Kirigami.Theme.positiveTextColor : Kirigami.Theme.textColor
    }

    // ---- talking to the Monitor -------------------------------------------------------------
    P5Support.DataSource {
        id: shell
        engine: "executable"
        connectedSources: []
        onNewData: (source, data) => {
            disconnectSource(source)
            if (source !== root.fileCommand) return
            root.readingFile = false
            try {
                const info = JSON.parse(data["stdout"])
                if (info.port && info.token) {
                    root.endpoint = "http://127.0.0.1:" + info.port
                    root.token = info.token
                    root.failures = 0
                    root.poll()
                }
            } catch (e) {
                root.endpoint = ""
            }
        }
    }

    function readFile() {
        if (readingFile) return
        readingFile = true
        shell.connectSource(fileCommand)
    }

    function lost() {
        failures += 1
        if (failures >= 2) {             // closed, or restarted with a new address: read the file again
            reachable = false
            endpoint = ""
        }
    }

    function poll() {
        if (!endpoint) { readFile(); return }
        if (asking) return
        asking = true
        const xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return
            root.asking = false
            if (xhr.status === 200) {
                try {
                    root.scanner = JSON.parse(xhr.responseText)
                    root.reachable = true
                    root.failures = 0
                    return
                } catch (e) {}
            }
            root.lost()
        }
        xhr.open("GET", endpoint + "/api/state?t=" + token)
        xhr.send()
    }

    function control(action) {
        if (!endpoint) return
        const xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) root.poll()
        }
        xhr.open("POST", endpoint + "/api/control?t=" + token + "&a=" + action)
        xhr.send()
    }

    function startMonitor() {
        // Starting it again brings an open Monitor forward (1.1.82), so this also works as "show".
        // The .deb puts sds100-monitor on the PATH; a folder install has launch.sh in ~/SDS100Monitor-<version>.
        shell.connectSource('if command -v sds100-monitor >/dev/null; then setsid -f sds100-monitor >/dev/null 2>&1; '
                            + 'else L="$(ls -d "$HOME"/SDS100Monitor-*/launch.sh 2>/dev/null | sort -V | tail -n 1)"; '
                            + '[ -n "$L" ] && setsid -f "$L" >/dev/null 2>&1; fi; true')
    }

    Timer {
        interval: root.reachable ? Math.max(250, Plasmoid.configuration.pollInterval) : 3000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: root.poll()
    }

    Timer {
        id: disarm
        interval: 4000
        onTriggered: root.avoidArmed = false
    }

    // ---- on a panel ---------------------------------------------------------------------------
    compactRepresentation: MouseArea {
        id: compactArea
        readonly property real full: row.implicitWidth + Kirigami.Units.smallSpacing * 2
        Layout.minimumWidth: root.vertical ? Kirigami.Units.iconSizes.small : full
        Layout.preferredWidth: root.vertical ? -1 : full
        Layout.maximumWidth: root.vertical ? Infinity : Kirigami.Units.gridUnit * 24
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.MiddleButton
        onClicked: mouse => {
            if (mouse.button === Qt.MiddleButton) root.startMonitor()
            else root.expanded = !root.expanded
        }

        RowLayout {
            id: row
            anchors.centerIn: parent
            width: Math.min(implicitWidth, compactArea.width)
            spacing: Kirigami.Units.smallSpacing

            Kirigami.Icon {
                visible: root.vertical
                source: "sds100-monitor"
                Layout.preferredWidth: Kirigami.Units.iconSizes.small
                Layout.preferredHeight: Kirigami.Units.iconSizes.small
            }
            Rectangle {
                Layout.preferredWidth: Kirigami.Units.smallSpacing * 2
                Layout.preferredHeight: Layout.preferredWidth
                radius: width / 2
                color: root.dotColor()
                opacity: root.receiving || !root.connected ? 1 : 0.35
            }
            PlasmaComponents.Label {
                visible: !root.vertical
                text: root.compactLine()
                elide: Text.ElideRight
                Layout.maximumWidth: Kirigami.Units.gridUnit * 22
                font.bold: root.receiving
            }
        }
    }

    // ---- the full panel (desktop, or the panel popup) -------------------------------------------
    fullRepresentation: Item {
        Layout.minimumWidth: Kirigami.Units.gridUnit * 14
        Layout.minimumHeight: Kirigami.Units.gridUnit * 6
        Layout.preferredWidth: Kirigami.Units.gridUnit * 22
        Layout.preferredHeight: body.implicitHeight + Kirigami.Units.smallSpacing * 4

        Rectangle {
            anchors.fill: parent
            radius: Kirigami.Units.smallSpacing
            color: root.connected && root.scanner.panel_bg ? root.scanner.panel_bg : "transparent"
        }

        ColumnLayout {
            id: body
            anchors.fill: parent
            anchors.margins: Kirigami.Units.smallSpacing * 2
            spacing: Kirigami.Units.smallSpacing

            RowLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing
                Rectangle {
                    Layout.preferredWidth: Kirigami.Units.smallSpacing * 2.5
                    Layout.preferredHeight: Layout.preferredWidth
                    radius: width / 2
                    color: root.dotColor()
                }
                PlasmaComponents.Label {
                    Layout.fillWidth: true
                    text: root.statusText()
                    font.bold: true
                    elide: Text.ElideRight
                    color: root.connected && root.scanner.special_mode ? Kirigami.Theme.neutralTextColor
                                                                      : Kirigami.Theme.textColor
                }
            }

            Repeater {
                model: root.reachable && root.scanner && root.scanner.lines ? root.scanner.lines.length : 0
                delegate: RowLayout {
                    required property int index
                    readonly property var line: (root.scanner && root.scanner.lines[index]) || ({})
                    Layout.fillWidth: true
                    spacing: Kirigami.Units.smallSpacing

                    PlasmaComponents.Label {
                        visible: (line.label || "") !== ""
                        text: line.label || ""
                        Layout.preferredWidth: Kirigami.Units.gridUnit * 7
                        Layout.alignment: Qt.AlignTop
                        elide: Text.ElideRight
                        color: line.fg || Kirigami.Theme.disabledTextColor
                        font.pointSize: Kirigami.Theme.smallFont.pointSize
                    }
                    PlasmaComponents.Label {
                        Layout.fillWidth: true
                        text: line.text || "—"
                        wrapMode: Text.Wrap
                        color: line.fg || Kirigami.Theme.textColor
                        font.bold: line.bold === true
                        font.pointSize: Kirigami.Theme.defaultFont.pointSize * (line.size || 100) / 100
                        leftPadding: line.bg ? Kirigami.Units.smallSpacing : 0
                        rightPadding: leftPadding
                        background: Rectangle {
                            color: line.bg || "transparent"
                            radius: 3
                        }
                    }
                }
            }

            PlasmaComponents.Button {
                visible: !root.reachable
                text: i18n("Start SDS100 Monitor")
                icon.name: "sds100-monitor"
                onClicked: root.startMonitor()
            }

            RowLayout {
                visible: root.connected && Plasmoid.configuration.showButtons
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing
                PlasmaComponents.Button {
                    text: i18n("Hold")
                    enabled: root.connected && root.scanner.can_hold === true
                    onClicked: root.control("channel_hold")
                    QQC2.ToolTip.text: i18n("Hold on the current channel")
                    QQC2.ToolTip.visible: hovered
                }
                PlasmaComponents.Button {
                    text: i18n("Scan")
                    onClicked: root.control("scan")
                    QQC2.ToolTip.text: i18n("Resume scanning")
                    QQC2.ToolTip.visible: hovered
                }
                PlasmaComponents.Button {
                    text: root.avoidArmed ? i18n("Confirm avoid") : i18n("Avoid")
                    enabled: root.connected && root.scanner.can_hold === true
                    onClicked: {
                        if (root.avoidArmed) {
                            root.avoidArmed = false
                            root.control("avoid")
                        } else {
                            root.avoidArmed = true
                            disarm.restart()
                        }
                    }
                    QQC2.ToolTip.text: i18n("Temporarily avoid the current channel (press twice)")
                    QQC2.ToolTip.visible: hovered
                }
                PlasmaComponents.Button {
                    visible: root.connected && (root.scanner.last_avoided || "") !== ""
                    text: i18n("Remove avoid")
                    onClicked: root.control("unavoid")
                    QQC2.ToolTip.text: root.connected ? (root.scanner.last_avoided || "") : ""
                    QQC2.ToolTip.visible: hovered
                }
            }

            Item { Layout.fillHeight: true }
        }
    }
}

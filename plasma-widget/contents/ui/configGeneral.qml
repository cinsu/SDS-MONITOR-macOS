// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (c) 2026 J. Lynch. See LICENSE.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.kcmutils as KCM

KCM.SimpleKCM {
    property alias cfg_pollInterval: poll.value
    property alias cfg_showButtons: buttons.checked
    property alias cfg_compactText: compact.text
    property int cfg_pollIntervalDefault
    property bool cfg_showButtonsDefault
    property string cfg_compactTextDefault

    Kirigami.FormLayout {
        QQC2.SpinBox {
            id: poll
            Kirigami.FormData.label: i18n("Update every (ms):")
            from: 250
            to: 5000
            stepSize: 250
        }
        QQC2.CheckBox {
            id: buttons
            Kirigami.FormData.label: i18n("Buttons:")
            text: i18n("Show Hold, Scan and Avoid")
        }
        QQC2.TextField {
            id: compact
            Kirigami.FormData.label: i18n("On a panel, show:")
            Layout.preferredWidth: Kirigami.Units.gridUnit * 16
            placeholderText: "{Channel} • {Frequency}"
        }
        QQC2.Label {
            Layout.preferredWidth: Kirigami.Units.gridUnit * 20
            wrapMode: Text.Wrap
            text: i18n("Fields: {Channel} {Frequency} {System} {Department} {Site} {Talkgroup} {Unit ID} {Mode} {RSSI}. "
                       + "The full panel shows the lines and colours set in the Monitor: View → Customize Scanner Information….")
        }
    }
}

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Extras 1.4

CircularGauge {
    id: gauge
    anchors.centerIn: parent
    minimumValue: 0
    maximumValue: 100
    width: 100
    height: 100
    value: backend.progress
}

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Extras 1.4

Item {
    width: 100
    height: 100

    Rectangle {
        anchors.fill: parent
      color: "#034efc"    // light grey
        radius: width/2
    }

    CircularGauge {
        id: gauge
        objectName: "sen"
        anchors.fill: parent
        minimumValue: 0
        maximumValue: 100
        value: 0
    }
}

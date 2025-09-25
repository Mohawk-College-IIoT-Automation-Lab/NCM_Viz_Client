import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Extras 1.4

Item {
    Rectangle {
        anchors.fill: parent
        color: "#535353"    // light grey
        width: parent.width 
        height: parent.height
    }
    CircularGauge {
          id: gauge
          objectName: "gauge"
          anchors.fill: parent
          minimumValue: 0
          maximumValue: 100
          value: 0
    }
}

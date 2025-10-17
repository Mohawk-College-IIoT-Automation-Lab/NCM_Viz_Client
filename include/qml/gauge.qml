import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Styles 1.4 
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

          property int min: 0
          property int max: 100 
          property int v: max / 2

          anchors.fill: parent
          minimumValue: min
          maximumValue: max
          value: v

          style: CircularGaugeStyle {
              tickmarkStepSize: gauge.max / 10
              labelStepSize: gauge.max / 10 
          }
    }
}

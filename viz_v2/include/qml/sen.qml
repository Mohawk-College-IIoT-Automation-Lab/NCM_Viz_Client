import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Extras 1.4
import QtQuick.Shapes 1.15


Item {
  id: sen
 
  property int gap: 20
  property int w: 600 
  property int h: 600

  width: w
  height: h
  

  Rectangle{
    anchors.fill: parent
    color: "#333333"

    // left face
    Rectangle {
      id: leftSen
      objectName: "leftSen"

      property int gap: 50

      width: (parent.width - sen.gap)/2
      height: parent.height
      radius: width / 12

      anchors.left: parent.left
      anchors.fill: parent.fill
      color: "#111111"

      // Left port
      Rectangle {
        id: leftPort 
        objectName: "leftPort"

        property real value: 75

        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: (parent.width - leftSen.gap) 
        height: (parent.height - 200)
        radius: width / 2           // Half of width/height to make it round
        color: "#3e4147"

        Text {
            // show label and current % dynamically
            text: `${Math.round(leftPort.value)}%`
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: leftPort.top
            anchors.bottomMargin: 8
            color: "white"
            font.pixelSize: 20
        }

        Rectangle {

          property real w: parent.width - leftSen.gap
          property real h: parent.height - leftSen.gap

          anchors.centerIn: parent
          color: "#00bbff"

          width: leftPort.value > 100 ? (w) : leftPort.value < 0 ? (0) : (leftPort.value / 100) * w
          height: leftPort.value > 100 ? (h) : leftPort.value < 0 ? (0) : (leftPort.value / 100) * h
          radius: width / 2
        }
      }
    }

    // right face
    Rectangle {
      id: rightSen
      objectName: "rightSen"

      property int gap: 50

      width: (parent.width - sen.gap)/2
      height: parent.height
      radius: width / 12

      anchors.right: parent.right
      anchors.fill: parent.fill
      color: "#111111"

      // right port
      Rectangle {
        id: rightPort 
        objectName: "rightPort"

        property real value: 25

        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: (parent.width - rightSen.gap) 
        height: (parent.height - 200)
        radius: width / 2           // Half of width/height to make it round
        color: "#3e4147"

        Text {
            // show label and current % dynamically
            text: `${Math.round(rightPort.value)}%`
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: rightPort.top
            anchors.bottomMargin: 8
            color: "white"
            font.pixelSize: 20
        }

        Rectangle {

          property real w: parent.width - rightSen.gap
          property real h: parent.height - rightSen.gap

          anchors.centerIn: parent
          color: "#00bbff"

          width: rightPort.value > 100 ? (w) : rightPort.value < 0 ? (0) : (rightPort.value / 100) * w
          height: rightPort.value > 100 ? (h) : rightPort.value < 0 ? (0) : (rightPort.value / 100) * h
          radius: width / 2
        }
      }
    }
    
  }
}




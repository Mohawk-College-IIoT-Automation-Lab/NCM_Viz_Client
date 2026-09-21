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
  height: Math.max(leftSen.height, rightSen.height)
  

  Rectangle{
    anchors.fill: parent
    color: "#333333"

    // left face
    Rectangle {
      id: leftSen
      objectName: "leftSen"

      property int gap: 20

      width: (parent.width - sen.gap)/2
      height: width + gap
      radius: width / 12

      anchors.left: parent.left
      color: "#111111"

      // Left port
      Rectangle {
        id: leftPort 
        objectName: "leftPort"

        property real value: 75

        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: (parent.width - leftSen.gap) 
        height: width
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

        // Left Opening
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

      property int gap: 20

      width: (parent.width - sen.gap)/2
      height: width + gap
      radius: width / 12

      anchors.right: parent.right
      color: "#111111"

      // right port
      Rectangle {
        id: rightPort 
        objectName: "rightPort"

        property real value: 25

        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: (parent.width - rightSen.gap) 
        height: width
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

        // Right Opening
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




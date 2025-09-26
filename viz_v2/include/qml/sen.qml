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

        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: (parent.width - leftSen.gap) 
        height: (parent.height - 200)
        radius: width / 2           // Half of width/height to make it round
        color: "#3e4147"

        Rectangle {

          id: leftPort 
          objectName: "leftPort"

          property real value: 75
          property real w: parent.width - leftSen.gap
          property real h: parent.height - leftSen.gap

          anchors.centerIn: parent
          color: "#00bbff"

          width: value > 100 ? (w) : value < 0 ? (0) : (value / 100) * w
          height: value > 100 ? (h) : value < 0 ? (0) : (value / 100) * h
          radius: width / 2
        }
      }
    }
    // Right face 
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

      // Right port
      Rectangle {

        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: (parent.width - rightSen.gap) 
        height: (parent.height - 200)
        radius: width / 2           // Half of width/height to make it round
        color: "#3e4147"

        Rectangle {

          id: rightPort 
          objectName: "rightPort"

          property real value: 25
          property real w: parent.width - rightSen.gap
          property real h: parent.height - rightSen.gap

          anchors.centerIn: parent
          color: "#00bbff"

          width: value > 100 ? (w) : value < 0 ? (0) : (value / 100) * w
          height: value > 100 ? (h) : value < 0 ? (0) : (value / 100) * h
          radius: width / 2
        }
      }
    }
  }
}




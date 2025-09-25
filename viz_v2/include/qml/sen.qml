import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Extras 1.4


Item {
    width: 800
    height: 800

    Rectangle {
      anchors.fill: parent
      color: "#111111"

    // Circle in the bottom-left
        Rectangle {
            width: (parent.width - 50) / 2
            height: (parent.height - 200)
            radius: width / 2           // Half of width/height to make it round
            color: "#3e4147"
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.margins: 10   // optional spacing from the edges
            Rectangle{
              width: parent.width - 25
              height: parent.height - 25
              radius: width / 2 
              color: "#00bbff"
              anchors.centerIn: parent
            }
          }

          Rectangle {
            width: (parent.width - 50) / 2
            height: (parent.height - 200)
            radius: width / 2            // Half of width/height to make it round
            color: "#3e4147"
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 10   // optional spacing from the edges
        }

    }
}



import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Extras 1.4


Item {
    width: 500
    height: 500

    Rectangle {
      anchors.fill: parent
      color: "#111111"

    // Circle in the bottom-left
        Rectangle {
            width: 225
            height: 350
            radius: width / 2           // Half of width/height to make it round
            color: "#3e4147"
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.margins: 10   // optional spacing from the edges
            Rectangle{

              width: 200
              height: 325
              radius: width / 2 
              color: "#ffffff"
              anchors.centerIn: parent
            }
          }

        Rectangle {
            width: 225
            height: 350
            radius: width / 2            // Half of width/height to make it round
            color: "#3e4147"
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 10   // optional spacing from the edges
        }

    }
}



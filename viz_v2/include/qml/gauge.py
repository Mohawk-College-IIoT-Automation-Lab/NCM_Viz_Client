import PyQt5
from PyQt5.QtCore import QUrl, QObject, pyqtSlot 
from PyQt5.QtWidgets import QWidget
from PyQt5.QtQuickWidgets import QQuickWidget


class GaugeWidget(QWidget):


    def __init__(self, w:int = 100, h:int = 100, min:int = 0, max:int = 100, parent = None):
        super().__init__(parent)

        _qml = QQuickWidget()
        _qml.setResizeMode(QQuickWidget.SizeRootObjectToView)
        _qml.setSource(QUrl.fromLocalFile("gauge.qml"))

        _q_root = _qml.rootObject()
        self.gauge = _q_root.findChild(QObject, "gauge")

        self.gauge.setProperty("width", w)
        self.gauge.setProperty("height", h)
        self.gauge.setProperty("minimumValue", min)
        self.gauge.setProperty("maximumValue", max)

    @pyqtSlot()
    def SetValue(self, value: int):
        self.gauge.setProperty("value", value)

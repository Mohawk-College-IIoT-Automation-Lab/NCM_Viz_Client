from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import QUrl, QObject, pyqtSlot

import logging


class QmlSenAnim(QWidget):

    LOG_FMT_STR = f"[QML] - %s"

    def __init__(self, parent):
        super().__init__(parent)

        self._qml = QQuickWidget(self)
        self._qml.setResizeMode(QQuickWidget.SizeRootObjectToView)

        self._qml.setSource(QUrl.fromLocalFile("qml/sen.qml"))

        if self._qml.status() != QQuickWidget.Ready:
            e = f"Failed to load qml: {self._qml.errors()}"
            logging.error(QmlSenAnim.LOG_FMT_STR, e)
            raise RuntimeError(e)

        _qml_root = self._qml.rootObject()
        self._l_port_root = _qml_root.findChild(QObject, "LeftPort")
        self._r_port_root = _qml_root.findChild(QObject, "RightPort")

        if not self._l_port_root or not self._r_port_root:
            e = f"Failed to find children in qml"
            logging.error(QmlSenAnim.LOG_FMT_STR, e)
            raise RuntimeError(e)

    @pyqtSlot()
    def SetSenAnimPorts(
        self, leftPort: int | None = None, rightPort: int | None = None
    ):
        if leftPort:
            # do something
            pass
        if rightPort:
            # do something
            pass


class SenWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        """ A central H box will hold 3 v boxs 
            - The left most vbox will be gauges
            - The center will be the sen animation
            - The right most vbox will be telemetry graphs
        """

        center_h_box = QHBoxLayout(self)
        gauge_v_box = QVBoxLayout()
        anim_v_box = QVBoxLayout()
        tele_v_box = QVBoxLayout()

        center_h_box.addLayout(gauge_v_box)
        center_h_box.addLayout(anim_v_box)
        center_h_box.addLayout(tele_v_box)
        self.setLayout(center_h_box)

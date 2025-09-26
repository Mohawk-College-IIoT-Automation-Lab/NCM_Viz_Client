from PyQt5.QtCore import pyqtSlot, QUrl
from PyQt5.QtWidgets import QSizePolicy, QWidget
from PyQt5.QtQuickWidgets import QQuickWidget
from pathlib import Path

import logging

class SenAnimWidget(QWidget):

    LOG_FMT_STR =  f"[Qml] - %s"

    def __init__(self, min:int = 0, max:int = 100, parent = None):
        super().__init__(parent)

        self._min = min 
        self._max = max

        _qml = QQuickWidget(self)
        # Resolve the QML file relative to THIS Python file, not the CWD
        base_dir = Path(__file__).resolve().parent
        qml_file = base_dir / "sen.qml"

        _qml.setSource(QUrl.fromLocalFile(str(qml_file)))

        if _qml.status() != QQuickWidget.Ready:
            e = f"Failed to load qml: {_qml.errors()}"
            logging.error(SenAnimWidget.LOG_FMT_STR, e)
            raise RuntimeError(e)

        # self._left_port = _qml.findChild(QObject, "LeftPort")
        # self._right_port = _qml.findChild(QObject, "rightPort")

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    @pyqtSlot()
    def SetPortValue(self, leftPort: int | None = None, rightPort: int | None = None):
        if leftPort:
            if self._min <= leftPort <= self._max: 
                self._left_port.setProperty("value", leftPort)

        if rightPort:
            if self._min <= rightPort <= self._max:
                self._right_port.setProperty("value", rightPort)

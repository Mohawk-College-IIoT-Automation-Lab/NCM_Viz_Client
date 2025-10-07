from PyQt5.QtCore import QUrl, QObject, pyqtSlot, Qt
from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtQuick import QQuickItem
import sys
from pathlib import Path

import logging

class GaugeWidget(QWidget):

    LOG_FMT_STR =  f"[Qml] - %s"


    def __init__(self, w:int = 100, h:int = 100, min:int = 0, max:int = 100, title:str = "default", label_color:str = "#ffffff", label_size:int=20, parent = None):
        super().__init__(parent)

        _qml = QQuickWidget()

        # Resolve the QML file relative to THIS Python file, not the CWD
        base_dir = Path(__file__).resolve().parent
        qml_file = base_dir / "gauge.qml"

        _qml.setSource(QUrl.fromLocalFile(str(qml_file)))
        _qml.setResizeMode(QQuickWidget.SizeRootObjectToView)
        
        if _qml.status() != QQuickWidget.Ready:
            e = f"Failed to load qml: {_qml.errors()}"
            logging.error(GaugeWidget.LOG_FMT_STR, e)
            raise RuntimeError(e)

        _q_root = _qml.rootObject()
        self.gauge = _q_root.findChild(QObject, "gauge")

        self.gauge.setProperty("min", min)
        self.gauge.setProperty("max", max)

        _v_box = QVBoxLayout(self)
        _title_label = QLabel(title)
        _title_label.setStyleSheet(f"font-size: {str(label_size)}px; color: {label_color}")
        
        _v_box.addWidget(_title_label, alignment=Qt.AlignCenter)
        _v_box.addWidget(_qml)

        self.setLayout(_v_box)
        self.setMinimumSize(w, h)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    @pyqtSlot(int)
    def SetValue(self, value: int):
        self.gauge.setProperty("v", value)

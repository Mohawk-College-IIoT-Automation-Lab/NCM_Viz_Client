from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import QUrl, QObject, pyqtSlot

import logging





class SenWidget(QWidget):

    LOG_FMT_STR =  f"[SEN] - %s"

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

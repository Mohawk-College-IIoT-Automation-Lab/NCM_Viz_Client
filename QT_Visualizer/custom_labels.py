from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QColor, QPalette

class AlarmLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAutoFillBackground(True)
        self.state = False
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_style()

    @pyqtSlot()
    def on(self):
        self.state = True
        self.update_style()

    @pyqtSlot()
    def off(self):
        self.state = False
        self.update_style()

    @pyqtSlot()
    def toggle(self):
        self.state = not self.state
        self.update_style()

    def update_style(self):
        palette = self.palette()
        color = QColor("lightgreen") if self.state else QColor("lightcoral")
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)
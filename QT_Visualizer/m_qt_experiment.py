from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from m_qobject import M_QObject


class QExperimentControlWidget(QWidget):

    def __init__(self, parent=None, host_name:str="localhost", host_port:int=1883, **kargs):
        super().__init__(parent, **kargs)

        self.v_box_layout = QVBoxLayout(self)
        self.v_box_layout.addWidget(QLabel("Hello"))

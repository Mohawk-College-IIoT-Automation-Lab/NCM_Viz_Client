from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QAction, QMenuBar

class MenuBar(QMenuBar):



    _instance = None

    @classmethod
    def get_instance(cls, parent=None):
        if cls._instance is None:
            cls._instance = cls(parent)
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)

        self.CloseAppAction = QAction("Close App")
        self.StartExpAction = QAction("Start Experiment")
        self.RenameExpAction = QAction("Rename Experiment")
        self.StopExpAction = QAction("Stop Experiment")

        self.SenMoveToMMAction = QAction("Move to MM")
        self.SenMoveToPosAction = QAction("Move to Pos")
        self.SenMoveToIdxAction = QAction("Move to Index")

        exp_menu = self.addMenu("Experiment")
        sen_menu = self.addMenu("SEN")

        exp_menu.addAction(self.StartExpAction)
        exp_menu.addAction(self.RenameExpAction)
        exp_menu.addAction(self.StopExpAction)

        sen_menu.addAction(self.SenMoveToMMAction)
        sen_menu.addAction(self.SenMoveToPosAction)
        sen_menu.addAction(self.SenMoveToIdxAction)





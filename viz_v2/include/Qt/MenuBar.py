from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QAction, QMenuBar 


class MenuBar(QMenuBar):

    CloseAppAction = QAction("Close App")
    StartExpAction = QAction("Start Experiment")
    RenameExpAction = QAction("Rename Experiment")
    StopExpAction = QAction("Stop Experiment")

    SenMoveToMMAction = QAction("Move to MM")
    SenMoveToPosAction = QAction("Move to Pos")
    SenMoveToIdxAction = QAction("Move to Index")

    @classmethod
    def get_instance(cls, parent=None):
        if cls._instance is None:
            cls._instance = cls(parent)
        return cls._instance

    def __init__(self, parent = None):
        super().__init__(parent)

        exp_menu = self.addMenu("Experiment")
        sen_menu = self.addMenu("SEN")

        exp_menu.addAction(MenuBar.StopExpAction)
        exp_menu.addAction(MenuBar.RenameExpAction)
        exp_menu.addAction(MenuBar.StopExpAction)

        sen_menu.addAction(MenuBar.SenMoveToMMAction)
        sen_menu.addAction(MenuBar.SenMoveToPosAction)
        sen_menu.addAction(MenuBar.SenMoveToIdxAction)


        

from PyQt5.QtWidgets import QAction, QMenuBar 


class MenuBar(QMenuBar):

    CloseAppAction = QAction("Close App")
    StartExpAction = QAction("Start Experiment")
    RenameExpAction = QAction("Rename Experiment")
    StopExpAction = QAction("Stop Experiment")

    def __init__(self, parent = None):
        super().__init__(parent)

        app_menu = self.addMenu("App")
        exp_menu = self.addMenu("Experiment")
        ctrl_menu = self.addMenu("Control")

        app_menu.addAction(MenuBar.CloseAppAction)

        exp_menu.addAction(MenuBar.StopExpAction)
        exp_menu.addAction(MenuBar.RenameExpAction)
        exp_menu.addAction(MenuBar.StopExpAction)


        

from PyQt5.QtWidgets import QToolBar, QMainWindow, QMenuBar

class M_QToolBar(QToolBar):
    def __init__(self, title:str, parent:QMainWindow):
        super().__init__(title, parent)
        self.setMovable(False)
        self.setFloatable(False)


class M_QMenuBar(QMenuBar):
    def __init__(self, title:str, parent:QMainWindow):
        super().__init__(parent)
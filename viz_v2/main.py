#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication
import sys, signal
import os
from include.MainWindow import MainWindow

app = QApplication(sys.argv)


def handle_signals(*args):
    app.quit()


if __name__ == "__main__":
    # Check os and set xcb
    if os.name != "nt":
        os.environ["QT_QPA_PLATFORM"] = "xcb"

    # handle signals
    signal.signal(signal.SIGINT, handle_signals)
    signal.signal(signal.SIGTERM, handle_signals)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())


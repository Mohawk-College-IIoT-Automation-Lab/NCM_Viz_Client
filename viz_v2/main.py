from PyQt5.QtWidgets import QApplication
import sys, signal 

app = QApplication(sys.argv)

def handle_signals(*args):
    app.quit()

if __name__ == "__main__":
    # initialize central logger 

    # handle signals 
    signal.signal(signal.SIGINT, handle_signals)
    signal.signal(signal.SIGTERM, handle_signals)

    # create main window 

    # show main window 

    # run the app and wait for exit 
    sys.exit(app.exec_())

    # clean up or indicate to broker that disconnect 

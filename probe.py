import sys
import yaml

from PyQt4 import QtCore, QtGui
from wizard_ui import Ui_MainWindow


class WizardUI(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.actions = []
        self.actions_map = {"Action 1", }

        self.ui.actionOpen.triggered.connect(self.open_file)
        #self.ui.pushButton.clicked.connect(self.next_action)

    def open_file(self):
        # The QWidget widget is the base class of all user interface objects in PyQt4.
        w = QtGui.QWidget()
        w.resize(320, 240)
        w.setWindowTitle("Hello World!")
        filename = QtGui.QFileDialog.getOpenFileName(w, 'Open File', '~')
        with open(filename, 'r') as f:
            self.actions = yaml.safe_load(f)
            f.close()
        w.show()

        print self.actions

    #def next_action(self):



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = WizardUI()
    myapp.show()
    sys.exit(app.exec_())
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wizard-interface.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(833, 354)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 833, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuOpen = QtGui.QMenu(self.menubar)
        self.menuOpen.setObjectName(_fromUtf8("menuOpen"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QtGui.QDockWidget(MainWindow)
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout_3 = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(4), self.dockWidget)
        self.dockWidget_3 = QtGui.QDockWidget(MainWindow)
        self.dockWidget_3.setObjectName(_fromUtf8("dockWidget_3"))
        self.dockWidgetContents_8 = QtGui.QWidget()
        self.dockWidgetContents_8.setObjectName(_fromUtf8("dockWidgetContents_8"))
        self.gridLayout_2 = QtGui.QGridLayout(self.dockWidgetContents_8)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_2 = QtGui.QLabel(self.dockWidgetContents_8)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 3, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.dockWidgetContents_8)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 4, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.dockWidgetContents_8)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 4, 1, 1, 1)
        self.stimuActionOneButton = QtGui.QPushButton(self.dockWidgetContents_8)
        self.stimuActionOneButton.setObjectName(_fromUtf8("stimuActionOneButton"))
        self.gridLayout_2.addWidget(self.stimuActionOneButton, 5, 0, 1, 1)
        self.stimuActionTwoButton = QtGui.QPushButton(self.dockWidgetContents_8)
        self.stimuActionTwoButton.setObjectName(_fromUtf8("stimuActionTwoButton"))
        self.gridLayout_2.addWidget(self.stimuActionTwoButton, 5, 1, 1, 1)
        self.pushButton = QtGui.QPushButton(self.dockWidgetContents_8)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout_2.addWidget(self.pushButton, 1, 0, 1, 1)
        self.pushButton_2 = QtGui.QPushButton(self.dockWidgetContents_8)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.gridLayout_2.addWidget(self.pushButton_2, 1, 1, 1, 1)
        self.label = QtGui.QLabel(self.dockWidgetContents_8)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 3, 0, 1, 1)
        self.stimuOneFeedback = QtGui.QPushButton(self.dockWidgetContents_8)
        self.stimuOneFeedback.setObjectName(_fromUtf8("stimuOneFeedback"))
        self.gridLayout_2.addWidget(self.stimuOneFeedback, 6, 0, 1, 1)
        self.stimuTwoFeedback = QtGui.QPushButton(self.dockWidgetContents_8)
        self.stimuTwoFeedback.setObjectName(_fromUtf8("stimuTwoFeedback"))
        self.gridLayout_2.addWidget(self.stimuTwoFeedback, 6, 1, 1, 1)
        self.dockWidget_3.setWidget(self.dockWidgetContents_8)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockWidget_3)
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.menuOpen.addAction(self.actionOpen)
        self.menubar.addAction(self.menuOpen.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Wizard", None))
        self.menuOpen.setTitle(_translate("MainWindow", "File", None))
        self.label_2.setText(_translate("MainWindow", "0", None))
        self.label_3.setText(_translate("MainWindow", "Current time:", None))
        self.label_4.setText(_translate("MainWindow", "0", None))
        self.stimuActionOneButton.setText(_translate("MainWindow", "Screen Training (Sound and Button)", None))
        self.stimuActionTwoButton.setText(_translate("MainWindow", "Highfive Training", None))
        self.pushButton.setText(_translate("MainWindow", "Next Action", None))
        self.pushButton_2.setText(_translate("MainWindow", "Turn Off", None))
        self.label.setText(_translate("MainWindow", "No. Action:", None))
        self.stimuOneFeedback.setText(_translate("MainWindow", "Screen Training (Speech and Button)", None))
        self.stimuTwoFeedback.setText(_translate("MainWindow", "Powerhand Training", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))


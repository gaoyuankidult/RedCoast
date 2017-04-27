import sys
import yaml
import time

from PyQt4 import QtGui
from PyQt4 import QtCore
from wizard import Ui_MainWindow

from redcoast import Robot

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

class WizardUI(QtGui.QMainWindow):

    def __init__(self, parent=None, robot = None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.robot = robot


        self.log = []

        self.explicit_actions = []
        self.no_explicit_action = 0 # number of explicit action
        self.no_implicit_action = 0  # number of explicit action
        self.robot.memory.raiseEvent("PicNumber", 0)

        def say_and_raise(args1, args2):
            robot.memory.raiseEvent(*args2)
            robot.say(*args1)


        self.actions_map = {"Action 1": [robot.say, ["Hello - welcome to our lab"]],
                            "Action 2": [robot.say, ["My name is Pepper, and I will be helping you today to build a LEGO robot."]],
                            "Action 3": [robot.say, ["Your task is fun! All you have to do is look at the LEGO manual and follow the instructions"]],
                            "Action 4": [robot.say, ["There are several instructions that are missing, and I will be helping you with them through my screen"]],
                            "Action 5": [say_and_raise, [["Look at my screen. This is what you have to build"], ["PicNumber", 99]]],
                            "Action 6": [robot.say, ["When you are ready then we can start... So are you ready ?"]],
                            "Action 7": [robot.say, ["Now you can start !"]],

                            "Milestone 1": [say_and_raise, [["This page is missing, I can show it to you."],["PicNumber", 1]]],
                            "Milestone 2": [say_and_raise, [["Look at here. I have the missing page."],["PicNumber", 2]]],
                            "Milestone 3": [say_and_raise, [["Oh, it is missing again"],["PicNumber", 3]]],
                            "Milestone 4": [say_and_raise, [["I can also help you with this one"],["PicNumber", 4]]],
                            "Milestone 5": [say_and_raise, [["Another missing page."], ["PicNumber", 5]]],
                            "Milestone 6": [say_and_raise, [["I also have this one, have a look."], ["PicNumber", 6]]],
                            "Milestone 7": [say_and_raise, [["We are almost done. Hope this is the final missing page."], ["PicNumber", 7]]],

                            "Final 1": [robot.say, ["Well done, you made it. Congratulations!"]],

                            "train 1": [robot.memory.raiseEvent, ["ButtonToBePressed", 8]],
                            "train 2": [robot.memory.raiseEvent, ["HighFiveToBeResponded", 1]],
                            "train 3": [robot.memory.raiseEvent, ["ButtonToBePressed", 1]],
                            "train 4": [robot.memory.raiseEvent, ["PowerHandToBeResponsed", 1]],

                            "Pre-study": [robot.say, ["Pre-study starts here. Hello, there !"]],

                            # After milestone 1
                            "Attractor 1": [robot.memory.raiseEvent, ["HighFiveToBeResponded", 2]],
                            "Attractor 2": [robot.memory.raiseEvent, ["ButtonToBePressed", 2]],

                            # After milestone 2
                            "Attractor 3": [robot.memory.raiseEvent, ["PowerHandToBeResponsed", 2]],
                            "Attractor 4": [robot.memory.raiseEvent, ["ButtonToBePressed", 3]],


                            # After milestone 3
                            "Attractor 5": [robot.memory.raiseEvent, ["HighFiveToBeResponded", 3]],
                            "Attractor 6": [robot.memory.raiseEvent, ["ButtonToBePressed", 4]],


                            # After milestone 4
                            "Attractor 7": [robot.memory.raiseEvent, ["HighFiveToBeResponded", 4]],
                            "Attractor 8": [robot.memory.raiseEvent, ["ButtonToBePressed", 5]],

                            # After milestone 5
                            "Attractor 9": [robot.memory.raiseEvent, ["PowerHandToBeResponsed", 3]],
                            "Attractor 10": [robot.memory.raiseEvent, ["ButtonToBePressed", 6]],


                            # After milestone 6
                            "Attractor 11": [robot.memory.raiseEvent, ["PowerHandToBeResponsed", 4]],
                            "Attractor 12": [robot.memory.raiseEvent, ["ButtonToBePressed", 6]],

                            # After milestone 7
                            "Attractor 13": [robot.memory.raiseEvent, ["HighFiveToBeResponded", 5]],
                            "Attractor 14": [robot.memory.raiseEvent, ["ButtonToBePressed", 7]],



                            }
#"To make me feel energetic, you can touch my screen. Try it!"

        self.action_labels = [QtGui.QLabel(self.ui.dockWidgetContents) for action_name in self.actions_map.keys()]
        self.action_texts = [QtGui.QLabel(self.ui.dockWidgetContents) for action_name in self.actions_map.values()]



        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.pushButton.clicked.connect(self.next_action)
        self.ui.pushButton_2.clicked.connect(self.screen_off)

        self.ui.stimuActionOneButton.clicked.connect(self.training_one)
        self.ui.stimuActionTwoButton.clicked.connect(self.training_two)

        self.ui.stimuOneFeedback.clicked.connect(self.training_three)
        self.ui.stimuTwoFeedback.clicked.connect(self.training_four)
        self.started = False

    def screen_off(self):
        self.robot.memory.raiseEvent("PicNumber", 0)

    def training_one(self):
        print "here"
        func, args = self.actions_map["train 1"]
        print func, args
        func(*args)

    def training_two(self):
        func, args = self.actions_map["train 2"]
        func(*args)

    def training_three(self):
        func, args = self.actions_map["train 3"]
        func(*args)

    def training_four(self):
        func, args = self.actions_map["train 4"]
        func(*args)

    def error(self, message):
        messageBox = QtGui.QMessageBox()
        messageBox.setText(message)
        messageBox.exec_()

    def open_file(self):
        if len(self.explicit_actions) is not 0:
            self.error("Actions are already loaded.")
        else:
            self.start_time = time.time()

            w = QtGui.QWidget()
            w.resize(320, 240)
            w.setWindowTitle("Open File")
            filename = QtGui.QFileDialog.getOpenFileName(w, 'Open File', '/media/alex/22E67196E6716AC5/Research/02-03-2017-Probe/Data')
            with open(filename, 'r') as f:
                actions_information = yaml.safe_load(f)
                self.excute_implicit = actions_information["excute_implicit"]
                self.implicit_actions = actions_information["implicit_actions"]
                self.explicit_actions = actions_information["explicit_actions"]
                self.before_action = actions_information["before_action"]
                self.after_action = actions_information["after_action"]
                self.action_time = actions_information["action_time"]
                self.ui.pushButton.setText("Start")
            self.max_actions = len(self.explicit_actions)

            # display all the actions
            for i in xrange(0, len(self.explicit_actions)):
                self.action_labels[i].setObjectName(_fromUtf8("Action %d:" % (i + 1)))
                self.action_labels[i].setText(_translate("MainWindow", "Action %d:" % (i + 1),
                                                         None))  # we use self.actions_map[action_name][1][0] here cause no matter function we use, what robot says is always at position [1][2]
                self.ui.gridLayout_3.addWidget(self.action_labels[i], i, 0, 2, 6)

                self.action_texts[i].setObjectName(_fromUtf8("Action %d:" % (i + 1)))
                self.action_texts[i].setText(_translate("MainWindow", str(self.actions_map[self.explicit_actions[i]][1]),
                                                        None))  # we use self.ac tions_map[action_name][1][0] here cause no matter function we use, what robot says is always at position [1][2]
                self.ui.gridLayout_3.addWidget(self.action_texts[i], i, 1, 2, 6)
            w.show()

    def threaded_function(self):
        for i in range(10):
            print time.time()

    def next_action(self):
        if self.ui.pushButton.text() == "Start":
            current_time = time.time() - self.start_time
            self.log.append(["Start", current_time])
            self.ui.pushButton.setText("Next Action")
            self.started = True
            if self.excute_implicit:
                time.sleep(self.before_action)
                self.actions_map[self.implicit_actions[self.no_implicit_action]]()
                self.no_implicit_action += 1
                time.sleep(self.after_action)

        else:
            if len(self.explicit_actions) is not 0 and self.started is True:

                if self.no_explicit_action <= self.max_actions-1:

                    current_time = time.time() - self.start_time


                    # execute explicit actions
                    action_type = self.explicit_actions[self.no_explicit_action]
                    print action_type

                    if action_type.startswith("Milestone"):
                        func, args = self.actions_map[self.explicit_actions[self.no_explicit_action]]
                        func(*args)
                        self.no_explicit_action += 1

                        func, args = self.actions_map[self.explicit_actions[self.no_explicit_action]]
                        func(*args)
                        self.no_explicit_action += 1

                        self.ui.label_2.setText(str(self.no_explicit_action))
                        self.ui.label_4.setText("%.2f s" % current_time)

                        self.log.append([self.no_explicit_action, current_time])

                        # execute implicit actions

                        if self.excute_implicit:
                            time.sleep(self.before_action)
                            self.actions_map[self.implicit_actions[self.no_implicit_action]]()
                            self.no_implicit_action += 1
                            time.sleep(self.after_action)

                        if self.no_explicit_action == self.max_actions:
                            self.ui.pushButton.setText("Stopped.")
                            with open('/media/alex/22E67196E6716AC5/Research/02-03-2017-Probe/Data/log.yaml',
                                      'w') as outfile:
                                yaml.dump(self.log, outfile, default_flow_style=False)
                    else:
                        func, args = self.actions_map[self.explicit_actions[self.no_explicit_action]]
                        func(*args)
                        self.no_explicit_action += 1
                        self.ui.label_2.setText(str(self.no_explicit_action))
                        self.ui.label_4.setText("%.2f s" % current_time)

                        self.log.append([self.no_explicit_action, current_time])

                        # execute implicit actions

                        if self.excute_implicit:
                            time.sleep(self.before_action)
                            self.actions_map[self.implicit_actions[self.no_implicit_action]]()
                            self.no_implicit_action += 1
                            time.sleep(self.after_action)

                        if self.no_explicit_action == self.max_actions:
                            self.ui.pushButton.setText("Stopped.")
                            with open('/media/alex/22E67196E6716AC5/Research/02-03-2017-Probe/Data/log.yaml', 'w') as outfile:
                                yaml.dump(self.log, outfile, default_flow_style=False)

                else:
                    self.error("All actions have been executed.")

            else:
                self.error("No actions loaded.")



if __name__ == "__main__":
    IP = "130.238.17.48"
    robot = Robot(IP, 9559, 0)
    robot.start()

    app = QtGui.QApplication(sys.argv)
    myapp = WizardUI(robot=robot)
    myapp.show()
    sys.exit(app.exec_())
from paramiko import SSHClient
from paramiko import AutoAddPolicy
from scp import SCPClient

import time

import sys

class RobotSpeechMixin(object):

    def adjust_speech_parameters(self, pitch=100, speed=100):
        self.speech_pitch = pitch
        self.speech_speed = speed

    def say(self, something, animation="animations/Stand/Gestures/Explain_1"):
        configuration = {"bodyLanguageMode": "random"}
        parameters = "\\vct=%d\\\\rspd=%d\\" % (self.speech_pitch, self.speech_speed)
        if animation is None:
            self.speech.say(parameters + something, configuration)
        else:
            self.speech.say(parameters + "^start(%s) " % animation + something + " ^wait(%s)" % animation,
                            configuration)

    def say_hello(self):
        self.say("Hello!")

class RobotConnectionMixin(object):
    def scp_send(self, filename):
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(self.ip, 22, username="nao", password="pepper")
        scp = SCPClient(client.get_transport())
        scp.put("/home/alex/Desktop/RedCoast/robot/" + filename, "/home/nao/"+ filename.split('/')[-1])
        client.close()


class RobotDialogMixin(object):
    def start_dialog(self, dialog_files):
        # just to ensure all topics are unloaded
        [self.dialog.unloadTopic(x) for x in self.dialog.getActivatedTopics()]


        # load and try to activate all topics to check integrity.
        for dialog_file in dialog_files:
            self.load_topic(dialog_file)
        self.dialog.subscribe('ExperimentModule')

        # check the status of the robot if the conversation has finished then switch to interaction mode.
        self.memory.insertData("robot", 0)

        #TODO this is for debugging purposes. need to be deleted latter.
        self.memory.insertData("robot", 1)
        while 1:
            time.sleep(1)
            if self.memory.getData("robot") == 1:
                self.end_dialog()
                break

    def end_dialog(self):
        self.unload_topic("dialog/introduction.top")
        self.dialog.unsubscribe("ExperimentModule")

    def load_topic(self, dialog_file):
        self.scp_send(dialog_file)


        self.dialog.setLanguage("English")
        dialog_file = dialog_file.decode("utf-8")

        # in case the file erroneously loaded
        try:
            self.focus_topic = self.dialog.loadTopic(("/home/nao/"+ dialog_file.split('/')[-1]).encode("utf-8"))
        except Exception:   # when topic is already loaded
            print "Tried to load file experienced exception:", sys.exc_info()
            self.unload_topic(dialog_file)
            self.focus_topic = self.dialog.loadTopic(("/home/nao/" + dialog_file.split('/')[-1]).encode("utf-8"))
        self.dialog.activateTopic(self.focus_topic)

    def unload_topic(self, dialog_file=None):
        if dialog_file is not None:
            topic = (dialog_file.split('/')[-1].split('.')[0]).encode("utf-8")
            self.dialog.deactivateTopic(topic)
            self.dialog.unloadTopic(topic)
        else:
            self.dialog.deactivateTopic(self.focus_topic)
            self.dialog.unloadTopic(self.focus_topic)

class RobotGesturesMixin(object):
    def open_lefthand(self):
        self.motion.openHand('LHand')

    def open_righthand(self):
        self.motion.openHand('RHand')


class RobotPostureMixin(object):
    def go_to_neutral(self):
        self.posture.goToPosture("Stand",1)

"""
        def move_control(out, last_time):

            if out[0] < -0.5:
                rot = 3.1415 * 0.2
            elif out[0] > 0.5:
                rot = -3.1415 * 0.2
            else:
                rot = 0.0

            if out[1] < -0.5:
                forw = 0.08
            elif out[1] > 0.5:
                forw = -0.08
            else:
                forw = 0

            if out[3] < -0.5:
                side = 0.08
            elif out[3] > 0.5:
                side = -0.08
            else:
                side = 0.0

            if time.time() - last_time > 0.1:
                self.robot.motion.move(forw, side, rot)
                return time.time()
            return last_time
"""

"""
    def move_arm(self, effectorName):
        isEnabled = True
        self.motion.wbEnableEffectorControl(effectorName, isEnabled)

        # Example showing how to set position target for LArm
        # The 3 coordinates are absolute LArm position in NAO_SPACE
        # Position in meter in x, y and z axis.

        # X Axis LArm Position feasible movement = [ +0.00, +0.12] meter
        # Y Axis LArm Position feasible movement = [ -0.05, +0.10] meter
        # Y Axis RArm Position feasible movement = [ -0.10, +0.05] meter
        # Z Axis LArm Position feasible movement = [ -0.10, +0.10] meter

        coef = 2.0
        # Send robot to Stand Init
        # postureProxy.goToPosture("StandInit", 0.5)

        frame = motion.FRAME_ROBOT
        useSensor = False

        effectorInit = self.motion.getPosition("LArm", frame, useSensor)

        targetCoordinateList = [
        [ +0.12, +0.00*coef, +0.00], # target 0
        [ +0.12, +0.00*coef, -0.10], # target 1
        [ +0.12, +0.05*coef, -0.10], # target 1
        [ +0.12, +0.05*coef, +0.10], # target 2
        [ +0.12, -0.10*coef, +0.10], # target 3
        [ +0.12, -0.10*coef, -0.10], # target 4
        [ +0.12, +0.00*coef, -0.10], # target 5
        [ +0.12, +0.00*coef, +0.00], # target 6
        [ +0.00, +0.00*coef, +0.00], # target 7
        ]


        # wbSetEffectorControl is a non blocking function
        # time.sleep allow head go to his target
        # The recommended minimum period between two successives set commands is
        # 0.2 s.
        for targetCoordinate in targetCoordinateList:
            targetCoordinate = [targetCoordinate[i] + effectorInit[i] for i in range(3)]
            self.motion.wbSetEffectorControl(effectorName, targetCoordinate)
            time.sleep(4.0)

        # Deactivate Head tracking
        isEnabled    = False
        self.motion.wbEnableEffectorControl(effectorName, isEnabled)

"""

class RobotVisionMixin(object):
    def get_image(self):
        pass
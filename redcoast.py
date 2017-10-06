from naoqi import ALProxy

import motion

import threading
import zmq

from alg import Exp3

from robot import Strategy
from robot import RobotNanogramExperiment

from robot import RobotSpeechMixin
from robot import RobotDialogMixin  # RobotSpeechMixedin depends on RobotConnectionMixedin
from robot import RobotConnectionMixin
from robot import RobotGesturesMixin
from robot import RobotVisionMixin
from robot import RobotPostureMixin

import qi


class Robot(threading.Thread,
            RobotSpeechMixin,
            RobotDialogMixin,
            RobotConnectionMixin,
            RobotGesturesMixin,
            RobotVisionMixin,
            RobotPostureMixin):

    def __init__(self, ip, port, joystick_id):
        def rfun(action):
            """ implementation of reward function

            :return:
            """
            configuration = {"bodyLanguageMode": "disable"}
            animation = "animations/Stand/Gestures/Explain_1"
            self.speech.say("^start(%s) " % animation + self.strategy.execute(action) + " ^wait(%s)" % animation,
                            configuration)
            return float(raw_input("Input reward (float)"))

        threading.Thread.__init__(self)
        self.daemon = True

        self.ip = ip
        self.port = port
        self.joystick_id = joystick_id

        connection_url = "tcp://" + self.ip + ":" + str(self.port)
        self.app = qi.Application(["NonogramTeacher", "--qi-url=" + connection_url])
        self.app.start()
        self.session = self.app.session
        
        #self.memory = ALProxy("ALMemory", self.ip, self.port)
        self.memory = self.session.service("ALMemory")

        self.speech_pitch = 100
        self.speech_speed = 100
        self.speech = ALProxy("ALAnimatedSpeech", self.ip, self.port)

        self.sound = ALProxy("ALSoundDetection", self.ip, self.port)
        self.sound.setParameter("Sensitivity", 0.0)

        self.dialog = ALProxy("ALDialog", self.ip, self.port)
        self.focus_topic = None

        self.posture = ALProxy("ALRobotPosture", self.ip, self.port)
        self.motion = ALProxy("ALMotion", self.ip, self.port)

        self.strategy = Strategy()
        self.experiment = RobotNanogramExperiment(robot=self)
        self.algorithm = Exp3(4, 0.1, self.experiment, debug=1)

        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % "5556")
        
    def run(self):
        niter = 50
        
        self.algorithm.run(niter)

if __name__ == "__main__":
    import sys

    sys.path.insert(0, "nonogram/gamelib")

    import pygame
    import main

    IP = "130.238.17.60"
    robot = Robot(IP, 9559, 0)
    robot.start()

    pygame.init()
    main.main()



from naoqi import ALProxy

import motion

import threading
import time
import almath

from alg import Exp3

import scp

from robot import Strategy
from robot import RobotNanogramExperiment
from robot import RobotSpeechMixin
from robot import RobotDialogMixedin

class Robot(threading.Thread, RobotSpeechMixin, RobotDialogMixedin):

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
        self.speech_pitch = 100
        self.speech_speed = 100

        self.speech = ALProxy("ALAnimatedSpeech", self.ip, self.port)

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


import sys
sys.path.insert(0, "nonogram/gamelib")

import pygame
import main

if __name__ == "__main__":
    IP = "130.238.150.236"
    robot = Robot(IP, 9559, 0)
    robot.start()

    pygame.init()
    main.main()



class RobotSpeechMixin(object):
    def say(self, something, animation="animations/Stand/Gestures/Explain_1"):
        configuration = {"bodyLanguageMode": "disable"}
        if animation is None:
            self.speech.say(something, configuration)
        else:
            self.speech.say("^start(%s) " % animation + something + " ^wait(%s)" % animation,
                            configuration)



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
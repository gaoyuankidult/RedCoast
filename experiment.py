import pygame
import time
import robot_methods

pygame.init()


class RewardMixin(object):
    def __init__(self):
        self.reward = 0


class UserRewardMixin(RewardMixin):

    def get_joystick_vector(self):
        out = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        it = 0  # iterator

        # Read input from the two joysticks
        for i in range(0, self.jstick.get_numaxes()):
            out[it] = self.jstick.get_axis(i)
            it += 1
        # Read input from buttons
        for i in range(0, self.jstick.get_numbuttons()):
            out[it] = self.jstick.get_button(i)
            it += 1
        return out

    def joystick_to_reward(self):

        while True:
            pygame.event.pump()
            self.out = self.get_joystick_vector()

            if self.out[6] == 1:
                self.reward = 0.2
                break
            elif self.out[7] == 1:
                self.reward = 0.4
                break
            elif self.out[8] == 1:
                self.reward = -0.2
                break
            elif self.out[9] == 1:
                self.reward = -0.4
                break
        return self.reward


class StaticRewardMixin(RewardMixin):
    def __init__(self):
        super(StaticRewardMixin, self).__init__()



class Experiment(object):
    """Implementation of Experiment class.

    """

    def __init__(self):
        assert issubclass(self.__class__, RewardMixin) == True, \
            "Robot experiment should have at lest one RewardMixin as its super class."

    def rfun(action):
        pass


class StaticExperiment(Experiment):
    """ implementation of a Simple Experiment with static reward function.

    """

    def __init__(self):
        super(StaticExperiment, self).__init__()

    @staticmethod
    def rfun(action):
        if action == 1:
            return 3
        elif action == 2:
            return 2
        else:
            return 0


class RobotExperiment(Experiment, UserRewardMixin):

    def __init__(self, robot):
        super(RobotExperiment, self).__init__()
        self.robot = robot
        self.jstick = pygame.joystick.Joystick(self.robot.joystick_id)
        self.jstick.init()
        print 'Initialized Joystick : %s' % self.jstick.get_name()

    def execute(self, action):
        animation = "animations/Stand/Gestures/Explain_1"
        assert issubclass(self.robot.__class__, robot_methods.RobotSpeechMixin), \
            "Robot instance does not have speech methods, please mixin speech methods in your robot class."
        self.robot.say(self.robot.strategy.execute(action), animation)

    def get_reward(self):
        self.joystick_to_reward()

    def rfun(self, action):
        self.out = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        while self.out[6] == 0 and self.out[7] == 0 and self.out[8] == 0 and self.out[9] == 0:
            pygame.event.pump()
            self.out = self.get_joystick_vector()
            self.execute(action)
            self.get_reward()

        return self.reward


class RoboChessExperiment(RobotExperiment):
    def __init__(self, robot):
        super(RoboChessExperiment, self).__init__(robot)


    def rfun(self, action):
        self.out = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        while self.out[6] == 0 and self.out[7] == 0 and self.out[8] == 0 and self.out[9] == 0:
            pygame.event.pump()
            self.out = self.get_joystick_vector()

            # recv something after a move is played.
            self.robot.socket.recv()
            self.robot.socket.send("received.")

            self.execute(action)
            self.get_reward()



        return self.reward
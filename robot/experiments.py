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


class RobotChessExperiment(RobotExperiment):
    def __init__(self, robot):
        super(RobotChessExperiment, self).__init__(robot)


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


class NanogramProcess(RobotExperiment):
    def __init__(self,robot):
        """
        NanogramProcess class specifies the process of interaction between robot and nanogram users.
        Currently the process has several steps. Despite the fact that there are several mechanisms to fellow for
        different functions, we now implement the simplest version.

        Current process is defined as follows

        1. instructe the rules of the nanogram: This sub-process corresponds to function instruct().
        2. interaction with users with four different kinds of supportive types: This sub-process corresponds to
        function interaction()
        3. post-interaction comments


        Additionally, a interrupting program is introduced in function interrupt:
        """
        super(NanogramProcess, self).__init__(robot)
        self.start_time = time.time()
        self.current_time = time.time()
        self.end_time = time.time()

        self.instruct()

        return

    def instruct(self):

        """
        This official description of nonogram is adopted from paper "An efficient algorithm for solving nonnograme"[1]

        [1] http://debut.cis.nctu.edu.tw/Publications/pdfs/J54.pdf
        :return:
        """
        self.robot.say("The positive integers in the top of a column or left of a row stand for the lengths of black "
                       "runs in the column or row respectively. The goal is to paint cells to form a picture that "
                       "satisfies the following three constraints")

        self.robot.say("Firstly, each cell must be colored (black) or left empty (white).")
        self.robot.say("Secondly, If a row or column has k numbers: s1,s2,...,sk , "
                       "then it must contain k black runs - the first (leftmost for rows/topmost for columns)"
                       "black run with length s1, the second black run with length s2, and so on.")
        self.robot.say(" The last rule is, there should be at least one empty cell between two consecutive black runs.")
        return

    def interaction(self, action):
        # recv something after a move is played.
        positionx, positiony = map(float, self.robot.socket.recv().split(','))
        self.robot.say("The action you just did is at position x=%d, y=%d" % (positionx + 1, positiony + 1))
        self.robot.socket.send("received.")
        self.execute(action)
        self.get_reward()

    def run(self, action):
        self.interaction(action)



class RobotNanogramExperiment(RobotExperiment):
    def __init__(self, robot):
        super(RobotNanogramExperiment, self).__init__(robot)
        self.process = NanogramProcess(robot)


    def rfun(self, action):
        self.out = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        while self.out[6] == 0 and self.out[7] == 0 and self.out[8] == 0 and self.out[9] == 0:
            pygame.event.pump()
            self.out = self.get_joystick_vector()
            self.process.run(action)
            self.reward = self.process.reward
        return self.reward


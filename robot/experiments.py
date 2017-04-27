import pygame
import time
import robot_methods
import json
import sys

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
        #self.jstick = pygame.joystick.Joystick(self.robot.joystick_id)
        #self.jstick.init()
        #print 'Initialized Joystick : %s' % self.jstick.get_name()

    def execute(self, action):
        animation = "animations/Stand/Gestures/Explain_1"
        assert issubclass(self.robot.__class__, robot_methods.RobotSpeechMixin), \
            "Robot instance does not have speech methods, please mixin speech methods in your robot class."
        self.robot.say(action, animation)

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

    def check_and_confirm(self, message):
        """
        This methods comfirm information received from nonogram process.
        :param message: message thats needs to be received from nonogram
        :return: true
        """
        received = self.robot.socket.recv()
        if message == received:
            self.robot.socket.send(message + "_confirmed")
        else:
            raise Exception("The process expects to receive message %s, however, message: %s is received." % (message, received))
        return True

    def check_confirm(self, message):
        """
        This methods comfirm information received from nonogram process.
        :param message: message thats needs to be received from nonogram
        :return: true
        """
        received = self.robot.socket.recv()
        if message+"_confirmed" == received:
            pass
        else:
            raise Exception("The process expects to receive message %s, however, message: %s is received." %
                            message + "_confirmed", received)
        return True

class RobotChessExperiment(RobotExperiment):
    def __init__(self, robot):
        super(RobotChessExperiment, self).__init__(robot)


    def rfun(self, action):
        self.out = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        while self.out[6] == 0 and self.out[7] == 0 and self.out[8] == 0 and self.out[9] == 0:
            pygame.event.pump()
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

        self.info = {"user":[], "game":{"size": None,   # size is defined as a tuple
                                        "solution": None,
                                        "config":None,
                                        "positions":[],
                                        "current_board": None,
                                        "previous_board": None,
                                        "behaviours":[],
                                        "evaluations":[],
                                        "times":[self.start_time],
                                        "behaviour_times":[self.start_time],
                                        "clicks":[]}}

        # Set global parameters to track infomation of whether each rule is excuted or not
        self.behaviour_excuted_rule1 = False
        self.behaviour_excuted_rule2 = False

        self.domain_excuted_rule1 = False
        self.domain_excuted_rule2 = False

        # Set global parameters to track
        self.behaviour_selected_rule1 = False
        self.behaviour_selected_rule2 = False

        self.domain_selected_rule1 = False
        self.domain_selected_rule2 = False

        # Set final selected rule

        class ActionType():
            NOTSELECTED = 0
            BRULE1 = 1    # behaviour level rule 1
            BRULE2 = 2
            BRULE3 = 3

            DRULE1 = 51   # domain level rule 1
            DRULE2 = 52
            DRULE3 = 52
        self.action_types = ActionType()
        self.selection = self.action_types.NOTSELECTED

        # Start the instruction process
        self.instruct()


    def instruct(self):

        """
        This official description of nonogram is adopted from paper "An efficient algorithm for solving nonnograme"[1]

        [1] http://debut.cis.nctu.edu.tw/Publications/pdfs/J54.pdf
        :return:
        """
        #self.robot.say("Now ")
        #self.robot.say("The positive integers in the top of a column or left of a row stand for the lengths of black "
        #               "runs in the column or row respectively. The goal is to paint cells to form a picture that "
        #               "satisfies the following three constraints")

        #self.robot.say("Firstly, each cell must be colored (black) or left empty.")
        #self.robot.say("Secondly, If a row or column has k numbers: s1,s2,...,sk , " "then it must contain k black runs - the first."
        #               "black run with length s1, the second black run with length s2, and so on.")
        #self.robot.say(" The last rule is, there should be at least one empty cell between two consecutive black runs.")
        #self.robot.start_dialog(["dialogs/introduction.top"])
        return

    def excute_action(self, behaviour_class, actions):
        """
        This function selects action according to actions set and behaviour class of the supportive behaviour
        :param behaviour_class:
        :param actions:
        :return:
        """
        self.robot.say(actions[behaviour_class])


    def strategy_evaluation(self, behaviour_class):
        """
        This method decides what conditions should be considered in order to ask robot to make an action and also excute
        the actions.

        Three levels of information are used to make actions.

        Behaviour level information:

        behaviour level information is recorded by user_behaviour variable

        Domain level information:

        domain level inforation considers whether user made a good decision or not. It is detected by comparing the
        current board with solution.

        Long analysis informaton:

        This level analysis time and it relevence to user behaviours

        :return:
        """

        # map all the information to differnt variables in order to use them conveniently.
        size = self.info["game"]["size"]
        solution = self.info["game"]["solution"]
        config = self.info["game"]["config"]
        positions = self.info["game"]["positions"]
        current_board = self.info["game"]["current_board"]
        previous_board = self.info["game"]["previous_board"]
        behaviours = self.info["game"]["behaviours"]
        evaluations = self.info["game"]["evaluations"]
        times = self.info["game"]["times"]
        clicks = self.info["game"]["clicks"]
        behaviour_times = self.info["game"]["behaviour_times"]

        actions = None




        # Reinforcement learning on each rule ?

        # Considering the four types of the supportive behaviours here.
        # 1. Information support 2. Tangible assistance 3. Esteem support 4. Emotional support
        # Behaviour level information can only decide whether one needs instrucmental or Informational support.
        # Domain knowledge level can decide whether user needs Appraisal support.
        # Long term analysis can decide whether user needs emotional support.

        # Behaviour level

        # Rule one
        # make a time t to be associated with difficulty of the game and for $t_1$ > $t$
        # currently, we define difficulty to be $n^2 + 1$ $t$ is defined to be $n^2 + 1 \times 0.1s$


        if not self.behaviour_excuted_rule1:
            count = len(positions)

            if count > 1:  # ensure that this does not trigger for the first behaviour
                if behaviour_times[-1] > times[-2]:          # ensure this does not trigger after another behaviour
                    w, h = size
                    t1 = (w * h + 1) * 0.2
                    if times[-1] - times[-2] > t1:
                        actions = ["Do you need to hear some information about this game?",
                                   "If you feel puzzled, I can complete next move for you.",
                                   "But please don't worry, this game is hard this time.",
                                   "But please don't worry, I am here for you."]

                        actions = ["Your last action took too long. " + action for action in actions]
                    self.selected_rule1 = True
                    self.action_type = self.action_types.BRULE1


        # Rule two: several selections are cancelled continuously.
        # Propose, should this model for possion distribution ? time 2 - time 1 expect on average 2 cancellation ?
        # if user gives a negative interference, then the expected value is increased.

        # If there are at least three positive discoveries in three actions, then an action is excuted.
        if not self.behaviour_excuted_rule2:
            import operator
            from copy import deepcopy

            def shift_left(lst, n):
                if n < 0:
                    raise ValueError('n must be a positive integer')
                if n > 0:
                    lst.insert(0, lst.pop(-1))  # shift one place
                    shift_left(lst, n - 1)  # repeat

            rule_two_n = 4
            limit = 1.0
            print clicks
            if len(positions) >= rule_two_n: # in case we have at least n points

                t1 = times[-rule_two_n:]
                t2 = deepcopy(times[-rule_two_n:])
                shift_left(t2, rule_two_n-1)



                if all([c < limit for c in map(operator.sub, t2, t1)[0:rule_two_n]]) :
                    actions = ["Do you need more information about this game?",
                               "Do feel difficulties completing this task, I can help you by filling this row.",
                               "It is actually a good idea, trying out might be important for thinking. isn't it?",
                               "If you have problems, I can help you with this one."]
                    actions = ["That was fast! were you just trying out different moves? " + action for action in actions]
            self.selected_rule2 = True
            self.action_type = self.action_types.BRULE2

        # If the possibility of poisson distribution does triger the proposal, the behaviours of this condition is
        # modeled using a multi-armed bandit algorithm ?
        #
        # a. recheck on rules, for example, you know rules already ? if the answer is ok, the probability is set to zero
        # b. comment on trying out, for example, you still trying how to interact with robot ? if yes the expected value
        # is set to be current value.


        # Rule two: several exclusions are cancelled continuously
        # This rule is implemented similar to rule one


        # Domain kownledge level

        # Rule one: user made a good moves after long time and it is a good one
        # Propose an action.
        # a. appraisal, for example, that was a right decision
        # b.
        print clicks
        if len(positions) >= rule_two_n:  # in case we have at least n points

            t1 = times[-rule_two_n:]
            t2 = deepcopy(times[-rule_two_n:])
            shift_left(t2, rule_two_n - 1)
        if all([c < limit for c in map(operator.sub, t2, t1)[0:rule_two_n]]):
            actions = ["Do you want to know it is correct or not?",
                       "As a reward, I can show you one corrent cell on the board.",
                       "and That really a good sign.",
                       "Isn't?"]
            actions = ["That took you some effort. " + action for action in actions]


        # Rule two 1): user made made continuous good moves then stop
        # Propse an action.
        # a. conditions to check in this case
        # 1. cotinueous selection
        # 2. action two in behaviou level is activated
        # 3. the last action makes a row or column to be correct.
        if not self.domain_excuted_rule2:
            def compare(position, size, board, solution):
                """
                Given a position, this function compares the whether the row and the column of this position are the same as
                solution's
                :param solution:
                :return:
                """
                w, h = size
                x, y = position

                check_row = True
                for i in xrange(h):
                    check_row = (board[x][i] == solution[x][i] and check_row)

                check_cloumn = True
                for j in xrange(w):
                    check_cloumn = (board[j][y] == solution[j][y] and check_cloumn)

                return check_cloumn, check_row

            position = positions[-1]
            column_complete, row_complete = compare(position, size,current_board, solution)
            print column_complete, row_complete
            if column_complete:

                actions = ["Do you want to know it is correct or not?",
                           "I can show you one correct answer on the board."
                           "That is great !",
                           "I can see that you are doing well."]
                actions = ["It seems you completed a column. " + action for action in actions]

            if row_complete:

                actions = ["Do you want to know it is correct or not?",
                           "I can show you one correct answer on the board.",
                           "That is great ! ",
                           "I can see that you are doing well."]
                actions = ["You completed a row. " + action for action in actions]

            if column_complete and row_complete:

                actions = ["Do you want to know it is correct or not?",
                           "I can show you one correct answer on the board.",
                           "That is so good",
                           "I can see that you are doing well."]
                actions = ["It seems you completed a row and column. " + action for action in actions]

            self.behaviour_selected_rule2 = True
            self.action_type = self.action_types.DRULE2






        if actions is not None:
            self.excute_action(behaviour_class, actions)





        return False

    def interaction(self, behaviour_class):
        # one time interaction
        received = self.robot.socket.recv()
        try:
            # receive current board information
            solution, current_board, previous_board = json.loads(received)
            self.robot.socket.send("board_information_received")
            self.info["game"]["current_board"] = current_board
            self.info["game"]["solution"] = solution
            self.info["game"]["previous_board"] = previous_board

            # receive current positions
            received = self.robot.socket.recv_json()
            positionx, positiony, click = received
            if isinstance(positionx,float):
                positionx = int(positionx)
            if isinstance(positiony,float):
                positiony = int(positiony)
            self.robot.socket.send("positions_received")

            # receive interaction information
            self.info["game"]["positions"].append([positionx, positiony])
            self.info["game"]["clicks"].append(click)
            self.info["game"]["times"].append(time.time())

            self.solution = self.info["game"]["solution"]
            self.board = self.info["game"]["current_board"]
            self.previous_board = self.info["game"]["previous_board"]

            FILLED = 1 # board is filled with black
            CROSS = 2 # board is filled with cross


            # user behaviour codes three user actions
            # 1: user made a selection
            # 2: user made an exclusion
            # 3: user made cancelled a selection
            # 4: user cancelled an exclusion
            user_behaviour = 0

            # evaluation result codes two states
            # 1: user's last action matches with the solution
            # 2: user's last action does not match the solution


            evaluation_result = 0

            if self.board[positiony][positionx] == FILLED or self.board[positiony][
                positionx] == CROSS:  # after selection, if the position is filled in with block or cross

                if click == 0:
                    user_behaviour = 1
                    if self.solution[positiony][positionx] == self.board[positiony][positionx]:
                        #self.robot.say("User made a good selection.")
                        evaluation_result = 1
                    else:
                        #self.robot.say( "User made a bad selection.")
                        evaluation_result = 2

                if click == 1:
                    user_behaviour = 2
                    print "User thinks this position can be excluded."
                    if self.solution[positiony][positionx] + 2 == self.board[positiony][positionx]:  # cross matches empty in solution
                        #self.robot.say( "User made a good exclusion.")
                        evaluation_result = 1
                    else:
                        #self.robot.say("User made a bad exclusion.")
                        evaluation_result = 2

            else:
                print "User thinks the position is a mistake."
                if click == 0:
                    print "User used left click to cancel."
                    if self.previous_board[positiony][positionx] == FILLED:
                        #self.robot.say( "User thinks this was a selection mistake")
                        user_behaviour = 3

                        if self.solution[positiony][positionx] == self.board[positiony][positionx]:
                            #self.robot.say("And he is right.")
                            evaluation_result = 1
                        else:
                            #self.robot.say( "But he is wrong.")
                            evaluation_result = 2

                    if self.previous_board[positiony][positionx] == CROSS:
                        #self.robot.say( "User thinks this was an exclusion mistake")
                        user_behaviour = 4

                        if self.solution[positiony][positionx] + 2 == self.board[positiony][
                            positionx]:  # cross matches empty in solution
                            #self.robot.say("But he is wrong.")
                            evaluation_result = 1
                        else:
                            #self.robot.say("And he is right.")
                            evaluation_result = 2


                if click == 1:
                    print "User used right click to cancel."
                    if self.previous_board[positiony][positionx] == FILLED:
                        #self.robot.say("User thinks this was a selection mistake")

                        if self.solution[positiony][positionx] == self.board[positiony][positionx]:
                            #self.robot.say("But he is wrong.")
                            evaluation_result = 1
                        else:
                            #self.robot.say("And he is right.")
                            evaluation_result = 2

                    if self.previous_board[positiony][positionx] == CROSS:
                        #self.robot.say("User thinks this was a exclusion mistake")
                        if self.solution[positiony][positionx] + 2 == self.board[positiony][
                            positionx]:  # cross matches empty in solution
                            #self.robot.say("But he is wrong.")
                            evaluation_result = 1
                        else:
                            #self.robot.say("And he is right.")
                            evaluation_result = 2

            self.info["game"]["behaviours"].append(user_behaviour)
            self.info["game"]["evaluations"].append(evaluation_result)

            self.strategy_evaluation(behaviour_class)



            return False




        except Exception:
            print sys.exc_info()

            # received game finished confirmation
            if received.startswith("game_finished"):
                self.robot.socket.send("game_finished_confirmed")




            #self.robot.say("The action you just did is at position x=%d, y=%d" % (positionx, positiony))


            return True
        #self.get_reward()

    def run(self, action):
        return self.interaction(action)




class RobotNanogramExperiment(RobotExperiment):
    def __init__(self, robot):
        super(RobotNanogramExperiment, self).__init__(robot)
        self.robot.adjust_speech_parameters(pitch=100, speed=90)
        self.process = NanogramProcess(robot)


    def rfun(self, action):
        self.out = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.robot.load_topic("dialogs/interaction.top")
        self.robot.dialog.subscribe('ExperimentModule')


        # receive size information
        received = self.robot.socket.recv()
        self.process.info["game"]["size"]= map(lambda x: int(x), received.split(','))
        self.robot.socket.send("size" + "_received")

        # receive game configurations
        received = self.robot.socket.recv_json()
        self.process.info["game"]["config"]= received
        self.robot.socket.send("config" + "_received")


        while self.out[6] == 0 and self.out[7] == 0 and self.out[8] == 0 and self.out[9] == 0:
            pygame.event.pump()
            #self.out = self.get_joystick_vector()
            game_finished = self.process.run(action)
            if game_finished:
                self.robot.say("The game is finished.")
                print self.process.info["game"]["positions"]
                print self.process.info["game"]["clicks"]
                print self.process.info["game"]["times"]
                print self.process.info["game"]["behaviours"]
                print self.process.info["game"]["evaluations"]

            #self.reward = self.process.reward


        return self.reward


import pygame
import time
import robot_methods
import json
import sys
import random
import copy
from datetime import datetime

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
        self.reward = 0.0
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
        self.start_readable_time = str(datetime.now())
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
                                        "readable_times":[self.start_readable_time],
                                        "behaviour_times":[self.start_time],
                                        "clicks":[]}}

        # Set global parameters to track infomation of whether each rule is excuted or not
        self.forbid_rule1 = False # waited long time fail
        self.forbid_rule2 = False # waited long time suceed
        self.forbid_rule3 = False # complete a row or cloumn
        self.forbid_rule4 = False # (any sign that user did not use any technique

        self.action_lock = False # if action lock is set to 1, no furthur action selection will be done
        self.game_finished = False

        self.rule1_selected = False
        self.rule2_selected = False
        self.rule3_selected = False
        self.rule4_selected = False

        self.rule1_answered = self.robot.memory.subscriber("Rule1Answered")
        self.rule2_answered = self.robot.memory.subscriber("Rule2Answered")
        self.rule3_answered = self.robot.memory.subscriber("Rule3Answered")
        
        self.rule1_answered.signal.connect(self._on_rule1_answered)
        self.rule2_answered.signal.connect(self._on_rule2_answered)
        self.rule3_answered.signal.connect(self._on_rule3_answered)

        self.rule1_replied = False
        self.rule2_replied = False 
        self.rule3_replied = False

        # Rule two evaluation
        self.rule2_skip = 0

        
        # Set final selected rule
        class ActionType():
            NOTSELECTED = 0
            RULE1 = 1    # behaviour level rule 1
            RULE2 = 2
            RULE3 = 3

        self.action_types = ActionType()
        self.final_selected = self.action_types.NOTSELECTED

    def set_mode(self, value):
        self.robot.memory.insertData("Mode", value)



    def instruct_begin(self):

        """
        This official description of nonogram is adopted from paper "An efficient algorithm for solving nonnograme"[1]

        [1] http://debut.cis.nctu.edu.tw/Publications/pdfs/J54.pdf
        :return:
        """
        self.robot.memory.raiseEvent("InstructBegin", 1)

        return

    def instruct_game(self):
        self.robot.memory.raiseEvent("InstructBegin", 1)

    def _rule2_supportive_action(self, n):
        x = random.sample([1,2],1)[0]
        if x == 1:
            return self._show_number_cells(n)
        elif x == 2:
            return self._say_completed()
        
        return 
    def _test_correct_answer(self):
        current_position = self.info["game"]["positions"][-1]
        current_board = self.info["game"]["current_board"]
        solution = self.info["game"]["solution"]

        i, j = position
        if current_board[i][j] == solution[i][j]:
            return "Previous answer is correct."
        else:
            return "Previous answer is not correct."
        
    def _say_completed(self):
        population = {}
        if self.row_complete:
            population[0] = "a row" # code row_complete as 0
        if self.column_complete:
            population[1] = "a column" # code column_complete as 1
        if self.column_complete and self.row_complete:
            population[2] = "both row and column" # code column_complete as 1
        sample = random.sample(population.keys(),1)

        interjections = ["Cool,", "Nice,", "Great,", "Good,"]
        interjection = random.sample(interjections, 1)[0]

        statements = [interjection + "you completed %s."%population[sample[0]], interjection + "%s completed,"%population[sample[0]], ""]
        statement = random.sample(statements, 1)[0]

        return statement
    
    def _show_number_cells(self, n):
        current_board = self.info["game"]["current_board"]
        solution= self.info["game"]["solution"]
        
        size = self.info["game"]["size"]
        w, h = size
        count = 0 
        for i in xrange(w):
            for j in xrange(h):
                if solution[i][j] == 1 and not current_board[i][j] == 1:
                    count += 1
        return {1: " Em, as far as I know, you still need to fill in %d cells."%count,
                2: " According to what you have on the board, in total, you still have %d cells to fill."%count,
                3: " Well, I think, there are still %d cells to fill."%count}[n]
    
    def _show_correct_answer(self, n):

        """
        Give the current board and solution, returns an action that is correct.
        :param:
        :return:
        """
        current_board = self.info["game"]["current_board"]
        solution = self.info["game"]["solution"]
        size = self.info["game"]["size"]
        
        w, h = size
        positions = [(i,j) for i in xrange(h) for j in xrange(w)]
        population = []
        for c in positions:
            i, j = c
            if current_board[i][j] != solution[i][j] and solution[i][j] == 1:
                population.append([i,j])
        sample = random.sample(population, 1)
        row, column = sample[0]
        smap = {1:"first", 2:"second", 3: "third", 4: "fourth", 5:"fifth", 6:"sixth", 7:"seventh"}
        instruct = {1: " I found a good move. You may want to fill %s row and %s column."%(smap[row+1], smap[column+1]),
                    2: " You may want to fill in %s row and %s column. It is a correct answer."%(smap[row+1], smap[column+1]),
                    3: " I think I can help you to spot a correct answer, you may want to fill in %s row and %s column."%(smap[row+1], smap[column+1])}[n]
        return instruct

    def _on_rule1_answered(self, value):
        def ignored():
            self.reward = -2.0
            
        def answered():
            self.reward = 2.0

        def switch(value):
            value = int(value)
            return {
                0:ignored,
                1:answered,
                2:answered,
                3:answered,
                4:answered}[value]()

        self.rule1_replied = True
        switch(value)

    def _on_rule2_answered(self, value):
        def ignored():
            self.reward = -2.0

        def answered():
            self.reward = 2.0

        def switch(value):
            value = int(value)
            return {0:ignored,
                    1:answered,
                    2:answered,
                    3:answered,
                    4:answered}[value]()

        switch(value)
        self.rule2_replied = True

    def _on_rule3_answered(self, value):
        self.rule3_replied = True
        pass
        

    def excute_action(self, behaviour_class, actions):
        """
        This function selects action according to actions set and behaviour class of the supportive behaviour
        :param behaviour_class:
        :param actions:
        :return:
        """
        # connect subcribers and their callback functions.
        self.robot.say(actions[behaviour_class])
        # this is used for debugging purpose
        print actions[behaviour_class]
        
        behaviour_class = int(behaviour_class)

        print "----> Sending signal"
        # send signals to robot.
        if self.action_type == self.action_types.RULE1:
            self.robot.memory.raiseEvent("Rule1Activated", behaviour_class)
        if self.action_type == self.action_types.RULE2:
            self.robot.memory.raiseEvent("Rule2Activated", behaviour_class)
        if self.action_type == self.action_types.RULE3:
            self.robot.memory.raiseEvent("Rule3Activated", behaviour_class)

        # continue if one of the rules is answered
        while (not self.rule1_replied) and (not self.rule2_replied) and (not self.rule3_replied):
            time.sleep(1)
            print self.reward
        self.rule1_replied = False
        self.rule2_replied = False
        self.rule3_replied = False
        return True

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
        #TODO
        # in order to debug, set the behaviour class to be 2
        # behaviour class ranges from 0 to 3
        #sbehaviour_class = 1

        # map all the information to differnt variables in order to use them conveniently.
        size = self.info["game"]["size"]
        solution = self.info["game"]["solution"]
        config = self.info["game"]["config"]
        positions = self.info["game"]["positions"]
        current_board = self.info["game"]["current_board"]
        previous_board = self.info["game"]["previous_board"]
        behaviours = self.info["game"]["behaviours"]

        # Evaluation detects whether last action was correct or not.
        evaluations = self.info["game"]["evaluations"]
        class Eval:
            def __init__(self):
                self.correct = 1
                self.incorrect = 2                                
        def last_evaluation():
            return evaluations[-1]
        
        times = self.info["game"]["times"]
        clicks = self.info["game"]["clicks"]
        behaviour_times = self.info["game"]["behaviour_times"]

        actions = None # variable for final actions
        action_excuted = False
        # reset action lock
        self.action_lock = False

        # Reinforcement learning on each rule ?

        # Considering the four types of the supportive behaviours here.
        # 1. Information support 2. Tangible assistance 3. Esteem support 4. Emotional support
        # Behaviour level information can only decide whether one needs instrucmental or Informational support.
        # Domain knowledge level can decide whether user needs Appraisal support.
        # Long term analysis can decide whether user needs emotional support.

        # Pre rules evaluation 
        def set_time(size=[0,0]):
            """ set a time reference to compare with"""
            n_rows, n_columns = size 
            t1 = (n_rows * n_columns + 1) * 0.3
            return t1
        count = len(positions)
        t1 = set_time(size)
        if (not self.forbid_rule1) and (not self.forbid_rule2): 
            # count > 1:  # ensure that this does not trigger for the first behaviour
            # behaviour_times[-1] > times[-2]:          # ensure this does not trigger after another behaviour
            # times[-1] - times[-2] > t1  # condition for rule1
            self.waited_long = ((count > 1) and (times[-1] - times[-2] > t1))

        eval = Eval()


        def compare(position, size, board, solution):
            """
            Given a position, this function compares the whether the row and the column of this position are the same as
            solution's
            :param solution:
            :return:
            """
            w, h = size
            positiony, positionx = position
  
            check_row = True
            for i in xrange(h):
                check_row = (((board[positiony][i] == 0 or board[positiony][i] == 2) and solution[positiony][i] == 0)
                             or (board[positiony][i] == 1 and solution[positiony][i] == 1)) and check_row
  
            check_cloumn = True
            print "check_row", check_row
            for j in xrange(w):
                check_cloumn = (((board[j][positionx] == 0 or board[j][positionx] == 2) and solution[j][positionx] == 0)
                             or (board[j][positionx] == 1 and solution[j][positionx] == 1)) and check_cloumn
            print "check_column", check_row
            
            return check_cloumn, check_row
  
        # Rule one ( waited long time with an incorrect answer)
        print "waited long", self.waited_long, times[-1] - times[-2], t1, count, "evaluation",last_evaluation(), eval.incorrect
        if self.waited_long and last_evaluation() == eval.incorrect and not self.action_lock:
                all_actions = [[self._rule2_supportive_action(1),   # balanced 
                                self._show_correct_answer(1), # balanced
                                " This step is hard, please do not worry.",
                                " I am here for you."],
                               [self._rule2_supportive_action(2),
                                self._show_correct_answer(2),
                                " This game is more difficult than averange, take your time.",
                                " Remember that I will help if I see there is some problem."],
                               [self._rule2_supportive_action(3),
                                self._show_correct_answer(3),
                                " I think I accidentally chose a difficult game for you. Take your time.",
                                " I will do my best to support you." ]
                ]
            
                beginnings = ["Is there any thing that troubles you?", "That was a difficult move,", "Last action took you some time"]
                beginning = random.sample(beginnings,1)[0]
                
                actions = random.sample(all_actions,1)[0]
                actions = [beginning + action for action in actions]
                self.rule1_selected = True
                self.action_lock = True
                self.action_type = self.action_types.RULE1

        #Rule two ( when user completed a row or a cloumn)
        if not self.forbid_rule2 and not self.action_lock and not self.info["game"]["clicks"][-1] == 1:  # last click is not right click
            position = positions[-1]
            column_complete, row_complete = compare(position, size, current_board, solution)
            self.column_complete = column_complete
            self.row_complete = row_complete

            if (column_complete or row_complete) and self.rule2_skip == 0:
                                        
                all_actions = [[self._rule2_supportive_action(1),   # balanced 
                                self._show_correct_answer(1), # balanced
                                " That was a skillful move.",
                                " It was nicely done."],
                               [self._rule2_supportive_action(2),
                                self._show_correct_answer(2),
                                " I really think you have the knowledge to complete the game.",
                                " I am really happy for you."],
                               [self._rule2_supportive_action(3),
                                self._show_correct_answer(3),
                                " I think you have mastered some skills that I do not know.",
                                " You have been doing really well."]
                ]

                #if user completed an action check whether user completed row, column or both

                actions = random.sample(all_actions, 1)[0]
                actions = [action for action in actions] 
                self.rule2_selected = True
                self.action_type = self.action_types.RULE2

                # skip next 3 actions.
                self.rule2_skip += 3
            elif (column_complete or row_complete) and self.rule2_skip > 0 :
                self.rule2_skip -= 1

        #Rule three (not implemented. it is something related to techniques)
        print actions
        if actions is not None:
            action_excuted = self.excute_action(behaviour_class, actions)
        else:
            action_excuted = False
            
        return action_excuted



    def idel_interaction(self):
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
            positiony, positionx, click = received
            if isinstance(positionx,float):
                positionx = int(positionx)
            if isinstance(positiony,float):
                positiony = int(positiony)
            self.robot.socket.send("positions_received")

            # receive interaction information
            self.info["game"]["positions"].append([positiony, positionx])
            self.info["game"]["clicks"].append(click)
            self.info["game"]["times"].append(time.time())
            self.info["game"]["readable_times"].append(str(datetime.now()))

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

                            # we do not consider removing exclusion is mistake
                            evaluation_result = 2
                        else:
                            #self.robot.say("And he is right.")
                            evaluation_result = 2
            
            self.info["game"]["behaviours"].append(user_behaviour)
            self.info["game"]["evaluations"].append(evaluation_result)

            return self.game_finished, True
        except Exception:
            print sys.exc_info()
            print "received",received

            if type(received) != list and received.startswith("game_finished"):
                self.robot.socket.send("game_finished_confirmed")
                self.game_finished = True
            return self.game_finished, True
        
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
            positiony, positionx, click = received
            if isinstance(positionx,float):
                positionx = int(positionx)
            if isinstance(positiony,float):
                positiony = int(positiony)
            self.robot.socket.send("positions_received")

            # receive interaction information
            self.info["game"]["positions"].append([positiony, positionx])
            self.info["game"]["clicks"].append(click)
            self.info["game"]["times"].append(time.time())
            self.info["game"]["readable_times"].append(str(datetime.now()))
            
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

                            # we do not consider removing exclusion is mistake
                            evaluation_result = 2
                        else:
                            #self.robot.say("And he is right.")
                            evaluation_result = 2
            self.info["game"]["behaviours"].append(user_behaviour)
            self.info["game"]["evaluations"].append(evaluation_result)
            
            return self.game_finished, self.strategy_evaluation(behaviour_class)
            
        except Exception:
            print sys.exc_info()
            print "received",received
            # received game finished confirmation
            if type(received) != list and received.startswith("game_finished"):
                self.robot.socket.send("game_finished_confirmed")
                self.game_finished = True
                
            #self.robot.say("The action you just did is at position x=%d, y=%d" % (positionx, positiony))
            return self.game_finished, True
        #self.get_reward()

    def run(self, action, mode):
        self.mode = mode
        if self.mode == 2:
            return self.interaction(action)
        else:
            return self.idel_interaction()




class RobotNanogramExperiment(RobotExperiment):
    def __init__(self, robot):
        super(RobotNanogramExperiment, self).__init__(robot)
        self.robot.adjust_speech_parameters(pitch=100, speed=90)
        self.process = NanogramProcess(robot)
        self.game_start = True
        self.game_start_time = 0.0
        self.game_end_time = 0.0
        self.process.info["game"]["game_times"] = []
        self.previous_clicks = 0
        self.game_finished_times = 0

    def rfun(self, action, mode, id):
        self.mode = mode
        self.process.reward = 0.0
        self.id = id
        #self.robot.load_topic("dialogs/interaction.top")
        #self.robot.dialog.subscribe('ExperimentModule')
        if len(self.process.info["game"]["clicks"]) - self.previous_clicks == 1:
            self.game_start_time = time.time()

        


        if self.game_start  == True:
            # receive size information
            received = self.robot.socket.recv()
            self.process.info["game"]["size"]= map(lambda x: int(x), received.split(','))
            self.robot.socket.send("size" + "_received")

            # receive game configurations
            received = self.robot.socket.recv_json()
            self.process.info["game"]["config"]= received
            self.robot.socket.send("config" + "_received")
            self.game_start = False

        if self.mode == 1 or self.mode == 3:
            learning = False
        elif self.mode == 2:
            learning = True
            
        ends = [" Congratulations!", " That was an awesome run.", " Great, I see that you enjoyed it.", " Good work.", " Nicely done."]
        while not learning:
            pygame.event.pump()
            game_finished, action_completed = self.process.run(action, self.mode)
            if game_finished:
                self.game_start = True
                self.process.game_finished = False

                end = random.sample(ends,1)[0]
                if self.game_finished_times <= 1:
                    self.robot.say("The game is finished." + end + " Please continue with game %d."%((self.mode-1) * 3 + self.game_finished_times + 2))

                self.game_finished_times += 1
                
                print self.process.info["game"]["positions"]
                print self.process.info["game"]["clicks"]
                print self.process.info["game"]["times"]
                print self.process.info["game"]["behaviours"]
                print self.process.info["game"]["evaluations"]

                self.game_end_time = time.time()
                self.process.info["game"]["game_times"].append(self.game_end_time - self.game_start_time)
                self.game_start_time = 0.0
                self.previous_clicks = len(self.process.info["game"]["clicks"])
                print "game time", self.process.info["game"]["game_times"]
                with open("data/ID:%d_Mode:%d.json"%(self.id, self.mode),'w') as outfile:
                          json.dump(self.process.info["game"], outfile)
                
            print action_completed
            if action_completed == True:
                 break

        while learning:
            pygame.event.pump()
            # if action is completed, the loop will be broken
            game_finished, action_completed = self.process.run(action, self.mode)
            if game_finished:
                self.game_start = True
                self.process.game_finished = False
                end = random.sample(ends,1)[0]
                
                if self.game_finished_times <= 1:
                    self.robot.say("The game is finished." + end + " Please continue with game %d."%((self.mode-1) * 3 + self.game_finished_times + 2))

                
                print self.process.info["game"]["positions"]
                print self.process.info["game"]["clicks"]
                print self.process.info["game"]["times"]
                print self.process.info["game"]["behaviours"]
                print self.process.info["game"]["evaluations"]

                self.game_finished_times += 1
                
                self.game_end_time = time.time()
                self.process.info["game"]["game_times"].append(self.game_end_time - self.game_start_time)
                self.game_start_time = 0.0
                self.previous_clicks = len(self.process.info["game"]["clicks"])
                print "game time", self.process.info["game"]["game_times"]

                with open("data/ID:%d_Mode:%d.json"%(self.id, self.mode),'w') as outfile:
                    json.dump(self.process.info["game"], outfile)
            if action_completed == True:
                break
            
        if self.game_finished_times == 3:

            self.robot.say("%s."%{1:"You completed the first session. Alex, come in please",
                                  2:"Nice work you did here. Later you will have another session.",
                                  3:"Now, you have done the last session. Thanks a lot! Alex, please come in."}[self.mode])
            self.game_finished_times = 0
             
        return self.process.reward


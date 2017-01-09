from naoqi import ALProxy

import motion

import threading
import time
import almath

from strategy import Strategy
from alg import Exp3
from experiment import RoboChessExperiment
from robot_methods import RobotSpeechMixin

import zmq


class Robot(threading.Thread, RobotSpeechMixin):

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

        self.speech = ALProxy("ALAnimatedSpeech", self.ip, self.port)
        self.posture = ALProxy("ALRobotPosture", self.ip, self.port)
        self.motion = ALProxy("ALMotion", self.ip, self.port)

        self.strategy = Strategy()
        self.experiment = RoboChessExperiment(robot=self)
        self.algorithm = Exp3(4, 0.1, self.experiment, debug=1)

        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % "5556")

    def run(self):
        niter = 50
        self.algorithm.run(niter)


class Chess(threading.Thread):
    def __init__(self):
        super(Chess, self).__init__()


    def run(self):
        from ChessBoard import ChessBoard
        from ChessAI import ChessAI_random, ChessAI_defense, ChessAI_offense
        from ChessPlayer import ChessPlayer
        from ChessGUI_text import ChessGUI_text
        from ChessGUI_pygame import ChessGUI_pygame
        from ChessRules import ChessRules
        from ChessGameParams import TkinterGameSetupParams

        from optparse import OptionParser
        import time

        import sys
        sys.path.append("/home/alex/Desktop/RedCoast/chess")

        class PythonChessMain:
            def __init__(self, options):
                if options.debug:
                    self.Board = ChessBoard(2)
                    self.debugMode = True
                else:
                    self.Board = ChessBoard(
                        0)  # 0 for normal board setup; see ChessBoard class for other options (for testing purposes)
                    self.debugMode = False

                self.Rules = ChessRules()

                context = zmq.Context()
                self.socket = context.socket(zmq.REQ)
                self.socket.connect("tcp://localhost:%s" % "5556")

            def SetUp(self, options):
                # gameSetupParams: Player 1 and 2 Name, Color, Human/AI level
                if self.debugMode:
                    player1Name = 'Kasparov'
                    player1Type = 'human'
                    player1Color = 'white'
                    player2Name = 'Light Blue'
                    player2Type = 'randomAI'
                    player2Color = 'black'
                else:
                    GameParams = TkinterGameSetupParams()
                    (player1Name, player1Color, player1Type, player2Name, player2Color,
                     player2Type) = GameParams.GetGameSetupParams()

                self.player = [0, 0]
                if player1Type == 'human':
                    self.player[0] = ChessPlayer(player1Name, player1Color)
                elif player1Type == 'randomAI':
                    self.player[0] = ChessAI_random(player1Name, player1Color)
                elif player1Type == 'defenseAI':
                    self.player[0] = ChessAI_defense(player1Name, player1Color)
                elif player1Type == 'offenseAI':
                    self.player[0] = ChessAI_offense(player1Name, player1Color)

                if player2Type == 'human':
                    self.player[1] = ChessPlayer(player2Name, player2Color)
                elif player2Type == 'randomAI':
                    self.player[1] = ChessAI_random(player2Name, player2Color)
                elif player2Type == 'defenseAI':
                    self.player[1] = ChessAI_defense(player2Name, player2Color)
                elif player2Type == 'offenseAI':
                    self.player[1] = ChessAI_offense(player2Name, player2Color)

                if 'AI' in self.player[0].GetType() and 'AI' in self.player[1].GetType():
                    self.AIvsAI = True
                else:
                    self.AIvsAI = False

                if options.pauseSeconds > 0:
                    self.AIpause = True
                    self.AIpauseSeconds = int(options.pauseSeconds)
                else:
                    self.AIpause = False

                # create the gui object - didn't do earlier because pygame conflicts with any gui manager (Tkinter, WxPython...)
                if options.text:
                    self.guitype = 'text'
                    self.Gui = ChessGUI_text()
                else:
                    self.guitype = 'pygame'
                    if options.old:
                        self.Gui = ChessGUI_pygame(0)
                    else:
                        self.Gui = ChessGUI_pygame(1)

            def MainLoop(self):
                currentPlayerIndex = 0
                turnCount = 0
                while not self.Rules.IsCheckmate(self.Board.GetState(), self.player[currentPlayerIndex].color):
                    board = self.Board.GetState()
                    currentColor = self.player[currentPlayerIndex].GetColor()
                    # hardcoded so that player 1 is always white
                    if currentColor == 'white':
                        turnCount = turnCount + 1
                    self.Gui.PrintMessage("")
                    baseMsg = "TURN %s - %s (%s)" % (
                        str(turnCount), self.player[currentPlayerIndex].GetName(), currentColor)
                    self.Gui.PrintMessage("-----%s-----" % baseMsg)
                    self.Gui.Draw(board)

                    if self.Rules.IsInCheck(board, currentColor):
                        self.Gui.PrintMessage(
                            "Warning..." + self.player[currentPlayerIndex].GetName() + " (" + self.player[
                                currentPlayerIndex].GetColor() + ") is in check!")

                    if self.player[currentPlayerIndex].GetType() == 'AI':
                        moveTuple = self.player[currentPlayerIndex].GetMove(self.Board.GetState(), currentColor)
                    else:
                        moveTuple = self.Gui.GetPlayerInput(board, currentColor)
                    moveReport = self.Board.MovePiece(
                        moveTuple)  # moveReport = string like "White Bishop moves from A1 to C3" (+) "and captures ___!"

                    self.Gui.PrintMessage(moveReport)
                    currentPlayerIndex = (
                                             currentPlayerIndex + 1) % 2  # this will cause the currentPlayerIndex to toggle between 1 and 0

                    #################################################################
                    if self.player[currentPlayerIndex].GetType() == 'AI' :
                        pass
                    elif turnCount%2 == 0:
                        self.socket.send("moved")
                        self.socket.recv()
                    ###################################################################



                    if self.AIvsAI and self.AIpause:
                        time.sleep(self.AIpauseSeconds)

                self.Gui.PrintMessage("CHECKMATE!")
                winnerIndex = (currentPlayerIndex + 1) % 2
                self.Gui.PrintMessage(
                    self.player[winnerIndex].GetName() + " (" + self.player[winnerIndex].GetColor() + ") won the game!")
                self.Gui.EndGame(board)

        parser = OptionParser()
        parser.add_option("-d", dest="debug",
                          action="store_true", default=False,
                          help="Enable debug mode (different starting board configuration)")
        parser.add_option("-t", dest="text",
                          action="store_true", default=False, help="Use text-based GUI")
        parser.add_option("-o", dest="old",
                          action="store_true", default=False, help="Use old graphics in pygame GUI")
        parser.add_option("-p", dest="pauseSeconds", metavar="SECONDS",
                          action="store", default=0,
                          help="Sets time to pause between moves in AI vs. AI games (default = 0)")

        (options, args) = parser.parse_args()

        game = PythonChessMain(options)
        game.SetUp(options)
        game.MainLoop()

if __name__ == "__main__":

    IP = "130.238.150.222"
    robot = Robot(IP, 9559, 0)
    robot.start()

    chess = Chess()
    chess.start()
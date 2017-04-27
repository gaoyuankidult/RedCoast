import numpy as np
import random

class Strategy(object):
    """
    This class is the batsic strategy class.
    """
    def __init__(self):
        self.number = 4
        self.name = {0: "information support",
                     1: "tangible assistance",
                     2: "esteem support",
                     3: "emotional support"}
        self.actions = {value: {} for value in self.name.values()}
        self.actions[self.name[0]] = [
            "Need help ? Press my left bumber so I can suggest you a move.",
            "That wasn't your best move.",
            "Maybe you fill the cell at position %d, %d",
            "You made two mistakes, maybe I can tell you a good strategy?",
            "There are three levels "
        ]
        self.actions[self.name[1]] = [
            "Ahha, I just play a bad move.",
            "I always say luck in love, unlucky in nonogram",
            "That was a mistake",
            "",
            "",
        ]
        self.actions[self.name[2]] = [
            "That was professionally done",
            "Don't worry you didn't have better options ...",

        ]
        self.actions[self.name[3]] = [
            "Greatings, nice to play with you.",
            "I really enjoy playijng with you!",
            "Come on, I still believe in you."
        ]

    def execute(self, cls):
        return self.actions[self.name[cls]][random.randint(0, 1)]

class Experiment(object):
    """Implementation of Experiment class.

    """

    def __init__(self):
        pass

    @staticmethod
    def rfun(action):
        pass


class StaticExp(Experiment):
    """ implementation of a Simple Experiment with static reward function.

    """

    def __init__(self):
        super(StaticExp, self).__init__()

    @staticmethod
    def rfun(action):
        if action == 1:
            return 3
        elif action == 2:
            return 2
        else:
            return 0

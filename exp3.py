import numpy as np
import matplotlib.pyplot as plt


class Exp3(object):
    """Implementation of EXP3 algorithms.
    # Arguments
    K: int >0. Number of actions
    gamma: float >=0 <=1. Tempering parameter
    exp: Instance of Experiment class
    debug: int = 0 or 1. Whether it is a debug run or not. 1 indicates it is a debug run.

    """

    def __init__(self, K, gamma, exp, debug=0):
        assert (K > 0 and type(K) is int), "K's value is %s but K should be int and larger than 0."
        self.K = K
        assert (0.0 <= gamma <= 1.0), " Gamma should be smaller than 1.0 and larger than 0.0."
        self.gamma = gamma
        self.W = np.ones([K])
        self.exp = exp
        self.debug = debug
        self.p = np.ones([K])
        if self.debug:
            self.log = self.p

    def update(self):
        self.p = (1 - self.gamma) * self.W / self.W.sum() + self.gamma / self.K
        action = np.random.choice(xrange(self.K),p=self.p)
        reward = self.exp.rfun(action)
        assert reward is not None, "Reward received from experiment %s is None."%str(exp)
        reward_hat = reward/self.p[action]
        self.W[action] = self.W[action] * np.exp(self.gamma * reward_hat / self.K)

    def run(self,iter):
        for i in xrange(iter):
            self.update()
            if self.debug == 1:
                self.log = np.vstack((self.log, self.p))


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

if __name__ == '__main__':
    exp = StaticExp()
    alg = Exp3(5, 0.1, exp, debug=1)
    iter = 1000
    alg.run(iter)
    for i in xrange(alg.K):
        plt.plot(xrange(iter+1), alg.log[:,i], label="Action %d" % i)
    plt.ylabel("Iteration Number")
    plt.xlabel("Exploration Rate")
    plt.legend()
    plt.show()

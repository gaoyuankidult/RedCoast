import numpy as np
import matplotlib.pyplot as plt


class Exp3(object):

    def __init__(self, K, gamma, exp, debug=0):
        """ Implementation of exp3 algorithm.

        :param K: number of possible actions.
        :param gamma: exploration rate.
        :param exp: instance of experiment.
        :param debug: debug indicator. if debug is 1, program runs in debug mode. default value is 0.
        """
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
        assert reward is not None, "Reward received from experiment %s is None."%str(self.exp)
        reward_hat = reward/self.p[action]
        self.W[action] = self.W[action] * np.exp(self.gamma * reward_hat / self.K)

    def run(self, niter):
        for i in xrange(niter):
            self.update()
            if self.debug == 1:
                self.log = np.vstack((self.log, self.p))

                print "New iteration..."
                for i in xrange(self.K):
                    print self.log[:, i]
                #plt.ylabel("Iteration Number")
                #plt.xlabel("Exploration Rate")
                #plt.legend()
                #plt.savefig("exp3_algorithm.png")


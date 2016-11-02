import numpy as np
import tensorflow as tf


class NeuralBandit(object):
    """
    # Arguments
    K: int >0. Number of actions
    gamma: float >=0 <=1. Tempering parameter
    exp: Instance of Experiment class
    debug: int = 0 or 1. Whether it is a debug run or not. 1 indicates it is a debug run.
    #References
        -[A Neural Networks Committee for the Contextual Bandit Problem](https://arxiv.org/abs/1409.8191)
    """
    def __init__(self, K, gamma, plambda, hidden, shape, exp, debug=0):
        self.K = K
        self.gamma = gamma
        self.plambda = plambda
        self.hidden = hidden
        assert len(shape)== 2, "The value of shape is %s, shape can only specify two dimensions" % str(shape)
        self.shape = shape
        self.exp = exp
        self.debug = debug
        self.p = np.array(np.ones([self.K])) / self.K
        if self.debug:
            self.log = self.p

        W1 = tf.Variable(tf.random_uniform([self.hidden, self.K], -0.5, 0.5))
        b1 = tf.Variable(tf.zeros(self.hidden))
        self.W = [W1]
        self.b = [b1]
        for i in xrange(self.K - 1):
            self.W.append(Wi)
            self.b.append(bi)
            Wi = tf.random_uniform([self.hidden, self.K], -0.5, 0.5)
            bi = tf.zeros[self.hidden]

        self.init = tf.initialize_all_variables()
        self.sess = tf.Session()

    def update(self, x_data, imode):
        self.y = []
        for i in xrange(self.K):
            self.y.append(self.W[i] * x_data + self.b[i])
        ymax = max(self.y)
        iymax = self.y.index(ymax)

        # select action according to following exploration and exploitation strategy and get the reward
        if imode: # init mode
            for i in xrange(self.K):
                action = i
                reward = self.exp.rfun(action)
                # tarin using label as reward
                loss = tf.reduce_mean(tf.square(self.y[i] - reward))
                optimizer = tf.train.GradientDescentOptimizer(0.5)
                train = optimizer.minimize(loss)

                self.sess.run(self.init)
                self.sess.run(train)

        else:
            self.aweight = np.array(np.zeros([self.K])) # action weight
            self.aweight[iymax] = 1
            self.p = (1 - self.gamma) * self.aweight + self.gamma / self.K
            action = np.random.choice(xrange(self.K), p=self.p)
            reward = self.exp.rfun(action)

            # tarin using label as reward
            loss = tf.reduce_mean(tf.square(self.y[i]-reward))
            optimizer = tf.train.GradientDescentOptimizer(0.5)
            train = optimizer.minimize(loss)

            self.sess.run(self.init)
            self.sess.run(train)

    def run(self, iter):
        for i in xrange(iter):
            self.update()
            if self.debug == 1:
                self.log = np.vstack((self.log, self.p))









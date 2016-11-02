from exp import StaticExp
from alg import Exp3

import matplotlib.pyplot as plt


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


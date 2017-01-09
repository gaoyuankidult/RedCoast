import unittest
from alg import Exp3
import matplotlib.pyplot as plt
from experiment import StaticExperiment


class TestMABMethods(unittest.TestCase):

    def test_exp3(self):
        """
        :return: boolean, True if the program can be executed correctly. However, the graph needs to be checked menually.
        """
        try:
            exp = StaticExperiment()
            alg = Exp3(5, 0.1, exp, debug=1)
            iter = 1000
            alg.run(iter)
            for i in xrange(alg.K):
                plt.plot(xrange(iter + 1), alg.log[:, i], label="Action %d" % i)
            plt.ylabel("Iteration Number")
            plt.xlabel("Exploration Rate")
            plt.legend()
            plt.savefig("exp3_algorithm.png")
            return True
        except:
            return False

if __name__ == '__main__':
    unittest.main()
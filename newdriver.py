from random import randint
import numpy as np
import os
import csv
import matplotlib.pyplot as plt
import NeuralNetwork as nn1
import ADD
import datetime
import timeit
import settings
import sys

def trp(tl, text):
    if TL > tl:
        print text


# Answer distribution table

class Distribution(object):
    global file_name, DSTR, add_nn, strat_nn

    # Record answers ranging from 0 to 11; 12 includes all other answers.

    def __init__(self):
        self.table = [[[0 for x in range(13)] for x in range(6)] for x in range(6)]

    # Update the distribution table when a new answer is generated.

    def update(self, eq):
        # eq is [a1,a2,result]
        a1 = eq[0]
        a2 = eq[1]
        result = eq[2]
        if (a1 > 5) or (a2 > 5):
            trp(1, "Addends (%s+%s) is/are larger than the distribution table limits -- Ignored!" % (a1, a2))
            return

        if result not in range(12):
            self.table[a1][a2][12] += 1
        else:
            self.table[a1][a2][result] += 1

    # Calculate relative frequency, return blank string when frequency is zero
    # so that the table looks clean when printed.

    def relative_frequency(self, a1, a2, result):
        s = sum(self.table[a1][a2])
        if (s == 0) or (self.table[a1][a2][result] == 0):
            return ''
        else:
            return round(float(self.table[a1][a2][result]) / s, 2)

    # Same function but return zero when frequency is zero so that
    # it can be plotted into graphs.

    def relative_frequency1(self, a1, a2, result):
        s = sum(self.table[a1][a2])
        if s == 0:
            return 0
        else:
            return float(self.table[a1][a2][result]) / s

    # Convert the whole frequency table to relative frequency.

    def relative_table(self, relative):
        if relative:
            return [[[self.relative_frequency1(x, y, z) for z in range(13)] for y in range(6)] for x in range(6)]
        else:
            return [[[self.table[x][y][z] for z in range(13)] for y in range(6)] for x in range(6)]

    # Print the table.

    def show(self, relative=True):
        table = self.relative_table(relative)
        full_name = os.path.join(os.path.join(os.path.dirname(__file__), 'test_txt'), file_name + '.txt')
        f = open(full_name, 'w')
        f.write('N_PROBLEMS: ' + str(n_problems) + '\n')
        f.write('EPOCHS: ' + str(settings.epoch) + '\n')
        f.write('LEARNING_RATE: ' + str(settings.learning_rate) + '\n')
        f.write('INCR_RIGHT: ' + str(settings.INCR_RIGHT) + '\n')
        f.write('STRATEGIES: ' + str(settings.strategies) + '\n')
        for i in range(1, 6):
            for j in range(1, 6):
                f.write("%s + %s = " % (i, j)),
                for k in range(13):
                    f.write("%s (%0.03f), " % (k, table[i][j][k])),
                f.write('\n')
            f.write('\n')

    # Export to csv file.

    def print_csv(self, relative=False):
        table = self.relative_table(relative)
        full_name = os.path.join(os.path.join(os.path.dirname(__file__), 'test_csv'), file_name + '.csv')
        with open(full_name, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['NPROBLEMS: ', settings.NPROBLEMS])
            writer.writerow(['EPOCHS: ', settings.EPOCH])
            writer.writerow(['LEARNING_RATE: ', settings.LEARNING_RATE])
            writer.writerow(['INCR_RIGHT: ', settings.INCR_RIGHT])
            writer.writerow(['STRATEGIES: ', settings.STRATEGIES])
            writer.writerow(['TEST: ', ])
            writer.writerow(['PROBLEM', 'ANSWER'])
            writer.writerow([''] + [str(x) for x in range(12)] + ['OTHER'])
            for i in range(1, 6):
                for j in range(1, 6):
                    writer.writerow(["%s + %s = " % (i, j)] + [table[i][j][k] for k in range(13)])

    # Plot the distribution table into bar charts.

    def bar_plot(self, relative=False):
        if relative:
            table = [[[self.relative_frequency1(x, y, z) for z in range(13)] for y in range(6)] for x in range(6)]

        else:
            table = [[[self.table[x][y][z] for z in range(13)] for y in range(6)] for x in range(6)]

        maxheight = max([max([max(table[x][y]) for x in range(6)]) for y in range(6)])

        plt.figure()

        for i in range(1, 6):
            for j in range(1, 6):
                ax = plt.subplot(5, 5, (i - 1) * 5 + j)
                plt.bar([x - 0.4 for x in range(13)], table[i][j], linewidth=0, color="steelblue")
                plt.xlim(-0.5, 12.5)
                plt.ylim(0, maxheight * 1.1)
                plt.text(.5, 1.03, "%s + %s" % (i, j), horizontalalignment='center', transform=ax.transAxes)
                plt.tick_params( \
                    axis='both',
                    which='both',
                    bottom='off',
                    top='off',
                    left='off',
                    right='off',
                    labelleft='on',
                    labelbottom='on', labelsize=8)
        plt.tight_layout(h_pad=1)
        plt.show()


def exec_strategy():
    global file_name, DSTR, add_nn, strat_nn
    ADD.PPA()
    # try getting a random number from a list above the confidence criterion
    retrieval = add_nn.guess(ADD.ADDEND.ad1, ADD.ADDEND.ad2)
    SOLUTION = 0
    if retrieval is not None:
        trp(1, "Used Retrieval")
        SOLUTION = retrieval
    else:
        # retrieval failed, so we get try to get a strategy from above the confidence criterion and use hands to add
        strat_num = strat_nn.guess(ADD.ADDEND.ad1, ADD.ADDEND.ad2)
        if strat_num is None:
            strat_num = randint(0, len(settings.STRATEGIES) - 1)
        SOLUTION = ADD.exec_strategy(settings.STRATEGIES[strat_num])
        # update the neural networks based on if the strategy worked or not
        strat_nn.update(ADD.ADDEND.ad1, ADD.ADDEND.ad2, SOLUTION, strat_num)
    add_nn.update(ADD.ADDEND.ad1, ADD.ADDEND.ad2, SOLUTION, ADD.ADDEND.ad1 + ADD.ADDEND.ad2)
    # add method here to get what strategy is used

    return [ADD.ADDEND.ad1, ADD.ADDEND.ad2, SOLUTION]


def test(n_times):
    global DSTR, add_nn, strat_nn

    # initialize the strategy selection network
    strat_nn = nn1.NeuralNetwork([14, 30, len(settings.STRATEGIES)])
    strat_nn.update_y()

    # initialize the assoc memory network incl. counting facts
    add_nn = counting_network()
    DSTR = Distribution()
    ADD.main()

    # Repeat n times.
    for i in range(n_times):
        eq = exec_strategy()
        DSTR.update(eq)

    # Output tables and charts.
    DSTR.show(relative=True)  # Useful for debugging, but most analysis is now done by code.
    DSTR.print_csv(relative=True)
    # DSTR.bar_plot(relative=True)

# sets up the neural network fitted to counting
def counting_network(hidden_units=30, learning_rate=0.15):
    # this is the addends matrix
    input_units = 14
    # this is the output matrix
    output_units = 13

    # fits to counting network
    NN = nn1.NeuralNetwork([input_units, hidden_units, output_units])
    X_count = []
    y_count = []
    for i in range(1, 5):
        X_count.append(nn1.addends_matrix(i, i + 1))
        y_count.append(nn1.sum_matrix(i + 2))
    X_count = np.array(X_count)
    y_count = np.array(y_count)
    NN.fit(X_count, y_count, learning_rate, 15000)
    NN.update_y()
    return NN

def runscan(l):
    global file_name, DSTR, add_nn, strat_nn
    print("Entering RUNSCAN with l = " + repr(l) + "\n")
    sys.stdout.flush()
    # Recurse over the list of scannables, mapping through each of
    # their value sets and when you get to the end, run the task. Each
    # entry in the scannable list is, first, the global value that

    # gets set, and then the list of values to set it to, as:
    # [['settings.INCR_RIGHT', 0.1, 0.2, 0.3],
    #  ['settings.N_PROBLEMS', 100, 200, 300] ...]
    if not l:
        for d in range(1, settings.NDUPS + 1):
            print("RUNSCAN running with NDUPS = " + repr(settings.NDUPS) + ", and  N_PROBLEMS = " + repr(settings.NPROBLEMS) + "\n")
            sys.stdout.flush()
            file_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            test(settings.NPROBLEMS)
    else:
        print(repr(l[0][1:]) + "\n")
        sys.stdout.flush()
        for v in l[0][1:]:
            form = l[0][0]+'='+repr(v)
            print("RUNSCAN exec'ed: " + form + "\n")
            sys.stdout.flush()
            exec(form)
            runscan(l[1:])

def main():
    global TL, strat_nn
    start = timeit.default_timer()
    TL = 0  # trace level, 0 means off
    print ("runscan(settings.scanspec)\n")
    runscan(settings.scanspec)
    stop = timeit.default_timer()
    print stop - start

if __name__ == "__main__":
    main()
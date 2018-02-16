# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"

from __future__ import division
from config import *
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import helper_functions as HF
import task_generator as TGEN


if __name__== '__main__':
    # load result from file
    result = HF.load_object_from_file("../" + PARAMS.EXP_ESEARCH_FILENAME)
    # result_prop = result.xi_prop
    # result_esearch = result.xi_esearch

    result_prop = result.eta_prop
    result_esearch = result.eta_esearch



    util_prop = [x[0] for x in result_prop]
    xi_prop = [x[1] for x in result_prop]

    util_esearch = [x[0] for x in result_esearch]
    xi_esearch = [x[1] for x in result_esearch]

    # p = e - k*e
    # k = (e-p)/e

    # diff_xi = [max(0, e-p) for e, p in zip(xi_esearch, xi_prop)]

    diff_xi = [max(0, ((e - p)/e)*100) for e, p in zip(xi_esearch, xi_prop)]



    # change font to Arial
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['font.size'] = 15
    plt.rcParams['legend.fontsize'] = 13
    plt.rcParams['axes.titlesize'] = 15
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10

    plt.hold(True)
    plt.subplot(2, 2, 1)

    plt.scatter(util_prop, diff_xi, marker='.')
    print max(diff_xi)

    plt.xlabel('Total Utilization')
    plt.ylabel('Difference in \n Cumulative Tightness (%)')

    plt.xlim([0, 2.02])
    plt.ylim([-5, 100])

    plt.tight_layout()

    plt.savefig("esearch_2.pdf", pad_inches=0.05, bbox_inches='tight')

    plt.show()

    print "Script Finished!"
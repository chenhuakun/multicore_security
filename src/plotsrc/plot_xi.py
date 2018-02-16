# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"

from __future__ import division

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import helper_functions as HF
import task_generator as TGEN


def get_xi_xy(corelist_indx, result, TOGGLE=False):
    """ Return the x and y coordinate for Schedulability plot for a given core number"""

    util_list = TGEN.get_util_list_by_core(PARAMS.CORE_LIST[corelist_indx])

    xi_list = result.xi_list_per_core[corelist_indx]
    xi_std_list = result.xi_std_list_per_core[corelist_indx]

    # xi_list = result.etasum_list_per_core[corelist_indx]
    # xi_std_list = result.etasum_std_list_per_core[corelist_indx]

    # if corelist_indx == 2 and TOGGLE:
    #     gvinx1 = len(util_list) - 22
    #     gvinx2 = len(util_list) - 20
    #     xi_list[gvinx1] = xi_list[gvinx1]+0.1
    #     xi_list[gvinx2] = xi_list[gvinx2]+0.05
    #
    # if corelist_indx == 1 and TOGGLE:
    #     gvinx1 = len(util_list) - 6
    #
    #     xi_list[gvinx1] = None


    return util_list, xi_list, xi_std_list



def plot_xi_by_coreindex(plt, corelist_index, filename):
    plt.subplot(2, 2, 1)

    x, y_prop, y_std_prop = get_xi_xy(corelist_indx=corelist_index, result=output_prop)  # for core 2
    _, y_ref, y_std_ref = get_xi_xy(corelist_indx=corelist_index, result=output_ref, TOGGLE=True)  # for core 2

    #print y_ref

    plt.hold(True)
    plt.plot(x, y_prop, marker='x',
             color='black',
             label="Proposed")

    plt.plot(x, y_ref, marker='o',
             color='black',
             label="Reference")

    plt.hold(False)

    plt.title(str(PARAMS.CORE_LIST[corelist_index]) + " Cores")
    plt.xlabel('Total Utilization')
    plt.ylabel('Avg EoS Index')

    plt.ylim([0, 1.05])
    
    if corelist_index == 2:
        plt.xticks(np.arange(0,PARAMS.CORE_LIST[corelist_index]+1, 1))   
    else:
        plt.xticks(np.arange(0,PARAMS.CORE_LIST[corelist_index]+0.5, 0.5))

    plt.legend(loc='lower left')
    plt.tight_layout()

    plt.savefig(filename, pad_inches=0.05, bbox_inches='tight')
    # plt.show()
    plt.cla()


if __name__ == '__main__':
    print "hello"
    print PARAMS.EXP_RES_FILENAME_PROP

    # load result from file
    output_prop = HF.load_object_from_file("../"+PARAMS.EXP_RES_FILENAME_PROP)
    output_ref = HF.load_object_from_file("../" + PARAMS.EXP_RES_FILENAME_REF)

    # change font to Arial
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['font.size'] = 15
    plt.rcParams['legend.fontsize'] = 13
    plt.rcParams['axes.titlesize'] = 15
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10


    #print plt.rcParams.keys()
    plt.hold(False)

    # for 2 cores
    plot_xi_by_coreindex(plt=plt, corelist_index=0, filename='xi_2.pdf')


    # for 4 cores
    plot_xi_by_coreindex(plt=plt, corelist_index=1, filename='xi_4.pdf')


    # # for 8 cores
    plot_xi_by_coreindex(plt=plt, corelist_index=2, filename='xi_8.pdf')

    print "Script Finished!"


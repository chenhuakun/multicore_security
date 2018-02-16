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


def get_sched_xy(corelist_indx, result):
    """ Return the x and y coordinate for Schedulability plot for a given core number"""

    util_list = TGEN.get_util_list_by_core(PARAMS.CORE_LIST[corelist_indx])
    sched_count = result.se_sched_list_per_core[corelist_indx]
    rt_sched_count = result.rt_sched_list_per_core[corelist_indx]

    # get the percentile
    #sched_count = [(c / rt_c) * 100 if rt_c > 0 else 0 for c, rt_c in zip(sched_count, rt_sched_count)]
    sched_count = [(c / PARAMS.N_TASKSET_EACH_CONF)*100 for c in sched_count]


    return util_list, sched_count


def get_percentage(prop, ref):

    assert len(prop) == len(ref), "Invalid input"

    # k = []
    # for i in range(0, len(prop)):
    #     if ref[i] == 0:
    #         k.append(0)
    #     else:
    #         k.append((prop[i] - ref[i])/ref[i])

    # k = [(p - r)/r for p, r in zip(prop, ref)]

    k = [((p - r) / p)*100 for p, r in zip(prop, ref)]

    return k


def plot_sched_by_coreindex(plt, corelist_index, filename):
    plt.subplot(2, 2, 1)

    x, y_prop = get_sched_xy(corelist_indx=corelist_index, result=output_prop)  # for core 2

    _, y_ref = get_sched_xy(corelist_indx=corelist_index, result=output_ref)  # for core 2
    y = get_percentage(prop=y_prop, ref=y_ref)

    plt.plot(x, y, marker='.',
             color='black',
             #label=str(PARAMS.CORE_LIST[corelist_index]) + " Cores"
             )

    plt.title(str(PARAMS.CORE_LIST[corelist_index]) + " Cores")
    
    plt.xlabel('Total Utilization')
    plt.ylabel('Improvement in \n Acceptance Ratio (%)')

    plt.ylim([-3, 103])
#    n_point = 8
#    plt.xticks(np.arange(0, max(x)+1, (max(x)+1)/n_point))
    if corelist_index == 2:
        plt.xticks(np.arange(0,PARAMS.CORE_LIST[corelist_index]+1, 1))   
    else:
        plt.xticks(np.arange(0,PARAMS.CORE_LIST[corelist_index]+0.5, 0.5))
        

    #plt.legend(loc='upper left')
    plt.tight_layout()

    plt.savefig(filename, pad_inches=0.05, bbox_inches='tight')
    # plt.show()


def plot_schedboth_by_coreindex(plt, corelist_index, filename):
    plt.subplot(2, 2, 1)

    x, y_prop = get_sched_xy(corelist_indx=corelist_index, result=output_prop)  # for core 2

    _, y_ref = get_sched_xy(corelist_indx=corelist_index, result=output_ref)  # for core 2
    #y = get_percentage(prop=y_prop, ref=y_ref)

    plt.hold(True)
    plt.plot(x, y_prop, marker='o',
             color='black',
             label="HYDRA"
             )
    plt.plot(x, y_ref, marker='*',
             linestyle='--',
             color='black',
             label="SecureCore"
             )

    plt.title(str(PARAMS.CORE_LIST[corelist_index]) + " Cores")

    plt.xlabel('Total Utilization')
    plt.ylabel('Acceptance Ratio (%)')

    plt.ylim([-3, 103])
    #    n_point = 8
    #    plt.xticks(np.arange(0, max(x)+1, (max(x)+1)/n_point))
    if corelist_index == 2:
        plt.xticks(np.arange(0, PARAMS.CORE_LIST[corelist_index] + 1, 1))
    else:
        plt.xticks(np.arange(0, PARAMS.CORE_LIST[corelist_index] + 0.5, 0.5))

    # plt.legend(loc='upper left')
    plt.tight_layout()

    plt.savefig(filename, pad_inches=0.05, bbox_inches='tight')
    plt.cla()
    # plt.show()


if __name__ == '__main__':
    print "hello"
    print PARAMS.EXP_RES_FILENAME_PROP

    # load result from file
    output_prop = HF.load_object_from_file("../"+PARAMS.EXP_RES_FILENAME_PROP)
    output_ref = HF.load_object_from_file("../" + PARAMS.EXP_RES_FILENAME_REF)
    # output_ref = HF.load_object_from_file("../" + PARAMS.EXP_RES_FILENAME_BF)

    # change font to Arial
    # change font to Arial
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['font.size'] = 15
    plt.rcParams['legend.fontsize'] = 13
    plt.rcParams['axes.titlesize'] = 15
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10

    plt.hold(False)

    # for 2 cores
    plot_sched_by_coreindex(plt=plt, corelist_index=0, filename='sched_2.pdf')
    # plot_schedboth_by_coreindex(plt=plt, corelist_index=0, filename='sched_2.pdf')
    # plot_sched_by_coreindex(plt=plt, corelist_index=0, filename='sched_2_bf.pdf')

    # for 4 cores
    plot_sched_by_coreindex(plt=plt, corelist_index=1, filename='sched_4.pdf')
    # plot_schedboth_by_coreindex(plt=plt, corelist_index=1, filename='sched_4.pdf')
    # plot_sched_by_coreindex(plt=plt, corelist_index=1, filename='sched_4_bf.pdf')

    # for 8 cores
    plot_sched_by_coreindex(plt=plt, corelist_index=2, filename='sched_8.pdf')
    # plot_schedboth_by_coreindex(plt=plt, corelist_index=2, filename='sched_8.pdf')
    # plot_sched_by_coreindex(plt=plt, corelist_index=2, filename='sched_8_bf.pdf')

    print "Script Finished!"


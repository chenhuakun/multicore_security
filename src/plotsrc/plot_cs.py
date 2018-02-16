#coding=utf-8


# Using the magic encoding
# This Python file uses the following encoding: utf-8
#!/usr/bin/python
# -*- coding: <encoding name> -*-

from __future__ import division
from __future__ import unicode_literals

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import statsmodels.api as sm # recommended import according to the docs

from config import *
import helper_functions as HF


def get_ecdf_xy(trace):
    ecdf = sm.distributions.ECDF(trace)
    x = np.linspace(min(trace), max(trace))
    y = ecdf(x)

    return x, y


def get_xy_by_core_index(core_index, output_ds):
    dt_both_prop = output_ds.detection_time_both_prop[core_index]
    dt_both_ref = output_ds.detection_time_both_ref[core_index]

    x_prop, y_prop = get_ecdf_xy(dt_both_prop)
    x_ref, y_ref = get_ecdf_xy(dt_both_ref)

    return x_prop, y_prop, x_ref, y_ref


def get_improvement_by_core_index(core_index, output_ds):
    dt_both_prop = output_ds.detection_time_both_prop[core_index]
    dt_both_ref = output_ds.detection_time_both_ref[core_index]

    # imv = [((prop - ref) / ref) % 100 for prop, ref in zip(dt_both_prop, dt_both_ref)]
    # print "Core", PARAMS.CORE_LIST[core_index], "-> Improvement: ", np.mean(imv)

    imv = ((np.mean(dt_both_prop) - np.mean(dt_both_ref))/np.mean(dt_both_ref))*100

    print "Core", PARAMS.CORE_LIST[core_index], "-> Improvement: ", -imv


def draw_plot(core_index, output_ds, filename):

    plt.subplot(2, 2, 1)

    plt.hold(True)
    x_prop, y_prop, x_ref, y_ref = get_xy_by_core_index(core_index=core_index, output_ds=output_ds)
    plt.plot(x_prop, y_prop,
             marker='.',
             markersize=4,
             linestyle='-',
             color='black',
             label="HYDRA"
             )
    plt.plot(x_ref, y_ref,
             marker='x',
             markersize=3,
             linestyle=':',
             color='black',
             #label="naïve"
             label="SingleCore"
             )

    # plt.title(str(PARAMS.CORE_LIST[core_index]) + " Cores")
    plt.xlabel('Detection Time (ms)')
    plt.ylabel('Empirical CDF')

    plt.xlim([0, 50000])

    plt.legend(loc='lower right')
    plt.tight_layout()

    plt.savefig(filename, pad_inches=0.05, bbox_inches='tight')

    # plt.show()
    plt.cla()


if __name__ == '__main__':

    print "hello"
    output_ds = HF.load_object_from_file("../" + PARAMS.EXP_CS_FILENAME)

    # change font to Arial
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['font.size'] = 15
    plt.rcParams['legend.fontsize'] = 13
    plt.rcParams['axes.titlesize'] = 15
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10


    # draw_plot(core_index=0, output_ds=output_ds, filename="cs_2.pdf")
    # draw_plot(core_index=1, output_ds=output_ds, filename="cs_4.pdf")
    # draw_plot(core_index=2, output_ds=output_ds, filename="cs_8.pdf")

    draw_plot(core_index=1, output_ds=output_ds, filename="cs_4_v2.pdf")

    # print % of improvement in detection time
    get_improvement_by_core_index(core_index=0, output_ds=output_ds)
    get_improvement_by_core_index(core_index=1, output_ds=output_ds)
    get_improvement_by_core_index(core_index=2, output_ds=output_ds)


    print "Script Finished!"


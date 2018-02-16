# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"

from __future__ import division
from config import *
import copy
import math
import random
import numpy as np
import task_generator as TGEN
import task_allocator as TALLOC
import task as TASK
import fp_simulator as SIM
import expresult as ER
import helper_functions as HF

def generate_cs_rt_taskset(n, periods, wcets, utils):
    """ Returns RT takset for case study (a list of n RT task) """

    #utils = [ci/ti for ci, ti in zip(wcets, periods)]

    rt_taskset = []
    for i in range(0, n):
        rt_taskset.append(TASK.RT_Task(wcets[i], periods[i], utils[i], periods[i], tid=i))

    return rt_taskset


def generate_cs_se_taskset(n, wcets, utils, se_names):
    """ Returns SE takset (a list of n SE task) """

    # utils = TGEN.get_utils(n, total_se_util)
    periods = [ci/ui for ci, ui in zip(wcets,utils)]

    # periods = TGEN.get_periods(n, PARAMS.CS_SE_PERIOD_MIN, PARAMS.CS_SE_PERIOD_MAX)
    # utils = [ci / ti for ci, ti in zip(wcets, periods)]

    # print periods
    # shorter index higher priority
    # periods_sorted = np.sort(periods)
    # argp = np.argsort(periods)
    # wcets_sorted = []
    #
    # for i in range(0, n):
    #     wcets_sorted.append(wcets[argp[i]])

    # print wcets_sorted
    se_taskset = []
    for i in range(0, n):
        se_taskset.append(TASK.SE_Task(wcet=wcets[i],
                                       period=periods[i],
                                       period_des=periods[i],
                                       period_max=periods[i]*PARAMS.SE_PERIOD_MAX_FACTOR,
                                       util=utils[i],
                                       deadline=periods[i], tid=se_names[i]))

    return se_taskset


def get_cs_task_config(n_core, total_system_util, total_rt_util, total_se_util, n_rt_task, n_se_task, rt_taskset, se_taskset):

    return TASK.TaskSetConfig(n_core, total_system_util, total_rt_util, total_se_util, n_rt_task, n_se_task, rt_taskset,
                              se_taskset)


if __name__ == '__main__':
    # print "hello"

    n_core_list = [2, 4, 8]
    #core = 2
    max_util = 0.7

    n_rt_task = 14
    n_se_task = 6

    # sampling_count = 2
    sim_duration = PARAMS.SIM_DURATION

    rt_period_list = [1000, 1000, 1000, 1000, 1000, 1000, 5000, 5000, 5000, 5000, 5000, 10000, 10000, 10000]  # in ms
    rt_wcet_list = [30, 30, 30, 50, 40, 50, 40, 30, 50, 300, 50, 50, 50, 200]
    rt_util_list = [ci/ti for ci, ti in zip(rt_wcet_list, rt_period_list)]

    #total_system_util = max_util * core
    total_rt_util = sum(rt_util_list)

    rt_taskset = generate_cs_rt_taskset(n_rt_task, rt_period_list, rt_wcet_list, rt_util_list)

    # sorted
    se_wcet_list = [364039069, 3845016680, 4003706162, 4031471265, 4220361072, 26701619825]
    se_names = ['IDS_BIN', 'CONF', 'KER', 'FS_BIN', 'NW_PCKT', 'FS_LIB']
    se_task_attack_detector_list = ['SE_TaskIDS_BIN', 'SE_TaskNW_PCKT', 'SE_TaskCONF', 'SE_TaskKER']

    se_wcet_list = [int(math.floor(ci/1000000)) for ci in se_wcet_list]  # change to millisecond

    # se_util_factor = 3.8
    # se_util_list = [se_util_factor/n_se_task] * n_se_task  # total Util for SE task 0.5 (we have 6 security task)
    #
    # total_se_util = sum(se_util_list)
    #
    # total_system_util = total_rt_util+total_se_util
    #
    # se_taskset = generate_cs_se_taskset(n_se_task, se_wcet_list, se_util_list, se_names)


    ###
    detection_time_both_prop = np.empty((len(n_core_list), 0)).tolist()  # for each core
    detection_time_any_prop = np.empty((len(n_core_list), 0)).tolist()  # for each core

    detection_time_both_ref = np.empty((len(n_core_list), 0)).tolist()  # for each core
    detection_time_any_ref = np.empty((len(n_core_list), 0)).tolist()  # for each core

    for core_index, core in enumerate(n_core_list):

        se_util_factor = core - 0.3 # a loaded system
        se_util_list = [se_util_factor / n_se_task] * n_se_task  # total Util for SE task 0.5 (we have 6 security task)

        total_se_util = sum(se_util_list)

        total_system_util = total_rt_util + total_se_util

        se_taskset = generate_cs_se_taskset(n_se_task, se_wcet_list, se_util_list, se_names)

        tc_conf = get_cs_task_config(n_core=core,
                                     total_system_util=total_system_util,
                                     total_rt_util=total_rt_util,
                                     total_se_util=total_se_util,
                                     n_rt_task=n_rt_task,
                                     n_se_task=n_se_task,
                                     rt_taskset=rt_taskset,
                                     se_taskset=se_taskset)

        # get RT allocation
        rt_alloc = TALLOC.get_rt_task_assignemnt(tc_conf, PARAMS.EXPERIMENT_NAME_PROP, worst_fit=True)



        # some error checking
        if rt_alloc is None:
            print "RT Taskset is not Schedulable (Holy Cow!)"
            raise Exception("Holy Cow!")

        # print rt_alloc
        # get the security task parameter

        tc_conf_prop = copy.deepcopy(tc_conf)
        tc_conf_ref = copy.deepcopy(tc_conf)

        _, se_opt_period_list_prop, _, x = TALLOC.allocate_security_task(tc_conf_prop, rt_alloc, True)
        _, se_opt_period_list_ref, _ = TALLOC.find_se_task_param_best_fit(tc_conf_ref, rt_alloc)

        # round it
        se_opt_period_list_prop = [int(round(i)) for i in se_opt_period_list_prop]
        se_opt_period_list_ref = [int(round(i)) for i in se_opt_period_list_ref]

        # print se_opt_period_list_prop
        # print se_opt_period_list_ref
        #
        # raise Exception("ok")

        # sim_duration = max(max(se_opt_period_list_prop), max(se_opt_period_list_ref))
        # sim_duration = sim_duration * PARAMS.SIM_DURATON_FACTOR

        #print sim_duration

        # update period
        for i in range(0, n_se_task):
            tc_conf_prop.se_taskset[i].period = copy.deepcopy(se_opt_period_list_prop[i])
            tc_conf_ref.se_taskset[i].period = copy.deepcopy(se_opt_period_list_ref[i])

        for i in range(0, PARAMS.N_SIM_SAMPLES):
            print "=== Core", core, "Exp Count", i+1, "==="

            attack_time = random.randint(PARAMS.ATTACK_MIN, PARAMS.ATTACK_MAX)
            print "Attack time", attack_time

            dt_both_prop, dt_any_prop = SIM.simulate_schedule(core, tc_conf_prop, rt_alloc, x, sim_duration, attack_time, se_task_attack_detector_list, PARAMS.EXPERIMENT_NAME_PROP)
            dt_both_ref, dt_any_ref = SIM.simulate_schedule(core, tc_conf_prop, rt_alloc, x, sim_duration, attack_time, se_task_attack_detector_list,
                              PARAMS.EXPERIMENT_NAME_BF)

            # detection_time_prop[core_index].append(SIM.simulate_schedule(core, tc_conf_prop, rt_alloc, x, sim_duration, attack_time,  se_task_attack_detector_list, PARAMS.EXPERIMENT_NAME_PROP))
            # detection_time_ref[core_index].append(SIM.simulate_schedule(core, tc_conf_prop, rt_alloc, x, sim_duration, attack_time, se_task_attack_detector_list,
            #                   PARAMS.EXPERIMENT_NAME_REF))

            detection_time_both_prop[core_index].append(dt_both_prop)
            detection_time_any_prop[core_index].append(dt_any_prop)
            detection_time_both_ref[core_index].append(dt_both_ref)
            detection_time_any_ref[core_index].append(dt_any_ref)

    sim_exp_result = ER.CSSimResult(detection_time_both_prop, detection_time_any_prop,
                                    detection_time_both_ref, detection_time_any_ref)

    print "Experiment Done! Writing Results..."
    HF.write_object_to_file(sim_exp_result, PARAMS.EXP_CS_BF_FILENAME)

    # print "prop"
    # print detection_time_both_prop
    # print detection_time_any_prop
    #
    # print "ref"
    # print detection_time_both_ref
    # print detection_time_any_ref

    print "Script Finished!!"

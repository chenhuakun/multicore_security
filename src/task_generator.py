__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"


import numpy as np
import task as TASK
import random
from collections import defaultdict
import copy
import helper_functions as HF
from config import *



def get_periods(n, low, high):
    """ Returns n periods (integers) for a given range  """

    periods = np.random.choice(range(low, high+1), n, replace=False)

    # shorter index higher priority
    return np.sort(periods)


def get_utils(n, base_util):
    """ Returns the n utilization values using Stafford Rand Fixed Sum Algorithm """
    return HF.get_util_by_rand_fixed_sum(n, base_util)


def get_wcets(utils, periods):
    """ Returns WCET """
    return [ui * ti for ui, ti in zip(utils, periods)]


# def generate_taskset(utils, periods):
#     print "hello"


def get_rt_taskset(n, total_rt_util):
    """ Returns RT takset (a list of n RT task) """

    periods = get_periods(n, PARAMS.RT_PERIOD_MIN, PARAMS.RT_PERIOD_MAX)
    utils = get_utils(n, total_rt_util)
    wcets = get_wcets(utils, periods)

    rt_taskset = []
    for i in range(0, n):
        rt_taskset.append(TASK.RT_Task(wcets[i], periods[i], utils[i], periods[i], tid=i))

    return rt_taskset


def get_se_taskset(n, total_se_util):
    """ Returns RT takset (a list of n SE task) """

    periods = get_periods(n, PARAMS.SE_PERIOD_MIN, PARAMS.SE_PERIOD_MAX)
    utils = get_utils(n, total_se_util)
    wcets = get_wcets(utils, periods)

    se_taskset = []
    for i in range(0, n):
        se_taskset.append(TASK.SE_Task(wcet=wcets[i],
                                       period=periods[i],
                                       period_des=periods[i],
                                       period_max=periods[i]*PARAMS.SE_PERIOD_MAX_FACTOR,
                                       util=utils[i],
                                       deadline=periods[i], tid=i))

    return se_taskset


def generate_taskset(n_core, n_rt_task, n_se_task, total_system_util):

    total_se_util = total_system_util * PARAMS.SE_UTIL_PERCENTAGE
    total_rt_util = total_system_util - total_se_util

    rt_taskset = get_rt_taskset(n_rt_task, total_rt_util)
    se_taskset = get_se_taskset(n_se_task, total_se_util)

    return TASK.TaskSetConfig(n_core, total_system_util, total_rt_util, total_se_util, n_rt_task, n_se_task, rt_taskset, se_taskset)


def generate_all_tasksets():
    """ Generate the all taskset for all core configurations """

    all_task_set_dict = defaultdict(lambda: defaultdict(dict))

    for core in PARAMS.CORE_LIST:
        util_list = get_util_list_by_core(core)
        for util in util_list:
            print "Core:", core, "System Utilization:", util
            for ntc in range(0, PARAMS.N_TASKSET_EACH_CONF):

                # print "Core:", core, "System Utilization:", util, "Taskset Index:", ntc

                n_rt_task = random.randint(PARAMS.N_RT_TASK_MIN * core, PARAMS.N_RT_TASK_MAX * core)
                n_se_task = random.randint(PARAMS.N_SE_TASK_MIN * core, PARAMS.N_SE_TASK_MAX * core)

                taskset = generate_taskset(core, n_rt_task, n_se_task, util)
                all_task_set_dict[core][util][ntc] = copy.deepcopy(taskset)

    return all_task_set_dict


def get_esearch_util_list_by_core(n_core):
    """ return utilization based on the concept of utilization groups """

    total_grp = n_core * PARAMS.N_BASE_UTIL_GRP
    util_list = []
    for i in range(PARAMS.N_TASKSET_EACH_CONF_ESEARCH):
        for u in range(total_grp):
            base_util = random.uniform(0.02 + 0.1 * u, 0.08 + 0.1 * u)
            util_list.append(base_util)
    return util_list


def generate_exsearch_tasksets(n_core):
    """ Generate the all taskset for exhaustive search experiment """

    all_task_set_dict = defaultdict(lambda: defaultdict(dict))
    util_list = get_esearch_util_list_by_core(n_core)
    #print util_list

    for util in util_list:

        # print "Core:", core, "System Utilization:", util, "Taskset Index:", ntc

        n_rt_task = random.randint(PARAMS.N_RT_TASK_MIN * n_core, PARAMS.N_RT_TASK_MAX * n_core)
        n_se_task = random.randint(PARAMS.N_SE_TASK_ESEARCH_MIN * n_core, PARAMS.N_SE_TASK_ESEARCH_MAX * n_core)

        taskset = generate_taskset(n_core, n_rt_task, n_se_task, util)
        all_task_set_dict[util] = copy.deepcopy(taskset)

    return all_task_set_dict, util_list


def get_util_list_by_core(core):
    """ Return the list of total utilization values we analyze based on Multi-core paper """

    return np.arange(PARAMS.UTIL_RANGE_MIN * core, PARAMS.UTIL_RANGE_MAX * core, PARAMS.UTIL_RANGE_STEP * core)


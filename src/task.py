__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"

import copy
import math
import helper_functions as HF


class RT_Task:
    def __init__(self, wcet, period, util, deadline, tid):
        self.wcet = wcet
        self.period = period
        self.util = util
        self.deadline = deadline
        self.tid = tid
        self.name = "RT_Task" + str(tid)


class SE_Task:
    def __init__(self, wcet, period, period_des, period_max, util, deadline, tid):
        self.wcet = wcet
        self.period = period  # actual period (obtained later by optimization problem)
        self.period_des = period_des
        self.period_max = period_max
        self.util = util
        self.deadline = deadline
        self.tid = tid
        self.name = "SE_Task" + str(tid)


class TaskSetConfig:
    def __init__(self, n_core, total_util, rt_util, se_util, n_rt_task, n_se_task, rt_taskset, se_taskset):
        self.core = n_core
        self.total_util = total_util
        self.rt_util = rt_util
        self.se_util = se_util
        self.n_rt_task = n_rt_task
        self.n_se_task = n_se_task
        self.rt_taskset = copy.deepcopy(rt_taskset)
        self.se_taskset = copy.deepcopy(se_taskset)


class Job:
    def __init__(self, arrival_time, wcet, priority, absolute_deadline, core_index, name):
        self.arrival_time = arrival_time
        self.wcet = wcet
        self.priority = priority
        self.usage = 0
        self.absolute_deadline = absolute_deadline
        self.core_index = core_index
        self.name = name


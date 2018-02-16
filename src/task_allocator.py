# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"

from __future__ import division
import task as TASK
import numpy as np
from numpy import linalg as LA
import copy
import gpkit
import helper_functions as HF
import itertools as it
from config import *


def get_interference(core_index, task_index, current_alloc, period_list, wcet_list):
    """ Return the interference experience by a task (task_index) for a given core """
    intf = 0
    for i in range(0, task_index):
        intf += current_alloc[i][core_index] * (period_list[task_index] / period_list[i] + 1) * wcet_list[i]

    # print "Core", core_index, "Task", task_index, "interference", intf
    return intf


def check_core_schedulability(core_index, task_index, current_alloc, period_list, wcet_list):

    # check whether we can fit task_index to core_index

    intf = get_interference(core_index, task_index, current_alloc, period_list, wcet_list)

    wcrt = wcet_list[task_index] + intf

    # WCRT less than deadline (Return Schedulable)
    if wcrt <= period_list[task_index]:
        return True

    return False


def get_possible_cores(n_cores, task_index, current_alloc, period_list, wcet_list):

    # the the list of possible cores that we can fit the task marked by task_index
    # all are zero indexing
    possible_cores = []
    for core_index in range(0, n_cores):

        isSched = check_core_schedulability(core_index, task_index, current_alloc, period_list, wcet_list)
        if isSched:
            possible_cores.append(core_index)

    return possible_cores


def get_worst_fit_core_index(n_rt_task, rt_alloc, possible_cores, rt_taskset):
    """ Return the core with best fit strategy """

    min_util = 100  # a large number
    min_m = -1
    for m in possible_cores:
        util = [(rt_taskset[i].wcet/rt_taskset[i].period) * rt_alloc[i][m] for i in range(0, n_rt_task)]
        util = sum(util)
        if min_util > util:
            min_util = util
            min_m = m

    return min_m


def get_rt_task_assignemnt(taskset_config, EXP_NAME, worst_fit=False):
    """ Return the RT task assignment using FIRST FIT stategy
    Output: a 2D Matrix X: x[i,j] = i if task i assigned to core j"""

    rt_taskset = taskset_config.rt_taskset

    if EXP_NAME == PARAMS.EXPERIMENT_NAME_PROP:
        n_core = taskset_config.core
    elif EXP_NAME == PARAMS.EXPERIMENT_NAME_REF:
        n_core = taskset_config.core - 1  # since we use rest of the cores for security task
    else:
        raise Exception("Invalid parameter for RT Task assignment!")

    # the allocation matrix
    x = np.zeros((taskset_config.n_rt_task, n_core))
    x[0][0] = 1

    period_list = [task.period for task in rt_taskset]
    wcet_list = [task.wcet for task in rt_taskset]

    # print "number of RT task:", taskset_config.n_rt_task
    for tindx in range(1, taskset_config.n_rt_task):
        possible_cores = get_possible_cores(n_cores=n_core,
                                            task_index=tindx, current_alloc=x, period_list=period_list, wcet_list=wcet_list)

        # print "task", tindx, "possible core", possible_cores

        # if the list of possible cores is not empty
        if possible_cores:

            if worst_fit:
                ffit_core_index = get_worst_fit_core_index(n_rt_task=taskset_config.n_rt_task,
                                                          rt_alloc=x,
                                                          possible_cores=possible_cores,
                                                          rt_taskset=rt_taskset)
            else:
                ffit_core_index = min(possible_cores)  # select the minimum core index


            x[tindx][ffit_core_index] = 1  # assign the task to the core
        else:
            print "RT Taskset Unshcedulable for", "(", taskset_config.core, ",", taskset_config.total_util, ")"
            return None

    # print x
    return x


def solve_gp_by_core_task(core_index, se_task_index, rt_alloc, se_alloc, n_rt_task, rt_period_list, rt_wcet_list,
                          se_period_list, se_des_period_list, se_max_period_list, se_wcet_list, verbose=True):
    """ Solve the GP for a given core for given task """

    # solve the GP
    try:
        verbosity = 0  # no verbosity
        ti_des = se_des_period_list[se_task_index]
        ti_max = se_max_period_list[se_task_index]

        # Decision variables
        ti = gpkit.Variable("ti")

        rt_intf = 0
        se_intf = 0

        for i in range(0, n_rt_task):
            rt_intf += ((ti + rt_period_list[i]) * (1 / rt_period_list[i]) * rt_wcet_list[i]) * rt_alloc[i][core_index]

        for i in range(0, se_task_index):
            se_intf += ((ti + se_period_list[i]) * (1 / se_period_list[i]) * se_wcet_list[i]) * se_alloc[i][core_index]

        wcrt = se_wcet_list[se_task_index] + rt_intf + se_intf

        objective = (1/ti_des) * ti
        constraints = []
        constraints.append(ti_des * (1/ti) <= 1)  # period bound
        constraints.append((1/ti_max) * ti <= 1)  # period bound
        constraints.append(wcrt * (1/ti) <= 1)  # schedulability constraint

        m = gpkit.Model(objective, constraints)

        try:
            with HF.timeout_handler(PARAMS.GP_TIMEOUT):
                sol = m.solve(verbosity=verbosity)
        except (RuntimeWarning, HF.TimeoutException):
            # if there the solution is not optimal return None
            if verbose:
                print "PROP_SHCME: GP Solution is not optimal or timeout!"
            return None, None
    except Exception:
        if verbose:
            print "PROP_SHCME: Unable to find any solution!"
        return None, None

    eta = 1 / float(sol["cost"])  # make it inverse (since we maximize)

    # print "Ti_des:", ti_des
    # print "Optimal cost:", eta
    # print("Optimal Period: %s" % sol(ti))

    # return the optimal eta and corresponding period
    return eta, sol(ti)


def calculate_xi(opt_period_list, des_period_list, max_period_list):
    """ Calculate Xi from equation (see older paper)"""

    numerator = np.subtract(opt_period_list, des_period_list)
    denominator = np.subtract(max_period_list, des_period_list)

    numerator = LA.norm(numerator)
    denominator = LA.norm(denominator)

    xi = 1 - (numerator/denominator)
    return xi


def calculate_eta_per_task(opt_period_list, des_period_list):
    """ Returns individual eta for the security task
        Output is a list """

    opt_p = np.multiply(opt_period_list, 1.0).tolist()  # for safety make it float

    return np.divide(des_period_list, opt_p).tolist()


def get_se_assignment_by_comb(n_core, n_task, comb):
    """retunrns the assignment matrix by combination"""

    # the allocation matrix
    x = np.zeros((n_task, n_core))

    for i in range(len(comb)):
        x[i][comb[i]] = 1

    return x


def allocate_security_task_esearch(taskset_config, rt_alloc):
    """ Return solution based on exhaustive search """

    rt_taskset = taskset_config.rt_taskset
    se_taskset = taskset_config.se_taskset

    n_core = taskset_config.core

    rt_period_list = [task.period for task in rt_taskset]
    rt_wcet_list = [task.wcet for task in rt_taskset]

    se_period_list = copy.deepcopy([task.period for task in se_taskset])  # since this we will update
    se_des_period_list = [task.period_des for task in se_taskset]
    se_max_period_list = [task.period_max for task in se_taskset]
    se_wcet_list = [task.wcet for task in se_taskset]

    eta_list = [None] * taskset_config.n_se_task

    all_pos_comb = list(it.product(range(n_core), repeat=taskset_config.n_se_task))

    print "Total Combinations", len(all_pos_comb)
    eta_max = -1
    xi_max = -1
    found = False
    for c in all_pos_comb:
        comb = list(c)
        # print "list", comb

        x = get_se_assignment_by_comb(n_core, taskset_config.n_se_task, comb)
        # print x

        # for j in range(taskset_config.n_se_task):
        #     cindx = list(x[j, :]).index(1)
        #     print "task", j,  "core", cindx
        # print "---"

        eta_list, pstar, xi = solve_gp_by_core_for_esearch(rt_alloc=rt_alloc,
                                                           se_alloc=x,
                                                           n_rt_task=taskset_config.n_rt_task,
                                                           n_se_task=taskset_config.n_se_task,
                                                           rt_period_list=rt_period_list,
                                                           rt_wcet_list=rt_wcet_list,
                                                           se_period_list=se_period_list,
                                                           se_des_period_list=se_des_period_list,
                                                           se_max_period_list=se_max_period_list,
                                                           se_wcet_list=se_wcet_list,
                                                           verbose=False)
        if eta_list is None:
            # print "invalid config", x
            continue
        if eta_max < sum(eta_list):
            eta_max = sum(eta_list)
            xi_max = xi
            # print "current xi max", xi_max
            found = True

    if found:
        print "Solution found for Exhaustive Search! Xi is", xi_max
    else:
        print "No Solution found for Exhaustive Search!"

    return eta_max, xi_max



def allocate_security_task_esearch_v2(taskset_config, rt_alloc):
    """ Return solution based on exhaustive search """

    rt_taskset = taskset_config.rt_taskset
    se_taskset = taskset_config.se_taskset

    n_core = taskset_config.core

    rt_period_list = [task.period for task in rt_taskset]
    rt_wcet_list = [task.wcet for task in rt_taskset]

    se_period_list = copy.deepcopy([task.period for task in se_taskset])  # since this we will update
    se_des_period_list = [task.period_des for task in se_taskset]
    se_max_period_list = [task.period_max for task in se_taskset]
    se_wcet_list = [task.wcet for task in se_taskset]

    eta_list = [None] * taskset_config.n_se_task

    all_pos_comb = list(it.product(range(n_core), repeat=taskset_config.n_se_task))

    print "Total Combinations", len(all_pos_comb)
    eta_max = 0
    xi_max = -1
    #pstar = []
    found = False
    for c in all_pos_comb:
        comb = list(c)
        # print "list", comb

        x = get_se_assignment_by_comb(n_core, taskset_config.n_se_task, comb)

        ptmp = [None]*taskset_config.n_se_task

        etasum = 0
        for stindx in range(0, taskset_config.n_se_task):

            core_index = list(x[stindx, :]).index(1)  # find the where this task is allocated

            eta, gp_period = solve_gp_by_core_task(core_index=core_index, se_task_index=stindx,
                                                   rt_alloc=rt_alloc,
                                                   se_alloc=x,
                                                   n_rt_task=taskset_config.n_rt_task,
                                                   rt_period_list=rt_period_list,
                                                   rt_wcet_list=rt_wcet_list,
                                                   se_period_list=se_period_list,
                                                   se_des_period_list=se_des_period_list,
                                                   se_max_period_list=se_max_period_list,
                                                   se_wcet_list=se_wcet_list,
                                                   verbose=False)

            if eta is None:
                etasum = 0
                break

            etasum += eta
            ptmp[stindx] = copy.deepcopy(gp_period)

        if eta_max < etasum:
            found = True
            eta_max = etasum
            xi_max = calculate_xi(ptmp, se_des_period_list, se_max_period_list)

    if found:
        print "Solution Found for Exhaustive Search! Xi is:", xi_max
    else:
        print "== NO Solution Found for Exhaustive Search!==", xi_max
    return eta_max, xi_max


def allocate_security_task(taskset_config, rt_alloc, return_schedule=False):
    """ Allocate security tasks based on heuristic
     Assuming the RT Taskset is schedulable """

    # the allocation matrix
    # x[i,j] = i if task i assigned to core j
    x = np.zeros((taskset_config.n_se_task, taskset_config.core))


    rt_taskset = taskset_config.rt_taskset
    se_taskset = taskset_config.se_taskset

    rt_period_list = [task.period for task in rt_taskset]
    rt_wcet_list = [task.wcet for task in rt_taskset]

    se_period_list = copy.deepcopy([task.period for task in se_taskset])  # since this we will update
    se_des_period_list = [task.period_des for task in se_taskset]
    se_max_period_list = [task.period_max for task in se_taskset]
    se_wcet_list = [task.wcet for task in se_taskset]

    eta_list = [None] * taskset_config.n_se_task

    for tindx in range(0, taskset_config.n_se_task):
        opt_eta = -1
        opt_period = -1
        opt_core_index = -1

        for core_index in range(0, taskset_config.core):
            eta, gp_period = solve_gp_by_core_task(core_index=core_index, se_task_index=tindx,
                                  rt_alloc=rt_alloc,
                                  se_alloc=x,
                                  n_rt_task=taskset_config.n_rt_task,
                                  rt_period_list=rt_period_list,
                                  rt_wcet_list=rt_wcet_list,
                                  se_period_list=se_period_list,
                                  se_des_period_list=se_des_period_list,
                                  se_max_period_list=se_max_period_list,
                                  se_wcet_list=se_wcet_list)

            if eta is None or gp_period is None:
                print "Unschedulable For Security Task", tindx,  "for core", core_index
                # check for next core
                continue

            if eta > opt_eta:
                opt_eta = eta
                opt_period = gp_period
                opt_core_index = core_index

        # we get an allocation
        if opt_core_index >= 0:
            x[tindx][opt_core_index] = 1  # assign the task to the core
            eta_list[tindx] = opt_eta
            se_period_list[tindx] = opt_period  # update period
        else:
            print "Unable to find any core for Security task", tindx
            return None, None, None

    # print x
    # print eta_list
    xi = calculate_xi(se_period_list, se_des_period_list, se_max_period_list)
    #print "xi is:", xi
    if return_schedule:
        return eta_list, se_period_list, xi, x
    else:
        return eta_list, se_period_list, xi


def solve_gp_all_task_single_core(n_se_task, se_period_list, se_des_period_list, se_max_period_list, se_wcet_list):
    """ This routine will solve the GP for all security tasks running a given single core index
        Return: Objecttive eta and the Period Vector """

    # solve the GP
    try:
        verbosity = 0  # no verbosity

        # Decision variables
        ti = gpkit.VectorVariable(n_se_task, "ti")

        omegai = range(1, n_se_task+1)  # a list of weights
        omegai = omegai[::-1]  # reverse (shorter index higher weight)

        omegai = [i / sum(omegai) for i in omegai]  # normalize the sum of weignt to 1

        constraints = []

        objective = 0
        for stindx in range(0, n_se_task):
            ti_des = se_des_period_list[stindx]
            ti_max = se_max_period_list[stindx]

            # calculate WCRT
            rt_intf = 0  # there is no interference from RT task
            # for i in range(0, n_rt_task):
            #     rt_intf += ((ti[stindx] + rt_period_list[i]) * (1 / rt_period_list[i]) * rt_wcet_list[i]) * rt_alloc[i][core_index]

            se_intf = 0
            for i in range(0, stindx):
                se_intf += ((ti[stindx] + se_period_list[i]) * (1 / se_period_list[i]) * se_wcet_list[i])

            wcrt = se_wcet_list[stindx] + rt_intf + se_intf

            constraints.append(ti_des * (1 / ti[stindx]) <= 1)  # period bound
            constraints.append((1 / ti_max) * ti[stindx] <= 1)  # period bound
            constraints.append(wcrt * (1 / ti[stindx]) <= 1)  # schedulability constraint

            objective += (1/(omegai[stindx] * ti_des)) * ti[stindx]

        m = gpkit.Model(objective, constraints)
        try:
            with HF.timeout_handler(PARAMS.GP_TIMEOUT):
                sol = m.solve(verbosity=verbosity)
        except (RuntimeWarning, HF.TimeoutException):
            # if there the solution is not optimal return None
            print "REF_SCHEME: GP Solution is not optimal or timeout!"
            return None, None

    except Exception:
        print "REF_SCHEME: Unable to find any Solution!"
        return None, None

    #eta = 1 / float(sol["cost"])  # make it inverse (since we maximize)
    pstar = sol(ti)

    # print "Ti_des:", se_des_period_list
    # print "Optimal cost:", eta
    # print("Optimal Period: %s" % sol(ti))

    eta_list = calculate_eta_per_task(pstar, se_des_period_list)
    # print "eta list:", eta_list
    return eta_list, pstar


def solve_gp_by_core_for_esearch(rt_alloc, se_alloc, n_rt_task, n_se_task, rt_period_list, rt_wcet_list, se_period_list,
                                 se_des_period_list, se_max_period_list, se_wcet_list, verbose=True):
    """ This routine will solve the GP for a given secruity task assignment for given core_index
        Return: Objecttive eta and the Period Vector """

    # solve the GP
    try:
        verbosity = 0  # no verbosity

        # Decision variables
        ti = gpkit.VectorVariable(n_se_task, "ti")

        omegai = range(1, n_se_task+1)  # a list of weights
        omegai = omegai[::-1]  # reverse (shorter index higher weight)

        # omegai = [i / sum(omegai) for i in omegai]  # normalize the sum of weignt to 1
        omegai = [i*0 + 1 for i in omegai]  # normalize the sum of weignt to 1

        constraints = []

        objective = 0
        for stindx in range(0, n_se_task):
            ti_des = se_des_period_list[stindx]
            ti_max = se_max_period_list[stindx]

            core_index = list(se_alloc[stindx, :]).index(1)  # find the where this task is allocated

            # calculate WCRT
            rt_intf = 0
            for i in range(0, n_rt_task):
                rt_intf += ((ti[stindx] + rt_period_list[i]) * (1 / rt_period_list[i]) * rt_wcet_list[i]) * rt_alloc[i][core_index]

            se_intf = 0
            for i in range(0, stindx):
                se_intf += ((ti[stindx] + se_period_list[i]) * (1 / se_period_list[i]) * se_wcet_list[i]) * se_alloc[i][core_index]

            wcrt = se_wcet_list[stindx] + rt_intf + se_intf

            constraints.append(ti_des * (1 / ti[stindx]) <= 1)  # period bound
            constraints.append((1 / ti_max) * ti[stindx] <= 1)  # period bound
            constraints.append(wcrt * (1 / ti[stindx]) <= 1)  # schedulability constraint

            objective += (1/(omegai[stindx] * ti_des)) * ti[stindx]

        m = gpkit.Model(objective, constraints)
        try:
            with HF.timeout_handler(PARAMS.GP_TIMEOUT):
                sol = m.solve(verbosity=verbosity)
        except (RuntimeWarning, HF.TimeoutException):
            # if there the solution is not optimal return None
            if verbose:
                print "EXHAUSTIVE_SEARCH: GP Solution is not optimal or timeout!"
            return None, None, None

    except Exception:
        if verbose:
            print "EXHAUSTIVE_SEARCH: Unable to find any Solution!"
        return None, None, None

    # eta = 1 / float(sol["cost"])  # make it inverse (since we maximize)
    pstar = sol(ti)

    # print "Ti_des:", se_des_period_list
    # print "Optimal cost:", eta
    # print("Optimal Period: %s" % sol(ti))

    eta_list = calculate_eta_per_task(pstar, se_des_period_list)

    xi = calculate_xi(pstar, se_des_period_list, se_max_period_list)

    # print "eta list:", eta_list
    return eta_list, pstar, xi


def find_se_task_param_reference_scheme(taskset_config):
    """ This routine will find the security tasks paramters for reference scheme
        Reference Scheme: allocate security tasks to a single core (SecureCore)
        We consider Highest core index is the secure core """

    # se_core_index = taskset_config.core - 1  # always use highest core index (remember we use 0 indexing)

    # rt_taskset = taskset_config.rt_taskset
    se_taskset = taskset_config.se_taskset

    # rt_period_list = [task.period for task in rt_taskset]
    # rt_wcet_list = [task.wcet for task in rt_taskset]

    se_period_list = copy.deepcopy([task.period for task in se_taskset])
    se_des_period_list = [task.period_des for task in se_taskset]
    se_max_period_list = [task.period_max for task in se_taskset]
    se_wcet_list = [task.wcet for task in se_taskset]

    eta_list, gp_period_list = solve_gp_all_task_single_core(n_se_task=taskset_config.n_se_task,
                                                             se_period_list=se_period_list,
                                                             se_des_period_list=se_des_period_list,
                                                             se_max_period_list=se_max_period_list,
                                                             se_wcet_list=se_wcet_list)

    if eta_list is None or gp_period_list is None:
        print "REF_SCHEME: Unable to find parameters for Security task!"
        return None, None, None

    xi = calculate_xi(gp_period_list, se_des_period_list, se_max_period_list)

    return eta_list, gp_period_list, xi


def get_slack_by_core_index(core_index, n_rt_task, n_se_task, rt_alloc, se_alloc, rt_period_list, rt_wcet_list, se_period_list, se_wcet_list):

    rt_u = 0
    for i in range(n_rt_task):
        rt_u += (rt_wcet_list[i]/rt_period_list[i]) * rt_alloc[i][core_index]

    se_u = 0
    for i in range(n_se_task):
        se_u += (se_wcet_list[i]/se_period_list[i]) * se_alloc[i][core_index]

    slack = 1 - (rt_u + se_u)
    return slack


def get_max_slack_index(n_cores, n_rt_task, n_se_task, rt_alloc, se_alloc, rt_period_list, rt_wcet_list, se_period_list, se_wcet_list):
    """ Returns the core with maximum slack """

    max_slack = 0
    core_index = -1

    for c in range(n_cores):
        slack_c = get_slack_by_core_index(core_index=c,
                                          n_rt_task=n_rt_task,
                                          n_se_task=n_se_task,
                                          rt_alloc=rt_alloc,
                                          se_alloc=se_alloc,
                                          rt_period_list=rt_period_list,
                                          rt_wcet_list=rt_wcet_list,
                                          se_period_list=se_period_list,
                                          se_wcet_list=se_wcet_list)
        # print "core:", c, "slack:", slack_c

        if slack_c > max_slack:
            max_slack = slack_c
            core_index = c

    return core_index


def find_se_task_param_best_fit(taskset_config, rt_alloc):
    """ This routine will find the security tasks paramters for Best Fit
        Best Fit: Pick the core with max-slack """

    x = np.zeros((taskset_config.n_se_task, taskset_config.core))

    rt_taskset = taskset_config.rt_taskset
    se_taskset = taskset_config.se_taskset

    rt_period_list = [task.period for task in rt_taskset]
    rt_wcet_list = [task.wcet for task in rt_taskset]

    se_period_list = copy.deepcopy([task.period for task in se_taskset])  # since this we will update
    se_des_period_list = [task.period_des for task in se_taskset]
    se_max_period_list = [task.period_max for task in se_taskset]
    se_wcet_list = [task.wcet for task in se_taskset]

    eta_list = [None] * taskset_config.n_se_task

    for tindx in range(0, taskset_config.n_se_task):
        opt_eta = -1
        opt_period = -1
        opt_core_index = -1

        core_index = get_max_slack_index(n_cores=taskset_config.core,
                                         n_rt_task=taskset_config.n_rt_task,
                                         n_se_task=taskset_config.n_se_task,
                                         rt_alloc=rt_alloc,
                                         se_alloc=x,
                                         rt_period_list=rt_period_list,
                                         rt_wcet_list=rt_wcet_list,
                                         se_period_list=se_period_list,
                                         se_wcet_list=se_wcet_list)

        # something wrong
        if core_index < 0:
            print "=== Core index is zero in Best-Fit!! ==="
            return None, None, None

        eta, gp_period = solve_gp_by_core_task(core_index=core_index, se_task_index=tindx,
                                               rt_alloc=rt_alloc,
                                               se_alloc=x,
                                               n_rt_task=taskset_config.n_rt_task,
                                               rt_period_list=rt_period_list,
                                               rt_wcet_list=rt_wcet_list,
                                               se_period_list=se_period_list,
                                               se_des_period_list=se_des_period_list,
                                               se_max_period_list=se_max_period_list,
                                               se_wcet_list=se_wcet_list)

        if eta is None or gp_period is None:
            print "Unschedulable For Security Task", tindx, "for core with lowest slack", core_index
            # taskset unschedulable
            return None, None, None

        # we get an allocation
        x[tindx][core_index] = 1  # assign the task to the core
        eta_list[tindx] = eta
        se_period_list[tindx] = gp_period  # update period

    xi = calculate_xi(se_period_list, se_des_period_list, se_max_period_list)
    # print "xi is:", xi

    return eta_list, se_period_list, xi


__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"

import numpy as np
from config import *
import helper_functions as HF
import sys
import task_generator as TGEN
import task_allocator as TALLOC
import expresult as ER


def run_experiment(tc, EXP_NAME):
    """ Run the experiment based on Taskset and Experiment Tag
        Output format is a Class defined in expresult.py """

    if EXP_NAME == PARAMS.EXPERIMENT_NAME_PROP:
        print "###### Finding Security Task Parameter using Proposed Heuristic ######"
    elif EXP_NAME == PARAMS.EXPERIMENT_NAME_REF:
        print "###### Finding Security Task Parameter using SecureCore Aproach ######"
    else:
        raise ValueError("Invalid Experiment Name!")

    xi_list_per_core = []  # save xi for all cores all utilization vals
    xi_std_list_per_core = []  # save STD(xi) for all cores all utilization vals

    etasum_list_per_core = []  # save sum(eta) for all cores all utilization vals
    etasum_std_list_per_core = []  # save STD(sum(eta)) for all cores all utilization vals

    se_sched_list_per_core = []  # save SE schedulablity count for all cores all utilization vals
    rt_sched_list_per_core = []  # save RT schedulablity count for all cores all utilization vals

    for core in PARAMS.CORE_LIST:
        util_list = TGEN.get_util_list_by_core(core)

        xi_per_util_list = [None] * len(util_list)
        xi_std_per_util_list = [None] * len(util_list)
        etasum_per_util_list = [None] * len(util_list)
        etasum_std_per_util_list = [None] * len(util_list)

        se_sched_per_util_list = [None] * len(util_list)
        rt_sched_per_util_list = [None] * len(util_list)

        for uindx, util in enumerate(util_list):

            xi_list = []
            etasum_list = []
            se_sched_count = 0

            rt_sched_count = 0

            for ntc in range(0, PARAMS.N_TASKSET_EACH_CONF):

                print EXP_NAME, "--> Analyzing Core:", core, "System Utilization:", util, "Task index", ntc

                tc_conf = tc[core][util][ntc]
                rt_alloc = TALLOC.get_rt_task_assignemnt(tc_conf, EXP_NAME, worst_fit=True)
                if rt_alloc is None:
                    continue

                rt_sched_count += 1  # count schedulable RT taskset

                # pick which experiment to run
                if EXP_NAME == PARAMS.EXPERIMENT_NAME_PROP:
                    eta_list, se_period_list, xi = TALLOC.allocate_security_task(tc_conf, rt_alloc)
                elif EXP_NAME == PARAMS.EXPERIMENT_NAME_REF:
                    eta_list, se_period_list, xi = TALLOC.find_se_task_param_reference_scheme(tc_conf)

                if eta_list is not None:
                    se_sched_count += 1
                    xi_list.append(xi)
                    etasum_list.append(sum(eta_list))

            if len(xi_list) > 0:
                xi_mean_prop = sum(xi_list) / float(len(xi_list))
                xi_std_prop = np.std(np.array(xi_list))

                etasum_mean_prop = sum(etasum_list) / float(len(etasum_list))
                etasum_std_prop = np.std(np.array(etasum_list))

            else:
                xi_mean_prop = None
                xi_std_prop = None

                etasum_mean_prop = None
                etasum_std_prop = None

            xi_per_util_list[uindx] = xi_mean_prop  # save xi per utilization
            xi_std_per_util_list[uindx] = xi_std_prop  # save xi std per utilization

            se_sched_per_util_list[uindx] = se_sched_count  # save SE schedulability count
            rt_sched_per_util_list[uindx] = rt_sched_count  # save RT schedulability count

            etasum_per_util_list[uindx] = etasum_mean_prop  # save xi per utilization
            etasum_std_per_util_list[uindx] = etasum_std_prop  # save xi std per utilization

        xi_list_per_core.append(xi_per_util_list)
        xi_std_list_per_core.append(xi_std_per_util_list)

        etasum_list_per_core.append(xi_per_util_list)
        etasum_std_list_per_core.append(xi_std_per_util_list)

        se_sched_list_per_core.append(se_sched_per_util_list)
        rt_sched_list_per_core.append(rt_sched_per_util_list)

    output = ER.ExportOutput(etasum_list_per_core, etasum_std_list_per_core,
                             xi_list_per_core, xi_std_list_per_core,
                             rt_sched_list_per_core,
                             se_sched_list_per_core)
    return output


if __name__ == "__main__":

    # decide load from file or generate new taskset
    if PARAMS.GENERATE_NEW_TC:
        # generate taskset and write to file as pickle object
        print "Generating Taskset and Saving to Pickle file..."
        tc = TGEN.generate_all_tasksets()
        HF.write_object_to_file(tc, PARAMS.TASKET_FILENAME)
    else:
        print "Loading Taskset from Pickle file..."
        tc = HF.load_object_from_file(PARAMS.TASKET_FILENAME)

    output_prop = run_experiment(tc, PARAMS.EXPERIMENT_NAME_PROP)

    # saving results to pickle file
    print PARAMS.EXPERIMENT_NAME_PROP, "--> Saving result to file..."
    HF.write_object_to_file(output_prop, PARAMS.EXP_RES_FILENAME_PROP)

    output_ref = run_experiment(tc, PARAMS.EXPERIMENT_NAME_REF)

    # saving results to pickle file
    print PARAMS.EXPERIMENT_NAME_REF, "--> Saving result to file..."
    HF.write_object_to_file(output_ref, PARAMS.EXP_RES_FILENAME_REF)

    print "Script finished!!"


__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"


import task_generator as TGEN
import task_allocator as TALLOC
import helper_functions as HF
import expresult as ER
from config import *


def run_experimet(tc, util_list, EXP_NAME):

    if EXP_NAME == PARAMS.EXPERIMENT_NAME_PROP:
        print "###### Finding Security Task Parameter using Proposed Heuristic ######"
    elif EXP_NAME == PARAMS.EXPERIMENT_NAME_ESEARCH:
        print "###### Finding Security Task Parameter using Exhaustive Search ######"
    else:
        raise ValueError("Invalid Experiment Name!")

    out_xi_list = []
    out_eta_list = []

    for uindx, util in enumerate(util_list):
        tc_conf = tc[util]
        rt_alloc = TALLOC.get_rt_task_assignemnt(tc_conf, PARAMS.EXPERIMENT_NAME_PROP, worst_fit=True)
        if rt_alloc is None:
            continue

        #print rt_alloc
        #print "====="

        # pick which experiment to run
        if EXP_NAME == PARAMS.EXPERIMENT_NAME_PROP:
            eta_list, _, xi = TALLOC.allocate_security_task(tc_conf, rt_alloc)
            eta_max = sum(eta_list)
        elif EXP_NAME == PARAMS.EXPERIMENT_NAME_ESEARCH:
            eta_max, xi = TALLOC.allocate_security_task_esearch(tc_conf, rt_alloc)

        out_xi_list.append((util, xi))
        out_eta_list.append((util, eta_max))

    return out_xi_list, out_eta_list

if __name__ == '__main__':

    n_core = 2

    # decide load from file or generate new taskset
    if PARAMS.GENERATE_NEW_TC_ESEARCH:
        # generate taskset and write to file as pickle object
        print "Generating Taskset and Saving to Pickle file..."
        tc, util_list = TGEN.generate_exsearch_tasksets(n_core)
        HF.write_object_to_file(tc, PARAMS.ESEARCH_TASKET_FILENAME)
        HF.write_object_to_file(util_list, PARAMS.ESEARCH_UTIL_FILENAME)
    else:
        print "Loading Taskset from Pickle file..."
        tc = HF.load_object_from_file(PARAMS.ESEARCH_TASKET_FILENAME)
        util_list = HF.write_object_to_file(PARAMS.ESEARCH_UTIL_FILENAME)

    xi_esearch, eta_esearch = run_experimet(tc, util_list, PARAMS.EXPERIMENT_NAME_ESEARCH)
    xi_prop, eta_prop = run_experimet(tc, util_list, PARAMS.EXPERIMENT_NAME_PROP)


    # print "Ex"
    # print xi_esearch
    #
    # print "prop"
    # print xi_prop

    result = ER.EXSearchResult(util_list=util_list, xi_prop=xi_prop, xi_esearch=xi_esearch,
                               eta_prop=eta_prop, eta_esearch=eta_esearch)

    # saving results to pickle file
    print "--> Saving result to file..."
    HF.write_object_to_file(result, PARAMS.EXP_ESEARCH_FILENAME)

    print "Script Finished!!"


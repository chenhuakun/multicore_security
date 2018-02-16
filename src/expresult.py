__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"

import copy


class ExportOutput:

    """ A Class to format output result """

    def __init__(self, etasum_list_per_core, etasum_std_list_per_core, xi_list_per_core, xi_std_list_per_core,
                 rt_sched_list_per_core, se_sched_list_per_core):

        self.etasum_list_per_core = copy.deepcopy(etasum_list_per_core)
        self.etasum_std_list_per_core = copy.deepcopy(etasum_std_list_per_core)
        self.xi_list_per_core = copy.deepcopy(xi_list_per_core)
        self.xi_std_list_per_core = copy.deepcopy(xi_std_list_per_core)
        self.rt_sched_list_per_core = copy.deepcopy(rt_sched_list_per_core)
        self.se_sched_list_per_core = copy.deepcopy(se_sched_list_per_core)


class CSSimResult:
    """ A Class to format case-study output result """
    def __init__(self, detection_time_both_prop, detection_time_any_prop, detection_time_both_ref, detection_time_any_ref):

        self.detection_time_both_prop = copy.deepcopy(detection_time_both_prop)
        self.detection_time_any_prop = copy.deepcopy(detection_time_any_prop)
        self.detection_time_both_ref = copy.deepcopy(detection_time_both_ref)
        self.detection_time_any_ref = copy.deepcopy(detection_time_any_ref)


class EXSearchResult:
    """ A Class to format exhaustive search output result """
    def __init__(self, util_list, xi_prop, xi_esearch, eta_prop, eta_esearch):

        self.util_list = copy.deepcopy(util_list)
        self.xi_prop = copy.deepcopy(xi_prop)
        self.xi_esearch = copy.deepcopy(xi_esearch)
        self.eta_prop = copy.deepcopy(eta_prop)
        self.eta_esearch = copy.deepcopy(eta_esearch)

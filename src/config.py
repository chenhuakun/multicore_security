__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


""" Helper for creating constant variables
    Found in: https://stackoverflow.com/questions/2682745/how-to-create-a-constant-in-python
"""


class MetaConst(type):
    def __getattr__(cls, key):
        return cls[key]

    def __setattr__(cls, key, value):
        raise TypeError


class Const(object):
    __metaclass__ = MetaConst

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        raise TypeError


class PARAMS(Const):

    """ This class stores all the configuration parameters """

    # Parameters mostly follow the following paper:
    # Global and Partitioned Multiprocessor Fixed Priority Scheduling with Deferred Pre-emption

    CORE_LIST = [2, 4, 8]
    # CORE_LIST = [2, 4]
    N_TASKSET_EACH_CONF = 250  # number of taskset in each configuration
    UTIL_RANGE_MIN = 0.025  # use 0.025m to 0.975m where m is the number of cores in CORE_LIST
    UTIL_RANGE_MAX = 1  # actually 0.975 (as in paper) since np.arange doesn't count endpoint
    UTIL_RANGE_STEP = 0.025

    SE_UTIL_PERCENTAGE = 0.3  # percentage of utilization for security tasks

    N_RT_TASK_MIN = 3  # n * number of cores
    N_RT_TASK_MAX = 10

    N_SE_TASK_MIN = 2  # n * number of cores
    N_SE_TASK_MAX = 5

    RT_PERIOD_MIN = 10
    RT_PERIOD_MAX = 100

    # for schedulability experiment
    SE_PERIOD_MIN = 1000
    SE_PERIOD_MAX = 3000

    # for Exhaustive search experiment
    # SE_PERIOD_MIN = 500
    # SE_PERIOD_MAX = 1000

    SE_PERIOD_MAX_FACTOR = 10

    GENERATE_NEW_TC = False  # indicate whether we will generate new taskset or load from file

    TASKET_FILENAME = 'all_taskset_250.pickle.gzip'
    # TASKET_FILENAME = 'all_taskset.pickle'

    EXP_RES_FILENAME_PROP = 'result_prop_250.pickle.gzip'
    EXP_RES_FILENAME_REF = 'result_ref_250.pickle.gzip'
    EXP_RES_FILENAME_BF = 'result_bf_250.pickle.gzip'

    # EXP_RES_FILENAME_PROP = 'result_prop.pickle.gzip'
    # EXP_RES_FILENAME_REF = 'result_ref.pickle.gzip'

    EXPERIMENT_NAME_PROP = "PROP"
    EXPERIMENT_NAME_REF = "REF"
    EXPERIMENT_NAME_BF = "BF"

    GP_TIMEOUT = 20  # timeout for GP routine (in seconds)

    # for case-study
    CS_SE_PERIOD_MIN = 15000
    CS_SE_PERIOD_MAX = 25000

    SIM_DURATON_FACTOR = 2  # run atleast n jobs of the lowest priority (max period) task
    SIM_DURATION = 1000 * 1000  # in millisecond

    ATTACK_MIN = 50*1000  # a time after attack will launch
    ATTACK_MAX = 150*1000  # upper bound of time when attack will launch


    # ATTACK_MIN = 5  # a time after attack will launch
    # ATTACK_MAX = 10  # upperbound of attack lunch

    N_SIM_SAMPLES = 50  # number of sample we examine to get ECDF
    EXP_CS_FILENAME = 'result_casestudy.pickle.gzip'
    EXP_CS_BF_FILENAME = 'result_casestudy_bf.pickle.gzip'
    # EXP_CS_FILENAME = 'result_casestudy-dumb.pickle.gzip'

    # for exhaustive search experiment
    N_TASKSET_EACH_CONF_ESEARCH = 50

    # number of se task for Exhaustive search Experiment
    N_SE_TASK_ESEARCH_MIN = 1
    N_SE_TASK_ESEARCH_MAX = 3

    N_BASE_UTIL_GRP = 10  # number of base utilization group (as Man-ki)

    ESEARCH_TASKET_FILENAME = 'all_taskset_esearch.pickle.gzip'
    ESEARCH_UTIL_FILENAME = 'all_utillist_esearch.pickle.gzip'

    GENERATE_NEW_TC_ESEARCH = False
    EXPERIMENT_NAME_ESEARCH = "REF"

    EXP_ESEARCH_FILENAME = 'result_esearch.pickle.gzip'


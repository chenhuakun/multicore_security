__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"


import task as TASK
import numpy as np
from config import *

def get_assignemnt_core_index(tindex, n_core, alloc):

    # return the core assignment (-1 if not found) which is not the case for a valid assignment
    core_index = -1
    for i in range(0, n_core):
        if alloc[tindex][i] == 1:
            core_index = i
            break
    return core_index


def simulate_schedule(n_core, tc_config, rt_alloc, se_alloc, sim_duration, attack_time, se_task_attack_detector_list, EXP_NAME):

    if EXP_NAME == PARAMS.EXPERIMENT_NAME_PROP:
        print "Simulating Proposed Scheme..."

    elif EXP_NAME == PARAMS.EXPERIMENT_NAME_REF:
        print "Simulating Reference Scheme..."

    elif EXP_NAME == PARAMS.EXPERIMENT_NAME_BF:
        print "Simulating Best-Fit Scheme..."

    else:
        raise Exception("Invalid Experiment Name")

    alltaskset = []  # a list contain all tasks in the system
    # ready_queue = []

    # print rt_alloc

    se_tname_host = se_task_attack_detector_list[0]
    se_tname_nw = se_task_attack_detector_list[1]


    priority = 1
    for i in range(0, tc_config.n_rt_task):
        cr_indx = get_assignemnt_core_index(i, n_core, rt_alloc)
        alltaskset.append((tc_config.rt_taskset[i], cr_indx, priority))
        priority +=1

    for i in range(0, tc_config.n_se_task):

        if EXP_NAME == PARAMS.EXPERIMENT_NAME_PROP:
            cr_indx = get_assignemnt_core_index(i, n_core, se_alloc)
        if EXP_NAME == PARAMS.EXPERIMENT_NAME_BF:
            cr_indx = get_assignemnt_core_index(i, n_core, se_alloc)
        elif EXP_NAME == PARAMS.EXPERIMENT_NAME_REF:
            cr_indx = n_core - 1  # always assign to highest indexed core

        alltaskset.append((tc_config.se_taskset[i], cr_indx, priority))
        priority += 1

    job_list = np.empty((n_core, 0)).tolist() # for each core


    # Create job instances
    for current_time in range(0, sim_duration):
        for taskinfo in alltaskset:
            task = taskinfo[0]  # this is the taskset
            cr_indx = taskinfo[1]
            priority = taskinfo[2]

            if current_time % task.period == 0:

                # print "task", task.name, "appending..."
                arrival_time = current_time
                absolute_deadline = arrival_time + task.period
                job_list[cr_indx].append(TASK.Job(arrival_time=arrival_time, wcet=task.wcet,
                                         priority=priority,
                                         core_index=cr_indx,
                                         absolute_deadline=absolute_deadline, name=task.name))


    #raise Exception("ok")
    # print("Job list:", len(job_list))


    queue = np.empty((n_core, 0)).tolist() # for each core
    # schedule = []  # output schedule

    detect_flag_host = False
    detect_flag_nw = False

    detection_time_host = -1
    detection_time_nw = -1
    detection_time_both = -1
    detection_time_any = -1


    for time in range(0, sim_duration):

        # print "Current time is", time

        # insert new tasks into the queue

        for core in range(0, n_core):

            for indx, jobs in enumerate(job_list[core]):
                if time == jobs.arrival_time:
                    # print "Job", jobs.name, "appending to queue..."
                    # print "wcet", jobs.wcet
                    queue[core].append(indx)  # save the job index

            # check attack logic
            # raise Exception("ok")


            # select next job to be scheduled

            min_prio = 10000  # initialize to a large value
            current_job_index = -1
            for indx in queue[core]:
                job = job_list[core][indx]

                if job.priority < min_prio:
                    min_prio = job.priority
                    current_job_index = indx

            if current_job_index >= 0:
                # print("current job index:", current_job_index)
                job_list[core][current_job_index].usage += 1  # update execution time

                # dequeue completed job
                if job_list[core][current_job_index].usage == job_list[core][current_job_index].wcet:
                    # print job_list[core][current_job_index].name ,"finishes at time", time
                    queue[core].remove(current_job_index)  # remove completed job

                    if (time > attack_time and job_list[core][current_job_index].arrival_time >= attack_time) and job_list[core][current_job_index].name == se_tname_host and (not detect_flag_host):
                        detect_flag_host = True
                        detection_time_host = time - attack_time
                        print EXP_NAME,  "--> Host attack detected at time", time
                    if (time > attack_time and job_list[core][current_job_index].arrival_time >= attack_time) and job_list[core][current_job_index].name == se_tname_nw and (not detect_flag_nw):
                        detect_flag_nw = True
                        detection_time_nw = time - attack_time
                        print EXP_NAME, "--> NW attack detected at time", time


            # capture schedule trace
            # if current_job_index >= 0:
            #     schedule.append((core, time + 1, job_list[core][current_job_index].name))
            # else:
            #     schedule.append((core, time + 1, "Idle"))

        if detection_time_host > 0 and detection_time_nw > 0:
            detection_time_both = max(detection_time_host, detection_time_nw)
            detection_time_any = min(detection_time_host, detection_time_nw)
            break


    # print "host", detection_time_host
    # print "nw", detection_time_nw
    # print "both", detection_time
    #print(schedule)
    # return schedule
    return detection_time_both, detection_time_any
#! /bin/bash
# cluster relabeling according to the group reference image

WD=$1
shift
SUB_LIST=$1
shift
MAX_CL_NUM=$1



python3 -u "$(dirname "$0")/cluster_relabel.py" --wd ${WD} --sub_list ${SUB_LIST} --max_cl_num ${MAX_CL_NUM}
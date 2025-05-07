#! /bin/bash
# transform parcellated ROI from DTI space to MNI space

WD=$1
shift
SUB_LIST=$1
shift
MAX_CL_NUM=$1
shift
TEMPLATE=$1
shift
POOLSIZE=$1


python3 -u "$(dirname "$0")/roi_to_template.py" --wd ${WD} --sub_list ${SUB_LIST} --max_cl_num ${MAX_CL_NUM} --template ${TEMPLATE} --poolsize ${POOLSIZE} 

#! /bin/bash
# ROI parcellation using spectral clustering, to generate 2 to max cluster number subregion

WD=$1
shift
SUB_LIST=$1
shift
MAX_CL_NUM=$1
shift
NIFTI=$1
shift
METHOD=$1
shift 
PROB_CLUSTERING=$1


python3 -u "$(dirname "$0")/roi_parcellation.py" --wd ${WD} --sub_list ${SUB_LIST} --max_cl_num ${MAX_CL_NUM} --method ${METHOD}

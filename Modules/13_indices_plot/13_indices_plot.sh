#! /bin/bash
# plot indices

WD=$1
shift
SUB_LIST=$1
shift
MAX_CL_NUM=$1
shift
VOX_SIZE=$1
shift
NIFTI=$1
shift
split_half=$1
shift
tpd=$1


${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${pipeline}/export_fig');addpath('${NIFTI}');indices_plot('${WD}','${SUB_LIST}',${VOX_SIZE},${MAX_CL_NUM},${split_half},${tpd});exit"
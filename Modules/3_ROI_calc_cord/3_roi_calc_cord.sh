#! /bin/bash
# calculate ROI coordinates in DTI space

PIPELINE=$1
shift
WD=$1
shift
SUB_LIST=$1
shift
POOLSIZE=$1
shift
NIFTI=$1

${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${NIFTI}');ROI_calc_coord('${WD}','${SUB_LIST}','${POOLSIZE}', 'ROI_masks');exit"
${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${NIFTI}');ROI_calc_coord('${WD}','${SUB_LIST}','${POOLSIZE}', 'Target_masks');exit"
${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${NIFTI}');ROI_calc_coord('${WD}','${SUB_LIST}','${POOLSIZE}', 'Exclusion_masks');exit"
${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${NIFTI}');ROI_calc_coord('${WD}','${SUB_LIST}','${POOLSIZE}', 'Stop_masks');exit"
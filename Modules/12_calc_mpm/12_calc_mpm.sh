#! /bin/bash
# generate maximum probability map for ROI and probabilistic maps for each subregion

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
MPM_THRES=$1
shift
VOX_SIZE=$1

for roi in "$WD/ROI_masks/"*; do
	filename=$(basename "$roi")
	roi_base="${filename%.nii*}"
    ${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${NIFTI}');calc_mpm_group_xmm('${WD}','${roi_base}', '${SUB_LIST}',${MAX_CL_NUM},'${METHOD}',${MPM_THRES},${VOX_SIZE});exit"
	wait
done
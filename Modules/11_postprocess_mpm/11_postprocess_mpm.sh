#! /bin/bash
# smooth the mpm image by taking a majority vote of the labels in the neighborhood of each voxel

WD=$1
shift
SUB_LIST=$1
shift
MAX_CL_NUM=$1
shift
NIFTI=$1
shift
MPM_THRES=$1
shift
VOX_SIZE=$1

for roi in "$WD/ROI_masks/"*; do
	filename=$(basename "$roi")
	roi_base="${filename%.nii*}"
    ${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${NIFTI}');postprocess_mpm_group_xmm('${WD}','${roi_base}','${SUB_LIST}',${MAX_CL_NUM},${MPM_THRES},${VOX_SIZE});exit"
done
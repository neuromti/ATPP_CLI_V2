#! /bin/bash
# calculate connectivity matrix between each voxel in ROI and the remain voxels of whole brain 

PIPELINE=$1
shift
WD=$1
shift
SUB_LIST=$1
shift
NIFTI=$1


${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${NIFTI}');ROI_calc_matrix('${WD}','${SUB_LIST}');exit"

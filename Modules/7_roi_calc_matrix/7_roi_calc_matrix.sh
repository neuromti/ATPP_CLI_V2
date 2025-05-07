#! /bin/bash
# calculate connectivity matrix between each voxel in ROI and the remain voxels of whole brain 

WD=$1
shift
SUB_LIST=$1
shift 
POOLSIZE=$1


python3 -u "$(dirname "$0")/roi_calc_matrix.py" "$WD" "$SUB_LIST" "$POOLSIZE"
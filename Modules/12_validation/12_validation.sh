#! /bin/bash
# produce various validity indices

WD=$1
shift
SUB=$1
shift
MAX_CL_NUM=$1
shift
NIFTI=$1
shift
METHOD=$1
shift
VOX_SIZE=$1
shift
SPM=$1
shift
N_ITER=$1
shift
GROUP_THRES=$1
shift
MPM_THRES=$1
shift
split_half=$1
shift
tpd=$1

echo "Working Directory: ${WD}"
echo "Subject: ${SUB}"
echo "Max Cluster Number: ${MAX_CL_NUM}"
echo "NIFTI Directory: ${NIFTI}"
echo "Method: ${METHOD}"
echo "Voxel Size: ${VOX_SIZE}"
echo "SPM Directory: ${SPM}"
echo "Number of Iterations: ${N_ITER}"
echo "Group Threshold: ${GROUP_THRES}"
echo "MPM Threshold: ${MPM_THRES}"
echo "Split Half: ${split_half}"
echo "TPD: ${tpd}"


${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${NIFTI}');addpath('${SPM}');validation('${WD}','${SUB}','${METHOD}',${VOX_SIZE},${MAX_CL_NUM},${N_ITER},${GROUP_THRES},${MPM_THRES},${split_half},${tpd});exit" 


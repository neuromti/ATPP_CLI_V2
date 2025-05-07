#! /bin/bash
# T1 registration, from T1 space to DTI space, using spm batch

PIPELINE=$1
shift
WD=$1
shift
SUB_LIST=$1
shift
POOLSIZE=$1
shift
SPM=$1
shift
NIFTI=$1
shift
TEMPLATE=$1



${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${SPM}');addpath('${NIFTI}');t1_to_b0('${WD}','${SUB_LIST}',${POOLSIZE},'${TEMPLATE}');exit"

for sub in `cat ${SUB_LIST}`
do
	mv ${WD}/${sub}/rT1_${sub}.nii ${WD}/${sub}/T1_in_diffusion_space_${sub}.nii
done
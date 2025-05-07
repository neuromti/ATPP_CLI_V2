#! /bin/bash
# ROI registration, from MNI space to DTI space, using spm batch

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

${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${SPM}');addpath('${NIFTI}');ROI_registration_spm('${WD}','${SUB_LIST}',${POOLSIZE},'${SPM}');exit"

for sub in `cat ${SUB_LIST}`
do
	mv ${WD}/${sub}/y_T1_in_diffusion_space_${sub}.nii ${WD}/${sub}/DTI_to_MNI_deformation_field_${sub}.nii
	for roi in $WD/${sub}/ROI_masks/*; do
		gzip $roi
	done
done

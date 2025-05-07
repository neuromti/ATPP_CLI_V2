#! /bin/bash
# transform parcellated ROI from DTI space to MNI space

PIPELINE=$1
shift
WD=$1
shift
SUB_LIST=$1
shift
MAX_CL_NUM=$1
shift
SPM=$1
shift
VOX_SIZE=$1
shift
METHOD=$1


${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${SPM}');ROI_to_Template_spm_xmm('${WD}','${SUB_LIST}',${MAX_CL_NUM},${VOX_SIZE},'${METHOD}');exit"


for sub in `cat ${SUB_LIST}`;
do
	for roi in "$WD/${sub}/ROI_masks/"*; do
		# Extract the ROI basename
        filename=$(basename -- "$roi")
        roi_base="${filename%.nii*}"
		mkdir -p ${WD}/${sub}/${roi_base}_${METHOD}/${VOX_SIZE}mm
		for num in $(seq 2 ${MAX_CL_NUM})
		do
			mv ${WD}/${sub}/${roi_base}_${METHOD}/w${roi_base}${num}.nii ${WD}/${sub}/${roi_base}_${METHOD}/${VOX_SIZE}mm/${VOX_SIZE}mm_${roi_base}${num}_Template.nii
			gzip ${WD}/${sub}/${roi_base}_${METHOD}/${VOX_SIZE}mm/${VOX_SIZE}mm_${roi_base}${num}_Template.nii
		done
	done
done
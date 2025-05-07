#! /bin/bash
# Produce various validation indices

WD=$1
shift
SUB=$1
shift
MAX_CL_NUM=$1
shift
METHOD=$1
shift
VOX_SIZE=$1
shift
N_ITER=$1
shift
GROUP_THRES=$1
shift
split_half=$1
shift
MATCH_HEMI=$1


# Calculate the explained variance per principal component and heuristics for the number of clusters to retain
for roi in "$WD/ROI_masks/"*; do
	filename=$(basename "$roi")
	roi_base="${filename%.nii*}"
	python3 -u Modules/12_validation/PCA_validation/ExplainedVarPerComponent.py ${WD} ${SUB} ${roi_base}
    python3 -u Modules/12_validation/PCA_validation/cluster_selection_heuristics.py ${WD} ${SUB} ${roi_base}
	wait
done

python3 -u Modules/12_validation/stability_between_hemispheres/between_hemisphere_validation.py ${WD} ${SUB} ${MAX_CL_NUM}

python3 Modules/12_validation/split_half_validation/between_subject_split_half.py ${WD} ${SUB} ${MAX_CL_NUM} ${N_ITER}


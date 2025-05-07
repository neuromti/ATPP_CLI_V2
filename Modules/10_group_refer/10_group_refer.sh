#! /bin/bash
# calculate symmetric group reference images to prepare for the relabel step

WD=$1
shift
SUB_LIST=$1
shift
MAX_CL_NUM=$1
shift
GROUP_THRES=$1
shift
MATCH_HEMI=$1

for roi in "$WD/ROI_masks/"*; do
	filename=$(basename "$roi")
	roi_base="${filename%.nii*}"
	python3 -u ${PIPELINE}/Modules/10_group_refer/consensus_clustering.py ${WD} ${roi_base} ${SUB_LIST} ${MAX_CL_NUM} ${GROUP_THRES}
	wait
done

# Match the hemisphreres
if [ "$MATCH_HEMI" = 1 ]; then
	python3 ${PIPELINE}/Modules/10_group_refer/match_hemispheres.py --wd ${WD} --sub_list ${SUB_LIST} --max_cl_num ${MAX_CL_NUM}
fi
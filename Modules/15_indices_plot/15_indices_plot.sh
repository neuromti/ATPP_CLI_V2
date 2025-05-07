#! /bin/bash
# plot indices

WD=$1
shift
SUB_LIST=$1
shift
MAX_CL_NUM=$1
shift
VOX_SIZE=$1
shift
NIFTI=$1
shift
split_half=$1
shift
tpd=$1


# Make split half and PCA analysis plots
for roi in "$WD/ROI_masks/"*; do
	filename=$(basename "$roi")
	roi_base="${filename%.nii*}"
	python3 Modules/13_indices_plot/make_split_half_plots.py ${WD} ${SUB_LIST} ${roi_base}
	python3 Modules/13_indices_plot/make_pca_analysis_plots.py ${WD} ${SUB_LIST} ${roi_base}
	wait
done


# Make hemispheric stability plots
python3 Modules/13_indices_plot/make_hemispheric_stability_plots.py ${WD} ${SUB_LIST} ${MAX_CL_NUM}

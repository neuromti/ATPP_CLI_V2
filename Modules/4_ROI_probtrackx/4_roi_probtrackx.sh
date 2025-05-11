#! /bin/bash
# generate probabilistic tractography for each voxel in ROI

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --wd) WD="$2"; shift ;;
    --data_dir) DATA_DIR="$2"; shift ;;
    --sub_list) SUB_LIST="$2"; shift ;;
    --n_samples) N_SAMPLES="$2"; shift ;;
    --dis_cor) DIS_COR="$2"; shift ;;
    --len_step) LEN_STEP="$2"; shift ;;
    --n_steps) N_STEPS="$2"; shift ;;
    --cur_thres) CUR_THRES="$2"; shift ;;
    --sampvox) SAMPVOX="$2"; shift ;;
    --probtrackx_gpu) PROBTRACKX_GPU="$2"; shift ;;
    --stop_masks) STOP_MASKS="$2"; shift ;;
    --waypoint_masks) WAYPOINT_MASKS="$2"; shift ;;
    --exclusion_masks) EXCLUSION_MASKS="$2"; shift ;;
    --target_masks) TARGET_MASKS="$2"; shift ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
  shift
done


echo "Working Directory: ${WD}"
echo "Data Directory: ${DATA_DIR}"
echo "Subject List: ${SUB_LIST}"
echo "Number of Samples: ${N_SAMPLES}"
echo "Distance Correction: ${DIS_COR}"
echo "Step Length: ${LEN_STEP}"
echo "Number of Steps: ${N_STEPS}"
echo "Curvature Threshold: ${CUR_THRES}"
echo "Sample Voxel: ${SAMPVOX}"
echo "Probtrackx GPU Flag: ${PROBTRACKX_GPU}"
echo "Stop Masks: ${STOP_MASKS}"
echo "Waypoint Masks: ${WAYPOINT_MASKS}"
echo "Exclusion Masks: ${EXCLUSION_MASKS}"
echo "Target Masks: ${TARGET_MASKS}"



# Determine probtrackx command based on PROBTRACKX_GPU flag
if [ "${PROBTRACKX_GPU}" = "1" ]; then
    TRACK_COMMAND=$FSLDIR/bin/probtrackx2_gpu10.2
else
    TRACK_COMMAND=$FSLDIR/bin/probtrackx2
fi

# Function to check and add mask
check_and_add_mask() {
    echo "Checking and adding mask..."
    local mask_type=$1
    local mask_dir=$2
    local mask_suffix=$3
    local mask_option=$4
    local original_mask_dir=$5

    if [ -n "${original_mask_dir}" ] && ([ -f "${mask_dir}/${roi}${mask_suffix}.nii" ] || [ -f "${mask_dir}/${roi}${mask_suffix}.nii.gz" ]); then
        
        if [ -f "${mask_dir}/${roi}${mask_suffix}.nii" ]; then
            mask_options+="${mask_option}=${mask_dir}/${roi}${mask_suffix}.nii "
        else
            mask_options+="${mask_option}=${mask_dir}/${roi}${mask_suffix}.nii.gz "
        fi
    else
        echo "Warning: ${mask_type} mask ${mask_dir}/${roi}${mask_suffix}.nii not found."
        if [ "$mask_type" = "TARGET_MASKS" ]; then
            mask_options+="--target2=${WD}/${sub}/T1_${sub}.nii "
        fi
    fi
}

# Function to run probtrackx for left or right ROI
run_probtrackx() {
    local roi=$1
    local sub=$2

    # Build the masking options for probtrackx
    mask_options=""
    check_and_add_mask "STOP_MASKS" "${WD}/${sub}/Stop_masks" "_stop" "--stop" $STOP_MASKS
    check_and_add_mask "WAYPOINT_MASKS" "${WD}/${sub}/Waypoint_masks" "_waypoint" "--waypoints" $WAYPOINT_MASKS
    check_and_add_mask "EXCLUSION_MASKS" "${WD}/${sub}/Exclusion_masks" "_exclusion" "--avoid" $EXCLUSION_MASKS
    check_and_add_mask "TARGET_MASKS" "${WD}/${sub}/Target_masks" "_targets" "--target2" $TARGET_MASKS


    echo "${roi} probtrackx is running...!"
    $TRACK_COMMAND -m "${DATA_DIR}/${sub}/Diffusion.bedpostX/nodif_brain_mask" \
                   -o "${roi}" \
                   -x "${WD}/${sub}/ROI_masks/${roi}.nii.gz" \
                   -l "${DIS_COR}" \
                   -c "${CUR_THRES}" \
                   -S "${N_STEPS}" \
                   --steplength="${LEN_STEP}" \
                   -P "${N_SAMPLES}" \
                   --forcedir --opd --ompl --sampvox=$SAMPVOX \
                   --onewaycondition --fibthresh=0.01 \
                   -s "${DATA_DIR}/${sub}/Diffusion.bedpostX/merged" \
                   --dir="${WD}/${sub}/${roi}_probtrackx" \
                   --omatrix2 \
                   $mask_options
}

# Loop through subjects in SUB_LIST
for sub in `cat ${SUB_LIST}`
do
    for roi in "$WD/${sub}/ROI_masks/"*; do
        # Extract the ROI basename
        filename=$(basename -- "$roi")
        roi_base="${filename%.nii*}"
        # Run Probtrackx with the users specified parameters
		run_probtrackx "$roi_base" "${sub}" 
	done
done

echo "====== Finally Probtrackx All Done!! ======"
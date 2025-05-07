#! /bin/bash
# generate working directory for ATPP
#
# Directory structure:
#	  Working_dir
#     |-- sub1
#     |   |-- T1_sub1.nii
#     |   `-- b0_sub1.nii
#     |-- ...
#     |-- subN
#     |   |-- T1_subN.nii
#     |   `-- b0_subN.nii
#     |-- ROI
#     |   |-- ROI.nii
#     |   `-- ...
#     `-- log 
#
# !! Please modify the following codes to organize these files according to the above structure

# Parse named arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --wd) WD="$2"; shift ;;
    --data_dir) DATA_DIR="$2"; shift ;;
    --sub_list) SUB_LIST="$2"; shift ;;
    --roi_dir) ROI_DIR="$2"; shift ;;
    --target_masks) TARGET_DIR="$2"; shift ;;
    --waypoint_masks) WAYPOINT_MASKS="$2"; shift ;;
    --exclusion_masks) EXCLUSION_MASKS="$2"; shift ;;
    --stop_masks) STOP_MASKS="$2"; shift ;;
    --template_space) TEMPLATE_SPACE="$2"; shift ;;
    *) 
      echo "Unknown argument: $1" 
      exit 1
      ;;
  esac
  shift
done

# Echo all arguments
echo "Working Directory: ${WD}"
echo "Data Directory: ${DATA_DIR}"
echo "Subject List: ${SUB_LIST}"
echo "ROI Directory: ${ROI_DIR}"
echo "Target Directory: ${TARGET_DIR}"
echo "Waypoint Masks: ${WAYPOINT_MASKS}"
echo "Exclusion Masks: ${EXCLUSION_MASKS}"
echo "Stop Masks: ${STOP_MASKS}"
echo "Template Space: ${TEMPLATE_SPACE}"

# Function to check the masks ROI, Target, Waypoint etc to have the same affine as the template space
SCRIPT_DIR="$(dirname "$0")"
CHECK_MASKS_SCRIPT="${SCRIPT_DIR}/check_masks.py"
check_masks() {
  local img=$1
  echo "Running check_masks.py on $img"
  python -u "$CHECK_MASKS_SCRIPT" "$img" "$TEMPLATE" 
}

copyfiles() {
  local file_dir=$1
  local indentifier=$2

  # generate the directory
  mkdir -p "${WD}/$indentifier"


  if [ -d "${file_dir}" ]; then
    for file in "${file_dir}"/*; do
      echo "Found $(basename "$file") in ${file_dir}"

      # Check if the file is provided in Nifti Format
      if [[ "${file: -4}" != ".nii" && "${file: -7}" != ".nii.gz" ]]; then
      echo "ERROR: $indentifier don't exist or aren't in the right format (<ROI>.nii.gz or <ROI>.nii)"
      exit 1
      fi

      cp -vrt "${WD}/$indentifier" "$file"
      echo "Checking affine of $(basename "$file")"
      check_masks "${WD}/$indentifier/$(basename "$file")"
    done
  else
    echo "No $indentifier directory given: ${file_dir}"
  fi
}

# copy ROI masks from ROI_DIR and check their affine
copyfiles "${ROI_DIR}" "ROI_masks"

# copy Target masks from ROI_DIR and check their affine
copyfiles "${TARGET_DIR}" "Target_masks"

# copy Waypoint masks from WAYPOINT_MASKS and check their affine
copyfiles "${WAYPOINT_MASKS}" "Waypoint_masks"

# copy Exclusion masks from EXCLUSION_MASKS and check their affine
copyfiles "${EXCLUSION_MASKS}" "Exclusion_masks"

# copy stop masks from STOP_MASKS and check their affine
copyfiles "${STOP_MASKS}" "Stop_masks"

for sub in $(cat "${SUB_LIST}"); do
  mkdir -p "${WD}/${sub}"

  ##### Handle b0 file #####
  b0_file=$(ls "${DATA_DIR}/${sub}/b0_brain.nii"* 2>/dev/null | head -n 1)
  if [ -z "${b0_file}" ]; then
    echo "b0 file for subject ${sub} does not exist."
    echo "Make sure that the T1 is already in diffusion space. Then Module 1 can be skipped."
  else
    b0_ext="${b0_file##*.nii}"  # will be "" or ".gz"
    cp "${b0_file}" "${WD}/${sub}/b0_${sub}.nii${b0_ext}"
  fi

  ##### Handle T1 file #####
  t1_file=$(ls "${DATA_DIR}/${sub}/T1_brain.nii"* 2>/dev/null | head -n 1)
  if [ -z "${t1_file}" ]; then
    echo "ERROR: T1 file does not exist or isn't in the right format for subject ${sub}"
  else
    t1_ext="${t1_file##*.nii}"  # will be "" or ".gz"
    cp "${t1_file}" "${WD}/${sub}/T1_${sub}.nii${t1_ext}"
  fi
done

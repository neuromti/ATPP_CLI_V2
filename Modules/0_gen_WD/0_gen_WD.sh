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



# Function to check and unzip if the file is zipped
unzip() {
  local file=$1
  echo $file
  # If the file is zipped, unzip it
  if [[ "${file: -7}" == ".nii.gz" ]]; then
    echo "Unzipping ${file}"
    gunzip "${file}"
  elif [[ "${file: -4}" == ".nii" ]]; then
    :
  else 
    echo "ERROR: ROI files don't exist or aren't in the right format (<ROI>.nii.gz or <ROI>.nii)"
    exit 1
  fi
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
      echo "${WD}/$indentifier/$(basename "$file")"
      unzip "${WD}/$indentifier/$(basename "$file")"
    done
  else
    echo "No $indentifier directory given: ${file_dir}"
  fi
}

# copy ROI masks from ROI_DIR and unzip them
copyfiles "${ROI_DIR}" "ROI_masks"

# copy Target masks from ROI_DIR and unzip them
copyfiles "${TARGET_DIR}" "Target_masks"

# copy Waypoint masks from WAYPOINT_MASKS and unzip them
copyfiles "${WAYPOINT_MASKS}" "Waypoint_masks"

# copy Exclusion masks from EXCLUSION_MASKS and unzip them
copyfiles "${EXCLUSION_MASKS}" "Exclusion_masks"

# copy stop masks from STOP_MASKS and unzip them
copyfiles "${STOP_MASKS}" "Stop_masks"

# copy T1 and b0 files from DATA_DIR for each subject
for sub in `cat "${SUB_LIST}"`; do
  # Make a folder for each subject
  mkdir -p "${WD}/${sub}"
  
  # Check if the b0 file is provided in Nifti Format
  if [ ! -f "${DATA_DIR}/${sub}/b0_brain."* ]; then
  echo "b0 file for subject ${sub} does not exist for subject ${sub}"
  echo "Make sure that the T1 is already in diffusion space. Then Module 1 can be skipped."
  else
  cp "${DATA_DIR}/${sub}/b0_brain."* "${WD}/${sub}/"
  unzip "${WD}/${sub}/b0_brain."*
  mv -v "${WD}/${sub}/b0_brain.nii" "${WD}/${sub}/b0_${sub}.nii"
  fi

  # Check if the T1 file is provided in Nifti Format
  if [ ! -f "${DATA_DIR}/${sub}/T1_brain."* ]; then
  echo "ERROR: T1 files don't exist or isn't in the right format (<T1>.nii.gz or <T1>.nii) for subject ${sub}"
  else
  cp "${DATA_DIR}/${sub}/T1_brain."* "${WD}/${sub}/"
  unzip "${WD}/${sub}/T1_brain."*
  mv -v "${WD}/${sub}/T1_brain.nii" "${WD}/${sub}/T1_${sub}.nii"
  fi
done

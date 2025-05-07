#! /bin/bash
# Moves Probtrackx Paths into Template Space to intersubject comparison

WD=$1
shift
SUB_LIST=$1
shift
NIFTI=$1
shift
VOX_SIZE=$1
shift
NORMALIZE=$1

echo "Working Directory: ${WD}"
echo "Subject List: ${SUB_LIST}"
echo "NIFTI Directory: ${NIFTI}"
echo "Voxel Size: ${VOX_SIZE}"
echo "Normalize: ${NORMALIZE}"

${COMMAND_MATLAB} -nodisplay -nosplash -r "addpath('$(dirname "$0")');addpath('${NIFTI}');Probtrackx_to_template('${WD}','${SUB_LIST}','${VOX_SIZE}','${NORMALIZE}');exit"

#! /bin/bash
# calculate ROI coordinates in DTI space

WD=$1
shift
SUB_LIST=$1
shift
POOLSIZE=$1

python3 -u "$(dirname "$0")/roi_calc_coord.py" "$WD" "$SUB_LIST" "ROI_masks"
python3 -u "$(dirname "$0")/roi_calc_coord.py" "$WD" "$SUB_LIST" "Target_masks"
python3 -u "$(dirname "$0")/roi_calc_coord.py" "$WD" "$SUB_LIST" "Exclusion_masks"
python3 -u "$(dirname "$0")/roi_calc_coord.py" "$WD" "$SUB_LIST" "Stop_masks"
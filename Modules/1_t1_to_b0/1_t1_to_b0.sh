#! /bin/bash
# T1 registration, from T1 space to DTI space, using spm batch

# Parse input arguments
WD=$1
shift
SUB_LIST=$1
shift
POOLSIZE=$1

SCRIPT_DIR="$(dirname "$0")"
PYTHON_SCRIPT="${SCRIPT_DIR}/t1_to_b0.py"

# Run the ANTsPy registration
python3 -u "${PYTHON_SCRIPT}" --wd "${WD}"  --sub_list "${SUB_LIST}"
#!/bin/bash
# Non-linear registration of DTI Space to template space using ANTs

WD=$1
shift
SUB_LIST=$1
shift
POOLSIZE=$1
shift
TEMPLATE=$1
shift
OVERWRITE_REGISTRATION=$1
shift

#===============================================================================
SCRIPT_DIR="$(dirname "$0")"
PY_SCRIPT="${SCRIPT_DIR}/t1_to_template_registration.py"
python -u "$PY_SCRIPT" "$WD" "$SUB_LIST" "$TEMPLATE" "$POOLSIZE" "$OVERWRITE_REGISTRATION"

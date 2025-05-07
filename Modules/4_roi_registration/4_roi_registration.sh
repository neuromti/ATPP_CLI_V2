#!/bin/bash
# Transfering ROIs from MNI space to DTI space, using ANTs

WD=$1
shift
SUB_LIST=$1
shift
POOLSIZE=$1
shift

SCRIPT_DIR="$(dirname "$0")"
PY_SCRIPT="${SCRIPT_DIR}/roi_registration.py"
python -u "$PY_SCRIPT" "$WD" "$SUB_LIST" "$POOLSIZE"

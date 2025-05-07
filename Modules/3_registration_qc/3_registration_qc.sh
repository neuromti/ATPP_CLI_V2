#!/bin/bash
# Perform Quality Check on ANT Non-linear Registrations

WD=$1
shift
SUB_LIST=$1
shift
POOLSIZE=$1
shift
TEMPLATE=$1
shift

#===============================================================================
SCRIPT_DIR="$(dirname "$0")"
QC_PY_SCRIPT="${SCRIPT_DIR}/registration_qc.py"
python -u "$QC_PY_SCRIPT" "$WD" "$SUB_LIST" "$TEMPLATE" "$POOLSIZE"
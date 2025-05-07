# Execution file

# bliblablub


roi_config=$1
#==============================================================================
# Global configuration file
# Before running the pipeline, you NEED to modify parameters in the file.
#==============================================================================
set -o allexport
if [ -f "./system_config.sh" ] && [ -f "./${roi_config}" ]; then
    source "./${roi_config}"
    source "./system_config.sh"
else
    echo "ERROR: One or both configuration files are missing!"
    exit 1
fi

#==============================================================================
#----------------------------START OF SCRIPT-----------------------------------
#------------NO EDITING BELOW UNLESS YOU KNOW WHAT YOU ARE DOING---------------
#==============================================================================


# show header info 
HEADER="${PIPELINE}/ATPP_V2.txt"

if [ -f "${HEADER}" ]; then
	cat "${HEADER}"
fi

echo "Data dir: ${DATA_DIR}"
echo "Subject list: ${SUB_LIST}"
echo "Working directory: ${WD}"
echo "Maximum number of clusters: ${MAX_CL_NUM}"

# 2. make a proper bash script 
mkdir -p ${WD}/log
LOG_DIR="${WD}/log"
LOG="${LOG_DIR}/ATPP_log_$(date +%m-%d_%H-%M-%S).txt"
# 3. Run the pipeline
echo "================ ATPP is running ================="
echo "log: ${LOG_DIR}/ATPP_log_$(date +%m-%d_%H-%M-%S).txt" 
bash "${PIPELINE}/pipeline.sh" "${roi_config}"
#================================ END =======================================
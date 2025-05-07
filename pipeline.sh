#! /bin/bash

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
    echo "moin"
    echo "ERROR: One or both configuration files are missing!"
    exit 1
fi

echo ""

LOG_DIR="${WD}/log"
LOG="${LOG_DIR}/ATPP_log_$(date +%m-%d_%H-%M-%S).txt"

#===============================================================================
#--------------------------------Pipeline---------------------------------------
#------------NO EDITING BELOW UNLESS YOU KNOW WHAT YOU ARE DOING----------------
#===============================================================================

# in case of errors 
SWITCH=(${SWITCH[@]/#/_}) #add a _ before step
SWITCH=(${SWITCH[@]/%/_}) #add a _ after step

# 0) generate the working directory and copy the necessary files
if [[ ${SWITCH[@]/_0_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =============== 0_gen_WD start! ===============" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/0_gen_WD/0_gen_WD.sh" \
  --wd "${WD}" \
  --data_dir "${DATA_DIR}" \
  --sub_list "${SUB_LIST}" \
  --roi_dir "${ROI_DIR}" \
  --target_masks "${TARGET_MASKS}" \
  --waypoint_masks "${WAYPOINT_MASKS}" \
  --exclusion_masks "${EXCLUSION_MASKS}" \
  --stop_masks "${STOP_MASKS}" \
  --template_space "${TEMPLATE}" 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =============== 0_gen_WD done!  ===============" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 1) T1_to_MNI registration
if [[ ${SWITCH[@]/_1_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =============== 1_t1_to_b0 start! =============" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/1_t1_to_b0/1_t1_to_b0.sh" "${WD}" ${SUB_LIST} ${POOLSIZE} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =============== 1_t1_to_b0 done!  =============" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 2) T1 to template registration
if [[ ${SWITCH[@]/_2_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =============== 2_t1_to_template_registration start! =============" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/2_t1_to_template_registration/2_t1_to_template_registration.sh" "${WD}" ${SUB_LIST} ${POOLSIZE} ${TEMPLATE} ${OVERWRITE_REGISTRATION} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =============== 2_t1_to_template_registration done!  =============" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 3) registration Quality check
if [[ ${SWITCH[@]/_3_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  ========= 3_registration_qc start! =========" |tee -a "${WD}/log/progress_check.txt"
T=$(date +%s)
bash "${PIPELINE}/Modules/3_registration_qc/3_registration_qc.sh" "${WD}" ${SUB_LIST} ${POOLSIZE} ${TEMPLATE} 2>&1 | tee -a "${LOG}"
T=$(($(date +%s)-T))
echo "$(date +%T)  ========= 3_registration_qc done! =========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi


# 4) ROI registration, from MNI space to DTI space 
if [[ ${SWITCH[@]/_4_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  ========= 4_roi_registration start! =========" |tee -a "${WD}/log/progress_check.txt"
T=$(date +%s)
bash "${PIPELINE}/Modules/4_roi_registration/4_roi_registration.sh" "${WD}" ${SUB_LIST} ${POOLSIZE} 2>&1 | tee -a "${LOG}"
T=$(($(date +%s)-T))
echo "$(date +%T)  ========= 4_roi_registration done! =========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 5) calculate ROI coordinates in DTI space 
if [[ ${SWITCH[@]/_5_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 5_roi_calc_cord start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/5_roi_calc_cord/5_roi_calc_cord.sh" "${WD}" ${SUB_LIST} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 5_roi_calc_cord done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi


# 6) generate probabilistic tractography for each voxel in ROI 
if [[ ${SWITCH[@]/_6_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 6_roi_probtrackx start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/6_roi_probtrackx/6_roi_probtrackx.sh" \
  --wd "${WD}" \
  --data_dir "${DATA_DIR}" \
  --sub_list "${SUB_LIST}" \
  --n_samples "${N_SAMPLES}" \
  --dis_cor "${DIS_COR}" \
  --len_step "${LEN_STEP}" \
  --n_steps "${N_STEPS}" \
  --cur_thres "${CUR_THRES}" \
  --sampvox "${SAMPVOX}" \
  --probtrackx_gpu "${PROBTRACKX_GPU}" \
  --stop_masks "${STOP_MASKS}" \
  --waypoint_masks "${WAYPOINT_MASKS}" \
  --exclusion_masks "${EXCLUSION_MASKS}" \
  --target_masks "${TARGET_MASKS}" \
  --is_t1_in_diffusion "${IS_T1_IN_DIFFUSION}" 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 6_roi_probtrackx done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 7) calculate connectivity matrix between each voxel in ROI and the remain voxels of whole brain 
#	 and correlation matrix among voxels in ROI
if [[ ${SWITCH[@]/_7_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 7_roi_calc_matrix start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/7_roi_calc_matrix/7_roi_calc_matrix.sh" "${WD}" ${SUB_LIST} ${POOLSIZE}  2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 7_roi_calc_matrix done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 8) ROI parcellation using spectral clustering, to generate 2 to max cluster number subregions
if [[ ${SWITCH[@]/_8_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 8_roi_parcellation start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/8_roi_parcellation/8_roi_parcellation.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${NIFTI} ${METHOD} ${PROB_CLUSTERING} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 8_roi_parcellation done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 9) Tranforming parcelated ROIs to Template space 
if [[ ${SWITCH[@]/_9_/} != ${SWITCH[@]} ]]; then 
echo "$(date +%T)  =========== 9_roi_to_template start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/9_roi_to_template/9_roi_to_template.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${TEMPLATE} ${POOLSIZE} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 9_roi_to_template done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 10) Combining the individual cluster ROIs to one file
if [[ ${SWITCH[@]/_10_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 10_group_refer start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/10_group_refer/10_group_refer.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${GROUP_THRES} ${MATCH_HEMI} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 10_group_refer done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 11) Relabeling the clusters according to the group reference image for individual subjects
if [[ ${SWITCH[@]/_11_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 11_cluster_relabel start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/11_cluster_relabel/11_cluster_relabel.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${NIFTI} ${GROUP_THRES} ${METHOD} ${VOX_SIZE} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 11_cluster_relabel done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 12) Calculate the mean probability matrix for each cluster
if [[ ${SWITCH[@]/_12_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 12_calc_mpm start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/12_calc_mpm/12_calc_mpm.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${NIFTI} ${METHOD} ${MPM_THRES} ${VOX_SIZE} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 12_calc_mpm done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 13) Smooth the MPM masks
if [[ ${SWITCH[@]/_13_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 13_postprocess_mpm start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/13_postprocess_mpm/13_postprocess_mpm.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${NIFTI} ${MPM_THRES} ${VOX_SIZE} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 13_postprocess_mpm done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 14) Calculate the validity indices for the parcellation
if [[ ${SWITCH[@]/_14_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 14_validation start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/14_validation/14_validation.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${METHOD} ${VOX_SIZE} ${N_ITER} ${GROUP_THRES} ${split_half} ${MATCH_HEMI} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 14_validation done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 15) Make Plots of the validation indices
if [[ ${SWITCH[@]/_15_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 15_indices_plot start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/15_indices_plot/15_indices_plot.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${VOX_SIZE} ${NIFTI} ${split_half} ${tpd} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 15_indices_plot done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 16) Probtrackx to Template space 
if [[ ${SWITCH[@]/_16_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 16_probtrackx_to_template start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/16_probtrackx_to_template/16_probtrackx_to_template.sh" "${WD}" ${SUB_LIST} ${NIFTI} ${VOX_SIZE} ${NORMALIZE} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 16_probtrackx_to_template done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 17) Add the template connctivities per cluster 
if [[ ${SWITCH[@]/_17_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 17_add_template_connectivity start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/17_add_template_connectivity/17_add_template_connectivity.sh" "${WD}" ${SUB_LIST} 2>&1 | tee -a "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 17_add_template_connectivity done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

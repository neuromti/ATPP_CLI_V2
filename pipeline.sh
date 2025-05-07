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
  --stop_masks "${STOP_MASKS}" >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =============== 0_gen_WD done!  ===============" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 1) T1_to_MNI registration
if [[ ${SWITCH[@]/_1_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =============== 1_t1_to_b0 start! =============" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/1_t1_to_b0/1_t1_to_b0.sh" ${PIPELINE} "${WD}" ${SUB_LIST} ${POOLSIZE} ${SPM} ${NIFTI} ${TEMPLATE} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =============== 1_t1_to_b0 done!  =============" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 2) ROI registration, from MNI space to DTI space 
if [[ ${SWITCH[@]/_2_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  ========= 2_ROI_registration start! =========" |tee -a "${WD}/log/progress_check.txt"
T=$(date +%s)
bash "${PIPELINE}/Modules/2_ROI_registration/2_ROI_registration.sh" ${PIPELINE} "${WD}" ${SUB_LIST} ${POOLSIZE} ${SPM} ${NIFTI} >> "${LOG}"
T=$(($(date +%s)-T))
echo "$(date +%T)  ========= 2_ROI_registration done! =========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 3) calculate ROI coordinates in DTI space 
if [[ ${SWITCH[@]/_3_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 3_ROI_calc_coord start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/3_ROI_calc_cord/3_roi_calc_cord.sh" ${PIPELINE} "${WD}" ${SUB_LIST} ${POOLSIZE} ${NIFTI} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 3_ROI_calc_coord done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi


# 4) generate probabilistic tractography for each voxel in ROI 
if [[ ${SWITCH[@]/_4_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 4_ROI_probtrackx start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/4_ROI_probtrackx/4_roi_probtrackx.sh" \
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
  --target_masks "${TARGET_MASKS}" >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 4_ROI_probtrackx done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 5) calculate connectivity matrix between each voxel in ROI and the remain voxels of whole brain 
#	 and correlation matrix among voxels in ROI
if [[ ${SWITCH[@]/_5_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 5_ROI_calc_matrix start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/5_ROI_calc_matrix/5_roi_calc_matrix.sh" ${PIPELINE} "${WD}" ${SUB_LIST} ${NIFTI} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 5_ROI_calc_matrix done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 6) ROI parcellation using spectral clustering, to generate 2 to max cluster number subregions
if [[ ${SWITCH[@]/_6_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 6_ROI_parcellation start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/6_ROI_parcellation/6_ROI_parcellation.sh" ${PIPELINE} "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${NIFTI} ${METHOD} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 6_ROI_parcellation done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 7) Tranforming parcelated ROIs to Templatespace 
if [[ ${SWITCH[@]/_7_/} != ${SWITCH[@]} ]]; then 
echo "$(date +%T)  =========== 7_ROI_to_Template start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/7_ROI_to_Template/7_ROI_to_Template.sh" ${PIPELINE} "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${SPM} ${VOX_SIZE} ${METHOD} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 7_ROI_to_Template done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 8) Combining the individual cluster ROIs to one file
if [[ ${SWITCH[@]/_8_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 8_group_refer start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/8_group_refer/8_group_refer.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${NIFTI} ${METHOD} ${VOX_SIZE} ${GROUP_THRES} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 8_group_refer done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 9) Relabeling the clusters according to the group reference image for individual subjects
if [[ ${SWITCH[@]/_9_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 9_cluster_relabel start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/9_cluster_relabel/9_cluster_relabel.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${NIFTI} ${GROUP_THRES} ${METHOD} ${VOX_SIZE} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 9_cluster_relabel done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 10) Calculate the mean probability matrix for each cluster
if [[ ${SWITCH[@]/_10_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 10_calc_mpm start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/10_calc_mpm/10_calc_mpm.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${NIFTI} ${METHOD} ${MPM_THRES} ${VOX_SIZE} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 10_calc_mpm done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 11) Smooth the MPM masks
if [[ ${SWITCH[@]/_11_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 11_postprocess_mpm start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/11_postprocess_mpm/11_postprocess_mpm.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${NIFTI} ${MPM_THRES} ${VOX_SIZE} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 11_postprocess_mpm done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 12) Calculate the validity indices for the parcellation
if [[ ${SWITCH[@]/_12_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 12_validation start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/12_validation/12_validation.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${NIFTI} ${METHOD} ${VOX_SIZE} ${SPM} ${N_ITER} ${GROUP_THRES} ${MPM_THRES} ${split_half} ${tpd} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 12_validation done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 13) Make Plots of the validation indices
if [[ ${SWITCH[@]/_13_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 13_indices_plot start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/13_indices_plot/13_indices_plot.sh" "${WD}" ${SUB_LIST} ${MAX_CL_NUM} ${VOX_SIZE} ${NIFTI} ${split_half} ${tpd} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 13_indices_plot done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 14) Probtrackx to Template space 
if [[ ${SWITCH[@]/_14_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 14_probtrackx_to_template start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/14_probtrackx_to_template/14_probtrackx_to_template.sh" ${PIPELINE} "${WD}" ${SUB_LIST} ${POOLSIZE} ${NIFTI} ${VOX_SIZE} ${NORMALIZE} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 14_probtrackx_to_template done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 15) Add the template connctivities per cluster 
if [[ ${SWITCH[@]/_15_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 15_add_template_connectivity start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/15_add_template_connectivity/15_add_template_connectivity.sh" "${WD}" ${SUB_LIST} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 15_add_template_connectivity done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi

# 15) Add the template connctivities per cluster 
if [[ ${SWITCH[@]/_15_/} != ${SWITCH[@]} ]]; then
echo "$(date +%T)  =========== 15_add_template_connectivity start! ===========" |tee -a "${WD}/log/progress_check.txt"
T="$(date +%s)"
bash "${PIPELINE}/Modules/15_add_template_connectivity/15_add_template_connectivity.sh" "${WD}" ${SUB_LIST} >> "${LOG}"
T="$(($(date +%s)-T))"
echo "$(date +%T)  =========== 15_add_template_connectivity done! ===========" |tee -a "${WD}/log/progress_check.txt"
printf "Time elapsed: %02d:%02d:%02d:%02d\n\n" "$((T/86400))" "$((T/3600%24))" "$((T/60%60))" "$((T%60))" |tee -a "${WD}/log/progress_check.txt"
fi
# switches for each step,
# a step will NOT run if its number is NOT in the following array
SWITCH=(0 2 3 4 5 6)

# Data Directory
DATA_DIR=/media/sn/Frieder_Data/Projects/White_Matter_Alterations/STN/data/HCP_7T_Pipeline

# List of Subject_IDs
SUB_LIST=/media/sn/Frieder_Data/Projects/White_Matter_Alterations/STN/data/HCP_7T_Diffusion_subject_ids_not_truncated_30_01_25.txt

# Working Directory
WD=/media/sn/Frieder_Data/Projects/White_Matter_Alterations/STN/Results/HCP_Parcellation/ATPPeX_DISTAL_STN_Parcellation_Improved_Registration

# ROI directory which contains ROI files, e.g., Amyg_L.nii
ROI_DIR=/media/sn/Frieder_Data/Projects/White_Matter_Alterations/STN/data/DISTAL_STN_2009b_thr_05_bin

# Directory containing the target masks for the probabilistic tractography (none if wholebrain tractography is desired)
TARGET_MASKS=

# Directory containing the waypoint masks for the probabilistic tractography (none if wholebrain tractography is desired)
WAYPOINT_MASKS=

# Directory containing the exclusion masks for the probabilistic tractography (none if wholebrain tractography is desired)
EXCLUSION_MASKS=

# Directory containing the stop masks for the probabilistic tractography (none if wholebrain tractography is desired)
STOP_MASKS=

# Max number of clusters to parceltate the ROI
MAX_CL_NUM=10

TEMPLATE=/media/sn/Frieder_Data/DTI_Utils/Image_registration/data/atlas/mni_icbm152_t1_tal_nlin_asym_09b_hires_brain.nii.gz

#===============================================================================
# specific variables for some steps
#===============================================================================

# 1. t1_to_b0
IS_T1_IN_DIFFUSION=True
 
# 2_t1_to_template_registration
OVERWRITE_REGISTRATION=True

# 4_ROI_probtrackx, Number of samples, default 5000
N_SAMPLES=5000

# 4_ROI_probtrackx, distance correction, yes--(--pd), no--( )space
DIS_COR=--pd

# 4_ROI_probtrackx, the length of each step, default 0.5 mm
LEN_STEP=0.5

# 4_ROI_probtrackx, maximum number of steps, default 2000
N_STEPS=2000

# 4_ROI_probtrackx, curvature threshold (cosine of degree), default 0.2
CUR_THRES=0.2

# 4_ROI_calc_matrix, downsampling, new voxel size, e.g. 5*5*5. default 5
DOWN_SIZE=5

# 4_ROI_probtrackx, sample the streamline origins around the center of the voxel with radius SAMPVOX (0 for no sampling)
SAMPVOX=0.5

# 6_ROI_parcellation, clustering method, e.g. spectral clustering, default sc (available methods: kmeans, sc, simlr)
METHOD=sc

# If probabilistic clustering is desired, provide the a probabilistic ROI_mask
# EXPERIMENTAL!! 6_ROI_parcellation probabilistic clustering
PROB_CLUSTERING=0

# 7_ROI_toMNI_spm, new voxel size, default 1*1*1
VOX_SIZE=1

# 8_group_refer, group threshold, default 0.25 (-1 for masking with the original mask)
GROUP_THRES=-1   #### THINK ABOUT THRESHOLDING WITH THE ORIGINAL MASK INSTEAD OF MAJORITY VOTE

# 10_calc_mpm, mpm threshold, default 0.25
MPM_THRES=0.25

# 12_validation, the number of iteration, default 100
N_ITER=20

# 12_validation, the switch of calculating CV/Dice/NMI using split_half strategy, 1--yes, 0--no
split_half=1

# 12_validation, the switch of calculating topology distance (TpD) index, 1--yes, 0--no
tpd=1

MATCH_HEMI=1


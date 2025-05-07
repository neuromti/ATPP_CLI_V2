# pipeline directory
PIPELINE=/media/sn/Frieder_Data/Projects/Parcellation_Pipeline/sn_dti

# the number of parallel workers for MATLAB programs, default 7
POOLSIZE=4

# Run probtrackx using GPU or CPU? 0=CPU 1=GPU
PROBTRACKX_GPU=1

# SPM installation dicrectory
SPM=/home/sn/spm12

# 2_ROI_calc_coord, NIFTI toolbox directory - usually not necessary to change
NIFTI=${PIPELINE}/Modules/NIfTI_20130306

#===============================================================================
# environment variables that should be added or modified if necessary
#===============================================================================

# absolute path of command matlab
MATLAB_PATH=/usr/local/MATLAB/R2023b/bin/matlab

if [ -f "$MATLAB_PATH" ]; then
    export COMMAND_MATLAB="$MATLAB_PATH"
else
	echo "Commmand 'matlab' is not found! Please set it in config.sh!"
	exit 1
fi

# absolute path of command fsl_sub
if command -v fsl_sub > /dev/null 2>&1; then
	export COMMAND_FSLSUB=$(command -v fsl_sub)
else
	echo "Commmand 'fsl_sub' is not found! Please set it in config.sh!"
	exit 1
fi

# absolute path of command probtrackx
if command -v probtrackx > /dev/null 2>&1; then
	export COMMAND_PROBTRACKX=$(command -v probtrackx)
else
	echo "Commmand 'probtrackx' is not found! Please set it in config.sh!"
	exit 1
fi	

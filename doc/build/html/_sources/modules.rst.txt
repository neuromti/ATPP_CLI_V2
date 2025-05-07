Modules
=======

The ATPP consists of several modular components, each with a specific role in the pipeline.



.. dropdown:: **0_gen_WD**
   
   This module organizes input files into a predefined directory structure for ATPPeX. The directory structure is as follows:

   .. code-block:: text

      Working_dir
      |-- sub1
      |   |-- T1_sub1.nii
      |   `-- b0_sub1.nii
      |-- ...
      |-- subN
      |   |-- T1_subN.nii
      |   `-- b0_subN.nii
      |-- ROI_masks
      |   |-- <ROI>.nii
      |   `-- ...
      |-- Stop_masks
      |   |-- <ROI>_stop.nii
      |   `-- ...
      |-- Target_masks
      |   |-- <ROI>_target.nii
      |   `-- ...
      |-- Waypoint_masks
      |   |-- <ROI>_waypoint.nii
      |   `-- ...
      `-- log

   The script performs several operations:

   1. Creates directories for subjects, ROIs, Target_masks, Stop_masks and Waypoint_masks .
   2. Copies and unzips ROI files from the respective directory into the working directory.
   3. For each subject listed in the subject list:
      - Creates a subdirectory.
      - Copies and renames T1 and b0 NIfTI files from the data directory.
      - Ensures files are in the correct format (.nii or .nii.gz).

   .. rubric:: Arguments

   - **WD** (*str*): Path to the working directory.
   - **DATA_DIR** (*str*): Path to the data directory containing subject-specific files.
   - **SUB_LIST** (*str*): Path to a file containing a list of subject identifiers (one per line).
   - **ROI_DIR** (*str*): Path to the directory containing ROI masks.
   - **TARGET_DIR** (*str*): Path to the directory containing target masks (optional) | Naming: "<ROI>_targets.nii".
   - **WAYPOINT_MASKS** (*str*): Path to the directory containing waypoint masks (optional) | Naming: "<ROI>_waypoint.nii".
   - **EXCLUSION_MASK_MASKS** (*str*): Path to the directory containing exclussion masks (optional) | Naming: "<ROI>_exclusion.nii".
   - **STOP_MASKS** (*str*): Path to the directory containing stop masks (optional) | Naming: "<ROI>_stop.nii". 

   .. rubric:: Error Handling
   - Exits with an error if ROI, target, waypoint or exclussion files are not in .nii or .nii.gz format.
   - Exits with an error if subject-specific b0_brain or T1_brain files are missing or in the wrong format.
   - Logs informative messages for each operation.



.. dropdown:: **1_t1_to_b0**

   This Module does the registration of  the subjects T1-weighted images from T1 space to DTI space using an SPM12.

   The script performs the following operations:

   1. Registration of the subjects T1-weighted images from T1 space to DTI space using affine transformation from SPM12.
   2. The T1-weighted images are replaced by the T1-weighted images in DTI space.

   .. rubric:: Arguments

   - **PIPELINE** (*str*): Path to the pipeline script or configuration.
   - **WD** (*str*): Path to the working directory.
   - **SUB_LIST** (*str*): Path to a file containing a list of subject identifiers (one per line).
   - **POOLSIZE** (*int*): Number of parallel processes to use for registration.
   - **SPM** (*str*): Path to the SPM toolbox.
   - **NIFTI** (*str*): Path to the NIFTI toolbox.
   - **TEMPLATE** (*str*): Path to the template file for registration.

   .. rubric:: Error Handling

   - Ensures all required input arguments are provided.
   - Logs errors if files are missing or if MATLAB fails to execute the registration.


   .. rubric:: Output

   The T1-MRI scans in the subjects diffusion space named: T1_in_diffusion_scpace_<subject>.nii

.. dropdown:: **2_ROI_registration**

   This Module estimated a non-linear defomation field from the subjects diffusion space to MNI space.
   The inverse of this deformation field is used to tranform the...

   - ROI_masks
   - Target_masks
   - Stop_masks
   - Waypoint_masks

   ...to the subjects diffusion space.

   The script performs the following operations:

   1. Registration of the subjects T1-weighted images from Diffusion space to standard space (ususally MNI152) using the nonlinear transformation from SPM12.
   2. The inverse of the deformation field is used to transform the ROI_masks, Target_masks, stop_masks and waypoint_masks from standard space to the subjects diffusion space.

   .. rubric:: Arguments

   - **PIPELINE** (*str*): Path to the pipeline script or configuration.
   - **WD** (*str*): Path to the working directory.
   - **SUB_LIST** (*str*): Path to a file containing a list of subject identifiers (one per line).
   - **POOLSIZE** (*int*): Number of parallel processes to use for registration.
   - **SPM** (*str*): Path to the SPM toolbox.
   - **NIFTI** (*str*): Path to the NIFTI toolbox.

   .. rubric:: Output

   A folder for each of the mask types in each subjectfolder containing the registered masks in diffusion space.

.. dropdown:: **3_ROI_calc_cord**

   This modules calculates the coordinates of the voxels in the various used masks in diffusio space. 
   Additionally, it calculates the volume of the masks in diffusion space.

   The script performs the following operations:

   1. Creates a txt file for each mask (ROI, Target, Stop, Waypoint) in each of the subjects subfolders containing the coordinates of each of the masks in diffusion space.
   2. Creates a csv file for each type of mask (ROI, Target, Stop, Waypoint) and saves the volumes of the masks in diffusion space.

   .. rubric:: Arguments

   - **PIPELINE** (*str*): Path to the pipeline script or configuration.
   - **WD** (*str*): Path to the working directory.
   - **SUB_LIST** (*str*): Path to a file containing a list of subject identifiers (one per line).
   - **POOLSIZE** (*int*): Number of parallel processes to use for registration.
   - **NIFTI** (*str*): Path to the NIFTI toolbox.

   .. rubric:: Output

   CSV files for each mask type (ROI, Target, Stop, Waypoint) in the WD containing the volume of the masks of each subject in diffusion space.
   The coordinates in diffusion spaces of the masks are saved in txt files in the subject folders.

.. dropdown:: **4_ROI_probtrackx**

   This module performs probabilistic tractography using FSL's probtrackx2.

   The script performs the following operations:

   1. Performs probabilistic tractography using FSL's probtrackx2 using the users specified parameters:
   
   .. tab-set::

    .. tab-item:: Waypoint Masks

        | **Naming:** "<ROI>_waypoint.nii" (ROI being the ROI_masks that the waypoint masks should be applied to) 
        | **Function:** The waypoint masks serve as waypoints for the streamlines. Streamlines that do not pass through the waypoint masks will be deleted.

    .. tab-item:: Stop Masks

        | **Naming:** "<ROI>_stop.nii" (ROI being the ROI_masks that the stop masks should be applied to) 
        | **Function:** The stop masks serve as define areas that stop the streamlines.

    .. tab-item:: Exclusion Masks

         | **Naming:** "<ROI>_exclusion.nii" (ROI being the ROI_masks that the exclusion masks should be applied to) 
         | **Function:** The exclusion masks serve as areas that the streamlines are not allowed to pass through. Any streamlines that hit the exclusion masks will be deleted.

    .. tab-item:: Target Masks

         | **Naming:** "<ROI>_target.nii" (ROI being the ROI_masks that the target masks should be applied to) 
         | **Function:** The target masks serve as the target regions for the streamlines. The number of streamlines that reach the target masks is estimated. All other streamlines will not be considered.

   .. rubric:: Arguments

   - **WD** (*str*): Path to the working directory.
   - **DATA_DIR** (*str*): Path to the data directory containing subject-specific files.
   - **SUB_LIST** (*str*): Path to a file containing a list of subject identifiers (one per line).
   - **N_SAMPLES** (*int*): Number of streamlines to estimated in probabilistic tractography.
   - **DIS_COR** (*float*): Use distance correction?
   - **LEN_STEP** (*float*): Length of each step in mm.
   - **N_STEPS** (*int*): Maximum number of steps for each streamline.
   - **CUR_THRES** (*float*): Curvature threshold.
   - **SAMPVOX** (*str*): Sample around the voxel in a radius of this size? (None for no sampling).
   - **PROBTRACKX_GPU** (*bool*): Whether to use GPU acceleration for probtrackx2.
   - **STOP_MASK** (*str*): Use the stop mask?
   - **WAYPOINT_MASKS** (*list*): Use the waypoint masks?
   - **EXCLUSION_MASKS** (*str*): Use the exclusion mask?
   - **TARGET_MASKS** (*str*): Use the target mask?

   .. rubric:: Output

   The output of the probtrackx2 is saved in each of the subjects subfolders.


.. dropdown:: **5_ROI_calc_matrix**

   This module calculates the connectivity matrix (between the voxels in the seed region and the rest of the brain) for each subject.

   The script performs the following operations:

   1. Creates a folder named '<ROI>_matrix' in each of the subjects subfolders containing the connectivity matrix.

   .. rubric:: Arguments

   - **PIPELINE** (*str*): Path to the pipeline script or configuration.
   - **WD** (*str*): Path to the working directory.
   - **SUB_LIST** (*str*): Path to a file containing a list of subject identifiers (one per line).
   - **POOLSIZE** (*int*): Number of parallel processes to use for registration.
   - **NIFTI** (*str*): Path to the NIFTI toolbox.


   .. rubric:: Output

   A folder named '<ROI>_matrix' is created in each of the subjects subfolders containing the connectivity matrix.

.. dropdown:: **6_ROI_parcellation**

   This module perform clustering of the voxels in the seed region based on the correlation of their whole-brain connectivity profiles. (For now only spectral clustering is implemented)

   The function performs the following operations:

   1. Reads a list of subjects from a provided file.
   2. Iterates over the ROIs of each subject and loads the corresponding data, including voxel coordinates and a connectivity matrix.
   3. Filters and prepares the connectivity matrix for clustering.
   4. Computes the pairwise correlation between voxels (and saves the correlation matrix).
   5. Applies the selected clustering method to divide the ROI into multiple clusters, with the number of clusters ranging from 2 to a maximum specified by ``MAX_CL_NUM``.
   6. Generates and saves parcellation maps for each ROI, with clusters encoded as distinct values.

   .. rubric:: Arguments

   - **PIPELINE** (*str*): Path to the pipeline script or configuration.
   - **WD** (*str*): Path to the working directory containing subject data.
   - **SUB_LIST** (*str*): Path to a file with a list of subject identifiers (one per line).
   - **MAX_CL_NUM** (*int*): Maximum number of clusters per ROI. Clustering will create maps with cluster numbers ranging from 2 to ``MAX_CL_NUM``.
   - **NIFTI** (*str*): Path to the NIFTI toolbox.
   - **METHOD** (*str*): Clustering method to use. Supported options:
   - ``sc`` (spectral clustering)


   .. rubric:: Error Handling

   - Checks if required files (``connection_matrix.mat``) are available for each ROI.
   - Ensures that a valid clustering method is selected; otherwise, an error is raised.

   .. rubric:: Output

   - For each subject and ROI, the function produces parcellated NIfTI files named ``<ROI_name><k>.nii``.
   - Files are stored in a subdirectory named ``<ROI_name>_<METHOD>`` within the subject's directory.

.. dropdown:: **7_ROI_to_template**

   This module transforms Regions of Interest (ROIs) from **Diffusion** space to **Template** space using SPM's spatial normalization.
   The deformation field from Module 2 **ROI_registration** is used for the tranformation.

   The function performs the following operations:

   1. Reads a list of ROIs from the working directory.
   2. Iterates through the provided subjects and applies the previously calculated transformation (Module 2_ROI_registration) to the ROI parcellations to move them from Diffusion space to Template space.
   3. Saves the normalized parcellation maps with a prefix ``w`` to indicate the transformation into MNI space.
   4. Renames the normalized files and moves them to a subdirectory of the clusters directory.

   .. rubric:: Arguments

   - **WD** (*str*): Path to the working directory containing subject data and ROI files.
   - **SUB_LIST** (*str*): Path to a file with a list of subject identifiers (one per line).
   - **MAX_CL_NUM** (*int*): Maximum number of clusters per ROI. The function will normalize maps for cluster numbers ranging from 2 to ``MAX_CL_NUM``.
   - **POOLSIZE** (*int*): Number of parallel processes (not used explicitly in the current function).
   - **TEMPLATE** (*str*): Path to the MNI template file for normalization.
   - **VOX_SIZE** (*float*): Desired voxel size for the normalized ROIs in millimeters (e.g., 2.0 for isotropic 2mm voxels).
   - **METHOD** (*str*): Clustering method used to generate ROI parcellation. Required for locating parcellated ROI files.

   .. rubric:: Error Handling

   - Ensures that necessary files (e.g., deformation fields and ROI files) are available for each subject before proceeding.
   - Skips normalization for subjects or ROIs that have already been processed.

   .. rubric:: Output

   - Normalized NIfTI files for each ROI and cluster count, saved in a subfolder of the clusters directory.
   - File names follow the format: ``<vox_size>/<vox_size><ROI_name><k><Template>.nii``, where ``k`` is the cluster count.

.. dropdown:: **8_group_refer**

   This module aggregates the individual ROI parcellations in MNI space for all subjects and generates an average group parcellation image.

   The function performs the following operations:

   1. **Group Reference Image Creation**:  
      Aggregates individual ROI parcellations in MNI space for all subjects, applies a group threshold, and generates a binary reference image indicating the common ROI region across subjects.

   2. **Clustering Matrix Calculation**:  
      For each cluster number (up to a maximum), calculates a group co-occurrence matrix across subjects.

   3. **Indexing and Image Saving**:  
      Re-clusters the group matrix and saves the resulting reference image for each cluster count.

   .. rubric:: Arguments

   - **WD** (*str*): Path to the working directory containing subject data and ROI files.  
   - **SUB_LIST** (*str*): Path to a file with a list of subject identifiers (one per line).  
   - **MAX_CL_NUM** (*int*): Maximum number of clusters to calculate for the group reference.  
   - **NIFTI** (*str*): Path to the NIfTI library required for processing.  
   - **METHOD** (*str*): Clustering method used to generate ROI parcellation.  
   - **VOX_SIZE** (*float*): Desired voxel size for group reference images in millimeters (e.g., 2.0 for isotropic 2mm voxels).  
   - **GROUP_THRES** (*float*): Threshold for determining group overlap in ROI parcellation, expressed as a fraction of subjects.
   - **MATCH_HEMI** (*int*): Whether to match hemispheres in the group reference image (1 for yes, 0 for no). (Only enable, if you just provide two ROIs which represents the same structure in both hemispheres)

   .. rubric:: Steps Performed

   1. **ROI Iteration**:  
         - Iterates through all ROI masks in the ``ROI_masks`` subdirectory of the working directory.

   2. **Group Reference Image Generation**:  
         - Loads ROI parcellations for each subject.  
         - Binarizes the ROI data, aggregates across subjects, and applies the group threshold.
         - Saves the resulting group reference image in the appropriate subdirectory.

   3. **Clustering Matrix Calculation**:  
         - For each cluster number (2 to ``MAX_CL_NUM``), calculates a co-occurrence matrix for the ROI.
         - Computes a re-clustered image based on the group matrix and saves the final result.
   4. **Match Hemispheres**:  
         - If ``MATCH_HEMI`` is enabled, the script matches the labels of the group parcellation between the hemispheres.

   .. rubric:: Output

   - **Group Reference Image**:  
      The final group reference image is saved with the name:  
      ``group_<num_subjects>_<vox_size>mm/<ROI>_roimask_thr<group_threshold>%.nii.gz``

   - **Cluster-Specific Reference Images**:  
      For each cluster count from 2 to ``MAX_CL_NUM``, the resulting reference images are saved with the name:  
      ``<vox_size>mm_<ROI>_<cluster_num>_<group_threshold>%_group.nii.gz``

.. dropdown:: **9_cluster_relabel**

   Relabels the subject specific clustering solutions to mach the group_refference parcellation.

   .. rubric:: Steps Performed

   1. **Iteration Through ROI Masks**:
         - The script loops through all ROI masks in the ``ROI_masks`` subdirectory of the working directory.

   2. **Cluster Relabeling**:
      - For each cluster number (from 2 to ``MAX_CL_NUM``), the module:
      - Loads the group reference image for the cluster number.
      - Matches clusters in each subject's image to the group reference using the Hungarian algorithm.
      - Relabels clusters in the subject's image to align with the group image.

   3. **Saving Relabeled Images**:
      - The relabeled images for each subject are saved in the corresponding directory with the following naming convention:

      ``<vox_size>mm_<ROI>_<cluster_num>_Template_relabel_group.nii.gz``

   .. rubric:: Arguments

   The script accepts the following arguments from the command line:

   - **WD** (*str*): Path to the working directory containing subject data and ROI files.
   - **SUB_LIST** (*str*): Path to a file listing subject identifiers (one per line).
   - **MAX_CL_NUM** (*int*): Maximum number of clusters.
   - **NIFTI** (*str*): Path to the NIfTI library required for processing.
   - **GROUP_THRES** (*float*): Threshold for determining group overlap in ROI parcellation, expressed as a fraction of subjects.
   - **METHOD** (*str*): Clustering method used to generate ROI parcellations.
   - **VOX_SIZE** (*float*): Desired voxel size for output images, in millimeters (e.g., 2.0 for isotropic 2mm voxels).

   .. rubric:: Outputs

   - **Relabeled Images**:
   The final relabeled images for each subject and cluster count are saved in the subject's directory.

   - **Naming Convention**:
   The output files follow this naming pattern:
   ``<vox_size>mm_<ROI>_<cluster_num>_Template_relabel_group.nii.gz``

.. dropdown:: **10_calc_mpm**

   Calculates a maximum probability map (MPM) for each of the clusters of each ROI representing the probabilty of each voxel belonging to the cluster.

   .. rubric:: Steps Performed

   1. **Iteration Through ROI Masks**:
         - The script loops through all ROI masks in the ``ROI_masks`` subdirectory of the working directory.

   2. **Probabilistic Maps Calculation**:
         - For each cluster number (from 2 to ``MAX_CL_NUM``), the MATLAB function:
         - Loads the corresponding relabeled subject-specific clustering images.
         - Calculates probabilistic maps for each cluster across all subjects.
         - Applies a threshold to exclude low-confidence regions.

   3. **Saving Results**:
         - The probabilistic maps are saved in the output directory with the following naming conventions:
         - Probabilistic maps: ``<vox_size>mm_<ROI>_<cluster_num>_<subregion>.nii.gz``

   .. rubric:: Arguments

   The Bash script accepts the following arguments:

   - **WD** (*str*): Path to the working directory containing subject data and ROI files.
   - **SUB_LIST** (*str*): Path to a file listing subject identifiers (one per line).
   - **MAX_CL_NUM** (*int*): Maximum number of clusters.
   - **NIFTI** (*str*): Path to the NIfTI library required for processing.
   - **METHOD** (*str*): Clustering method used to generate ROI parcellations.
   - **MPM_THRES** (*float*): Threshold for determining confidence in MPM generation, expressed as a fraction of subjects.
   - **VOX_SIZE** (*float*): Desired voxel size for output images, in millimeters (e.g., 2.0 for isotropic 2mm voxels).


   .. rubric:: Outputs

   - **Probabilistic Maps**:
   - The script generates probabilistic maps for each cluster within an ROI, saved with the naming pattern:
      ``<vox_size>mm_<ROI>_<cluster_num>_<subregion>.nii.gz``


.. dropdown:: **11_postprocess_mpm**

   Smooths the Maximum Probability Maps (MPMs) by applying a majority vote within the neighborhood of each voxel.

   .. rubric:: Steps Performed

   1. **Iteration Through ROI Masks**:
         - The script loops through all ROI masks in the ``ROI_masks`` subdirectory of the working directory.

   2. **Neighborhood-Based Smoothing**:
         - For each cluster number (from 2 to ``MAX_CL_NUM``):
         - Loads the MPM image for the cluster number.
         - For each non-zero voxel, collects the labels of its six immediate neighbors.
         - Applies a majority voting scheme to reassign the voxel's label based on the most frequent label among its neighbors.

   3. **Saving Smoothed MPM**:
      - The smoothed MPM for each cluster is saved with the following naming convention:

      ``<vox_size>mm_<ROI>_<cluster_num>_MPM_thr<MPM_THRES>_group_smoothed.nii.gz``

   .. rubric:: Arguments

   **Inputs from Command Line**:

   The Bash script accepts the following arguments:

   - **WD** (*str*): Path to the working directory containing subject data and ROI files.
   - **SUB_LIST** (*str*): Path to a file listing subject identifiers (one per line).
   - **MAX_CL_NUM** (*int*): Maximum number of clusters.
   - **NIFTI** (*str*): Path to the NIfTI library required for processing.
   - **MPM_THRES** (*float*): Threshold for determining confidence in MPM generation, expressed as a fraction of subjects.
   - **VOX_SIZE** (*float*): Desired voxel size for output images, in millimeters (e.g., 2.0 for isotropic 2mm voxels).

   .. rubric:: Outputs

   - **Smoothed MPMs**:
   - The smoothed MPMs for each cluster are saved with the naming convention:
      ``<vox_size>mm_<ROI>_<cluster_num>_MPM_thr<MPM_THRES>_group_smoothed.nii.gz``

.. dropdown:: **12_validation**

   Calculates various metrics to validate the clustering solutions and helps to make an informed decision for the amount of clusters in the ROI.

   .. rubric:: Validation indices:

   1. **Split-Half Sampling:**
   - Randomly splits the subjects into two groups and calculates the similarity between the clustering solutions.
   Calculated scores:
         - Dice coefficient
         - Cramer's V
         - Normalized Mutual Information (NMI)
   1. **Topological distance:**
         - Calculates the topological distance between any combination of two ROIs clustering solutions.
         - This is usefull, if the ROIs is present in both hemisspheres and similar parcellations are expected.



.. dropdown:: **13_indices_plot**

   Generates plots of the validation metrics.

   .. rubric:: Resulting Plots:

   1. **Split-Half Sampling:**
         - Line Plots of the Dice coefficient, Cramer's V, and Normalized Mutual Information (NMI).
   2. **Topological Distance:**
         - Topological distance plot.

.. dropdown:: **14_shap_exp**

   Calculates the differentiating features of the clusters.

Refer to individual scripts in the `Modules` directory for detailed descriptions and usage.


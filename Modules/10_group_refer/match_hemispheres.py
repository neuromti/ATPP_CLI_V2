import nibabel as nib
import argparse
from medpy.metric.binary import dc
from scipy.optimize import linear_sum_assignment
import numpy as np
import os
import ants
import pyvista as pv


class MatchHemispheres:
    def __init__(self, wd, max_cl_num=8, sub_list=''):
        self.wd = wd
        self.max_cl_num = max_cl_num
        self.sub_list = sub_list
        self.get_input_files()
        self.get_transformation_between_hemis()
        self.apply_relabeling()

    def flip_nifti(self, nifti, axis=0):
        """
        Flip a NIfTI image along a specific axis.

        Parameters:
        nifti_path (str): The path to the NIfTI file.
        axis (int): The axis along which to flip the image.

        Returns:
        nib.Nifti1Image: The flipped NIfTI image.
        """
        data = nifti.numpy()
        flipped_data = np.flip(data, axis=axis)
        flipped_nifti = ants.from_numpy(flipped_data, origin=nifti.origin, spacing=nifti.spacing, direction=nifti.direction)
        return flipped_nifti

    def get_transformation_between_hemis(self):
        """
        Check if the hemispheres are symmetric.
        Returns:
        float: The % of overlap of the full mask.
        """
        roi_side_1 = self.mask_paths[0][0]
        roi_side_2 = self.mask_paths[0][1]
        print(f"Checking symmetry between {roi_side_1} and {roi_side_2}...")

        # Load the masks
        roi_side_1 = ants.image_read(roi_side_1).threshold_image(0.1)
        roi_side_2 = ants.image_read(roi_side_2).threshold_image(0.1)

        # Save the masks for debugging or further analysis
        roi_side_1_path = os.path.join(self.wd, 'roi_side_1.nii.gz')
        roi_side_2_path = os.path.join(self.wd, 'roi_side_2.nii.gz')
        ants.image_write(roi_side_1, roi_side_1_path)
        ants.image_write(roi_side_2, roi_side_2_path)

        # Flip the second mask along the horizontal axis
        flipped_nifti = self.flip_nifti(roi_side_2, axis=0)

        ants.image_write(flipped_nifti, os.path.join(self.wd, 'flipped_nifti.nii.gz'))

        registration = ants.registration(fixed=roi_side_1, moving=flipped_nifti, 
                                 type_of_transform='SyN')  # Use 'Affine' for affine registration
        
        ## Apply the registration to the flipped image
        #aligned_flipped_nifti = ants.apply_transforms(fixed=roi_side_1, moving=flipped_nifti, 
        #                                              transformlist=registration['fwdtransforms'], interpolator='genericLabel')

        ## Save the aligned flipped image for debugging or further analysis
        #aligned_flipped_nifti_path = os.path.join(self.wd, 'aligned_flipped_nifti.nii.gz')
        #ants.image_write(aligned_flipped_nifti, aligned_flipped_nifti_path)

        # Get the transformation (rigid or affine matrix)
        self.transformation = registration['fwdtransforms']



    def get_input_files(self):
        """
        Get the input files for the matching process.

        Returns:
        tuple: A tuple containing the input files for the left and right hemispheres.
        """
        # Get the name of the ROIs
        roi_mask_folder = os.path.join(self.wd, 'ROI_masks')
        roi_masks = os.listdir(roi_mask_folder)
        roi_names = [roi.split('.')[0] for roi in roi_masks]
        
        roi_side_1 = roi_names[0]
        roi_side_2 = roi_names[1]

        with open(self.sub_list, 'r') as f:
            subjects = f.readlines()
        num_subjects = len(subjects)

        # Construct the file paths
        file_paths = []
        for num_clusters in range(2, self.max_cl_num + 1):
            label_image_side_1 = os.path.join(self.wd, f'ConsensusClustering', roi_side_1, f'{roi_side_1}_{num_clusters}_clusters.nii.gz')
            label_image_side_2 = os.path.join(self.wd, f'ConsensusClustering', roi_side_2, f'{roi_side_2}_{num_clusters}_clusters.nii.gz')
            file_paths.append([label_image_side_1, label_image_side_2])
        self.mask_paths = file_paths

        
    def load_nifti(self, file_path):
        """
        Load a NIfTI file from a given path.

        Parameters:
        file_path (str): The path to the NIfTI file.

        Returns:
        nib.Nifti1Image: The loaded NIfTI file.
        """
        return nib.load(file_path), nib.load(file_path).get_fdata()
    
    def dice_coefficient(self, mask1, mask2):
        intersection = np.sum(mask1 & mask2)
        total = np.sum(mask1) + np.sum(mask2)
        return 2 * intersection / total if total > 0 else 0  # Avoid division by zero
    
    def match_clusters(self, hemisphere1, hemisphere2):
        """Match clusters between two hemispheres based on the Dice coefficient."""

        mask1_ants = ants.image_read(hemisphere1)
        mask2_ants = ants.image_read(hemisphere2)
        
        mask2_ants_flipped = self.flip_nifti(mask2_ants, axis=0)

        aligned_mask2 = ants.apply_transforms(fixed=mask1_ants, moving=mask2_ants_flipped, 
                                            transformlist=self.transformation, interpolator='genericLabel')  # Use 'genericLabel' for label images


        # Get the image data as a NumPy array
        hemisphere_1_data = mask1_ants.numpy()
        aligned_mask2 = aligned_mask2.numpy()


        labels1 = np.unique(hemisphere_1_data)
        labels2 = np.unique(aligned_mask2)
        
        # Remove background label
        labels1 = labels1[labels1 != 0]
        labels2 = labels2[labels2 != 0]

        # Initialize cost matrix (negative Dice coefficients for minimization)
        cost_matrix = np.zeros((len(labels1), len(labels2)))

        for i, label1 in enumerate(labels1):
            for j, label2 in enumerate(labels2):
                mask1 = (hemisphere_1_data == label1)
                mask2 = (aligned_mask2 == label2)
                cost_matrix[i, j] = 1-self.dice_coefficient(mask1, mask2)  # Use Dice coefficient
 
        # Solve the assignment problem
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        # Create a mapping of labels
        mapping = {labels1[row]: labels2[col] for row, col in zip(row_ind, col_ind)}
        print(f'Mapping of labels: {mapping}')
        return mapping
    
    def relabel_clusters(sef, data, mapping):
        """Reassign labels in the data array based on the mapping."""
        relabeled_data = np.copy(data)
        for old_label, new_label in mapping.items():
            relabeled_data[data == new_label] = old_label
        return relabeled_data
    
    def apply_relabeling(self):
        for i, (hemisphere1, hemisphere2) in enumerate(self.mask_paths):
            print(f"[{i+2}/{self.max_cl_num}] Matching clusters between {hemisphere1} and {hemisphere2}...")
            mapping = self.match_clusters(hemisphere1, hemisphere2)
            nifti_hem_2, data_hem_2 = self.load_nifti(hemisphere2)

            relabeled_hemisphere_data = self.relabel_clusters(data_hem_2, mapping)
            relabeled_hemisphere_nifti = nib.Nifti1Image(relabeled_hemisphere_data, nifti_hem_2.affine, nifti_hem_2.header)
            os.rename(hemisphere2, hemisphere2 + '.old')
            nib.save(relabeled_hemisphere_nifti, hemisphere2)


def read_parameters():
    """
    Read parameters from command line arguments.
    Returns:
    dict: A dictionary of parameters.
    """
    parser = argparse.ArgumentParser(description='ROI Parcellation Script')
    parser.add_argument('--wd', type=str, required=True, help='Working directory')
    parser.add_argument('--sub_list', type=str, required=True, help='Subject list')
    parser.add_argument('--max_cl_num', type=int, default=8, help='Maximum number of clusters')
    args = parser.parse_args()

    parameters = {
        'WD': args.wd,
        'SUB_LIST': args.sub_list,
        'MAX_CL_NUM': args.max_cl_num,
    }
    return parameters

if __name__ == "__main__":
    parameters = read_parameters()
    MatchHemispheres(parameters['WD'], parameters['MAX_CL_NUM'], parameters['SUB_LIST'])    

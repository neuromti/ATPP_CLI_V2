import ants
import numpy as np



class CalculateWarpBetweenHemispheres:
    def __init__(self, image_hemisphere_1, image_hemisphere_2, type_of_transform='SyN', flip_one_hemisphere=True):
        self.image_hemisphere_1 = image_hemisphere_1
        self.image_hemisphere_2 = image_hemisphere_2
        self.type_of_transform = type_of_transform
        self.flip_one_hemisphere = flip_one_hemisphere

    def run(self):
        # Use ANTs to calculate the warp between the two hemispheres
        if self.flip_one_hemisphere:
            image_hemisphere_2 = self.flip_nifti(self.image_hemisphere_2, axis=0)
        else:
            image_hemisphere_2 = self.image_hemisphere_2

        registration = ants.registration(fixed=self.image_hemisphere_1, moving=image_hemisphere_2, 
                                 type_of_transform='SyN')
        



        return registration['fwdtransforms']
    
    @staticmethod
    def flip_nifti(nifti, axis=0):
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

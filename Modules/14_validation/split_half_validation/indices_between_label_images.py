import numpy as np
from medpy.metric import binary
from sklearn.metrics import normalized_mutual_info_score
from sklearn.metrics import adjusted_rand_score



class IndicesBetweenLabelImages:
    """
    Calculates a number of indeces between two label images.

    Parameters:
    label_image_1 (np.ndarray): The first label image.
    label_image_2 (np.ndarray): The second label image.
    """
    def __init__(self, label_image_1, label_image_2):
        self.label_image_1 = label_image_1
        self.label_image_2 = label_image_2

    def dice_coefficient(self):
        """
        Calculate the Dice coefficient between two label images.

        Returns:
        float: The Dice coefficient.
        """
        # Get the unique labels in the label images
        labels = np.unique(self.label_image_1)


        # Remove the background label
        labels = labels[labels != 0]
        
        # Create an empty list to store the Dice coefficient for each label
        dice_coefficients_per_cluster = {}

        # Calculate the Dice coefficient for each label
        for label in labels:

            # Make a mask for each label
            label_mask_1 = np.where(self.label_image_1 == label, 1, 0)
            label_mask_2 = np.where(self.label_image_2 == label, 1, 0)

            # Calculate the dice coefficient
            dice_coefficient = binary.dc(label_mask_1, label_mask_2)
            dice_coefficients_per_cluster[label] = dice_coefficient

        return dice_coefficients_per_cluster, np.mean(list(dice_coefficients_per_cluster.values()))
    
    def jaccard_index(self):
        """
        Calculate the Jaccard index between two label images.

        Returns:
        float: The Jaccard index.
        """
        # Get the unique labels in the label images
        labels = np.unique(self.label_image_1)

        # Remove the background label
        labels = labels[labels != 0]
        
        # Create an empty list to store the Jaccard index for each label
        jaccard_indices_per_cluster = {}

        # Calculate the Jaccard index for each label
        for label in labels:

            # Make a mask for each label
            label_mask_1 = (self.label_image_1 == label).astype(int)
            label_mask_2 = (self.label_image_2 == label).astype(int)

            # Calculate the Jaccard index
            intersection = np.sum(np.logical_and(label_mask_1, label_mask_2))
            union = np.sum(np.logical_or(label_mask_1, label_mask_2))
            jaccard_index = intersection / union
            jaccard_indices_per_cluster[label] = jaccard_index

        return jaccard_indices_per_cluster, np.mean(list(jaccard_indices_per_cluster.values()))
    
    def normalized_mutual_information(self):
        """
        Calculate the normalized mutual information between two label images.

        Returns:
        float: The normalized mutual information.
        """
        label_image_1_flat = self.label_image_1.flatten()
        label_image_2_flat = self.label_image_2.flatten()

        # Remove the background label (0) from the flattened label images
        mask = (label_image_1_flat != 0) & (label_image_2_flat != 0)
        label_image_1_flat = label_image_1_flat[mask]
        label_image_2_flat = label_image_2_flat[mask]

        nmi = normalized_mutual_info_score(label_image_1_flat, label_image_2_flat)

        return nmi
    
    def rand_index(self):
        """
        Calculate the Rand index between two label images.

        Returns:
        float: The Rand index.
        """
        label_image_1_flat = self.label_image_1.flatten()
        label_image_2_flat = self.label_image_2.flatten()

        # Remove the background label (0) from the flattened label images
        mask = (label_image_1_flat != 0) & (label_image_2_flat != 0)
        label_image_1_flat = label_image_1_flat[mask]
        label_image_2_flat = label_image_2_flat[mask]

        rand = adjusted_rand_score(label_image_1_flat, label_image_2_flat)

        return rand
        


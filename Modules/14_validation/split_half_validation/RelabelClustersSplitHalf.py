import numpy as np
import os
from scipy.optimize import linear_sum_assignment



class RelabelClusteringSolutions():
    def __init__(self, map1, map2):
        self.label_image_1 = map1
        self.label_image_2 = map2

    def dice_coefficient(self, mask1, mask2):
        """
            Calculate the Dice coefficient between two binary masks.
        """
        intersection = np.sum(mask1 & mask2)
        total = np.sum(mask1) + np.sum(mask2)
        return 2 * intersection / total if total > 0 else 0  # Avoid division by zero


    def get_label_mapping(self):
        """
            Get the mapping of labels between two label images that maximizes the dice coefficient. 
        """
        
        labels1 = np.unique(self.label_image_1)
        labels2 = np.unique(self.label_image_2)
        
        # Remove background label (assumed to be 0)
        labels1 = labels1[labels1 != 0]
        labels2 = labels2[labels2 != 0]

        # Initialize cost matrix (negative Dice coefficients for minimization)
        cost_matrix = np.zeros((len(labels1), len(labels2)))

        for i, label1 in enumerate(labels1):
            for j, label2 in enumerate(labels2):
                mask1 = (self.label_image_1 == label1)
                mask2 = (self.label_image_2 == label2)
                cost_matrix[i, j] = 1-self.dice_coefficient(mask1, mask2)

        # Solve the assignment problem
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        # Create a mapping of labels
        mapping = {labels1[row]: labels2[col] for row, col in zip(row_ind, col_ind)}

        return mapping
    
    def relabel_map2_to_match_map1(self):
        """
            Relabel the labels in the second label image to match the labels in the first label image. With the mapping that miximizes the Dice coefficient.
        """
        mapping = self.get_label_mapping()

        relabeled_data = np.copy(self.label_image_2)
        for old_label, new_label in mapping.items():
            relabeled_data[self.label_image_2 == new_label] = old_label
    
        return relabeled_data
    
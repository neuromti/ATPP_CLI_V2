import sys
import numpy as np
import nibabel as nib
import os
import matplotlib.pyplot as plt
import pandas as pd
import ants
import seaborn as sns
from sklearn.metrics.cluster import normalized_mutual_info_score
from calculate_warp_between_hemispheres import CalculateWarpBetweenHemispheres
from indices_between_label_images import IndicesBetweenLabelImages
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm


class BetweenHemisphereEvaluations():
    def __init__(self, WD, SUB, MAX_CL_NUM):
        self.WD = WD
        with open(SUB, 'r') as f:
            self.SUB = [line.strip() for line in f]
        self.MAX_CL_NUM = MAX_CL_NUM
        self.ROIs = [f.split('.')[0] for f in os.listdir(os.path.join(self.WD, 'ROI_masks'))]

        # Define relevant paths:

        # The ROIs in template space
        self.template_roi_side_1 = os.path.join(self.WD, 'ROI_masks', f'{self.ROIs[0]}.nii.gz')
        self.template_roi_side_2 = os.path.join(self.WD, 'ROI_masks', f'{self.ROIs[1]}.nii.gz')

        # The group parcellation of the ROIs
        self.group_parcellation_paths_ROI_side_1 = {
            i: os.path.join(self.WD, 'ConsensusClustering', self.ROIs[0], f'{self.ROIs[0]}_{i}_clusters.nii.gz')
            for i in range(2, int(self.MAX_CL_NUM) + 1)
        }
        self.group_parcellation_paths_ROI_side_2 = {
            i: os.path.join(self.WD, 'ConsensusClustering', self.ROIs[1], f'{self.ROIs[1]}_{i}_clusters.nii.gz')
            for i in range(2, int(self.MAX_CL_NUM) + 1)
        }

        # Subject specific parcellation paths
        self.subject_parcellation_paths_ROI_side_1 = {
            sub: {
                i: os.path.join(self.WD, sub, f'{sub}_{self.ROIs[0]}_cluster_results', f'{i}_Clusters', f'{self.ROIs[0]}_{i}_clusters_template_group_labels.nii.gz')
                for i in range(2, int(self.MAX_CL_NUM) + 1)
            }
            for sub in self.SUB
        }

        self.subject_parcellation_paths_ROI_side_2 = {
            sub: {
                i: os.path.join(self.WD, sub, f'{sub}_{self.ROIs[1]}_cluster_results', f'{i}_Clusters', f'{self.ROIs[1]}_{i}_clusters_template_group_labels.nii.gz')
                for i in range(2, int(self.MAX_CL_NUM) + 1)
            }
            for sub in self.SUB
        }



        self.validation_folder = os.path.join(self.WD, f'validation_{len(self.SUB)}')
        if not os.path.exists(self.validation_folder):
            os.makedirs(self.validation_folder)


    def hemispheric_coefficients_group(self):
        """
        Calculate the dice coefficient between hemispheres for each cluster.
        """

        roi_side_1_path = self.template_roi_side_1
        roi_side_2_path = self.template_roi_side_2

        # Load the ROIs
        roi_side_1 = ants.image_read(roi_side_1_path)
        roi_side_2 = ants.image_read(roi_side_2_path)

        registration = CalculateWarpBetweenHemispheres(roi_side_1, roi_side_2, type_of_transform='SyN', flip_one_hemisphere=True).run()
        

        average_results = []
        dice_coefficients_per_cluster = []
        jaccard_indices_per_cluster = []
        # Loop through the MAX_CL_NUM
        for i in range(2, int(MAX_CL_NUM) + 1):

            # Construct the paths to each of the hemispheres parcellations
            label_mask_side_1_path = self.group_parcellation_paths_ROI_side_1[i]
            label_mask_side_2_path = self.group_parcellation_paths_ROI_side_2[i]
            
            # Load the label masks
            side_1_ant = ants.image_read(label_mask_side_1_path)
            side_2_ant = ants.image_read(label_mask_side_2_path)

            side_2_ant_flipped = CalculateWarpBetweenHemispheres.flip_nifti(nifti=side_2_ant, axis=0)
            
            # Apply the transformation
            side_2_ant_flipped_warped = ants.apply_transforms(fixed=side_1_ant, moving=side_2_ant_flipped, transformlist=registration, interpolator='genericLabel')

            # Calculate the dice coefficient between the two hemispheres
            cluster_group_dice_coefficients, mean_group_dice_coefficient = IndicesBetweenLabelImages(side_1_ant.numpy(), side_2_ant_flipped_warped.numpy()).dice_coefficient()

            # Calculate the Jaccaard index between the two hemispheres
            cluster_group_jaccard_indices, mean_group_jaccard_index = IndicesBetweenLabelImages(side_1_ant.numpy(), side_2_ant_flipped_warped.numpy()).jaccard_index()

            # Calculate the Normalized Mutual Information between the two hemispheres
            nmi = IndicesBetweenLabelImages(side_1_ant.numpy(), side_2_ant_flipped_warped.numpy()).normalized_mutual_information()
            
            rand = IndicesBetweenLabelImages(side_1_ant.numpy(), side_2_ant_flipped_warped.numpy()).rand_index()

            results_per_cluster = {'Clusters': i, 'Dice Coefficient': mean_group_dice_coefficient, 'Jaccard Index': mean_group_jaccard_index, 'NMI (normalized mutual information)': nmi, 'Rand Index': rand}
            average_results.append(results_per_cluster)

            dice_coefficients_per_cluster.append(cluster_group_dice_coefficients)
            jaccard_indices_per_cluster.append(cluster_group_jaccard_indices)

            

        # Ensure the data folder exists
        os.makedirs(os.path.join(self.validation_folder, 'data'), exist_ok=True)
        # Save the results to a CSV file
        results_df = pd.DataFrame(average_results)
        results_df.to_csv(os.path.join(self.validation_folder, 'data', f'group_validation_hemispheric_stability.csv'), index=False)
        cluster_group_dice_coefficients_df = pd.DataFrame(dice_coefficients_per_cluster)
        cluster_group_dice_coefficients_df.to_csv(os.path.join(self.validation_folder, 'data', f'group_validation_hemispheric_stability_dice_coefficients_per_cluster.csv'), index=False)
        cluster_group_jaccard_indices_df = pd.DataFrame(jaccard_indices_per_cluster)
        cluster_group_jaccard_indices_df.to_csv(os.path.join(self.validation_folder, 'data',f'group_validation_hemispheric_stability_jaccard_indices_per_cluster.csv'), index=False)

    
    def hemispheric_coefficients_subject(self):
        """
        Calculate the dice coefficient between hemispheres for each subject, parallelized over subjects.
        Adds a progress indicator for parallel tasks.
        """

        results = []

        roi_side_1_path = self.template_roi_side_1
        roi_side_2_path = self.template_roi_side_2
        
        # Load the ROIs
        roi_side_1 = ants.image_read(roi_side_1_path)
        roi_side_2 = ants.image_read(roi_side_2_path)

        registration = CalculateWarpBetweenHemispheres(roi_side_1, roi_side_2, type_of_transform='SyN', flip_one_hemisphere=True).run()

        # Using ProcessPoolExecutor to parallelize over subjects
        with ProcessPoolExecutor(max_workers=6) as executor:  # Adjust max_workers based on your system's capacity
            # Create a tqdm progress bar for the number of subjects
            future_to_subject = {executor.submit(self.process_subject, sub, self.MAX_CL_NUM, registration): sub for sub in self.SUB}

            # Initialize tqdm for progress tracking
            with tqdm(total=len(self.SUB), desc="Processing Subjects") as pbar:
                # Collect the results as each task completes
                for future in as_completed(future_to_subject):
                    subject_results = future.result()
                    results.extend(subject_results)
                    pbar.update(1)  # Update the progress bar after each subject is processed

        # Convert the list of dictionaries to a DataFrame
        results_df = pd.DataFrame(results)
        os.makedirs(f"{self.validation_folder}/data", exist_ok=True)
        results_df.to_csv(os.path.join(f"{self.validation_folder}/data", 'subject_level_validation_hemispheric_stability.csv'), index=False)

    def process_subject(self, sub, MAX_CL_NUM, registration):
        subject_results = []

        for i in range(2, int(MAX_CL_NUM) + 1):

            sub_label_mask_roi_side_1_path = self.subject_parcellation_paths_ROI_side_1[sub][i]
            sub_label_mask_roi_side_2_path = self.subject_parcellation_paths_ROI_side_2[sub][i]

            # Load the label masks
            sub_side_1_ant = ants.image_read(sub_label_mask_roi_side_1_path)
            sub_side_2_ant = ants.image_read(sub_label_mask_roi_side_2_path)

            side_2_ant_flipped = CalculateWarpBetweenHemispheres.flip_nifti(nifti=sub_side_2_ant, axis=0)
        
            # Apply the transformation
            side_2_ant_flipped_warped = ants.apply_transforms(fixed=sub_side_1_ant, moving=side_2_ant_flipped, transformlist=registration, interpolator='genericLabel')

            # Calculate the dice coefficient between the two hemispheres
            _, mean_group_dice_coefficient = IndicesBetweenLabelImages(sub_side_1_ant.numpy(), side_2_ant_flipped_warped.numpy()).dice_coefficient()

            # Calculate the Jaccard index between the two hemispheres
            _, mean_group_jaccard_index = IndicesBetweenLabelImages(sub_side_1_ant.numpy(), side_2_ant_flipped_warped.numpy()).jaccard_index()

            # Calculate the Normalized Mutual Information between the two hemispheres
            nmi = IndicesBetweenLabelImages(sub_side_1_ant.numpy(), side_2_ant_flipped_warped.numpy()).normalized_mutual_information()

            rand_index = IndicesBetweenLabelImages(sub_side_1_ant.numpy(), side_2_ant_flipped_warped.numpy()).rand_index()

            # Store the results for the current cluster in a dictionary
            results_per_cluster = {
                'Subject': sub,
                'Clusters': i,
                'Dice Coefficient': mean_group_dice_coefficient,
                'Jaccard Index': mean_group_jaccard_index,
                'NMI (normalized mutual information)': nmi,
                'Rand Index': rand_index
            }
            subject_results.append(results_per_cluster)
        
        return subject_results
    

if __name__ == "__main__":  
    if len(sys.argv) != 4:
        print("Usage: python3 topological_distance.py <WD> <SUB> <MAX_CL_NUM>")
        sys.exit(1)

    WD = sys.argv[1]
    SUB = sys.argv[2]
    MAX_CL_NUM = sys.argv[3]


    evaluations = BetweenHemisphereEvaluations(WD, SUB, MAX_CL_NUM)
    print("Calculating hemispheric coefficients on group level...")
    #evaluations.hemispheric_coefficients_group()
    print("Calculating hemispheric coefficients on subject level...")
    evaluations.hemispheric_coefficients_subject()
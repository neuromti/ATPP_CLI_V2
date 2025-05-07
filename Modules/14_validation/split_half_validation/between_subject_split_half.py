import sys
import numpy as np
import os
import pandas as pd
from indices_between_label_images import IndicesBetweenLabelImages
from ConsensusClustering import ConsensusClustering
from RelabelClustersSplitHalf import RelabelClusteringSolutions


class BetweenSubjectSplitHalfEvaluations:
    """
    A class to evaluate the stability of clustering solutions using a split-half reliability approach.

    This class performs split-half reliability testing on clustering solutions by randomly splitting
    subjects into two groups, making a consenus clustering of either group, and then comparing
    the clustering solutions using various similarity metrics.

    Attributes:
    -----------
    WD : str
        Working directory where results and data are stored.
    SUB : list
        List of subject IDs read from a file.
    MAX_CL_NUM : int
        Maximum number of clusters to evaluate.
    N_ITER : int
        Number of iterations for split-half evaluation.
    ROIs : list
        List of regions of interest (ROIs) for clustering analysis.
    validation_folder : str
        Path to the folder where validation results are stored.
    
    Methods:
    --------
    split_half_coefficients():
        Computes split-half reliability scores for each ROI by repeatedly splitting subjects into two halves,
        performing clustering, and computing similarity metrics.
    
    calculate_split_half_scores(SUB1, SUB2, split):
        Performs clustering on two subject halves and computes similarity metrics between the clustering solutions.
    """

    def __init__(self, WD, SUB, MAX_CL_NUM, N_ITER):
        """
        Initializes the evaluation class with parameters for clustering and validation.
        
        Parameters:
        -----------
        WD : str
            Working directory where results and data are stored.
        SUB : str
            Path to the file containing subject IDs.
        MAX_CL_NUM : int
            Maximum number of clusters to evaluate.
        METHOD : str
            Clustering method used.
        VOX_SIZE : str
            Voxel size used in the analysis.
        N_ITER : int
            Number of iterations for split-half evaluation.
        GROUP_THRES : float
            Threshold for group-level ROI considered (0.25 meaning only voxels are considered that are labeled by at leat 25% of subjects).
        """
        self.WD = WD
        with open(SUB, 'r') as f:
            self.SUB = [line.strip() for line in f]
        self.MAX_CL_NUM = int(MAX_CL_NUM)
        self.N_ITER = int(N_ITER)
        self.ROIs = [f.split('.')[0] for f in os.listdir(os.path.join(self.WD, 'ROI_masks'))]
        
        self.validation_folder = os.path.join(self.WD, f'validation_{len(self.SUB)}')
        if not os.path.exists(self.validation_folder):
            os.makedirs(self.validation_folder)

    def split_half_coefficients(self):
        """
        Computes split-half reliability scores for each ROI.

        The method randomly splits subjects into two halves for multiple iterations,
        performs consensus clustering on each half separatly, and then compares the clustering
        solutions using similarity metrics such as Dice coefficient, Jaccard index,
        normalized mutual information, and Rand index. Results are saved as CSV files.
        """
        for ROI in self.ROIs:
            self.ROI = ROI
            scores_list = []

            print(f'Calculating split-half coefficients for {ROI}...', flush=True)

            for i in range(self.N_ITER):
                print(f'Split {i + 1}/{self.N_ITER}', flush=True)
                np.random.shuffle(self.SUB)
                half = len(self.SUB) // 2
                self.SUB1 = self.SUB[:half]
                self.SUB2 = self.SUB[half:]

                scores = self.calculate_split_half_scores(self.SUB1, self.SUB2, i)

                scores_list.extend(scores)

            # Convert the list of scores to a DataFrame and save to CSV
            scores_df = pd.DataFrame(scores_list)
            os.makedirs(f'{self.validation_folder}/data', exist_ok=True)
            scores_df.to_csv(os.path.join(f'{self.validation_folder}/data', f'split_half_scores_{ROI}.csv'), index=False)

    def calculate_split_half_scores(self, SUB1, SUB2, split):
        """
        Performs clustering on two subject halves and computes similarity metrics.

        Parameters:
        -----------
        SUB1 : list
            First half of the subject list.
        SUB2 : list
            Second half of the subject list.
        split : int
            The split iteration index.

        Returns:
        --------
        list
            A list of dictionaries containing similarity metrics for different numbers of clusters.
        """
        results = []
        
        for i in range(2, self.MAX_CL_NUM + 1):
            print(f'Clusters {i}/{self.MAX_CL_NUM}', flush=True)
            
            consensus_clustering_half_1 = ConsensusClustering(self.WD, self.ROI, SUB1, i).consensus_clustering_of_co_association_matrix()
            consensus_clustering_half_2 = ConsensusClustering(self.WD, self.ROI, SUB2, i).consensus_clustering_of_co_association_matrix()
            
            consensus_clustering_half_2 = RelabelClusteringSolutions(map1=consensus_clustering_half_1, map2=consensus_clustering_half_2).relabel_map2_to_match_map1()
            
            os.makedirs(f'{self.validation_folder}/data/split_half_clusterings', exist_ok=True)
            consensus_path1 = os.path.join(f'{self.validation_folder}/data/split_half_clusterings', f'{self.ROI}_split_{split + 1}_clusters_{i}_half_1.nii.gz')
            consensus_path2 = os.path.join(f'{self.validation_folder}/data/split_half_clusterings', f'{self.ROI}_split_{split + 1}_clusters_{i}_half_2.nii.gz')
            self.array_to_nifti(consensus_clustering_half_1, consensus_path1)
            self.array_to_nifti(consensus_clustering_half_2, consensus_path2)
            
            indices = IndicesBetweenLabelImages(consensus_clustering_half_1, consensus_clustering_half_2)
            metrics = {
                'Split': split + 1,
                'Clusters': i,
                'Dice Coefficient': indices.dice_coefficient()[1],
                'Jaccard Index': indices.jaccard_index()[1],
                'NMI (normalized mutual information)': indices.normalized_mutual_information(),
                'Rand Index': indices.rand_index()
            }
            results.append(metrics)

        return results

    def array_to_nifti(self, array, filepath):
        """
        Converts a numpy array to a NIfTI file and saves it to disk.

        Parameters:
        -----------
        array : numpy.ndarray
            The array to convert to NIfTI.
        filepath : str
            The path to save the NIfTI file.
        """
        import nibabel as nib
        nifti = nib.Nifti1Image(array, np.eye(4))
        nib.save(nifti, filepath)


if __name__ == '__main__':
    # Parse command-line arguments
    WD, SUB, MAX_CL_NUM, N_ITER = sys.argv[1:]
    evaluator = BetweenSubjectSplitHalfEvaluations(WD, SUB, MAX_CL_NUM, N_ITER)
    evaluator.split_half_coefficients()
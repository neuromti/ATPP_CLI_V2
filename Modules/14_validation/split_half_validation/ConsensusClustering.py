import numpy as np
import os
import nibabel as nib
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.cluster import SpectralClustering
import sys
from tqdm import tqdm


class ConsensusClustering:
    def __init__(self, WD, ROI, SUBs, CL_NUM):
        self.WD = WD
        self.SUBs = SUBs
        self.CL_NUM = CL_NUM
        self.ROI = ROI
        self.GROUP_THRESH = -1  # Default value for GROUP_THRESH

    def get_ROI_coordiantes(self):
        # If the group threshold is not set, use the original ROI mask
        if self.GROUP_THRESH == -1:
            ROI_coordinates = os.path.join(
                self.WD, 'ROI_masks', f'{self.ROI}.nii.gz'
            )
            ROI = nib.load(ROI_coordinates).get_fdata()
            ROI_indices = np.where((ROI != 0) & ~np.isnan(ROI))
            return np.transpose(ROI_indices)
        
        # Use the ROI thesh to make a new ROI mask -- THIS TAKES A LONG TIME - FIX THIS
        else:
            first_subject = self.get_file_path_of_normalized_subjectspecific_clustering(self.SUBs[0])
            first_subject = nib.load(first_subject).get_fdata()
        
            ROI_indices = np.zeros(shape=first_subject.shape)
            for sub in self.SUBs:
                ROI_sub_coordinates = self.get_file_path_of_normalized_subjectspecific_clustering(sub)
                ROI_sub = nib.load(ROI_sub_coordinates).get_fdata()
                ROI_sub_bin = (ROI_sub > 0).astype(int)
                ROI_indices += ROI_sub_bin

            ROI_indices = np.where(ROI_indices > int(float(self.GROUP_THRESH) * len(self.SUBs)))
                
            return np.transpose(ROI_indices)     

    def compute_similarity_matrix(self, relevant_voxel_data):
        num_voxels = relevant_voxel_data.shape[1]
        similarity_matrix = np.zeros((num_voxels, num_voxels), dtype=np.int32)

        print('Computing similarity matrix...')
        for i in tqdm(range(num_voxels)):
            similarity_matrix[i, i:] = np.sum(relevant_voxel_data[:, i:i+1] == relevant_voxel_data[:, i:], axis=0)
            similarity_matrix[i:, i] = similarity_matrix[i, i:]
        return similarity_matrix

    def make_co_association_matrix(self):
        def load_relevant_voxels(sub, relevant_voxel_coords):
            clustered_roi_path = self.get_file_path_of_normalized_subjectspecific_clustering(sub)
            img = nib.load(clustered_roi_path)
            data = img.get_fdata()
            # Only extract relevant voxels
            return np.array([data[x, y, z] for (x, y, z) in relevant_voxel_coords], dtype=np.int16)

        # Get the coordinates of the voxels in the ROI
        relevant_voxel_coords = self.get_ROI_coordiantes()  # Assume this function exists
        num_relevant_voxels = len(relevant_voxel_coords)
        num_subjects = len(self.SUBs)

        # Initialize an array to hold relevant voxels for each subject
        relevant_voxel_data = np.zeros((num_subjects, num_relevant_voxels), dtype=np.int16)

        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit a task for each subject to load relevant voxels
            future_to_sub = {executor.submit(load_relevant_voxels, sub, relevant_voxel_coords): i for i, sub in enumerate(self.SUBs)}
            
            # Wait for all futures to complete and store the results
            for future in as_completed(future_to_sub):
                i = future_to_sub[future]
                try:
                    relevant_voxel_data[i, :] = future.result()  # Store the loaded voxel data
                except Exception as e:
                    print(f"[ERROR] Error loading data for subject {self.SUBs[i]}: {e}")

        print('Loading relevant voxels completed')
        print(relevant_voxel_data.shape)

        
        similarity_matrix = self.compute_similarity_matrix(relevant_voxel_data)

        
        print('Similarity matrix computation completed')
        print(similarity_matrix.shape)

        # Remove self-similarity by setting the diagonal to zero
        np.fill_diagonal(similarity_matrix, 0)

        return similarity_matrix, relevant_voxel_coords
    
    def consensus_clustering_of_co_association_matrix(self):
        co_association_matrix, coordiantes = self.make_co_association_matrix()
        # Apply Spectral Clustering
        spectral = SpectralClustering(
            n_clusters=self.CL_NUM,
            affinity='precomputed',
            random_state=0
        )
        labels = spectral.fit_predict(co_association_matrix)
        print('Spectral clustering completed')
        
        # Create an empty NIfTI image with zeros
        first_subject_path = self.get_file_path_of_normalized_subjectspecific_clustering(self.SUBs[0])
        first_subject_img = nib.load(first_subject_path)


        consensus_clustering = np.zeros(first_subject_img.shape)

        # Fill the empty image with the labels at the relevant coordinates
        for label, (x, y, z) in zip(labels, coordiantes):
            consensus_clustering[x, y, z] = label + 1

        return consensus_clustering
    
    def get_file_path_of_normalized_subjectspecific_clustering(self, subject):
        possible_paths = [
            os.path.join(
                self.WD, subject, f'{subject}_{self.ROI}_cluster_results',
                f'{self.CL_NUM}_Clusters', f'{subject}_{self.ROI}_{self.CL_NUM}_clusters_template.nii.gz'
            )
        ]
        return next((p for p in possible_paths if os.path.exists(p)), None)
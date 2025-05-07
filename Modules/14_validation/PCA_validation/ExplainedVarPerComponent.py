import h5py
import os
import numpy as np
from sklearn.decomposition import PCA
import sys
import csv
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time


class PCA_validation:
    def __init__(self, WD, SUBs, ROI):
        self.WD = WD
        with open(SUBs, 'r') as f:
            self.SUB = [line.strip() for line in f]
        self.ROI = ROI

    def load_connectivity_mat(self, sub):
        connectivity_mat_path = os.path.join(self.WD, sub, f'{sub}_{self.ROI}_matrix', 'connection_matrix.npz')
        with np.load(connectivity_mat_path) as data:
            connectivity_mat = data['matrix']
        return connectivity_mat
    
    def calculate_the_explained_variance_per_principle_component(self, sub):
        
        # Load connectivity matrix
        connectivity_mat = self.load_connectivity_mat(sub)
        
        # Perform PCA
        pca = PCA(n_components=50)
        pca.fit(connectivity_mat)
        
        # Extract results
        explained_variance = pca.explained_variance_ratio_
        eigenvalues = pca.explained_variance_
        del connectivity_mat
        del pca
        
        return [sub] + np.array(explained_variance).tolist(), [sub] + np.array(eigenvalues).tolist()
    
    def get_explained_variances_per_principle_component_per_subject(self):
        save_path_variance = os.path.join(
            self.WD, f'validation_{len(self.SUB)}', 'data',
            f'explained_variance_per_principle_component_{self.ROI}.csv'
        )
        save_path_eigenvalues = os.path.join(
            self.WD, f'validation_{len(self.SUB)}', 'data',
            f'eigenvalues_per_principle_component_{self.ROI}.csv'
        )
        os.makedirs(os.path.dirname(save_path_variance), exist_ok=True)  # Ensure directory exists

        results = []
        
        # Parallel processing
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(self.calculate_the_explained_variance_per_principle_component, sub): sub for sub in self.SUB}
            for future in tqdm(as_completed(futures), desc="Processing Subjects", unit="subject", total=len(self.SUB)):
                explained_variance, eigenvalues = future.result()
                results.append((explained_variance, eigenvalues))

        header = ["Subject"] + [f"PC{i+1}" for i in range(50)]
        
        # Write results to CSV
        with open(save_path_variance, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for explained_variance, eigenvalues in results:
                writer.writerow(explained_variance)  # Pad shorter rows with None

                # Write results to CSV
        with open(save_path_eigenvalues, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for explained_variance, eigenvalues in results:
                writer.writerow(eigenvalues)  # Pad shorter rows with None 
            
    

if __name__ == '__main__':
    # Parse command-line arguments
    WD, SUB, ROI = sys.argv[1:]
    evaluator = PCA_validation(WD, SUB, ROI)
    evaluator.get_explained_variances_per_principle_component_per_subject()

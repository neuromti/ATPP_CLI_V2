from sklearn.cluster import SpectralClustering
import scipy.io
import h5py
import numpy as np
from scipy.sparse import csr_matrix
import nibabel as nib
import seaborn as sns
import os
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN, KMeans
from scipy.io import savemat
import argparse


def load_subject_ids(file_path):
    """
    Load a list of subject IDs from a given file.

    Parameters:
    file_path (str): The path to the file containing subject IDs.

    Returns:
    list: A list of subject IDs.
    """
    with open(file_path, 'r') as file:
        subject_ids = [line.strip() for line in file]
    return subject_ids


def plot_correlation_matrix(correlation_matrix):
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, cmap='coolwarm', center=0)
    plt.title('Correlation Matrix')
    plt.xlabel('ROI')
    plt.ylabel('ROI')
    plt.show()


def parse_arguments():
    """
    Parse command-line arguments.
    Returns:
    argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description='ROI Parcellation Script')
    parser.add_argument('--subject_list', type=str, required=True, help='Path to the subject list file')
    return parser.parse_args()

def read_parameters():
    """
    Read parameters from command line arguments.
    Returns:
    dict: A dictionary of parameters.
    """
    parser = argparse.ArgumentParser(description='ROI Parcellation Script')
    parser.add_argument('--pipeline', type=str, required=True, help='Pipeline Path')
    parser.add_argument('--wd', type=str, required=True, help='Working directory')
    parser.add_argument('--sub_list', type=str, required=True, help='Subject list')

    args = parser.parse_args()

    parameters = {
        'PIPELINE': args.pipeline,
        'WD': args.wd,
        'SUB_LIST': args.sub_list,
    }
    return parameters

def load_nifti(file_path):
    """
    Load a NIfTI file from a given path.

    Parameters:
    file_path (str): The path to the NIfTI file.

    Returns:
    nib.Nifti1Image: The loaded NIfTI file.
    """
    return nib.load(file_path), nib.load(file_path).get_fdata()

if __name__ == "__main__":
    parameters = read_parameters()
    subjects = load_subject_ids(parameters['SUB_LIST'])



    for subject in subjects:
        print(f"Processing subject {subject}...")

        # Make a folder for the correlation matrices
        correlation_matrices_folder = f"{parameters['WD']}/{subject}/Correlation_Matrices"
        if not os.path.exists(correlation_matrices_folder):
            os.makedirs(correlation_matrices_folder)

        # Load the probabilistic mask
        probabilistic_roi = f"{parameters['WD']}/{subject}/ROI_masks/"
        roi_files = os.listdir(f"{parameters['WD']}/{subject}/ROI_masks")

        for file in roi_files:
            
            # Get the ROI name without the extension
            basename = file.split('.')[0]
            
            # Check if this step has already been done
            mat_file_path_old = f"{parameters['WD']}/{subject}/{basename}_matrix/connection_matrix_inliers.mat"
            if os.path.exists(mat_file_path_old):
                print(f"File {mat_file_path_old} already exists. Skipping...")
                continue

            
            print(f"Processing ROI {basename}...")

            # Load probabilistic ROI mask
            nifti, roi_nifti = load_nifti(f"{probabilistic_roi}/{file}")
            print(f"Shape of the probabilistic mask: {roi_nifti.shape}")


            # Load the the connection matrix and coordinates
            mat_file_path = f"{parameters['WD']}/{subject}/{basename}_matrix/connection_matrix.mat"


            with h5py.File(mat_file_path, 'r') as mat_file:
                connection_matrix = mat_file['matrix'][:]
                coordinates_mat = mat_file['xyz'][:]

            print(f"Connection matrix loaded for subject {subject}.")
            print(f"Connection matrix shape: {connection_matrix.shape}")

            # Calculation the correlation matrix    
            correlation_matrix = np.corrcoef(connection_matrix.T)
            print(f"Correlation matrix computed for subject {subject}.")

            # Save the correlation matrix
            correlation_matrix_path = f"{correlation_matrices_folder}/{basename}_correlation_matrix.npy"
            np.save(correlation_matrix_path, correlation_matrix)
            print(f"Correlation matrix saved for subject {subject}.")

            # Load the coordinates of the ROI from the text file
            coordinates_file_path = f"{parameters['WD']}/{subject}/ROI_masks_Coords/{basename}_coords.txt"
            coordinates = np.loadtxt(coordinates_file_path)
            print(f"Coordinates loaded for subject {subject}.")
            print(f"Coordinates shape: {coordinates.shape}")

            # Extract the XYZ coordiantes as lists
            x_coords = coordinates[:,0].astype(int)
            y_coords = coordinates[:,1].astype(int)
            z_coords = coordinates[:,2].astype(int)

            # Retrieve all corresponding values from nifti_data in one step
            probabilisties_of_roi = roi_nifti[x_coords, y_coords, z_coords]
            
            # Remove the voxels with probabilisties less than 0.1
            probabilisties_of_roi = np.where(probabilisties_of_roi < 0.1, 0, probabilisties_of_roi)

            p = np.array(probabilisties_of_roi)
            # Diagonal importance matrix
            P = np.diag(p)
            
            # Compute the affinity matrix scaled by the diagonal importance matrix
            correlation_matrix = P @ correlation_matrix @ P
            # Save the cscaled orrelation matrix
            correlation_matrix_path = f"{correlation_matrices_folder}/{basename}_correlation_matrix_scaled.npy"
            np.save(correlation_matrix_path, correlation_matrix)

            # Transform the Affinity matrix into a distance matrix
            distance_matrix = 1 - correlation_matrix

            # Perform density-based clustering
            db = DBSCAN(eps=0.5, min_samples=5, metric='precomputed')
            labels = db.fit_predict(distance_matrix)
            
            # Remove outliers and only keep the biggest cluster
            unique_labels, counts = np.unique(labels[labels != -1], return_counts=True)
            print(f"Unique labels: {unique_labels}, Counts: {counts}")
            biggest_cluster_label = unique_labels[np.argmax(counts)]
            print(f"Biggest cluster label: {biggest_cluster_label}")


            # Set all voxels not in the biggest cluster to 0 and the biggest cluster to 1
            labels[labels != biggest_cluster_label] = -2
            labels[labels == biggest_cluster_label] = 1
            labels[labels != 1] = 0

            # Make the mask of the roi
            nifti_mask = np.zeros(roi_nifti.shape)
            for i, label in enumerate(labels):
                x, y, z = coordinates[i]
                nifti_mask[int(x), int(y), int(z)] = label

            # Save the nifti file
            new_nifti_img = nib.Nifti1Image(nifti_mask, nifti.affine, nifti.header)
            nib.save(new_nifti_img, f"{parameters['WD']}/{subject}/{basename}_subject_specific.nii")
            print(f"Parcellation saved for subject {subject}.")

            # Remove all rows with 0 from the connection matrix

            # Get the indices of the coordinates with label 1
            indices_with_label_1 = np.where(labels == 1)[0]

            # Remove rows from the connection matrix that are not in indices_with_label_1
            filtered_connection_matrix = connection_matrix[:, indices_with_label_1]
            print(f"Filtered connection matrix shape: {filtered_connection_matrix.shape}")
            # Remove rows from the coordinates_mat that are not in indices_with_label_1_mat
            filtered_coordinates_mat = coordinates_mat[:, indices_with_label_1]
            print(f"Filtered coordinates_mat shape: {filtered_coordinates_mat.shape}")
            # Save the filtered connection matrix and coordinates_mat in one mat file
            mat_file_path = f"{parameters['WD']}/{subject}/{basename}_matrix/connection_matrix.mat"

            # Save the data in MATLAB-compatible format
            savemat(mat_file_path, {
                'matrix': filtered_connection_matrix.T,
                'xyz': filtered_coordinates_mat.T
            })

            print(f"Filtered connection matrix and coordinates saved for subject {subject}.")
            del correlation_matrix
            del connection_matrix
            del distance_matrix
            del filtered_connection_matrix
            del filtered_coordinates_mat


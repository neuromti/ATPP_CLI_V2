import argparse
import os
import numpy as np
from sklearn.cluster import SpectralClustering
import nibabel as nib

def roi_parcellation(wd, subject, max_cl_num, method):
    """
    Perform ROI parcellation using spectral clustering.

    Parameters:
    wd (str): Working directory.
    sub_list (str): Path to the subject list file.
    max_cl_num (int): Maximum number of clusters.
    method (str): Clustering method (e.g., 'sc').
    """

    # ---- Define the relevant paths ----
    subject_folder = os.path.join(wd, subject)
    roi_folder = os.path.join(subject_folder, 'ROI_masks')

    # Get the list of ROIs
    roi_list = [f for f in os.listdir(roi_folder) if f.endswith('.nii') or f.endswith('.nii.gz')]

    # Loop through each ROI
    for roi in roi_list:
        # Load the correlation matrix for the current ROI
        matrix_path = os.path.join(subject_folder, roi.split('.')[0] + '_matrix', 'correlation_matrix.npz')
        # Load the currect roi
        roi_path = os.path.join(roi_folder, roi)
        roi_nifti = nib.load(roi_path)


        correlation_matrix = np.load(matrix_path)['matrix']
        seed_coords = np.load(matrix_path)['seed_vox_coords']



        for i in range(2, max_cl_num + 1):
            # Making the output folder
            output_folder = os.path.join(subject_folder, roi.split('.')[0] + f'_cluster_results', f"{i}_Clusters")
            os.makedirs(output_folder, exist_ok=True)


            # Perform spectral clustering
            clustering = SpectralClustering(n_clusters=i, affinity='precomputed', random_state=42)
            labels = clustering.fit_predict(correlation_matrix)

            # Save the clustering results
            output_path = os.path.join(output_folder, f"{roi.split('.')[0]}_{i}_clusters_native.nii.gz")
            clustered_roi = np.zeros(roi_nifti.get_fdata().shape)
            seeds_to_indeces = np.array([list(map(int, line.split()[:3])) for line in seed_coords])
            clustered_roi[tuple(seeds_to_indeces.T)] = labels + 1

            # Save the clustered ROI as a NIfTI file
            nib.save(nib.Nifti1Image(clustered_roi, roi_nifti.affine), output_path)



def main():
    parser = argparse.ArgumentParser(description="ROI parcellation using spectral clustering.")
    parser.add_argument("--wd", help="Working directory")
    parser.add_argument("--sub_list", help="Path to subject list file")
    parser.add_argument("--max_cl_num", type=int, help="Maximum number of clusters")
    parser.add_argument("--method", help="Clustering method (e.g., 'sc')")
    args = parser.parse_args()

    print(f"[INFO] Starting ROI parcellation with parameters:")
    print(f"  Working Directory: {args.wd}")
    print(f"  Subject List: {args.sub_list}")
    print(f"  Max Clusters: {args.max_cl_num}")
    print(f"  Method: {args.method}")

        # Load subject list
    with open(args.sub_list, "r") as f:
        subjects = [line.strip() for line in f if line.strip()]
    
    print(f"[INFO] Found {len(subjects)} subjects in the list.")

    for subject in subjects:
        print(f"[INFO] Processing subject: {subject}")
        roi_parcellation(args.wd, subject, args.max_cl_num, args.method)

if __name__ == "__main__":
    main()
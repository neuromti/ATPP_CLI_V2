import numpy as np
from scipy.sparse import coo_matrix
import os
import argparse
from concurrent.futures import ProcessPoolExecutor

def create_connectivity_and_correlation_matrix(imgfolder, outfolder):
    # [INFO] Loading the seed voxel coordinates
    seed_coords_path = os.path.join(imgfolder, 'coords_for_fdt_matrix2')
    with open(seed_coords_path, 'r') as file:
        lines = file.readlines()
    seed_coords = [line.strip() for line in lines]

    # [INFO] Loading the brainspace voxel coordinates
    brain_coords_path = os.path.join(imgfolder, 'tract_space_coords_for_fdt_matrix2')
    with open(brain_coords_path, 'r') as file:
        lines = file.readlines()
    brain_coords = [line.strip() for line in lines]

    # [INFO] Loading connectivity matrix from .dot file
    connection_mat_path = os.path.join(imgfolder, 'fdt_matrix2.dot')
    try:
        x = np.loadtxt(connection_mat_path)
        print(f"[INFO] Loaded matrix data from {connection_mat_path}")
    except Exception as e:
        print(f"[ERROR] Failed to load matrix data: {e}")
        return

    # [INFO] Building sparse connectivity matrix
    rows, cols, data = x[:, 0] - 1, x[:, 1] - 1, x[:, 2]
    num_rows = int(np.max(rows)) + 1
    num_cols = int(np.max(cols)) + 1
    con_matrix = coo_matrix((data, (rows.astype(int), cols.astype(int))), shape=(num_rows, num_cols)).tocsc()

    # [INFO] Cleaning matrix: Removing NaN and Inf values
    con_matrix.data[np.isnan(con_matrix.data) | np.isinf(con_matrix.data)] = 0

    # [INFO] Removing columns with all-zero values
    col_mask = np.array((con_matrix != 0).sum(axis=0)).flatten() > 0
    removed_cols = np.sum(~col_mask)
    con_matrix = con_matrix[:, col_mask]
    print(f"[INFO] Removed {removed_cols} empty columns.")

    # [INFO] Converting sparse matrix to dense format
    con_matrix = con_matrix.toarray()

    # [INFO] Calculating correlation matrix
    correlation_matrix = np.corrcoef(con_matrix.T, rowvar=False)
    print("[INFO] Correlation matrix calculated.")

    # [INFO] Saving connectivity matrix to .npz file
    output_path_con = os.path.join(outfolder, 'connection_matrix.npz')
    try:
        np.savez_compressed(output_path_con, 
                            matrix=con_matrix, 
                            seed_vox_coords=np.array(seed_coords), 
                            brainspace_coords=np.array(brain_coords))
        print(f"[INFO] Connectivity matrix saved to {output_path_con}")
    except Exception as e:
        print(f"[ERROR] Failed to save connectivity matrix: {e}")

    # [INFO] Saving correlation matrix to .npz file
    output_path_corr = os.path.join(outfolder, 'correlation_matrix.npz')
    try:
        np.savez_compressed(output_path_corr, 
                            matrix=correlation_matrix, 
                            seed_vox_coords=seed_coords)
        print(f"[INFO] Correlation matrix saved to {output_path_corr}")
    except Exception as e:
        print(f"[ERROR] Failed to save correlation matrix: {e}")

def process_subject(subject, wd):
    print(f"[INFO] Processing subject: {subject}")
    subject_folder = os.path.join(wd, subject)
    roi_folder = os.path.join(subject_folder, 'ROI_masks')

    if not os.path.exists(roi_folder):
        print(f"[WARNING] ROI folder not found for subject {subject}: {roi_folder}")
        return

    subject_roi_list = [f for f in os.listdir(roi_folder) if f.endswith('.nii') or f.endswith('.nii.gz')]
    print(f"[INFO] Found {len(subject_roi_list)} ROIs for subject {subject}.")

    for roi in subject_roi_list:
        roi_name = roi.split('.')[0]  # Remove the file extension
        probtrackx_folder = os.path.join(subject_folder, f"{roi_name}_probtrackx")
        if not os.path.isdir(probtrackx_folder):
            print(f"[WARNING] Probtrackx folder {probtrackx_folder} not found. Skipping.")
            continue
        matrix_folder = os.path.join(subject_folder, roi_name + '_matrix')
        os.makedirs(matrix_folder, exist_ok=True)
        create_connectivity_and_correlation_matrix(probtrackx_folder, matrix_folder)

def main():
    parser = argparse.ArgumentParser(description="Create connectivity and correlation matrices for multiple subjects.")
    parser.add_argument("wd", help="Working directory")
    parser.add_argument("sub_list", help="Path to file with list of subjects")
    parser.add_argument("pool_size", type=int, help="Number of parallel processes")
    args = parser.parse_args()

    print(f"[INFO] ----- Arguments: -----")
    print(f"  Working Directory: {args.wd}")
    print(f"  Subject List File: {args.sub_list}")
    print(f"  Pool Size: {args.pool_size}")
    print(f" ------------------------------")

    with open(args.sub_list, "r") as f:
        subjects = [line.strip() for line in f if line.strip()]
    print(f"[INFO] Found {len(subjects)} subjects in the list.")

    for subject in subjects:
        process_subject(subject, args.wd)

if __name__ == "__main__":
    main()
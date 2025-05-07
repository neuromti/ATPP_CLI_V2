import argparse
import os
import nibabel as nib
import numpy as np
from scipy.optimize import linear_sum_assignment
from concurrent.futures import ProcessPoolExecutor


def dice_coefficient(mask1, mask2):
    intersection = np.sum(mask1 & mask2)
    total = np.sum(mask1) + np.sum(mask2)
    return 2 * intersection / total if total > 0 else 0  # Avoid division by zero

def relabel_clusters(data, mapping):
    """Reassign labels in the data array based on the mapping."""
    relabeled_data = np.copy(data)
    for old_label, new_label in mapping.items():
        relabeled_data[data == old_label] = new_label
    return relabeled_data 

def process_cluster_wrapper(args):
    return process_cluster(*args)

def process_cluster(wd, subject, roi, i):
    roi_basename = roi.split('.')[0]
    subject_folder = os.path.join(wd, subject)
    cluster_results_folder = os.path.join(subject_folder, subject + '_' + roi_basename + '_cluster_results')

    print(f"[INFO] Processing {roi_basename} with {i} clusters for subject {subject}")
    
    clustered_roi_path = os.path.join(cluster_results_folder, f"{i}_Clusters", f"{subject}_{roi_basename}_{i}_clusters_template.nii.gz")
    group_template_path = os.path.join(wd, 'ConsensusClustering', roi_basename, f'{roi_basename}_{i}_clusters.nii.gz')

    if not os.path.exists(clustered_roi_path) or not os.path.exists(group_template_path):
        print(f"[WARNING] Missing file for {roi_basename} with {i} clusters. Skipping.")
        return

    clustered_roi = nib.load(clustered_roi_path)
    clustered_roi_data = clustered_roi.get_fdata()
    group_template = nib.load(group_template_path)
    group_template_data = group_template.get_fdata()

    labels1 = np.unique(group_template_data)
    labels2 = np.unique(clustered_roi_data)
    labels1 = labels1[labels1 != 0]
    labels2 = labels2[labels2 != 0]

    cost_matrix = np.zeros((len(labels1), len(labels2)))
    for l, label1 in enumerate(labels1):
        for j, label2 in enumerate(labels2):
            mask1 = (clustered_roi_data == label1)
            mask2 = (group_template_data == label2)
            cost_matrix[l, j] = 1 - dice_coefficient(mask1, mask2)

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    mapping = {labels1[row]: labels2[col] for row, col in zip(row_ind, col_ind)}
    relabeled_clustered_roi_data = relabel_clusters(clustered_roi_data, mapping)

    output_path = os.path.join(cluster_results_folder, f"{i}_Clusters", f"{roi_basename}_{i}_clusters_template_group_labels.nii.gz")
    nib.save(nib.Nifti1Image(relabeled_clustered_roi_data, clustered_roi.affine), output_path)


def cluster_relabel(wd, subject, max_cl_num, max_workers=14):
    roi_folder = os.path.join(wd, 'ROI_masks')
    roi_list = [f for f in os.listdir(roi_folder) if f.endswith('.nii.gz')]

    tasks = []
    for roi in roi_list:
        for i in range(2, max_cl_num + 1):
            tasks.append((wd, subject, roi, i))


    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        executor.map(process_cluster_wrapper, tasks)


def main():
    parser = argparse.ArgumentParser(description="ROI parcellation using spectral clustering.")
    parser.add_argument("--wd", help="Working directory")
    parser.add_argument("--sub_list", help="Path to subject list file")
    parser.add_argument("--max_cl_num", type=int, help="Maximum number of clusters")
    args = parser.parse_args()

    print(f"[INFO] Starting ROI parcellation with parameters:")
    print(f"  Working Directory: {args.wd}")
    print(f"  Subject List: {args.sub_list}")
    print(f"  Max Clusters: {args.max_cl_num}")

        # Load subject list
    with open(args.sub_list, "r") as f:
        subjects = [line.strip() for line in f if line.strip()]
    
    print(f"[INFO] Found {len(subjects)} subjects in the list.")

    for subject in subjects:
        print(f"[INFO] Processing subject: {subject}")
        cluster_relabel(args.wd, subject, args.max_cl_num)

if __name__ == "__main__":
    main()
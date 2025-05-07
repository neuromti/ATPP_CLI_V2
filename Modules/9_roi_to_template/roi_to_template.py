import nibabel as nib
import argparse
import numpy as np
import os
import ants
from concurrent.futures import ProcessPoolExecutor, as_completed

def roi_to_template(wd, subject, max_cl_num, template):
    # Define the relevant paths
    subject_folder = os.path.join(wd, subject)
    roi_folder = os.path.join(subject_folder, 'ROI_masks')
    # Get the list of ROIs
    roi_list = [f for f in os.listdir(roi_folder) if f.endswith('.nii') or f.endswith('.nii.gz')]

    for roi in roi_list:
        cluster_results_folder = os.path.join(subject_folder, roi.split('.')[0] + '_cluster_results')

        for i in range(2, max_cl_num + 1):
            # Load the clustered ROI
            clustered_roi_path = os.path.join(cluster_results_folder, f"{i}_Clusters", f"{roi.split('.')[0]}_{i}_clusters_native.nii.gz")
            apply_transform(subject_folder, roi, clustered_roi_path, template, i)


def apply_transform(subject_folder, roi, clustered_roi_path, template, i):
    # Load the clustered ROI
    roi_image = ants.image_read(clustered_roi_path)
    # Load the template image
    reference_image = ants.image_read(template)

    # Read the transforms
    affine_transform = os.path.join(subject_folder, 'transforms_between_diffusion_and_template_space', 'affine.mat')
    warp_transform = os.path.join(subject_folder, 'transforms_between_diffusion_and_template_space', 'warp.nii.gz')

    template_roi = ants.apply_transforms(
        fixed=reference_image,
        moving=roi_image,
        transformlist=[warp_transform, affine_transform],
        whichtoinvert=[False, False],
        interpolator='genericLabel'
    )

    # Save the transformed ROI
    cluster_results_folder = os.path.join(subject_folder, roi.split('.')[0] + '_cluster_results' , f"{i}_Clusters")
    os.makedirs(cluster_results_folder, exist_ok=True)
    output_path = os.path.join(cluster_results_folder, f"{roi.split('.')[0]}_{i}_clusters_template.nii.gz")
    ants.image_write(template_roi, output_path)



def main():
    parser = argparse.ArgumentParser(description="ROI parcellation using spectral clustering.")
    parser.add_argument("--wd", help="Working directory")
    parser.add_argument("--sub_list", help="Path to subject list file")
    parser.add_argument("--max_cl_num", type=int, help="Maximum number of clusters")
    parser.add_argument("--template", help="Path to the template image")
    parser.add_argument("--poolsize", type=int, default=4, help="Number of parallel jobs")
    args = parser.parse_args()

    print(f"[INFO] Starting ROI parcellation with parameters:")
    print(f"  Working Directory: {args.wd}")
    print(f"  Subject List: {args.sub_list}")
    print(f"  Max Clusters: {args.max_cl_num}")
    print(f"  Template: {args.template}")
    print(f"  Parallel Jobs: {args.poolsize}")

    with open(args.sub_list, "r") as f:
        subjects = [line.strip() for line in f if line.strip()]

    print(f"[INFO] Found {len(subjects)} subjects in the list.")

    with ProcessPoolExecutor(max_workers=args.poolsize) as executor:
        futures = {executor.submit(roi_to_template, args.wd, subject, args.max_cl_num, args.template): subject for subject in subjects}
        for future in as_completed(futures):
            subject = futures[future]
            try:
                future.result()
                print(f"[INFO] Finished subject: {subject}")
            except Exception as e:
                print(f"[ERROR] Error processing subject {subject}: {e}")

if __name__ == "__main__":
    main()
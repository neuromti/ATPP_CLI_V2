#!/usr/bin/env python3

import os
import argparse
import ants
from concurrent.futures import ProcessPoolExecutor, as_completed

def apply_inverse_transform(subject, wd, registration, roi_dir, roi_name):
    """
    Applies the inverse transformation to warp an ROI mask from MNI to native space.

    Parameters:
        subject (str): Subject ID.
        wd (str): Working directory.
        registration (dict): Registration object containing transforms.
        roi_dir (str): Directory containing ROI masks.
        roi_name (str): Name of the ROI mask file.
    """
    subject_dir = os.path.join(wd, subject)
    output_dir = os.path.join(subject_dir, roi_dir)
    os.makedirs(output_dir, exist_ok=True)

    roi_path = os.path.join(wd, roi_dir, roi_name)
    if not os.path.exists(roi_path):
        print(f"[WARNING] ROI mask {roi_name} not found. Skipping.")
        return

    roi_image = ants.image_read(roi_path)
    # Check if the reference image exists
    reference_image_path = os.path.join(subject_dir, f"T1_in_diffusion_space_{subject}.nii.gz")
    if not os.path.exists(reference_image_path):
        print(f"[Warning] Reference image not found for subject {subject}. Assuming T1 was already in Diffusion space.")
        # check if the T1_{subject}.nii.gz or T1_{subject}.nii.gz exists
        reference_image_path = os.path.join(subject_dir, f"T1_{subject}.nii.gz")
        if not os.path.exists(reference_image_path):
            reference_image_path = os.path.join(subject_dir, f"T1_{subject}.nii")
            if not os.path.exists(reference_image_path):
                print(f"[Error] Reference image not found for {subject}, skipping.")
                return
    # Load the reference image
    reference_image = ants.image_read(reference_image_path)

    # Check if the ROI image is probabilistic or binary
    roi_data = roi_image.numpy()
    unique_values = set(roi_data.flatten())

    if len(unique_values) < 3:
        print(f"[INFO] ROI {roi_name} is binary.")
        interpolator = 'genericLabel'
    else:
        print(f"[INFO] ROI {roi_name} is probabilistic.")
        interpolator = 'linear'

    print(f"[INFO] Applying inverse transform to ROI {roi_name} for subject {subject}.")
    warped_roi = ants.apply_transforms(
        fixed=reference_image,
        moving=roi_image,
        transformlist=[registration['affine_transform'], registration['invtransforms']],
        whichtoinvert=[True, False],
        interpolator=interpolator
    )

    output_path = os.path.join(output_dir, f"{subject}_{roi_name}")
    ants.image_write(warped_roi, output_path)

    # If processing Target_masks, append the path to target_paths.txt
    if roi_dir == 'Target_masks':
        target_paths_file = os.path.join(subject_dir, 'target_paths.txt')
        with open(target_paths_file, 'a') as f:
            f.write(f"{output_path}\n")

def load_transform_files(subject, wd):
    """
    Load the transform files for a given subject.
    """
    transform_dir = os.path.join(wd, subject, "transforms_between_diffusion_and_template_space")
    if not os.path.exists(transform_dir):
        print(f"[WARNING] Transform directory {transform_dir} not found.")
        return None

    fwd_transform = os.path.join(transform_dir, 'warp.nii.gz')
    affine_transform = os.path.join(transform_dir, 'affine.mat')
    inv_transform = os.path.join(transform_dir, 'inv_warp.nii.gz')

    if not all(os.path.exists(tf) for tf in [fwd_transform, affine_transform, inv_transform]):
        print(f"[WARNING] One or more transform files are missing for subject {subject}.")
        return None

    return {'fwdtransforms':fwd_transform, 'affine_transform': affine_transform, 'invtransforms':inv_transform}

def process_subject(subject, wd, roi_dirs):
    """
    Processes a single subject: registers T1 (in Diffussion space) to Template and applies inverse transforms to ROI masks.

    Parameters:
        subject (str): Subject ID.
        wd (str): Working directory.
        roi_dirs (list): List of ROI directories to process.
    """
    registration = load_transform_files(subject, wd)

    for roi_dir in roi_dirs:
        roi_dir_path = os.path.join(wd, roi_dir)
        if not os.path.isdir(roi_dir_path):
            print(f"[WARNING] ROI directory {roi_dir} not found. Skipping.")
            continue

        roi_files = [f for f in os.listdir(roi_dir_path) if f.endswith('.nii') or f.endswith('.nii.gz')]
        for roi_name in roi_files:
            apply_inverse_transform(subject, wd, registration, roi_dir, roi_name)


def process_wrapper(args_tuple):
    subject, wd = args_tuple
    try:
        process_subject(subject, wd, ['ROI_masks', 'Target_masks', 'Exclusion_masks', 'Stop_masks'])
        print(f"[INFO] Finished processing subject: {subject}")
    except Exception as e:
        print(f"[ERROR] Error processing subject {subject}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Register T1 images to MNI space")
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

    tasks = [(subject, args.wd) for subject in subjects]
    with ProcessPoolExecutor(max_workers=args.pool_size) as executor:
        executor.map(process_wrapper, tasks)

if __name__ == "__main__":
    main()
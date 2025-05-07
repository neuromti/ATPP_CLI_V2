#!/usr/bin/env python3

import ants
import os
import argparse
import shutil

def coregister(subject, wd):
    subject_dir = os.path.join(wd, subject)

    # check if f"b0_{subject}.nii.gz" does not exist, then check if f"b0_{subject}.nii" exists
    b0_img_path = os.path.join(subject_dir, f"b0_{subject}.nii")
    if not os.path.exists(b0_img_path):
        b0_img_path = os.path.join(subject_dir, f"b0_{subject}.nii.gz")
        if not os.path.exists(b0_img_path):
            print(f"[WARNING] b0 image not found: {b0_img_path}, skipping.")
            return
    # check if f"T1_{subject}.nii.gz" does not exist, then check if f"T1_{subject}.nii" exists
    t1_img_path = os.path.join(subject_dir, f"T1_{subject}.nii")
    if not os.path.exists(t1_img_path):
        t1_img_path = os.path.join(subject_dir, f"T1_{subject}.nii.gz")
        if not os.path.exists(t1_img_path):
            print(f"[WARNING] T1 image not found: {t1_img_path}, skipping.")
            return
        
    b0_img = ants.image_read(b0_img_path)
    t1_img = ants.image_read(t1_img_path)

    # Run registration
    reg = ants.registration(fixed=b0_img, moving=t1_img, type_of_transform='Affine')

    # Save the registered image
    output_path = os.path.join(subject_dir, f"T1_in_diffusion_space_{subject}.nii.gz")
    ants.image_write(reg['warpedmovout'], output_path)

    # Create output directory for warps
    warp_dir = os.path.join(subject_dir, "T1_to_b0")
    os.makedirs(warp_dir, exist_ok=True)

    # Save forward and inverse transforms as NIfTI files
    fwd_out_path = os.path.join(warp_dir, f"t1_to_b0_affine_{subject}.mat")
    shutil.copy(reg['fwdtransforms'][0], fwd_out_path)

def main():
    parser = argparse.ArgumentParser(description="Register T1 images to b0 space using ANTsPy.")
    parser.add_argument("--wd", required=True, help="Working directory containing subject folders")
    parser.add_argument("--sub_list", required=True, help="Text file with subject IDs (one per line)")

    args = parser.parse_args()

    with open(args.sub_list, 'r') as f:
        subjects = [line.strip() for line in f if line.strip()]

    print(f"[INFO] Found {len(subjects)} subjects.")
    for subject in subjects:
        print(f"[INFO] Processing subject: {subject} [{subjects.index(subject) + 1}/{len(subjects)}]")
        coregister(subject, args.wd)



if __name__ == "__main__":
    main()
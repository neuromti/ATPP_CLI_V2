#!/usr/bin/env python3

import os
import sys
import argparse
import ants
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed

def parse_arguments():
    parser = argparse.ArgumentParser(description="Transform ROI masks from MNI to native space using ANTsPy.")
    parser.add_argument('--wd', required=True, help='Working directory containing subject folders.')
    parser.add_argument('--sub_list', required=True, help='Text file with list of subject IDs.')
    parser.add_argument('--pool_size', type=int, default=1, help='Number of parallel processes.')
    parser.add_argument('--template', required=True, help='Path to the MNI template image.')
    return parser.parse_args()

def redirect_output_to_file(log_file_path):
    """
    Redirects stdout and stderr (including subprocesses and native code) to a log file.
    """
    # Flush before redirecting
    sys.stdout.flush()
    sys.stderr.flush()

    # Open log file
    log_file = open(log_file_path, 'w')

    # Duplicate file descriptors
    os.dup2(log_file.fileno(), sys.stdout.fileno())
    os.dup2(log_file.fileno(), sys.stderr.fileno())

    return log_file

def register_t1_to_template(subject, wd, template_path, overwrite):
    """
    Registers the subject's T1 image to template space and logs the ANTs output.
    """

    subject_dir = os.path.join(wd, subject)
    t1_image_path = os.path.join(subject_dir, f"T1_in_diffusion_space_{subject}.nii.gz")

    # check if the T1 image exists
    if not os.path.exists(t1_image_path):
        t1_image_path = os.path.join(subject_dir, f"T1_{subject}.nii.gz")
        if not os.path.exists(t1_image_path):
            t1_image_path = os.path.join(subject_dir, f"T1_{subject}.nii")
            if not os.path.exists(t1_image_path):
                print(f"[ERROR] T1 image not found for subject {subject}. Skipping registration.")
                return
    # check if the template image exists
    if not os.path.exists(template_path):
        print(f"[ERROR] Template image not found at {template_path}. Skipping registration.")
        return
    # Load the T1 image and template
    t1_image = ants.image_read(t1_image_path)
    template_image = ants.image_read(template_path)

    print(f"[INFO] Registering T1 image of subject {subject} to Template space.")

    transform_dir = os.path.join(subject_dir, "transforms_between_diffusion_and_template_space")

    if os.path.exists(transform_dir):
        if os.path.exists(os.path.join(transform_dir, 'warp.nii.gz')) and not overwrite:
            print(f"[INFO] Transform already exists for subject {subject}. Skipping registration.")
            return
        else:
            print(f"[INFO] Transform already exists for subject {subject}. Overwriting.")
            shutil.rmtree(transform_dir)
            
    os.makedirs(transform_dir, exist_ok=True)
    try:
        # Prepare subject-specific log file
        log_path = os.path.join(subject_dir, f"ants_registration_{subject}.log")
        log_file = redirect_output_to_file(log_path)
        print(f"[INFO] Starting registration for subject {subject}.")
        registration = ants.registration(fixed=template_image, moving=t1_image, type_of_transform='SyN', verbose=True)
        print(f"[INFO] Registration completed for subject {subject}.")
    finally:
        log_file.close()
        print(f"[INFO] completed registration for subject {subject}. ANT Log saved to {log_path}.")

    shutil.copy(registration['fwdtransforms'][0], os.path.join(transform_dir, 'warp.nii.gz'))
    shutil.copy(registration['fwdtransforms'][1], os.path.join(transform_dir, 'affine.mat'))
    shutil.copy(registration['invtransforms'][1], os.path.join(transform_dir, 'inv_warp.nii.gz'))

    ants.image_write(registration['warpedmovout'], os.path.join(subject_dir, f"T1_in_template_space_{subject}.nii.gz"))

    # Clean up transform files
    for tf in registration.get('invtransforms', []) + registration.get('fwdtransforms', []):
        try:
            if os.path.exists(tf):
                os.remove(tf)
                print(f"[INFO] Deleted temporary file: {tf}")
        except Exception as e:
            print(f"[WARNING] Could not delete temporary file {tf}: {e}")

def process_subject(subject, wd, template_path, overwrite):
    """
    Processes a single subject: registers T1 (in Diffussion space) to Template.

    Parameters:
        subject (str): Subject ID.
        wd (str): Working directory.
        template_path (str): Path to the Template template image.
    """
    register_t1_to_template(subject, wd, template_path, overwrite)

def process_wrapper(args_tuple):
    subject, wd, template, overwrite = args_tuple
    try:
        process_subject(subject, wd, template, overwrite)
        print(f"[INFO] Finished processing subject: {subject}")
    except Exception as e:
        print(f"[ERROR] Error processing subject {subject}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register T1 images to MNI space")
    parser.add_argument("wd", help="Working directory")
    parser.add_argument("sub_list", help="Path to file with list of subjects")
    parser.add_argument("template", help="Path to template image")
    parser.add_argument("pool_size", type=int, help="Number of parallel processes")
    parser.add_argument("overwrite", type=bool, help="Overwrite existing transforms")
    args = parser.parse_args()

    print(f"[INFO] ----- Arguments: -----")
    print(f"  Working Directory: {args.wd}")
    print(f"  Subject List File: {args.sub_list}")
    print(f"  Template Path: {args.template}")
    print(f"  Pool Size: {args.pool_size}")
    print(f"  Overwrite: {args.overwrite}")
    print(f" ------------------------------")

    with open(args.sub_list, "r") as f:
        subjects = [line.strip() for line in f if line.strip()]
    print(f"[INFO] Found {len(subjects)} subjects in the list.")

    tasks = [(subject, args.wd, args.template, args.overwrite) for subject in subjects]
    with ProcessPoolExecutor(max_workers=args.pool_size) as executor:
        executor.map(process_wrapper, tasks)
#!/usr/bin/env python3

import os
import argparse
import shutil
import nibabel as nib
import subprocess

def check_and_resample_rois_if_needed(image, template_path):
    """
    Check if the input image is aligned with the template_path.
    If not, resample it using FSL's flirt.
    """
    # get file name of image
    image_name = os.path.basename(image)
    
    # Load the input and template images
    input_img = nib.load(image)
    template_img = nib.load(template_path)

    # Check affine matrices
    if not (input_img.affine == template_img.affine).all():
        print(f"[IMPORTANT WARNING] Affine mismatch detected. Resampling {image_name} to match the moving space...")

        # copy image to the same directory with tag raw, make sure to detect both .nii and .nii.gz
        if image.endswith('.gz'):
            image_raw = os.path.join(os.path.dirname(image), f"{image_name.split('.')[0]}_raw.nii.gz")
        else:
            image_raw = os.path.join(os.path.dirname(image), f"{image_name.split('.')[0]}_raw.nii")
        shutil.copy(image, image_raw)
        try:
            subprocess.run([
                "flirt",
                "-in", input_img,
                "-ref", template_path,
                "-out", input_img,
                "-applyxfm",
                "-usesqform"
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error during resampling mask {image_name}: {e}")
            raise



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Checks input masks (image) and resamples them to template space if needed.")
    parser.add_argument("image", help="image path to be checked")
    parser.add_argument("template", help="template space path")
    args = parser.parse_args()

    print(f"[INFO] ----- Arguments: -----")
    print(f"  image: {args.image}")
    print(f"  Template Path: {args.template}")
    print(f" ------------------------------")

    check_and_resample_rois_if_needed(args.image, args.template)
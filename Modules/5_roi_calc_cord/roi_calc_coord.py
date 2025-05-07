import os
import numpy as np
import nibabel as nib
import csv
import argparse

def ROI_calc_coord(WD, SUB_LIST, type):

    Roi_dir = os.path.join(WD, type)
    # Check if the ROI directory exists
    if not os.path.exists(Roi_dir):
        print(f"[WARNING] ROI directory '{Roi_dir}' does not exist. Continuing with the next masks...")
        return

    # Read the list of subjects
    with open(SUB_LIST, 'r') as file:
        SUB = [line.strip() for line in file]

    # Open the CSV file for writing ROI volumes
    print(f"[INFO] Writing ROI volumes to CSV: {type}_volumes.csv")
    with open(os.path.join(WD, f'{type}_volumes.csv'), 'w', newline='') as sizeFile:
        writer = csv.writer(sizeFile)

        # Get the list of ROIs
        roi_list = [f for f in os.listdir(os.path.join(WD, type)) if f not in ['.', '..']]
        
        # Write the header row with ROI names as column names
        header_row = ['subject'] + [roi.split('.')[0] for roi in roi_list]
        writer.writerow(header_row)

        # Process each subject
        for subject in SUB:
            print(f"[INFO] Processing subject {subject}.")
            subject_roi_dir = os.path.join(WD, subject, type)

            if not os.path.exists(subject_roi_dir):
                print(f"[WARNING] Subject directory '{subject_roi_dir}' does not exist. Continuing with the next subject...")
                continue

            subject_roi_list = [f for f in os.listdir(subject_roi_dir) if f.endswith('.nii') or f.endswith('.nii.gz')]

            # Write the subject name
            subject_row = [subject]
            
            # Process each ROI
            for roi in subject_roi_list:
                file_path = os.path.join(subject_roi_dir, roi)
                print(f"[INFO] Processing ROI: {file_path}")

                # Load the ROI NIfTI file
                roi_img = nib.load(file_path)
                roi_data = roi_img.get_fdata()
                roi_data[np.isnan(roi_data)] = 0  # Remove NaN values

                # Count the number of nonzero voxels
                nonzero_voxels = np.count_nonzero(roi_data)
                subject_row.append(nonzero_voxels)

                # Create a new NIfTI image with the same affine and header
                new_img = nib.Nifti1Image(roi_data, roi_img.affine, roi_img.header)

                # Save the modified NIfTI file
                nib.save(new_img, file_path)

            # Write the voxel counts for the subject
            writer.writerow(subject_row)

    print("[INFO] ROI calculation and saving completed.")

def main():
    parser = argparse.ArgumentParser(description="Calculate ROI volumes.")
    parser.add_argument("wd", help="Working directory")
    parser.add_argument("sub_list", help="Path to file with list of subjects")
    parser.add_argument("type", help="Type of the ROI files (e.g., 'ROI_masks', 'Target_masks')")
    
    args = parser.parse_args()

    print(f"[INFO] ----- Arguments: -----")
    print(f"  Working Directory: {args.wd}")
    print(f"  Subject List File: {args.sub_list}")
    print(f"  ROI Type: {args.type}")
    print(f" -----------------------------")

    # Call the ROI calculation function
    ROI_calc_coord(args.wd, args.sub_list, args.type)
    print("[INFO] Volume calculation completed.")


if __name__ == "__main__":
    main()
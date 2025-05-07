#!/usr/bin/env python3

'''
ANTs-based QC Script for Nonlinear Normalization
Author: Farzin

This script performs QC on ANTs nonlinear normalization using the SyN algorithm.
It computes Jacobian determinants from deformation fields and flags problematic cases.
Also parses ANTs log files for convergence metrics.
'''

import os
import numpy as np
import pandas as pd
import argparse
from ants import create_jacobian_determinant_image, image_read
from concurrent.futures import ProcessPoolExecutor, as_completed
import re
from sklearn.ensemble import IsolationForest

def parse_ants_log(log_file_path):
    """
    Parses an ANTs registration log file and extracts:
    - Final metric value
    - Final convergence value
    - Number of iterations
    - Count of warning messages
    Returns a dictionary with these values.
    """
    final_metric = None
    final_convergence = None
    n_iterations = 0
    warning_count = 0

    metric_lines = []
    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                if "DIAGNOSTIC" in line and ',' in line:
                    if re.match(r"\s*\d+DIAGNOSTIC", line):
                        metric_lines.append(line.strip())
                elif '[WARNING]' in line:
                    warning_count += 1

        if metric_lines:
            last_line = metric_lines[-1]
            parts = last_line.split(',')
            if len(parts) >= 4:
                try:
                    final_metric = float(parts[2].strip())
                    final_convergence = float(parts[3].strip()) if parts[3].strip() != 'inf' else float('inf')
                    n_iterations = int(parts[1].strip())
                except ValueError:
                    pass
    except Exception as e:
        print(f"[WARN] Could not parse log file {log_file_path}: {e}")

    return {
        'final_metric': final_metric,
        'final_convergence': final_convergence,
        'n_iterations': n_iterations,
        'warning_count': warning_count
    }

def qc_subject(subject_id, input_dir, fixed_img_path):
    """
    Perform QC on a single subject's registration.
    Computes Jacobian determinants and parses ANTs log files.
    """
    print(f"[INFO] Processing subject {subject_id} for QC.")
    
    warp_field_path = os.path.join(input_dir, subject_id, "transforms_between_diffusion_and_template_space", "warp.nii.gz")
    log_file_path = os.path.join(input_dir, subject_id, f"ants_registration_{subject_id}.log")

    if not os.path.exists(fixed_img_path):
        raise FileNotFoundError(f"Fixed image {fixed_img_path} does not exist.")
    if not os.path.exists(warp_field_path):
        raise FileNotFoundError(f"Warp field {warp_field_path} does not exist.")

    try:
        # Compute Jacobian
        jac_img = create_jacobian_determinant_image(image_read(fixed_img_path), image_read(warp_field_path), do_log=False, geom=False)
        jac_np = jac_img.numpy()

        # Stats
        jac_mean = np.mean(jac_np)
        jac_std = np.std(jac_np)
        jac_min = np.min(jac_np)
        jac_max = np.max(jac_np)
        jac_neg_vox = np.sum(jac_np < 0)

        if os.path.exists(log_file_path):
            # Log parsing
            log_metrics = parse_ants_log(log_file_path)
        else:
            log_metrics = {
                "final_metric": None,
                "final_convergence": None,
                "n_iterations": 0,
                "warning_count": 0
            }
            print(f"[WARN] Log file {log_file_path} does not exist. Skipping log parsing.")
            
        return {
            "subject_id": subject_id,
            "jacobian_mean": jac_mean,
            "jacobian_std": jac_std,
            "jacobian_min": jac_min,
            "jacobian_max": jac_max,
            "jacobian_neg_voxels": jac_neg_vox,
            "metric_value": log_metrics.get("final_metric"),
            "convergence_value": log_metrics.get("final_convergence"),
            "n_iterations": log_metrics.get("n_iterations"),
            "warnings_in_log": log_metrics.get("warning_count"),
        }
    except Exception as e:
        print(f"[ERROR] Failed to QC process {subject_id}: {e}")
        return None

def apply_advanced_qc_flags(df):
    """
    Apply advanced QC flags based on the computed metrics.
    Flags are set based on thresholds for jacobian, metric, convergence, and warnings.
    """
    df['flag_jacobian'] = (
        (df['jacobian_min'] < 0) |
        (df['jacobian_max'] > 5) |
        (df['jacobian_mean'] < 0.5) |
        (df['jacobian_neg_voxels'] > 1000)
    ).astype(int)

    df['flag_metric'] = (df['metric_value'] < -1.0).astype(int)
    df['flag_convergence'] = (
        (df['convergence_value'] > 1e-3) |
        (df['n_iterations'] < 10)
    ).astype(int)

    df['flag_warnings'] = (df['warnings_in_log'] > 0).astype(int)

    df['n_flags'] = df[['flag_jacobian', 'flag_metric', 'flag_convergence', 'flag_warnings']].sum(axis=1)

    # Isolation Forest Outlier Detection (only on subjects with no flags)
    if df[df['n_flags'] == 0].shape[0] >= 10:  # apply only if enough clean subjects
        features = df[['jacobian_mean', 'jacobian_std', 'metric_value', 'jacobian_min', 'jacobian_max', 'convergence_value']].fillna(0)
        clf = IsolationForest(contamination=0.05, random_state=42)
        df['outlier_score'] = clf.fit_predict(features)
        df['flag_outlier'] = (df['outlier_score'] == -1).astype(int)
    else:
        df['flag_outlier'] = 0
        df['outlier_score'] = None

    return df

def main():
    parser = argparse.ArgumentParser(description="Calculate QC metrics for ANTs nonlinear normalization.")
    parser.add_argument("wd", help="Working directory")
    parser.add_argument("sub_list", help="Path to file with list of subjects")
    parser.add_argument("template", help="Path to template image")
    parser.add_argument("pool_size", type=int, help="Number of parallel processes")
    args = parser.parse_args()

    print(f"[INFO] ----- ANT Normalization QC -----")
    print(f"  Working Directory: {args.wd}")
    print(f"  Subject List File: {args.sub_list}")
    print(f"  Template Path: {args.template}")
    print(f"  Pool Size: {args.pool_size}")
    print(f" ------------------------------")

    with open(args.sub_list, "r") as f:
        subjects = [line.strip() for line in f if line.strip()]
    print(f"[INFO] Found {len(subjects)} subjects in the list.")

    results = []
    tasks = [(subject, args.wd, args.template) for subject in subjects]
    #if args.pool_size > 1:
    with ProcessPoolExecutor(max_workers=args.pool_size) as executor:
        futures = {executor.submit(qc_subject, *task): task for task in tasks}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                print(f"[INFO] Registration QC Processed subject: {result['subject_id']}")
            else:
                print(f"[ERROR] Failed to process subject: {futures[future][0]}")

    df = pd.DataFrame(results)

    if df.empty:
        print("[ERROR] No valid results to process.")
        return
    
    # Make a folder named QC_results in the wd
    qc_results_dir = os.path.join(args.wd, "QC_results")
    os.makedirs(qc_results_dir, exist_ok=True)
    # Save the DataFrame to a CSV file
    df.to_csv(os.path.join(qc_results_dir, "raw_qc_data.csv"), index=False)

    # Apply advanced QC flags
    df = apply_advanced_qc_flags(df)

    # Save the DataFrame to a CSV file
    df.to_csv(os.path.join(qc_results_dir, "registration_qc_results.csv"), index=False)

    print("QC complete. Results saved.")

if __name__ == "__main__":
    main()

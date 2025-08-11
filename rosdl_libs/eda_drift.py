# rosdl/core/eda_drift.py

import pandas as pd
import numpy as np
import os
from scipy.stats import ks_2samp, chi2_contingency

def quick_eda(df: pd.DataFrame):
    print("\n--- QUICK EDA REPORT ---")
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n")

    # Data types
    print("\nData Types:")
    print(df.dtypes.to_string())

    # Missing values
    print("\nMissing Values:")
    print(df.isnull().sum().to_string())

    # Basic statistics
    stats = df.describe(include='all').transpose()
    # Fill NaNs only for non-numeric stats
    for col in stats.columns:
        if stats[col].dtype == 'O':
            stats[col] = stats[col].fillna("-")
    stats = stats.round(2)

    print("\nBasic Statistics:")
    print(stats.to_string())

    # Unique values
    print("\nUnique Values (first 10 columns):")
    for col in df.columns[:10]:
        print(f" {col}: {df[col].nunique()} unique values")


def detect_drift(df1: pd.DataFrame, df2: pd.DataFrame):
    print("\n--- DATA DRIFT ANALYSIS ---")
    drift_report = []

    for col in df1.columns:
        if col not in df2.columns:
            continue

        # Skip if values are exactly the same
        if df1[col].equals(df2[col]):
            drift_report.append((col, "No Change", 1.0))
            continue

        # Numerical Drift: KS Test
        if np.issubdtype(df1[col].dropna().dtype, np.number):
            stat, p_val = ks_2samp(df1[col].dropna(), df2[col].dropna())
            drift_report.append((col, "Numerical", p_val))

        # Categorical Drift: Chi-Square Test
        else:
            contingency = pd.crosstab(df1[col].dropna(), df2[col].dropna())
            if contingency.shape[0] > 1 and contingency.shape[1] > 1:
                chi2, p_val, _, _ = chi2_contingency(contingency)
                drift_report.append((col, "Categorical", p_val))
            else:
                drift_report.append((col, "Categorical", 1.0))  # No variability → No drift

    # Output results
    print("\nColumn\t\tType\t\tp-value\t\tDrift Detected?")
    for col, col_type, p_val in drift_report:
        drift_flag = "YES" if p_val < 0.05 and col_type != "No Change" else "NO"
        print(f"{col:15} {col_type:12} {p_val:.4f}\t{drift_flag}")


def main():
    print("\n=== Quick EDA & Drift Analysis Tool ===\n")
    print("1. Perform Quick EDA on a single dataset")
    print("2. Compare two datasets for drift")
    choice = input("Choose an option (1/2): ").strip()

    if choice == "1":
        file_path = input("Enter CSV file path: ").strip()
        if not os.path.exists(file_path):
            print("File not found!")
            return
        df = pd.read_csv(file_path)
        quick_eda(df)

    elif choice == "2":
        file1 = input("Enter first CSV file path: ").strip()
        file2 = input("Enter second CSV file path: ").strip()

        if not os.path.exists(file1) or not os.path.exists(file2):
            print("One or both files not found!")
            return

        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)

        print("\n--- EDA for First Dataset ---")
        quick_eda(df1)

        print("\n--- EDA for Second Dataset ---")
        quick_eda(df2)

        detect_drift(df1, df2)

    else:
        print("Invalid choice!")

    def main_cli(args):
        import argparse
        parser = argparse.ArgumentParser(description="Perform EDA & data drift analysis")
        parser.add_argument("--input", required=True, help="Input dataset file")
        parser.add_argument("--report", required=True, help="Output report file")
        opts = parser.parse_args(args)
    
        # TODO: replace with your existing EDA/drift logic
        print(f"Analyzing drift for {opts.input} → Report: {opts.report}")


if __name__ == "__main__":
    main()

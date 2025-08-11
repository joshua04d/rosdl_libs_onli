import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

import pandas as pd
import numpy as np
import logging
import sys
from scipy import stats

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("csv_cleaner.log", mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

def detect_and_cast_types(df):
    logging.info("Detecting and casting data types...")
    for col in df.columns:
        if df[col].dtype == object:
            # Try datetime
            try:
                df[col] = pd.to_datetime(df[col], errors='raise')
                logging.info(f"Column '{col}' casted to datetime.")
                continue
            except Exception:
                pass
            # Try numeric
            try:
                df[col] = pd.to_numeric(df[col])
                logging.info(f"Column '{col}' casted to numeric.")
            except Exception:
                logging.info(f"Column '{col}' could not be cast to numeric.")
    return df

def find_column(df, target):
    for col in df.columns:
        if col.strip().lower() == target:
            return col
    return None

def suggest_imputation_method(df, col):
    series = df[col]
    if pd.api.types.is_datetime64_any_dtype(series):
        return 'mode'  # Dates: mode or skip
    elif pd.api.types.is_numeric_dtype(series):
        skew = series.skew()
        return 'mean' if abs(skew) < 1 else 'median'
    else:
        return 'skip'  # Text: skip

def impute_column(df, col):
    suggestion = suggest_imputation_method(df, col)
    print(f"\nColumn '{col}' has missing values.")
    print(f"Suggested imputation: {suggestion.upper()}")
    print("Options:")

    if pd.api.types.is_datetime64_any_dtype(df[col]):
        print("  mode - fill with most frequent date")
        print("  skip - drop rows with missing")
    elif pd.api.types.is_numeric_dtype(df[col]):
        print("  mean   - fill with mean")
        print("  median - fill with median")
        print("  mode   - fill with mode")
        print("  skip   - drop rows with missing")
    else:
        print("  skip   - drop rows with missing")

    choice = input(f"Choose method or press Enter to accept '{suggestion}': ").strip().lower()
    if choice == '':
        choice = suggestion

    if pd.api.types.is_datetime64_any_dtype(df[col]):
        if choice == 'mode':
            val = df[col].mode()
            if len(val) > 0:
                df[col].fillna(val[0], inplace=True)
                print(f"Imputed '{col}' with mode date: {val[0]}")
            else:
                print(f"No mode found for '{col}', no imputation done.")
        elif choice == 'skip':
            before = len(df)
            df.dropna(subset=[col], inplace=True)
            print(f"Dropped {before - len(df)} rows missing '{col}'.")
        else:
            print("Invalid choice, skipping imputation.")
    elif pd.api.types.is_numeric_dtype(df[col]):
        if choice == 'mean':
            df[col].fillna(df[col].mean(), inplace=True)
            print(f"Imputed '{col}' with mean.")
        elif choice == 'median':
            df[col].fillna(df[col].median(), inplace=True)
            print(f"Imputed '{col}' with median.")
        elif choice == 'mode':
            val = df[col].mode()
            if len(val) > 0:
                df[col].fillna(val[0], inplace=True)
                print(f"Imputed '{col}' with mode.")
            else:
                print(f"No mode found for '{col}', no imputation done.")
        elif choice == 'skip':
            before = len(df)
            df.dropna(subset=[col], inplace=True)
            print(f"Dropped {before - len(df)} rows missing '{col}'.")
        else:
            print("Invalid choice, skipping imputation.")
    else:
        # Text or other columns: only skip allowed
        if choice == 'skip':
            before = len(df)
            df.dropna(subset=[col], inplace=True)
            print(f"Dropped {before - len(df)} rows missing '{col}'.")
        else:
            print("Invalid choice, skipping imputation.")
    return df

def detect_duplicates(df):
    count = df.duplicated().sum()
    if count > 0:
        print(f"\nFound {count} duplicate rows.")
        rm = input("Remove duplicates? (y/n): ").strip().lower()
        if rm == 'y':
            df = df.drop_duplicates()
            print(f"Removed {count} duplicates.")
    return df

def generate_report(df_original, df_cleaned, dropped_rows):
    lines = []
    lines.append(f"Initial rows: {len(df_original)}")
    lines.append(f"Rows dropped: {dropped_rows}")
    lines.append(f"Final rows: {len(df_cleaned)}\n")
    lines.append("Missing values per column:")
    missing = df_cleaned.isnull().sum()
    for col in df_cleaned.columns:
        lines.append(f"  {col}: {missing[col]} missing")

    lines.append("\nSummary stats:")
    for col in df_cleaned.columns:
        s = df_cleaned[col]
        if pd.api.types.is_datetime64_any_dtype(s):
            lines.append(f"{col} - dates: min={s.min()}, max={s.max()}, unique={s.nunique()}")
        elif pd.api.types.is_numeric_dtype(s):
            lines.append(f"{col} - numeric: mean={s.mean():.2f}, median={s.median():.2f}, min={s.min()}, max={s.max()}")
        else:
            lines.append(f"{col} - text: unique={s.nunique()}, mode={s.mode().tolist()[:3]}")

    return "\n".join(lines)

def main():
    print("\n=== Simple CSV Cleaner ===\n")

    filename = input("Enter CSV filename: ").strip()
    try:
        df = pd.read_csv(filename)
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)

    print(f"\nLoaded {len(df)} rows and {df.shape[1]} columns.")

    # Save original row count
    original_rows = len(df)

    # Detect types
    df = detect_and_cast_types(df)

    # Drop rows missing 'name' or 'pid' if columns exist (case-insensitive + stripped)
    dropped_rows = 0
    for key_col in ['name', 'pid']:
        col_name = find_column(df, key_col)
        if col_name:
            before = len(df)
            df = df.dropna(subset=[col_name])
            dropped_rows += before - len(df)
        else:
            print(f"Warning: '{key_col}' column not found.")

    # Remove duplicates
    df = detect_duplicates(df)

    # Impute missing values
    missing_cols = [c for c in df.columns if df[c].isnull().any()]
    if missing_cols:
        print(f"\nColumns with missing values: {', '.join(missing_cols)}")
        for col in missing_cols:
            df = impute_column(df, col)
    else:
        print("\nNo missing values detected.")

    # Generate report
    report = generate_report(pd.read_csv(filename), df, dropped_rows)
    print("\n--- Cleaning Report ---")
    print(report)
    print("-----------------------\n")

    # Export report
    exp = input("Export report? Enter filename (.txt) or leave blank to skip: ").strip()
    if exp:
        try:
            with open(exp, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to {exp}")
        except Exception as e:
            print(f"Failed to save report: {e}")

    # Save cleaned CSV
    out = input("Enter filename to save cleaned CSV (e.g. cleaned.csv): ").strip()
    try:
        df.to_csv(out, index=False)
        print(f"Cleaned CSV saved to {out}")
    except Exception as e:
        print(f"Failed to save cleaned CSV: {e}")

    def main_cli(args):
        import argparse
        parser = argparse.ArgumentParser(description="Clean CSV files")
        parser.add_argument("--input", required=True, help="Input CSV file")
        parser.add_argument("--output", required=True, help="Output CSV file")
        opts = parser.parse_args(args)
    
        # TODO: replace with your existing CSV cleaning call
        print(f"Cleaning {opts.input} → {opts.output}")

if __name__ == "__main__":
    main()

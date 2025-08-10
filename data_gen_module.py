import sys
import os
import pandas as pd
import numpy as np
import random
import string
from datetime import datetime, timedelta
from faker import Faker # type: ignore

fake = Faker('en_IN')

# --- Helper input functions ---

def input_int(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = int(input(prompt))
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                print(f"Please enter a value between {min_val} and {max_val}.")
                continue
            return val
        except ValueError:
            print("Invalid input, please enter an integer.")

def input_float(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = float(input(prompt))
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                print(f"Please enter a value between {min_val} and {max_val}.")
                continue
            return val
        except ValueError:
            print("Invalid input, please enter a number.")

def input_choice(prompt, choices):
    choices_lower = [c.lower() for c in choices]
    while True:
        val = input(prompt).strip().lower()
        if val in choices_lower:
            return val
        print(f"Invalid choice. Please choose from {choices}.")

# --- Data generation helpers ---

def generate_int_column(min_val, max_val, n):
    return np.random.randint(min_val, max_val + 1, size=n)

def generate_float_column(min_val, max_val, n):
    return np.random.uniform(min_val, max_val, size=n).round(2)

def generate_category_column(categories, n):
    return np.random.choice(categories, size=n)

def generate_string_column(str_len, n):
    def rand_str():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=str_len))
    return [rand_str() for _ in range(n)]

def generate_realistic_name(n):
    return [fake.name() for _ in range(n)]

def generate_realistic_city(n):
    return [fake.city() for _ in range(n)]

def generate_realistic_phone(n):
    return [fake.phone_number() for _ in range(n)]

def generate_email_from_names(names):
    emails = []
    for nm in names:
        base = nm.lower().replace(' ', '.').replace("'", '').replace('-', '')
        emails.append(base + "@example.com")
    return emails

def generate_pid_column(n, existing_ids=None):
    existing_ids = existing_ids or set()
    new_ids = []
    current = max(existing_ids) + 1 if existing_ids else 10000  # start PID at 10,000
    while len(new_ids) < n:
        if current not in existing_ids:
            new_ids.append(current)
            current += 1
        else:
            current += 1
    return new_ids

def generate_date_column(start_date_str, end_date_str, n):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    delta = end_date - start_date
    dates = []
    for _ in range(n):
        random_days = random.randint(0, delta.days)
        random_date = start_date + timedelta(days=random_days)
        dates.append(random_date.strftime("%Y-%m-%d"))
    return dates

# --- Augmentation helpers ---

def fit_numeric_distributions(df, numeric_cols):
    stats = {}
    for col in numeric_cols:
        series = df[col].dropna()
        stats[col] = {
            'mean': series.mean(),
            'std': series.std() if series.std() > 0 else 1
        }
    return stats

def augment_numeric_column(col_stats, n, is_int):
    mean, std = col_stats['mean'], col_stats['std']
    samples = np.random.normal(mean, std, n)
    if is_int:
        samples = np.round(samples).astype(int)
    return samples

def augment_categorical_column(categories, n, existing_values=None):
    augmented_categories = list(categories)
    if random.random() < 0.1:  # 10% chance to add new faker word
        new_cat = fake.word().capitalize()
        if new_cat not in augmented_categories:
            augmented_categories.append(new_cat)
    if existing_values is not None and len(existing_values) > 0:
        pool = list(set(existing_values)) + augmented_categories
    else:
        pool = augmented_categories
    return np.random.choice(pool, n)

def augment_string_column(name, n):
    name_lower = name.lower()
    if 'name' in name_lower:
        return [fake.name() for _ in range(n)]
    elif 'city' in name_lower:
        return [fake.city() for _ in range(n)]
    elif 'phone' in name_lower or 'mobile' in name_lower:
        return [fake.phone_number() for _ in range(n)]
    else:
        length = 8
        return [''.join(random.choices(string.ascii_letters + string.digits, k=length)) for _ in range(n)]

# --- Main functions ---

def generate_from_schema():
    print("\nYou chose: Generate data from schema")
    n_cols = input_int("How many columns? ", min_val=1)
    schema = []
    for i in range(n_cols):
        print(f"\nDefine Column {i+1}:")
        name = input("  Column name: ").strip()
        dtype = input_choice("  Type (int, float, category, string): ", ['int', 'float', 'category', 'string'])
        col_info = {'name': name, 'type': dtype}
        if dtype == 'int':
            col_info['min'] = input_int("    Min int value: ")
            col_info['max'] = input_int("    Max int value: ", min_val=col_info['min'])
        elif dtype == 'float':
            col_info['min'] = input_float("    Min float value: ")
            col_info['max'] = input_float("    Max float value: ", min_val=col_info['min'])
        elif dtype == 'category':
            cats = input("    Categories (comma separated): ")
            cats_list = [c.strip() for c in cats.split(',') if c.strip()]
            if not cats_list:
                print("    Warning: No categories entered. Using ['A', 'B']")
                cats_list = ['A', 'B']
            col_info['categories'] = cats_list
        elif dtype == 'string':
            col_info['length'] = input_int("    String length (ignored for name/city/phone/email): ", min_val=1, max_val=100)
        schema.append(col_info)

    n_rows = input_int("\nHow many rows to generate? ", min_val=1, max_val=100000)

    data = {}
    # First generate all columns except email (handle email later)
    for col in schema:
        cname = col['name'].lower()
        if cname == 'pid':
            data[col['name']] = generate_pid_column(n_rows)
        elif col['type'] == 'int':
            data[col['name']] = generate_int_column(col['min'], col['max'], n_rows)
        elif col['type'] == 'float':
            data[col['name']] = generate_float_column(col['min'], col['max'], n_rows)
        elif col['type'] == 'category':
            data[col['name']] = generate_category_column(col['categories'], n_rows)
        elif col['type'] == 'string':
            if 'name' in cname:
                data[col['name']] = generate_realistic_name(n_rows)
            elif 'city' in cname:
                data[col['name']] = generate_realistic_city(n_rows)
            elif 'phone' in cname or 'mobile' in cname:
                data[col['name']] = generate_realistic_phone(n_rows)
            elif 'email' in cname:
                pass
            else:
                data[col['name']] = generate_string_column(col['length'], n_rows)

    # Now handle email column generation if email exists and name exists
    name_col = next((col['name'] for col in schema if 'name' in col['name'].lower()), None)
    email_col = next((col['name'] for col in schema if 'email' in col['name'].lower()), None)
    if email_col:
        if name_col and name_col in data:
            data[email_col] = generate_email_from_names(data[name_col])
        else:
            data[email_col] = [fake.email() for _ in range(n_rows)]

    df = pd.DataFrame(data)
    fname = f"synthetic_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(fname, index=False)
    print(f"\nData generated and saved as {fname}")

def augment_dataset():
    print("\nYou chose: Augment existing dataset with improved augmentation")
    path = input("Enter path to CSV dataset: ").strip()
    if not os.path.exists(path):
        print("File does not exist. Returning to main menu.")
        return
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return

    print(f"Dataset loaded with {len(df)} rows and {len(df.columns)} columns.")
    n_add = input_int("How many rows to add? ", min_val=1, max_val=100000)

    existing_pids = set()
    if 'pid' in df.columns:
        try:
            existing_pids = set(df['pid'].dropna().astype(int))
        except:
            existing_pids = set()

    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and col.lower() != 'pid']
    categorical_cols = [col for col in df.columns if pd.api.types.is_object_dtype(df[col])]

    numeric_stats = fit_numeric_distributions(df, numeric_cols)

    col_strategies = {}

    new_rows = []
    for i in range(n_add):
        new_row = {}
        for col in df.columns:
            col_lower = col.lower()
            if col_lower == 'pid':
                continue

            col_dtype = df[col].dtype

            if col not in col_strategies:
                if pd.api.types.is_numeric_dtype(col_dtype):
                    print(f"\nChoose augmentation strategy for numeric column '{col}':")
                    print("  1. Sample from fitted normal distribution")
                    print("  2. Sample existing + noise (default)")
                    strat = input_choice("Enter 1 or 2: ", ['1','2'])
                elif pd.api.types.is_object_dtype(col_dtype):
                    print(f"\nChoose augmentation strategy for categorical/string column '{col}':")
                    print("  1. Sample from existing values")
                    print("  2. Sample from existing + faker augmentation (default)")
                    strat = input_choice("Enter 1 or 2: ", ['1','2'])
                else:
                    strat = '2'
                col_strategies[col] = strat
            else:
                strat = col_strategies[col]

            if pd.api.types.is_numeric_dtype(col_dtype):
                # Force age to be int type for augmentation regardless of dtype
                is_int = True if col_lower == 'age' else pd.api.types.is_integer_dtype(col_dtype)
                if strat == '1':
                    val = augment_numeric_column(numeric_stats[col], 1, is_int)[0]
                else:
                    val_orig = df[col].sample(1).values[0]
                    if is_int:
                        noise = random.randint(-2, 2)
                        val = int(val_orig) + noise
                    else:
                        noise = np.random.normal(0, 1)
                        val = float(val_orig) + noise
                new_row[col] = val
            elif pd.api.types.is_object_dtype(col_dtype):
                existing_vals = list(df[col].dropna().unique())
                if strat == '1':
                    val = random.choice(existing_vals)
                else:
                    val = augment_categorical_column(existing_vals, 1, existing_vals)[0]
                new_row[col] = val
            else:
                new_row[col] = df[col].sample(1).values[0]

        new_rows.append(new_row)

    df_aug = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

    # Fix PID for new rows
    if 'pid' in df.columns:
        n_existing = len(df)
        n_total = len(df_aug)
        n_new = n_total - n_existing
        new_pids = generate_pid_column(n_new, existing_pids)
        df_aug.loc[n_existing:, 'pid'] = new_pids

    # Fix email based on name if both columns exist
    if 'email' in df_aug.columns and 'name' in df_aug.columns:
        names = df_aug['name'].fillna('user').astype(str).tolist()
        emails = generate_email_from_names(names)
        df_aug['email'] = emails

    fname = f"augmented_data_improved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df_aug.to_csv(fname, index=False)
    print(f"\nAugmented dataset saved as {fname}")

def parse_prompt_and_generate():
    print("\nYou chose: Generate data from prompt")
    print("Example prompt format:")
    print("  5 rows, columns: age int 20-50, gender category M/F, salary float 1000-5000, doj date 2020-01-01:2023-12-31")
    prompt = input("Enter prompt describing data to generate:\n").strip().lower()

    try:
        parts = prompt.split('columns:')
        if len(parts) != 2:
            print("Prompt must contain 'columns:' section.")
            return
        n_rows_part = parts[0].strip()
        n_rows = int(''.join(filter(str.isdigit, n_rows_part)))
        columns_part = parts[1].strip()
        cols = [c.strip() for c in columns_part.split(',')]

        schema = []
        for c in cols:
            tokens = c.split()
            if len(tokens) < 2:
                print(f"Invalid column definition: {c}")
                return
            name = tokens[0]
            dtype = tokens[1]
            col_info = {'name': name, 'type': dtype}

            if dtype == 'int' or dtype == 'float':
                if len(tokens) < 3:
                    print(f"Missing range for numeric column {name}")
                    return
                range_str = tokens[2]
                if '-' not in range_str:
                    print(f"Invalid range format for {name}")
                    return
                min_val, max_val = range_str.split('-')
                col_info['min'] = float(min_val)
                col_info['max'] = float(max_val)
                if dtype == 'int':
                    col_info['min'] = int(col_info['min'])
                    col_info['max'] = int(col_info['max'])
            elif dtype == 'category':
                if len(tokens) < 3:
                    print(f"Missing categories for {name}")
                    return
                cats = tokens[2]
                categories = [x.strip().upper() for x in cats.split('/')]
                col_info['categories'] = categories
            elif dtype == 'date':
                if len(tokens) < 3:
                    print(f"Missing date range for {name}")
                    return
                date_range = tokens[2]
                if ':' not in date_range:
                    print(f"Invalid date range format for {name}, expected start:end")
                    return
                start_date_str, end_date_str = date_range.split(':')
                col_info['start_date'] = start_date_str
                col_info['end_date'] = end_date_str
            elif dtype == 'string':
                # no extra args needed
                pass
            else:
                print(f"Unsupported type {dtype}")
                return

            schema.append(col_info)

        # Generate data per schema
        data = {}
        for col in schema:
            cname = col['name'].lower()
            if cname == 'pid':
                data[col['name']] = generate_pid_column(n_rows)
            elif col['type'] == 'int':
                data[col['name']] = generate_int_column(col['min'], col['max'], n_rows)
            elif col['type'] == 'float':
                data[col['name']] = generate_float_column(col['min'], col['max'], n_rows)
            elif col['type'] == 'category':
                data[col['name']] = generate_category_column(col['categories'], n_rows)
            elif col['type'] == 'date':
                data[col['name']] = generate_date_column(col['start_date'], col['end_date'], n_rows)
            elif col['type'] == 'string':
                if 'name' in cname:
                    data[col['name']] = generate_realistic_name(n_rows)
                elif 'city' in cname:
                    data[col['name']] = generate_realistic_city(n_rows)
                elif 'phone' in cname or 'mobile' in cname:
                    data[col['name']] = generate_realistic_phone(n_rows)
                elif 'email' in cname:
                    # generate after name
                    pass
                else:
                    data[col['name']] = generate_string_column(8, n_rows)

        # Handle email generation if both name and email exist
        name_col = next((col['name'] for col in schema if 'name' in col['name'].lower()), None)
        email_col = next((col['name'] for col in schema if 'email' in col['name'].lower()), None)
        if email_col:
            if name_col and name_col in data:
                data[email_col] = generate_email_from_names(data[name_col])
            else:
                data[email_col] = [fake.email() for _ in range(n_rows)]

        df = pd.DataFrame(data)
        fname = f"prompt_generated_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(fname, index=False)
        print(f"\nData generated and saved as {fname}")

    except Exception as e:
        print(f"Error parsing prompt or generating data: {e}")

def main_menu():
    while True:
        print("\nWelcome to SimpleSynth - Synthetic Data Generator\n")
        print("Please choose an option:")
        print("1. Generate synthetic data from schema")
        print("2. Augment existing dataset")
        print("3. Generate data from prompt")
        print("4. Exit")
        choice = input("Enter choice (1-4): ").strip()
        if choice == '1':
            generate_from_schema()
        elif choice == '2':
            augment_dataset()
        elif choice == '3':
            parse_prompt_and_generate()
        elif choice == '4':
            print("Exiting. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")

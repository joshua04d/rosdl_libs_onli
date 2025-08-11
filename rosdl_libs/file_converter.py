import pandas as pd
import yaml
import os
import sys

def xlsx_to_csv(input_path, output_path, delimiter=",", encoding="utf-8"):
    df = pd.read_excel(input_path)
    df.to_csv(output_path, index=False, sep=delimiter, encoding=encoding)
    print(f"\n✅ Converted XLSX to CSV:\n  Input: {input_path}\n  Output: {output_path}")

def csv_to_xlsx(input_path, output_path):
    df = pd.read_csv(input_path)
    df.to_excel(output_path, index=False)
    print(f"\n✅ Converted CSV to XLSX:\n  Input: {input_path}\n  Output: {output_path}")

def load_config(yaml_path):
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def get_input(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

def main():
    while True:
        print("\n--- File Converter ---")
        print("1) XLSX to CSV")
        print("2) CSV to XLSX")
        print("3) Use YAML config file")
        print("4) Exit")
        choice = get_input("Enter choice (1-4): ").strip()

        match choice:
            case "1":
                input_file = get_input("Enter XLSX input file path: ").strip()
                if not os.path.exists(input_file):
                    print("Input file does not exist. Try again.")
                    continue
                output_file = get_input("Enter CSV output file path: ").strip()
                delimiter = get_input("Enter CSV delimiter (default ','): ").strip() or ","
                encoding = get_input("Enter CSV encoding (default 'utf-8'): ").strip() or "utf-8"
                xlsx_to_csv(input_file, output_file, delimiter, encoding)

            case "2":
                input_file = get_input("Enter CSV input file path: ").strip()
                if not os.path.exists(input_file):
                    print("Input file does not exist. Try again.")
                    continue
                output_file = get_input("Enter XLSX output file path: ").strip()
                csv_to_xlsx(input_file, output_file)

            case "3":
                yaml_path = get_input("Enter YAML config file path: ").strip()
                if not os.path.exists(yaml_path):
                    print("Config file does not exist. Try again.")
                    continue
                config = load_config(yaml_path)
                conv = config.get("conversion", {})
                mode = conv.get("mode")
                input_file = conv.get("input_file")
                output_file = conv.get("output_file")
                csv_conf = conv.get("csv", {})
                delimiter = csv_conf.get("delimiter", ",")
                encoding = csv_conf.get("encoding", "utf-8")

                if not mode or not input_file or not output_file:
                    print("Config YAML missing required fields (mode, input_file, output_file).")
                    continue

                if not os.path.exists(input_file):
                    print(f"Input file does not exist: {input_file}")
                    continue

                if mode == "xlsx_to_csv":
                    xlsx_to_csv(input_file, output_file, delimiter, encoding)
                elif mode == "csv_to_xlsx":
                    csv_to_xlsx(input_file, output_file)
                else:
                    print(f"Unknown mode in config: {mode}")

            case "4":
                print("Goodbye!")
                break

            case _:
                print("Invalid choice. Please enter 1, 2, 3 or 4.")

    def main_cli(args):
        import argparse
        parser = argparse.ArgumentParser(description="Convert files between formats")
        parser.add_argument("--input", required=True, help="Input file path")
        parser.add_argument("--output", required=True, help="Output file path")
        parser.add_argument("--format", required=True, help="Output format (e.g., csv, json, parquet)")
        opts = parser.parse_args(args)
    
        # TODO: replace with your existing file conversion logic
        print(f"Converting {opts.input} → {opts.output} (format={opts.format})")

if __name__ == "__main__":
    main()

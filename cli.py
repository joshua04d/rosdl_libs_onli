#!/usr/bin/env python3
import argparse

# Import each tool
from rosdl_libs import (
    csv_cleaner,
    data_gen_module,
    eda_drift,
    file_converter,
    image_tools,
    metadata_module,
    ocr_module,
    pdf_module,
    text_utils_module
)

def main():
    parser = argparse.ArgumentParser(
        prog="rosdl",
        description="ROS Data Library CLI"
    )
    parser.add_argument(
        "tool",
        help="Tool name to run (csv, data-gen, eda, convert, image, metadata, ocr, pdf, text)"
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments for the selected tool"
    )

    args = parser.parse_args()

    # Switch-case dispatcher
    if args.tool == "csv":
        csv_cleaner.main_cli(args.args)
    elif args.tool == "data-gen":
        data_gen_module.main_cli(args.args)
    elif args.tool == "eda":
        eda_drift.main_cli(args.args)
    elif args.tool == "convert":
        file_converter.main_cli(args.args)
    elif args.tool == "image":
        image_tools.main_cli(args.args)
    elif args.tool == "metadata":
        metadata_module.main_cli(args.args)
    elif args.tool == "ocr":
        ocr_module.main_cli(args.args)
    elif args.tool == "pdf":
        pdf_module.main_cli(args.args)
    elif args.tool == "text":
        text_utils_module.main_cli(args.args)
    else:
        print(f"Unknown tool: {args.tool}")
        parser.print_help()

if __name__ == "__main__":
    main()

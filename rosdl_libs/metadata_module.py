#!/usr/bin/env python3
import os
import sys
import argparse
import datetime
import json
import csv

try:
    import magic # type: ignore
except ImportError:
    magic = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    Image = None

try:
    from mutagen import File as MutagenFile # type: ignore
except ImportError:
    MutagenFile = None


def format_timestamp(ts):
    try:
        return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return 'N/A'


def get_creation_time(filepath):
    if sys.platform.startswith('win'):
        return os.path.getctime(filepath)
    else:
        try:
            stat = os.stat(filepath)
            if hasattr(stat, 'st_birthtime'):
                return stat.st_birthtime
            else:
                return None
        except Exception:
            return None


def extract_pdf_metadata(filepath):
    if PdfReader is None:
        return {}

    metadata = {}
    try:
        reader = PdfReader(filepath)
        info = reader.metadata
        if info:
            for key in ['/Author', '/Title', '/Subject', '/Producer', '/Creator']:
                val = info.get(key)
                if val:
                    metadata[key.strip('/').lower()] = val
    except Exception:
        pass
    return metadata


def extract_image_exif(filepath):
    if Image is None:
        return {}

    exif_data = {}
    try:
        img = Image.open(filepath)
        info = img._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                exif_data[decoded] = value
    except Exception:
        pass
    return exif_data


def extract_audio_metadata(filepath):
    if MutagenFile is None:
        return {}

    audio_data = {}
    try:
        audio = MutagenFile(filepath)
        if audio:
            for key, val in audio.items():
                audio_data[key] = str(val)
    except Exception:
        pass
    return audio_data


def get_mime_type(filepath):
    if magic:
        try:
            mime = magic.from_file(filepath, mime=True)
            return mime
        except Exception:
            return None
    else:
        ext = os.path.splitext(filepath)[1].lower()
        mime_map = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.log': 'text/plain',
            '.md': 'text/markdown',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.csv': 'text/csv',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.flac': 'audio/flac',
        }
        return mime_map.get(ext, 'unknown')


def extract_metadata(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None

    stats = os.stat(filepath)
    size_bytes = stats.st_size
    ctime = get_creation_time(filepath)
    mtime = stats.st_mtime
    ctime_str = format_timestamp(ctime) if ctime else "Unavailable"
    mtime_str = format_timestamp(mtime)
    ext = os.path.splitext(filepath)[1].lower()
    mime = get_mime_type(filepath)

    metadata = {
        "filepath": filepath,
        "size_bytes": size_bytes,
        "created": ctime_str,
        "modified": mtime_str,
        "format": mime,
        "extension": ext,
    }

    if mime == 'application/pdf':
        pdf_meta = extract_pdf_metadata(filepath)
        metadata.update(pdf_meta)
    elif mime.startswith('image/') and Image is not None:
        exif = extract_image_exif(filepath)
        if exif:
            metadata["exif"] = exif
    elif mime.startswith('audio/') and MutagenFile is not None:
        audio_meta = extract_audio_metadata(filepath)
        if audio_meta:
            metadata["audio_tags"] = audio_meta

    return metadata


def print_metadata(metadata):
    if not metadata:
        return

    print(f"\nMetadata for file: {metadata['filepath']}")
    print("-" * 40)
    print(f"Size (bytes): {metadata['size_bytes']}")
    print(f"Created:     {metadata['created']}")
    print(f"Modified:    {metadata['modified']}")
    print(f"Format:      {metadata['format']} ({metadata['extension']})")

    for key in ['author', 'title', 'subject', 'producer', 'creator']:
        if key in metadata:
            print(f"{key.capitalize()}: {metadata[key]}")

    if "exif" in metadata:
        print("EXIF data (sample):")
        exif = metadata["exif"]
        for i, (k, v) in enumerate(exif.items()):
            print(f"  {k}: {v}")
            if i >= 4:
                break

    if "audio_tags" in metadata:
        print("Audio tags (sample):")
        audio_tags = metadata["audio_tags"]
        for i, (k, v) in enumerate(audio_tags.items()):
            print(f"  {k}: {v}")
            if i >= 4:
                break
    print("-" * 40)


def scan_folder(folder_path):
    metadata_list = []
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            full_path = os.path.join(root, f)
            meta = extract_metadata(full_path)
            if meta:
                metadata_list.append(meta)
    return metadata_list


def export_metadata(metadata_list, export_format, output_file):
    if export_format == 'json':
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, indent=2)
        print(f"Exported metadata to JSON file: {output_file}")
    elif export_format == 'csv':
        keys = set()
        for m in metadata_list:
            keys.update(m.keys())
        keys = sorted(keys)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for m in metadata_list:
                row = {}
                for k in keys:
                    v = m.get(k)
                    if isinstance(v, dict):
                        row[k] = json.dumps(v)
                    else:
                        row[k] = v
                writer.writerow(row)
        print(f"Exported metadata to CSV file: {output_file}")
    else:
        print(f"Unsupported export format: {export_format}")


def ask_export(metadata_list):
    response = input("Do you want to export the metadata? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        while True:
            export_format = input("Choose export format (json/csv): ").strip().lower()
            if export_format not in ['json', 'csv']:
                print("Please enter 'json' or 'csv'.")
                continue
            output_file = input(f"Enter output filename (e.g., output.{export_format}): ").strip()
            if not output_file:
                print("Filename cannot be empty.")
                continue
            try:
                export_metadata(metadata_list, export_format, output_file)
                break
            except Exception as e:
                print(f"Error exporting file: {e}")
                continue


def main():
    parser = argparse.ArgumentParser(description="Enhanced CLI File Metadata Extractor")
    parser.add_argument("path", help="File or folder path to extract metadata")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively scan folder (if path is folder)")
    parser.add_argument("-e", "--export", nargs='?', const='ask', help="Export metadata to JSON or CSV file (optionally specify format json/csv). If no format given, will ask interactively.")
    parser.add_argument("-o", "--output", help="Output file path for export (required if --export specified with format)")
    args = parser.parse_args()

    if os.path.isdir(args.path):
        if not args.recursive:
            print("Error: For folders, use --recursive to scan recursively")
            sys.exit(1)
        metadata_list = scan_folder(args.path)
        for meta in metadata_list:
            print_metadata(meta)
    else:
        meta = extract_metadata(args.path)
        print_metadata(meta)
        metadata_list = [meta] if meta else []

    if args.export:
        if args.export == 'ask':
            ask_export(metadata_list)
        else:
            # export format specified by user e.g. --export json
            if not args.output:
                print("Error: --output must be specified when exporting with format.")
                sys.exit(1)
            export_metadata(metadata_list, args.export, args.output)
    else:
        # If no export argument, ask user interactively after printing metadata
        if metadata_list:
            ask_export(metadata_list)

    def main_cli(args):
        import argparse
        parser = argparse.ArgumentParser(description="Extract metadata from files")
        parser.add_argument("--input", required=True, help="Input file path")
        parser.add_argument("--output", required=False, help="Output metadata file")
        opts = parser.parse_args(args)
    
        # TODO: replace with your existing metadata extraction logic
        print(f"Extracting metadata from {opts.input} → {opts.output or 'stdout'}")

if __name__ == "__main__":
    main()

import argparse
import os
import sys
import time
from PIL import Image

SUPPORTED_EXTS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

def check_tesseract_installed():
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except ImportError:
        print("Error: pytesseract is not installed.\nInstall it with: pip install pytesseract")
        sys.exit(1)
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract is not installed or not found in PATH.")
        print("Installation guide: https://github.com/tesseract-ocr/tesseract")
        sys.exit(1)

def extract_text_tesseract(image_path):
    import pytesseract
    pil_img = Image.open(image_path)

    config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(pil_img, config=config)
    return text.strip()

def main():
    parser = argparse.ArgumentParser(description="OCR tool using Tesseract.")
    parser.add_argument('filepath', help="Path to the image file")
    parser.add_argument('-o', '--output', help="Output text file path")

    args = parser.parse_args()

    if not os.path.isfile(args.filepath):
        print(f"Error: File '{args.filepath}' does not exist.")
        sys.exit(1)

    ext = os.path.splitext(args.filepath)[1].lower()
    if ext not in SUPPORTED_EXTS:
        print(f"Unsupported file type: {ext}. Supported types: {', '.join(SUPPORTED_EXTS)}")
        sys.exit(1)

    check_tesseract_installed()
    start = time.time()
    text = extract_text_tesseract(args.filepath)
    elapsed = time.time() - start

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\n✅ Extracted text saved to {args.output}")
        except Exception as e:
            print(f"\n❌ Failed to write to {args.output}: {e}")
    else:
        print("\n📄 Extracted Text:\n" + "-"*50)
        print(text)
        print("-"*50)

    print(f"⏱ Processed in {elapsed:.2f} seconds")

    def main_cli(args):
        import argparse
        parser = argparse.ArgumentParser(description="Run OCR on images or PDFs")
        parser.add_argument("--input", required=True, help="Input image or PDF")
        parser.add_argument("--output", required=True, help="Output text file")
        opts = parser.parse_args(args)
    
        # TODO: replace with your existing OCR logic
        print(f"Performing OCR on {opts.input} → {opts.output}")


if __name__ == "__main__":
    main()

import os
from PyPDF2 import PdfReader, PdfWriter
import shutil
import sys

try:
    import fitz  # type: ignore # PyMuPDF for PDF rendering and text extraction
except ImportError:
    fitz = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None


def split_pdf(input_pdf_path, output_dir, pages=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    reader = PdfReader(input_pdf_path)
    num_pages = len(reader.pages)
    output_files = []

    if pages is None:
        pages = [(i + 1, i + 1) for i in range(num_pages)]

    for idx, (start, end) in enumerate(pages):
        writer = PdfWriter()
        for p in range(start - 1, min(end, num_pages)):
            writer.add_page(reader.pages[p])

        out_path = os.path.join(output_dir, f"split_part_{idx + 1}.pdf")
        with open(out_path, "wb") as f_out:
            writer.write(f_out)
        output_files.append(out_path)

    return output_files


def merge_pdfs(pdf_paths, output_pdf_path):
    writer = PdfWriter()
    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_pdf_path, "wb") as f_out:
        writer.write(f_out)


def extract_text_from_pdf(input_pdf_path):
    if fitz:
        text = ""
        doc = fitz.open(input_pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    else:
        reader = PdfReader(input_pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text


def pdf_to_images(input_pdf_path, output_folder, dpi=300, img_format="png"):
    """
    Convert PDF pages to images using PyMuPDF (fitz) instead of pdf2image/Poppler.
    """
    if fitz is None:
        raise ImportError("PyMuPDF (fitz) is not installed. Run `pip install pymupdf`.")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(input_pdf_path)
    zoom = dpi / 72  # 72 dpi is default
    mat = fitz.Matrix(zoom, zoom)

    image_paths = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=mat)
        img_path = os.path.join(output_folder, f"page_{page_num + 1}.{img_format}")
        pix.save(img_path)
        image_paths.append(img_path)

    return image_paths


def ocr_image(image_path):
    if pytesseract is None:
        raise ImportError("pytesseract is not installed. Run `pip install pytesseract`.")

    img = Image.open(image_path)
    return pytesseract.image_to_string(img)


def ocr_pdf(input_pdf_path, temp_img_folder="/tmp/pdf_ocr_images", dpi=300):
    image_files = pdf_to_images(input_pdf_path, temp_img_folder, dpi=dpi)
    full_text = ""

    for img_file in image_files:
        full_text += ocr_image(img_file) + "\n\n"

    return full_text


def merge_pdfs_in_folder(input_folder, output_pdf_path):
    if not os.path.isdir(input_folder):
        raise ValueError(f"Input folder not found: {input_folder}")

    pdf_files = sorted([
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.lower().endswith(".pdf")
    ])

    if not pdf_files:
        raise ValueError(f"No PDF files found in folder: {input_folder}")

    merge_pdfs(pdf_files, output_pdf_path)


def check_tesseract_installed():
    if shutil.which("tesseract") is None:
        print("\nERROR: Tesseract OCR is not installed or not found in your system PATH.")
        print("Tesseract is required for OCR functions.")
        print("\nInstall Tesseract:")
        print("Windows:")
        print("  Download installer from https://github.com/tesseract-ocr/tesseract/wiki")
        print("  and add the installation folder to your PATH.")
        print("\nLinux (Debian/Ubuntu):")
        print("  sudo apt install tesseract-ocr")
        print("\nmacOS (using Homebrew):")
        print("  brew install tesseract\n")
        sys.exit(1)

    def main_cli(args):
        import argparse
        parser = argparse.ArgumentParser(description="PDF processing tools")
        parser.add_argument("--operation", required=True, help="merge, split, extract-text, etc.")
        parser.add_argument("--inputs", nargs="+", help="List of input PDF files")
        parser.add_argument("--output", required=True, help="Output PDF or text file")
        opts = parser.parse_args(args)
    
        # TODO: replace with your existing PDF logic
        print(f"PDF {opts.operation} on {opts.inputs} → {opts.output}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pdf_module.py <command> <pdf_path_or_folder> [output_dir_or_pdf]")
        print("Commands:")
        print("  split <pdf_path> [output_folder]")
        print("  merge <output_pdf> <comma_separated_pdf_list>")
        print("  merge_folder <input_folder> <output_pdf>")
        print("  extract_text <pdf_path>")
        print("  pdf2img <pdf_path> [output_folder]")
        print("  ocr <pdf_path> [temp_image_folder]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    # Only these commands have input_path at argv[2]
    if cmd in ["split", "extract_text", "pdf2img", "ocr"]:
        input_path = sys.argv[2]

    if cmd == "split":
        outdir = sys.argv[3] if len(sys.argv) > 3 else "./pdf_splits"
        split_files = split_pdf(input_path, outdir)
        print("Split files:", split_files)

    elif cmd == "merge":
        if len(sys.argv) < 4:
            print("Provide a comma-separated list of PDFs to merge as the 3rd argument")
            sys.exit(1)
        output_pdf = sys.argv[2]
        pdf_list = sys.argv[3].split(",")
        merge_pdfs(pdf_list, output_pdf)
        print(f"Merged {pdf_list} into {output_pdf}")

    elif cmd == "merge_folder":
        if len(sys.argv) < 4:
            print("Usage: python pdf_module.py merge_folder <input_folder> <output_pdf>")
            sys.exit(1)
        input_folder = sys.argv[2]
        output_pdf = sys.argv[3]
        merge_pdfs_in_folder(input_folder, output_pdf)
        print(f"Merged all PDFs from '{input_folder}' into '{output_pdf}'")

    elif cmd == "extract_text":
        print(extract_text_from_pdf(input_path))

    elif cmd == "pdf2img":
        outdir = sys.argv[3] if len(sys.argv) > 3 else "./pdf_images"
        imgs = pdf_to_images(input_path, outdir)
        print("Saved images:", imgs)

    elif cmd == "ocr":
        check_tesseract_installed()
        outdir = sys.argv[3] if len(sys.argv) > 3 else "/tmp/pdf_ocr_images"
        print(ocr_pdf(input_path, temp_img_folder=outdir))

    else:
        print(f"Unknown command: {cmd}")


import os
import shutil
import tempfile
from PyPDF2 import PdfReader, PdfWriter

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None


def split_pdf(input_pdf_path, output_file_base):
    reader = PdfReader(input_pdf_path)
    num_pages = len(reader.pages)
    output_files = []
    for i in range(num_pages):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        base, ext = os.path.splitext(output_file_base)
        out_path = f"{base}_page{i+1}{ext or '.pdf'}"
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
        return "".join(page.extract_text() or "" for page in reader.pages)


def pdf_to_images(input_pdf_path, output_folder, dpi=300, img_format="png"):
    if fitz is None:
        raise ImportError("PyMuPDF (fitz) is not installed. Run `pip install pymupdf`.")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    doc = fitz.open(input_pdf_path)
    zoom = dpi / 72
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


def ocr_pdf(input_pdf_path, dpi=300):
    if shutil.which("tesseract") is None:
        raise RuntimeError("Tesseract OCR not installed or not found in PATH.")
    temp_img_folder = tempfile.mkdtemp(prefix="pdf_ocr_")
    try:
        image_files = pdf_to_images(input_pdf_path, temp_img_folder, dpi=dpi)
        return "\n\n".join(ocr_image(img_file) for img_file in image_files)
    finally:
        shutil.rmtree(temp_img_folder, ignore_errors=True)


def merge_pdfs_in_folder(input_folder, output_pdf_path):
    pdf_files = sorted([
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.lower().endswith(".pdf")
    ])
    if not pdf_files:
        raise ValueError(f"No PDF files found in folder: {input_folder}")
    merge_pdfs(pdf_files, output_pdf_path)

import os
import re
import string
from typing import List

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# For reading docx and pdf
try:
    import docx
except ImportError:
    docx = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# Download nltk resources if needed
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class TextUtilities:
    def __init__(self, language: str = 'english'):
        self.stop_words = set(stopwords.words(language))
        self.stemmer = PorterStemmer()

    def clean_text(self, text: str, remove_stopwords: bool = True) -> str:
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        if remove_stopwords:
            words = word_tokenize(text)
            words = [w for w in words if w not in self.stop_words]
            text = ' '.join(words)
        return text

    def tokenize(self, text: str) -> List[str]:
        return word_tokenize(text)

    def stem_words(self, words: List[str]) -> List[str]:
        return [self.stemmer.stem(word) for word in words]

    def extract_keywords(self, documents: List[str], top_k: int = 10) -> List[str]:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=top_k)
        X = vectorizer.fit_transform(documents)
        return vectorizer.get_feature_names_out().tolist()

def read_txt_file(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def read_docx_file(filepath: str) -> str:
    if not docx:
        print("python-docx is not installed. Install it with: pip install python-docx")
        return ""
    doc = docx.Document(filepath)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def read_pdf_file(filepath: str) -> str:
    if not PyPDF2:
        print("PyPDF2 is not installed. Install it with: pip install PyPDF2")
        return ""
    text = []
    with open(filepath, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text.append(page.extract_text() or '')
    return '\n'.join(text)

def get_text_from_user() -> str:
    print("Choose input method:")
    print("1 - Type text manually")
    print("2 - Import from a .txt file")
    print("3 - Import from a .docx file")
    print("4 - Import from a .pdf file")
    choice = input("Enter choice (1/2/3/4): ").strip()

    if choice == '1':
        print("Type your text below (end with an empty line):")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        return '\n'.join(lines)

    elif choice in {'2', '3', '4'}:
        filepath = input("Enter full file path: ").strip()
        if not os.path.isfile(filepath):
            print("File does not exist.")
            return ""
        ext = filepath.lower().split('.')[-1]
        if choice == '2' and ext == 'txt':
            return read_txt_file(filepath)
        elif choice == '3' and ext == 'docx':
            return read_docx_file(filepath)
        elif choice == '4' and ext == 'pdf':
            return read_pdf_file(filepath)
        else:
            print(f"File extension mismatch or unsupported for choice {choice}.")
            return ""
    else:
        print("Invalid choice.")
        return ""

def main():
    tu = TextUtilities()

    text = get_text_from_user()
    if not text:
        print("No input text provided. Exiting.")
        return

    print("\n--- Original Text ---")
    print(text)

    cleaned = tu.clean_text(text)
    print("\n--- Cleaned Text ---")
    print(cleaned)

    tokens = tu.tokenize(cleaned)
    print("\n--- Tokens ---")
    print(tokens)

    stemmed = tu.stem_words(tokens)
    print("\n--- Stemmed Tokens ---")
    print(stemmed)

    # For keyword extraction, using only one document (the input text)
    keywords = tu.extract_keywords([cleaned], top_k=10)
    print("\n--- Top Keywords ---")
    print(keywords)

    def main_cli(args):
        import argparse
        parser = argparse.ArgumentParser(description="Text processing utilities")
        parser.add_argument("--input", required=True, help="Input text file")
        parser.add_argument("--output", required=True, help="Output text file")
        parser.add_argument("--operation", required=True, help="clean, tokenize, summarize, etc.")
        opts = parser.parse_args(args)
    
        # TODO: replace with your existing text utility logic
        print(f"Processing text {opts.input} → {opts.output} (operation={opts.operation})")

if __name__ == '__main__':
    main()

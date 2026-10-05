import pymupdf

def extract_text_from_pdf(file_path):
    document = pymupdf.open(file_path)

    text = ""

    for page in document:
        text = text + page.get_text() + "\n"

    return text
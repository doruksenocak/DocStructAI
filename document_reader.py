import pymupdf
import pytesseract
from PIL import Image, ImageEnhance
from pathlib import Path

def preprocess_image(image: Image.Image) -> Image.Image:

    image = image.convert("L")


    image = image.resize(
        (image.width * 2, image.height * 2),
        Image.Resampling.LANCZOS
    )


    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    return image

def extract_text_from_pdf(file_path):
    document = pymupdf.open(file_path)
    text = ""

    for page in document:
        page_text = page.get_text().strip()

        if len(page_text) >= 50:
            text += page_text + "\n"

        else:
            pixmap = page.get_pixmap(dpi=300)

            image = Image.frombytes(
                "RGB",
                [pixmap.width, pixmap.height],
                pixmap.samples
            )

            ocr_text = pytesseract.image_to_string(
                image,
                config="--psm 6"
            )

            text += ocr_text + "\n"

    return text


def extract_text_from_image(file_path):
    image = Image.open(file_path)

    image = preprocess_image(image)

    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    return text

def extract_text(file_path):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension in {".jpg", ".jpeg", ".png"}:
        return extract_text_from_image(file_path)

    raise ValueError(f"Unsupported file type: {extension}")
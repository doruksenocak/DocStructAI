from pdf_reader import extract_text_from_pdf
from document_classifier import classify_document
from ai_extractor import extract_structured_data
from models import SCHEMA_MAP


def process_document(file_path: str):
    text = extract_text_from_pdf(file_path)

    document_type = classify_document(text)

    if document_type.value not in SCHEMA_MAP:
        raise ValueError(
            f"Unsupported document type: {document_type.value}"
        )

    schema = SCHEMA_MAP[document_type.value]

    result = extract_structured_data(text, schema)

    return result
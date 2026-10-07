from document_reader import extract_text
from document_classifier import classify_document
from ai_extractor import extract_structured_data
from custom_extractor import create_custom_schema
from models import SCHEMA_MAP


def process_document(file_path: str, custom_fields: list[str] | None = None):
    text = extract_text(file_path)

    document_type = classify_document(text)

    if document_type.value in SCHEMA_MAP:
        schema = SCHEMA_MAP[document_type.value]

    elif custom_fields:
        schema = create_custom_schema(custom_fields)

    else:
        raise ValueError(
            "Unknown document type and no custom fields were provided."
        )

    data = extract_structured_data(text, schema)

    return document_type, data
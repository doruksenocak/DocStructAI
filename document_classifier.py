from enum import Enum

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()

client = OpenAI()


class DocumentType(str, Enum):
    CV = "cv"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    PURCHASE_ORDER = "purchase order"
    CONTRACT = "contract"
    BANK_STATEMENT = "bank statement"
    UNKNOWN = "unknown"


class ClassificationResult(BaseModel):
    document_type: DocumentType


def classify_document(text: str) -> DocumentType:
    if not text.strip():
        raise ValueError("Cannot classify a document with no readable text.")

    response = client.responses.parse(
        model="gpt-6-luna",
        input=[
            {
                "role": "system",
                "content": """
Classify the provided document.

Possible document types:
- cv
- invoice
- purchase order
- receipt
- contract
- bank statement
- unknown

Return unknown if the document does not clearly belong to one
of the supported document types.
"""
            },
            {
                "role": "user",
                "content": text
            }
        ],
        text_format=ClassificationResult,
    )

    return response.output_parsed.document_type

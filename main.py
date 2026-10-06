from document_processor import process_document

result = process_document(
    "input/dummy.pdf",
    custom_fields=[

    ]
)

print(result.model_dump_json(indent=2))
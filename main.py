from document_processor import process_document

result = process_document("input/bank_statement.png")

print(result.model_dump_json(indent=2))
from document_processor import process_document


file_path = "input/contract.pdf"

result = process_document(file_path)

print(result.model_dump_json(indent=2))
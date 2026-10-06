from document_reader import extract_text
from ai_extractor import extract_structured_data
from models import BankStatementData
from validator import validate_bank_statement


text = extract_text("input/bank_statement_img.png")

statement = extract_structured_data(text, BankStatementData)

print("EXTRACTED:")
print(statement.model_dump_json(indent=2))

result = validate_bank_statement(statement)

print("\nVALIDATION:")
print(result.model_dump_json(indent=2))
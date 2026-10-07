from document_processor import process_document
from exporter import export_to_json, export_to_excel


result = process_document("input/bank_statement.png")

export_to_json(result, "output/bank_statement.json")

export_to_excel(result,"output/bank_statement.xlsx")

print("Json export completed.")
print("Excel export completed.")
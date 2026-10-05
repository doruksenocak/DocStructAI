from pdf_reader import extract_text_from_pdf
from ai_extractor import extract_cv_data


text = extract_text_from_pdf("input/sample.pdf")

cv_data = extract_cv_data(text)

with open("output/cv_data.json", "w", encoding="utf-8") as file:
    file.write(cv_data.model_dump_json(indent=2))

print("Structured data saved to output/cv_data.json")
# DocStructAI

### AI-Powered Document Processing, Structured Data Extraction & Validation

DocStructAI is a full-stack, AI-powered document processing platform that converts unstructured information from PDF and image files into organized, machine-readable data.

The application supports six common document categories: **CVs, invoices, receipts, purchase orders, contracts, and bank statements**.

Users can upload documents through a React-based web interface, where DocStructAI automatically classifies the document, extracts its contents using PDF parsing or OCR, and leverages the OpenAI API to transform the information into structured data.

**Beyond extraction, DocStructAI includes an automated validation layer designed to identify potential discrepancies, inconsistencies, and missing or questionable information in the extracted results.** This helps users identify information that may require manual review rather than relying blindly on AI-generated output.

The application displays extracted information alongside validation feedback, allowing users to inspect the results before exporting them as **JSON, CSV, or XLSX (Microsoft Excel)** files.

Processed documents are also stored in a SQLite database, enabling users to revisit previous extraction results.

## Key Features

- **Multi-format document processing:** Supports PDF, PNG, JPG, and JPEG files.
- **Automatic document classification:** Recognizes CVs, invoices, receipts, purchase orders, contracts, and bank statements.
- **PDF parsing and OCR:** Extracts textual information from digital documents and image-based files using PyMuPDF and Tesseract OCR.
- **AI-powered data extraction:** Uses the OpenAI API to interpret document contents and generate structured, document-specific information.
- **Automated extraction validation:** Checks extracted information for potential discrepancies, inconsistencies, missing fields, and questionable values, highlighting issues that may require manual review.
- **Validation feedback:** Displays validation status and identified issues alongside the extracted data.
- **Interactive React interface:** Provides a user-friendly environment for uploading documents, reviewing results, and managing processed files.
- **Multiple export formats:** Exports structured information as JSON, CSV, or XLSX files compatible with Microsoft Excel.
- **Persistent document history:** Stores processed results using SQLite and SQLAlchemy, allowing users to revisit or delete previous records.
- **Dockerized full-stack application:** Uses Docker Compose to run the React/Nginx frontend and Python/FastAPI backend together.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, JavaScript, Vite, CSS |
| Backend | Python, FastAPI, Pydantic |
| AI Processing | OpenAI API |
| PDF & Image Processing | PyMuPDF, Tesseract OCR, Pillow |
| Data Validation | Custom Python validation logic |
| Database | SQLite, SQLAlchemy |
| Export Formats | JSON, CSV, XLSX |
| Excel Generation Library | openpyxl |
| Containerization | Docker, Docker Compose, Nginx |

## Document Processing Workflow

1. **Document Upload:** The user uploads a supported PDF or image file.
2. **Text Extraction:** The application extracts textual content through PDF parsing or OCR.
3. **Document Classification:** The system identifies the document category.
4. **AI-Powered Extraction:** The OpenAI API transforms the unstructured content into document-specific structured fields.
5. **Automated Validation:** DocStructAI evaluates the extracted information, identifies potential discrepancies or inconsistencies, and generates validation feedback.
6. **Result Visualization:** The extracted fields and validation results are displayed in the React interface.
7. **Data Export:** The user can download the structured information as JSON, CSV, or XLSX.
8. **Document History:** Processed results are saved in SQLite for later retrieval.
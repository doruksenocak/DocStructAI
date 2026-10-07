from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import shutil

from document_processor import process_document
from validator import validate_document


app = FastAPI(
    title="DocStructAI API"
)


@app.get("/")
def home():
    return {
        "message": "DocStructAI API is running"
    }


@app.post("/process")
async def process_uploaded_document(
    file: UploadFile = File(...)
):
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    temp_path = temp_dir / file.filename

    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = process_document(str(temp_path))

    validation = validate_document(result)

    temp_path.unlink()

    return {
        "filename": file.filename,
        "data": result.model_dump(),
        "validation": validation.model_dump()
    }
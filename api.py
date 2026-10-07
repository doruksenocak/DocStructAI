from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4
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
    extension = Path(file.filename).suffix.lower()

    if extension not in {".pdf", ".png", ".jpg", ".jpeg"}:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
        )

    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    temp_path = temp_dir / f"{uuid4()}{extension}"

    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = process_document(str(temp_path))
        validation = validate_document(result)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    finally:
        temp_path.unlink(missing_ok=True)

    return {
        "filename": file.filename,
        "data": result.model_dump(),
        "validation": validation.model_dump()
    }
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4
import shutil
from document_processor import process_document
from validator import validate_document
import json
from database import SessionLocal, ProcessedDocument
from typing import Annotated
from pydantic import WithJsonSchema

BinaryUploadFile = Annotated[
    UploadFile,
    WithJsonSchema({
        "type": "string",
        "format": "binary"
    })
]


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
        document_type, result = process_document(str(temp_path))
        validation = validate_document(result)

        db = SessionLocal()

        try:
            document = ProcessedDocument(
                filename=file.filename,
                document_type=document_type.value,
                data=json.dumps(result.model_dump())
            )

            db.add(document)
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

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


@app.get("/documents")
def get_documents():
    db = SessionLocal()

    try:
        documents = db.query(ProcessedDocument).all()

        return [
            {
                "id": document.id,
                "filename": document.filename,
                "document_type": document.document_type,
                "data": json.loads(document.data)
            }
            for document in documents
        ]

    finally:
        db.close()


@app.get("/documents/{document_id}")
def get_document(document_id: int):
    db = SessionLocal()

    try:
        document = db.get(ProcessedDocument, document_id)

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        return {
            "id": document.id,
            "filename": document.filename,
            "document_type": document.document_type,
            "data": json.loads(document.data)
        }

    finally:
        db.close()



@app.delete("/documents/{document_id}")
def delete_document(document_id: int):
    db = SessionLocal()

    try:
        document = db.get(ProcessedDocument, document_id)

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        db.delete(document)
        db.commit()

        return {
            "message": "Document deleted successfully",
            "id": document_id
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()



@app.post("/process-batch")
async def process_batch(
    files: list[BinaryUploadFile] = File(...)
):
    results = []

    for file in files:
        extension = Path(file.filename).suffix.lower()

        if extension not in {".pdf", ".png", ".jpg", ".jpeg"}:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": f"Unsupported file type: {extension}"
            })
            continue

        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)

        temp_path = temp_dir / f"{uuid4()}{extension}"

        try:
            with temp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            document_type, result = process_document(str(temp_path))
            validation = validate_document(result)

            db = SessionLocal()

            try:
                document = ProcessedDocument(
                    filename=file.filename,
                    document_type=document_type.value,
                    data=json.dumps(result.model_dump())
                )

                db.add(document)
                db.commit()

                document_id = document.id

            except Exception:
                db.rollback()
                raise

            finally:
                db.close()

            results.append({
                "filename": file.filename,
                "success": True,
                "id": document_id,
                "document_type": document_type.value,
                "data": result.model_dump(),
                "validation": validation.model_dump()
            })

        except Exception as error:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(error)
            })

        finally:
            temp_path.unlink(missing_ok=True)

    return {
        "total": len(files),
        "successful": sum(1 for result in results if result["success"]),
        "failed": sum(1 for result in results if not result["success"]),
        "results": results
    }
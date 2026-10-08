from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pathlib import Path
from uuid import uuid4
import shutil
from document_processor import process_document
from validator import validate_document
import json
from database import SessionLocal, ProcessedDocument
from typing import Annotated
from pydantic import WithJsonSchema
from fastapi.middleware.cors import CORSMiddleware
from exporter import export_to_json, export_to_excel, export_to_csv
from fastapi.responses import FileResponse
from models import SCHEMA_MAP
from starlette.background import BackgroundTask


BinaryUploadFile = Annotated[
    UploadFile,
    WithJsonSchema({
        "type": "string",
        "format": "binary"
    })
]


app = FastAPI(title="DocStructAI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "DocStructAI API is running"
    }


@app.post("/process")
async def process_uploaded_document(
    file: UploadFile = File(...),
    export_format: str = Form("json")
):
    print("Export format:", export_format)
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
            document_id = document.id

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
        "id": document_id,
        "filename": file.filename,
        "document_type": document_type.value,
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


def cleanup_csv_export(zip_path, csv_dir):
    Path(zip_path).unlink(missing_ok=True)
    shutil.rmtree(csv_dir, ignore_errors=True)

@app.get("/documents/{document_id}/export")
def export_document(document_id: int, format: str = "json"):
    db = SessionLocal()

    try:
        document = db.get(ProcessedDocument, document_id)

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        if document.document_type not in SCHEMA_MAP:
            raise HTTPException(
                status_code=400,
                detail="Unsupported document type"
            )

        schema = SCHEMA_MAP[document.document_type]

        document_data = json.loads(document.data)

        data = schema(**document_data)

        output_dir = Path("temp")
        output_dir.mkdir(exist_ok=True)

        if format == "json":
            output_path = output_dir / f"document_{document_id}.json"
            export_to_json(data, str(output_path))

            return FileResponse(
                path=output_path,
                filename=f"document_{document_id}.json",
                media_type="application/json",
                background=BackgroundTask(output_path.unlink)
            )

        if format == "xlsx":
            output_path = output_dir / f"document_{document_id}.xlsx"
            export_to_excel(data, str(output_path))

            return FileResponse(
                path=output_path,
                filename=f"document_{document_id}.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                background=BackgroundTask(output_path.unlink)
            )

        if format == "csv":
            csv_dir = output_dir / f"document_{document_id}_csv"

            export_to_csv(
                data,
                str(csv_dir),
                f"document_{document_id}"
            )

            zip_path = shutil.make_archive(
                str(csv_dir),
                "zip",
                csv_dir
            )

            return FileResponse(
                path=zip_path,
                filename=f"document_{document_id}_csv.zip",
                media_type="application/zip",
                background=BackgroundTask(
                    cleanup_csv_export,
                    zip_path,
                    csv_dir
                )
            )

        raise HTTPException(
            status_code=400,
            detail="Unsupported export format"
        )

    finally:
        db.close()
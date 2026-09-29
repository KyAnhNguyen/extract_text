import json
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.workers.batch_worker import BatchWorker


router = APIRouter(prefix="/documents", tags=["documents"])
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")


@router.post("/batch")
def process_batch(
    files: list[UploadFile] = File(...),
    batch_size: int = Query(default=10, ge=1)
):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least one file is required"
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    file_paths = []
    original_names = {}

    for upload in files:
        original_name = Path(upload.filename or "").name
        if not original_name:
            raise HTTPException(
                status_code=400,
                detail="Every file must have a name"
            )

        extension = Path(original_name).suffix.lower()
        stored_path = UPLOAD_DIR / f"{uuid4().hex}{extension}"

        with stored_path.open("wb") as destination:
            shutil.copyfileobj(upload.file, destination)

        file_paths.append(str(stored_path))
        original_names[stored_path.name] = original_name

    report = BatchWorker(batch_size=batch_size).run(file_paths)
    response_results = []

    for result in report["results"]:
        original_name = original_names.get(
            result["file_name"],
            result["file_name"]
        )
        result["file_name"] = original_name

        output_path = OUTPUT_DIR / f"{uuid4().hex}.json"
        document = {
            key: value
            for key, value in result.items()
            if key not in {"status", "attempt"}
        }
        with output_path.open("w", encoding="utf-8") as output_file:
            json.dump(document, output_file, ensure_ascii=False, indent=2)

        response_results.append({
            "file_name": original_name,
            "status": result["status"],
            "attempt": result["attempt"],
            "output_file": str(output_path)
        })

    errors = []
    for error in report["errors"]:
        error["file_name"] = original_names.get(
            error["file_name"],
            error["file_name"]
        )
        errors.append(error)

    return {
        "status": report["status"],
        "total": report["total"],
        "succeeded": report["succeeded"],
        "failed": report["failed"],
        "results": response_results,
        "errors": errors
    }
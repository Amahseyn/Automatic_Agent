from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.schemas.dataset import DatasetResponse, FieldMapping
from app.crud.dataset import fetch_imported_datasets, import_dataset_from_file
from app.database.session import get_db
from fastapi import Form


router = APIRouter(prefix="/dataset")
@router.get("/view/")
def get_imported_datasets(db: Session = Depends(get_db)):
    datasets = fetch_imported_datasets(db)
    return {"datasets": datasets}

@router.post("/file/", response_model=DatasetResponse)
def import_from_file(
    file: UploadFile = File(...),
    name: str = "Uploaded Dataset",
    table_name: str = "custom_data",
    mappings: FieldMapping = Depends(FieldMapping.as_form),
    db: Session = Depends(get_db)
):
    try:
        with open(f"/tmp/{file.filename}", "wb") as f:
            f.write(file.file.read())

        return import_dataset_from_file(
            db,
            f"/tmp/{file.filename}",
            name,
            table_name,
            
            mappings=mappings.mappings,
            skip_columns=mappings.skip_columns
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
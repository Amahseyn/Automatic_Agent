import json
from fastapi import Form
from pydantic import BaseModel
from typing import Dict, List, Optional

class DatasetBase(BaseModel):
    name: str
    source_type: str
    table_name: str

class DatasetCreate(BaseModel):
        name: str
        source_type: str
        table_name: str
        agentcolumns: Optional[List[str]] = None

        class Config:
            from_attributes = True
class DatasetResponse(DatasetBase):
    id: int

    class Config:
        from_attributes = True

class FieldMapping(BaseModel):
    mappings: Optional[Dict[str, str]] = None
    skip_columns: Optional[List[str]] = []
    agentcolumns: Optional[List[str]] = []  # <-- New field added

    @classmethod
    def as_form(
        cls,
        mappings: Optional[str] = Form(default="{}"),  # JSON string
        skip_columns: Optional[str] = Form(default="[]"),  # JSON string
        agentcolumns: Optional[str] = Form(default="[]")  # JSON string  <-- New param
    ):
        try:
            mappings_dict = json.loads(mappings) if mappings else {}
            skip_columns_list = json.loads(skip_columns) if skip_columns else []
            agentcolumns_list = json.loads(agentcolumns) if agentcolumns else []  # <-- New parse
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        return cls(
            mappings=mappings_dict,
            skip_columns=skip_columns_list,
            agentcolumns=agentcolumns_list  # <-- Pass to model
        )
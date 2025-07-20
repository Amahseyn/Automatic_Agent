from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.session import Base
from sqlalchemy.dialects.postgresql import JSON  # or use Text/JSON string if not using PostgreSQL

class ImportedDataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    source_type = Column(String)  # csv/excel/json/database
    table_name = Column(String, unique=True, nullable=False)
    #owner_id = Column(Integer, ForeignKey("users.id"))
    agentcolumns = Column(JSON, nullable=True)
    faiss_index_path = Column(String)
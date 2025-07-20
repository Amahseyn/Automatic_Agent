# app/main.py

from fastapi import FastAPI
from app.api import datasetroute
from app.core.config import settings
from app.database.session import engine
from fastapi.middleware.cors import CORSMiddleware



# Import models so Base has them before creating tables
from app.models import dataset
from app.models.dataset import Dataset
app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(datasetroute.router, prefix="/dataset/v1", tags=["Dataset"])


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}


# -----------------------------
# Create DB tables on startup
# -----------------------------
@app.on_event("startup")
def initialize_database():
    from sqlalchemy.ext.declarative import declarative_base
    from app.database.session import Base
    Base.metadata.create_all(bind=engine)

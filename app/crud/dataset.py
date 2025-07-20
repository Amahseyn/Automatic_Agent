from sqlalchemy.orm import Session
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetCreate

from app.utils.db_loader import create_table_from_df, load_file_to_dataframe, load_table_to_dataframe

from app.utils.db_loader import get_db_table_columns
from app.database.session import engine
from sqlalchemy import Table, MetaData, select
from sqlalchemy.exc import NoSuchTableError
# def preview_file_columns(file_path: str) -> list:
#     return get_file_columns(file_path)

def fetch_imported_datasets(db: Session):
    datasets = db.query(Dataset).all()
    metadata = MetaData()
    results = []

    for dataset in datasets:
        table_name = dataset.table_name
        try:
            # Reflect the dataset's table
            table = Table(table_name, metadata, autoload_with=db.bind)
            
            # Get column names
            columns = [col.name for col in table.columns]
            
            # Query two sample rows
            query = select(table).limit(2)
            samples = db.execute(query).fetchall()
            
            # Convert sample rows to list of dicts
            sample_data = [dict(row._mapping) for row in samples]

            results.append({
                "dataset": dataset,
                "columns": columns,
                "samples": sample_data
            })
        except NoSuchTableError:
            # Handle case where table does not exist
            results.append({
                "dataset": dataset,
                "columns": [],
                "samples": []
            })

    return results
def preview_db_columns(db_url: str, table_name: str) -> list:
    return get_db_table_columns(db_url, table_name)

def import_dataset_from_file(
    db: Session,
    file_path: str,
    name: str,
    table_name: str,

    mappings: dict = None,
    agentcolumns: list = None,   # Whitelist: keep these
    skip_columns: list = None     # Blacklist: drop these (if agentcolumns not given)
):
    df = load_file_to_dataframe(file_path)

    # Step 1: Apply column renaming
    if mappings:
        df.rename(columns=mappings, inplace=True)

    # Step 2: Decide which columns to keep
    if agentcolumns:
        valid_agentcolumns = [col for col in agentcolumns if col in df.columns]
        if not valid_agentcolumns:
            raise ValueError("None of the provided agentcolumns exist in the dataset.")
        df = df[valid_agentcolumns]
    if skip_columns:
        # Drop skipped columns if no agentcolumns are provided
        cols_to_drop = [col for col in skip_columns if col in df.columns]
        df = df.drop(columns=cols_to_drop)

    # Step 3: Create table from filtered DataFrame
    create_table_from_df(df, table_name)

    # Step 4: Save dataset metadata
    dataset = DatasetCreate(
        name=name,
        source_type="file",
        table_name=table_name,
        agentcolumns=valid_agentcolumns if agentcolumns else list(df.columns),
        # You can store skip_columns too if needed — see below
    )

    db_dataset = Dataset(**dataset.model_dump())
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

# def edit_dataset(
#     db: Session,
#     dataset_id: int,
#     new_name: str = None,
#     new_agentcolumns: list = None,
#     new_mappings: dict = None  # Currently unused, can be removed if not needed
# ):
#     db_dataset = db.query(ImportedDataset).filter(ImportedDataset.id == dataset_id).first()
#     if not db_dataset:
#         raise ValueError("Dataset not found")

#     # Step 1: Update name
#     if new_name is not None:
#         db_dataset.name = new_name

#     # Step 2: Update agentcolumns
#     if new_agentcolumns is not None:
#         db_dataset.agentcolumns = new_agentcolumns  # Assumes this field exists on model

#     db.commit()
#     db.refresh(db_dataset)
#     return db_dataset
# def delete_dataset(db: Session, dataset_id: int):
#     db_dataset = db.query(ImportedDataset).filter(ImportedDataset.id == dataset_id).first()
#     if not db_dataset:
#         raise ValueError("Dataset not found")

#     table_name = db_dataset.table_name

#     # Delete the actual table from the database
#     drop_table(table_name)

#     # Delete the dataset record
#     db.delete(db_dataset)
#     db.commit()

#     return {"message": f"Dataset '{db_dataset.name}' deleted successfully"}
# def drop_table(table_name: str):
#     """
#     Drop a table safely if it exists in the database.
    
#     Args:
#         table_name (str): Name of the table to drop.
#     """
#     try:
#         # Create metadata object and reflect existing tables
#         metadata = MetaData()
#         metadata.reflect(bind=engine)

#         if table_name in metadata.tables:
#             table = Table(table_name, metadata)
#             table.drop(bind=engine)
#             print(f"✅ Table '{table_name}' dropped successfully.")
#         else:
#             print(f"⚠️ Table '{table_name}' does not exist. Skipping drop.")
    
#     except Exception as e:
#         print(f"❌ Error dropping table '{table_name}': {e}")
#         raise
# def import_dataset_from_database(
#     db: Session,
#     db_url: str,
#     src_table: str,
#     name: str,
#     table_name: str,
#     owner_id: int,
#     mappings: dict = None,
#     skip_columns: list = None
# ):
#     df = load_table_to_dataframe(db_url, src_table)
#     df = apply_column_mapping(df, mappings or {}, skip_columns or [])
#     create_table_from_df(df, table_name)

#     dataset = DatasetCreate(name=name, source_type="database", table_name=table_name)
#     db_dataset = ImportedDataset(**dataset.model_dump(), owner_id=owner_id)
#     db.add(db_dataset)
#     db.commit()
#     db.refresh(db_dataset)
#     return db_dataset
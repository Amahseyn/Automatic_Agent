from sqlalchemy import create_engine, inspect
import pandas as pd
from app.database.session import engine
import pandas as pd
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, inspect
from app.database.session import engine  # Make sure this path is correct
from typing import Optional, Dict, List

def load_file_to_dataframe(file_path: str):
    _, ext = os.path.splitext(file_path)
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)
    elif ext == ".json":
        return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    

def get_file_columns(file_path: str) -> list:
    _, ext = os.path.splitext(file_path)
    if ext == ".csv":
        df = pd.read_csv(file_path, nrows=0)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path, nrows=0)
    elif ext == ".json":
        df = pd.read_json(file_path, nrows=0)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return df.columns.tolist()

def create_table_from_df(df: pd.DataFrame, table_name: str):
    """
    Creates a new table dynamically based on DataFrame schema.
    If table exists, it will be dropped and recreated.
    """
    metadata = MetaData()

    # Drop existing table if exists
    if inspect(engine).has_table(table_name):
        Table(table_name, metadata, autoload_with=engine)
        metadata.drop_all(engine)

    columns = []
    for col_name, dtype in df.dtypes.items():
        if dtype == 'int64':
            col_type = Integer
        elif dtype == 'float64':
            col_type = Float
        elif dtype == 'object':
            col_type = String
        else:
            col_type = String
        columns.append(Column(col_name, col_type))

    table = Table(table_name, metadata, *columns)
    metadata.create_all(engine)

    # Insert data
    with engine.connect() as conn:
        df.to_sql(table_name, con=conn, if_exists='append', index=False)

def get_tables_from_db(db_url: str):
    engine = create_engine(db_url)
    inspector = inspect(engine)
    return inspector.get_table_names()

def load_table_to_dataframe(table_name: str) -> pd.DataFrame:
    return pd.read_sql_table(table_name, con=engine)
def get_db_table_columns(db_url: str, table_name: str) -> list:
    engine = create_engine(db_url)
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        raise ValueError(f"Table '{table_name}' not found")
    return [col['name'] for col in inspector.get_columns(table_name)]
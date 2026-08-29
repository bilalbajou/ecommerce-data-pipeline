import os
import sys
import pandas as pd
from typing import Dict
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from src.config import Config
from src.logger import get_logger

logger = get_logger("load")

def create_database_if_not_exists(target_url: str, db_name: str):
    """Creates the target PostgreSQL database if it does not exist."""
    default_url = target_url.rsplit('/', 1)[0] + '/postgres'
    try:
        engine = create_engine(default_url)
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": db_name}
            )
            exists = result.scalar() == 1
            
            if not exists:
                logger.info(f"Database '{db_name}' does not exist. Creating...")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Database '{db_name}' created successfully.")
            else:
                logger.info(f"Database '{db_name}' already exists.")
    except OperationalError as e:
        logger.error(f"Could not connect to PostgreSQL server to create database: {e}")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Error while checking/creating database: {e}")
        raise

def define_products_table(metadata: MetaData) -> Table:
    """Defines the schema for the products table."""
    return Table(
        'products', metadata,
        Column('id', Integer, primary_key=True),
        Column('title', String),
        Column('category', String),
        Column('price', Float),
        Column('discount_percentage', Float),
        Column('rating', Float),
        Column('stock', Integer),
        Column('brand', String),
        Column('sku', String),
        Column('weight', Float),
        Column('dimensions_width', Float),
        Column('dimensions_height', Float),
        Column('dimensions_depth', Float),
        Column('meta_barcode', String),
        Column('meta_created_at', DateTime),
        Column('final_price', Float)
    )

def load_data(db_url: str, db_name: str, input_path: str) -> Dict[str, int]:
    """
    Reads the processed CSV and loads it into PostgreSQL using an optimized UPSERT.
    Returns metrics on inserted, updated, and unchanged records.
    """
    create_database_if_not_exists(db_url, db_name)

    engine = create_engine(db_url)
    metadata = MetaData()
    products_table = define_products_table(metadata)
    
    try:
        metadata.create_all(engine)
        logger.info("Ensured 'products' table exists in the database.")
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file {input_path} not found.")
            
        logger.info(f"Loading data from {input_path}")
        df = pd.read_csv(input_path)
        
        if 'meta_created_at' in df.columns:
            df['meta_created_at'] = pd.to_datetime(df['meta_created_at'])
            
        records = df.to_dict(orient='records')
        
        if not records:
            logger.warning("No records found in the input file.")
            return {"inserted": 0, "updated": 0, "unchanged": 0}
            
        with engine.begin() as conn:
            insert_stmt = insert(products_table).values(records)
            update_dict = {c.name: c for c in insert_stmt.excluded if c.name != 'id'}
            
            # Create a WHERE clause to only update if a column has changed
            where_conditions = [
                getattr(products_table.c, col).is_distinct_from(insert_stmt.excluded[col])
                for col in update_dict.keys()
            ]
            where_clause = or_(*where_conditions)
            
            # Upsert with PostgreSQL RETURNING xmax to differentiate insert vs update
            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=['id'],
                set_=update_dict,
                where=where_clause
            ).returning(
                products_table.c.id,
                text("(xmax = 0) AS is_inserted")
            )
            
            result = conn.execute(upsert_stmt)
            returned_rows = result.fetchall()
            
            inserted = sum(1 for row in returned_rows if row.is_inserted)
            updated = len(returned_rows) - inserted
            unchanged = len(records) - len(returned_rows)
            
            metrics = {
                "inserted": inserted,
                "updated": updated,
                "unchanged": unchanged
            }
            
            logger.info(f"Load metrics: {metrics}")
            return metrics
            
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred during load: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

if __name__ == "__main__":
    try:
        load_data(Config.get_db_url(), Config.DB_NAME, Config.PROCESSED_DATA_PATH)
    except Exception:
        sys.exit(1)

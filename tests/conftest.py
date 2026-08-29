import os
import pytest
import pandas as pd
from sqlalchemy import create_engine, text
from src.config import Config

@pytest.fixture
def sample_raw_data():
    """Provides a sample of raw product data as it would come from the API."""
    return [
        {
            "id": 1,
            "title": "Test Product",
            "category": "Test Category",
            "price": 100.0,
            "discountPercentage": 10.0,
            "rating": 4.5,
            "stock": 50,
            "brand": "Test Brand",
            "sku": "TST-001",
            "weight": 1.5,
            "dimensions": {
                "width": 10.0,
                "height": 20.0,
                "depth": 30.0
            },
            "meta": {
                "barcode": "123456789",
                "createdAt": "2023-01-01T00:00:00Z"
            }
        },
        {
            "id": 2,
            "title": "Null Brand Product",
            "category": None,
            "price": 50.0,
            "discountPercentage": 0.0,
            "rating": 3.0,
            "stock": 10,
            "brand": None,
            "sku": "TST-002",
            "weight": 2.0,
            "dimensions": {
                "width": 5.0,
                "height": 5.0,
                "depth": 5.0
            },
            "meta": {
                "barcode": "987654321",
                "createdAt": "2023-01-02T00:00:00Z"
            }
        }
    ]

@pytest.fixture
def sample_raw_df(sample_raw_data):
    """Provides a normalized pandas DataFrame mimicking pd.json_normalize(sample_raw_data)."""
    return pd.json_normalize(sample_raw_data)

@pytest.fixture
def test_db_url():
    """Returns a test database URL."""
    # Ensure test uses a specific test database name to avoid overwriting real data
    test_db_name = "ecommerce_test_db"
    return Config.get_db_url(db_name=test_db_name)

@pytest.fixture
def test_db(test_db_url):
    """Sets up and tears down a test database."""
    default_url = test_db_url.rsplit('/', 1)[0] + '/postgres'
    test_db_name = test_db_url.rsplit('/', 1)[1]
    
    engine = create_engine(default_url)
    
    # Setup
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))
        conn.execute(text(f"CREATE DATABASE {test_db_name}"))
        
    yield test_db_url
    
    # Teardown
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        # Terminate any active connections before dropping
        conn.execute(text(f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{test_db_name}' AND pid <> pg_backend_pid()"))
        conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))

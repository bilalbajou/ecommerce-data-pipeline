import os
import pytest
from sqlalchemy import create_engine, text
from src.transform import process_dataframe
from src.load import load_data

def test_load_data_integration(test_db, sample_raw_df, tmp_path):
    """
    Integration test:
    1. Transform sample data.
    2. Save to a temporary CSV.
    3. Load into test Postgres DB.
    4. Assert data is present.
    """
    # Prepare CSV
    transformed_df = process_dataframe(sample_raw_df)
    temp_csv_path = tmp_path / "processed.csv"
    transformed_df.to_csv(temp_csv_path, index=False)
    
    # Run load phase
    test_db_url = test_db
    test_db_name = test_db_url.rsplit('/', 1)[1]
    
    metrics1 = load_data(test_db_url, test_db_name, str(temp_csv_path))
    assert metrics1["inserted"] == 2
    assert metrics1["updated"] == 0
    assert metrics1["unchanged"] == 0
    
    # Assert data was loaded
    engine = create_engine(test_db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM products"))
        count = result.scalar()
        assert count == 2
        
        # Test Upsert logic (running again should not duplicate)
        metrics2 = load_data(test_db_url, test_db_name, str(temp_csv_path))
        assert metrics2["inserted"] == 0
        assert metrics2["updated"] == 0
        assert metrics2["unchanged"] == 2
        
        result = conn.execute(text("SELECT COUNT(*) FROM products"))
        count2 = result.scalar()
        assert count2 == 2 # Still 2

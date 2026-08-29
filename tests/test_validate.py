import pytest
from sqlalchemy import create_engine, text
from src.transform import process_dataframe
from src.load import load_data
from src.validate import DataValidator

def test_validator_with_valid_data(test_db, sample_raw_df, tmp_path):
    """
    Integration test: Load valid data and ensure validator passes.
    """
    transformed_df = process_dataframe(sample_raw_df)
    temp_csv_path = tmp_path / "processed.csv"
    transformed_df.to_csv(temp_csv_path, index=False)
    
    test_db_url = test_db
    test_db_name = test_db_url.rsplit('/', 1)[1]
    
    load_data(test_db_url, test_db_name, str(temp_csv_path))
    
    # Run Validator
    validator = DataValidator(test_db_url, str(temp_csv_path))
    validator.validate_row_count()
    validator.validate_unique_ids()
    validator.validate_not_null_fields()
    validator.validate_value_ranges()
    validator.validate_final_price_logic()
    
    assert validator.failed_checks == 0

def test_validator_with_invalid_data(test_db, sample_raw_df, tmp_path):
    """
    Integration test: Introduce invalid data into DB and ensure validator fails.
    """
    transformed_df = process_dataframe(sample_raw_df)
    temp_csv_path = tmp_path / "processed.csv"
    transformed_df.to_csv(temp_csv_path, index=False)
    
    test_db_url = test_db
    test_db_name = test_db_url.rsplit('/', 1)[1]
    load_data(test_db_url, test_db_name, str(temp_csv_path))
    
    # Manually sabotage DB data
    engine = create_engine(test_db_url)
    with engine.connect() as conn:
        # Create a negative price
        conn.execute(text("UPDATE products SET price = -10.0 WHERE id = 1"))
        # Create a final price mismatch
        conn.execute(text("UPDATE products SET final_price = 999.0 WHERE id = 2"))
        conn.commit()
        
    # Run Validator
    validator = DataValidator(test_db_url, str(temp_csv_path))
    validator.validate_value_ranges()
    validator.validate_final_price_logic()
    
    assert validator.failed_checks > 0

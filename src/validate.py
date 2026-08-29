import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from src.config import Config
from src.logger import get_logger

logger = get_logger("validate")

class DataValidator:
    def __init__(self, db_url: str, csv_path: str):
        self.engine = create_engine(db_url)
        self.csv_path = csv_path
        self.failed_checks = 0
        
    def check(self, condition: bool, success_msg: str, error_msg: str, critical: bool = True):
        """Helper method to log PASS/FAIL and keep track of failures."""
        if condition:
            logger.info(f"[PASS] {success_msg}")
        else:
            logger.error(f"[FAIL] {error_msg}")
            if critical:
                self.failed_checks += 1
                
    def validate_row_count(self):
        try:
            df = pd.read_csv(self.csv_path)
            csv_count = len(df)
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM products"))
                db_count = result.scalar()
            self.check(
                csv_count == db_count,
                f"Row count matches: CSV ({csv_count}) == DB ({db_count})",
                f"Row count mismatch: CSV ({csv_count}) != DB ({db_count})"
            )
        except Exception as e:
            self.check(False, "", f"Failed to perform row count validation: {e}")

    def validate_unique_ids(self):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(id) as total_ids, COUNT(DISTINCT id) as unique_ids FROM products"))
                row = result.fetchone()
            self.check(
                row.total_ids == row.unique_ids,
                "Product IDs are unique.",
                f"Duplicate IDs found. Total: {row.total_ids}, Unique: {row.unique_ids}"
            )
        except Exception as e:
            self.check(False, "", f"Failed to perform unique ID validation: {e}")

    def validate_not_null_fields(self):
        required_fields = ['id', 'title', 'price']
        try:
            with self.engine.connect() as conn:
                for field in required_fields:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM products WHERE {field} IS NULL"))
                    null_count = result.scalar()
                    self.check(
                        null_count == 0,
                        f"Field '{field}' has no NULL values.",
                        f"Field '{field}' contains {null_count} NULL values."
                    )
        except Exception as e:
            self.check(False, "", f"Failed to perform NOT NULL validation: {e}")

    def validate_value_ranges(self):
        constraints = [
            ("price >= 0", "Price is non-negative"),
            ("final_price >= 0", "Final price is non-negative"),
            ("discount_percentage >= 0 AND discount_percentage <= 100", "Discount percentage is between 0 and 100"),
            ("rating >= 0 AND rating <= 5", "Rating is between 0 and 5"),
            ("stock >= 0", "Stock is non-negative")
        ]
        try:
            with self.engine.connect() as conn:
                for condition, desc in constraints:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM products WHERE NOT ({condition})"))
                    violations = result.scalar()
                    self.check(
                        violations == 0,
                        f"Values within bounds: {desc}",
                        f"Value range violation: {violations} rows failed condition '{condition}'"
                    )
        except Exception as e:
            self.check(False, "", f"Failed to perform value range validation: {e}")

    def validate_final_price_logic(self):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM products WHERE ABS(final_price - (price * (1 - discount_percentage / 100.0))) > 0.02"))
                violations = result.scalar()
                self.check(
                    violations == 0,
                    "Final prices are mathematically consistent with price and discount.",
                    f"Mathematical inconsistency found in {violations} rows for final_price calculation."
                )
        except Exception as e:
            self.check(False, "", f"Failed to perform final price logic validation: {e}")

from typing import Dict
def run_validation(db_url: str, input_path: str) -> Dict[str, bool]:
    """Runs all validation checks."""
    logger.info("Starting Data Quality Validation Phase...")
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} not found. Cannot validate row counts.")
        
    validator = DataValidator(db_url, input_path)
    
    logger.info("--- Running Checks ---")
    validator.validate_row_count()
    validator.validate_unique_ids()
    validator.validate_not_null_fields()
    validator.validate_value_ranges()
    validator.validate_final_price_logic()
    logger.info("----------------------")
    
    if validator.failed_checks > 0:
        raise ValueError(f"Validation completed with {validator.failed_checks} critical failures.")
    else:
        logger.info("Validation completed successfully. All checks PASSED!")
        return {"validated_passed": True}

if __name__ == "__main__":
    try:
        run_validation(Config.get_db_url(), Config.PROCESSED_DATA_PATH)
    except Exception as err:
        logger.error(str(err))
        sys.exit(1)

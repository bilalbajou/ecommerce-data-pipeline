import sys
import time
from src.config import Config
from src.logger import get_logger
from src.extract import extract_products
from src.transform import transform_products
from src.load import load_data
from src.validate import run_validation

logger = get_logger("pipeline")

def main():
    logger.info("Starting E-commerce ETL Pipeline")
    start_time = time.time()
    
    try:
        logger.info("=== PHASE 1: EXTRACT ===")
        extract_metrics = extract_products(Config.API_URL, Config.RAW_DATA_PATH)
        
        logger.info("=== PHASE 2: TRANSFORM ===")
        transform_metrics = transform_products(Config.RAW_DATA_PATH, Config.PROCESSED_DATA_PATH)
        
        logger.info("=== PHASE 3: LOAD ===")
        load_metrics = load_data(Config.get_db_url(), Config.DB_NAME, Config.PROCESSED_DATA_PATH)
        
        logger.info("=== PHASE 4: VALIDATE ===")
        val_metrics = run_validation(Config.get_db_url(), Config.PROCESSED_DATA_PATH)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info("========================================")
        logger.info("      ETL PIPELINE SUMMARY REPORT       ")
        logger.info("========================================")
        logger.info(f"Execution Time : {duration:.2f} seconds")
        logger.info(f"Extracted      : {extract_metrics.get('extracted', 0)} records")
        logger.info(f"Transformed    : {transform_metrics.get('transformed', 0)} records")
        logger.info(f"DB Inserted    : {load_metrics.get('inserted', 0)} records")
        logger.info(f"DB Updated     : {load_metrics.get('updated', 0)} records")
        logger.info(f"DB Unchanged   : {load_metrics.get('unchanged', 0)} records")
        logger.info(f"Validation     : {'PASSED' if val_metrics.get('validated_passed') else 'FAILED'}")
        logger.info("========================================")
        logger.info("ETL Pipeline completed successfully!")
        
        sys.exit(0)
    except Exception as e:
        logger.critical(f"ETL Pipeline failed due to an error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

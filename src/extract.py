import os
import sys
import json
import requests
from typing import Dict
from src.config import Config
from src.logger import get_logger

logger = get_logger("extract")

def extract_products(api_url: str, output_path: str) -> Dict[str, int]:
    """
    Extracts product data from the given API URL with pagination and saves it to a local JSON file.
    Returns metrics on the number of products extracted.
    """
    logger.info(f"Starting data extraction from {api_url}")
    
    all_products = []
    skip = 0
    limit = 30 # Configure chunk size
    
    try:
        while True:
            # Add pagination parameters
            paginated_url = f"{api_url}?limit={limit}&skip={skip}"
            logger.info(f"Fetching {paginated_url}")
            
            response = requests.get(paginated_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            products = data.get('products', [])
            
            if not products:
                break
                
            all_products.extend(products)
            logger.info(f"Fetched {len(products)} products (Total so far: {len(all_products)})")
            
            total_available = data.get('total', 0)
            skip += limit
            
            if skip >= total_available:
                break
                
        if not all_products:
            logger.warning("No products found in the API response.")
            raise ValueError("No products returned by the API.")
            
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the raw products list to a local JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=4)
            
        logger.info(f"Successfully saved {len(all_products)} total products to {output_path}")
        return {"extracted": len(all_products)}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error occurred while fetching data: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during extraction: {e}")
        raise

if __name__ == "__main__":
    try:
        metrics = extract_products(Config.API_URL, Config.RAW_DATA_PATH)
        print(metrics)
    except Exception:
        sys.exit(1)

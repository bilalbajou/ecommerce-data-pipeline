import os
import sys
import json
import pandas as pd
import re
from src.config import Config
from src.logger import get_logger

logger = get_logger("transform")

from typing import Dict

def to_snake_case(name: str) -> str:
    """Convert camelCase or dot.notation to snake_case."""
    name = name.replace('.', '_')
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return s2.replace('__', '_')

def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Pure function that applies all transformation rules to the dataframe."""
    # 1. Keep only business-relevant fields
    cols_to_keep = [
        'id', 'title', 'category', 'price', 'discountPercentage', 'rating', 'stock', 
        'brand', 'sku', 'weight', 
        'dimensions.width', 'dimensions.height', 'dimensions.depth',
        'meta.barcode', 'meta.createdAt'
    ]
    
    existing_cols = [c for c in cols_to_keep if c in df.columns]
    df = df[existing_cols].copy()
    
    # 2. Normalize column names (snake_case)
    df.columns = [to_snake_case(c) for c in df.columns]
    
    # 3. Detect and remove duplicate products based on product ID
    df.drop_duplicates(subset=['id'], inplace=True)
        
    # 4. Validate required fields
    required_fields = ['id', 'title', 'price']
    df.dropna(subset=required_fields, inplace=True)
    
    # 5. Handle missing/null values explicitly
    if 'brand' in df.columns:
        df['brand'] = df['brand'].fillna('Unknown')
    if 'category' in df.columns:
        df['category'] = df['category'].fillna('Uncategorized')
        
    # 6. Convert numeric fields to proper numeric types
    numeric_cols = [
        'price', 'discount_percentage', 'rating', 'stock', 'weight', 
        'dimensions_width', 'dimensions_height', 'dimensions_depth'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # 7. Create a calculated final_price
    if 'price' in df.columns and 'discount_percentage' in df.columns:
        df['final_price'] = df['price'] * (1 - df['discount_percentage'] / 100)
        df['final_price'] = df['final_price'].round(2)
        
    return df

def transform_products(input_path: str, output_path: str) -> Dict[str, int]:
    """
    Reads raw product data, transforms it into a clean analytics-ready format,
    and saves it to a CSV file. Raises exceptions on critical failures.
    Returns metrics on the number of products transformed.
    """
    logger.info(f"Loading raw data from {input_path}")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} not found.")

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        df = pd.json_normalize(data)
        logger.info(f"Loaded {len(df)} records. Initial shape: {df.shape}")
        
        # Apply pure transformation function
        transformed_df = process_dataframe(df)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the transformed dataset
        transformed_df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Successfully transformed data and saved to {output_path}. Final shape: {transformed_df.shape}")
        
        return {"transformed": len(transformed_df)}
        
    except Exception as e:
        logger.error(f"An error occurred during transformation: {e}")
        raise

if __name__ == "__main__":
    try:
        transform_products(Config.RAW_DATA_PATH, Config.PROCESSED_DATA_PATH)
    except Exception:
        sys.exit(1)

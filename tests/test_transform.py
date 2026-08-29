import pandas as pd
from src.transform import process_dataframe, to_snake_case

def test_to_snake_case():
    assert to_snake_case("discountPercentage") == "discount_percentage"
    assert to_snake_case("dimensions.width") == "dimensions_width"
    assert to_snake_case("camelCaseString") == "camel_case_string"
    assert to_snake_case("Normal_String") == "normal_string"

def test_process_dataframe(sample_raw_df):
    df_out = process_dataframe(sample_raw_df)
    
    # Check shape
    assert len(df_out) == 2
    assert len(df_out.columns) == 16
    
    # Check final price calculation (100 * (1 - 0.1) = 90.0)
    assert df_out.loc[df_out['id'] == 1, 'final_price'].values[0] == 90.0
    # No discount for second product
    assert df_out.loc[df_out['id'] == 2, 'final_price'].values[0] == 50.0
    
    # Check null handling
    assert df_out.loc[df_out['id'] == 2, 'brand'].values[0] == "Unknown"
    assert df_out.loc[df_out['id'] == 2, 'category'].values[0] == "Uncategorized"
    
    # Check column names are snake case
    assert "discount_percentage" in df_out.columns
    assert "dimensions_width" in df_out.columns

def test_process_dataframe_drops_missing_required():
    data = [
        {"id": 1, "title": "Valid", "price": 10.0},
        {"id": 2, "title": None, "price": 10.0},  # Missing title
        {"id": 3, "title": "Valid2", "price": None}, # Missing price
        {"title": "Valid3", "price": 10.0} # Missing ID
    ]
    df = pd.json_normalize(data)
    df_out = process_dataframe(df)
    
    # Only the first valid row should remain
    assert len(df_out) == 1
    assert df_out.iloc[0]['id'] == 1

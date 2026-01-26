"""
Product Normalization (Daily Level)

Purpose:
Aggregate daily SKU-level product demand into daily product-level forecast.
Aggregates across all SKUs and stores for each product per day.

Stage:
SKU → Product normalization

Input:
- sku_product_demand.csv (daily)

Output:
- product_forecast.csv (daily)
"""

import pandas as pd
import warnings
import os

warnings.filterwarnings("ignore")


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")

INPUT_FILE = os.path.join(DATASETS_DIR, "sku_product_demand.csv")
OUTPUT_FILE = os.path.join(DATASETS_DIR, "product_forecast.csv")


# --------------------------------------------------
# Product Normalization Logic
# --------------------------------------------------

def normalize_product_demand(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates daily product demand across all SKUs and stores.
    
    Input columns:
    - date, sku_id, store_id, product_id, forecast_horizon, product_units
    
    Output columns:
    - date, product_id, forecast_horizon, product_units
    """

    product_forecast = (
        df.groupby(
            ["date", "product_id", "forecast_horizon"],
            as_index=False
        )["product_units"]
        .sum()
    )
    
    # Sort by date and product
    product_forecast = product_forecast.sort_values(
        ["forecast_horizon", "date", "product_id"]
    ).reset_index(drop=True)
    
    return product_forecast


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("=" * 60)
    print("PRODUCT NORMALIZATION (DAILY)")
    print("=" * 60)
    print()

    print("Loading SKU-product demand data...")
    df = pd.read_csv(INPUT_FILE)
    print(f"  Loaded {len(df)} rows")

    print("\nNormalizing product demand...")
    product_forecast = normalize_product_demand(df)

    print("\nSaving product forecast...")
    product_forecast.to_csv(OUTPUT_FILE, index=False)

    print()
    print("=" * 60)
    print("PRODUCT NORMALIZATION COMPLETED")
    print("=" * 60)
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"  Total rows: {len(product_forecast)}")
    print(f"  Unique dates: {product_forecast['date'].nunique()}")
    print(f"  Unique products: {product_forecast['product_id'].nunique()}")
    
    # Summary by horizon
    print("\n--- By Forecast Horizon ---")
    for horizon in product_forecast['forecast_horizon'].unique():
        subset = product_forecast[product_forecast['forecast_horizon'] == horizon]
        print(f"  {horizon}: {len(subset)} rows, total units = {subset['product_units'].sum()}")


if __name__ == "__main__":
    main()

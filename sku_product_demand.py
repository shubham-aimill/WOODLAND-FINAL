"""
SKU → Product Demand Disaggregation (Daily Level)

Purpose:
Convert daily SKU-level forecast into daily product-level demand
using inferred product mix allocation.

Formula:
product_units = forecast_units × allocation_weight

Inputs:
- sku_daily_forecast.csv (daily forecasts for 7-day and 30-day horizons)
- sku_product_allocation.csv

Output:
- sku_product_demand.csv (daily product demand)
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

SKU_FORECAST_FILE = os.path.join(DATASETS_DIR, "sku_daily_forecast.csv")
SKU_PRODUCT_ALLOCATION_FILE = os.path.join(DATASETS_DIR, "sku_product_allocation.csv")
OUTPUT_FILE = os.path.join(DATASETS_DIR, "sku_product_demand.csv")


# --------------------------------------------------
# SKU → Product Disaggregation
# --------------------------------------------------

def create_sku_product_demand(
    sku_forecast: pd.DataFrame,
    sku_allocation: pd.DataFrame
) -> pd.DataFrame:
    """
    Applies product allocation weights to daily SKU forecasts.
    
    Input columns (sku_forecast):
    - date, sku_id, store_id, forecast_horizon, forecast_units
    
    Output columns:
    - date, sku_id, store_id, product_id, forecast_horizon, product_units
    """

    # Join forecast with allocation weights
    merged = sku_forecast.merge(
        sku_allocation[["sku_id", "product_id", "allocation_weight"]],
        on="sku_id",
        how="left"
    )

    # Calculate product demand (integer units)
    merged["product_units"] = (
        merged["forecast_units"] * merged["allocation_weight"]
    ).round().astype(int)

    # Final output columns
    sku_product_demand = merged[
        [
            "date",
            "sku_id",
            "store_id",
            "product_id",
            "forecast_horizon",
            "product_units"
        ]
    ]

    return sku_product_demand


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("=" * 60)
    print("SKU → PRODUCT DEMAND DISAGGREGATION (DAILY)")
    print("=" * 60)
    print()

    print("Loading daily SKU forecast...")
    sku_forecast = pd.read_csv(SKU_FORECAST_FILE)
    print(f"  Loaded {len(sku_forecast)} forecast rows")
    print(f"  Horizons: {sku_forecast['forecast_horizon'].unique().tolist()}")

    print("\nLoading SKU–product allocation...")
    sku_allocation = pd.read_csv(SKU_PRODUCT_ALLOCATION_FILE)
    print(f"  Loaded {len(sku_allocation)} allocation mappings")

    print("\nCreating SKU → Product demand...")
    sku_product_demand = create_sku_product_demand(
        sku_forecast,
        sku_allocation
    )

    print("\nSaving SKU–product demand...")
    sku_product_demand.to_csv(OUTPUT_FILE, index=False)

    print()
    print("=" * 60)
    print("SKU → PRODUCT DEMAND COMPLETED")
    print("=" * 60)
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"  Total rows: {len(sku_product_demand)}")
    print(f"  Unique dates: {sku_product_demand['date'].nunique()}")
    print(f"  Unique SKUs: {sku_product_demand['sku_id'].nunique()}")
    print(f"  Unique products: {sku_product_demand['product_id'].nunique()}")
    
    # Summary by horizon
    print("\n--- By Forecast Horizon ---")
    for horizon in sku_product_demand['forecast_horizon'].unique():
        subset = sku_product_demand[sku_product_demand['forecast_horizon'] == horizon]
        print(f"  {horizon}: {len(subset)} rows, total units = {subset['product_units'].sum()}")


if __name__ == "__main__":
    main()

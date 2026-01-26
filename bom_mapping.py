"""
BOM Mapping (Daily Level)

Purpose:
Map daily product-level forecast to Bill of Materials.

Stage:
Product → BOM mapping

Inputs:
- product_forecast.csv (daily)
- product_bom.csv

Output:
- product_bom_expanded.csv (daily)
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

PRODUCT_FORECAST_FILE = os.path.join(DATASETS_DIR, "product_forecast.csv")
PRODUCT_BOM_FILE = os.path.join(DATASETS_DIR, "product_bom.csv")
OUTPUT_FILE = os.path.join(DATASETS_DIR, "product_bom_expanded.csv")


# --------------------------------------------------
# BOM Mapping Logic
# --------------------------------------------------

def map_bom(
    product_forecast: pd.DataFrame,
    product_bom: pd.DataFrame
) -> pd.DataFrame:
    """
    Expands daily product forecast using BOM definitions.
    
    Input columns (product_forecast):
    - date, product_id, forecast_horizon, product_units
    
    Input columns (product_bom):
    - product_id, raw_material, material_type, consumption_per_unit
    
    Output columns:
    - date, product_id, forecast_horizon, product_units, 
      raw_material, material_type, consumption_per_unit
    """

    expanded = product_forecast.merge(
        product_bom,
        on="product_id",
        how="left"
    )

    # Explicit column ordering
    expanded = expanded[
        [
            "date",
            "product_id",
            "forecast_horizon",
            "product_units",
            "raw_material",
            "material_type",
            "consumption_per_unit"
        ]
    ]
    
    # Sort for consistency
    expanded = expanded.sort_values(
        ["forecast_horizon", "date", "product_id", "raw_material"]
    ).reset_index(drop=True)

    return expanded


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("=" * 60)
    print("BOM MAPPING (DAILY)")
    print("=" * 60)
    print()

    print("Loading daily product forecast...")
    product_forecast = pd.read_csv(PRODUCT_FORECAST_FILE)
    print(f"  Loaded {len(product_forecast)} forecast rows")

    print("\nLoading product BOM...")
    product_bom = pd.read_csv(PRODUCT_BOM_FILE)
    print(f"  Loaded {len(product_bom)} BOM entries")

    print("\nMapping BOM with daily forecast...")
    expanded = map_bom(product_forecast, product_bom)

    print("\nSaving BOM expanded data...")
    expanded.to_csv(OUTPUT_FILE, index=False)

    print()
    print("=" * 60)
    print("BOM MAPPING COMPLETED")
    print("=" * 60)
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"  Total rows: {len(expanded)}")
    print(f"  Unique dates: {expanded['date'].nunique()}")
    print(f"  Unique products: {expanded['product_id'].nunique()}")
    print(f"  Unique raw materials: {expanded['raw_material'].nunique()}")
    
    # Summary by horizon
    print("\n--- By Forecast Horizon ---")
    for horizon in expanded['forecast_horizon'].unique():
        subset = expanded[expanded['forecast_horizon'] == horizon]
        print(f"  {horizon}: {len(subset)} rows")


if __name__ == "__main__":
    main()

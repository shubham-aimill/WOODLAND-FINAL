"""
Demand Explosion (Daily Level)

Purpose:
Convert daily product-level demand into daily raw material-level demand.

Stage:
Product → Raw Material demand explosion

Formula:
material_demand = product_units × consumption_per_unit

Input:
- product_bom_expanded.csv (daily)

Output:
- raw_material_demand.csv (daily)
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

INPUT_FILE = os.path.join(DATASETS_DIR, "product_bom_expanded.csv")
OUTPUT_FILE = os.path.join(DATASETS_DIR, "raw_material_demand.csv")


# --------------------------------------------------
# Demand Explosion Logic
# --------------------------------------------------

def explode_demand(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates daily raw material demand using BOM consumption rates.
    
    Input columns:
    - date, product_id, forecast_horizon, product_units, 
      raw_material, material_type, consumption_per_unit
    
    Output columns:
    - date, raw_material, material_type, forecast_horizon, material_demand_units
    """

    # ----------------------------------
    # Step 1: Calculate material-level demand
    # ----------------------------------
    df["material_demand_units"] = (
        df["product_units"] * df["consumption_per_unit"]
    )

    # ----------------------------------
    # Step 2: Aggregate by date and material
    # ----------------------------------
    raw_material_demand = (
        df.groupby(
            [
                "date",
                "raw_material",
                "material_type",
                "forecast_horizon"
            ],
            as_index=False
        )["material_demand_units"]
        .sum()
    )
    
    # Round to integer for cleaner output
    raw_material_demand["material_demand_units"] = (
        raw_material_demand["material_demand_units"].round().astype(int)
    )
    
    # Sort for consistency
    raw_material_demand = raw_material_demand.sort_values(
        ["forecast_horizon", "date", "raw_material"]
    ).reset_index(drop=True)

    return raw_material_demand


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("=" * 60)
    print("DEMAND EXPLOSION (DAILY)")
    print("=" * 60)
    print()

    print("Loading BOM expanded data...")
    df = pd.read_csv(INPUT_FILE)
    print(f"  Loaded {len(df)} rows")

    print("\nRunning demand explosion...")
    raw_material_demand = explode_demand(df)

    print("\nSaving raw material demand...")
    raw_material_demand.to_csv(OUTPUT_FILE, index=False)

    print()
    print("=" * 60)
    print("DEMAND EXPLOSION COMPLETED")
    print("=" * 60)
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"  Total rows: {len(raw_material_demand)}")
    print(f"  Unique dates: {raw_material_demand['date'].nunique()}")
    print(f"  Unique raw materials: {raw_material_demand['raw_material'].nunique()}")
    
    # Summary by horizon
    print("\n--- By Forecast Horizon ---")
    for horizon in raw_material_demand['forecast_horizon'].unique():
        subset = raw_material_demand[raw_material_demand['forecast_horizon'] == horizon]
        print(f"  {horizon}: {len(subset)} rows, total demand = {subset['material_demand_units'].sum()}")
    
    # Summary by material type
    print("\n--- By Material Type ---")
    for mtype in raw_material_demand['material_type'].unique():
        subset = raw_material_demand[raw_material_demand['material_type'] == mtype]
        print(f"  {mtype}: total demand = {subset['material_demand_units'].sum()}")


if __name__ == "__main__":
    main()

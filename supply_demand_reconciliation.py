"""
Supply–Demand Reconciliation (Daily Level)

Purpose:
Compare daily raw material demand against available inventory
for each forecast date.

Inputs:
- raw_material_demand.csv (daily)
- raw_material_inventory_ledger.csv

Output:
- raw_material_reconciliation.csv (daily)
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

DEMAND_FILE = os.path.join(DATASETS_DIR, "raw_material_demand.csv")
INVENTORY_FILE = os.path.join(DATASETS_DIR, "raw_material_inventory_ledger.csv")
OUTPUT_FILE = os.path.join(DATASETS_DIR, "raw_material_reconciliation.csv")


# --------------------------------------------------
# Reconciliation Logic
# --------------------------------------------------

def reconcile_supply_demand(
    demand_df: pd.DataFrame,
    inventory_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Reconciles daily raw material demand with inventory snapshots.
    
    For each forecast date, uses the latest available inventory snapshot
    prior to or on that date.
    
    Input columns (demand_df):
    - date, raw_material, material_type, forecast_horizon, material_demand_units
    
    Input columns (inventory_df):
    - date, raw_material, closing_inventory, safety_stock, etc.
    
    Output columns:
    - date, raw_material, material_type, forecast_horizon, material_demand_units,
      inventory_date, closing_inventory, safety_stock, inventory_gap_units
    """

    # ----------------------------------
    # Step 1: Ensure dates are parsed
    # ----------------------------------
    demand_df["date"] = pd.to_datetime(demand_df["date"], errors="coerce")
    inventory_df["date"] = pd.to_datetime(inventory_df["date"], errors="coerce", format="mixed")

    # ----------------------------------
    # Step 2: Get unique forecast dates
    # ----------------------------------
    forecast_dates = demand_df["date"].unique()
    
    # Get the earliest forecast date to find relevant inventory
    min_forecast_date = demand_df["date"].min()
    
    # ----------------------------------
    # Step 3: Get latest inventory snapshot before forecast period
    # ----------------------------------
    inventory_snapshot = (
        inventory_df[inventory_df["date"] <= min_forecast_date]
        .sort_values("date")
        .groupby("raw_material", as_index=False)
        .last()
    )
    
    # Rename date column to avoid confusion
    inventory_snapshot = inventory_snapshot.rename(columns={"date": "inventory_date"})
    
    # Select relevant inventory columns
    inventory_cols = ["raw_material", "inventory_date", "closing_inventory", "safety_stock"]
    available_cols = [c for c in inventory_cols if c in inventory_snapshot.columns]
    inventory_snapshot = inventory_snapshot[available_cols]

    # ----------------------------------
    # Step 4: Merge demand with inventory
    # ----------------------------------
    reconciliation = demand_df.merge(
        inventory_snapshot,
        on="raw_material",
        how="left"
    )

    # ----------------------------------
    # Step 5: Calculate inventory gap
    # ----------------------------------
    # Gap = Closing Inventory - Daily Demand
    # Positive = surplus, Negative = shortfall
    reconciliation["inventory_gap_units"] = (
        reconciliation["closing_inventory"] - reconciliation["material_demand_units"]
    )
    
    # ----------------------------------
    # Step 6: Calculate cumulative demand for running balance
    # ----------------------------------
    reconciliation = reconciliation.sort_values(
        ["forecast_horizon", "raw_material", "date"]
    ).reset_index(drop=True)
    
    # Cumulative demand per material per horizon
    reconciliation["cumulative_demand"] = (
        reconciliation.groupby(["forecast_horizon", "raw_material"])["material_demand_units"]
        .cumsum()
    )
    
    # Running inventory balance
    reconciliation["running_inventory_balance"] = (
        reconciliation["closing_inventory"] - reconciliation["cumulative_demand"]
    )

    return reconciliation


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("=" * 60)
    print("SUPPLY-DEMAND RECONCILIATION (DAILY)")
    print("=" * 60)
    print()

    print("Loading daily raw material demand...")
    demand_df = pd.read_csv(DEMAND_FILE)
    print(f"  Loaded {len(demand_df)} demand rows")

    print("\nLoading inventory ledger...")
    inventory_df = pd.read_csv(INVENTORY_FILE)
    print(f"  Loaded {len(inventory_df)} inventory rows")

    print("\nRunning supply–demand reconciliation...")
    reconciliation_df = reconcile_supply_demand(demand_df, inventory_df)

    print("\nSaving reconciliation output...")
    reconciliation_df.to_csv(OUTPUT_FILE, index=False)

    print()
    print("=" * 60)
    print("RECONCILIATION COMPLETED")
    print("=" * 60)
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"  Total rows: {len(reconciliation_df)}")
    print(f"  Unique dates: {reconciliation_df['date'].nunique()}")
    print(f"  Unique raw materials: {reconciliation_df['raw_material'].nunique()}")
    
    # Summary by horizon
    print("\n--- By Forecast Horizon ---")
    for horizon in reconciliation_df['forecast_horizon'].unique():
        subset = reconciliation_df[reconciliation_df['forecast_horizon'] == horizon]
        shortfall = (subset['inventory_gap_units'] < 0).sum()
        print(f"  {horizon}: {len(subset)} rows, daily shortfalls = {shortfall}")
    
    # Materials with running balance issues
    print("\n--- Materials with Inventory Shortfall (End of Period) ---")
    for horizon in reconciliation_df['forecast_horizon'].unique():
        subset = reconciliation_df[reconciliation_df['forecast_horizon'] == horizon]
        # Get last day per material
        last_day = subset.groupby("raw_material").last()
        shortfall_materials = last_day[last_day['running_inventory_balance'] < 0]
        if len(shortfall_materials) > 0:
            print(f"  {horizon}:")
            for mat in shortfall_materials.index[:5]:  # Show top 5
                balance = shortfall_materials.loc[mat, 'running_inventory_balance']
                print(f"    - {mat}: balance = {balance:.0f}")
            if len(shortfall_materials) > 5:
                print(f"    ... and {len(shortfall_materials) - 5} more")


if __name__ == "__main__":
    main()

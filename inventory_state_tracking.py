"""
Inventory State Tracking

Purpose:
Create a validated raw material inventory ledger
using provided inventory movements.

Input:
- raw_material_inventory.csv

Output:
- raw_material_inventory_ledger.csv
"""

import pandas as pd
import warnings

warnings.filterwarnings("ignore")


# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT_FILE = "datasets/raw_material_inventory.csv"
OUTPUT_FILE = "datasets/raw_material_inventory_ledger.csv"


# --------------------------------------------------
# Inventory Ledger Logic
# --------------------------------------------------

def create_inventory_ledger(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates and standardizes inventory ledger.
    """

    # ----------------------------------
    # Step 1: Robust date parsing
    # ----------------------------------
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        format="mixed"
    )

    # ----------------------------------
    # Step 2: Sort ledger chronologically
    # ----------------------------------
    df = df.sort_values(
        by=["raw_material", "date"]
    ).reset_index(drop=True)

    # ----------------------------------
    # Step 3: Recalculate closing inventory
    # ----------------------------------
    df["calculated_closing_inventory"] = (
        df["opening_inventory"]
        + df["inflow_quantity"]
        - df["consumed_quantity"]
    )

    # ----------------------------------
    # Step 4: Validation flag
    # ----------------------------------
    df["inventory_validation_status"] = (
        df["closing_inventory"]
        == df["calculated_closing_inventory"]
    )

    return df


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("Loading raw material inventory data...")
    inventory_df = pd.read_csv(INPUT_FILE)

    print("Creating inventory ledger...")
    ledger_df = create_inventory_ledger(inventory_df)

    print("Saving inventory ledger...")
    ledger_df.to_csv(OUTPUT_FILE, index=False)

    print("Inventory ledger created successfully.")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

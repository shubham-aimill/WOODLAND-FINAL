"""
SKU → Product Mix Inference

Purpose:
1. Infer product mix for each SKU using rolling 30-day actual sales
2. Generate allocation weights used later for SKU → Product demand split

Inputs:
- sku_daily_sales.csv
- sku_master.csv

Output:
- sku_product_allocation.csv

Business Logic:
- Rolling 30-day window
- allocation_weight = product_units / total_sku_units
- Allocation weights sum to 1.0 per SKU
"""

import pandas as pd
from datetime import timedelta
import warnings

warnings.filterwarnings("ignore")


# --------------------------------------------------
# Configuration
# --------------------------------------------------

SKU_DAILY_SALES_FILE = "/Users/pranaynath/Downloads/Woodland Forecast/datasets/sku_daily_sales.csv"
SKU_MASTER_FILE = "/Users/pranaynath/Downloads/Woodland Forecast/datasets/sku_master.csv"
OUTPUT_FILE = "/Users/pranaynath/Downloads/Woodland Forecast/datasets/sku_product_allocation.csv"

ROLLING_WINDOW_DAYS = 30


# --------------------------------------------------
# Load Data
# --------------------------------------------------

def load_data():
    sales_df = pd.read_csv(SKU_DAILY_SALES_FILE)
    sku_master_df = pd.read_csv(SKU_MASTER_FILE)

    sales_df["date"] = pd.to_datetime(sales_df["date"])

    return sales_df, sku_master_df


# --------------------------------------------------
# Product Mix Inference
# --------------------------------------------------

def infer_product_mix(sales_df: pd.DataFrame,
                      sku_master_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes rolling 30-day product contribution per SKU.
    """

    # --------------------------------------------------
    # Step 1: Join sales with SKU → Product mapping
    # --------------------------------------------------
    sales_enriched = sales_df.merge(
        sku_master_df,
        on="sku_id",
        how="left"
    )

    # --------------------------------------------------
    # Step 2: Filter rolling 30-day window
    # --------------------------------------------------
    max_date = sales_enriched["date"].max()
    window_start = max_date - timedelta(days=ROLLING_WINDOW_DAYS)

    rolling_sales = sales_enriched[
        sales_enriched["date"] >= window_start
    ]

    # --------------------------------------------------
    # Step 3: Aggregate at SKU × Product level
    # --------------------------------------------------
    sku_product_sales = (
        rolling_sales
        .groupby(["sku_id", "product_id"], as_index=False)
        ["actual_sales_units"]
        .sum()
        .rename(columns={"actual_sales_units": "product_units"})
    )

    # --------------------------------------------------
    # Step 4: Total SKU units
    # --------------------------------------------------
    sku_totals = (
        sku_product_sales
        .groupby("sku_id", as_index=False)["product_units"]
        .sum()
        .rename(columns={"product_units": "sku_total_units"})
    )

    # --------------------------------------------------
    # Step 5: Allocation weight calculation
    # --------------------------------------------------
    allocation = sku_product_sales.merge(
        sku_totals,
        on="sku_id",
        how="left"
    )

    allocation["allocation_weight"] = (
        allocation["product_units"]
        / allocation["sku_total_units"]
    )

    # --------------------------------------------------
    # Step 6: Final output
    # --------------------------------------------------
    output_df = allocation[
        ["sku_id", "product_id", "allocation_weight"]
    ].copy()

    output_df["allocation_weight"] = output_df["allocation_weight"].round(3)
    output_df["window_days"] = ROLLING_WINDOW_DAYS

    return output_df


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("Loading datasets...")
    sales_df, sku_master_df = load_data()

    print("Inferring SKU → Product mix (rolling 30 days)...")
    allocation_df = infer_product_mix(sales_df, sku_master_df)

    print("Saving allocation output...")
    allocation_df.to_csv(OUTPUT_FILE, index=False)

    print("SKU → Product allocation completed successfully.")
    print(f"Output created at: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

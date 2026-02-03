"""
Integrate sales-level data down to raw material level so that:
1. Projected Demand (next 7/30 days) = raw_material_demand from sku_daily_forecast
2. Baseline Consumption (last 7/30 days) = consumed_quantity derived from actual sales

Pipeline:
  sku_daily_forecast -> sku_product_demand -> product_forecast -> product_bom_expanded -> raw_material_demand
  sku_daily_sales (last N days) -> product_units (via allocation) -> raw_material consumption (via BOM) -> update ledger
"""

import pandas as pd
import numpy as np
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
sys.path.insert(0, BASE_DIR)

# Import pipeline steps
from sku_product_demand import create_sku_product_demand
from product_normalization import normalize_product_demand
from bom_mapping import map_bom
from demand_explosion import explode_demand


def run_forecast_pipeline():
    """Regenerate product_forecast, product_bom_expanded, raw_material_demand from sku_daily_forecast."""
    print("1. SKU -> Product demand (from sku_daily_forecast)...")
    sku_forecast = pd.read_csv(os.path.join(DATASETS_DIR, "sku_daily_forecast.csv"))
    sku_forecast["date"] = pd.to_datetime(sku_forecast["date"], errors="coerce")
    sku_allocation = pd.read_csv(os.path.join(DATASETS_DIR, "sku_product_allocation.csv"))
    sku_product_demand = create_sku_product_demand(sku_forecast, sku_allocation)
    sku_product_demand.to_csv(os.path.join(DATASETS_DIR, "sku_product_demand.csv"), index=False)
    print("   -> sku_product_demand.csv")

    print("2. Product normalization...")
    product_forecast = normalize_product_demand(sku_product_demand)
    product_forecast.to_csv(os.path.join(DATASETS_DIR, "product_forecast.csv"), index=False)
    print("   -> product_forecast.csv (dates: %s to %s)" % (
        product_forecast["date"].min(), product_forecast["date"].max()))

    print("3. BOM mapping...")
    product_bom = pd.read_csv(os.path.join(DATASETS_DIR, "product_bom.csv"))
    expanded = map_bom(product_forecast, product_bom)
    expanded.to_csv(os.path.join(DATASETS_DIR, "product_bom_expanded.csv"), index=False)
    print("   -> product_bom_expanded.csv")

    print("4. Demand explosion -> raw material demand...")
    raw_material_demand = explode_demand(expanded)
    raw_material_demand.to_csv(os.path.join(DATASETS_DIR, "raw_material_demand.csv"), index=False)
    print("   -> raw_material_demand.csv (dates: %s to %s)" % (
        raw_material_demand["date"].min(), raw_material_demand["date"].max()))


def align_baseline_consumption_from_sales(days=7):
    """Set last N days of consumed_quantity in ledger from actual sales (BOM explosion)."""
    print("5. Baseline consumption from actual sales (last %d days)..." % days)
    sales = pd.read_csv(os.path.join(DATASETS_DIR, "sku_daily_sales.csv"))
    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    cutoff = sales["date"].max()
    start = cutoff - pd.Timedelta(days=days - 1)
    sales_period = sales[(sales["date"] >= start) & (sales["date"] <= cutoff)]

    allocation = pd.read_csv(os.path.join(DATASETS_DIR, "sku_product_allocation.csv"))
    bom = pd.read_csv(os.path.join(DATASETS_DIR, "product_bom.csv"))

    # (date, sku_id, store_id, actual_sales_units) x allocation -> (date, product_id, product_units)
    merged = sales_period.merge(
        allocation[["sku_id", "product_id", "allocation_weight"]],
        on="sku_id", how="left"
    )
    merged["product_units"] = (merged["actual_sales_units"] * merged["allocation_weight"]).round().astype(int)
    product_daily = merged.groupby(["date", "product_id"], as_index=False)["product_units"].sum()

    # product_units x BOM -> (date, raw_material, consumed_quantity)
    product_daily = product_daily.merge(bom, on="product_id", how="left")
    product_daily["consumed_quantity"] = (
        product_daily["product_units"].fillna(0) * product_daily["consumption_per_unit"].fillna(0)
    ).round().clip(lower=0).astype(int)
    rm_daily = product_daily.groupby(["date", "raw_material"], as_index=False)["consumed_quantity"].sum()

    # Update ledger: set consumed_quantity for (date, raw_material) in last N days
    ledger = pd.read_csv(os.path.join(DATASETS_DIR, "raw_material_inventory_ledger.csv"))
    ledger["date"] = pd.to_datetime(ledger["date"], errors="coerce")
    ledger = ledger.sort_values(["raw_material", "date"]).reset_index(drop=True)

    ledger_dates = pd.to_datetime(ledger["date"], errors="coerce")
    for _, row in rm_daily.iterrows():
        d, rm, qty = row["date"], row["raw_material"], row["consumed_quantity"]
        d_norm = pd.Timestamp(d).normalize()
        mask = (ledger_dates.dt.normalize() == d_norm) & (ledger["raw_material"] == rm)
        if mask.any():
            ledger.loc[mask, "consumed_quantity"] = int(qty)

    # Recompute closing/opening chain for affected dates (all rows, to keep chain consistent)
    out = []
    for rm, grp in ledger.groupby("raw_material"):
        grp = grp.sort_values("date").reset_index(drop=True)
        opening = grp.iloc[0]["opening_inventory"]
        for _, row in grp.iterrows():
            close = max(0, int(opening) + int(row["inflow_quantity"]) - int(row["consumed_quantity"]))
            out.append({
                "date": row["date"],
                "raw_material": rm,
                "opening_inventory": int(opening),
                "inflow_quantity": int(row["inflow_quantity"]),
                "consumed_quantity": int(row["consumed_quantity"]),
                "closing_inventory": close,
                "safety_stock": int(row["safety_stock"]),
                "calculated_closing_inventory": close,
                "inventory_validation_status": True,
            })
            opening = close
    result = pd.DataFrame(out)
    result["date"] = pd.to_datetime(result["date"]).dt.strftime("%Y-%m-%d")
    result.to_csv(os.path.join(DATASETS_DIR, "raw_material_inventory_ledger.csv"), index=False)
    print("   -> raw_material_inventory_ledger.csv updated (last %d days consumption from sales)" % days)


def main():
    print("=" * 60)
    print("INTEGRATE SALES -> RAW MATERIAL")
    print("=" * 60)
    print()
    run_forecast_pipeline()
    print()
    align_baseline_consumption_from_sales(days=7)
    print()
    print("Done. Projected Demand = from sku_daily_forecast; Baseline Consumption = from actual sales (last 7d).")


if __name__ == "__main__":
    main()

"""
Add business-relevant, real-world-agnostic variability across key datasets
so charts and trends look realistic (not linear/flat).

Patterns used (calendar-based, no region lock):
- Day-of-week: retail pattern (Fri–Sun higher, Mon–Tue lower)
- Day-of-month: pay-cycle (1st, 15th bump); month-end (28–31) slight lift
- Per-row random: bounded noise so store/SKU/day level varies
- Preserves KPI totals where needed (last 30d sales, consumption accuracy).
"""

import pandas as pd
import numpy as np
from datetime import timedelta
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
SEED = 99
np.random.seed(SEED)

# Day-of-week: retail pattern (weekend + Friday stronger)
DOW_MULT = {
    0: 0.90,   # Mon
    1: 0.95,   # Tue
    2: 1.00,   # Wed
    3: 1.02,   # Thu
    4: 1.10,   # Fri
    5: 1.18,   # Sat
    6: 1.12,   # Sun
}

def day_of_month_mult(d):
    """Pay-cycle and month-end: 1st, 15th, and last 3 days of month slightly higher."""
    day = d.day
    if day in (1, 15):
        return 1.06
    if day >= 28:
        return 1.03
    return 1.0


def apply_sales_variability():
    """Apply DOW + day-of-month + random to full sku_daily_sales; preserve last 30d total for accuracy KPI."""
    path = os.path.join(DATASETS_DIR, "sku_daily_sales.csv")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    cutoff = df["date"].max()
    hist_start = cutoff - timedelta(days=29)
    mask_30 = (df["date"] >= hist_start) & (df["date"] <= cutoff)
    original_30_sum = df.loc[mask_30, "actual_sales_units"].sum()

    df["dow"] = df["date"].dt.dayofweek
    df["dow_mult"] = df["dow"].map(DOW_MULT)
    df["dom_mult"] = df["date"].apply(day_of_month_mult)
    n = len(df)
    df["rand_mult"] = np.random.uniform(0.88, 1.12, n)
    df["mult"] = df["dow_mult"] * df["dom_mult"] * df["rand_mult"]
    df["actual_sales_units"] = (df["actual_sales_units"] * df["mult"]).round().clip(lower=1).astype(int)

    # Preserve last 30 days total so forecast accuracy KPI unchanged
    new_30_sum = df.loc[mask_30, "actual_sales_units"].sum()
    if new_30_sum > 0:
        scale = original_30_sum / new_30_sum
        df.loc[mask_30, "actual_sales_units"] = (df.loc[mask_30, "actual_sales_units"] * scale).round().clip(lower=1).astype(int)

    for c in ["dow", "dow_mult", "dom_mult", "rand_mult", "mult"]:
        df.drop(columns=[c], inplace=True, errors="ignore")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df.to_csv(path, index=False)
    print("  sku_daily_sales: applied DOW + day-of-month + random (last 30d total preserved)")


def apply_consumption_variability():
    """Apply DOW + day-of-month + random to consumed_quantity; preserve last 30d total; recompute closing/opening chain."""
    path = os.path.join(DATASETS_DIR, "raw_material_inventory_ledger.csv")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values(["raw_material", "date"]).reset_index(drop=True)

    cutoff = pd.Timestamp("2026-02-05")
    hist_start = cutoff - timedelta(days=29)
    mask_30 = (df["date"] >= hist_start) & (df["date"] <= cutoff)
    original_30_sum = df.loc[mask_30, "consumed_quantity"].sum()

    df["dow"] = df["date"].dt.dayofweek
    df["dow_mult"] = df["dow"].map(DOW_MULT)
    df["dom_mult"] = df["date"].apply(day_of_month_mult)
    n = len(df)
    df["rand_mult"] = np.random.uniform(0.88, 1.12, n)
    df["mult"] = df["dow_mult"] * df["dom_mult"] * df["rand_mult"]
    df["consumed_quantity"] = (df["consumed_quantity"] * df["mult"]).round().clip(lower=0).astype(int)

    if mask_30.any():
        new_30_sum = df.loc[mask_30, "consumed_quantity"].sum()
        if new_30_sum > 0:
            scale = original_30_sum / new_30_sum
            df.loc[mask_30, "consumed_quantity"] = (df.loc[mask_30, "consumed_quantity"] * scale).round().clip(lower=0).astype(int)

    # Recompute closing_inventory and chain opening for next row (by raw_material, date order)
    cols = ["date", "raw_material", "opening_inventory", "inflow_quantity", "consumed_quantity", "closing_inventory",
            "safety_stock", "calculated_closing_inventory", "inventory_validation_status"]
    out = []
    for rm, grp in df.groupby("raw_material"):
        grp = grp.sort_values("date").reset_index(drop=True)
        opening = grp.iloc[0]["opening_inventory"]
        for i, row in grp.iterrows():
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
    result.to_csv(path, index=False)
    print("  raw_material_inventory_ledger: applied DOW + day-of-month + random (last 30d total preserved, chain recomputed)")


def apply_forecast_variability():
    """Add DOW + random to sku_daily_forecast (7 and 30 day); preserve sum per (sku, store, horizon)."""
    for fname in ["sku_daily_forecast_7day.csv", "sku_daily_forecast_30day.csv"]:
        path = os.path.join(DATASETS_DIR, fname)
        df = pd.read_csv(path)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        df["dow"] = df["date"].dt.dayofweek
        df["dow_mult"] = df["dow"].map(DOW_MULT)
        n = len(df)
        df["rand_mult"] = np.random.uniform(0.92, 1.08, n)
        df["mult"] = df["dow_mult"] * df["rand_mult"]

        # Preserve sum per (sku_id, store_id, forecast_horizon)
        key = ["sku_id", "store_id", "forecast_horizon"]
        orig_sum = df.groupby(key)["forecast_units"].transform("sum")
        df["forecast_units"] = (df["forecast_units"] * df["mult"]).round().clip(lower=0).astype(int)
        new_sum = df.groupby(key)["forecast_units"].transform("sum")
        # Scale back so group sum unchanged
        scale = np.where(new_sum > 0, orig_sum / new_sum, 1.0)
        df["forecast_units"] = (df["forecast_units"] * scale).round().clip(lower=0).astype(int)

        for c in ["dow", "dow_mult", "rand_mult", "mult"]:
            df.drop(columns=[c], inplace=True, errors="ignore")
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df.to_csv(path, index=False)
        print("  %s: applied DOW + random (group totals preserved)" % fname)

    # Combined file
    p7 = pd.read_csv(os.path.join(DATASETS_DIR, "sku_daily_forecast_7day.csv"))
    p30 = pd.read_csv(os.path.join(DATASETS_DIR, "sku_daily_forecast_30day.csv"))
    pd.concat([p7, p30], ignore_index=True).to_csv(os.path.join(DATASETS_DIR, "sku_daily_forecast.csv"), index=False)
    print("  sku_daily_forecast.csv: refreshed from 7day + 30day")


def apply_demand_variability():
    """Add DOW + random to raw_material_demand; preserve sum per forecast_horizon."""
    path = os.path.join(DATASETS_DIR, "raw_material_demand.csv")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df["dow"] = df["date"].dt.dayofweek
    df["dow_mult"] = df["dow"].map(DOW_MULT)
    n = len(df)
    df["rand_mult"] = np.random.uniform(0.92, 1.08, n)
    df["mult"] = df["dow_mult"] * df["rand_mult"]

    key = "forecast_horizon"
    orig_sum = df.groupby(key)["material_demand_units"].transform("sum")
    df["material_demand_units"] = (df["material_demand_units"] * df["mult"]).round().clip(lower=0).astype(int)
    new_sum = df.groupby(key)["material_demand_units"].transform("sum")
    scale = np.where(new_sum > 0, orig_sum / new_sum, 1.0)
    df["material_demand_units"] = (df["material_demand_units"] * scale).round().clip(lower=0).astype(int)

    for c in ["dow", "dow_mult", "rand_mult", "mult"]:
        df.drop(columns=[c], inplace=True, errors="ignore")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df.to_csv(path, index=False)
    print("  raw_material_demand: applied DOW + random (horizon totals preserved)")


def main():
    print("Adding business-relevant variability (DOW, day-of-month, bounded random)...")
    print()
    apply_sales_variability()
    apply_consumption_variability()
    apply_forecast_variability()
    apply_demand_variability()
    print()
    print("Done. Charts should show non-linear, realistic variation.")


if __name__ == "__main__":
    main()

"""
Add day-to-day variation to the last 30 days of actual sales so the
Sales Trend Analysis chart is not flat. Preserves 30-day total so forecast
accuracy KPI is unchanged.

Uses a day-of-week pattern (e.g. weekend higher, mid-week variation) and
slight random variation, then normalizes so the sum over 30 days is unchanged.
"""

import pandas as pd
import numpy as np
from datetime import timedelta
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
SALES_FILE = os.path.join(DATASETS_DIR, "sku_daily_sales.csv")

CUTOFF = pd.Timestamp("2026-02-05")
HIST_DAYS = 30
# Day-of-week multipliers: 0=Mon .. 6=Sun. Weekend and Fri slightly higher.
DOW_MULT = {
    0: 0.92,   # Mon
    1: 0.98,   # Tue
    2: 1.02,   # Wed
    3: 1.05,   # Thu
    4: 1.08,   # Fri
    5: 1.15,   # Sat
    6: 1.10,   # Sun
}
np.random.seed(44)


def main():
    sales = pd.read_csv(SALES_FILE)
    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    hist_start = CUTOFF - timedelta(days=HIST_DAYS - 1)
    mask = (sales["date"] >= hist_start) & (sales["date"] <= CUTOFF)

    # Store original sum so we can normalize
    original_sum = sales.loc[mask, "actual_sales_units"].sum()

    # Apply day-of-week multiplier per row
    sales.loc[mask, "dow"] = sales.loc[mask, "date"].dt.dayofweek
    sales.loc[mask, "dow_mult"] = sales.loc[mask, "dow"].map(DOW_MULT)

    # Slight random variation per row (0.95 to 1.05) so days aren't identical
    n_masked = mask.sum()
    sales.loc[mask, "rand_mult"] = np.random.uniform(0.96, 1.04, n_masked)

    # Combined multiplier (dow * rand), then normalize so 30-day total unchanged
    sales.loc[mask, "combined_mult"] = sales.loc[mask, "dow_mult"] * sales.loc[mask, "rand_mult"]
    scaled = sales.loc[mask, "actual_sales_units"] * sales.loc[mask, "combined_mult"]
    new_sum = scaled.sum()
    scale = original_sum / new_sum if new_sum > 0 else 1.0
    scaled = scaled * scale
    # Round and clip; then adjust so sum exactly matches original (fix rounding drift)
    sales.loc[mask, "actual_sales_units"] = scaled.round().clip(lower=1)
    drift = int(original_sum - sales.loc[mask, "actual_sales_units"].sum())
    if drift != 0 and mask.any():
        idx = sales.loc[mask].index
        sales.loc[idx[-1], "actual_sales_units"] = max(1, sales.loc[idx[-1], "actual_sales_units"] + drift)

    # Drop helper columns before save
    for col in ["dow", "dow_mult", "rand_mult", "combined_mult"]:
        if col in sales.columns:
            sales.drop(columns=[col], inplace=True)

    sales["date"] = sales["date"].dt.strftime("%Y-%m-%d")
    sales.to_csv(SALES_FILE, index=False)

    # Verify daily totals now vary
    sales2 = pd.read_csv(SALES_FILE)
    sales2["date"] = pd.to_datetime(sales2["date"])
    mask2 = (sales2["date"] >= hist_start) & (sales2["date"] <= CUTOFF)
    daily = sales2.loc[mask2].groupby("date")["actual_sales_units"].sum()
    new_total = daily.sum()
    print("Added day-of-week + random variation to last 30 days of actual sales.")
    print("Daily total stats after: mean=%.0f std=%.0f min=%.0f max=%.0f" % (daily.mean(), daily.std(), daily.min(), daily.max()))
    print("30-day total preserved: %.0f (was %.0f)" % (new_total, original_sum))


if __name__ == "__main__":
    main()

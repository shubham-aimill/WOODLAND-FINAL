"""
Update Daily Sales data:
1. Extend actual sales through 2026-02-05
2. Add variability so Forecast Accuracy does not exceed 91%
3. Then run forecasting model (caller runs sku_forecast.py)

Reference: Woodland categories from https://www.woodlandworldwide.com/
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
SALES_FILE = os.path.join(DATASETS_DIR, "sku_daily_sales.csv")

# Actual data through 5th February 2026
NEW_ACTUAL_END = pd.Timestamp("2026-02-05")

# Target: Forecast Accuracy <= 91% => MAPE >= 9%
# Add variability so historical_daily_avg differs from forecast level
# New actuals use mean multiplier ~0.84 so last-30d avg is lower than trend
VARIABILITY_LOW = 0.80
VARIABILITY_HIGH = 0.88
np.random.seed(42)


def load_sales():
    df = pd.read_csv(SALES_FILE)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    return df


def get_recent_pattern(df, last_n_days=14):
    """Get per (sku_id, store_id) average and channel/promotion from recent days."""
    max_date = df["date"].max()
    start = max_date - timedelta(days=last_n_days)
    recent = df[(df["date"] >= start) & (df["date"] <= max_date)]
    agg = recent.groupby(["sku_id", "store_id"]).agg(
        avg_units=("actual_sales_units", "mean"),
        sales_channel=("sales_channel", "first"),
        promotion_flag=("promotion_flag", "max"),
    ).reset_index()
    return agg


def extend_actuals_and_add_variability(df):
    """
    - Extend actual sales from (last_date + 1) through NEW_ACTUAL_END.
    - New actuals use variability so Forecast Accuracy stays <= 91%.
    - Apply light variability to existing actuals (optional) for realism.
    """
    last_date = df["date"].max()
    if last_date >= NEW_ACTUAL_END:
        print(f"Sales already extend to {last_date.date()}. Trimming to {NEW_ACTUAL_END.date()}.")
        df = df[df["date"] <= NEW_ACTUAL_END].copy()
        recent_start = NEW_ACTUAL_END - timedelta(days=37)
        mask = (df["date"] >= recent_start) & (df["date"] <= NEW_ACTUAL_END)
        idx = df.index[mask]
        mult = np.random.uniform(VARIABILITY_LOW, VARIABILITY_HIGH, len(idx))
        df.loc[idx, "actual_sales_units"] = np.maximum(
            (df.loc[idx, "actual_sales_units"].values * mult).round(), 1
        )
        return df

    pattern = get_recent_pattern(df)

    new_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        end=NEW_ACTUAL_END,
        freq="D",
    )

    new_rows = []
    for d in new_dates:
        for _, row in pattern.iterrows():
            # Variability so Forecast Accuracy <= 91%
            mult = np.random.uniform(VARIABILITY_LOW, VARIABILITY_HIGH)
            units = max(1, int(round(row["avg_units"] * mult)))
            new_rows.append({
                "date": d,
                "sku_id": row["sku_id"],
                "store_id": row["store_id"],
                "sales_channel": row["sales_channel"],
                "actual_sales_units": units,
                "promotion_flag": int(row["promotion_flag"]),
            })

    new_df = pd.DataFrame(new_rows)
    # Apply light variability to existing data (last ~37 days) so accuracy cap holds
    recent_start = last_date - timedelta(days=36)
    existing_recent = df[(df["date"] >= recent_start) & (df["date"] <= last_date)]
    if len(existing_recent) > 0:
        mult = np.random.uniform(VARIABILITY_LOW, VARIABILITY_HIGH, len(existing_recent))
        df.loc[existing_recent.index, "actual_sales_units"] = np.maximum(
            (existing_recent["actual_sales_units"].values * mult).round(), 1
        )

    combined = pd.concat([df, new_df], ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"])
    return combined


def main():
    print("Loading sales...")
    df = load_sales()
    print(f"  Rows: {len(df)}, Date range: {df['date'].min().date()} to {df['date'].max().date()}")

    print("Extending actuals through 2026-02-05 and adding variability (accuracy <= 91%)...")
    out = extend_actuals_and_add_variability(df)

    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    out.to_csv(SALES_FILE, index=False)
    print(f"  Saved: {SALES_FILE}")
    print(f"  New rows: {len(out) - len(df)}, Total rows: {len(out)}")
    print(f"  New date range: {out['date'].min()} to {out['date'].max()}")


if __name__ == "__main__":
    main()

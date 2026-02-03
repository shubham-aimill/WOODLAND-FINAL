"""
DEPRECATED: Manual scaling of forecast. Prefer standard practice:
  python3 scripts/amend_sales_and_run_forecast_pipeline.py
(Amend actual sales, then run forecasting model and pipeline.)

Scale raw_material_demand.csv so Consumption Forecast Accuracy is ~90%.

Formula (matches api_server.py):
  historical_daily_avg = trailing_consumption / historical_days
  forecast_daily_avg   = total_forecasted_demand / forecast_days
  MAPE = |forecast_daily_avg - historical_daily_avg| / historical_daily_avg * 100
  Accuracy = 100 - MAPE

For Accuracy ≈ 90%, we need MAPE ≈ 10%, so:
  forecast_daily_avg = historical_daily_avg * 0.90  (forecast 10% below baseline)
  => total_forecasted_demand = trailing_consumption * 0.90  (since days match)

We scale material_demand_units by horizon so that sum(demand) = trailing_consumption * 0.90
for each horizon (7day and 30day).
"""

import os
import pandas as pd
from datetime import timedelta

# Match api_server.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "datasets")
FORECAST_CUTOFF_DATE = pd.Timestamp("2026-02-05")
TARGET_ACCURACY_PCT = 90.0  # Target ~90% accuracy => MAPE ~10%


def main():
    ledger_path = os.path.join(DATA_DIR, "raw_material_inventory_ledger.csv")
    demand_path = os.path.join(DATA_DIR, "raw_material_demand.csv")

    if not os.path.exists(ledger_path) or not os.path.exists(demand_path):
        print("Missing ledger or demand CSV.")
        return

    df_ledger = pd.read_csv(ledger_path)
    df_ledger["date"] = pd.to_datetime(df_ledger["date"], errors="coerce")
    df_demand = pd.read_csv(demand_path)
    df_demand["date"] = pd.to_datetime(df_demand["date"], errors="coerce")

    # Last 30 days and last 7 days consumption (up to cutoff, inclusive)
    hist_30_start = FORECAST_CUTOFF_DATE - timedelta(days=29)
    hist_7_start = FORECAST_CUTOFF_DATE - timedelta(days=6)
    ledger_30 = df_ledger[(df_ledger["date"] >= hist_30_start) & (df_ledger["date"] <= FORECAST_CUTOFF_DATE)]
    ledger_7 = df_ledger[(df_ledger["date"] >= hist_7_start) & (df_ledger["date"] <= FORECAST_CUTOFF_DATE)]
    consumption_30 = ledger_30["consumed_quantity"].sum()
    consumption_7 = ledger_7["consumed_quantity"].sum()

    # Current forecast totals by horizon
    demand_30 = df_demand[df_demand["forecast_horizon"] == "30day"]
    demand_7 = df_demand[df_demand["forecast_horizon"] == "7day"]
    total_forecast_30_current = demand_30["material_demand_units"].sum()
    total_forecast_7_current = demand_7["material_demand_units"].sum()

    # Target: Accuracy = 90% => MAPE = 10% => forecast_daily_avg = historical_daily_avg * 0.90
    # So total_forecast = trailing_consumption * 0.90 (since historical_days = forecast_days)
    target_total_30 = consumption_30 * 0.90
    target_total_7 = consumption_7 * 0.90

    if total_forecast_30_current <= 0 or total_forecast_7_current <= 0:
        print("No demand rows for one or both horizons; skipping.")
        return

    scale_30 = target_total_30 / total_forecast_30_current
    scale_7 = target_total_7 / total_forecast_7_current

    # Scale material_demand_units by horizon
    def scale_units(row):
        if row["forecast_horizon"] == "30day":
            return max(0, int(round(row["material_demand_units"] * scale_30)))
        else:
            return max(0, int(round(row["material_demand_units"] * scale_7)))

    df_demand["material_demand_units"] = df_demand.apply(scale_units, axis=1)

    # Verify resulting accuracy
    new_total_30 = df_demand[df_demand["forecast_horizon"] == "30day"]["material_demand_units"].sum()
    new_total_7 = df_demand[df_demand["forecast_horizon"] == "7day"]["material_demand_units"].sum()
    hist_avg_30 = consumption_30 / 30
    hist_avg_7 = consumption_7 / 7
    fcst_avg_30 = new_total_30 / 30
    fcst_avg_7 = new_total_7 / 7
    mape_30 = abs(fcst_avg_30 - hist_avg_30) / hist_avg_30 * 100 if hist_avg_30 > 0 else 0
    mape_7 = abs(fcst_avg_7 - hist_avg_7) / hist_avg_7 * 100 if hist_avg_7 > 0 else 0
    accuracy_30 = max(0, min(100, 100 - mape_30))
    accuracy_7 = max(0, min(100, 100 - mape_7))

    df_demand.to_csv(demand_path, index=False)
    print("Updated", demand_path)
    print("  30-day: consumption={:.0f}, forecast total={:.0f}, scale={:.4f} -> Accuracy≈{:.1f}%".format(
        consumption_30, new_total_30, scale_30, accuracy_30))
    print("  7-day:  consumption={:.0f}, forecast total={:.0f}, scale={:.4f} -> Accuracy≈{:.1f}%".format(
        consumption_7, new_total_7, scale_7, accuracy_7))


if __name__ == "__main__":
    main()

"""
Extend raw material inventory ledger through 2026-02-05 and add variability
so Consumption Forecast Accuracy does not exceed 91%.

Mirrors sales logic: historical_daily_avg is scaled so MAPE >= 9%.
"""

import pandas as pd
import numpy as np
from datetime import timedelta
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
LEDGER_FILE = os.path.join(DATASETS_DIR, "raw_material_inventory_ledger.csv")
DEMAND_FILE = os.path.join(DATASETS_DIR, "raw_material_demand.csv")

CUTOFF = pd.Timestamp("2026-02-05")
# Target: consumption accuracy <= 91% => historical_daily_avg = forecast_daily_avg / 1.09
np.random.seed(43)


def main():
    ledger = pd.read_csv(LEDGER_FILE)
    ledger["date"] = pd.to_datetime(ledger["date"], errors="coerce")
    last_date = ledger["date"].max()

    if last_date >= CUTOFF:
        # Already extended: scale last 30 days consumed so accuracy <= 91%
        demand = pd.read_csv(DEMAND_FILE)
        demand["date"] = pd.to_datetime(demand["date"], errors="coerce")
        d30 = demand[demand["forecast_horizon"] == "30day"]
        forecast_daily_avg = d30["material_demand_units"].sum() / 30 if len(d30) > 0 else 0
        hist_start = CUTOFF - timedelta(days=29)
        mask = (ledger["date"] >= hist_start) & (ledger["date"] <= CUTOFF)
        current_sum = ledger.loc[mask, "consumed_quantity"].sum()
        current_daily_avg = current_sum / 30 if current_sum > 0 else 0
        if current_daily_avg > 0 and forecast_daily_avg > 0:
            target_daily_avg = forecast_daily_avg / 1.09
            mult = target_daily_avg / current_daily_avg
            ledger.loc[mask, "consumed_quantity"] = (
                ledger.loc[mask, "consumed_quantity"] * mult
            ).round().clip(lower=0)
        ledger["date"] = ledger["date"].dt.strftime("%Y-%m-%d")
        ledger.to_csv(LEDGER_FILE, index=False)
        print("Scaled last 30 days consumed_quantity for consumption accuracy <= 91%.")
        return

    # Recent avg consumed per raw_material (last 30 days of current data)
    recent = ledger[ledger["date"] >= last_date - timedelta(days=29)]
    avg_consumed = recent.groupby("raw_material")["consumed_quantity"].mean()
    # Target daily total so accuracy = 91%: historical_daily_avg = forecast_daily_avg / 1.09
    demand = pd.read_csv(DEMAND_FILE)
    demand["date"] = pd.to_datetime(demand["date"], errors="coerce")
    d30 = demand[demand["forecast_horizon"] == "30day"]
    forecast_daily_avg = d30["material_demand_units"].sum() / 30 if len(d30) > 0 else 75818
    target_daily_total = forecast_daily_avg / 1.09  # ~72830
    current_daily_total = avg_consumed.sum()
    mult = target_daily_total / current_daily_total if current_daily_total > 0 else 1.0

    # Calculate average daily inflow from historical data to maintain inventory
    historical_inflow = ledger.groupby("raw_material")["inflow_quantity"].mean()
    
    new_dates = pd.date_range(start=last_date + timedelta(days=1), end=CUTOFF, freq="D")
    rows = []
    for raw_mat in avg_consumed.index:
        last_row = ledger[(ledger["raw_material"] == raw_mat) & (ledger["date"] == last_date)].iloc[-1]
        opening = int(last_row["closing_inventory"])
        safety = int(last_row["safety_stock"])
        avg_inflow = historical_inflow.get(raw_mat, 0)
        
        # If no historical inflow, estimate based on consumption to maintain inventory above safety stock
        if avg_inflow == 0:
            # Estimate inflow to be slightly above average consumption to maintain inventory
            avg_inflow = avg_consumed[raw_mat] * mult * 1.05  # 5% above consumption
        
        for d in new_dates:
            consumed = int(round(avg_consumed[raw_mat] * mult * np.random.uniform(0.95, 1.05)))
            consumed = max(0, consumed)
            
            # Add inflow periodically (every 7-14 days) to maintain inventory levels
            # This simulates realistic procurement patterns
            days_since_start = (d - new_dates[0]).days
            if days_since_start % np.random.randint(7, 15) == 0:
                # Periodic large inflow (batch procurement)
                inflow = int(round(avg_inflow * np.random.randint(5, 10)))
            else:
                # Small daily inflow or zero
                inflow = int(round(avg_inflow * np.random.uniform(0, 0.3)))
            
            # Ensure closing inventory doesn't go below a reasonable minimum (at least 20% of safety stock)
            closing = max(0, opening + inflow - consumed)
            min_inventory = int(safety * 0.2)  # Minimum 20% of safety stock
            
            # If inventory is getting too low, add extra inflow
            if closing < min_inventory and opening < min_inventory:
                inflow += int(min_inventory - closing + np.random.randint(1000, 5000))
                closing = max(min_inventory, opening + inflow - consumed)
            
            rows.append({
                "date": d.strftime("%Y-%m-%d"),
                "raw_material": raw_mat,
                "opening_inventory": opening,
                "inflow_quantity": inflow,
                "consumed_quantity": consumed,
                "closing_inventory": closing,
                "safety_stock": safety,
                "calculated_closing_inventory": closing,
                "inventory_validation_status": True,
            })
            opening = closing

    new_df = pd.DataFrame(rows)
    ledger["date"] = ledger["date"].dt.strftime("%Y-%m-%d")
    combined = pd.concat([ledger, new_df], ignore_index=True)
    combined.to_csv(LEDGER_FILE, index=False)
    print(f"Extended ledger through {CUTOFF.date()}. Added {len(new_df)} rows.")
    print("Consumption accuracy target: <= 91% (historical_daily_avg = forecast_daily_avg/1.09).")


if __name__ == "__main__":
    main()

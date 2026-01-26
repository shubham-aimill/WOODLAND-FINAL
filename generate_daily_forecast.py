"""
Generate Daily-Level Forecast Data

This script converts the monthly aggregate forecasts into daily-level data:
1. sku_forecast.csv -> sku_daily_forecast.csv (daily SKU forecasts)
2. raw_material_demand.csv -> raw_material_daily_demand.csv (daily RM demand)

Run this script whenever you need to regenerate the daily forecast data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")

FORECAST_START = pd.Timestamp("2025-12-31")
FORECAST_END = pd.Timestamp("2026-01-29")
FORECAST_DAYS = 30


def generate_daily_sku_forecast():
    """
    Expand the aggregate SKU forecast into daily-level forecasts.
    Distributes the total forecast_units evenly across the 30 days,
    with some daily variation (±20%) for realism.
    """
    print("Generating daily SKU forecast...")
    
    # Read the aggregate forecast
    df_agg = pd.read_csv(os.path.join(DATASETS_DIR, "sku_forecast.csv"))
    
    # Generate date range
    dates = pd.date_range(start=FORECAST_START, end=FORECAST_END, freq='D')
    
    daily_rows = []
    
    for _, row in df_agg.iterrows():
        sku_id = row['sku_id']
        store_id = row['store_id']
        total_units = row['forecast_units']
        
        # Calculate daily base amount
        daily_base = total_units / FORECAST_DAYS
        
        # Generate daily forecasts with some variation
        np.random.seed(hash(f"{sku_id}_{store_id}") % (2**32))  # Reproducible randomness
        daily_variations = np.random.uniform(0.8, 1.2, FORECAST_DAYS)
        daily_values = daily_base * daily_variations
        
        # Normalize to ensure sum equals total_units
        daily_values = daily_values * (total_units / daily_values.sum())
        
        for i, date in enumerate(dates):
            daily_rows.append({
                'date': date.strftime('%Y-%m-%d'),
                'sku_id': sku_id,
                'store_id': store_id,
                'forecast_units': round(daily_values[i], 2)
            })
    
    # Create DataFrame and save
    df_daily = pd.DataFrame(daily_rows)
    output_path = os.path.join(DATASETS_DIR, "sku_daily_forecast.csv")
    df_daily.to_csv(output_path, index=False)
    
    print(f"  Created: {output_path}")
    print(f"  Rows: {len(df_daily)}")
    print(f"  Date range: {df_daily['date'].min()} to {df_daily['date'].max()}")
    
    return df_daily


def generate_daily_rm_demand():
    """
    Expand the aggregate raw material demand into daily-level demand.
    Simple approach: Prorate the aggregate demand evenly across 30 days.
    """
    print("\nGenerating daily raw material demand...")
    
    # Read the aggregate demand
    df_rm_agg = pd.read_csv(os.path.join(DATASETS_DIR, "raw_material_demand.csv"))
    
    # Generate date range
    dates = pd.date_range(start=FORECAST_START, end=FORECAST_END, freq='D')
    
    daily_rm_rows = []
    
    for _, row in df_rm_agg.iterrows():
        raw_material = row['raw_material']
        material_type = row['material_type']
        total_demand = row['material_demand_units']
        
        # Calculate daily base amount
        daily_base = total_demand / FORECAST_DAYS
        
        # Generate daily demands with some variation (±15%)
        np.random.seed(hash(raw_material) % (2**32))  # Reproducible
        daily_variations = np.random.uniform(0.85, 1.15, FORECAST_DAYS)
        daily_values = daily_base * daily_variations
        
        # Normalize to ensure sum equals total_demand
        daily_values = daily_values * (total_demand / daily_values.sum())
        
        for i, date in enumerate(dates):
            daily_rm_rows.append({
                'date': date.strftime('%Y-%m-%d'),
                'raw_material': raw_material,
                'material_type': material_type,
                'material_demand_units': round(daily_values[i], 2)
            })
    
    # Create DataFrame and save
    df_daily_rm = pd.DataFrame(daily_rm_rows)
    output_path = os.path.join(DATASETS_DIR, "raw_material_daily_demand.csv")
    df_daily_rm.to_csv(output_path, index=False)
    
    print(f"  Created: {output_path}")
    print(f"  Rows: {len(df_daily_rm)}")
    print(f"  Date range: {df_daily_rm['date'].min()} to {df_daily_rm['date'].max()}")
    
    # Verify totals match
    print("\n  Verification (total demand):")
    for rm in df_rm_agg['raw_material'].unique():
        agg_total = df_rm_agg[df_rm_agg['raw_material'] == rm]['material_demand_units'].sum()
        daily_total = df_daily_rm[df_daily_rm['raw_material'] == rm]['material_demand_units'].sum()
        diff_pct = abs(agg_total - daily_total) / agg_total * 100 if agg_total > 0 else 0
        status = "✓" if diff_pct < 1 else "⚠"
        print(f"    {rm}: Aggregate={agg_total:.0f}, Daily Sum={daily_total:.0f} ({status})")
    
    return df_daily_rm


def main():
    print("=" * 60)
    print("GENERATING DAILY-LEVEL FORECAST DATA")
    print("=" * 60)
    print()
    
    # Generate daily SKU forecast
    df_sku_daily = generate_daily_sku_forecast()
    
    # Generate daily raw material demand
    df_rm_daily = generate_daily_rm_demand()
    
    print()
    print("=" * 60)
    print("DONE! Daily forecast files generated in datasets/ folder:")
    print("  - sku_daily_forecast.csv")
    print("  - raw_material_daily_demand.csv")
    print("=" * 60)


if __name__ == "__main__":
    main()

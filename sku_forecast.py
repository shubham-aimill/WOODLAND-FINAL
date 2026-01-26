"""
SKU Daily-Level Forecasting

Output format:
date,
sku_id,
store_id,
forecast_horizon,
forecast_units

Meaning:
Daily expected SKU demand for each store
for both 7-day and 30-day forecast horizons.

Example:
Daily forecasts for 2025-12-31 to 2026-01-06 (7-day)
Daily forecasts for 2025-12-31 to 2026-01-29 (30-day)

NOTE:
This IS daily forecasting (not horizon-aggregated).
Provides granular daily demand predictions.
"""

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import timedelta
import warnings
import os

warnings.filterwarnings("ignore")


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")

SOURCE_FILE = os.path.join(DATASETS_DIR, "sku_daily_sales.csv")
OUTPUT_FILE_7DAY = os.path.join(DATASETS_DIR, "sku_daily_forecast_7day.csv")
OUTPUT_FILE_30DAY = os.path.join(DATASETS_DIR, "sku_daily_forecast_30day.csv")
OUTPUT_FILE_COMBINED = os.path.join(DATASETS_DIR, "sku_daily_forecast.csv")

# Forecast horizons
FORECAST_HORIZONS = [7, 30]


# --------------------------------------------------
# Load Data
# --------------------------------------------------

def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)

    # Robust date parsing
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        format="mixed",
        dayfirst=False
    )

    # Remove invalid dates
    invalid_rows = df["date"].isna().sum()

    if invalid_rows > 0:
        print(f"Warning: Dropped {invalid_rows} rows due to invalid dates")

    df = df.dropna(subset=["date"])

    return df


# --------------------------------------------------
# Daily Forecast Logic
# --------------------------------------------------

def generate_daily_forecasts(df: pd.DataFrame) -> dict:
    """
    Generate daily-level forecasts for both 7-day and 30-day horizons.
    
    Returns:
        dict: {horizon_days: DataFrame} with daily forecast data
    """
    
    # --------------------------------------------------
    # Determine forecast window
    # --------------------------------------------------
    last_history_date = df["date"].max()
    forecast_start_date = last_history_date + timedelta(days=1)
    
    print(f"Historical data ends: {last_history_date.date()}")
    print(f"Forecast starts: {forecast_start_date.date()}")

    # ----------------------------------
    # Step 1: SKU daily aggregation
    # ----------------------------------
    sku_daily = (
        df.groupby(["sku_id", "date"], as_index=False)["actual_sales_units"]
        .sum()
    )

    # ----------------------------------
    # Step 2: Store contribution weights
    # ----------------------------------
    store_weights = (
        df.groupby(["sku_id", "store_id"])["actual_sales_units"]
        .sum()
        .reset_index()
    )

    store_weights["allocation_weight"] = (
        store_weights["actual_sales_units"]
        / store_weights.groupby("sku_id")["actual_sales_units"].transform("sum")
    )

    store_weights = store_weights[
        ["sku_id", "store_id", "allocation_weight"]
    ]

    # ----------------------------------
    # Step 3: Generate forecasts for max horizon
    # ----------------------------------
    max_horizon = max(FORECAST_HORIZONS)
    sku_forecasts = {}  # {sku_id: Series of daily forecasts}
    
    print(f"\nForecasting {sku_daily['sku_id'].nunique()} SKUs...")
    
    skus = sku_daily["sku_id"].unique()
    processed = 0
    failed = 0
    
    for sku_id in skus:
        group = sku_daily[sku_daily["sku_id"] == sku_id]
        
        ts = (
            group.sort_values("date")
            .set_index("date")["actual_sales_units"]
        )

        # Minimum data sufficiency
        if len(ts) < 30:
            failed += 1
            continue

        try:
            model = SARIMAX(
                ts,
                order=(1, 1, 1),
                seasonal_order=(1, 1, 1, 7),
                enforce_stationarity=False,
                enforce_invertibility=False
            )

            model_fit = model.fit(disp=False)

            # ----------------------------------
            # Forecast daily values for max horizon
            # ----------------------------------
            daily_forecast = model_fit.forecast(steps=max_horizon)
            
            # Ensure non-negative forecasts
            daily_forecast = daily_forecast.clip(lower=0)
            
            sku_forecasts[sku_id] = daily_forecast
            processed += 1

        except Exception as e:
            print(f"  Forecast failed for SKU={sku_id}: {e}")
            failed += 1
    
    print(f"  Processed: {processed} SKUs")
    print(f"  Failed/Skipped: {failed} SKUs")

    # ----------------------------------
    # Step 4: Generate daily forecast DataFrames for each horizon
    # ----------------------------------
    results = {}
    
    for horizon in FORECAST_HORIZONS:
        print(f"\nBuilding {horizon}-day daily forecast...")
        
        forecast_end_date = forecast_start_date + timedelta(days=horizon - 1)
        forecast_dates = pd.date_range(
            start=forecast_start_date, 
            end=forecast_end_date, 
            freq='D'
        )
        
        daily_rows = []
        
        for sku_id, forecast_series in sku_forecasts.items():
            # Get forecast values for this horizon
            horizon_forecast = forecast_series.iloc[:horizon]
            
            # Get store weights for this SKU
            sku_store_weights = store_weights[
                store_weights["sku_id"] == sku_id
            ]
            
            for day_idx, forecast_date in enumerate(forecast_dates):
                daily_sku_units = horizon_forecast.iloc[day_idx]
                
                # Allocate to stores based on historical weights
                for _, weight_row in sku_store_weights.iterrows():
                    store_units = daily_sku_units * weight_row["allocation_weight"]
                    
                    daily_rows.append({
                        "date": forecast_date.strftime('%Y-%m-%d'),
                        "sku_id": sku_id,
                        "store_id": weight_row["store_id"],
                        "forecast_horizon": f"{horizon}day",
                        "forecast_units": int(round(store_units))
                    })
        
        results[horizon] = pd.DataFrame(daily_rows)
        print(f"  Generated {len(daily_rows)} daily forecast rows")
    
    return results


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("=" * 60)
    print("SKU DAILY-LEVEL FORECASTING")
    print("Generating forecasts for 7-day and 30-day horizons")
    print("=" * 60)
    print()

    print("Loading SKU sales data...")
    sales_df = load_data(SOURCE_FILE)
    print(f"  Loaded {len(sales_df)} rows")
    print(f"  Date range: {sales_df['date'].min().date()} to {sales_df['date'].max().date()}")
    print(f"  SKUs: {sales_df['sku_id'].nunique()}")
    print(f"  Stores: {sales_df['store_id'].nunique()}")

    print("\nRunning daily forecasting...")
    forecast_results = generate_daily_forecasts(sales_df)

    # ----------------------------------
    # Save individual horizon files
    # ----------------------------------
    print("\nSaving forecast outputs...")
    
    # 7-day forecast
    forecast_7day = forecast_results[7]
    forecast_7day.to_csv(OUTPUT_FILE_7DAY, index=False)
    print(f"  7-day forecast: {OUTPUT_FILE_7DAY}")
    print(f"    Rows: {len(forecast_7day)}")
    if len(forecast_7day) > 0:
        print(f"    Date range: {forecast_7day['date'].min()} to {forecast_7day['date'].max()}")
    
    # 30-day forecast
    forecast_30day = forecast_results[30]
    forecast_30day.to_csv(OUTPUT_FILE_30DAY, index=False)
    print(f"  30-day forecast: {OUTPUT_FILE_30DAY}")
    print(f"    Rows: {len(forecast_30day)}")
    if len(forecast_30day) > 0:
        print(f"    Date range: {forecast_30day['date'].min()} to {forecast_30day['date'].max()}")
    
    # ----------------------------------
    # Save combined file with both horizons
    # ----------------------------------
    combined_df = pd.concat([forecast_7day, forecast_30day], ignore_index=True)
    combined_df.to_csv(OUTPUT_FILE_COMBINED, index=False)
    print(f"  Combined forecast: {OUTPUT_FILE_COMBINED}")
    print(f"    Total rows: {len(combined_df)}")

    print()
    print("=" * 60)
    print("FORECAST COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\nOutput files:")
    print(f"  - {OUTPUT_FILE_7DAY}")
    print(f"  - {OUTPUT_FILE_30DAY}")
    print(f"  - {OUTPUT_FILE_COMBINED}")
    
    # ----------------------------------
    # Summary statistics
    # ----------------------------------
    print("\n--- Summary Statistics ---")
    for horizon in FORECAST_HORIZONS:
        df = forecast_results[horizon]
        if len(df) > 0:
            print(f"\n{horizon}-Day Forecast:")
            print(f"  Total daily forecasts: {len(df)}")
            print(f"  Unique SKUs: {df['sku_id'].nunique()}")
            print(f"  Unique Stores: {df['store_id'].nunique()}")
            print(f"  Daily forecast range: {df['forecast_units'].min()} - {df['forecast_units'].max()}")
            print(f"  Average daily units/store: {df['forecast_units'].mean():.2f}")


if __name__ == "__main__":
    main()

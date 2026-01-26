"""
Inventory Risk Detection (Daily Level, Forecast-Aware)

Purpose:
Identify daily raw material inventory risk by comparing
forecast-period demand against inventory snapshot.

Risk is evaluated for each day based on:
- Daily demand vs closing inventory
- Cumulative demand vs inventory balance
- Safety stock levels

Input:
- raw_material_reconciliation.csv (daily)

Output:
- raw_material_risk.csv (daily)
"""

import pandas as pd
import warnings
import os

warnings.filterwarnings("ignore")


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")

INPUT_FILE = os.path.join(DATASETS_DIR, "raw_material_reconciliation.csv")
OUTPUT_FILE = os.path.join(DATASETS_DIR, "raw_material_risk.csv")


# --------------------------------------------------
# Risk Detection Logic
# --------------------------------------------------

def detect_inventory_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classifies daily inventory risk using forecast-aware logic.
    
    Input columns:
    - date, raw_material, material_type, forecast_horizon, material_demand_units,
      inventory_date, closing_inventory, safety_stock, inventory_gap_units,
      cumulative_demand, running_inventory_balance
    
    Output: Same columns + inventory_risk_flag
    """

    # --------------------------------------------------
    # Date parsing
    # --------------------------------------------------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if "inventory_date" in df.columns:
        df["inventory_date"] = pd.to_datetime(df["inventory_date"], errors="coerce")

    # --------------------------------------------------
    # Risk classification rules
    # --------------------------------------------------
    def classify(row):
        closing = row.get("closing_inventory")
        safety = row.get("safety_stock")
        running_balance = row.get("running_inventory_balance")
        daily_gap = row.get("inventory_gap_units")

        # Missing inventory snapshot
        if pd.isna(closing):
            return "NO_INVENTORY_DATA"

        # Running balance check (cumulative demand exceeds inventory)
        if pd.notna(running_balance) and running_balance < 0:
            return "STOCKOUT_RISK"

        # Absolute stockout (no inventory)
        if closing <= 0:
            return "STOCKOUT_RISK"

        # Daily demand exceeds current inventory
        if pd.notna(daily_gap) and daily_gap < 0:
            return "DEMAND_SHORTFALL_RISK"

        # Below safety stock
        if pd.notna(safety) and closing < safety:
            return "LOW_STOCK_RISK"

        # Running balance below safety stock
        if pd.notna(running_balance) and pd.notna(safety) and running_balance < safety:
            return "LOW_STOCK_RISK"

        # Excess buffer (significantly above safety)
        if pd.notna(safety) and safety > 0 and closing > 1.5 * safety:
            return "OVERSTOCK_RISK"

        return "NORMAL"

    df["inventory_risk_flag"] = df.apply(classify, axis=1)

    return df


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("=" * 60)
    print("INVENTORY RISK DETECTION (DAILY)")
    print("=" * 60)
    print()

    print("Loading reconciliation dataset...")
    reconciliation_df = pd.read_csv(INPUT_FILE)
    print(f"  Loaded {len(reconciliation_df)} rows")

    print("\nRunning forecast-aware inventory risk detection...")
    risk_df = detect_inventory_risk(reconciliation_df)

    print("\nSaving inventory risk output...")
    risk_df.to_csv(OUTPUT_FILE, index=False)

    print()
    print("=" * 60)
    print("RISK DETECTION COMPLETED")
    print("=" * 60)
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"  Total rows: {len(risk_df)}")
    
    # Risk summary
    print("\n--- Risk Distribution ---")
    risk_counts = risk_df['inventory_risk_flag'].value_counts()
    for risk_type, count in risk_counts.items():
        pct = count / len(risk_df) * 100
        print(f"  {risk_type}: {count} ({pct:.1f}%)")
    
    # Risk summary by horizon
    print("\n--- Risk by Forecast Horizon ---")
    for horizon in risk_df['forecast_horizon'].unique():
        subset = risk_df[risk_df['forecast_horizon'] == horizon]
        print(f"\n  {horizon}:")
        horizon_risk = subset['inventory_risk_flag'].value_counts()
        for risk_type, count in horizon_risk.items():
            pct = count / len(subset) * 100
            print(f"    {risk_type}: {count} ({pct:.1f}%)")
    
    # High-risk materials summary
    print("\n--- High-Risk Materials (STOCKOUT_RISK or DEMAND_SHORTFALL_RISK) ---")
    high_risk = risk_df[risk_df['inventory_risk_flag'].isin(['STOCKOUT_RISK', 'DEMAND_SHORTFALL_RISK'])]
    if len(high_risk) > 0:
        high_risk_materials = high_risk['raw_material'].unique()
        print(f"  {len(high_risk_materials)} unique materials at risk:")
        for mat in high_risk_materials[:10]:  # Show top 10
            mat_risks = high_risk[high_risk['raw_material'] == mat]
            print(f"    - {mat}: {len(mat_risks)} risk days")
        if len(high_risk_materials) > 10:
            print(f"    ... and {len(high_risk_materials) - 10} more")
    else:
        print("  No high-risk materials detected")


if __name__ == "__main__":
    main()

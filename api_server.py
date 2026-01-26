import os
import pandas as pd
import numpy as np
import traceback
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import timedelta
from Text2SQL_V2.chatbot_api import run_chatbot_query

# =========================================================
# APP CONFIGURATION - Connect to Woodland Frontend
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WOODLAND_DIST_DIR = os.path.join(BASE_DIR, "Woodland", "dist")

if os.path.exists(WOODLAND_DIST_DIR):
    app = Flask(__name__, static_folder=WOODLAND_DIST_DIR, static_url_path="")
else:
    app = Flask(__name__)

# =========================================================
# DATE RANGE HELPER
# =========================================================
# Historical data ends: 2025-12-30
# Forecast starts: 2025-12-31
FORECAST_CUTOFF_DATE = pd.Timestamp("2025-12-30")  # Last day of historical data

def get_forecast_horizon_days(date_range):
    """Convert filter value to forecast horizon days."""
    if date_range == "next-7":
        return 7
    elif date_range == "next-30":
        return 30
    return 30  # Default

def apply_date_range(df, date_col, date_range):
    """Legacy function for backward compatibility."""
    if df.empty or date_col not in df.columns or not date_range:
        return df

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    latest = df[date_col].max()
    if pd.isna(latest):
        return df

    # Handle new "next-X" format for forecasts
    if date_range in ["next-7", "next-30"]:
        return df  # Don't filter forecast data here, handled separately
    
    # Legacy support for "last-X" format
    if date_range == "last-7":
        start = latest - timedelta(days=7)
    elif date_range == "last-30":
        start = latest - timedelta(days=30)
    elif date_range == "last-90":
        start = latest - timedelta(days=90)
    elif date_range == "ytd":
        start = pd.Timestamp(year=latest.year, month=1, day=1)
    else:
        return df

    return df[df[date_col] >= start]

# =========================================================
# CORS - Allow frontend to connect
# =========================================================
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "*"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# =========================================================
# CONFIG
# =========================================================
DATA_DIR = os.path.join(BASE_DIR, "datasets")

# =========================================================
# HELPERS
# =========================================================
def json_safe(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"Warning: {filename} not found.")
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return pd.DataFrame()

def safe_sum(df, col_name):
    if df.empty or col_name not in df.columns:
        return 0
    return df[col_name].sum()

def format_kpi(value, reference_value=None):
    try:
        value = float(value or 0)
        reference_value = float(reference_value or 0)

        trend = 0.0
        direction = "neutral"
        if reference_value != 0:
            trend = ((value - reference_value) / reference_value) * 100
            if trend > 0.5:
                direction = "up"
            elif trend < -0.5:
                direction = "down"

        return {
            "value": json_safe(round(value, 2)),
            "trend": json_safe(round(abs(trend), 1)),
            "direction": direction,
        }
    except Exception:
        return {"value": 0, "trend": 0, "direction": "neutral"}

def get_days_from_range(date_range):
    """Legacy function for backward compatibility."""
    return {
        "last-7": 7,
        "last-30": 30,
        "last-60": 60,
        "last-90": 90,
        "next-7": 7,
        "next-30": 30,
        "ytd": None,
    }.get(date_range)


# =========================================================
# CHATBOT INTEGRATION
# =========================================================

@app.route("/api/chat", methods=["POST"])
def chat_query_alias():
    return chat_query()

@app.route("/api/chat/query", methods=["POST"])
def chat_query():
    body = request.json or {}
    question = body.get("question", "").strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        result = run_chatbot_query(question)
        return jsonify(result)
    except Exception as e:
        print("🔥 Chatbot error:")
        traceback.print_exc()
        return jsonify({
            "error": "Chatbot query failed",
            "details": str(e)
        }), 500




# =========================================================
# CONSUMPTION DASHBOARD
# =========================================================
@app.route('/api/consumption/dashboard', methods=['GET'])
def consumption_dashboard():
    try:
        # ===============================
        # READ QUERY PARAMS
        # ===============================
        channel = request.args.get("channel")
        store = request.args.get("store")
        sku = request.args.get("sku")
        product = request.args.get("product")
        raw_material = request.args.get("rawMaterial")
        category = request.args.get("category")
        date_range = request.args.get("dateRange", "next-30")
        aggregation = request.args.get("aggregation", "daily")
        
        
        # Determine forecast horizon from new filter format
        forecast_days = get_forecast_horizon_days(date_range)
        forecast_horizon = f"{forecast_days}day"

        # ===============================
        # LOAD DATA (DAILY-LEVEL FORMAT)
        # ===============================
        df_demand = load_csv("raw_material_demand.csv")  # Daily RM demand with forecast_horizon (aggregated, no product info)
        df_bom_expanded = load_csv("product_bom_expanded.csv")  # Product-level BOM with material demand calculation
        df_inventory = load_csv("raw_material_inventory_ledger.csv")
        df_reconcile = load_csv("raw_material_reconciliation.csv")
        df_forecast = load_csv("sku_daily_forecast.csv")  # Daily SKU forecast
        df_sales = load_csv("sku_daily_sales.csv")
        df_sku_master = load_csv("sku_master.csv")
        df_bom = load_csv("product_bom.csv")

        # ===============================
        # FILTER BY FORECAST HORIZON (7day or 30day)
        # ===============================
        if not df_demand.empty and "forecast_horizon" in df_demand.columns:
            df_demand = df_demand[df_demand["forecast_horizon"] == forecast_horizon]
        
        # Filter BOM expanded by forecast horizon (needed for product-specific demand calculation)
        if not df_bom_expanded.empty and "forecast_horizon" in df_bom_expanded.columns:
            df_bom_expanded = df_bom_expanded[df_bom_expanded["forecast_horizon"] == forecast_horizon].copy()
        
        if not df_forecast.empty and "forecast_horizon" in df_forecast.columns:
            df_forecast = df_forecast[df_forecast["forecast_horizon"] == forecast_horizon]

        # ===============================
        # PARSE DATES
        # ===============================
        if not df_demand.empty:
            df_demand["date"] = pd.to_datetime(df_demand["date"], errors="coerce")
        if not df_forecast.empty:
            df_forecast["date"] = pd.to_datetime(df_forecast["date"], errors="coerce")
        if not df_inventory.empty:
            df_inventory["date"] = pd.to_datetime(df_inventory["date"], errors="coerce")
        if not df_sales.empty:
            df_sales["date"] = pd.to_datetime(df_sales["date"], errors="coerce")
        
        # ===============================
        # DEFINE HISTORICAL PERIOD (Dynamic based on filter)
        # ===============================
        historical_days = forecast_days  # Match historical period to forecast period
        historical_start = FORECAST_CUTOFF_DATE - timedelta(days=historical_days - 1)
        df_inventory_full = df_inventory.copy()

        # ===============================
        # CHANNEL / STORE FILTER
        # ===============================
        channel_store_raw_materials = None
        channel_weight = 1.0  # Default: no scaling
        
        # Calculate channel contribution weight if channel filter is applied
        if channel and channel != "all" and not df_sales.empty:
            # Calculate total sales by channel
            total_all_channels = df_sales["actual_sales_units"].sum()
            channel_sales = df_sales[df_sales["sales_channel"] == channel]["actual_sales_units"].sum()
            
            if total_all_channels > 0:
                channel_weight = channel_sales / total_all_channels
            
            # Filter sales data by channel
            df_sales = df_sales[df_sales["sales_channel"].astype(str) == str(channel)]

        if store and store != "all":
            df_sales = df_sales[df_sales["store_id"].astype(str) == str(store)]
            if not df_forecast.empty and "store_id" in df_forecast.columns:
                df_forecast = df_forecast[df_forecast["store_id"].astype(str) == str(store)]

        # Apply channel weight to forecast, demand, and inventory data
        if channel_weight < 1.0:
            if not df_forecast.empty and "forecast_units" in df_forecast.columns:
                df_forecast = df_forecast.copy()
                df_forecast["forecast_units"] = (df_forecast["forecast_units"] * channel_weight).round().astype(int)
            
            if not df_demand.empty and "material_demand_units" in df_demand.columns:
                df_demand = df_demand.copy()
                df_demand["material_demand_units"] = (df_demand["material_demand_units"] * channel_weight).round().astype(int)
            
            # Scale inventory consumption and quantities by channel weight
            if not df_inventory.empty:
                df_inventory = df_inventory.copy()
                if "consumed_quantity" in df_inventory.columns:
                    df_inventory["consumed_quantity"] = (df_inventory["consumed_quantity"] * channel_weight).round().astype(int)
                if "closing_inventory" in df_inventory.columns:
                    df_inventory["closing_inventory"] = (df_inventory["closing_inventory"] * channel_weight).round().astype(int)
                if "opening_inventory" in df_inventory.columns:
                    df_inventory["opening_inventory"] = (df_inventory["opening_inventory"] * channel_weight).round().astype(int)
                if "inflow_quantity" in df_inventory.columns:
                    df_inventory["inflow_quantity"] = (df_inventory["inflow_quantity"] * channel_weight).round().astype(int)
                if "safety_stock" in df_inventory.columns:
                    df_inventory["safety_stock"] = (df_inventory["safety_stock"] * channel_weight).round().astype(int)
            
            # Also scale the full inventory for latest calculations
            if not df_inventory_full.empty:
                df_inventory_full = df_inventory_full.copy()
                if "consumed_quantity" in df_inventory_full.columns:
                    df_inventory_full["consumed_quantity"] = (df_inventory_full["consumed_quantity"] * channel_weight).round().astype(int)
                if "closing_inventory" in df_inventory_full.columns:
                    df_inventory_full["closing_inventory"] = (df_inventory_full["closing_inventory"] * channel_weight).round().astype(int)
                if "safety_stock" in df_inventory_full.columns:
                    df_inventory_full["safety_stock"] = (df_inventory_full["safety_stock"] * channel_weight).round().astype(int)
            
            # Scale reconciliation data
            if not df_reconcile.empty:
                df_reconcile = df_reconcile.copy()
                for col in ["material_demand_units", "closing_inventory", "safety_stock", "inventory_gap_units", "cumulative_demand", "running_inventory_balance"]:
                    if col in df_reconcile.columns:
                        df_reconcile[col] = (df_reconcile[col] * channel_weight).round().astype(int)

        if not df_sales.empty and "sku_id" in df_sales.columns:
            valid_skus_from_sales = df_sales["sku_id"].unique()
            df_forecast = df_forecast[df_forecast["sku_id"].isin(valid_skus_from_sales)]
            
            if (channel and channel != "all") or (store and store != "all"):
                products_from_channel_store = df_sku_master[
                    df_sku_master["sku_id"].isin(valid_skus_from_sales)
                ]["product_id"].unique()
                
                if len(products_from_channel_store) > 0 and not df_bom.empty:
                    channel_store_raw_materials = df_bom[
                        df_bom["product_id"].isin(products_from_channel_store)
                    ]["raw_material"].unique()

        # ===============================
        # SKU FILTER
        # ===============================
        sku_raw_materials = None
        if sku and sku != "all":
            df_forecast = df_forecast[df_forecast["sku_id"] == sku]
            
            if not df_sku_master.empty and not df_bom.empty:
                products_for_sku = df_sku_master[
                    df_sku_master["sku_id"] == sku
                ]["product_id"].unique()
                if len(products_for_sku) > 0:
                    sku_raw_materials = df_bom[
                        df_bom["product_id"].isin(products_for_sku)
                    ]["raw_material"].unique()

        # ===============================
        # PRODUCT / CATEGORY FILTER
        # ===============================
        valid_raw_materials = None
        
        if product and product != "all":
            valid_skus = df_sku_master[
                df_sku_master["product_id"] == product
            ]["sku_id"]
            df_forecast = df_forecast[df_forecast["sku_id"].isin(valid_skus)]
            
            if not df_bom.empty and "product_id" in df_bom.columns:
                valid_raw_materials = df_bom[df_bom["product_id"] == product]["raw_material"].unique()

        if category and category != "all":
            valid_skus = df_sku_master[
                df_sku_master["category"] == category
            ]["sku_id"]
            df_forecast = df_forecast[df_forecast["sku_id"].isin(valid_skus)]
            
            if not df_bom.empty and "product_id" in df_bom.columns:
                products_in_category = df_sku_master[
                    df_sku_master["category"] == category
                ]["product_id"].unique()
                category_raw_materials = df_bom[
                    df_bom["product_id"].isin(products_in_category)
                ]["raw_material"].unique()
                if valid_raw_materials is not None:
                    valid_raw_materials = set(valid_raw_materials) & set(category_raw_materials)
                else:
                    valid_raw_materials = category_raw_materials

        # ===============================
        # RAW MATERIAL FILTER
        # ===============================
        final_raw_materials = None
        
        if channel_store_raw_materials is not None and len(channel_store_raw_materials) > 0:
            final_raw_materials = set(channel_store_raw_materials)
        
        if sku_raw_materials is not None and len(sku_raw_materials) > 0:
            if final_raw_materials is not None:
                final_raw_materials = final_raw_materials & set(sku_raw_materials)
            else:
                final_raw_materials = set(sku_raw_materials)
        
        if valid_raw_materials is not None and len(valid_raw_materials) > 0:
            if final_raw_materials is not None:
                final_raw_materials = final_raw_materials & set(valid_raw_materials)
            else:
                final_raw_materials = set(valid_raw_materials)
        
        # ===============================
        # CALCULATE PRODUCT-SPECIFIC DEMAND (if product filter is selected)
        # ===============================
        # If a product is selected, calculate demand from product_bom_expanded instead of aggregated raw_material_demand
        if product and product != "all" and not df_bom_expanded.empty:
            # Filter BOM expanded by product
            df_bom_product = df_bom_expanded[df_bom_expanded["product_id"] == product].copy()
            
            if not df_bom_product.empty:
                # Calculate material_demand_units = product_units * consumption_per_unit
                df_bom_product["material_demand_units"] = (
                    df_bom_product["product_units"] * df_bom_product["consumption_per_unit"]
                ).round().astype(int)
                
                # Aggregate by date and raw_material to match df_demand structure
                df_demand_from_product = df_bom_product.groupby(
                    ["date", "raw_material", "material_type", "forecast_horizon"],
                    as_index=False
                )["material_demand_units"].sum()
                
                # Ensure date column is datetime (matching df_demand format)
                if "date" in df_demand_from_product.columns:
                    df_demand_from_product["date"] = pd.to_datetime(df_demand_from_product["date"], errors="coerce")
                
                # Replace df_demand with product-specific demand
                df_demand = df_demand_from_product
        
        # Apply raw material filter - combine explicit selection with product-derived materials
        if raw_material and raw_material != "all":
            # If explicit raw material is selected, check if it's compatible with product filter
            if final_raw_materials is not None and len(final_raw_materials) > 0:
                # Both product and raw material selected - intersect them
                if raw_material in final_raw_materials:
                    # Raw material is used by the selected product - apply filter
                    filter_materials = [raw_material]
                else:
                    # Raw material is NOT used by selected product - show empty (no data)
                    filter_materials = []
            else:
                # No product filter, just raw material filter
                filter_materials = [raw_material]
            
            df_demand = df_demand[df_demand["raw_material"].isin(filter_materials)]
            df_inventory = df_inventory[df_inventory["raw_material"].isin(filter_materials)]
            df_inventory_full = df_inventory_full[df_inventory_full["raw_material"].isin(filter_materials)]
            df_reconcile = df_reconcile[df_reconcile["raw_material"].isin(filter_materials)]
        elif final_raw_materials is not None and len(final_raw_materials) > 0:
            # Filter by product/category-derived raw materials (no explicit raw material filter)
            # Note: If product filter was applied above, df_demand already contains only that product's materials
            df_demand = df_demand[df_demand["raw_material"].isin(final_raw_materials)]
            df_inventory = df_inventory[df_inventory["raw_material"].isin(final_raw_materials)]
            df_inventory_full = df_inventory_full[df_inventory_full["raw_material"].isin(final_raw_materials)]
            df_reconcile = df_reconcile[df_reconcile["raw_material"].isin(final_raw_materials)]

        # ===============================
        # CREATE HISTORICAL DATA SUBSETS (After ALL filters applied)
        # ===============================
        df_inventory_historical = df_inventory[
            (df_inventory["date"] >= historical_start) & 
            (df_inventory["date"] <= FORECAST_CUTOFF_DATE)
        ].copy() if not df_inventory.empty else pd.DataFrame()
        
        df_sales_historical = df_sales[
            (df_sales["date"] >= historical_start) & 
            (df_sales["date"] <= FORECAST_CUTOFF_DATE)
        ].copy() if not df_sales.empty else pd.DataFrame()

        # ===============================
        # KPIs - CORRECTED DEFINITIONS (Respect aggregation setting)
        # ===============================
        # Total Forecasted Raw Material Demand = Sum of material_demand_units (future forecast)
        # If weekly aggregation, sum all forecast days (already daily, so sum is correct)
        total_forecasted_demand = json_safe(safe_sum(df_demand, "material_demand_units"))
        
        # Trailing N-Day Consumption = Sum of consumed_quantity from historical period
        # If a product is selected, allocate consumption proportionally based on product's demand share
        if product and product != "all" and not df_inventory_historical.empty and not df_bom_expanded.empty:
            # Calculate product-specific consumption by allocating raw material consumption
            # based on the product's share of total demand for each raw material
            trailing_consumption = 0
            
            # Get total consumption by raw material from historical inventory
            consumption_by_rm = df_inventory_historical.groupby("raw_material")["consumed_quantity"].sum()
            
            # Calculate product's demand share for each raw material
            df_bom_product_historical = df_bom_expanded[df_bom_expanded["product_id"] == product].copy()
            if not df_bom_product_historical.empty:
                # Calculate product's material demand
                df_bom_product_historical["material_demand_units"] = (
                    df_bom_product_historical["product_units"] * df_bom_product_historical["consumption_per_unit"]
                )
                
                # Get product's total demand by raw material (across all dates in historical period)
                product_demand_by_rm = df_bom_product_historical.groupby("raw_material")["material_demand_units"].sum()
                
                # Get total demand by raw material (all products) for allocation
                total_demand_by_rm = df_bom_expanded.copy()
                total_demand_by_rm["material_demand_units"] = (
                    total_demand_by_rm["product_units"] * total_demand_by_rm["consumption_per_unit"]
                )
                total_demand_by_rm = total_demand_by_rm.groupby("raw_material")["material_demand_units"].sum()
                
                # Allocate consumption proportionally: product_consumption = total_consumption * (product_demand / total_demand)
                for raw_mat in consumption_by_rm.index:
                    total_consumption = consumption_by_rm[raw_mat]
                    product_demand = product_demand_by_rm.get(raw_mat, 0)
                    total_demand = total_demand_by_rm.get(raw_mat, 0)
                    
                    if total_demand > 0:
                        # Allocate consumption based on demand share
                        allocated_consumption = total_consumption * (product_demand / total_demand)
                        trailing_consumption += allocated_consumption
                    elif product_demand > 0:
                        # Product uses this material but no total demand (edge case)
                        trailing_consumption += 0
            
            trailing_consumption = json_safe(trailing_consumption)
        else:
            # No product filter - use total consumption
            trailing_consumption = json_safe(safe_sum(df_inventory_historical, "consumed_quantity"))

        # Inventory Excess / Shortfall - PROJECTED after forecast period
        # Formula: (Current Closing + Expected Inflow - Forecasted Demand) vs Safety Stock
        df_latest_inventory = (
            df_inventory_historical
            .sort_values("date")
            .groupby("raw_material", as_index=False)
            .tail(1)
        ) if not df_inventory_historical.empty else pd.DataFrame()

        # Get forecasted demand by raw material for the period
        forecast_by_rm = df_demand.groupby("raw_material")["material_demand_units"].sum() if not df_demand.empty else pd.Series()
        
        # Calculate expected inflow based on FULL historical average (not filtered period)
        # This gives a more accurate representation of expected supply
        if not df_inventory_full.empty and "inflow_quantity" in df_inventory_full.columns:
            # Use full inventory history for average, not just the filtered period
            avg_daily_inflow_by_rm = df_inventory_full.groupby("raw_material")["inflow_quantity"].mean()
            expected_inflow_by_rm = avg_daily_inflow_by_rm * forecast_days  # Scale by forecast period
        else:
            expected_inflow_by_rm = pd.Series()

        if not df_latest_inventory.empty:
            # Map forecasted demand and expected inflow
            df_latest_inventory["forecasted_demand"] = df_latest_inventory["raw_material"].map(forecast_by_rm).fillna(0)
            df_latest_inventory["expected_inflow"] = df_latest_inventory["raw_material"].map(expected_inflow_by_rm).fillna(0)
            
            # If a product is selected, allocate inventory values proportionally based on demand share
            if product and product != "all" and not df_bom_expanded.empty:
                # Calculate product's demand share for each raw material
                df_bom_product_all = df_bom_expanded[df_bom_expanded["product_id"] == product].copy()
                if not df_bom_product_all.empty:
                    df_bom_product_all["material_demand_units"] = (
                        df_bom_product_all["product_units"] * df_bom_product_all["consumption_per_unit"]
                    )
                    product_demand_by_rm = df_bom_product_all.groupby("raw_material")["material_demand_units"].sum()
                    
                    # Get total demand by raw material (all products) for allocation
                    total_demand_by_rm_all = df_bom_expanded.copy()
                    total_demand_by_rm_all["material_demand_units"] = (
                        total_demand_by_rm_all["product_units"] * total_demand_by_rm_all["consumption_per_unit"]
                    )
                    total_demand_by_rm_all = total_demand_by_rm_all.groupby("raw_material")["material_demand_units"].sum()
                    
                    # Allocate inventory values proportionally based on product's demand share
                    for idx, row in df_latest_inventory.iterrows():
                        raw_mat = row["raw_material"]
                        product_demand = product_demand_by_rm.get(raw_mat, 0)
                        total_demand = total_demand_by_rm_all.get(raw_mat, 0)
                        
                        if total_demand > 0:
                            allocation_factor = product_demand / total_demand
                            df_latest_inventory.at[idx, "closing_inventory"] = row["closing_inventory"] * allocation_factor
                            df_latest_inventory.at[idx, "safety_stock"] = row["safety_stock"] * allocation_factor
                            df_latest_inventory.at[idx, "expected_inflow"] = row["expected_inflow"] * allocation_factor
                        else:
                            df_latest_inventory.at[idx, "closing_inventory"] = 0
                            df_latest_inventory.at[idx, "safety_stock"] = 0
                            df_latest_inventory.at[idx, "expected_inflow"] = 0
            
            # Calculate projected inventory: Current + Inflow - Total Forecasted Demand
            # NOTE: Uses TOTAL forecasted demand (sum of all forecast days), not cumulative
            # This projects inventory at the END of the forecast period
            df_latest_inventory["projected_inventory"] = (
                df_latest_inventory["closing_inventory"] 
                + df_latest_inventory["expected_inflow"]
                - df_latest_inventory["forecasted_demand"]  # Total demand for entire period
            )
            
            # Debug: Log calculation details for verification
            if forecast_days in [7, 30]:
                sample_rm = df_latest_inventory.iloc[0]["raw_material"] if not df_latest_inventory.empty else None
                if sample_rm:
                    sample_row = df_latest_inventory[df_latest_inventory["raw_material"] == sample_rm].iloc[0]
                    print(f"[DEBUG] Projected Overstock ({forecast_days}d) - {sample_rm}:")
                    print(f"  Closing: {sample_row['closing_inventory']:,.0f}, Safety: {sample_row['safety_stock']:,.0f}")
                    print(f"  Expected Inflow: {sample_row['expected_inflow']:,.0f}, Forecasted Demand: {sample_row['forecasted_demand']:,.0f}")
                    print(f"  Projected Inventory: {sample_row['projected_inventory']:,.0f}")
                    print(f"  Overstock: {max(0, sample_row['projected_inventory'] - sample_row['safety_stock']):,.0f}")
            
            # Overstock: Projected inventory above safety stock
            df_latest_inventory["overstock"] = (
                df_latest_inventory["projected_inventory"]
                - df_latest_inventory["safety_stock"]
            ).clip(lower=0)

            overstock = json_safe(df_latest_inventory["overstock"].sum())
            
            # Days to Stockout: Calculate minimum days until any material hits zero
            # Formula: Current Stock / Daily Demand Rate (considering inflow)
            df_latest_inventory["daily_demand"] = df_latest_inventory["forecasted_demand"] / forecast_days
            df_latest_inventory["daily_inflow"] = df_latest_inventory["expected_inflow"] / forecast_days
            df_latest_inventory["net_daily_consumption"] = df_latest_inventory["daily_demand"] - df_latest_inventory["daily_inflow"]
            
            # Days until stockout = Current Stock / Net Daily Consumption
            df_latest_inventory["days_to_stockout"] = df_latest_inventory.apply(
                lambda row: row["closing_inventory"] / row["net_daily_consumption"] 
                if row["net_daily_consumption"] > 0 else 999,  # 999 = no risk
                axis=1
            )
            
            # Find the minimum days to stockout across all materials
            min_days_to_stockout = df_latest_inventory["days_to_stockout"].min()
            days_to_stockout = json_safe(round(min_days_to_stockout, 0))
        else:
            overstock = 0
            days_to_stockout = 999

        # Forecast Accuracy - Compare daily averages
        forecast_daily_avg = total_forecasted_demand / forecast_days if forecast_days > 0 else 0
        historical_daily_avg = trailing_consumption / historical_days if trailing_consumption > 0 else 0
        
        if historical_daily_avg > 0:
            mape = abs(forecast_daily_avg - historical_daily_avg) / historical_daily_avg * 100
            accuracy = max(0, min(100, 100 - mape))
        else:
            accuracy = 0

        kpis = {
            "totalForecastedRMDemand": format_kpi(total_forecasted_demand, total_forecasted_demand * 0.9),
            "trailing30DConsumption": format_kpi(trailing_consumption, trailing_consumption * 0.95),
            "consumptionForecastAccuracy": format_kpi(round(accuracy, 1), 85.0),
            "projectedOverstock": format_kpi(overstock, overstock + 500),
            "daysToStockout": format_kpi(days_to_stockout, days_to_stockout + 5),
        }
        
        # Cutoff date for UI
        forecast_cutoff = FORECAST_CUTOFF_DATE.strftime('%Y-%m-%d')

        # ===============================
        # TREND DATA - INDUSTRY STANDARD FORMAT
        # Last 30 days historical + Next 7/30 days forecast (Daily level)
        # ===============================
        
        # Get daily forecast data
        if not df_demand.empty:
            daily_forecast_by_date = df_demand.groupby("date")["material_demand_units"].sum().reset_index()
            daily_forecast_by_date.columns = ["date", "forecast"]
        else:
            daily_forecast_by_date = pd.DataFrame(columns=["date", "forecast"])
        
        # Get daily historical actuals (consumed_quantity from inventory)
        # If a product is selected, allocate consumption proportionally based on demand share
        if not df_inventory_historical.empty:
            if product and product != "all" and not df_bom_expanded.empty:
                # Calculate product-specific daily consumption by allocating proportionally
                daily_historical_by_date = pd.DataFrame()
                
                # Get product's demand share for each raw material
                df_bom_product_all = df_bom_expanded[df_bom_expanded["product_id"] == product].copy()
                if not df_bom_product_all.empty:
                    df_bom_product_all["material_demand_units"] = (
                        df_bom_product_all["product_units"] * df_bom_product_all["consumption_per_unit"]
                    )
                    product_demand_by_rm = df_bom_product_all.groupby("raw_material")["material_demand_units"].sum()
                    
                    # Get total demand by raw material (all products) for allocation
                    total_demand_by_rm_all = df_bom_expanded.copy()
                    total_demand_by_rm_all["material_demand_units"] = (
                        total_demand_by_rm_all["product_units"] * total_demand_by_rm_all["consumption_per_unit"]
                    )
                    total_demand_by_rm_all = total_demand_by_rm_all.groupby("raw_material")["material_demand_units"].sum()
                    
                    # Allocate consumption by date and raw material
                    daily_allocated = []
                    for date in df_inventory_historical["date"].unique():
                        date_data = df_inventory_historical[df_inventory_historical["date"] == date]
                        allocated_consumption = 0
                        
                        for _, row in date_data.iterrows():
                            raw_mat = row["raw_material"]
                            total_consumption = row["consumed_quantity"]
                            product_demand = product_demand_by_rm.get(raw_mat, 0)
                            total_demand = total_demand_by_rm_all.get(raw_mat, 0)
                            
                            if total_demand > 0:
                                allocation_factor = product_demand / total_demand
                                allocated_consumption += total_consumption * allocation_factor
                        
                        daily_allocated.append({
                            "date": date,
                            "actual": allocated_consumption
                        })
                    
                    daily_historical_by_date = pd.DataFrame(daily_allocated)
                else:
                    daily_historical_by_date = pd.DataFrame(columns=["date", "actual"])
            else:
                # No product filter - use total consumption
                daily_historical_by_date = df_inventory_historical.groupby("date")["consumed_quantity"].sum().reset_index()
                daily_historical_by_date.columns = ["date", "actual"]
        else:
            daily_historical_by_date = pd.DataFrame(columns=["date", "actual"])
        
        # Build combined trend data
        trend_rows = []
        
        # Part 1: Historical actuals (no forecast)
        for _, row in daily_historical_by_date.iterrows():
            trend_rows.append({
                "date": row["date"],
                "actual": row["actual"],
                "forecast": None,
                "period": "historical"
            })
        
        # Part 2: Future forecast (no actual)
        for _, row in daily_forecast_by_date.iterrows():
            trend_rows.append({
                "date": row["date"],
                "actual": None,
                "forecast": row["forecast"],
                "period": "forecast"
            })
        
        combined_data = pd.DataFrame(trend_rows)
        
        # Aggregate trend data based on aggregation setting
        trend_data = []
        if not combined_data.empty:
            if aggregation == "weekly":
                combined_data["bucket"] = pd.to_datetime(combined_data["date"]).dt.to_period("W").dt.start_time
                trend_agg = combined_data.groupby("bucket").agg({
                    "forecast": lambda x: x.dropna().sum() if x.dropna().any() else None,
                    "actual": lambda x: x.dropna().sum() if x.dropna().any() else None,
                    "period": "first"
                }).reset_index()
            elif aggregation == "monthly":
                combined_data["bucket"] = pd.to_datetime(combined_data["date"]).dt.to_period("M").dt.start_time
                trend_agg = combined_data.groupby("bucket").agg({
                    "forecast": lambda x: x.dropna().sum() if x.dropna().any() else None,
                    "actual": lambda x: x.dropna().sum() if x.dropna().any() else None,
                    "period": "first"
                }).reset_index()
            else:
                # Daily - no aggregation
                trend_agg = combined_data.copy()
                trend_agg["bucket"] = trend_agg["date"]
            
            for _, row in trend_agg.iterrows():
                # Format date properly - convert to string if it's a datetime
                bucket_date = row["bucket"]
                if hasattr(bucket_date, 'strftime'):
                    date_str = bucket_date.strftime("%Y-%m-%d")
                elif isinstance(bucket_date, str):
                    date_str = bucket_date
                else:
                    date_str = str(bucket_date)
                
                trend_data.append({
                    "date": date_str,
                    "forecast": json_safe(row["forecast"]) if pd.notna(row.get("forecast")) else None,
                    "actual": json_safe(row["actual"]) if pd.notna(row.get("actual")) else None,
                    "period": row.get("period", "historical")
                })
        
        df_inventory_trend = df_inventory_historical

        # ===============================
        # FORECAST COMPARISON - INDUSTRY STANDARD
        # Historical actuals (weekly) + Future forecast with confidence bands
        # ===============================
        forecast_comparison_data = []
        confidence_pct = 0.15
        
        # Build weekly data from daily historical and forecast
        weekly_dict = {}  # Use dict to merge by week
        
        # Part 1: Historical actuals (weekly aggregation)
        if not df_inventory_historical.empty:
            df_hist_weekly = df_inventory_historical.copy()
            df_hist_weekly["week"] = df_hist_weekly["date"].dt.to_period("W").dt.start_time
            hist_weekly_agg = df_hist_weekly.groupby("week")["consumed_quantity"].sum().reset_index()
            
            for _, row in hist_weekly_agg.iterrows():
                week_key = row["week"]
                if week_key not in weekly_dict:
                    weekly_dict[week_key] = {"week": week_key, "actual": 0, "forecast": 0}
                weekly_dict[week_key]["actual"] += row["consumed_quantity"]
        
        # Part 2: Future forecast (weekly aggregation)
        if not df_demand.empty:
            df_fcst_weekly = df_demand.copy()
            df_fcst_weekly["week"] = df_fcst_weekly["date"].dt.to_period("W").dt.start_time
            fcst_weekly_agg = df_fcst_weekly.groupby("week")["material_demand_units"].sum().reset_index()
            
            for _, row in fcst_weekly_agg.iterrows():
                week_key = row["week"]
                if week_key not in weekly_dict:
                    weekly_dict[week_key] = {"week": week_key, "actual": 0, "forecast": 0}
                weekly_dict[week_key]["forecast"] += row["material_demand_units"]
        
        # Convert to sorted list and format
        cutoff_week = FORECAST_CUTOFF_DATE.to_period("W").start_time
        
        for week_key in sorted(weekly_dict.keys()):
            data = weekly_dict[week_key]
            week_str = week_key.strftime("%b %d") if hasattr(week_key, "strftime") else str(week_key)
            
            actual_val = data["actual"] if data["actual"] > 0 else None
            forecast_val = data["forecast"] if data["forecast"] > 0 else None
            
            # Determine period based on whether it's before or after cutoff
            if week_key < cutoff_week:
                period = "historical"
            elif week_key > cutoff_week:
                period = "forecast"
            else:
                period = "transition"  # Cutoff week has both
            
            # Calculate confidence bands only for forecast values
            if forecast_val and forecast_val > 0:
                conf_low = forecast_val * (1 - confidence_pct)
                conf_high = forecast_val * (1 + confidence_pct)
            else:
                conf_low = None
                conf_high = None
            
            forecast_comparison_data.append({
                "date": week_str,
                "actual": json_safe(actual_val) if actual_val else None,
                "forecast": json_safe(forecast_val) if forecast_val else None,
                "confidenceLow": json_safe(conf_low) if conf_low else None,
                "confidenceHigh": json_safe(conf_high) if conf_high else None,
                "period": period
            })

        # ===============================
        # DEMAND FLOW FUNNEL
        # ===============================
        sku_units = json_safe(safe_sum(df_forecast, "forecast_units"))
        
        if not df_forecast.empty and not df_sku_master.empty:
            forecasted_skus = df_forecast["sku_id"].unique()
            products_from_skus = df_sku_master[
                df_sku_master["sku_id"].isin(forecasted_skus)
            ]["product_id"].unique()
            product_count = len(products_from_skus)
        else:
            products_from_skus = []
            product_count = 0
        
        df_bom_expanded = load_csv("product_bom_expanded.csv")
        if not df_bom_expanded.empty and len(products_from_skus) > 0:
            df_bom_filtered = df_bom_expanded[
                df_bom_expanded["product_id"].isin(products_from_skus)
            ]
            product_units_df = df_bom_filtered.drop_duplicates(subset=["product_id", "date"])
            product_forecast_units = json_safe(product_units_df["product_units"].sum() if "product_units" in product_units_df.columns else 0)
        else:
            product_forecast_units = sku_units
        
        raw_material_demand_units = json_safe(total_forecasted_demand)

        funnel = {
            "steps": {
                "skuForecast": {"label": "SKU Forecast", "value": sku_units, "unit": "Units"},
                "productMix": {"label": "Product Mix", "value": product_count, "unit": "Products"},
                "productForecast": {"label": "Product Forecast", "value": product_forecast_units, "unit": "Units"},
                "rawMaterialDemand": {
                    "label": "Material Demand",
                    "value": raw_material_demand_units,
                    "unit": "Units",
                },
            }
        }

        # ===============================
        # CONSUMPTION VARIANCE HEATMAP
        # Shows forecasted consumption vs 30-day historical average
        # Forecast period: From Dec 31, 2025 onwards
        # Historical average: Last 30 days (Dec 1-30, 2025)
        # ===============================
        heatmap_data = []
        
        if not df_inventory_historical.empty and not df_demand.empty:
            # Calculate 30-day historical average for each raw material (Dec 1-30, 2025)
            historical_30d = df_inventory_historical[
                (df_inventory_historical["date"] >= FORECAST_CUTOFF_DATE - timedelta(days=29)) &
                (df_inventory_historical["date"] <= FORECAST_CUTOFF_DATE)
            ]
            avg_by_rm = historical_30d.groupby("raw_material")["consumed_quantity"].mean()
            
            # Get forecasted consumption from Dec 31, 2025 onwards
            forecast_start_date = FORECAST_CUTOFF_DATE + timedelta(days=1)
            df_forecast_period = df_demand[df_demand["date"] >= forecast_start_date].copy()
            
            if not df_forecast_period.empty:
                # Get forecasted consumption by date and raw material
                forecast_by_date_rm = df_forecast_period.groupby(["date", "raw_material"])["material_demand_units"].sum().reset_index()
                
                # Limit to forecast period dates (Dec 31, 2025 onwards) - show next 7 or 30 days based on filter
                forecast_dates = sorted(forecast_by_date_rm["date"].unique())
                if forecast_days == 7:
                    forecast_dates = forecast_dates[:7]
                else:
                    forecast_dates = forecast_dates[:30]
                forecast_by_date_rm = forecast_by_date_rm[forecast_by_date_rm["date"].isin(forecast_dates)]
                
                # Limit to top 6 raw materials by volume (based on historical average)
                top_materials = avg_by_rm.nlargest(6).index.tolist()
                forecast_by_date_rm = forecast_by_date_rm[forecast_by_date_rm["raw_material"].isin(top_materials)]
                
                for _, row in forecast_by_date_rm.iterrows():
                    date_val = row["date"]
                    rm = row["raw_material"]
                    forecasted = row["material_demand_units"]
                    
                    historical_avg = avg_by_rm.get(rm, 0)
                    
                    if historical_avg > 0:
                        variance_pct = ((forecasted - historical_avg) / historical_avg) * 100
                    else:
                        variance_pct = 0
                    
                    # Format date nicely
                    date_str = date_val.strftime("%b %d") if hasattr(date_val, "strftime") else str(date_val)[:10]
                    
                    heatmap_data.append({
                        "date": date_str,
                        "rawMaterial": str(rm),
                        "variancePct": json_safe(round(variance_pct, 2)),
                        "forecast": json_safe(round(forecasted, 0)),  # Forecasted consumption
                        "average": json_safe(round(historical_avg, 0))  # 30-day historical average
                    })

        # ===============================
        # RAW MATERIAL RISK TABLE
        # ===============================
        risk_table_data = []
        
        if not df_inventory_historical.empty and not df_demand.empty:
            df_inv_latest = (
                df_inventory_historical
                .sort_values("date")
                .groupby("raw_material", as_index=False)
                .tail(1)
            )
            
            # Get consumption by raw material - allocate if product filter is selected
            if product and product != "all" and not df_bom_expanded.empty:
                # Calculate product-specific consumption allocation
                df_bom_product_all = df_bom_expanded[df_bom_expanded["product_id"] == product].copy()
                if not df_bom_product_all.empty:
                    df_bom_product_all["material_demand_units"] = (
                        df_bom_product_all["product_units"] * df_bom_product_all["consumption_per_unit"]
                    )
                    product_demand_by_rm = df_bom_product_all.groupby("raw_material")["material_demand_units"].sum()
                    
                    total_demand_by_rm_all = df_bom_expanded.copy()
                    total_demand_by_rm_all["material_demand_units"] = (
                        total_demand_by_rm_all["product_units"] * total_demand_by_rm_all["consumption_per_unit"]
                    )
                    total_demand_by_rm_all = total_demand_by_rm_all.groupby("raw_material")["material_demand_units"].sum()
                    
                    # Allocate consumption proportionally
                    consumption_by_rm = {}
                    total_consumption_by_rm = df_inventory_historical.groupby("raw_material")["consumed_quantity"].sum()
                    for rm in total_consumption_by_rm.index:
                        total_consumption = total_consumption_by_rm[rm]
                        product_demand = product_demand_by_rm.get(rm, 0)
                        total_demand = total_demand_by_rm_all.get(rm, 0)
                        if total_demand > 0:
                            consumption_by_rm[rm] = total_consumption * (product_demand / total_demand)
                        else:
                            consumption_by_rm[rm] = 0
                    consumption_by_rm = pd.Series(consumption_by_rm)
                else:
                    consumption_by_rm = pd.Series()
            else:
                consumption_by_rm = df_inventory_historical.groupby("raw_material")["consumed_quantity"].sum()
            
            forecast_by_rm = df_demand.groupby("raw_material")["material_demand_units"].sum()
            
            # Get expected inflow for stockout date calculation
            if not df_inventory_full.empty and "inflow_quantity" in df_inventory_full.columns:
                avg_daily_inflow_by_rm = df_inventory_full.groupby("raw_material")["inflow_quantity"].mean()
            else:
                avg_daily_inflow_by_rm = pd.Series()
            
            for idx, row in df_inv_latest.iterrows():
                rm = row["raw_material"]
                closing_inv = row.get("closing_inventory", 0)
                safety_stock = row.get("safety_stock", 0)
                
                forecast_demand = forecast_by_rm.get(rm, 0)
                actual_consumption = consumption_by_rm.get(rm, 0) if isinstance(consumption_by_rm, pd.Series) else consumption_by_rm.get(rm, 0)
                
                # Allocate inventory values if product filter is selected
                allocation_factor = 1.0  # Default: no allocation
                if product and product != "all" and not df_bom_expanded.empty:
                    df_bom_product_all = df_bom_expanded[df_bom_expanded["product_id"] == product].copy()
                    if not df_bom_product_all.empty:
                        df_bom_product_all["material_demand_units"] = (
                            df_bom_product_all["product_units"] * df_bom_product_all["consumption_per_unit"]
                        )
                        product_demand_by_rm = df_bom_product_all.groupby("raw_material")["material_demand_units"].sum()
                        
                        total_demand_by_rm_all = df_bom_expanded.copy()
                        total_demand_by_rm_all["material_demand_units"] = (
                            total_demand_by_rm_all["product_units"] * total_demand_by_rm_all["consumption_per_unit"]
                        )
                        total_demand_by_rm_all = total_demand_by_rm_all.groupby("raw_material")["material_demand_units"].sum()
                        
                        product_demand = product_demand_by_rm.get(rm, 0)
                        total_demand = total_demand_by_rm_all.get(rm, 0)
                        if total_demand > 0:
                            allocation_factor = product_demand / total_demand
                            closing_inv = closing_inv * allocation_factor
                            safety_stock = safety_stock * allocation_factor
                
                # Calculate daily consumption rate for stockout date
                daily_consumption = actual_consumption / historical_days if historical_days > 0 else 0
                # Allocate daily inflow proportionally if product filter is selected
                daily_inflow_total = avg_daily_inflow_by_rm.get(rm, 0) if isinstance(avg_daily_inflow_by_rm, pd.Series) else avg_daily_inflow_by_rm.get(rm, 0)
                daily_inflow = daily_inflow_total * allocation_factor  # Allocate inflow proportionally
                net_daily_consumption = daily_consumption - daily_inflow
                
                # Calculate stockout risk date
                if net_daily_consumption > 0 and closing_inv > 0:
                    days_until_stockout = closing_inv / net_daily_consumption
                    # Only show date if stockout is within reasonable timeframe (within 2 years)
                    if days_until_stockout < 730:
                        stockout_risk_date = (FORECAST_CUTOFF_DATE + pd.Timedelta(days=int(days_until_stockout))).strftime("%Y-%m-%d")
                    else:
                        stockout_risk_date = None  # Too far in future to be meaningful
                else:
                    stockout_risk_date = None  # No risk (inflow >= consumption or no inventory)
                
                # Risk status determination
                if closing_inv < 0 or closing_inv < safety_stock * 0.5:
                    risk_status = "Stockout"
                elif closing_inv > safety_stock * 2:
                    risk_status = "Overstock"
                else:
                    risk_status = "Balanced"
                
                risk_table_data.append({
                    "id": str(rm),
                    "rawMaterial": str(rm),
                    "forecastDemand": json_safe(round(forecast_demand, 2)),
                    "actualConsumption": json_safe(round(actual_consumption, 2)),
                    "closingInventory": json_safe(round(closing_inv, 2)),
                    "safetyStock": json_safe(round(safety_stock, 2)),
                    "riskStatus": risk_status,
                    "stockoutRiskDate": stockout_risk_date
                })

        return jsonify({
            "kpis": kpis,
            "rawMaterialDemandTrend": trend_data,
            "rawMaterialRiskTable": risk_table_data,
            "demandFlowFunnel": funnel,
            "forecastComparison": forecast_comparison_data,
            "consumptionErrorHeatmap": heatmap_data,
            "forecastCutoffDate": forecast_cutoff,  # Cutoff date for UI visualization
            "forecastHorizon": forecast_horizon,
            "historicalDays": historical_days  # Number of historical days shown
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# =========================================================
# ENDPOINT 2: SALES DASHBOARD (Updated for daily format)
# =========================================================
@app.route('/api/sales/dashboard', methods=['GET'])
def sales_dashboard():
    try:
        date_range = request.args.get("dateRange", "next-30")
        channel = request.args.get("channel")
        store = request.args.get("store")
        sku_filter = request.args.get("sku")
        category = request.args.get("category")
        product = request.args.get("product")  # NEW: Product filter
        rolling_window = request.args.get("rollingWindow", "7")  # 7 or 30
        
        
        # Determine forecast horizon from new filter format
        forecast_days = get_forecast_horizon_days(date_range)
        forecast_horizon = f"{forecast_days}day"
        
        df_forecast = load_csv("sku_daily_forecast.csv")
        df_sales = load_csv("sku_daily_sales.csv")
        df_sku_master = load_csv("sku_master.csv")
        
        # Parse dates
        if not df_forecast.empty:
            df_forecast['date'] = pd.to_datetime(df_forecast['date'], errors='coerce')
        if not df_sales.empty:
            df_sales['date'] = pd.to_datetime(df_sales['date'], errors='coerce')
        
        # Filter forecast by horizon (7day or 30day)
        if not df_forecast.empty and "forecast_horizon" in df_forecast.columns:
            df_forecast = df_forecast[df_forecast["forecast_horizon"] == forecast_horizon]
        
        # Get last N days of historical sales (based on filter)
        historical_days = forecast_days  # Match historical period to forecast period
        historical_start = FORECAST_CUTOFF_DATE - timedelta(days=historical_days - 1)
        df_sales_historical = df_sales[
            (df_sales["date"] >= historical_start) & 
            (df_sales["date"] <= FORECAST_CUTOFF_DATE)
        ].copy() if not df_sales.empty else pd.DataFrame()
        
        # Apply product filter FIRST - filter by SKUs belonging to this product
        if product and product != "all" and not df_sku_master.empty:
            valid_skus = df_sku_master[df_sku_master["product_id"] == product]["sku_id"].unique()
            df_forecast = df_forecast[df_forecast["sku_id"].isin(valid_skus)]
            df_sales_historical = df_sales_historical[df_sales_historical["sku_id"].isin(valid_skus)] if not df_sales_historical.empty else df_sales_historical
        
        # Apply channel weight
        channel_weight = 1.0
        if channel and channel != "all" and not df_sales_historical.empty:
            total_all = df_sales_historical["actual_sales_units"].sum()
            channel_sales = df_sales_historical[df_sales_historical["sales_channel"] == channel]["actual_sales_units"].sum()
            if total_all > 0:
                channel_weight = channel_sales / total_all
            df_sales_historical = df_sales_historical[df_sales_historical["sales_channel"] == channel]
        
        # Apply store filter
        if store and store != "all":
            if not df_forecast.empty and "store_id" in df_forecast.columns:
                df_forecast = df_forecast[df_forecast["store_id"] == store]
            df_sales_historical = df_sales_historical[df_sales_historical["store_id"] == store] if not df_sales_historical.empty else df_sales_historical
        
        # Apply SKU filter
        if sku_filter and sku_filter != "all":
            df_forecast = df_forecast[df_forecast["sku_id"] == sku_filter]
            df_sales_historical = df_sales_historical[df_sales_historical["sku_id"] == sku_filter] if not df_sales_historical.empty else df_sales_historical
        
        # Apply category filter
        if category and category != "all" and not df_sku_master.empty:
            valid_skus = df_sku_master[df_sku_master["category"] == category]["sku_id"].unique()
            df_forecast = df_forecast[df_forecast["sku_id"].isin(valid_skus)]
            df_sales_historical = df_sales_historical[df_sales_historical["sku_id"].isin(valid_skus)] if not df_sales_historical.empty else df_sales_historical
        
        # Apply channel weight to forecast
        if channel_weight < 1.0 and not df_forecast.empty:
            df_forecast = df_forecast.copy()
            df_forecast["forecast_units"] = (df_forecast["forecast_units"] * channel_weight).round().astype(int)

        # ===============================
        # KPIs - Using historical data for accuracy calculation
        # ===============================
        total_forecast_units = safe_sum(df_forecast, 'forecast_units')
        total_historical_units = safe_sum(df_sales_historical, 'actual_sales_units')
        volatility = df_forecast['forecast_units'].std() if 'forecast_units' in df_forecast.columns and len(df_forecast) > 0 else 0
        
        # Calculate average daily rates for comparison
        forecast_daily_avg = total_forecast_units / forecast_days if forecast_days > 0 else 0
        # Use historical_days (which matches forecast_days) instead of hardcoded 30
        historical_daily_avg = total_historical_units / historical_days if historical_days > 0 and not df_sales_historical.empty else 0
        
        # Calculate accuracy based on avg daily comparison
        if historical_daily_avg > 0:
            mape = abs(forecast_daily_avg - historical_daily_avg) / historical_daily_avg * 100
            accuracy = max(0, min(100, 100 - mape))
        else:
            accuracy = 0
        
        # Calculate bias
        if historical_daily_avg > 0:
            bias = ((forecast_daily_avg - historical_daily_avg) / historical_daily_avg) * 100
        else:
            bias = 0

        kpis = {
            "skuForecastAccuracy": format_kpi(round(accuracy, 1), 85.0),
            "totalForecastedUnits": format_kpi(total_forecast_units, total_forecast_units * 0.95),
            "forecastBias": format_kpi(round(bias, 1), 2.0),
            "demandVolatilityIndex": format_kpi(round(volatility, 1), volatility * 1.1 if volatility else 0),
            "highRiskSKUsCount": format_kpi(0, 0)  # Will be updated below
        }

        # ===============================
        # SKU Sales Trend - INDUSTRY STANDARD FORMAT
        # Last 30 days historical actuals + Next 7/30 days forecast
        # ===============================
        sales_trend = []
        forecast_cutoff = FORECAST_CUTOFF_DATE.strftime('%Y-%m-%d')
        
        if not df_sales_historical.empty or not df_forecast.empty:
            # Get list of channels from historical data
            channels = df_sales_historical['sales_channel'].unique().tolist() if not df_sales_historical.empty else []
            
            # --- PART 1: Historical Actuals (last 30 days) ---
            if not df_sales_historical.empty:
                # Create date range for historical period (ensure all dates are included)
                historical_start = FORECAST_CUTOFF_DATE - timedelta(days=historical_days - 1)
                date_range = pd.date_range(start=historical_start, end=FORECAST_CUTOFF_DATE, freq='D')
                
                # Ensure dates in historical data are datetime
                df_sales_historical['date'] = pd.to_datetime(df_sales_historical['date'])
                
                # Group historical data by date and channel
                historical_by_date_channel = df_sales_historical.groupby(['date', 'sales_channel'])['actual_sales_units'].sum().reset_index()
                
                # Create a complete date-channel matrix to ensure all dates have entries (even if 0)
                for date in date_range:
                    date_str = date.strftime('%Y-%m-%d')
                    for ch in channels:
                        # Find matching row for this date and channel (normalize dates for comparison)
                        date_normalized = pd.Timestamp(date).normalize()
                        matching = historical_by_date_channel[
                            (pd.to_datetime(historical_by_date_channel['date']).dt.normalize() == date_normalized) & 
                            (historical_by_date_channel['sales_channel'] == ch)
                        ]
                        
                        if not matching.empty:
                            actual_value = int(matching.iloc[0]['actual_sales_units'])
                        else:
                            actual_value = 0  # No sales on this date for this channel
                        
                        sales_trend.append({
                            "date": json_safe(date_str),
                            "channel": ch,
                            "actual": json_safe(actual_value),
                            "forecast": None,  # No forecast for historical period
                            "period": "historical"
                        })
            
            # --- PART 2: Future Forecast (next 7/30 days) ---
            if not df_forecast.empty and channels:
                # Get channel proportions from historical data (overall and daily)
                channel_totals = df_sales_historical.groupby('sales_channel')['actual_sales_units'].sum() if not df_sales_historical.empty else pd.Series()
                total_sales = channel_totals.sum() if len(channel_totals) > 0 else 1
                channel_proportions = (channel_totals / total_sales).to_dict() if total_sales > 0 else {}
                
                # Calculate daily channel proportions from historical data (to preserve daily variation patterns)
                df_sales_historical['date'] = pd.to_datetime(df_sales_historical['date'])
                daily_channel_sales = df_sales_historical.groupby(['date', 'sales_channel'])['actual_sales_units'].sum().reset_index()
                daily_totals = df_sales_historical.groupby('date')['actual_sales_units'].sum()
                
                # Create daily channel proportion lookup
                daily_channel_props = {}
                for _, row in daily_channel_sales.iterrows():
                    date_key = row['date'].strftime('%Y-%m-%d')
                    ch = row['sales_channel']
                    daily_total = daily_totals.get(row['date'], 1)
                    if date_key not in daily_channel_props:
                        daily_channel_props[date_key] = {}
                    daily_channel_props[date_key][ch] = row['actual_sales_units'] / daily_total if daily_total > 0 else channel_proportions.get(ch, 1.0 / len(channels))
                
                # Daily forecast totals (preserve daily variation)
                daily_forecast = df_forecast.groupby('date')['forecast_units'].sum().reset_index()
                daily_forecast.columns = ['date', 'forecast']
                daily_forecast = daily_forecast.sort_values('date')
                daily_forecast['date'] = pd.to_datetime(daily_forecast['date'])
                
                # Get day of week pattern from historical data (to match weekly patterns)
                df_sales_historical['day_of_week'] = pd.to_datetime(df_sales_historical['date']).dt.dayofweek
                weekly_channel_patterns = {}
                for ch in channels:
                    ch_data = df_sales_historical[df_sales_historical['sales_channel'] == ch]
                    if not ch_data.empty:
                        weekly_channel_patterns[ch] = ch_data.groupby('day_of_week')['actual_sales_units'].mean().to_dict()
                
                for _, row in daily_forecast.iterrows():
                    forecast_date = row['date']
                    forecast_date_str = forecast_date.strftime('%Y-%m-%d')
                    total_forecast = row['forecast']
                    day_of_week = forecast_date.dayofweek
                    
                    # Try to use daily proportions from similar historical days, fallback to overall proportions
                    # Look for historical dates with same day of week (to preserve weekly patterns)
                    similar_dates = df_sales_historical[df_sales_historical['day_of_week'] == day_of_week]
                    
                    if not similar_dates.empty:
                        # Use average proportions for this day of week
                        similar_daily_totals = similar_dates.groupby('date')['actual_sales_units'].sum()
                        similar_channel_sales = similar_dates.groupby(['date', 'sales_channel'])['actual_sales_units'].sum().reset_index()
                        
                        day_of_week_props = {}
                        for ch in channels:
                            ch_sales = similar_channel_sales[similar_channel_sales['sales_channel'] == ch]['actual_sales_units']
                            if not ch_sales.empty:
                                avg_ch_sales = ch_sales.mean()
                                avg_total = similar_daily_totals.mean()
                                day_of_week_props[ch] = avg_ch_sales / avg_total if avg_total > 0 else channel_proportions.get(ch, 1.0 / len(channels))
                            else:
                                day_of_week_props[ch] = channel_proportions.get(ch, 1.0 / len(channels))
                    else:
                        # Fallback to overall proportions
                        day_of_week_props = channel_proportions.copy()
                        if not day_of_week_props:
                            day_of_week_props = {ch: 1.0 / len(channels) for ch in channels}
                    
                    for ch in channels:
                        # Allocate forecast to channels based on day-of-week patterns (preserves variation)
                        ch_proportion = day_of_week_props.get(ch, channel_proportions.get(ch, 1.0 / len(channels)))
                        ch_forecast = int(total_forecast * ch_proportion)
                        
                        sales_trend.append({
                            "date": json_safe(forecast_date_str),
                            "channel": ch,
                            "actual": None,  # No actual for future dates
                            "forecast": json_safe(ch_forecast),
                            "period": "forecast"
                        })

        # ===============================
        # SKU Performance Table
        # ===============================
        sku_performance = []
        if not df_forecast.empty and not df_sales_historical.empty:
            # Get number of forecast days
            forecast_days = df_forecast['date'].nunique()
            
            # Calculate metrics per SKU from forecast
            sku_forecast_agg = df_forecast.groupby('sku_id').agg({
                'forecast_units': ['sum', 'std', 'mean']
            }).reset_index()
            sku_forecast_agg.columns = ['sku_id', 'total_forecast', 'volatility', 'avg_forecast_daily']
            
            # Calculate actual metrics from historical sales
            sku_actual_agg = df_sales_historical.groupby('sku_id').agg({
                'actual_sales_units': ['sum', 'mean', 'std']
            }).reset_index()
            sku_actual_agg.columns = ['sku_id', 'total_actual', 'avg_daily', 'actual_volatility']
            
            # Merge
            sku_metrics = pd.merge(sku_forecast_agg, sku_actual_agg, on='sku_id', how='outer').fillna(0)
            
            # Add category from master
            if not df_sku_master.empty and 'category' in df_sku_master.columns:
                sku_metrics = pd.merge(sku_metrics, df_sku_master[['sku_id', 'category']].drop_duplicates(), 
                                       on='sku_id', how='left')
            else:
                sku_metrics['category'] = 'Unknown'
            
            # Calculate accuracy: Compare forecast avg daily with historical avg daily
            # This gives a realistic accuracy measure
            sku_metrics['accuracy'] = sku_metrics.apply(
                lambda row: max(0, 100 - abs(row['avg_forecast_daily'] - row['avg_daily']) / row['avg_daily'] * 100) 
                if row['avg_daily'] > 0 else 0, axis=1
            )
            
            # Cap accuracy at 100
            sku_metrics['accuracy'] = sku_metrics['accuracy'].clip(upper=100)
            
            # Determine risk using RELATIVE thresholds (bottom performers)
            # This ensures actionable insights even when overall accuracy is high
            accuracy_mean = sku_metrics['accuracy'].mean()
            accuracy_std = sku_metrics['accuracy'].std() if len(sku_metrics) > 1 else 1
            volatility_mean = sku_metrics['volatility'].mean()
            
            # Dynamic thresholds based on distribution
            high_risk_threshold = accuracy_mean - accuracy_std  # Bottom ~16%
            med_risk_threshold = accuracy_mean - (accuracy_std * 0.3)  # Bottom ~35%
            
            def calc_risk(row):
                # High risk: bottom performers OR very high volatility
                if row['accuracy'] < high_risk_threshold:
                    return 'High'
                elif row['volatility'] > volatility_mean * 1.5 and volatility_mean > 0:
                    return 'High'  # High volatility relative to peers
                elif row['accuracy'] < med_risk_threshold:
                    return 'Medium'
                else:
                    return 'Low'
            
            sku_metrics['risk'] = sku_metrics.apply(calc_risk, axis=1)
            
            sku_performance = [
                {
                    "id": idx + 1,
                    "sku": str(row['sku_id']),
                    "name": str(row['sku_id']),  # Use SKU as name for now
                    "category": str(row.get('category', 'Unknown')),
                    "avgDailySales": json_safe(round(row['avg_daily'], 1)),
                    "accuracy": json_safe(round(row['accuracy'], 1)),
                    "demandVolatility": json_safe(round(row['volatility'], 1) if pd.notna(row['volatility']) else 0),
                    "riskFlag": str(row['risk']).lower()  # lowercase for frontend
                }
                for idx, (_, row) in enumerate(sku_metrics.iterrows())
            ]
            
            # Update high risk count in KPIs
            high_risk_count = len(sku_metrics[sku_metrics['risk'] == 'High'])
            kpis["highRiskSKUsCount"] = format_kpi(high_risk_count, high_risk_count)

        # ===============================
        # SKU Contribution Heatmap (SKU x Date)
        # Business insight: Show top 10 SKUs with highest variance in contribution
        # ===============================
        heatmap = []
        if not df_forecast.empty and {'sku_id', 'date', 'forecast_units'}.issubset(df_forecast.columns):
            # Group by SKU and date
            sku_date_grp = df_forecast.groupby(['sku_id', 'date'])['forecast_units'].sum().reset_index()
            
            # Calculate total per date for contribution %
            date_totals = sku_date_grp.groupby('date')['forecast_units'].sum().reset_index()
            date_totals.columns = ['date', 'date_total']
            
            sku_date_grp = pd.merge(sku_date_grp, date_totals, on='date')
            sku_date_grp['contribution_pct'] = (sku_date_grp['forecast_units'] / sku_date_grp['date_total'] * 100).round(2)
            
            # Select top 10 SKUs by total forecast volume (most impactful)
            top_skus = df_forecast.groupby('sku_id')['forecast_units'].sum().nlargest(10).index.tolist()
            
            # Limit to 10 dates for readability (most recent forecast dates)
            recent_dates = sorted(sku_date_grp['date'].unique())[-10:]
            
            # Filter data
            sku_date_filtered = sku_date_grp[
                (sku_date_grp['sku_id'].isin(top_skus)) & 
                (sku_date_grp['date'].isin(recent_dates))
            ]
            
            heatmap = [
                {
                    "sku": str(row['sku_id']),
                    "date": json_safe(row['date']),
                    "contributionPct": json_safe(row['contribution_pct']),
                    "forecastUnits": json_safe(row['forecast_units'])
                }
                for _, row in sku_date_filtered.iterrows()
            ]

        # ===============================
        # Top Demand Drivers (Top 10 SKUs)
        # ===============================
        top_demand_drivers = []
        if not df_forecast.empty:
            sku_totals = df_forecast.groupby('sku_id')['forecast_units'].sum().reset_index()
            total_demand = sku_totals['forecast_units'].sum()
            sku_totals['contribution_pct'] = (sku_totals['forecast_units'] / total_demand * 100).round(2) if total_demand > 0 else 0
            sku_totals = sku_totals.nlargest(10, 'forecast_units')
            
            top_demand_drivers = [
                {
                    "sku": str(row['sku_id']),
                    "name": str(row['sku_id']),  # Use SKU as name
                    "forecastUnits": json_safe(int(row['forecast_units'])),
                    "contributionPct": json_safe(row['contribution_pct']),
                    "trendDirection": "up" if row['contribution_pct'] > 3 else ("down" if row['contribution_pct'] < 2 else "flat")
                }
                for _, row in sku_totals.iterrows()
            ]

        # ===============================
        # High Risk SKUs (Items requiring attention)
        # ===============================
        high_risk_skus = []
        if sku_performance:
            risk_items = [item for item in sku_performance if item['riskFlag'] == 'high']
            high_risk_skus = [
                {
                    "id": idx + 1,
                    "sku": item['sku'],
                    "name": item['name'],
                    "category": item['category'],
                    "severity": "high" if item['accuracy'] < 70 else "medium",
                    "issue": "Low Accuracy" if item['accuracy'] < 80 else "High Volatility",
                    "recommendation": "Review forecast",
                    "daysUntilStockout": max(3, int(30 * (100 - item['accuracy']) / 100)) if item['accuracy'] < 90 else None
                }
                for idx, item in enumerate(risk_items)
            ][:10]  # Limit to top 10

        # ===============================
        # Rolling Error (for trend analysis)
        # Calculate rolling MAPE with specified window (7 or 30 days)
        # MAPE = mean(|actual - forecast| / actual) * 100
        # Only show forecast period data (Dec 31, 2025 onwards)
        # Rolling window controls both: historical average calculation AND number of forecast days shown
        # ===============================
        rolling_error = []
        if not df_forecast.empty and not df_sales_historical.empty:
            window_days = int(rolling_window)
            forecast_start_date = FORECAST_CUTOFF_DATE + timedelta(days=1)  # Dec 31, 2025
            forecast_end_date = forecast_start_date + timedelta(days=window_days - 1)  # Limit to window_days
            
            # Get daily aggregated data
            df_historical_daily = df_sales_historical.groupby('date')['actual_sales_units'].sum().reset_index()
            df_historical_daily = df_historical_daily.sort_values('date').reset_index(drop=True)
            df_forecast_daily = df_forecast.groupby('date')['forecast_units'].sum().reset_index()
            df_forecast_daily = df_forecast_daily.sort_values('date').reset_index(drop=True)
            
            # Filter forecast data to only include dates from Dec 31, 2025 onwards, limited to window_days
            df_forecast_daily_filtered = df_forecast_daily[
                (df_forecast_daily['date'] >= forecast_start_date) & 
                (df_forecast_daily['date'] <= forecast_end_date)
            ].copy()
            
            # Calculate rolling average from historical data (last N days before cutoff)
            if len(df_historical_daily) >= window_days:
                historical_rolling_avg = df_historical_daily.tail(window_days)['actual_sales_units'].mean()
            else:
                historical_rolling_avg = df_historical_daily['actual_sales_units'].mean() if len(df_historical_daily) > 0 else 0
            
            # Calculate error for forecast period only (Dec 31, 2025 onwards, limited to window_days)
            for _, row in df_forecast_daily_filtered.iterrows():
                forecast_val = row['forecast_units']
                if historical_rolling_avg > 0:
                    error_pct = abs(forecast_val - historical_rolling_avg) / historical_rolling_avg * 100
                    # Cap at reasonable maximum (1000% to prevent extreme outliers)
                    error_pct = min(error_pct, 1000)
                else:
                    error_pct = 0
                rolling_error.append({
                    "date": json_safe(row['date']),
                    "mape": json_safe(round(error_pct, 2))
                })

        # ===============================
        # Forecast Deviation Histogram
        # ===============================
        deviation_histogram = []
        if not df_forecast.empty and not df_sales_historical.empty:
            # Calculate deviation per SKU
            sku_forecast_sum = df_forecast.groupby('sku_id')['forecast_units'].sum()
            sku_actual_sum = df_sales_historical.groupby('sku_id')['actual_sales_units'].sum()
            
            deviations = []
            for sku in sku_forecast_sum.index:
                forecast = sku_forecast_sum.get(sku, 0)
                actual = sku_actual_sum.get(sku, 0)
                if actual > 0:
                    deviation = ((forecast - actual) / actual) * 100
                    deviations.append(deviation)
            
            # Create histogram buckets (under/accurate/over format for frontend)
            if deviations:
                under_count = len([d for d in deviations if d < -10])  # Under-forecast
                accurate_count = len([d for d in deviations if -10 <= d <= 10])  # Accurate band
                over_count = len([d for d in deviations if d > 10])  # Over-forecast
                
                deviation_histogram = [
                    {"bucket": "under", "count": under_count},
                    {"bucket": "accurate", "count": accurate_count},
                    {"bucket": "over", "count": over_count}
                ]

        return jsonify({
            "kpis": kpis,
            "skuSalesTrend": sales_trend,
            "skuPerformance": sku_performance,
            "riskAlerts": high_risk_skus,
            "skuContributionHeatmap": heatmap,
            "topDemandDrivers": top_demand_drivers,
            "rollingError": rolling_error,
            "forecastDeviationHistogram": deviation_histogram,
            "highRiskSkus": high_risk_skus,
            "forecastCutoffDate": forecast_cutoff,  # Cutoff date for UI visualization
            "forecastHorizon": forecast_horizon,
            "historicalDays": historical_days  # Number of historical days shown
        })

    except Exception as e:
        print("CRITICAL SERVER ERROR:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# =========================================================
# FILTER METADATA
# =========================================================
@app.route("/api/filters", methods=["GET"])
def get_filter_metadata():
    try:
        df_sales = load_csv("sku_daily_sales.csv")
        df_forecast = load_csv("sku_daily_forecast.csv")
        df_sku_master = load_csv("sku_master.csv")
        df_demand = load_csv("raw_material_demand.csv")

        def get_unique_values(df, column):
            if df.empty or column not in df.columns:
                return []
            values = df[column].dropna().unique()
            return sorted([str(v) for v in values])

        filters = {
            "channels": get_unique_values(df_sales, "sales_channel"),
            "stores": get_unique_values(df_sales, "store_id"),
            "skus": get_unique_values(df_forecast, "sku_id"),
            "products": get_unique_values(df_sku_master, "product_id"),
            "categories": get_unique_values(df_sku_master, "category"),
            "rawMaterials": get_unique_values(df_demand, "raw_material"),
            "forecastHorizons": get_unique_values(df_forecast, "forecast_horizon"),
        }

        print("Filter metadata loaded:")
        for key, values in filters.items():
            print(f"   {key}: {len(values)} items")

        return jsonify(filters)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# =========================================================
# DYNAMIC FILTER OPTIONS - Products filtered by Raw Material
# =========================================================
@app.route("/api/filters/products", methods=["GET"])
def get_products_by_raw_material():
    """Get products that use a specific raw material"""
    try:
        raw_material = request.args.get("rawMaterial")
        df_bom = load_csv("product_bom.csv")
        df_sku_master = load_csv("sku_master.csv")
        
        if df_bom.empty or "raw_material" not in df_bom.columns:
            return jsonify({"products": []})
        
        if raw_material and raw_material != "all":
            # Get products that use this raw material
            products_using_rm = df_bom[df_bom["raw_material"] == raw_material]["product_id"].unique()
            products = sorted([str(p) for p in products_using_rm])
        else:
            # Return all products
            products = sorted(df_sku_master["product_id"].dropna().unique().astype(str))
        
        return jsonify({"products": products})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "products": []}), 500


# =========================================================
# DYNAMIC FILTER OPTIONS - Raw Materials filtered by Product
# =========================================================
@app.route("/api/filters/rawMaterials", methods=["GET"])
def get_raw_materials_by_product():
    """Get raw materials used by a specific product"""
    try:
        product = request.args.get("product")
        df_bom = load_csv("product_bom.csv")
        df_demand = load_csv("raw_material_demand.csv")
        
        if df_bom.empty or "raw_material" not in df_bom.columns:
            return jsonify({"rawMaterials": []})
        
        if product and product != "all":
            # Get raw materials used by this product
            raw_materials_used = df_bom[df_bom["product_id"] == product]["raw_material"].unique()
            raw_materials = sorted([str(rm) for rm in raw_materials_used])
        else:
            # Return all raw materials
            raw_materials = sorted(df_demand["raw_material"].dropna().unique().astype(str))
        
        return jsonify({"rawMaterials": raw_materials})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "rawMaterials": []}), 500


# =========================================================
# DYNAMIC FILTER OPTIONS - SKUs filtered by Category
# =========================================================
@app.route("/api/filters/skus", methods=["GET"])
def get_skus_by_category():
    """Get SKUs for a specific category"""
    try:
        category = request.args.get("category")
        df_sku_master = load_csv("sku_master.csv")
        df_forecast = load_csv("sku_daily_forecast.csv")
        
        if df_sku_master.empty or "category" not in df_sku_master.columns:
            return jsonify({"skus": []})
        
        if category and category != "all":
            # Get SKUs in this category
            skus_in_category = df_sku_master[df_sku_master["category"] == category]["sku_id"].unique()
            # Only return SKUs that have forecast data
            valid_skus = df_forecast["sku_id"].unique() if not df_forecast.empty else []
            skus = sorted([str(sku) for sku in skus_in_category if sku in valid_skus])
        else:
            # Return all SKUs that have forecast data
            skus = sorted(df_forecast["sku_id"].dropna().unique().astype(str)) if not df_forecast.empty else []
        
        return jsonify({"skus": skus})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "skus": []}), 500


# =========================================================
# DYNAMIC FILTER OPTIONS - Stores filtered by SKU
# =========================================================
@app.route("/api/filters/stores", methods=["GET"])
def get_stores_by_sku():
    """Get stores that have a specific SKU"""
    try:
        sku = request.args.get("sku")
        df_sales = load_csv("sku_daily_sales.csv")
        df_forecast = load_csv("sku_daily_forecast.csv")
        
        if sku and sku != "all":
            # Get stores that have this SKU (from both sales and forecast data)
            stores_from_sales = df_sales[df_sales["sku_id"] == sku]["store_id"].unique() if not df_sales.empty and "store_id" in df_sales.columns else []
            stores_from_forecast = df_forecast[df_forecast["sku_id"] == sku]["store_id"].unique() if not df_forecast.empty and "store_id" in df_forecast.columns else []
            # Combine and deduplicate
            all_stores = set(stores_from_sales) | set(stores_from_forecast)
            stores = sorted([str(s) for s in all_stores])
        else:
            # Return all stores
            stores_from_sales = df_sales["store_id"].dropna().unique() if not df_sales.empty and "store_id" in df_sales.columns else []
            stores_from_forecast = df_forecast["store_id"].dropna().unique() if not df_forecast.empty and "store_id" in df_forecast.columns else []
            all_stores = set(stores_from_sales) | set(stores_from_forecast)
            stores = sorted([str(s) for s in all_stores])
        
        return jsonify({"stores": stores})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "stores": []}), 500


@app.route("/api/consumption/risk-table", methods=["GET"])
def raw_material_risk_table():
    try:
        df = load_csv("raw_material_risk.csv")

        if df.empty:
            return jsonify([])

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        records = df.sort_values("date", ascending=False).to_dict(orient="records")

        return jsonify(records)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/consumption/material-table", methods=["GET"])
def raw_material_material_table():
    try:
        df = load_csv("raw_material_reconciliation.csv")

        if df.empty:
            return jsonify([])

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return jsonify(df.to_dict(orient="records"))

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/sales/forecast-table", methods=["GET"])
def sku_forecast_table():
    try:
        forecast_horizon = request.args.get("forecastHorizon", "30day")
        
        df = load_csv("sku_daily_forecast.csv")

        if df.empty:
            return jsonify([])

        # Filter by horizon
        if "forecast_horizon" in df.columns:
            df = df[df["forecast_horizon"] == forecast_horizon]

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return jsonify(df.to_dict(orient="records"))

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/flow/funnel", methods=["GET"])
def demand_flow_funnel():
    try:
        forecast_horizon = request.args.get("forecastHorizon", "30day")
        
        sku_df = load_csv("sku_daily_forecast.csv")
        prod_df = load_csv("product_forecast.csv")
        rm_df = load_csv("raw_material_demand.csv")
        
        # Filter by horizon
        if not sku_df.empty and "forecast_horizon" in sku_df.columns:
            sku_df = sku_df[sku_df["forecast_horizon"] == forecast_horizon]
        if not prod_df.empty and "forecast_horizon" in prod_df.columns:
            prod_df = prod_df[prod_df["forecast_horizon"] == forecast_horizon]
        if not rm_df.empty and "forecast_horizon" in rm_df.columns:
            rm_df = rm_df[rm_df["forecast_horizon"] == forecast_horizon]

        return jsonify({
            "skuForecast": safe_sum(sku_df, "forecast_units"),
            "productForecast": safe_sum(prod_df, "product_units"),
            "rawMaterialDemand": safe_sum(rm_df, "material_demand_units"),
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# =========================================================
# FRONTEND SERVING ROUTES
# =========================================================

@app.route("/")
def serve_frontend():
    if os.path.exists(WOODLAND_DIST_DIR):
        return send_from_directory(WOODLAND_DIST_DIR, "index.html")
    return jsonify({
        "message": "Woodland API Server",
        "status": "running",
        "note": "Frontend not built. Run 'npm run build' in Woodland folder",
        "endpoints": {
            "consumption_dashboard": "/api/consumption/dashboard",
            "sales_dashboard": "/api/sales/dashboard",
            "filters": "/api/filters",
            "consumption_risk_table": "/api/consumption/risk-table",
            "consumption_material_table": "/api/consumption/material-table",
            "sales_forecast_table": "/api/sales/forecast-table",
            "flow_funnel": "/api/flow/funnel"
        }
    })


@app.route("/<path:path>")
def serve_static_or_spa(path):
    if not os.path.exists(WOODLAND_DIST_DIR):
        return jsonify({"error": "Frontend not built"}), 404
    
    file_path = os.path.join(WOODLAND_DIST_DIR, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(WOODLAND_DIST_DIR, path)
    
    return send_from_directory(WOODLAND_DIST_DIR, "index.html")


# =========================================================
# HEALTH CHECK ENDPOINT
# =========================================================
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "server": "Woodland API",
        "port": 5051,
        "frontend_built": os.path.exists(WOODLAND_DIST_DIR)
    })


# =========================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Woodland Forecast API Server")
    print("=" * 60)
    print(f"  API running at: http://localhost:5051")
    print(f"  Frontend dist:  {'Found' if os.path.exists(WOODLAND_DIST_DIR) else 'Not built'}")
    print("")
    print("  Endpoints:")
    print("    /api/consumption/dashboard")
    print("    /api/sales/dashboard")
    print("    /api/filters")
    print("    /api/health")
    print("=" * 60)
    app.run(debug=True, use_reloader=False, port=5051)


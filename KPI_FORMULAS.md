# KPI Calculation Formulas - Consumption Dashboard

## Main KPIs

### 1. **Projected Demand** (Total Forecasted Raw Material Demand)
```
Total Forecasted Demand = Σ(material_demand_units) for all forecast dates
```
- **Source**: `raw_material_demand.csv` (filtered by forecast_horizon: 7day or 30day)
- **Note**: Sum of all daily forecasted demand units across the forecast period

---

### 2. **Baseline Consumption** (Trailing N-Day Consumption)
```
Baseline Consumption = Σ(consumed_quantity) for last N days
```
- **Source**: `raw_material_inventory_ledger.csv` (historical period)
- **N**: Matches forecast period (7 or 30 days)
- **Product Filter**: If product selected, allocates proportionally:
  ```
  Product Consumption = Total Consumption × (Product Demand / Total Demand)
  ```

---

### 3. **Forecast Accuracy** (Consumption Forecast Accuracy)
```
Forecast Daily Avg = Total Forecasted Demand / Forecast Days
Historical Daily Avg = Baseline Consumption / Historical Days
MAPE = |Forecast Daily Avg - Historical Daily Avg| / Historical Daily Avg × 100
Accuracy = max(0, min(100, 100 - MAPE))
```
- **Range**: 0-100% (higher is better)

---

### 4. **Projected Overstock**
```
Expected Inflow = Average Daily Inflow × Forecast Days
Projected Inventory = Closing Inventory + Expected Inflow - Forecasted Demand
Overstock = max(0, Projected Inventory - Safety Stock)
Total Overstock = Σ(Overstock) across all materials
```
- **Why Cumulative Demand?**: Uses **total forecasted demand** (sum of all days) because we're projecting inventory at the **end** of the forecast period
- **Logic**: After N days of demand and inflow, what will inventory be vs safety stock?

---

### 5. **Days to Stockout**
```
Daily Demand = Forecasted Demand / Forecast Days
Daily Inflow = Expected Inflow / Forecast Days
Net Daily Consumption = Daily Demand - Daily Inflow
Days to Stockout = Closing Inventory / Net Daily Consumption (if > 0, else 999)
Result = min(Days to Stockout) across all materials
```
- **999** = No risk (inflow >= demand or no consumption)

---

## Supporting Calculations

### Expected Inflow
```
Average Daily Inflow = mean(inflow_quantity) from full historical data
Expected Inflow = Average Daily Inflow × Forecast Days
```
- **Why full historical?**: More stable average, not affected by filter period

### Product-Specific Allocation
```
Allocation Factor = Product Demand / Total Demand (for each raw material)
Allocated Value = Total Value × Allocation Factor
```
- Applied to: Consumption, Closing Inventory, Safety Stock, Expected Inflow

---

## Reconciliation File Columns (from supply_demand_reconciliation.py)

### inventory_gap_units
```
inventory_gap_units = closing_inventory - material_demand_units
```
- **Purpose**: Daily gap (positive = surplus, negative = shortfall)

### cumulative_demand
```
cumulative_demand = cumsum(material_demand_units) grouped by [forecast_horizon, raw_material]
```
- **Purpose**: Running total of demand from start of forecast period
- **Why used?**: To calculate running inventory balance over time

### running_inventory_balance
```
running_inventory_balance = closing_inventory - cumulative_demand
```
- **Purpose**: Shows how inventory depletes day-by-day as cumulative demand increases
- **Used in Risk Detection**: If < 0 → STOCKOUT_RISK

### inventory_risk_flag
```
Risk Classification Rules:
- STOCKOUT_RISK: running_balance < 0 OR closing <= 0
- DEMAND_SHORTFALL_RISK: inventory_gap_units < 0 (daily demand > inventory)
- LOW_STOCK_RISK: closing < safety_stock OR running_balance < safety_stock
- OVERSTOCK_RISK: closing > 1.5 × safety_stock
- NORMAL: otherwise
```

---

## Why Cumulative Demand in Projected Overstock?

**Answer**: The projected overstock calculation uses **total forecasted demand** (sum of all days), not cumulative demand. However, cumulative demand is used in:

1. **Running Inventory Balance** (in reconciliation file):
   - Tracks day-by-day depletion: `running_balance = closing - cumulative_demand`
   - Used for risk detection to identify when inventory will run out

2. **Projected Overstock** (in KPIs):
   - Uses **total forecasted demand** (sum of all forecast days)
   - Formula: `Projected = Closing + Inflow - Total Demand`
   - This projects inventory at the **end** of the forecast period

**Key Difference**:
- **Cumulative Demand**: Day-by-day running total (used for running balance)
- **Total Forecasted Demand**: Sum of all days (used for projected overstock)

---

## Data Flow Summary

```
SKU Forecast → Product Demand → Raw Material Demand
                                           ↓
                                    Forecasted Demand (total)
                                           ↓
                    Closing Inventory + Expected Inflow - Forecasted Demand
                                           ↓
                                    Projected Inventory
                                           ↓
                    Projected Inventory - Safety Stock = Overstock
```

---

# KPI Calculation Formulas - Sales Dashboard

## Main KPIs

### 1. **Projected Sales** (Total Forecasted Units)

**Metric key:** `totalForecastedUnits`

```text
Total Forecasted Units = Σ(forecast_units) over all forecast rows
```

- **Source**: `sku_daily_forecast.csv` (filtered by `forecast_horizon` = `7day` or `30day` based on `dateRange` filter)
- **Forecast Days**:  
  \[
  \text{forecast\_days} =
  \begin{cases}
  7 & \text{if dateRange = next-7} \\
  30 & \text{if dateRange = next-30}
  \end{cases}
  \]

---

### 2. **Baseline Sales** (Historical Sales for Last N Days)

**Metric key:** `baselineSales`

```text
Baseline Sales = Σ(actual_sales_units) over the last N historical days
```

- **Source**: `sku_daily_sales.csv`
- **Historical window**:
  - Let `FORECAST_CUTOFF_DATE` be the last historical date (e.g., 2026‑02‑05).
  - Let `historical_days = forecast_days` (7 or 30, matched to forecast horizon).
  - Historical period:
    ```text
    historical_start = FORECAST_CUTOFF_DATE - (historical_days - 1)
    historical_end   = FORECAST_CUTOFF_DATE
    ```
  - Filter:
    ```text
    df_sales_historical = df_sales[
        (date >= historical_start) AND (date <= FORECAST_CUTOFF_DATE)
    ]
    ```
- **Baseline Sales**:
  ```text
  Baseline Sales (total_historical_units)
      = Σ(actual_sales_units) in df_sales_historical
  ```

---

### 3. **Forecast Accuracy** (Sales Forecast Accuracy vs Baseline)

**Metric key:** `skuForecastAccuracy`

```text
Forecast Daily Avg   = Total Forecasted Units / forecast_days
Historical Daily Avg = Baseline Sales / historical_days

MAPE  = |Forecast Daily Avg − Historical Daily Avg|
        / Historical Daily Avg × 100

Accuracy = max(0, min(100, 100 − MAPE))
```

- **Range**: 0–100% (higher = better).
- **Note**: Uses daily averages so that 7‑day and 30‑day horizons are comparable.

---

### 4. **Demand Volatility Index**

**Metric key:** `demandVolatilityIndex`

```text
Volatility = stddev(forecast_units) over all forecast rows
```

- **Source**: `sku_daily_forecast.csv` (same filtered forecast set used for Projected Sales).
- **Interpretation**:
  - Higher value = more variation in daily forecast units (less stable demand).

---

### 5. **At‑Risk SKUs** (High Risk Count)

**Metric key:** `highRiskSKUsCount`

This KPI is derived from SKU‑level performance metrics built from both forecast and historical data.

1. **Aggregate forecast per SKU**
   ```text
   sku_forecast_agg = df_forecast
       .groupby(sku_id)
       .agg({
         forecast_units: [sum, std, mean]
       })

   total_forecast (per SKU)   = sum(forecast_units)
   volatility (per SKU)       = std(forecast_units)
   avg_forecast_daily (per SKU) = mean(forecast_units)
   ```

2. **Aggregate historical actuals per SKU**
   ```text
   sku_actual_agg = df_sales_historical
       .groupby(sku_id)
       .agg({
         actual_sales_units: [sum, mean, std]
       })

   total_actual (per SKU)  = sum(actual_sales_units)
   avg_daily (per SKU)     = mean(actual_sales_units)
   actual_volatility       = std(actual_sales_units)
   ```

3. **Join metrics**
   ```text
   sku_metrics = merge(sku_forecast_agg, sku_actual_agg, on="sku_id", how="outer").fillna(0)
   ```

4. **Per‑SKU Accuracy**

For each SKU:
```text
if avg_daily > 0:
    accuracy_sku = max(0, 100 − |avg_forecast_daily − avg_daily| / avg_daily × 100)
else:
    accuracy_sku = 0
```

5. **Distribution‑based thresholds**

Across all SKUs:
```text
accuracy_mean = mean(accuracy_sku)
accuracy_std  = std(accuracy_sku) (or 1 if only one SKU)
volatility_mean = mean(volatility)

high_risk_threshold = accuracy_mean − accuracy_std        # bottom ~16%
med_risk_threshold  = accuracy_mean − accuracy_std * 0.3  # bottom ~35%
```

6. **Risk Classification per SKU**

```text
if accuracy_sku < high_risk_threshold:
    risk = "High"
elif volatility > volatility_mean * 1.5 and volatility_mean > 0:
    risk = "High"
elif accuracy_sku < med_risk_threshold:
    risk = "Medium"
else:
    risk = "Low"
```

7. **KPI: High Risk Count**

```text
highRiskSKUsCount = number of SKUs where risk == "High"
```

This is returned as:

```json
"highRiskSKUsCount": { "value": highRiskSKUsCount, "trend": highRiskSKUsCount, ... }
```

---

## Summary: Consumption vs Sales KPIs

- **Consumption Dashboard**
  - Projected Demand = Σ material_demand_units (future raw material demand)
  - Baseline Consumption = Σ consumed_quantity over last N days
  - Consumption Forecast Accuracy = MAPE between forecasted vs historical daily consumption
  - Projected Overstock = max(0, Projected Inventory − Safety Stock)
  - Days to Stockout = min over materials of Closing / Net Daily Consumption

- **Sales Dashboard**
  - Projected Sales = Σ forecast_units (future SKU demand)
  - Baseline Sales = Σ actual_sales_units over last N days
  - Sales Forecast Accuracy = MAPE between forecasted vs historical daily sales
  - Demand Volatility Index = stddev of forecast_units
  - At‑Risk SKUs = count of SKUs classified as High risk based on low accuracy and/or high volatility


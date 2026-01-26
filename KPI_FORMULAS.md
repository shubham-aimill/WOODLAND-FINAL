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

# Data Source Schemas

This document describes the schema (structure, columns, data types, and constraints) for the key source data files used in the Woodland system.

---

## 1. Daily Sales Source Data

### File: `sku_daily_sales.csv`

**Description:** Daily SKU-level actual sales data at store level, including promotion indicators. This is the primary historical fact table for sales transactions.

**Schema:**

| Column Name | Data Type | Description | Constraints | Example Values |
|------------|-----------|-------------|-------------|----------------|
| `date` | Date (YYYY-MM-DD) | Sales transaction date | Required, valid date | `2024-01-01`, `2025-12-31` |
| `sku_id` | String | Unique SKU or product identifier | Required, Format: `WL-SKU-XXX` | `WL-SKU-001`, `WL-SKU-002` |
| `store_id` | String | Identifier of the store where the sale occurred | Required, Format: `Store_XX` | `Store_01`, `Store_02` |
| `sales_channel` | String | Channel through which the sale occurred | Required, Enum | `E-Commerce`, `Offline Retail` |
| `actual_sales_units` | Integer | Actual number of units sold | Required, ≥ 0, Aggregation: SUM | `22`, `25`, `31` |
| `promotion_flag` | Integer | Indicates whether the SKU was under promotion (1 = yes, 0 = no) | Required, Enum: [0, 1] | `0`, `1` |

**Key Characteristics:**
- **Granularity:** One row per SKU per Store per Date per Channel
- **Aggregation Rules:**
  - `actual_sales_units`: Use SUM when aggregating across dates, stores, channels, or SKUs
  - `date`: Do NOT aggregate (use for filtering/grouping)
  - `promotion_flag`: Use MAX or COUNT for analysis
- **Primary Use Cases:**
  - Historical sales analysis
  - Baseline sales calculation for forecast accuracy
  - Channel and store performance analysis
  - Promotion impact analysis

**Sample Data:**
```csv
date,sku_id,store_id,sales_channel,actual_sales_units,promotion_flag
2024-01-01,WL-SKU-001,Store_01,E-Commerce,22,0
2024-01-01,WL-SKU-001,Store_02,Offline Retail,25,0
2024-01-01,WL-SKU-001,Store_14,Offline Retail,30,1
```

---

## 2. Raw Material Source Data

### File: `raw_material_inventory.csv`

**Description:** Daily raw material inventory levels and movements. Each row represents inventory state for a raw material on a specific date.

**Schema:**

| Column Name | Data Type | Description | Constraints | Example Values |
|------------|-----------|-------------|-------------|----------------|
| `date` | Date (YYYY-MM-DD) | Inventory record date | Required, valid date | `2025-09-01`, `2025-12-31` |
| `raw_material` | String | Name or identifier of the raw material | Required, Case-insensitive matching | `EVA_Foam`, `Leather_FG`, `Rubber_Sole`, `Textile_Nylon`, `Leather_Suede`, `Metal_Eyelet`, `Metal_Buckle`, `Textile_Lining`, `Metal_Zip` |
| `opening_inventory` | Integer | Inventory units available at the start of the day | Required, ≥ 0, **Do NOT sum across days** | `103271`, `308749` |
| `inflow_quantity` | Integer | Quantity of raw material added to inventory on the day | Required, ≥ 0, Aggregation: SUM | `0`, `74196` |
| `consumed_quantity` | Integer | Quantity of raw material consumed during the day | Required, ≥ 0, Aggregation: SUM | `8012`, `14435` |
| `closing_inventory` | Integer | Inventory units available at the end of the day | Required, ≥ 0, **Do NOT sum across days** | `99824`, `298845` |
| `safety_stock` | Integer | Minimum required inventory level to avoid stockout | Required, ≥ 0 | `112000`, `210000` |

**Key Characteristics:**
- **Granularity:** One row per Raw Material per Date
- **Inventory Balance Formula:** `closing_inventory = opening_inventory + inflow_quantity - consumed_quantity`
- **Aggregation Rules:**
  - `opening_inventory`, `closing_inventory`: **Do NOT sum across days** (these are snapshots)
  - `inflow_quantity`, `consumed_quantity`: Use SUM when aggregating across dates
  - `safety_stock`: Typically constant per material (use MAX or first value)
- **Primary Use Cases:**
  - Inventory level tracking
  - Consumption analysis
  - Stockout risk calculation
  - Days to stockout calculation

**Sample Data:**
```csv
date,raw_material,opening_inventory,inflow_quantity,consumed_quantity,closing_inventory,safety_stock
2025-09-01,EVA_Foam,103271,0,8012,99824,112000
2025-09-01,Leather_FG,308749,0,14435,298845,210000
2025-09-11,EVA_Foam,28759,74196,9087,93868,112000
```

---

## 3. Raw Material Inventory Ledger (Extended)

### File: `raw_material_inventory_ledger.csv`

**Description:** Comprehensive raw material inventory ledger with calculated closing inventory and validation status. Includes all inventory movements and calculated validations.

**Schema:**

| Column Name | Data Type | Description | Constraints |
|------------|-----------|-------------|-------------|
| `date` | Date | Inventory record date | Required |
| `raw_material` | String | Name or identifier of the raw material | Required |
| `opening_inventory` | Integer | Inventory units at start of day | Required, ≥ 0 |
| `inflow_quantity` | Integer | Quantity added to inventory | Required, ≥ 0 |
| `consumed_quantity` | Integer | Quantity consumed from inventory | Required, ≥ 0 |
| `closing_inventory` | Integer | Recorded closing inventory units at end of day | Required, ≥ 0 |
| `safety_stock` | Integer | Minimum required inventory level | Required, ≥ 0 |
| `calculated_closing_inventory` | Integer | Calculated closing inventory (opening + inflow - consumed) | Calculated field |
| `inventory_validation_status` | Boolean | Flag indicating if recorded closing matches calculated value | `true` or `false` |

**Key Characteristics:**
- **Validation:** `inventory_validation_status = (closing_inventory == calculated_closing_inventory)`
- **Use Case:** Data quality validation and reconciliation

---

## 4. Raw Material Demand (Forecast)

### File: `raw_material_demand.csv`

**Description:** Forecasted daily raw material demand for future periods.

**Schema:**

| Column Name | Data Type | Description | Constraints | Example Values |
|------------|-----------|-------------|-------------|----------------|
| `date` | Date (YYYY-MM-DD) | Forecast date | Required, future date | `2026-02-06` |
| `raw_material` | String | Name or identifier of the raw material | Required | `EVA_Foam`, `Leather_FG` |
| `material_type` | String | Category of raw material | Required | `Rubber`, `Leather`, `Metal`, `Textile` |
| `forecast_horizon` | String | Forecast horizon identifier | Required, Enum | `7day`, `30day` |
| `material_demand_units` | Integer | Forecasted demand units for the material on this date | Required, ≥ 0 | `6093`, `11582` |

**Key Characteristics:**
- **Granularity:** One row per Raw Material per Date per Forecast Horizon
- **Aggregation:** `material_demand_units` should be SUM when aggregating across dates
- **Use Case:** Future demand planning and inventory projection

**Sample Data:**
```csv
date,raw_material,material_type,forecast_horizon,material_demand_units
2026-02-06,EVA_Foam,Rubber,30day,6093
2026-02-06,Leather_FG,Leather,30day,11582
2026-02-07,EVA_Foam,Rubber,30day,7135
```

---

## 5. Data Relationships

### Key Relationships:

1. **Sales → Products → Raw Materials:**
   - `sku_daily_sales.sku_id` → `sku_master.sku_id` → `sku_product_allocation.product_id` → `product_bom.product_id` → `product_bom.raw_material`

2. **Inventory Tracking:**
   - `raw_material_inventory.raw_material` = `raw_material_demand.raw_material`
   - Used for reconciliation: Forecast Demand vs Available Inventory

3. **Date Semantics:**
   - **Historical Data:** `sku_daily_sales.date` and `raw_material_inventory.date` (up to cutoff date)
   - **Forecast Data:** `raw_material_demand.date` (future dates after cutoff)

---

## 6. Common Raw Materials

The system tracks the following raw materials:

- **Rubber:** `EVA_Foam`, `Rubber_Sole`
- **Leather:** `Leather_FG`, `Leather_Suede`
- **Metal:** `Metal_Buckle`, `Metal_Eyelet`, `Metal_Zip`
- **Textile:** `Textile_Lining`, `Textile_Nylon`

---

## 7. Important Notes

1. **Date Format:** All dates are in `YYYY-MM-DD` format (ISO 8601)
2. **Aggregation Warnings:**
   - Never sum `opening_inventory` or `closing_inventory` across dates (they are snapshots)
   - Always sum `inflow_quantity` and `consumed_quantity` when aggregating
3. **Data Quality:**
   - Use `raw_material_inventory_ledger` for validation checks
   - `inventory_validation_status` should be `true` for all records
4. **Forecast Cutoff:** Historical data ends at `2026-02-05`, forecasts start from `2026-02-06`

---

## 8. File Locations

All data files are located in: `/datasets/`

- `sku_daily_sales.csv` - Daily sales transactions
- `raw_material_inventory.csv` - Daily inventory levels
- `raw_material_inventory_ledger.csv` - Inventory ledger with validation
- `raw_material_demand.csv` - Forecasted material demand

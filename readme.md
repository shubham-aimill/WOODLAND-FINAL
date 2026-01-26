Woodland Demand Forecasting & Inventory Intelligence Backend
1. Overview

This backend system powers Woodland’s end-to-end demand forecasting and raw-material risk intelligence platform.

It transforms historical SKU sales data into:

SKU-level demand forecasts

Product-level demand distribution

Raw material consumption forecasts

Inventory reconciliation

Stockout and overstock risk detection

The backend is designed with strict governance:

Forecasting logic exists only in backend

Inventory logic exists only in backend

Frontend consumes finalized datasets only

No KPI computation occurs on frontend

2. High-Level Architecture

Historical Sales
      ↓
SKU Forecasting
      ↓
SKU → Product Allocation
      ↓
Product Demand
      ↓
Product Forecast
      ↓
BOM Mapping
      ↓
Raw Material Demand
      ↓
Inventory Ledger
      ↓
Supply–Demand Reconciliation
      ↓
Inventory Risk Classification
      ↓
Frontend Dashboards


Each step produces an authoritative dataset consumed by the next stage.

3. Folder Structure
woodland-backend/
│
├── datasets/
│   ├── sku_daily_sales.csv
│   ├── sku_forecast.csv
│   ├── sku_product_allocation.csv
│   ├── sku_product_demand.csv
│   ├── product_forecast.csv
│   ├── product_bom.csv
│   ├── product_bom_expanded.csv
│   ├── raw_material_demand.csv
│   ├── raw_material_inventory.csv
│   ├── raw_material_inventory_ledger.csv
│   ├── raw_material_reconciliation.csv
│   └── raw_material_risk.csv
│
├── scripts/
│   ├── sku_forecast.py
│   ├── sku_product_allocation.py
│   ├── sku_product_demand.py
│   ├── product_forecast.py
│   ├── bom_mapping.py
│   ├── demand_explosion.py
│   ├── inventory_state_tracking.py
│   ├── supply_demand_reconciliation.py
│   └── inventory_risk_detection.py
│
└── README.md

4. Core Design Principles
4.1 Separation of Concerns
Layer	Responsibility
Forecasting	Predict future demand
Allocation	Distribute demand logically
BOM	Translate products → materials
Inventory	Track stock movement
Reconciliation	Compare demand vs supply
Risk	Classify business impact

Each script performs one business responsibility only.

4.2 Date Semantics (Critical)

The system uses two different time concepts:

Concept	Meaning
Inventory Date	Historical snapshot
Forecast Horizon	Future demand window

They are never merged blindly.

Example:

Inventory available till: 2024-12-31

Forecast horizon: 2025-01-01 → 2025-01-30

Reconciliation compares:

Forecast demand (future)
vs
Inventory snapshot (latest available)

5. Input Datasets
5.1 sku_daily_sales.csv

Historical transactional sales.

Column	Description
date	Sales date
sku_id	SKU identifier
store_id	Store
actual_sales_units	Units sold

This is the only historical fact table.

5.2 product_bom.csv

Defines Bill of Materials per product.

Column	Description
product_id	Product
raw_material	Material used
material_type	Leather / Rubber / Textile / Metal
consumption_per_unit	Units consumed per product
5.3 raw_material_inventory.csv

Historical inventory movements.

Column	Description
date	Inventory date
raw_material	Material
opening_inventory	Opening stock
inflow_quantity	Procurement
consumed_quantity	Usage
closing_inventory	Closing stock
safety_stock	Minimum buffer
6. Backend Processing Pipeline
Step 1 — SKU Forecasting

Script

sku_forecast.py


Purpose

Forecast total SKU demand for the next N days.

Output

sku_forecast.csv


Key Fields

Field	Meaning
forecast_start_date	Day after last historical date
forecast_end_date	start + horizon
sku_id	SKU
store_id	Store
forecast_units	Total horizon demand

This forecast represents aggregate demand across the next 30 days, not daily predictions.

Step 2 — SKU → Product Allocation

Script

sku_product_allocation.py


Purpose

Infer product mix inside each SKU using historical contribution.

Logic

allocation_weight =
product_units / total_sku_units


Output

sku_product_allocation.csv

Step 3 — SKU Product Demand

Script

sku_product_demand.py


Purpose

Disaggregate SKU forecast into product demand.

Formula

product_units =
sku_forecast_units × allocation_weight


Output

sku_product_demand.csv

Step 4 — Product Forecast

Script

product_forecast.py


Purpose

Aggregate product demand across all SKUs and stores.

Output

product_forecast.csv


This dataset becomes the single product demand truth.

Step 5 — BOM Mapping

Script

bom_mapping.py


Purpose

Attach BOM definitions to product forecast.

Output

product_bom_expanded.csv


Each product row expands into multiple raw material rows.

Step 6 — Demand Explosion

Script

demand_explosion.py


Purpose

Convert product demand into raw material demand.

Formula

material_demand_units =
product_units × consumption_per_unit


Output

raw_material_demand.csv


This dataset represents future consumption requirement.

Step 7 — Inventory State Tracking

Script

inventory_state_tracking.py


Purpose

Validate and standardize inventory movements.

Validation

opening + inflow − consumed = calculated_closing


Output

raw_material_inventory_ledger.csv

Step 8 — Supply–Demand Reconciliation

Script

supply_demand_reconciliation.py


Purpose

Compare forecasted raw material demand against latest inventory snapshot.

Formula

inventory_gap_units =
closing_inventory − material_demand_units


Output

raw_material_reconciliation.csv


Negative gap indicates shortage risk.

Step 9 — Inventory Risk Detection

Script

inventory_risk_detection.py


Purpose

Classify business risk per raw material.

Rules

Condition	Risk
closing < safety_stock	STOCKOUT_RISK
closing > 1.5 × safety	OVERSTOCK_RISK
otherwise	NORMAL

Output

raw_material_risk.csv


This dataset is consumed directly by frontend dashboards.

7. Execution Order

Scripts must be executed sequentially:

1. sku_forecast.py
2. sku_product_allocation.py
3. sku_product_demand.py
4. product_forecast.py
5. bom_mapping.py
6. demand_explosion.py
7. inventory_state_tracking.py
8. supply_demand_reconciliation.py
9. inventory_risk_detection.py


Each script depends on the output of the previous step.

8. Frontend Consumption

Frontend dashboards never compute KPIs.

They consume only:

sku_forecast.csv

raw_material_demand.csv

raw_material_reconciliation.csv

raw_material_risk.csv

raw_material_inventory_ledger.csv

All aggregation logic occurs in backend APIs.



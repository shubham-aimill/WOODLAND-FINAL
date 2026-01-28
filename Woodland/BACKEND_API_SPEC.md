# Backend API Spec – Woodland Dashboards

This document describes the API contracts the frontend expects. The app uses **two combined endpoints** (one per dashboard). All filter params are sent as query string; response must be JSON.

---

## Base URLs & env

- **Consumption:** `VITE_CONSUMPTION_API_URL` or `VITE_API_BASE_URL` (default `"/api"`).
- **Sales:** `VITE_SALES_API_URL` or `VITE_API_BASE_URL` (default `"/api"`).

If unset or `"/api"`, the frontend uses **mock data** and does not call the backend. To integrate, set e.g.:

```
VITE_CONSUMPTION_API_URL=https://your-api.example.com
VITE_SALES_API_URL=https://your-api.example.com
```

- **Method:** GET  
- **Headers:** `Content-Type: application/json`  
- **CORS:** Allow origin of the frontend (e.g. `http://localhost:5173` in dev).

---

## Query parameters (all requests)

Every dashboard request includes these. Backend should accept and optionally filter by them. When value is `"all"`, frontend means “no filter”.

| Param | Type | Values | Used by |
|-------|------|--------|---------|
| `dateRange` | string | `last-7`, `last-30`, `last-90`, `ytd`, `custom` | Both |
| `channel` | string | `all`, `retail`, `wholesale`, `ecommerce`, `direct` | Both |
| `store` | string | `all`, `store-1` … `store-5` | Sales |
| `sku` | string | `all`, `sku-1` … `sku-4` | Sales |
| `view` | string | `daily`, `weekly`, `monthly` | Sales |
| `raw_material` | string | `all`, `rm-1` … `rm-4` | Consumption |
| `product_id` | string | `all`, `prod-1` … `prod-4` | Consumption |
| `category` | string | `all`, `Footwear`, `Apparel`, `Bags`, `Accessories` | Sales |
| `aggregation` | string | `daily`, `weekly` | Consumption |
| `rollingWindow` | string | `7`, `14`, `30` | Sales (rolling error) |

`raw_material`, `product_id`, `category` are only sent when not `"all"`. Others are always sent.

---

## 1. Consumption dashboard

**Endpoint:** `GET /consumption/dashboard?{params}`  
**Base URL:** `VITE_CONSUMPTION_API_URL` / `VITE_API_BASE_URL`

**Response:** JSON matching `ConsumptionDashboardData`:

```ts
{
  "kpis": {
    "totalForecastedRMDemand": { "value": number, "trend": number, "direction": "up" | "down" | "neutral" },
    "actualRMConsumption": { "value": number, "trend": number, "direction": "up" | "down" | "neutral" },
    "consumptionForecastAccuracy": { "value": number, "trend": number, "direction": "up" | "down" | "neutral" },
    "inventoryExcessUnits": { "value": number, "trend": number, "direction": "up" | "down" | "neutral" },
    "inventoryShortfallUnits": { "value": number, "trend": number, "direction": "up" | "down" | "neutral" }
  },
  "rawMaterialDemandTrend": [
    { "date": string, "forecast": number, "actual": number }
  ],
  "rawMaterialRiskTable": [
    {
      "id": string,
      "rawMaterial": string,
      "forecastDemand": number,
      "actualConsumption": number,
      "closingInventory": number,
      "safetyStock": number,
      "riskStatus": "Overstock" | "Stockout" | "Balanced"
    }
  ],
  "demandFlowFunnel": {
    "steps": {
      "skuForecast": { "label": string, "value": number, "unit": string },
      "productMix": { "label": string, "value": number, "unit": string },
      "productForecast": { "label": string, "value": number, "unit": string },
      "rawMaterialDemand": { "label": string, "value": number, "unit": string }
    }
  },
  "forecastComparison": [
    {
      "date": string,
      "actual": number,
      "forecast": number,
      "confidenceLow": number,
      "confidenceHigh": number
    }
  ],
  "consumptionErrorHeatmap": [
    { "date": string, "rawMaterial": string, "forecastErrorPct": number }
  ]
}
```

- **Wireframe:** KPIs from Steps 6–10; trend X = `date`, Y = `material_demand_units`; heatmap X = Date, Y = Raw Material, color = Forecast Error %.

---

## 2. Sales dashboard

**Endpoint:** `GET /sales/dashboard?{params}`  
**Base URL:** `VITE_SALES_API_URL` / `VITE_API_BASE_URL`

**Response:** JSON matching `SalesDashboardData`:

```ts
{
  "kpis": {
    "skuForecastAccuracy": { "value": number, "trend": number, "direction": "up" | "down" | "neutral" },
    "totalForecastedUnits": { "value": number, "trend": number, "direction": "up" | "down" | "neutral" },
    "baselineSales": { "value": number, "trend": number, "direction": "up" | "down" | "neutral" },
    "demandVolatilityIndex": { "value": number, "trend": number, "direction": "up" | "down" | "neutral" },
    "highRiskSKUsCount": { "value": number, "trend": number, "direction": "up" | "down" | "neutral" }
  },
  "skuSalesTrend": [
    { "date": string, "actual": number, "forecast": number, "channel"?: string }
  ],
  "skuPerformance": [
    {
      "id": number,
      "sku": string,
      "name": string,
      "category": string,
      "avgDailySales": number,
      "accuracy": number,
      "demandVolatility": number,
      "riskFlag": "low" | "medium" | "high"
    }
  ],
  "riskAlerts": [
    {
      "id": number,
      "sku": string,
      "name": string,
      "category": string,
      "severity": "high" | "critical",
      "issue": string,
      "recommendation": string,
      "daysUntilStockout"?: number
    }
  ],
  "skuContributionHeatmap": [
    { "sku": string, "date": string, "contributionPct": number }
  ],
  "topDemandDrivers": [
    {
      "sku": string,
      "name": string,
      "contributionPct": number,
      "trendDirection": "up" | "down" | "flat"
    }
  ],
  "rollingError": [
    { "date": string, "mape": number, "bias"?: number }
  ],
  "forecastDeviationHistogram": [
    { "bucket": "under" | "accurate" | "over", "count": number }
  ]
}
```

- **rollingError:** Respect `rollingWindow` (7 / 14 / 30). `date` = bucket label (e.g. `"W1"`, `"2025-01-20"`).
- **skuContributionHeatmap:** Frontend uses X = SKU, Y = Date; ensure both dimensions are present.

---

## Error handling

- **HTTP 4xx/5xx:** Frontend falls back to **mock data** and logs a warning. No retries.
- **JSON parse error:** Same fallback.
- Optional: return `{ "message": string }` for API-side error details.

---

## TypeScript source of truth

All request/response types live in:

- `src/services/api.ts` – interfaces, `filtersToParams`, fetch helpers  
- `src/contexts/FilterContext.tsx` – filter enums and `FilterState`

Mock implementations in `src/services/mockData.ts` show sample shapes and filter-aware behavior.

---

## Checklist for backend

- [ ] Implement `GET /consumption/dashboard` and `GET /sales/dashboard`.
- [ ] Accept query params above; filter data accordingly.
- [ ] Return JSON matching the response shapes (extra fields are ignored).
- [ ] Set CORS and base URLs via env. Frontend uses mocks until URLs are configured.

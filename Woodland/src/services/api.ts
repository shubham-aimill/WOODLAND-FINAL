// /**
//  * API Service Layer
//  *
//  * This file provides the structure to connect to your external API.
//  * Replace the BASE_URL and implement the fetch logic for your backend.
//  */

// import { FilterState } from "@/contexts/FilterContext";

// const CONSUMPTION_API_URL = import.meta.env.VITE_CONSUMPTION_API_URL || import.meta.env.VITE_API_BASE_URL || "/api";
// const SALES_API_URL = import.meta.env.VITE_SALES_API_URL || import.meta.env.VITE_API_BASE_URL || "/api";

// async function apiRequest<T>(
//   endpoint: string,
//   options: RequestInit = {},
//   baseUrl?: string
// ): Promise<T> {
//   const url = `${baseUrl || CONSUMPTION_API_URL}${endpoint}`;
//   const config: RequestInit = {
//     headers: {
//       "Content-Type": "application/json",
//       ...options.headers,
//     },
//     ...options,
//   };
//   const response = await fetch(url, config);
//   if (!response.ok) {
//     const errorData = await response.json().catch(() => ({}));
//     throw new Error(errorData.message || `API Error: ${response.status}`);
//   }
//   return response.json();
// }

// function filtersToParams(filters: FilterState): URLSearchParams {
//   const params = new URLSearchParams();
//   params.append("dateRange", filters.dateRange);
//   if (filters.channel !== "all") params.append("channel", filters.channel);
//   if (filters.store !== "all") params.append("store", filters.store);
//   if (filters.sku !== "all") params.append("sku", filters.sku);
//   params.append("view", filters.view);
//   if (filters.rawMaterial !== "all") params.append("raw_material", filters.rawMaterial);
//   if (filters.product !== "all") params.append("product_id", filters.product);
//   if (filters.category !== "all") params.append("category", filters.category);
//   if (filters.aggregation) params.append("aggregation", filters.aggregation);
//   if (filters.rollingWindow) params.append("rollingWindow", filters.rollingWindow);
//   return params;
// }

// // ============ KPI Types (wireframe-aligned) ============

// type KpiMetric = { value: number; trend: number; direction: "up" | "down" | "neutral" };

// export interface KPIData {
//   totalForecastedRMDemand: KpiMetric;
//   actualRMConsumption: KpiMetric;
//   consumptionForecastAccuracy: KpiMetric;
//   inventoryExcessUnits: KpiMetric;
//   inventoryShortfallUnits: KpiMetric;
// }

// export interface SalesKPIData {
//   skuForecastAccuracy: KpiMetric;
//   totalForecastedUnits: KpiMetric;
//   forecastBias: KpiMetric;
//   demandVolatilityIndex: KpiMetric;
//   highRiskSKUsCount: KpiMetric;
// }

// // ============ Trend ============

// export interface RawMaterialDemandTrendPoint {
//   date: string;
//   forecast: number;
//   actual: number;
// }

// export interface SKUSalesTrendPoint {
//   date: string;
//   actual: number;
//   forecast: number;
//   channel?: string;
// }

// // ============ Tables ============

export interface RawMaterialRiskRow {
  id: string;
  rawMaterial: string;
  forecastDemand: number;
  actualConsumption: number;
  closingInventory: number;
  safetyStock: number;
  riskStatus: "Overstock" | "Stockout" | "Balanced";
  stockoutRiskDate?: string | null;  // Date when stockout is expected (YYYY-MM-DD format)
}

// export interface SKUPerformance {
//   id: number;
//   sku: string;
//   name: string;
//   category: string;
//   avgDailySales: number;
//   accuracy: number;
//   demandVolatility: number;
//   riskFlag: "low" | "medium" | "high";
// }

// // ============ Flow ============

// export interface DemandFlowFunnelData {
//   steps: {
//     skuForecast: { label: string; value: number; unit: string };
//     productMix: { label: string; value: number; unit: string };
//     productForecast: { label: string; value: number; unit: string };
//     rawMaterialDemand: { label: string; value: number; unit: string };
//   };
// }

// // ============ Heatmaps ============

// export interface ConsumptionHeatmapCell {
//   date: string;
//   rawMaterial: string;
//   forecastErrorPct: number;
// }

// export interface SKUContributionHeatmapCell {
//   sku: string;
//   date: string;
//   contributionPct: number;
// }

// // ============ Rolling & Histogram ============

// export interface RollingErrorPoint {
//   date: string;
//   mape: number;
//   bias?: number;
// }

// export type RollingWindow = "7" | "14" | "30";

// export interface ForecastDeviationBucket {
//   bucket: "under" | "accurate" | "over";
//   count: number;
// }

// // ============ Legacy / shared ============

// export interface ForecastComparisonPoint {
//   date: string;
//   actual: number;
//   forecast: number;
//   confidenceLow: number;
//   confidenceHigh: number;
// }

// export interface RiskAlert {
//   id: number;
//   sku: string;
//   name: string;
//   category: string;
//   severity: "high" | "critical";
//   issue: string;
//   recommendation: string;
//   daysUntilStockout?: number;
// }

// export interface TopDemandDriver {
//   sku: string;
//   name: string;
//   contributionPct: number;
//   trendDirection: "up" | "down" | "flat";
// }

// // ============ Fetch helpers ============

// export async function fetchConsumptionKPIs(filters: FilterState): Promise<KPIData> {
//   const params = filtersToParams(filters);
//   return apiRequest<KPIData>(`/consumption/kpis?${params}`);
// }

// export async function fetchSalesKPIs(filters: FilterState): Promise<SalesKPIData> {
//   const params = filtersToParams(filters);
//   return apiRequest<SalesKPIData>(`/sales/kpis?${params}`);
// }

// // ============ Combined Dashboard Payloads ============

// export interface ConsumptionDashboardData {
//   kpis: KPIData;
//   rawMaterialDemandTrend: RawMaterialDemandTrendPoint[];
//   rawMaterialRiskTable: RawMaterialRiskRow[];
//   demandFlowFunnel: DemandFlowFunnelData;
//   forecastComparison: ForecastComparisonPoint[];
//   consumptionErrorHeatmap: ConsumptionHeatmapCell[];
// }

// export interface SalesDashboardData {
//   kpis: SalesKPIData;
//   skuSalesTrend: SKUSalesTrendPoint[];
//   skuPerformance: SKUPerformance[];
//   riskAlerts: RiskAlert[];
//   skuContributionHeatmap: SKUContributionHeatmapCell[];
//   topDemandDrivers: TopDemandDriver[];
//   rollingError: RollingErrorPoint[];
//   forecastDeviationHistogram: ForecastDeviationBucket[];
// }

// export async function fetchConsumptionDashboardData(
//   filters: FilterState
// ): Promise<ConsumptionDashboardData> {
//   const params = filtersToParams(filters);
//   return apiRequest<ConsumptionDashboardData>(`/consumption/dashboard?${params}`, {}, CONSUMPTION_API_URL);
// }

// export async function fetchSalesDashboardData(
//   filters: FilterState
// ): Promise<SalesDashboardData> {
//   const params = filtersToParams(filters);
//   return apiRequest<SalesDashboardData>(`/sales/dashboard?${params}`, {}, SALES_API_URL);
// }





































/**
 * API Service Layer
 * Updated to support aggregated Dashboard Endpoints
 */

import { FilterState } from "@/contexts/FilterContext";

// FORCE Localhost for Development
const API_BASE_URL = "https://woodland-final-lxcg.onrender.com";

const CONSUMPTION_API_URL = API_BASE_URL;
const SALES_API_URL = API_BASE_URL;

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  baseUrl?: string
): Promise<T> {
  const base = baseUrl || CONSUMPTION_API_URL;
  // Handle slash logic safely
  const url = `${base}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
  
  const config: RequestInit = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };
  
  const response = await fetch(url, config);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `API Error: ${response.status}`);
  }
  return response.json();
}

// function filtersToParams(filters: FilterState): URLSearchParams {



function filtersToParams(filters: FilterState): URLSearchParams {
  const params = new URLSearchParams();

  if (filters.dateRange) params.append("dateRange", filters.dateRange);

  if (filters.channel !== "all") params.append("channel", filters.channel);
  if (filters.store !== "all") params.append("store", filters.store);
  if (filters.sku !== "all") params.append("sku", filters.sku);
  if (filters.product !== "all") params.append("product", filters.product);
  if (filters.rawMaterial !== "all") params.append("rawMaterial", filters.rawMaterial);
  if (filters.category !== "all") params.append("category", filters.category);

  params.append("aggregation", filters.aggregation);
  params.append("view", filters.view);
  
  if (filters.rollingWindow) params.append("rollingWindow", filters.rollingWindow);

  return params;
}



// ============ Type Definitions ============

type KpiMetric = { value: number; trend: number; direction: "up" | "down" | "neutral" };

export interface KPIData {
  totalForecastedRMDemand: KpiMetric;
  trailing30DConsumption?: KpiMetric;  // Historical baseline
  actualRMConsumption?: KpiMetric;     // Legacy: kept for backwards compatibility
  consumptionForecastAccuracy: KpiMetric;
  projectedOverstock?: KpiMetric;      // New: Overstock above safety
  daysToStockout?: KpiMetric;          // New: Days until first stockout
  inventoryExcessUnits?: KpiMetric;    // Legacy
  inventoryShortfallUnits: KpiMetric;
}

export interface SalesKPIData {
  skuForecastAccuracy: KpiMetric;
  totalForecastedUnits: KpiMetric;
  baselineSales: KpiMetric;
  demandVolatilityIndex: KpiMetric;
  highRiskSKUsCount: KpiMetric;
}

// ============ Dashboard Data Structures ============

export interface ConsumptionDashboardData {
  kpis: KPIData;
  rawMaterialDemandTrend: any[];
  rawMaterialRiskTable: RawMaterialRiskRow[];
  demandFlowFunnel: any;
  forecastComparison: any[];
  consumptionErrorHeatmap: any[];
  forecastCutoffDate?: string;  // Date string marking end of historical data
  forecastHorizon?: string;     // "7day" or "30day"
  historicalDays?: number;      // Number of historical days shown
}

export interface SalesDashboardData {
  kpis: SalesKPIData;
  skuSalesTrend: any[];
  skuPerformance: any[];
  riskAlerts: any[];
  skuContributionHeatmap: any[];
  topDemandDrivers: any[];
  rollingError: any[];
  forecastDeviationHistogram: any[];
  forecastCutoffDate?: string;  // Date string marking end of historical data
  forecastHorizon?: string;     // "7day" or "30day"
  historicalDays?: number;      // Number of historical days shown
}

// ============ API Functions (The Missing Parts) ============

export async function fetchConsumptionDashboardData(
  filters: FilterState
): Promise<ConsumptionDashboardData> {
  const params = filtersToParams(filters);
  const paramString = params.toString();
  console.log("[API] ===== FETCHING CONSUMPTION DASHBOARD =====");
  console.log("[API] Filters object:", {
    product: filters.product,
    rawMaterial: filters.rawMaterial,
    dateRange: filters.dateRange,
  });
  console.log("[API] URL params string:", paramString);
  console.log("[API] Product param in URL:", params.get("product") || "NOT PRESENT");
  // This calls the aggregated endpoint we created in Python
  const url = `/consumption/dashboard?${paramString}`;
  console.log("[API] Full URL:", url);
  return apiRequest<ConsumptionDashboardData>(url);
}

export async function fetchSalesDashboardData(
  filters: FilterState
): Promise<SalesDashboardData> {
  const params = filtersToParams(filters);
  // This calls the aggregated endpoint we created in Python
  return apiRequest<SalesDashboardData>(`/sales/dashboard?${params}`);
}

// Keep these for backward compatibility if needed, though dashboards use the above now
export async function fetchConsumptionKPIs(filters: FilterState): Promise<KPIData> {
  const params = filtersToParams(filters);
  return apiRequest<KPIData>(`/consumption/kpis?${params}`);
}

export async function fetchSalesKPIs(filters: FilterState): Promise<SalesKPIData> {
  const params = filtersToParams(filters);
  return apiRequest<SalesKPIData>(`/sales/kpis?${params}`);
}



export interface FilterMetadata {
  channels: string[];
  stores: string[];
  skus: string[];
  products: string[];
  categories: string[];
  rawMaterials: string[];
}

export async function fetchFilterMetadata(): Promise<FilterMetadata> {
  return apiRequest<FilterMetadata>("/filters");
}

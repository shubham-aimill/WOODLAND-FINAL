/**
 * Mock Data Service
 *
 * Provides realistic mock data while API is not connected.
 * Wireframe-aligned shapes; see src/services/api.ts.
 */

import { FilterState } from "@/contexts/FilterContext";
import type {
  KPIData,
  SalesKPIData,
  RawMaterialDemandTrendPoint,
  RawMaterialRiskRow,
  DemandFlowFunnelData,
  ConsumptionHeatmapCell,
  SKUSalesTrendPoint,
  SKUContributionHeatmapCell,
  TopDemandDriver,
  RollingErrorPoint,
  ForecastDeviationBucket,
  ForecastComparisonPoint,
  SKUPerformance,
  RiskAlert,
} from "./api";
import type { RollingWindow } from "@/contexts/FilterContext";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const applyFilterVariance = (baseValue: number, filters: FilterState): number => {
  let multiplier = 1;
  if (filters.channel === "retail") multiplier *= 1.2;
  if (filters.channel === "wholesale") multiplier *= 0.9;
  if (filters.dateRange === "last-7") multiplier *= 0.85;
  if (filters.dateRange === "last-90") multiplier *= 1.15;
  return Math.round(baseValue * multiplier * (0.95 + Math.random() * 0.1));
};

// ============ Consumption KPIs ============

export async function mockConsumptionKPIs(filters: FilterState): Promise<KPIData> {
  await delay(400);
  const v = (x: number) => applyFilterVariance(x, filters);
  return {
    totalForecastedRMDemand: { value: v(28500), trend: 6.2, direction: "up" },
    actualRMConsumption: { value: v(24680), trend: 5.1, direction: "up" },
    consumptionForecastAccuracy: { value: 94.2, trend: 2.3, direction: "up" },
    inventoryExcessUnits: { value: v(1240), trend: 1.8, direction: "down" },
    inventoryShortfallUnits: { value: v(320), trend: 5.2, direction: "down" },
  };
}

// ============ Sales KPIs ============

export async function mockSalesKPIs(filters: FilterState): Promise<SalesKPIData> {
  await delay(400);
  const v = (x: number) => applyFilterVariance(x, filters);
  return {
    skuForecastAccuracy: { value: 91.8, trend: 1.4, direction: "up" },
    totalForecastedUnits: { value: v(18420), trend: 12.3, direction: "up" },
    baselineSales: { value: v(17250), trend: 8.5, direction: "up" },
    demandVolatilityIndex: { value: 14.2, trend: 3.1, direction: "down" },
    highRiskSKUsCount: { value: filters.store === "all" ? 4 : 1, trend: 2, direction: "down" },
  };
}

// ============ Raw Material Demand Trend ============

export async function mockRawMaterialDemandTrend(
  filters: FilterState
): Promise<RawMaterialDemandTrendPoint[]> {
  await delay(450);
  const weeks = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"];
  let data = weeks.map((w, i) => ({
    date: w,
    forecast: 2800 + i * 120 + Math.random() * 200,
    actual: i < 6 ? 2700 + i * 100 + Math.random() * 250 : 0,
  }));
  if (filters.dateRange === "last-7") data = data.slice(-2);
  if (filters.dateRange === "last-30") data = data.slice(-4);
  return data.map((d) => ({
    ...d,
    forecast: Math.round(applyFilterVariance(d.forecast, filters)),
    actual: d.actual ? Math.round(applyFilterVariance(d.actual, filters)) : 0,
  }));
}

// ============ Raw Material Risk Table ============

const RAW_MATERIALS = [
  "Full-Grain Leather",
  "Suede",
  "Nubuck",
  "Leather Lining",
  "Hardware Kit",
];

export async function mockRawMaterialRiskTable(
  filters: FilterState
): Promise<RawMaterialRiskRow[]> {
  await delay(400);
  const rows: RawMaterialRiskRow[] = RAW_MATERIALS.map((rm, i) => {
    const fd = 3200 + i * 800 + Math.random() * 400;
    const ac = fd * (0.92 + Math.random() * 0.12);
    const closing = 800 + i * 200 + Math.random() * 300;
    const safety = 600 + i * 150;
    let riskStatus: "Overstock" | "Stockout" | "Balanced" = "Balanced";
    if (closing > safety * 1.3) riskStatus = "Overstock";
    else if (closing < safety * 0.7) riskStatus = "Stockout";
    return {
      id: `rm-${i + 1}`,
      rawMaterial: rm,
      forecastDemand: Math.round(applyFilterVariance(fd, filters)),
      actualConsumption: Math.round(applyFilterVariance(ac, filters)),
      closingInventory: Math.round(closing),
      safetyStock: Math.round(safety),
      riskStatus,
    };
  });
  if (filters.rawMaterial !== "all") {
    const idx = parseInt(filters.rawMaterial.split("-")[1]) - 1;
    return rows.filter((_, i) => i === idx);
  }
  return rows;
}

// ============ Demand Flow Funnel ============

export async function mockDemandFlowFunnel(
  filters: FilterState
): Promise<DemandFlowFunnelData> {
  await delay(350);
  const v = (x: number) => Math.round(applyFilterVariance(x, filters));
  return {
    steps: {
      skuForecast: { label: "SKU Forecast Units", value: v(12500), unit: "units" },
      productMix: { label: "Product Mix Allocation", value: v(11800), unit: "units" },
      productForecast: { label: "Product Forecast Units", value: v(11800), unit: "units" },
      rawMaterialDemand: { label: "Raw Material Demand", value: v(10200), unit: "sqm" },
    },
  };
}

// ============ Consumption Error Heatmap ============

export async function mockConsumptionErrorHeatmap(
  filters: FilterState
): Promise<ConsumptionHeatmapCell[]> {
  await delay(400);
  const dates = ["W1", "W2", "W3", "W4", "W5", "W6"];
  const materials = RAW_MATERIALS;
  return materials.flatMap((rawMaterial) =>
    dates.map((date) => ({
      date,
      rawMaterial,
      forecastErrorPct: -15 + Math.random() * 30,
    }))
  );
}

// ============ SKU Sales Trend (time series by channel) ============

const CHANNELS = ["retail", "wholesale", "ecommerce", "direct"] as const;

export async function mockSKUSalesTrend(
  filters: FilterState
): Promise<SKUSalesTrendPoint[]> {
  await delay(450);
  const points: SKUSalesTrendPoint[] = [];
  const weeks = ["W1", "W2", "W3", "W4", "W5", "W6"];
  for (const w of weeks) {
    for (const ch of CHANNELS) {
      if (filters.channel !== "all" && filters.channel !== ch) continue;
      const base = ch === "retail" ? 1200 : ch === "wholesale" ? 900 : ch === "ecommerce" ? 600 : 400;
      points.push({
        date: w,
        actual: Math.round(applyFilterVariance(base * (0.9 + Math.random() * 0.2), filters)),
        forecast: Math.round(applyFilterVariance(base * (0.92 + Math.random() * 0.18), filters)),
        channel: ch,
      });
    }
  }
  return points;
}

// ============ SKU Contribution Heatmap ============

const SKUS = ["WL-BOOT-001", "WL-JACK-002", "WL-BAG-003", "WL-BELT-004", "WL-WALL-005", "WL-SHOE-006"];

export async function mockSKUContributionHeatmap(
  filters: FilterState
): Promise<SKUContributionHeatmapCell[]> {
  await delay(400);
  const dates = ["W1", "W2", "W3", "W4", "W5", "W6"];
  return SKUS.flatMap((sku) =>
    dates.map((date) => ({
      sku,
      date,
      contributionPct: 5 + Math.random() * 25,
    }))
  );
}

// ============ Top Demand Drivers ============

const SKU_NAMES: Record<string, string> = {
  "WL-BOOT-001": "Heritage Boot",
  "WL-JACK-002": "Rancher Jacket",
  "WL-BAG-003": "Trail Backpack",
  "WL-BELT-004": "Classic Belt",
  "WL-WALL-005": "Leather Wallet",
  "WL-SHOE-006": "Oxford Shoe",
};

export async function mockTopDemandDrivers(
  filters: FilterState
): Promise<TopDemandDriver[]> {
  await delay(350);
  return SKUS.slice(0, 10).map((sku, i) => ({
    sku,
    name: SKU_NAMES[sku] ?? sku,
    contributionPct: 22 - i * 2 + Math.random() * 3,
    trendDirection: (["up", "down", "flat"] as const)[i % 3],
  }));
}

// ============ Rolling Error (7 / 14 / 30-day windows) ============

export async function mockRollingError(
  filters: FilterState,
  window?: RollingWindow
): Promise<RollingErrorPoint[]> {
  await delay(400);
  const w = window ?? filters.rollingWindow ?? "14";
  const len = w === "7" ? 7 : w === "14" ? 10 : 12;
  const dates = Array.from({ length: len }, (_, i) => `W${i + 1}`);
  return dates.map((date) => ({
    date,
    mape: 5 + Math.random() * 10,
    bias: -3 + Math.random() * 6,
  }));
}

// ============ Forecast Deviation Histogram ============

export async function mockForecastDeviationHistogram(
  filters: FilterState
): Promise<ForecastDeviationBucket[]> {
  await delay(350);
  return [
    { bucket: "under", count: Math.round(applyFilterVariance(120, filters)) },
    { bucket: "accurate", count: Math.round(applyFilterVariance(340, filters)) },
    { bucket: "over", count: Math.round(applyFilterVariance(85, filters)) },
  ];
}

// ============ Forecast Comparison (consumption) ============

export async function mockForecastComparison(
  filters: FilterState
): Promise<ForecastComparisonPoint[]> {
  await delay(500);
  const weeks = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"];
  let data = weeks.map((date, i) => {
    const actual = 2000 + i * 400 + Math.random() * 500;
    const forecast = actual * (0.92 + Math.random() * 0.16);
    return {
      date,
      actual: Math.round(actual),
      forecast: Math.round(forecast),
      confidenceLow: Math.round(forecast * 0.85),
      confidenceHigh: Math.round(forecast * 1.15),
    };
  });
  if (filters.dateRange === "last-7") data = data.slice(-2);
  if (filters.dateRange === "last-30") data = data.slice(-4);
  if (filters.dateRange === "last-90") data = data.slice(-6);
  return data.map((d) => {
    const actual = Math.round(applyFilterVariance(d.actual, filters));
    const forecast = Math.round(applyFilterVariance(d.forecast, filters));
    return {
      date: d.date,
      actual,
      forecast,
      confidenceLow: Math.round(forecast * 0.85),
      confidenceHigh: Math.round(forecast * 1.15),
    };
  });
}

// ============ SKU Performance (extended) ============

export async function mockSKUPerformance(
  filters: FilterState
): Promise<SKUPerformance[]> {
  await delay(450);
  const skus: SKUPerformance[] = [
    { id: 1, sku: "WL-BOOT-001", name: "Heritage Boot", category: "Footwear", avgDailySales: 140, accuracy: 95.2, demandVolatility: 12, riskFlag: "low" },
    { id: 2, sku: "WL-JACK-002", name: "Rancher Jacket", category: "Apparel", avgDailySales: 127, accuracy: 90.5, demandVolatility: 18, riskFlag: "medium" },
    { id: 3, sku: "WL-BAG-003", name: "Trail Backpack", category: "Bags", avgDailySales: 107, accuracy: 93.3, demandVolatility: 14, riskFlag: "low" },
    { id: 4, sku: "WL-BELT-004", name: "Classic Belt", category: "Accessories", avgDailySales: 93, accuracy: 96.6, demandVolatility: 10, riskFlag: "low" },
    { id: 5, sku: "WL-WALL-005", name: "Leather Wallet", category: "Accessories", avgDailySales: 80, accuracy: 90.9, demandVolatility: 16, riskFlag: "medium" },
    { id: 6, sku: "WL-SHOE-006", name: "Oxford Shoe", category: "Footwear", avgDailySales: 70, accuracy: 91.3, demandVolatility: 22, riskFlag: "high" },
  ];
  if (filters.sku !== "all") {
    const map: Record<string, string> = { "sku-1": "WL-BOOT-001", "sku-2": "WL-JACK-002", "sku-3": "WL-BAG-003", "sku-4": "WL-BELT-004" };
    const skuId = map[filters.sku] ?? filters.sku;
    return skus.filter((s) => s.sku === skuId);
  }
  return skus;
}

// ============ Risk Alerts ============

export async function mockRiskAlerts(filters: FilterState): Promise<RiskAlert[]> {
  await delay(350);
  return [
    { id: 1, sku: "WL-BOOT-001", name: "Heritage Boot", category: "Footwear", severity: "critical", issue: "Stock depleting faster than forecast", recommendation: "Increase next order by 25%", daysUntilStockout: 8 },
    { id: 2, sku: "WL-JACK-002", name: "Rancher Jacket", category: "Apparel", severity: "high", issue: "Seasonal demand spike predicted", recommendation: "Review inventory levels", daysUntilStockout: 15 },
    { id: 3, sku: "WL-SHOE-006", name: "Oxford Shoe", category: "Footwear", severity: "high", issue: "Low inventory cover", recommendation: "Expedite pending orders", daysUntilStockout: 12 },
  ];
}

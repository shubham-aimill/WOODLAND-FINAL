// /**
//  * Dashboard Data Hooks
//  *
//  * React Query hooks for fetching dashboard data.
//  * Wireframe-aligned; uses combined API endpoints with mock fallback.
//  */

// import { useQuery } from "@tanstack/react-query";
// import { useLocation } from "react-router-dom";
// import { useFilters } from "@/contexts/FilterContext";
// import {
//   fetchConsumptionDashboardData,
//   fetchSalesDashboardData,
// } from "@/services/api";
// import {
//   mockConsumptionKPIs,
//   mockSalesKPIs,
//   mockRawMaterialDemandTrend,
//   mockRawMaterialRiskTable,
//   mockDemandFlowFunnel,
//   mockConsumptionErrorHeatmap,
//   mockForecastComparison,
//   mockSKUSalesTrend,
//   mockSKUPerformance,
//   mockRiskAlerts,
//   mockSKUContributionHeatmap,
//   mockTopDemandDrivers,
//   mockRollingError,
//   mockForecastDeviationHistogram,
// } from "@/services/mockData";

// // ============ Consumption Dashboard ============

// function useConsumptionDashboard(enabled = true) {
//   const { filters, lastRefresh } = useFilters();

//   return useQuery({
//     queryKey: ["consumption-dashboard", filters, lastRefresh],
//     queryFn: async () => {
//       try {
//         const url = import.meta.env.VITE_CONSUMPTION_API_URL || import.meta.env.VITE_API_BASE_URL;
//         const useApi = url && url !== "/api" && url !== "";
//         if (useApi) {
//           try {
//             return await fetchConsumptionDashboardData(filters);
//           } catch (e) {
//             console.warn("Consumption API failed, using mock:", e);
//           }
//         }
//       } catch (e) {
//         console.warn("Consumption fetch error, using mock:", e);
//       }
//       return {
//         kpis: await mockConsumptionKPIs(filters),
//         rawMaterialDemandTrend: await mockRawMaterialDemandTrend(filters),
//         rawMaterialRiskTable: await mockRawMaterialRiskTable(filters),
//         demandFlowFunnel: await mockDemandFlowFunnel(filters),
//         forecastComparison: await mockForecastComparison(filters),
//         consumptionErrorHeatmap: await mockConsumptionErrorHeatmap(filters),
//       };
//     },
//     enabled,
//     staleTime: 30000,
//     refetchInterval: 60000,
//     retry: false,
//   });
// }

// export function useConsumptionKPIs() {
//   const { data, ...rest } = useConsumptionDashboard();
//   return { data: data?.kpis, ...rest };
// }

// export function useRawMaterialDemandTrend() {
//   const { data, ...rest } = useConsumptionDashboard();
//   return { data: data?.rawMaterialDemandTrend, ...rest };
// }

// export function useRawMaterialRiskTable() {
//   const { data, ...rest } = useConsumptionDashboard();
//   return { data: data?.rawMaterialRiskTable, ...rest };
// }

// export function useDemandFlowFunnel() {
//   const { data, ...rest } = useConsumptionDashboard();
//   return { data: data?.demandFlowFunnel, ...rest };
// }

// export function useForecastComparison() {
//   const location = useLocation();
//   const consumption = useConsumptionDashboard(location.pathname !== "/sales");
//   return {
//     data: consumption.data?.forecastComparison,
//     isLoading: consumption.isLoading,
//     error: consumption.error,
//     refetch: consumption.refetch,
//   };
// }

// export function useConsumptionErrorHeatmap() {
//   const { data, ...rest } = useConsumptionDashboard();
//   return { data: data?.consumptionErrorHeatmap, ...rest };
// }

// // ============ Sales Dashboard ============

// function useSalesDashboard(enabled = true) {
//   const { filters, lastRefresh } = useFilters();

//   return useQuery({
//     queryKey: ["sales-dashboard", filters, lastRefresh],
//     queryFn: async () => {
//       try {
//         const url = import.meta.env.VITE_SALES_API_URL || import.meta.env.VITE_API_BASE_URL;
//         const useApi = url && url !== "/api" && url !== "";
//         if (useApi) {
//           try {
//             return await fetchSalesDashboardData(filters);
//           } catch (e) {
//             console.warn("Sales API failed, using mock:", e);
//           }
//         }
//       } catch (e) {
//         console.warn("Sales fetch error, using mock:", e);
//       }
//       return {
//         kpis: await mockSalesKPIs(filters),
//         skuSalesTrend: await mockSKUSalesTrend(filters),
//         skuPerformance: await mockSKUPerformance(filters),
//         riskAlerts: await mockRiskAlerts(filters),
//         skuContributionHeatmap: await mockSKUContributionHeatmap(filters),
//         topDemandDrivers: await mockTopDemandDrivers(filters),
//         rollingError: await mockRollingError(filters),
//         forecastDeviationHistogram: await mockForecastDeviationHistogram(filters),
//       };
//     },
//     enabled,
//     staleTime: 30000,
//     refetchInterval: 60000,
//     retry: false,
//   });
// }

// export function useSalesKPIs() {
//   const { data, ...rest } = useSalesDashboard();
//   return { data: data?.kpis, ...rest };
// }

// export function useSKUSalesTrend() {
//   const { data, ...rest } = useSalesDashboard();
//   return { data: data?.skuSalesTrend, ...rest };
// }

// export function useSKUPerformance() {
//   const { data, ...rest } = useSalesDashboard();
//   return { data: data?.skuPerformance, ...rest };
// }

// export function useRiskAlerts() {
//   const { data, ...rest } = useSalesDashboard();
//   return { data: data?.riskAlerts, ...rest };
// }

// export function useSKUContributionHeatmap() {
//   const { data, ...rest } = useSalesDashboard();
//   return { data: data?.skuContributionHeatmap, ...rest };
// }

// export function useTopDemandDrivers() {
//   const { data, ...rest } = useSalesDashboard();
//   return { data: data?.topDemandDrivers, ...rest };
// }

// export function useRollingError() {
//   const { data, ...rest } = useSalesDashboard();
//   return { data: data?.rollingError, ...rest };
// }

// export function useForecastDeviationHistogram() {
//   const { data, ...rest } = useSalesDashboard();
//   return { data: data?.forecastDeviationHistogram, ...rest };
// }































/**
 * Dashboard Data Hooks
 * * DIRECT INTEGRATION MODE
 * Fetches real data from Python Backend via api.ts.
 * Mock data has been completely removed.
 */

import { useQuery } from "@tanstack/react-query";
import { useLocation } from "react-router-dom";
import { useEffect, useMemo, useRef } from "react";
import { useFilters } from "@/contexts/FilterContext";
import {
  fetchConsumptionDashboardData,
  fetchSalesDashboardData,
  ConsumptionDashboardData,
  SalesDashboardData
} from "@/services/api";

// --- FALLBACK CONSTANTS (To prevent UI crash if Backend is offline) ---

const emptyConsumptionData: ConsumptionDashboardData = {
  kpis: {
    totalForecastedRMDemand: { value: 0, trend: 0, direction: "neutral" },
    actualRMConsumption: { value: 0, trend: 0, direction: "neutral" },
    consumptionForecastAccuracy: { value: 0, trend: 0, direction: "neutral" },
    inventoryExcessUnits: { value: 0, trend: 0, direction: "neutral" },
    inventoryShortfallUnits: { value: 0, trend: 0, direction: "neutral" },
  },
  rawMaterialDemandTrend: [],
  rawMaterialRiskTable: [],
  demandFlowFunnel: {
    steps: {
      skuForecast: { label: "SKU Forecast", value: 0, unit: "Units" },
      productMix: { label: "Product Mix", value: 0, unit: "Units" },
      productForecast: { label: "Product Demand", value: 0, unit: "Units" },
      rawMaterialDemand: { label: "Material Demand", value: 0, unit: "Units" }
    }
  },
  forecastComparison: [],
  consumptionErrorHeatmap: [],
  forecastCutoffDate: "2025-12-30",
  forecastHorizon: "30day"
};

const emptySalesData: SalesDashboardData = {
    kpis: {
        skuForecastAccuracy: { value: 0, trend: 0, direction: "neutral" },
        totalForecastedUnits: { value: 0, trend: 0, direction: "neutral" },
        forecastBias: { value: 0, trend: 0, direction: "neutral" },
        demandVolatilityIndex: { value: 0, trend: 0, direction: "neutral" },
        highRiskSKUsCount: { value: 0, trend: 0, direction: "neutral" }
    },
    skuSalesTrend: [],
    skuPerformance: [],
    riskAlerts: [],
    skuContributionHeatmap: [],
    topDemandDrivers: [],
    rollingError: [],
    forecastDeviationHistogram: [],
    forecastCutoffDate: "2025-12-30",
    forecastHorizon: "30day"
};

// ============ Consumption Dashboard ============

function useConsumptionDashboard(enabled = true) {
  const { filters, lastRefresh } = useFilters();

  // Serialize filters to ensure React Query detects changes
  // Use useMemo to prevent recalculation on every render
  const queryKey = useMemo(() => {
    const filterKey = [
      filters.dateRange || "next-30",
      filters.product || "all",      // Product filter - default to "all"
      filters.rawMaterial || "all",   // Raw material filter - default to "all"
      filters.channel || "all",
      filters.store || "all",
      filters.sku || "all",
      filters.category || "all",
      filters.aggregation || "daily",
      filters.view || "daily",
      lastRefresh?.getTime() || Date.now(),
    ].join("|");
    
    return ["consumption-dashboard", filterKey];
  }, [
    filters.dateRange,
    filters.product,
    filters.rawMaterial,
    filters.channel,
    filters.store,
    filters.sku,
    filters.category,
    filters.aggregation,
    filters.view,
    lastRefresh?.getTime(),
  ]);

  // Track query key changes to prevent infinite loops
  const queryKeyString = useMemo(() => JSON.stringify(queryKey), [queryKey]);
  const prevQueryKeyRef = useRef<string>("");
  useEffect(() => {
    if (prevQueryKeyRef.current !== queryKeyString) {
      prevQueryKeyRef.current = queryKeyString;
    }
  }, [queryKeyString]);

  const query = useQuery({
    queryKey,
    queryFn: async () => {
      try {
        // DIRECT CALL TO API - No Mock Fallback
        const data = await fetchConsumptionDashboardData(filters);
        return data;
      } catch (e) {
        console.error("CRITICAL: Failed to fetch Consumption Data. Is api_server.py running?", e);
        // Return empty structure so UI shows 0s instead of crashing
        return emptyConsumptionData; 
      }
    },
    enabled,
    staleTime: 0, // Always refetch when filters change
    gcTime: 0, // Don't cache - always fetch fresh data
    refetchInterval: false, // Disable auto-refetch, rely on filter changes
    retry: 1,
    // Force refetch on mount and when query key changes
    refetchOnMount: "always",
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
  });


  return query;
}

// --- Selectors (These extract specific parts of the data for components) ---

export function useConsumptionKPIs() {
  const { data, ...rest } = useConsumptionDashboard();
  const kpis = data?.kpis || emptyConsumptionData.kpis;
  
  
  return { data: kpis, ...rest };
}

export function useRawMaterialDemandTrend(localAggregation?: "daily" | "weekly") {
  const { filters, lastRefresh } = useFilters();
  
  // Use local aggregation if provided, otherwise use global filter
  const aggregation = localAggregation || filters.aggregation || "daily";
  
  // Create a modified filters object with the local aggregation
  const modifiedFilters = { ...filters, aggregation };
  
  // Serialize filters for query key
  const queryKey = useMemo(() => {
    const filterKey = [
      modifiedFilters.dateRange || "next-30",
      modifiedFilters.product || "all",
      modifiedFilters.rawMaterial || "all",
      modifiedFilters.channel || "all",
      modifiedFilters.store || "all",
      modifiedFilters.sku || "all",
      modifiedFilters.category || "all",
      aggregation, // Use the aggregation parameter
      modifiedFilters.view || "daily",
      lastRefresh?.getTime() || Date.now(),
    ].join("|");
    
    return ["consumption-dashboard", filterKey];
  }, [
    modifiedFilters.dateRange,
    modifiedFilters.product,
    modifiedFilters.rawMaterial,
    modifiedFilters.channel,
    modifiedFilters.store,
    modifiedFilters.sku,
    modifiedFilters.category,
    aggregation,
    modifiedFilters.view,
    lastRefresh?.getTime(),
  ]);

  const query = useQuery({
    queryKey,
    queryFn: async () => {
      try {
        const data = await fetchConsumptionDashboardData(modifiedFilters);
        return data;
      } catch (e) {
        console.error("Failed to fetch Consumption Data", e);
        return emptyConsumptionData;
      }
    },
    enabled: true,
    staleTime: 0,
    gcTime: 0,
    refetchInterval: false,
    retry: 1,
    refetchOnMount: "always",
  });

  return { 
    data: query.data?.rawMaterialDemandTrend || [], 
    forecastCutoffDate: query.data?.forecastCutoffDate,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  };
}

export function useRawMaterialRiskTable() {
  const { data, ...rest } = useConsumptionDashboard();
  return { data: data?.rawMaterialRiskTable || [], ...rest };
}

export function useDemandFlowFunnel() {
  const { data, ...rest } = useConsumptionDashboard();
  return { data: data?.demandFlowFunnel || emptyConsumptionData.demandFlowFunnel, ...rest };
}

export function useForecastComparison() {
  const location = useLocation();
  const consumption = useConsumptionDashboard(location.pathname !== "/sales");
  return {
    data: consumption.data?.forecastComparison || [],
    forecastCutoffDate: consumption.data?.forecastCutoffDate,
    isLoading: consumption.isLoading,
    error: consumption.error,
    refetch: consumption.refetch,
  };
}

export function useConsumptionErrorHeatmap() {
  const { data, ...rest } = useConsumptionDashboard();
  return { data: data?.consumptionErrorHeatmap || [], ...rest };
}

// ============ Sales Dashboard ============

function useSalesDashboard(enabled = true) {
  const { filters, lastRefresh } = useFilters();

  // Serialize filters to ensure React Query detects changes
  const queryKey = [
    "sales-dashboard",
    filters.dateRange,
    filters.channel,
    filters.store,
    filters.sku,
    filters.product,
    filters.category,
    filters.aggregation,
    filters.view,
    filters.rollingWindow,
    lastRefresh?.getTime(),
  ];

  return useQuery({
    queryKey,
    queryFn: async () => {
      try {
        console.log("[useSalesDashboard] Fetching with filters:", {
          product: filters.product,
          dateRange: filters.dateRange,
        });
        // DIRECT CALL TO API
        const data = await fetchSalesDashboardData(filters);
        return data;
      } catch (e) {
        console.error("CRITICAL: Failed to fetch Sales Data. Is api_server.py running?", e);
        return emptySalesData;
      }
    },
    enabled,
    staleTime: 0, // Always refetch when filters change
    refetchInterval: false, // Disable auto-refetch, rely on filter changes
    retry: 1,
  });
}

// --- Sales Selectors ---

export function useSalesKPIs() {
  const { data, ...rest } = useSalesDashboard();
  return { data: data?.kpis || emptySalesData.kpis, ...rest };
}

export function useSKUSalesTrend() {
  const { data, ...rest } = useSalesDashboard();
  return { 
    data: data?.skuSalesTrend || [], 
    forecastCutoffDate: data?.forecastCutoffDate,
    ...rest 
  };
}

export function useSKUPerformance() {
  const { data, ...rest } = useSalesDashboard();
  return { data: data?.skuPerformance || [], ...rest };
}

export function useRiskAlerts() {
  const { data, ...rest } = useSalesDashboard();
  return { data: data?.riskAlerts || [], ...rest };
}

export function useSKUContributionHeatmap() {
  const { data, ...rest } = useSalesDashboard();
  return { data: data?.skuContributionHeatmap || [], ...rest };
}

export function useTopDemandDrivers() {
  const { data, ...rest } = useSalesDashboard();
  return { data: data?.topDemandDrivers || [], ...rest };
}

export function useRollingError() {
  const { data, ...rest } = useSalesDashboard();
  return { data: data?.rollingError || [], ...rest };
}

export function useForecastDeviationHistogram() {
  const { data, ...rest } = useSalesDashboard();
  return { data: data?.forecastDeviationHistogram || [], ...rest };
}
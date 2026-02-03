import { Package, Activity, AlertTriangle, TrendingDown, BarChart3 } from "lucide-react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { KPICard } from "@/components/dashboard/KPICard";
import { RawMaterialDemandTrendChart } from "@/components/dashboard/RawMaterialDemandTrendChart";
import { RawMaterialRiskTable } from "@/components/dashboard/RawMaterialRiskTable";
import { DemandFlowFunnel } from "@/components/dashboard/DemandFlowFunnel";
import { ConsumptionErrorHeatmap } from "@/components/dashboard/ConsumptionErrorHeatmap";
import { useConsumptionKPIs } from "@/hooks/useDashboardData";
import { useFilters } from "@/contexts/FilterContext";

const ConsumptionDashboard = () => {
  const { data: kpis, isLoading } = useConsumptionKPIs();
  const { filters } = useFilters();
  
  
  // Dynamic labels based on filter selection (always show days for KPIs)
  const forecastDays = filters.dateRange === "next-7" ? 7 : 30;
  const historicalDays = forecastDays; // Match historical period to forecast period

  const trend = (k: { trend: number; direction: "up" | "down" | "neutral" } | undefined) =>
    k ? { value: k.trend, direction: k.direction } : undefined;

  return (
    <DashboardLayout dashboard="consumption">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        <KPICard
          key={`demand-${filters.product}-${filters.rawMaterial}-${kpis?.totalForecastedRMDemand?.value}`}
          title="Projected Demand"
          value={kpis?.totalForecastedRMDemand?.value?.toLocaleString() ?? "0"}
          unit="units"
          icon={<Package className="w-5 h-5" />}
          trend={trend(kpis?.totalForecastedRMDemand)}
          subtitle={`Next ${forecastDays} days forecast`}
          onClick={() => {}}
          isLoading={isLoading}
        />
        <KPICard
          key={`consumption-${filters.product}-${filters.rawMaterial}-${kpis?.trailing30DConsumption?.value}`}
          title="Baseline Consumption"
          value={kpis?.trailing30DConsumption?.value?.toLocaleString() ?? kpis?.actualRMConsumption?.value?.toLocaleString() ?? "0"}
          unit="units"
          icon={<Activity className="w-5 h-5" />}
          trend={trend(kpis?.trailing30DConsumption ?? kpis?.actualRMConsumption)}
          subtitle={`Last ${historicalDays} days actual`}
          onClick={() => {}}
          isLoading={isLoading}
        />
        <KPICard
          key={`accuracy-${filters.product}-${filters.rawMaterial}-${kpis?.consumptionForecastAccuracy?.value}`}
          title="Forecast Accuracy"
          value={kpis?.consumptionForecastAccuracy?.value?.toFixed(1) ?? "0"}
          unit="%"
          icon={<BarChart3 className="w-5 h-5" />}
          trend={trend(kpis?.consumptionForecastAccuracy)}
          status="success"
          subtitle={`Next ${forecastDays}d forecast vs last ${forecastDays}d consumption (100 − MAPE)`}
          onClick={() => {}}
          isLoading={isLoading}
        />
        <KPICard
          key={`overstock-${filters.product}-${filters.rawMaterial}-${kpis?.projectedOverstock?.value}`}
          title="Projected Overstock"
          value={kpis?.projectedOverstock?.value?.toLocaleString() ?? kpis?.inventoryExcessUnits?.value?.toLocaleString() ?? "0"}
          unit="units"
          icon={<AlertTriangle className="w-5 h-5" />}
          trend={trend(kpis?.projectedOverstock ?? kpis?.inventoryExcessUnits)}
          status="warning"
          subtitle={`Above safety after ${forecastDays}d`}
          onClick={() => {}}
          isLoading={isLoading}
        />
        <KPICard
          key={`stockout-${filters.product}-${filters.rawMaterial}-${kpis?.daysToStockout?.value ?? 999}`}
          title="Days to Stockout"
          value={kpis?.daysToStockout?.value != null ? kpis.daysToStockout.value.toLocaleString() : "999"}
          unit="days"
          icon={<TrendingDown className="w-5 h-5" />}
          trend={trend(kpis?.daysToStockout)}
          status={(kpis?.daysToStockout?.value ?? 999) < 14 ? "error" : "success"}
          subtitle="Until first material runs out"
          onClick={() => {}}
          isLoading={isLoading}
        />
      </div>

      {/* Demand Trend Analysis - Full Width */}
      <div className="mb-6">
        <RawMaterialDemandTrendChart />
      </div>

      {/* Demand Flow Funnel - Full Width */}
      <div className="mb-6">
        <DemandFlowFunnel />
      </div>

      {/* Raw Material Risk Summary and Consumption Error Heatmap - Side by Side */}
      <div className="grid lg:grid-cols-2 gap-6">
        <RawMaterialRiskTable />
        <ConsumptionErrorHeatmap />
      </div>
    </DashboardLayout>
  );
};

export default ConsumptionDashboard;

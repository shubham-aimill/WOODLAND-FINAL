import { Target, Package, BarChart3, AlertCircle, Activity } from "lucide-react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { KPICard } from "@/components/dashboard/KPICard";
import { SKUSalesTrendChart } from "@/components/dashboard/SKUSalesTrendChart";
import { SKUPerformanceTable } from "@/components/dashboard/SKUPerformanceTable";
import { SKUContributionHeatmap } from "@/components/dashboard/SKUContributionHeatmap";
import { TopDemandDriversPanel } from "@/components/dashboard/TopDemandDriversPanel";
import { RiskAlertCards } from "@/components/dashboard/RiskAlertCard";
import { RollingErrorChart } from "@/components/dashboard/RollingErrorChart";
import { useSalesKPIs } from "@/hooks/useDashboardData";
import { useFilters } from "@/contexts/FilterContext";

const SalesDashboard = () => {
  const { data: kpis, isLoading } = useSalesKPIs();
  const { filters } = useFilters();
  
  // Dynamic labels based on filter selection
  const forecastDays = filters.dateRange === "next-7" ? 7 : 30;

  const trend = (k: { trend: number; direction: "up" | "down" | "neutral" } | undefined) =>
    k ? { value: k.trend, direction: k.direction } : undefined;

  return (
    <DashboardLayout dashboard="sales">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        <KPICard
          title="Projected Sales"
          value={kpis?.totalForecastedUnits.value.toLocaleString() ?? "0"}
          unit="units"
          icon={<Package className="w-5 h-5" />}
          trend={trend(kpis?.totalForecastedUnits)}
          subtitle={`Next ${forecastDays} days forecast`}
          onClick={() => {}}
          isLoading={isLoading}
        />
        <KPICard
          title="Baseline Sales"
          value={kpis?.baselineSales.value.toLocaleString() ?? "0"}
          unit="units"
          icon={<BarChart3 className="w-5 h-5" />}
          trend={trend(kpis?.baselineSales)}
          subtitle={`Last ${forecastDays} days actual`}
          onClick={() => {}}
          isLoading={isLoading}
        />
        <KPICard
          title="Forecast Accuracy"
          value={kpis?.skuForecastAccuracy.value.toFixed(1) ?? "0"}
          unit="%"
          icon={<Target className="w-5 h-5" />}
          trend={trend(kpis?.skuForecastAccuracy)}
          status="success"
          subtitle="MAPE vs baseline"
          onClick={() => {}}
          isLoading={isLoading}
        />
        <KPICard
          title="Demand Volatility"
          value={kpis?.demandVolatilityIndex.value.toFixed(1) ?? "0"}
          unit=""
          icon={<Activity className="w-5 h-5" />}
          trend={trend(kpis?.demandVolatilityIndex)}
          subtitle="Standard deviation of forecast units"
          onClick={() => {}}
          isLoading={isLoading}
        />
        <KPICard
          title="At-Risk SKUs"
          value={kpis?.highRiskSKUsCount.value.toLocaleString() ?? "0"}
          unit="SKUs"
          icon={<AlertCircle className="w-5 h-5" />}
          trend={trend(kpis?.highRiskSKUsCount)}
          status="warning"
          subtitle="Require attention"
          onClick={() => {}}
          isLoading={isLoading}
        />
      </div>

      <div className="mb-6">
        <SKUSalesTrendChart />
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-6">
        <div className="space-y-4">
          <SKUContributionHeatmap />
          <TopDemandDriversPanel />
        </div>
        <div className="space-y-4">
          <SKUPerformanceTable />
          <RiskAlertCards />
        </div>
      </div>

      <div>
        <RollingErrorChart />
      </div>
    </DashboardLayout>
  );
};

export default SalesDashboard;

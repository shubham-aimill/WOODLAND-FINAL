import { ChartContainer } from "./ChartContainer";
import { useDemandFlowFunnel } from "@/hooks/useDashboardData";
import { Skeleton } from "@/components/ui/skeleton";
import { ChevronRight } from "lucide-react";

const STEP_IDS = ["skuForecast", "productMix", "productForecast", "rawMaterialDemand"] as const;

export const DemandFlowFunnel = () => {
  const { data, isLoading } = useDemandFlowFunnel();

  if (isLoading) {
    return (
      <ChartContainer
        title="Demand Flow Funnel"
        subtitle="SKU Forecast → Product Mix → Product Forecast → Raw Material Demand"
      >
        <Skeleton className="w-full h-[200px]" />
      </ChartContainer>
    );
  }

  const steps = data?.steps;
  if (!steps) return null;

  const list = STEP_IDS.map((id) => {
    const s = steps[id];
    return s ? { id, ...s } : null;
  }).filter(Boolean) as { id: string; label: string; value: number; unit: string }[];

  return (
    <ChartContainer
      title="Demand Flow Funnel"
      subtitle="SKU Forecast → Product Mix → Product Forecast → Raw Material Demand (Explainability)"
    >
      <div className="flex flex-wrap items-center gap-4 py-4">
        {list.map((step, i) => (
          <div key={step.id} className="flex items-center gap-2">
            <div className="rounded-xl border-2 border-primary/30 bg-primary/5 px-5 py-3 min-w-[180px]">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {step.label}
              </p>
              <p className="text-xl font-bold tabular-nums mt-1">
                {step.value.toLocaleString()} <span className="text-sm font-normal text-muted-foreground">{step.unit}</span>
              </p>
            </div>
            {i < list.length - 1 && (
              <ChevronRight className="w-5 h-5 text-muted-foreground flex-shrink-0" />
            )}
          </div>
        ))}
      </div>
    </ChartContainer>
  );
};

import { useMemo } from "react";
import { ChartContainer } from "./ChartContainer";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useConsumptionErrorHeatmap } from "@/hooks/useDashboardData";
import { useFilters } from "@/contexts/FilterContext";
import { Skeleton } from "@/components/ui/skeleton";

interface HeatmapItem {
  date: string;
  rawMaterial: string;
  variancePct?: number;
  forecastErrorPct?: number; // Legacy field
  actual?: number;
  average?: number;
  forecast?: number; // Forecasted consumption
}

// Simplified 3-color scheme
const getColorClass = (variancePct: number) => {
  const abs = Math.abs(variancePct);
  if (abs <= 10) return { bg: "bg-emerald-200", text: "text-emerald-900", label: "Normal" };
  if (abs <= 25) return { bg: "bg-amber-200", text: "text-amber-900", label: "Moderate" };
  return { bg: "bg-red-400", text: "text-white", label: "High" };
};

export const ConsumptionErrorHeatmap = () => {
  const { data, isLoading } = useConsumptionErrorHeatmap();
  const { filters } = useFilters();
  
  const { dates, materials, matrix, detailsMatrix } = useMemo(() => {
    if (!data?.length) return { 
      dates: [] as string[], 
      materials: [] as string[], 
      matrix: {} as Record<string, Record<string, number>>,
      detailsMatrix: {} as Record<string, Record<string, { forecast: number; average: number }>>
    };
    
    const dateSet = new Set<string>();
    const matSet = new Set<string>();
      const m: Record<string, Record<string, number>> = {};
      const d: Record<string, Record<string, { forecast: number; average: number }>> = {};
      
      (data as HeatmapItem[]).forEach((c) => {
        dateSet.add(c.date);
        matSet.add(c.rawMaterial);
        if (!m[c.rawMaterial]) m[c.rawMaterial] = {};
        if (!d[c.rawMaterial]) d[c.rawMaterial] = {};
        // Support both new (variancePct) and legacy (forecastErrorPct) field names
        m[c.rawMaterial][c.date] = c.variancePct ?? c.forecastErrorPct ?? 0;
        d[c.rawMaterial][c.date] = { 
          forecast: c.forecast ?? c.actual ?? 0,  // Forecasted consumption
          average: c.average ?? 0  // 30-day historical average
        };
      });
    
    return {
      dates: Array.from(dateSet).sort(),
      materials: Array.from(matSet),
      matrix: m,
      detailsMatrix: d
    };
  }, [data]);

  if (isLoading) {
    return (
      <ChartContainer
        title="Consumption Variance Heatmap"
        subtitle="Forecasted consumption vs historical average (last 30 days) — identifies forecast deviations"
      >
        <Skeleton className="w-full h-[280px]" />
      </ChartContainer>
    );
  }

  return (
    <ChartContainer
      title="Consumption Variance Heatmap"
      subtitle="Forecasted consumption vs historical average (last 30 days) — identifies forecast deviations"
    >
      <div className="space-y-3">
        {/* Legend */}
        <div className="flex items-center justify-end gap-3 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded bg-emerald-200" />
            <span className="text-muted-foreground">±10% (Normal)</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded bg-amber-200" />
            <span className="text-muted-foreground">±10-25% (Moderate)</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded bg-red-400" />
            <span className="text-muted-foreground">&gt;±25% (High)</span>
          </div>
        </div>

        <div className="overflow-auto">
          <div className="min-w-[400px]">
            {/* X-axis: Dates */}
            <div className="flex gap-1 mb-1">
              <div className="w-28 flex-shrink-0" />
              {dates.map((d) => (
                <div
                  key={d}
                  className="flex-1 min-w-[50px] text-center text-[10px] font-medium text-muted-foreground py-1"
                >
                  {d}
                </div>
              ))}
            </div>
            
            {/* Y-axis: Raw Materials */}
            <TooltipProvider delayDuration={100}>
              {materials.map((mat) => (
                <div key={mat} className="flex gap-1 mb-1">
                  <div className="w-28 text-[10px] font-medium text-muted-foreground flex items-center truncate flex-shrink-0" title={mat}>
                    {mat.replace(/_/g, " ")}
                  </div>
                  {dates.map((d) => {
                    const v = matrix[mat]?.[d] ?? 0;
                    const details = detailsMatrix[mat]?.[d] || { forecast: 0, average: 0 };
                    const color = getColorClass(v);
                    
                    return (
                      <Tooltip key={d}>
                        <TooltipTrigger asChild>
                          <div
                            className={cn(
                              "flex-1 min-w-[50px] h-9 rounded flex items-center justify-center text-[10px] font-medium cursor-pointer transition-all hover:scale-105 hover:shadow-md hover:ring-2 hover:ring-primary/50",
                              color.bg,
                              color.text
                            )}
                          >
                            {v > 0 ? "+" : ""}{v.toFixed(0)}%
                          </div>
                        </TooltipTrigger>
                        <TooltipContent className="space-y-1">
                          <p className="font-semibold">{mat.replace(/_/g, " ")}</p>
                          <p className="text-sm text-muted-foreground">{d}</p>
                          <div className="border-t pt-1 mt-1 space-y-0.5">
                            <p className="text-sm">Forecasted: <strong>{details.forecast.toLocaleString()} units</strong></p>
                            <p className="text-sm">30-day Avg: <strong>{details.average.toLocaleString()} units</strong></p>
                            <p className={cn(
                              "text-xs font-medium",
                              Math.abs(v) <= 10 ? "text-emerald-600" : Math.abs(v) <= 25 ? "text-amber-600" : "text-red-600"
                            )}>
                              Variance: {v > 0 ? "+" : ""}{v.toFixed(1)}% ({color.label})
                            </p>
                          </div>
                        </TooltipContent>
                      </Tooltip>
                    );
                  })}
                </div>
              ))}
            </TooltipProvider>
          </div>
        </div>
        
        {/* Business Insight */}
        <div className="text-xs text-muted-foreground border-t pt-2">
          <strong>Insight:</strong> Red cells show forecasted consumption significantly above/below 30-day historical average — review forecast accuracy.
          Green cells indicate forecast aligns with historical patterns.
        </div>
      </div>
    </ChartContainer>
  );
};

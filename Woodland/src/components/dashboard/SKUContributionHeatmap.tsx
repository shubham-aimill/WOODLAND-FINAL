import { useMemo } from "react";
import { ChartContainer } from "./ChartContainer";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useSKUContributionHeatmap } from "@/hooks/useDashboardData";
import { Skeleton } from "@/components/ui/skeleton";

interface HeatmapData {
  sku: string;
  date: string;
  contributionPct: number;
  forecastUnits?: number;
}

// Simplified 3-color scale: Below Avg | Average | Above Avg
const HEATMAP_COLORS = {
  below: { bg: "bg-blue-200", text: "text-blue-900", label: "Below Avg" },
  average: { bg: "bg-gray-100", text: "text-gray-700", label: "Average" },
  above: { bg: "bg-red-400", text: "text-white", label: "Above Avg" },
};

// Get color based on value relative to average
const getHeatmapColor = (value: number, min: number, max: number, avg: number) => {
  const threshold = (max - min) * 0.15; // 15% band around average
  
  if (value < avg - threshold) return HEATMAP_COLORS.below;
  if (value > avg + threshold) return HEATMAP_COLORS.above;
  return HEATMAP_COLORS.average;
};

// Format date for display
const formatDate = (dateStr: string) => {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch {
    return dateStr;
  }
};

export const SKUContributionHeatmap = () => {
  const { data, isLoading } = useSKUContributionHeatmap();

  const { skus, dates, matrix, unitsMatrix, stats } = useMemo(() => {
    if (!data?.length) return { 
      skus: [] as string[], 
      dates: [] as string[], 
      matrix: {} as Record<string, Record<string, number>>,
      unitsMatrix: {} as Record<string, Record<string, number>>,
      stats: { min: 0, max: 0, avg: 0 }
    };
    
    const skuSet = new Set<string>();
    const dateSet = new Set<string>();
    const m: Record<string, Record<string, number>> = {};
    const u: Record<string, Record<string, number>> = {};
    let allValues: number[] = [];
    
    (data as HeatmapData[]).forEach((c) => {
      skuSet.add(c.sku);
      dateSet.add(c.date);
      if (!m[c.sku]) m[c.sku] = {};
      if (!u[c.sku]) u[c.sku] = {};
      m[c.sku][c.date] = c.contributionPct;
      u[c.sku][c.date] = c.forecastUnits || 0;
      allValues.push(c.contributionPct);
    });
    
    // Calculate stats for relative coloring
    const min = Math.min(...allValues);
    const max = Math.max(...allValues);
    const avg = allValues.reduce((a, b) => a + b, 0) / allValues.length;
    
    return {
      skus: Array.from(skuSet),
      dates: Array.from(dateSet).sort(),
      matrix: m,
      unitsMatrix: u,
      stats: { min, max, avg }
    };
  }, [data]);

  if (isLoading) {
    return (
      <ChartContainer
        title="SKU Contribution Heatmap"
        subtitle="Relative contribution % to daily demand — highlights over/under performers"
      >
        <Skeleton className="w-full h-[280px]" />
      </ChartContainer>
    );
  }

  return (
    <ChartContainer
      title="SKU Contribution Heatmap"
      subtitle="Relative contribution % to daily demand — highlights over/under performers"
    >
      <div className="space-y-3">
        {/* Color Legend - Simplified */}
        <div className="flex items-center justify-end gap-3 text-xs">
          <div className="flex items-center gap-1">
            <div className={cn("w-4 h-4 rounded", HEATMAP_COLORS.below.bg)} />
            <span className="text-muted-foreground">Below Avg</span>
          </div>
          <div className="flex items-center gap-1">
            <div className={cn("w-4 h-4 rounded", HEATMAP_COLORS.average.bg)} />
            <span className="text-muted-foreground">Average</span>
          </div>
          <div className="flex items-center gap-1">
            <div className={cn("w-4 h-4 rounded", HEATMAP_COLORS.above.bg)} />
            <span className="text-muted-foreground">Above Avg</span>
          </div>
        </div>
        
        {/* Stats Summary */}
        <div className="flex items-center gap-4 text-xs text-muted-foreground border-b pb-2">
          <span>Min: <strong className="text-foreground">{stats.min.toFixed(1)}%</strong></span>
          <span>Avg: <strong className="text-foreground">{stats.avg.toFixed(1)}%</strong></span>
          <span>Max: <strong className="text-foreground">{stats.max.toFixed(1)}%</strong></span>
        </div>

        <div className="overflow-auto max-h-[320px]">
          <div className="min-w-[400px]">
            {/* X-axis = SKU (columns) */}
            <div className="flex gap-1 mb-1 sticky top-0 bg-background z-10 pb-1">
              <div className="w-16 flex-shrink-0" />
              {skus.map((sku) => (
                <div 
                  key={sku} 
                  className="w-14 flex-shrink-0 text-center text-[10px] font-medium text-muted-foreground py-1 truncate" 
                  title={sku}
                >
                  {sku.replace("WL-SKU-", "SKU-").substring(0, 8)}
                </div>
              ))}
            </div>
            
            {/* Y-axis = Date (rows) */}
            <TooltipProvider delayDuration={100}>
              {dates.map((d) => (
                <div key={d} className="flex gap-1 mb-1">
                  <div className="w-16 text-[10px] font-medium text-muted-foreground flex items-center flex-shrink-0">
                    {formatDate(d)}
                  </div>
                  {skus.map((sku) => {
                    const v = matrix[sku]?.[d] ?? 0;
                    const units = unitsMatrix[sku]?.[d] ?? 0;
                    const color = getHeatmapColor(v, stats.min, stats.max, stats.avg);
                    const deviation = v - stats.avg;
                    const deviationStr = deviation >= 0 ? `+${deviation.toFixed(2)}%` : `${deviation.toFixed(2)}%`;
                    
                    return (
                      <Tooltip key={sku}>
                        <TooltipTrigger asChild>
                          <div
                            className={cn(
                              "w-14 flex-shrink-0 h-8 rounded flex items-center justify-center text-[10px] font-medium cursor-pointer transition-all hover:scale-105 hover:shadow-md hover:ring-2 hover:ring-primary/50",
                              color.bg,
                              color.text
                            )}
                          >
                            {v.toFixed(1)}%
                          </div>
                        </TooltipTrigger>
                        <TooltipContent className="space-y-1">
                          <p className="font-semibold">{sku}</p>
                          <p className="text-sm">{formatDate(d)}</p>
                          <div className="border-t pt-1 mt-1 space-y-0.5">
                            <p className="text-sm">Forecast: <strong>{units.toLocaleString()} units</strong></p>
                            <p className="text-sm">Contribution: <strong>{v.toFixed(2)}%</strong></p>
                            <p className={cn(
                              "text-xs",
                              deviation >= 0 ? "text-red-500" : "text-blue-500"
                            )}>
                              vs Avg: {deviationStr}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Status: {color.label}
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
        
        {/* Business Insight Footer */}
        <div className="text-xs text-muted-foreground border-t pt-2">
          <strong>Insight:</strong> Red cells indicate SKUs contributing above average — focus inventory and promotions there. 
          Blue cells show lower contributors — consider bundling or discontinuation analysis.
        </div>
      </div>
    </ChartContainer>
  );
};

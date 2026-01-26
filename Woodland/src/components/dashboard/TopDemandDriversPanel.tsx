import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { ChartContainer } from "./ChartContainer";
import { useTopDemandDrivers } from "@/hooks/useDashboardData";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export const TopDemandDriversPanel = () => {
  const { data, isLoading } = useTopDemandDrivers();

  if (isLoading) {
    return (
      <ChartContainer title="Top Demand Drivers" subtitle="Top 10 SKUs by contribution">
        <div className="space-y-3">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      </ChartContainer>
    );
  }

  const drivers = (data ?? []).slice(0, 10);

  return (
    <ChartContainer title="Top Demand Drivers" subtitle="Top 10 SKUs by contribution">
      <div className="space-y-2 max-h-[320px] overflow-auto">
        {drivers.map((d, i) => (
          <div
            key={d.sku}
            className={cn(
              "flex items-center justify-between rounded-lg border border-border/50 px-3 py-2",
              "hover:bg-muted/50 transition-colors"
            )}
          >
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-xs font-medium text-muted-foreground w-5">{i + 1}</span>
              <div className="min-w-0">
                <p className="font-medium text-foreground text-sm truncate">{d.sku}</p>
                <p className="text-xs text-muted-foreground truncate">{d.name}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className="tabular-nums font-semibold text-sm">{d.contributionPct.toFixed(1)}%</span>
              {d.trendDirection === "up" && <TrendingUp className="w-4 h-4 text-success" />}
              {d.trendDirection === "down" && <TrendingDown className="w-4 h-4 text-destructive" />}
              {d.trendDirection === "flat" && <Minus className="w-4 h-4 text-muted-foreground" />}
            </div>
          </div>
        ))}
      </div>
    </ChartContainer>
  );
};

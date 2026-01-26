import { ChartContainer } from "./ChartContainer";
import { useForecastDeviationHistogram } from "@/hooks/useDashboardData";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const BUCKET_LABELS: Record<string, string> = {
  under: "Under-forecast",
  accurate: "Accurate band",
  over: "Over-forecast",
};

const BUCKET_STYLES: Record<string, string> = {
  under: "bg-destructive/80",
  accurate: "bg-success",
  over: "bg-warning",
};

export const ForecastDeviationHistogram = () => {
  const { data, isLoading } = useForecastDeviationHistogram();

  if (isLoading) {
    return (
      <ChartContainer
        title="Forecast Deviation Distribution"
        subtitle="Under / Accurate / Over-forecast"
      >
        <Skeleton className="w-full h-[280px]" />
      </ChartContainer>
    );
  }

  const buckets = data ?? [];
  const max = Math.max(1, ...buckets.map((b) => b.count));

  return (
    <ChartContainer
      title="Forecast Deviation Distribution"
      subtitle="Under / Accurate / Over-forecast"
    >
      <div className="space-y-4 py-4">
        {buckets.map((b) => (
          <div key={b.bucket} className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="font-medium text-muted-foreground">{BUCKET_LABELS[b.bucket] ?? b.bucket}</span>
              <span className="tabular-nums text-foreground">{b.count}</span>
            </div>
            <div className="h-8 rounded-lg bg-muted/50 overflow-hidden">
              <div
                className={cn("h-full rounded-lg transition-all", BUCKET_STYLES[b.bucket] ?? "bg-muted")}
                style={{ width: `${Math.max(4, (b.count / max) * 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </ChartContainer>
  );
};

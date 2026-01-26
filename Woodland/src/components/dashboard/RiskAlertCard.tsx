import { AlertTriangle, TrendingDown, Clock, ExternalLink } from "lucide-react";
import { ChartContainer } from "./ChartContainer";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useRiskAlerts } from "@/hooks/useDashboardData";
import { Skeleton } from "@/components/ui/skeleton";

const severityStyles = {
  high: {
    bg: "bg-destructive/5 border-destructive/20",
    icon: "bg-destructive/10 text-destructive",
    badge: "bg-destructive/10 text-destructive",
  },
  critical: {
    bg: "bg-destructive/5 border-destructive/20",
    icon: "bg-destructive/10 text-destructive",
    badge: "bg-destructive/10 text-destructive",
  },
  medium: {
    bg: "bg-warning/5 border-warning/20",
    icon: "bg-warning/10 text-warning",
    badge: "bg-warning/10 text-warning",
  },
  low: {
    bg: "bg-chart-5/5 border-chart-5/20",
    icon: "bg-chart-5/10 text-chart-5",
    badge: "bg-chart-5/10 text-chart-5",
  },
};

export const RiskAlertCards = () => {
  const { data: riskItems, isLoading } = useRiskAlerts();

  if (isLoading) {
    return (
      <ChartContainer title="High Risk SKUs" subtitle="Items requiring immediate attention">
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-24 w-full rounded-xl" />
          ))}
        </div>
      </ChartContainer>
    );
  }

  return (
    <ChartContainer 
      title="High Risk SKUs" 
      subtitle="Items requiring immediate attention"
      footer={
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mt-2 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-destructive/10 border border-destructive/20" />
            <span><strong>High/Critical:</strong> Low accuracy (&lt; mean - 1σ) or high volatility (&gt; 1.5× mean)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-warning/10 border border-warning/20" />
            <span><strong>Medium:</strong> Accuracy &lt; mean - 0.3σ</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-chart-5/10 border border-chart-5/20" />
            <span><strong>Low:</strong> Above average performance</span>
          </div>
        </div>
      }
    >
      <div className="space-y-3 max-h-[340px] overflow-auto scrollbar-thin pr-1">
        {riskItems?.map((item) => {
          const styles = severityStyles[item.severity as keyof typeof severityStyles] || severityStyles.medium;
          
          return (
            <div
              key={item.id}
              className={cn(
                "rounded-xl border p-4 transition-all duration-200 hover:shadow-md cursor-pointer",
                styles.bg
              )}
            >
              <div className="flex items-start gap-3">
                {/* Risk Icon */}
                <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center shrink-0", styles.icon)}>
                  {item.severity === "critical" || item.severity === "high" ? (
                    <AlertTriangle className="w-5 h-5" />
                  ) : item.issue.includes("Drop") ? (
                    <TrendingDown className="w-5 h-5" />
                  ) : (
                    <Clock className="w-5 h-5" />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <div>
                      <span className="text-sm font-semibold text-foreground">
                        {item.sku}
                      </span>
                      <span className={cn("ml-2 text-xs px-2 py-0.5 rounded-full font-medium", styles.badge)}>
                        {item.issue}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2 truncate">
                    {item.name}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    {item.daysUntilStockout && (
                      <span className="text-xs text-muted-foreground">
                        <span className="font-medium text-foreground">{item.daysUntilStockout}</span> days to stockout
                      </span>
                    )}
                    
                    <Button 
                      size="sm" 
                      variant={item.severity === "critical" || item.severity === "high" ? "default" : "outline"}
                      className={cn(
                        "h-7 text-xs gap-1",
                        (item.severity === "critical" || item.severity === "high") && "bg-primary hover:bg-primary/90"
                      )}
                    >
                      {item.recommendation}
                      <ExternalLink className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </ChartContainer>
  );
};

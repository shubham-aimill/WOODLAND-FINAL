import { Info, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { ChartContainer } from "./ChartContainer";
import { cn } from "@/lib/utils";

export const VolatilityExplainability = () => {
  return (
    <ChartContainer 
      title="Demand Volatility Metrics" 
      subtitle="How volatility is calculated and interpreted"
    >
      <div className="space-y-4">
        {/* Calculation Explanation */}
        <div className="bg-muted/30 rounded-lg p-4 space-y-3">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
            <div className="space-y-2 text-sm">
              <p className="font-semibold text-foreground">Calculation Method</p>
              <div className="space-y-1.5 text-muted-foreground">
                <p>
                  <strong>Volatility</strong> = Standard Deviation of daily forecast units
                </p>
                <p className="text-xs pl-4 border-l-2 border-primary/20">
                  Measures the spread/variation in daily forecasted demand. 
                  Higher values indicate more unpredictable demand patterns.
                </p>
                <p className="pt-2">
                  <strong>Formula:</strong> σ = √[Σ(xᵢ - x̄)² / n]
                </p>
                <p className="text-xs pl-4 border-l-2 border-primary/20">
                  Where xᵢ = daily forecast units, x̄ = mean forecast, n = number of days
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Volatility Levels Legend */}
        <div className="space-y-2">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
            Volatility Levels
          </p>
          <div className="grid grid-cols-1 gap-2">
            {/* High Volatility */}
            <div className="flex items-center gap-3 p-2.5 rounded-lg bg-destructive/5 border border-destructive/20">
              <div className="flex items-center gap-2 min-w-[100px]">
                <TrendingUp className="w-4 h-4 text-destructive" />
                <span className="text-sm font-medium text-foreground">High Volatility</span>
              </div>
              <div className="flex-1 text-xs text-muted-foreground">
                <span className="font-medium">Threshold:</span> Volatility &gt; 1.5× mean volatility
              </div>
              <div className="text-xs text-muted-foreground/70 italic">
                Indicates unpredictable demand patterns requiring closer monitoring
              </div>
            </div>

            {/* Medium Volatility */}
            <div className="flex items-center gap-3 p-2.5 rounded-lg bg-warning/5 border border-warning/20">
              <div className="flex items-center gap-2 min-w-[100px]">
                <Minus className="w-4 h-4 text-warning" />
                <span className="text-sm font-medium text-foreground">Medium Volatility</span>
              </div>
              <div className="flex-1 text-xs text-muted-foreground">
                <span className="font-medium">Range:</span> 0.75× - 1.5× mean volatility
              </div>
              <div className="text-xs text-muted-foreground/70 italic">
                Moderate variation in demand, standard forecasting applies
              </div>
            </div>

            {/* Low Volatility */}
            <div className="flex items-center gap-3 p-2.5 rounded-lg bg-success/5 border border-success/20">
              <div className="flex items-center gap-2 min-w-[100px]">
                <TrendingDown className="w-4 h-4 text-success" />
                <span className="text-sm font-medium text-foreground">Low Volatility</span>
              </div>
              <div className="flex-1 text-xs text-muted-foreground">
                <span className="font-medium">Range:</span> &lt; 0.75× mean volatility
              </div>
              <div className="text-xs text-muted-foreground/70 italic">
                Stable, predictable demand patterns with consistent forecasting
              </div>
            </div>
          </div>
        </div>

        {/* Business Insight */}
        <div className="bg-primary/5 rounded-lg p-3 border border-primary/10">
          <p className="text-xs font-semibold text-foreground mb-1.5">Business Impact</p>
          <p className="text-xs text-muted-foreground leading-relaxed">
            High volatility SKUs may require safety stock adjustments, more frequent reviews, 
            or alternative forecasting methods. Low volatility SKUs are ideal candidates for 
            automated replenishment systems.
          </p>
        </div>
      </div>
    </ChartContainer>
  );
};

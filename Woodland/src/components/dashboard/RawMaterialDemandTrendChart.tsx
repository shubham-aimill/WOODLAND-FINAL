import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { ChartContainer } from "./ChartContainer";
import { useRawMaterialDemandTrend } from "@/hooks/useDashboardData";
import { useFilters } from "@/contexts/FilterContext";
import { Skeleton } from "@/components/ui/skeleton";
import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { BarChart3 } from "lucide-react";

// Industry standard colors
const ACTUAL_COLOR = "hsl(210 29% 24%)";      // Dark for historical actuals
const FORECAST_COLOR = "hsl(45 89% 55%)";     // Branded gold for forecast

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: { dataKey: string; value: number; color: string }[]; label?: string }) => {
  if (!active || !payload?.length) return null;
  
  const actual = payload.find((p) => p.dataKey === "actual");
  const forecast = payload.find((p) => p.dataKey === "forecast");
  const period = actual?.value != null ? "Historical" : forecast?.value != null ? "Forecast" : "";
  
  return (
    <div className="bg-background border border-border rounded-lg shadow-lg p-4">
      <p className="font-semibold text-foreground mb-1">{label}</p>
      {period && <p className="text-xs text-muted-foreground mb-2">{period} Period</p>}
      <div className="space-y-1.5 text-sm">
        {actual && actual.value != null && (
          <div className="flex justify-between gap-4">
            <span className="text-muted-foreground">Actual Consumption</span>
            <span className="font-medium tabular-nums">{actual.value.toLocaleString()} units</span>
          </div>
        )}
        {forecast && forecast.value != null && (
          <div className="flex justify-between gap-4">
            <span className="text-muted-foreground">Forecasted Demand</span>
            <span className="font-medium tabular-nums text-primary">{forecast.value.toLocaleString()} units</span>
          </div>
        )}
      </div>
    </div>
  );
};

export const RawMaterialDemandTrendChart = () => {
  const { filters } = useFilters();
  const [localAggregation, setLocalAggregation] = useState<"daily" | "weekly">("daily");
  
  // Fetch data with local aggregation setting
  const { data, forecastCutoffDate, isLoading } = useRawMaterialDemandTrend(localAggregation);
  
  // Dynamic labels based on filter
  const forecastDays = filters.dateRange === "next-7" ? 7 : 30;
  const subtitle = `Last ${forecastDays} days actual (solid) + Next ${forecastDays} days forecast (dashed)`;

  const { chartData, cutoffDisplayDate } = useMemo(() => {
    if (!data?.length) return { chartData: [], cutoffDisplayDate: null };
    
    // Format dates for display
    const formatted = data.map((item: any) => {
      const dateStr = typeof item.date === 'string' ? item.date.split('T')[0] : item.date;
      return {
        ...item,
        date: dateStr,
        displayDate: new Date(dateStr).toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric' 
        })
      };
    }).sort((a: any, b: any) => a.date.localeCompare(b.date));
    
    // Find cutoff date display value
    const cutoff = forecastCutoffDate || '2025-12-30';
    const cutoffItem = formatted.find((d: any) => d.date === cutoff);
    
    return { 
      chartData: formatted,
      cutoffDisplayDate: cutoffItem?.displayDate || null
    };
  }, [data, forecastCutoffDate]);

  if (isLoading) {
    return (
      <ChartContainer
        title="Demand Trend Analysis"
        subtitle={subtitle}
      >
        <Skeleton className="w-full h-[320px]" />
      </ChartContainer>
    );
  }

  return (
    <ChartContainer
      title="Demand Trend Analysis"
      subtitle={subtitle}
      actions={
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-border bg-secondary/30 p-0.5">
            {(["daily", "weekly"] as const).map((v) => (
              <Button
                key={v}
                variant="ghost"
                size="sm"
                onClick={() => setLocalAggregation(v)}
                className={cn(
                  "capitalize text-xs px-3 h-7 rounded-md transition-all",
                  localAggregation === v
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {v}
              </Button>
            ))}
          </div>
        </div>
      }
    >
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(40 15% 88%)" vertical={false} />
          <XAxis
            dataKey="displayDate"
            axisLine={false}
            tickLine={false}
            tick={{ fill: "hsl(207 13% 45%)", fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: "hsl(207 13% 45%)", fontSize: 12 }}
            tickFormatter={(v) => (v >= 1000 ? `${(v / 1000).toFixed(1)}k` : String(v))}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ paddingBottom: 20 }}
            formatter={(v) => <span className="text-sm text-muted-foreground capitalize">{v}</span>}
          />
          
          {/* Forecast Cutoff Line */}
          {cutoffDisplayDate && (
            <ReferenceLine
              x={cutoffDisplayDate}
              stroke="hsl(0 0% 60%)"
              strokeDasharray="4 4"
              strokeWidth={2}
              label={{
                value: "Forecast →",
                position: "top",
                fill: "hsl(0 0% 50%)",
                fontSize: 11,
                fontWeight: 500
              }}
            />
          )}
          
          {/* Actual line (solid, dark) - Historical consumption */}
          <Line
            type="monotone"
            dataKey="actual"
            name="Actual Consumption"
            stroke={ACTUAL_COLOR}
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 6, fill: ACTUAL_COLOR, stroke: "#fff", strokeWidth: 2 }}
            connectNulls={false}
          />
          
          {/* Forecast line (dashed, branded) - Future demand */}
          <Line
            type="monotone"
            dataKey="forecast"
            name="Forecasted Demand"
            stroke={FORECAST_COLOR}
            strokeWidth={2.5}
            strokeDasharray="6 4"
            dot={false}
            activeDot={{ r: 6, fill: FORECAST_COLOR, stroke: "#fff", strokeWidth: 2 }}
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

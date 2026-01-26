import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Line,
  Area,
  ComposedChart,
} from "recharts";
import { ChartContainer } from "./ChartContainer";
import { useForecastComparison } from "@/hooks/useDashboardData";
import { useFilters } from "@/contexts/FilterContext";
import { Skeleton } from "@/components/ui/skeleton";
import { useMemo } from "react";

// Industry standard colors
const ACTUAL_COLOR = "hsl(210 29% 24%)";
const FORECAST_COLOR = "hsl(45 89% 55%)";
const CONFIDENCE_COLOR = "hsl(45 89% 60%)";

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  
  const actualData = payload.find((p: any) => p.dataKey === "actual");
  const forecastData = payload.find((p: any) => p.dataKey === "forecast");
  const confLow = payload.find((p: any) => p.dataKey === "confidenceLow");
  const confHigh = payload.find((p: any) => p.dataKey === "confidenceHigh");
  
  const period = actualData?.value != null ? "Historical" : forecastData?.value != null ? "Forecast" : "";

  return (
    <div className="bg-background border border-border rounded-lg shadow-lg p-4">
      <p className="font-semibold text-foreground mb-1">{label}</p>
      {period && <p className="text-xs text-muted-foreground mb-2">{period} Period</p>}
      <div className="space-y-1.5 text-sm">
        {actualData?.value != null && (
          <div className="flex items-center justify-between gap-4">
            <span className="text-muted-foreground">Actual Consumption</span>
            <span className="font-medium text-foreground tabular-nums">
              {actualData.value.toLocaleString()} units
            </span>
          </div>
        )}
        {forecastData?.value != null && (
          <>
            <div className="flex items-center justify-between gap-4">
              <span className="text-muted-foreground">Forecasted Demand</span>
              <span className="font-medium text-primary tabular-nums">
                {forecastData.value.toLocaleString()} units
              </span>
            </div>
            {confLow?.value != null && confHigh?.value != null && (
              <div className="flex items-center justify-between gap-4 text-xs">
                <span className="text-muted-foreground">90% Confidence</span>
                <span className="font-medium tabular-nums text-muted-foreground">
                  {confLow.value.toLocaleString()} - {confHigh.value.toLocaleString()}
                </span>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export const ForecastComparisonChart = () => {
  const { data: rawData, isLoading } = useForecastComparison();
  const { filters } = useFilters();
  
  // Dynamic labels based on filter
  const forecastDays = filters.dateRange === "next-7" ? 7 : 30;
  const subtitle = `Weekly aggregation — Last ${forecastDays} days actual vs Next ${forecastDays} days forecast`;

  const { chartData, cutoffIndex } = useMemo(() => {
    if (!rawData?.length) return { chartData: [], cutoffIndex: null };
    
    // Find the cutoff point (last historical data point)
    const historicalData = rawData.filter((d: any) => d.period === "historical");
    const lastHistoricalDate = historicalData.length > 0 
      ? historicalData[historicalData.length - 1]?.date 
      : null;
    
    return {
      chartData: rawData,
      cutoffIndex: lastHistoricalDate
    };
  }, [rawData]);

  if (isLoading) {
    return (
      <ChartContainer
        title="Forecast Accuracy Comparison"
        subtitle={subtitle}
      >
        <Skeleton className="w-full h-[280px]" />
      </ChartContainer>
    );
  }

  return (
    <ChartContainer
      title="Forecast Accuracy Comparison"
      subtitle={subtitle}
    >
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="confidenceBandGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CONFIDENCE_COLOR} stopOpacity={0.3} />
              <stop offset="95%" stopColor={CONFIDENCE_COLOR} stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(40 15% 88%)" vertical={false} />
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={{ fill: "hsl(207 13% 45%)", fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: "hsl(207 13% 45%)", fontSize: 12 }}
            tickFormatter={(value) => (value >= 1000 ? `${(value / 1000).toFixed(0)}k` : String(value))}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ paddingBottom: 20 }}
            formatter={(value) => (
              <span className="text-sm text-muted-foreground capitalize">{value}</span>
            )}
          />
          
          {/* Forecast Cutoff Line */}
          {cutoffIndex && (
            <ReferenceLine
              x={cutoffIndex}
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
          
          {/* Confidence Band (only for forecast period) */}
          <Area
            type="monotone"
            dataKey="confidenceHigh"
            stroke="transparent"
            fill="url(#confidenceBandGradient)"
            connectNulls={false}
            name="Confidence Band"
          />
          <Area
            type="monotone"
            dataKey="confidenceLow"
            stroke="transparent"
            fill="hsl(var(--background))"
            connectNulls={false}
            legendType="none"
          />
          
          {/* Forecast Line (dashed, golden) - Future period */}
          <Line
            type="monotone"
            dataKey="forecast"
            stroke={FORECAST_COLOR}
            strokeWidth={2.5}
            strokeDasharray="6 4"
            dot={false}
            activeDot={{ r: 5, fill: FORECAST_COLOR, stroke: "#fff", strokeWidth: 2 }}
            connectNulls={false}
            name="Forecasted Demand"
          />
          
          {/* Actual Line (solid, dark) - Historical period */}
          <Line
            type="monotone"
            dataKey="actual"
            stroke={ACTUAL_COLOR}
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 6, fill: ACTUAL_COLOR, stroke: "#fff", strokeWidth: 2 }}
            connectNulls={false}
            name="Actual Consumption"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

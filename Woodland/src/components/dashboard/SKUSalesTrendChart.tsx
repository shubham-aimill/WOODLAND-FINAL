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
import { useSKUSalesTrend } from "@/hooks/useDashboardData";
import { useFilters } from "@/contexts/FilterContext";
import { Skeleton } from "@/components/ui/skeleton";
import { useMemo } from "react";

// Colors for channels (forecast lines)
const CHANNEL_COLORS: Record<string, string> = {
  "E-Commerce": "hsl(220 70% 50%)",      // Blue for E-Commerce
  "Offline Retail": "hsl(25 85% 55%)",   // Orange/Red for Retail
  "Wholesale": "hsl(145 40% 45%)",       // Green for Wholesale
  "Direct": "hsl(200 60% 55%)",          // Cyan for Direct
};

// Actual line colors (darker versions of channel colors for solid lines)
const ACTUAL_COLORS: Record<string, string> = {
  "E-Commerce": "hsl(220 70% 35%)",      // Darker blue for E-Commerce actual
  "Offline Retail": "hsl(25 85% 40%)",   // Darker orange/red for Retail actual
  "Wholesale": "hsl(145 40% 30%)",       // Darker green for Wholesale actual
  "Direct": "hsl(200 60% 40%)",          // Darker cyan for Direct actual
};

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: { name: string; value: number; color: string; dataKey: string }[]; label?: string }) => {
  if (!active || !payload?.length) return null;
  
  // Determine if this is historical or forecast period
  const hasActual = payload.some(p => p.dataKey?.includes('_actual') && p.value != null);
  const hasForecast = payload.some(p => p.dataKey?.includes('_forecast') && p.value != null);
  const periodLabel = hasActual ? "Historical" : hasForecast ? "Forecast" : "";
  
  return (
    <div className="bg-background border border-border rounded-lg shadow-lg p-4">
      <p className="font-semibold text-foreground mb-1">{label}</p>
      {periodLabel && <p className="text-xs text-muted-foreground mb-2">{periodLabel} Period</p>}
      <div className="space-y-1.5 text-sm">
        {payload.filter(p => p.value != null).map((p) => (
          <div key={p.name} className="flex justify-between gap-4">
            <span className="text-muted-foreground capitalize">{p.name}</span>
            <span className="font-medium tabular-nums">{p.value?.toLocaleString()} units</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const SKUSalesTrendChart = () => {
  const { data, forecastCutoffDate, isLoading } = useSKUSalesTrend();
  const { filters } = useFilters();
  
  // Dynamic labels based on filter
  const forecastDays = filters.dateRange === "next-7" ? 7 : 30;
  const subtitle = `Last ${forecastDays} days actual (solid) + Next ${forecastDays} days forecast (dashed)`;

  const { chartData, channels, cutoffDate } = useMemo(() => {
    if (!data?.length) return { chartData: [], channels: [] as string[], cutoffDate: null };
    
    // Extract unique channels
    const chSet = new Set<string>();
    data.forEach((d: any) => d.channel && chSet.add(d.channel));
    const chList = Array.from(chSet);
    
    // Group data by date and pivot by channel
    const byDate = new Map<string, Record<string, any>>();
    
    data.forEach((d: any) => {
      const dateKey = typeof d.date === 'string' ? d.date.split('T')[0] : d.date;
      
      if (!byDate.has(dateKey)) {
        byDate.set(dateKey, { 
          date: dateKey,
          period: d.period || 'historical'
        });
      }
      
      const row = byDate.get(dateKey)!;
      
      if (d.channel) {
        // Actual values (historical period)
        if (d.actual != null) {
          row[`${d.channel}_actual`] = d.actual;
        }
        // Forecast values (forecast period)
        if (d.forecast != null) {
          row[`${d.channel}_forecast`] = d.forecast;
        }
      }
    });
    
    const arr = Array.from(byDate.values()).sort((a, b) => 
      String(a.date).localeCompare(String(b.date))
    );
    
    // Format dates for display
    const formatted = arr.map(item => ({
      ...item,
      rawDate: item.date,  // Keep original date for cutoff comparison
      displayDate: new Date(item.date).toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      })
    }));
    
    return { 
      chartData: formatted, 
      channels: chList,
      cutoffDate: forecastCutoffDate || '2025-12-30'
    };
  }, [data, forecastCutoffDate]);

  // Find the index of the cutoff date for the reference line
  const cutoffIndex = useMemo(() => {
    if (!cutoffDate || !chartData.length) return null;
    const idx = chartData.findIndex((d: any) => d.rawDate === cutoffDate);
    return idx >= 0 ? chartData[idx].displayDate : null;
  }, [chartData, cutoffDate]);

  const visibleChannels = filters.channel === "all" ? channels : [filters.channel].filter(Boolean);

  if (isLoading) {
    return (
      <ChartContainer title="Sales Trend Analysis" subtitle={subtitle}>
        <Skeleton className="w-full h-[320px]" />
      </ChartContainer>
    );
  }

  return (
    <ChartContainer 
      title="Sales Trend Analysis" 
      subtitle={subtitle}
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
            formatter={(v) => <span className="text-sm text-muted-foreground">{v}</span>}
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
          
          {/* Render lines for each visible channel */}
          {visibleChannels.flatMap((ch) => {
            const channelColor = CHANNEL_COLORS[ch] ?? "hsl(200 50% 50%)";
            const actualColor = ACTUAL_COLORS[ch] ?? "hsl(200 50% 35%)";
            return [
              // Actual line (solid, darker channel color) - Historical period
              <Line
                key={`${ch}-actual`}
                type="monotone"
                dataKey={`${ch}_actual`}
                name={`${ch} (Actual)`}
                stroke={actualColor}
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5, fill: actualColor, stroke: "#fff", strokeWidth: 2 }}
                connectNulls={true}
              />,
              // Forecast line (dashed, branded color) - Forecast period
              <Line
                key={`${ch}-forecast`}
                type="monotone"
                dataKey={`${ch}_forecast`}
                name={`${ch} (Forecast)`}
                stroke={channelColor}
                strokeWidth={2}
                strokeDasharray="6 4"
                dot={false}
                activeDot={{ r: 4, fill: channelColor, stroke: "#fff", strokeWidth: 2 }}
                connectNulls={false}
              />,
            ];
          })}
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

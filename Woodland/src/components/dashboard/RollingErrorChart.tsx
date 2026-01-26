import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { ChartContainer } from "./ChartContainer";
import { useRollingError } from "@/hooks/useDashboardData";
import { useFilters } from "@/contexts/FilterContext";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useMemo } from "react";

const WINDOWS = ["7", "30"] as const;

const CustomTooltip = ({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
}) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-background border border-border rounded-lg shadow-lg p-4">
      <p className="font-semibold text-foreground mb-2">{label}</p>
      <div className="space-y-1.5 text-sm">
        {payload.map((entry, i) => (
          <div key={i} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
              <span className="text-muted-foreground uppercase text-xs">{entry.name}</span>
            </div>
            <span className="font-medium text-foreground tabular-nums">{entry.value?.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const RollingErrorChart = () => {
  const { data, isLoading } = useRollingError();
  const { filters, setRollingWindow } = useFilters();
  const window = filters.rollingWindow ?? "7";

  // Calculate dynamic Y-axis domain based on data
  const yAxisDomain = useMemo(() => {
    if (!data || data.length === 0) return [0, 20];
    const maxValue = Math.max(...data.map((d: any) => d.mape || 0));
    // Add 20% padding to the top, with minimum of 20
    const paddedMax = Math.max(20, Math.ceil(maxValue * 1.2));
    return [0, paddedMax];
  }, [data]);

  if (isLoading) {
    return (
      <ChartContainer
        title="Rolling Forecast Error"
        subtitle="MAPE by 7 / 30-day window"
      >
        <Skeleton className="w-full h-[280px]" />
      </ChartContainer>
    );
  }

  return (
    <ChartContainer
      title="Rolling Forecast Error"
      subtitle="MAPE by 7 / 30-day window"
      actions={
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-border bg-secondary/30 p-0.5">
            {WINDOWS.map((w) => (
              <Button
                key={w}
                variant="ghost"
                size="sm"
                onClick={() => setRollingWindow(w)}
                className={cn(
                  "capitalize text-xs px-3 h-7 rounded-md transition-all",
                  window === w
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {w}-day
              </Button>
            ))}
          </div>
        </div>
      }
    >
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data ?? []} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(40 15% 88%)" vertical={false} />
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={{ fill: "hsl(207 13% 45%)", fontSize: 12 }}
            tickFormatter={(value) => {
              // Format date for display
              if (typeof value === 'string' && value.includes('T')) {
                return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
              }
              return value;
            }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: "hsl(207 13% 45%)", fontSize: 12 }}
            tickFormatter={(v) => `${v}%`}
            domain={yAxisDomain}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={5}
            stroke="hsl(145 50% 53%)"
            strokeDasharray="4 4"
            opacity={0.5}
            label={{ value: "Target", position: "right", fill: "hsl(145 50% 53%)", fontSize: 10 }}
          />
          <Line
            type="monotone"
            dataKey="mape"
            name="MAPE"
            stroke="hsl(45 89% 60%)"
            strokeWidth={2.5}
            dot={{ fill: "hsl(45 89% 60%)", stroke: "#fff", strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, fill: "hsl(45 89% 60%)", stroke: "#fff", strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

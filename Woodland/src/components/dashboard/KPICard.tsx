import { ReactNode } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

interface KPICardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: {
    value: number;
    direction: "up" | "down" | "neutral";
  };
  icon: ReactNode;
  subtitle?: string;
  onClick?: () => void;
  status?: "success" | "warning" | "error" | "neutral";
  isLoading?: boolean;
}

export const KPICard = ({
  title,
  value,
  unit,
  trend,
  icon,
  subtitle,
  onClick,
  status = "neutral",
  isLoading = false,
}: KPICardProps) => {
  const trendColor = {
    up: "text-success bg-success/10",
    down: "text-destructive bg-destructive/10",
    neutral: "text-muted-foreground bg-muted",
  };

  const statusStyles = {
    success: "border-success/20",
    warning: "border-warning/20",
    error: "border-destructive/20",
    neutral: "border-transparent",
  };

  if (isLoading) {
    return (
      <div className={cn("kpi-card", statusStyles[status])}>
        <div className="flex items-start justify-between mb-4">
          <Skeleton className="w-10 h-10 rounded-xl" />
          <Skeleton className="w-16 h-6 rounded-full" />
        </div>
        <Skeleton className="h-9 w-24 mb-1" />
        <Skeleton className="h-4 w-32 mb-1" />
        <Skeleton className="h-3 w-20" />
      </div>
    );
  }

  return (
    <div
      onClick={onClick}
      className={cn(
        "kpi-card group relative overflow-hidden",
        statusStyles[status],
        onClick && "cursor-pointer"
      )}
    >
      {/* Accent border on hover */}
      <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary scale-y-0 group-hover:scale-y-100 transition-transform origin-top" />

      <div className="flex items-start justify-between mb-4">
        {/* Icon */}
        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
          {icon}
        </div>

        {/* Trend Badge */}
        {trend && (
          <div
            className={cn(
              "flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium",
              trendColor[trend.direction]
            )}
          >
            <span className="w-3 h-3">
              {trend.direction === "up" && <TrendingUp className="w-3 h-3" />}
              {trend.direction === "down" && <TrendingDown className="w-3 h-3" />}
              {trend.direction === "neutral" && <Minus className="w-3 h-3" />}
            </span>
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>

      {/* Value */}
      <div className="mb-1">
        <span className="text-3xl font-bold text-foreground tabular-nums">
          {value}
        </span>
        {unit && (
          <span className="text-sm text-muted-foreground ml-1">{unit}</span>
        )}
      </div>

      {/* Title */}
      <div className="text-sm font-medium text-muted-foreground">{title}</div>

      {/* Subtitle */}
      {subtitle && (
        <div className="text-xs text-muted-foreground/70 mt-1">{subtitle}</div>
      )}
    </div>
  );
};

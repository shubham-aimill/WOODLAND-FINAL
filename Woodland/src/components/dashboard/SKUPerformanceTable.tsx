import { useState } from "react";
import { ChevronRight } from "lucide-react";
import { ChartContainer } from "./ChartContainer";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import { useSKUPerformance } from "@/hooks/useDashboardData";
import { Skeleton } from "@/components/ui/skeleton";
import type { SKUPerformance as SKUPerformanceType } from "@/services/api";

const categoryColors: Record<string, string> = {
  Footwear: "bg-chart-1/10 text-chart-1 border-chart-1/20",
  Apparel: "bg-chart-2/10 text-chart-2 border-chart-2/20",
  Bags: "bg-chart-3/10 text-chart-3 border-chart-3/20",
  Accessories: "bg-chart-5/10 text-chart-5 border-chart-5/20",
};

const riskStyles: Record<string, string> = {
  low: "bg-success/10 text-success",
  medium: "bg-warning/10 text-warning",
  high: "bg-destructive/10 text-destructive",
};

const MIX_CONTRIBUTION: Record<string, { channel: string; pct: number }[]> = {
  "WL-BOOT-001": [
    { channel: "Retail", pct: 45 },
    { channel: "Wholesale", pct: 30 },
    { channel: "E-Commerce", pct: 15 },
    { channel: "Direct", pct: 10 },
  ],
  "WL-JACK-002": [
    { channel: "Retail", pct: 40 },
    { channel: "Wholesale", pct: 35 },
    { channel: "E-Commerce", pct: 25 },
  ],
  "WL-BAG-003": [
    { channel: "Retail", pct: 50 },
    { channel: "E-Commerce", pct: 35 },
    { channel: "Wholesale", pct: 15 },
  ],
  "WL-BELT-004": [
    { channel: "Retail", pct: 55 },
    { channel: "Wholesale", pct: 25 },
    { channel: "Direct", pct: 20 },
  ],
  "WL-WALL-005": [
    { channel: "E-Commerce", pct: 50 },
    { channel: "Retail", pct: 30 },
    { channel: "Wholesale", pct: 20 },
  ],
  "WL-SHOE-006": [
    { channel: "Retail", pct: 60 },
    { channel: "Wholesale", pct: 40 },
  ],
};

export const SKUPerformanceTable = () => {
  const { data: skuData, isLoading } = useSKUPerformance();
  const [drillSku, setDrillSku] = useState<SKUPerformanceType | null>(null);

  const mix = drillSku ? (MIX_CONTRIBUTION[drillSku.sku] ?? []) : [];

  if (isLoading) {
    return (
      <ChartContainer title="SKU Performance" subtitle="Avg daily sales, accuracy, volatility, risk">
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-14 w-full" />
          ))}
        </div>
      </ChartContainer>
    );
  }

  return (
    <>
      <ChartContainer 
        title="SKU Performance" 
        subtitle="Avg daily sales, accuracy, volatility, risk"
      >
        <div className="max-h-[320px] overflow-auto scrollbar-thin">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent border-border/50">
                <TableHead className="text-xs font-semibold text-muted-foreground">SKU</TableHead>
                <TableHead className="text-xs font-semibold text-muted-foreground">Category</TableHead>
                <TableHead className="text-xs font-semibold text-muted-foreground text-right">Avg Daily Sales</TableHead>
                <TableHead className="text-xs font-semibold text-muted-foreground text-right">Accuracy</TableHead>
                <TableHead className="text-xs font-semibold text-muted-foreground text-right">Volatility</TableHead>
                <TableHead className="text-xs font-semibold text-muted-foreground">Risk</TableHead>
                <TableHead className="w-8" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {(skuData ?? []).map((item) => (
                <TableRow
                  key={item.id}
                  className="table-row-hover cursor-pointer border-border/30"
                  onClick={() => setDrillSku(item)}
                >
                  <TableCell>
                    <div>
                      <div className="font-medium text-foreground text-sm">{item.sku}</div>
                      <div className="text-xs text-muted-foreground truncate max-w-[140px]">{item.name}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={cn("text-[10px] font-medium border", categoryColors[item.category] ?? categoryColors.Accessories)}
                    >
                      {item.category}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right tabular-nums font-medium">
                    {item.avgDailySales.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <span
                      className={cn(
                        "tabular-nums font-medium",
                        item.accuracy >= 95 ? "text-success" : item.accuracy >= 90 ? "text-primary" : "text-warning"
                      )}
                    >
                      {item.accuracy}%
                    </span>
                  </TableCell>
                  <TableCell className="text-right tabular-nums text-muted-foreground">
                    {item.demandVolatility}
                  </TableCell>
                  <TableCell>
                    <span
                      className={cn(
                        "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium capitalize",
                        riskStyles[item.riskFlag]
                      )}
                    >
                      {item.riskFlag}
                    </span>
                  </TableCell>
                  <TableCell>
                    <ChevronRight className="w-4 h-4 text-muted-foreground" />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </ChartContainer>

      <Dialog open={!!drillSku} onOpenChange={(open) => !open && setDrillSku(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>SKU mix contribution — {drillSku?.sku}</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            {mix.map((m, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span className="text-foreground">{m.channel}</span>
                <span className="tabular-nums text-muted-foreground">{m.pct}%</span>
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

import { useState } from "react";
import { ChevronRight, AlertTriangle, CheckCircle, AlertCircle } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ChartContainer } from "./ChartContainer";
import { cn } from "@/lib/utils";
import { useRawMaterialRiskTable } from "@/hooks/useDashboardData";
import { Skeleton } from "@/components/ui/skeleton";
import type { RawMaterialRiskRow } from "@/services/api";

const RiskBadge = ({ status }: { status: RawMaterialRiskRow["riskStatus"] }) => {
  const styles = {
    Overstock: "bg-warning/10 text-warning",
    Stockout: "bg-destructive/10 text-destructive",
    Balanced: "bg-success/10 text-success",
  };
  const icons = {
    Overstock: <AlertTriangle className="w-3 h-3" />,
    Stockout: <AlertCircle className="w-3 h-3" />,
    Balanced: <CheckCircle className="w-3 h-3" />,
  };
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
        styles[status]
      )}
    >
      {icons[status]}
      {status}
    </span>
  );
};

const PRODUCT_CONTRIBUTORS: Record<string, { product: string; pct: number }[]> = {
  "Full-Grain Leather": [
    { product: "Heritage Boot", pct: 42 },
    { product: "Rancher Jacket", pct: 28 },
    { product: "Trail Backpack", pct: 18 },
    { product: "Classic Belt", pct: 12 },
  ],
  Suede: [
    { product: "Rancher Jacket", pct: 55 },
    { product: "Trail Backpack", pct: 30 },
    { product: "Heritage Boot", pct: 15 },
  ],
  Nubuck: [
    { product: "Heritage Boot", pct: 60 },
    { product: "Oxford Shoe", pct: 40 },
  ],
  "Leather Lining": [
    { product: "Heritage Boot", pct: 25 },
    { product: "Rancher Jacket", pct: 25 },
    { product: "Trail Backpack", pct: 25 },
    { product: "Classic Belt", pct: 25 },
  ],
  "Hardware Kit": [
    { product: "Trail Backpack", pct: 50 },
    { product: "Classic Belt", pct: 50 },
  ],
};

export const RawMaterialRiskTable = () => {
  const { data, isLoading } = useRawMaterialRiskTable();
  const [drillRow, setDrillRow] = useState<RawMaterialRiskRow | null>(null);

  const contributors = drillRow
    ? PRODUCT_CONTRIBUTORS[drillRow.rawMaterial] ?? [{ product: "—", pct: 0 }]
    : [];

  if (isLoading) {
    return (
      <ChartContainer title="Raw Material Risk Summary" subtitle="Forecast, consumption, inventory & risk">
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      </ChartContainer>
    );
  }

  return (
    <>
      <ChartContainer 
        title="Raw Material Risk Summary" 
        subtitle="Forecast, consumption, inventory & risk"
        footer={
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 mt-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <CheckCircle className="w-3 h-3 text-success" />
              <span><strong>Balanced:</strong> 50% - 200% of safety stock</span>
            </div>
            <div className="flex items-center gap-1.5">
              <AlertTriangle className="w-3 h-3 text-warning" />
              <span><strong>Overstock:</strong> &gt; 200% of safety stock</span>
            </div>
            <div className="flex items-center gap-1.5">
              <AlertCircle className="w-3 h-3 text-destructive" />
              <span><strong>Stockout:</strong> &lt; 50% of safety stock</span>
            </div>
          </div>
        }
      >
        <div className="max-h-[320px] overflow-auto scrollbar-thin">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent border-border/50">
                <TableHead className="text-xs font-semibold text-muted-foreground">Raw Material</TableHead>
                <TableHead className="text-xs font-semibold text-muted-foreground text-right">Forecast</TableHead>
                <TableHead className="text-xs font-semibold text-muted-foreground text-right">Actual</TableHead>
                <TableHead className="text-xs font-semibold text-muted-foreground text-right">Closing</TableHead>
                <TableHead className="text-xs font-semibold text-muted-foreground text-right">Safety</TableHead>
                <TableHead className="text-xs font-semibold text-muted-foreground">Risk</TableHead>
                <TableHead className="text-xs font-semibold text-muted-foreground">Stockout Date</TableHead>
                <TableHead className="w-8" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {(data ?? []).map((row) => (
                <TableRow
                  key={row.id}
                  className="table-row-hover cursor-pointer border-border/30"
                  onClick={() => setDrillRow(row)}
                >
                  <TableCell className="font-medium text-foreground">{row.rawMaterial}</TableCell>
                  <TableCell className="text-right tabular-nums">{row.forecastDemand.toLocaleString()}</TableCell>
                  <TableCell className="text-right tabular-nums">{row.actualConsumption.toLocaleString()}</TableCell>
                  <TableCell className="text-right tabular-nums">{row.closingInventory.toLocaleString()}</TableCell>
                  <TableCell className="text-right tabular-nums">{row.safetyStock.toLocaleString()}</TableCell>
                  <TableCell>
                    <RiskBadge status={row.riskStatus} />
                  </TableCell>
                  <TableCell className="text-xs tabular-nums">
                    {row.stockoutRiskDate ? (
                      <span className={cn(
                        "px-2 py-0.5 rounded",
                        row.riskStatus === "Stockout" ? "bg-destructive/10 text-destructive" : "text-muted-foreground"
                      )}>
                        {new Date(row.stockoutRiskDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </span>
                    ) : (
                      <span className="text-muted-foreground/50">—</span>
                    )}
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

      <Dialog open={!!drillRow} onOpenChange={(open) => !open && setDrillRow(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Product-level contributors — {drillRow?.rawMaterial}</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            {contributors.map((c, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span className="text-foreground">{c.product}</span>
                <span className="tabular-nums text-muted-foreground">{c.pct}%</span>
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

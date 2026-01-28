import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { RefreshCw, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useFilters } from "@/contexts/FilterContext";

const PAGE_TITLES: Record<string, string> = {
  "/": "AI Command Center",
  "/consumption": "AI Command Center",
};

export const TopNavigation = () => {
  const location = useLocation();
  const [currentTime, setCurrentTime] = useState(new Date());
  const { lastRefresh, triggerRefresh, isRefreshing } = useFilters();

  const subtitle = PAGE_TITLES[location.pathname] ?? PAGE_TITLES["/"];
  const lastRefreshStr = lastRefresh.toLocaleString(undefined, {
    dateStyle: "short",
    timeStyle: "medium",
  });

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const navItems = [
    { path: "/", label: "Sales Forecasting" },
    { path: "/consumption", label: "Consumption Forecasting" },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-[72px] glass border-b border-border/50">
      <div className="h-full px-6 flex items-center justify-between max-w-[1920px] mx-auto">
        <div className="flex items-center gap-8">
          <Link to="/" className="flex items-center gap-3 group">
            <img src="/logo.png" alt="Woodland" className="h-16 w-auto object-contain" />
            <div className="flex flex-col">
              <span className="text-xs font-medium text-foreground">
                {subtitle}
              </span>
            </div>
          </Link>
          <nav className="hidden md:flex items-center gap-1 ml-4">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  location.pathname === item.path
                    ? "bg-primary/10 text-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 text-sm text-muted-foreground">
            <span>Last refreshed: {lastRefreshStr}</span>
          </div>
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-secondary/50">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium tabular-nums">
              {currentTime.toLocaleString(undefined, {
                dateStyle: "short",
                timeStyle: "medium",
              })}
            </span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={triggerRefresh}
            disabled={isRefreshing}
            className="gap-2"
          >
            <RefreshCw className={cn("w-4 h-4", isRefreshing && "animate-spin")} />
            <span className="hidden sm:inline">Refresh</span>
          </Button>
        </div>
      </div>
    </header>
  );
};

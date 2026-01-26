import { ReactNode } from "react";
import { TopNavigation } from "./TopNavigation";
import { FilterBar } from "./FilterBar";

interface DashboardLayoutProps {
  children: ReactNode;
  dashboard: "consumption" | "sales";
}

export const DashboardLayout = ({ children, dashboard }: DashboardLayoutProps) => {
  return (
    <div className="min-h-screen bg-background">
      <TopNavigation />
      <FilterBar dashboard={dashboard} />
      <main className="pt-32 pb-8 px-6 max-w-[1920px] mx-auto">
        {children}
      </main>
    </div>
  );
};

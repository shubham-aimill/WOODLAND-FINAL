import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { FilterProvider } from "@/contexts/FilterContext";
import ConsumptionDashboard from "./pages/ConsumptionDashboard";
import SalesDashboard from "./pages/SalesDashboard";
import NotFound from "./pages/NotFound";
import { ChatProvider } from "./components/floating-bot/ChatContext";
import { FloatingBot } from "./components/floating-bot/FloatingBot";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <FilterProvider>
        <ChatProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<ConsumptionDashboard />} />
              <Route path="/sales" element={<SalesDashboard />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>

          {/* Global floating assistant */}
          <FloatingBot />
        </ChatProvider>
      </FilterProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;

// import { createContext, useContext, useState, ReactNode, useCallback } from "react";

// export type DateRange = "last-7" | "last-30" | "last-90" | "ytd" | "custom";
// export type ViewMode = "daily" | "weekly" | "monthly";
// export type Channel = "all" | "retail" | "wholesale" | "ecommerce" | "direct";
// export type Store = "all" | "store-1" | "store-2" | "store-3" | "store-4" | "store-5";
// export type SKU = "all" | "sku-1" | "sku-2" | "sku-3" | "sku-4";
// export type RawMaterial = "all" | "rm-1" | "rm-2" | "rm-3" | "rm-4";
// export type Product = "all" | "prod-1" | "prod-2" | "prod-3" | "prod-4";
// export type Category = "all" | "Footwear" | "Apparel" | "Bags" | "Accessories";
// export type Aggregation = "daily" | "weekly";
// export type RollingWindow = "7" | "14" | "30";

// export interface FilterState {
//   dateRange: DateRange;
//   channel: Channel;
//   store: Store;
//   sku: SKU;
//   view: ViewMode;
//   rawMaterial: RawMaterial;
//   product: Product;
//   category: Category;
//   aggregation: Aggregation;
//   rollingWindow: RollingWindow;
// }

// export interface FilterContextType {
//   filters: FilterState;
//   setDateRange: (value: DateRange) => void;
//   setChannel: (value: Channel) => void;
//   setStore: (value: Store) => void;
//   setSku: (value: SKU) => void;
//   setView: (value: ViewMode) => void;
//   setRawMaterial: (value: RawMaterial) => void;
//   setProduct: (value: Product) => void;
//   setCategory: (value: Category) => void;
//   setAggregation: (value: Aggregation) => void;
//   setRollingWindow: (value: RollingWindow) => void;
//   resetFilters: () => void;
//   lastRefresh: Date;
//   triggerRefresh: () => void;
//   isRefreshing: boolean;
// }

// const defaultFilters: FilterState = {
//   dateRange: "last-30",
//   channel: "all",
//   store: "all",
//   sku: "all",
//   view: "daily",
//   rawMaterial: "all",
//   product: "all",
//   category: "all",
//   aggregation: "daily",
//   rollingWindow: "14",
// };

// const FilterContext = createContext<FilterContextType | undefined>(undefined);

// export const FilterProvider = ({ children }: { children: ReactNode }) => {
//   const [filters, setFilters] = useState<FilterState>(defaultFilters);
//   const [lastRefresh, setLastRefresh] = useState(new Date());
//   const [isRefreshing, setIsRefreshing] = useState(false);

//   const setDateRange = useCallback((value: DateRange) => {
//     setFilters((prev) => ({ ...prev, dateRange: value }));
//   }, []);

//   const setChannel = useCallback((value: Channel) => {
//     setFilters((prev) => ({ ...prev, channel: value }));
//   }, []);

//   const setStore = useCallback((value: Store) => {
//     setFilters((prev) => ({ ...prev, store: value }));
//   }, []);

//   const setSku = useCallback((value: SKU) => {
//     setFilters((prev) => ({ ...prev, sku: value }));
//   }, []);

//   const setView = useCallback((value: ViewMode) => {
//     setFilters((prev) => ({ ...prev, view: value }));
//   }, []);

//   const setRawMaterial = useCallback((value: RawMaterial) => {
//     setFilters((prev) => ({ ...prev, rawMaterial: value }));
//   }, []);

//   const setProduct = useCallback((value: Product) => {
//     setFilters((prev) => ({ ...prev, product: value }));
//   }, []);

//   const setCategory = useCallback((value: Category) => {
//     setFilters((prev) => ({ ...prev, category: value }));
//   }, []);

//   const setAggregation = useCallback((value: Aggregation) => {
//     setFilters((prev) => ({ ...prev, aggregation: value }));
//   }, []);

//   const setRollingWindow = useCallback((value: RollingWindow) => {
//     setFilters((prev) => ({ ...prev, rollingWindow: value }));
//   }, []);

//   const resetFilters = useCallback(() => {
//     setFilters(defaultFilters);
//   }, []);

//   const triggerRefresh = useCallback(() => {
//     setIsRefreshing(true);
//     setLastRefresh(new Date());
//     setTimeout(() => setIsRefreshing(false), 1500);
//   }, []);

//   return (
//     <FilterContext.Provider
//       value={{
//         filters,
//         setDateRange,
//         setChannel,
//         setStore,
//         setSku,
//         setView,
//         setRawMaterial,
//         setProduct,
//         setCategory,
//         setAggregation,
//         setRollingWindow,
//         resetFilters,
//         lastRefresh,
//         triggerRefresh,
//         isRefreshing,
//       }}
//     >
//       {children}
//     </FilterContext.Provider>
//   );
// };

// export const useFilters = (): FilterContextType => {
//   const context = useContext(FilterContext);
//   if (!context) {
//     throw new Error("useFilters must be used within a FilterProvider");
//   }
//   return context;
// };


































import { createContext, useContext, useState, ReactNode, useCallback } from "react";

/* =====================
   STRICT ENUM FILTERS
   (these are logic-driven, not data-driven)
   Forecast horizon: next 7 or 30 days from cutoff date (2025-12-31)
===================== */
export type DateRange = "next-7" | "next-30";  // Forecast horizon: 7 or 30 days
export type ViewMode = "daily" | "weekly" | "monthly";   // Daily view now available
export type Aggregation = "daily" | "weekly";            // Daily aggregation available
export type RollingWindow = "7" | "30";

/* =====================
   DATA-DRIVEN FILTERS
   (values come from backend datasets)
===================== */
export type Channel = string;       // e.g. "retail", "ecommerce"
export type Store = string;         // real store_id
export type SKU = string;           // real sku_id
export type RawMaterial = string;   // real raw_material name
export type Product = string;       // real product_name
export type Category = string;      // real category name

/* =====================
   FILTER STATE
===================== */
export interface FilterState {
  dateRange: DateRange;
  channel: Channel;
  store: Store;
  sku: SKU;
  view: ViewMode;
  rawMaterial: RawMaterial;
  product: Product;
  category: Category;
  aggregation: Aggregation;
  rollingWindow: RollingWindow;
}

/* =====================
   CONTEXT TYPE
===================== */
export interface FilterContextType {
  filters: FilterState;

  setDateRange: (value: DateRange) => void;
  setChannel: (value: Channel) => void;
  setStore: (value: Store) => void;
  setSku: (value: SKU) => void;
  setView: (value: ViewMode) => void;
  setRawMaterial: (value: RawMaterial) => void;
  setProduct: (value: Product) => void;
  setCategory: (value: Category) => void;
  setAggregation: (value: Aggregation) => void;
  setRollingWindow: (value: RollingWindow) => void;

  resetFilters: () => void;
  lastRefresh: Date;
  triggerRefresh: () => void;
  isRefreshing: boolean;
}

/* =====================
   DEFAULT FILTERS
   "all" remains a valid semantic value
   Shows 30-day forecast horizon by default with daily granularity
===================== */
const defaultFilters: FilterState = {
  dateRange: "next-30",     // Default: 30-day forecast horizon
  channel: "all",
  store: "all",
  sku: "all",
  view: "daily",            // Daily view now available
  rawMaterial: "all",
  product: "all",
  category: "all",
  aggregation: "daily",     // Daily aggregation now available
  rollingWindow: "7",
};

const FilterContext = createContext<FilterContextType | undefined>(undefined);

/* =====================
   PROVIDER
===================== */
export const FilterProvider = ({ children }: { children: ReactNode }) => {
  const [filters, setFilters] = useState<FilterState>(defaultFilters);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);

  const setDateRange = useCallback((value: DateRange) => {
    setFilters((prev) => ({ ...prev, dateRange: value }));
  }, []);

  const setChannel = useCallback((value: Channel) => {
    setFilters((prev) => ({ ...prev, channel: value }));
  }, []);

  const setStore = useCallback((value: Store) => {
    setFilters((prev) => ({ ...prev, store: value }));
  }, []);

  const setSku = useCallback((value: SKU) => {
    setFilters((prev) => ({ ...prev, sku: value }));
  }, []);

  const setView = useCallback((value: ViewMode) => {
    setFilters((prev) => ({ ...prev, view: value }));
  }, []);

  const setRawMaterial = useCallback((value: RawMaterial) => {
    setFilters((prev) => ({ ...prev, rawMaterial: value }));
  }, []);

  const setProduct = useCallback((value: Product) => {
    setFilters((prev) => ({ ...prev, product: value }));
  }, []);

  const setCategory = useCallback((value: Category) => {
    setFilters((prev) => ({ ...prev, category: value }));
  }, []);

  const setAggregation = useCallback((value: Aggregation) => {
    setFilters((prev) => ({ ...prev, aggregation: value }));
  }, []);

  const setRollingWindow = useCallback((value: RollingWindow) => {
    setFilters((prev) => ({ ...prev, rollingWindow: value }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(defaultFilters);
  }, []);

  const triggerRefresh = useCallback(() => {
    setIsRefreshing(true);
    setLastRefresh(new Date());
    setTimeout(() => setIsRefreshing(false), 1500);
  }, []);

  return (
    <FilterContext.Provider
      value={{
        filters,
        setDateRange,
        setChannel,
        setStore,
        setSku,
        setView,
        setRawMaterial,
        setProduct,
        setCategory,
        setAggregation,
        setRollingWindow,
        resetFilters,
        lastRefresh,
        triggerRefresh,
        isRefreshing,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
};

/* =====================
   HOOK
===================== */
export const useFilters = (): FilterContextType => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error("useFilters must be used within a FilterProvider");
  }
  return context;
};
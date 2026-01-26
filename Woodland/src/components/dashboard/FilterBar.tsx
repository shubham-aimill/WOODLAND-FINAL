// import { Calendar, Building2, Store, Package, Layers, Tag, BarChart3 } from "lucide-react";
// import {
//   Select,
//   SelectContent,
//   SelectItem,
//   SelectTrigger,
//   SelectValue,
// } from "@/components/ui/select";
// import { Button } from "@/components/ui/button";
// import { cn } from "@/lib/utils";
// import {
//   useFilters,
//   DateRange,
//   Channel,
//   Store as StoreType,
//   SKU,
//   ViewMode,
//   RawMaterial,
//   Product,
//   Category,
//   Aggregation,
// } from "@/contexts/FilterContext";

// const filterClass = cn(
//   "bg-background border border-border hover:border-primary/50 focus:ring-primary/20",
//   "transition-all duration-200"
// );

// const RAW_MATERIAL_OPTIONS: { value: RawMaterial; label: string }[] = [
//   { value: "all", label: "All Raw Materials" },
//   { value: "rm-1", label: "Full-Grain Leather" },
//   { value: "rm-2", label: "Suede" },
//   { value: "rm-3", label: "Nubuck" },
//   { value: "rm-4", label: "Leather Lining" },
// ];

// const PRODUCT_OPTIONS: { value: Product; label: string }[] = [
//   { value: "all", label: "All Products" },
//   { value: "prod-1", label: "Heritage Boot" },
//   { value: "prod-2", label: "Rancher Jacket" },
//   { value: "prod-3", label: "Trail Backpack" },
//   { value: "prod-4", label: "Classic Belt" },
// ];

// const CATEGORY_OPTIONS: { value: Category; label: string }[] = [
//   { value: "all", label: "All Categories" },
//   { value: "Footwear", label: "Footwear" },
//   { value: "Apparel", label: "Apparel" },
//   { value: "Bags", label: "Bags" },
//   { value: "Accessories", label: "Accessories" },
// ];

// interface FilterBarProps {
//   dashboard: "consumption" | "sales";
// }

// export const FilterBar = ({ dashboard }: FilterBarProps) => {
//   const {
//     filters,
//     setDateRange,
//     setChannel,
//     setStore,
//     setSku,
//     setView,
//     setRawMaterial,
//     setProduct,
//     setCategory,
//     setAggregation,
//   } = useFilters();

//   const isConsumption = dashboard === "consumption";

//   return (
//     <div className="sticky top-[72px] z-40 bg-background/95 backdrop-blur-sm border-b border-border/50 py-4">
//       <div className="px-6 max-w-[1920px] mx-auto">
//         <div className="flex flex-wrap items-center gap-3">
//           <div className="flex items-center gap-2">
//             <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
//               <Calendar className="w-4 h-4 text-primary" />
//             </div>
//             <Select value={filters.dateRange} onValueChange={(v) => setDateRange(v as DateRange)}>
//               <SelectTrigger className={cn(filterClass, "w-[160px]")}>
//                 <SelectValue placeholder="Date Range" />
//               </SelectTrigger>
//               <SelectContent>
//                 <SelectItem value="last-7">Last 7 Days</SelectItem>
//                 <SelectItem value="last-30">Last 30 Days</SelectItem>
//                 <SelectItem value="last-90">Last 90 Days</SelectItem>
//                 <SelectItem value="ytd">Year to Date</SelectItem>
//                 <SelectItem value="custom">Custom Range</SelectItem>
//               </SelectContent>
//             </Select>
//           </div>

//           <div className="flex items-center gap-2">
//             <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
//               <Building2 className="w-4 h-4 text-primary" />
//             </div>
//             <Select value={filters.channel} onValueChange={(v) => setChannel(v as Channel)}>
//               <SelectTrigger className={cn(filterClass, "w-[150px]")}>
//                 <SelectValue placeholder="Channel" />
//               </SelectTrigger>
//               <SelectContent>
//                 <SelectItem value="all">All Channels</SelectItem>
//                 <SelectItem value="retail">Retail</SelectItem>
//                 <SelectItem value="wholesale">Wholesale</SelectItem>
//                 <SelectItem value="ecommerce">E-Commerce</SelectItem>
//                 <SelectItem value="direct">Direct Sales</SelectItem>
//               </SelectContent>
//             </Select>
//           </div>

//           {isConsumption ? (
//             <>
//               <div className="flex items-center gap-2">
//                 <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
//                   <Layers className="w-4 h-4 text-primary" />
//                 </div>
//                 <Select value={filters.rawMaterial} onValueChange={(v) => setRawMaterial(v as RawMaterial)}>
//                   <SelectTrigger className={cn(filterClass, "w-[180px]")}>
//                     <SelectValue placeholder="Raw Material" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     {RAW_MATERIAL_OPTIONS.map((o) => (
//                       <SelectItem key={o.value} value={o.value}>
//                         {o.label}
//                       </SelectItem>
//                     ))}
//                   </SelectContent>
//                 </Select>
//               </div>
//               <div className="flex items-center gap-2">
//                 <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
//                   <Package className="w-4 h-4 text-primary" />
//                 </div>
//                 <Select value={filters.product} onValueChange={(v) => setProduct(v as Product)}>
//                   <SelectTrigger className={cn(filterClass, "w-[160px]")}>
//                     <SelectValue placeholder="Product" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     {PRODUCT_OPTIONS.map((o) => (
//                       <SelectItem key={o.value} value={o.value}>
//                         {o.label}
//                       </SelectItem>
//                     ))}
//                   </SelectContent>
//                 </Select>
//               </div>
//               <div className="flex items-center gap-2">
//                 <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
//                   <BarChart3 className="w-4 h-4 text-primary" />
//                 </div>
//                 <div className="flex rounded-lg border border-border bg-secondary/30 p-0.5">
//                   {(["daily", "weekly"] as Aggregation[]).map((v) => (
//                     <Button
//                       key={v}
//                       variant="ghost"
//                       size="sm"
//                       onClick={() => setAggregation(v)}
//                       className={cn(
//                         "capitalize text-xs px-3 h-7 rounded-md transition-all",
//                         filters.aggregation === v
//                           ? "bg-primary text-primary-foreground shadow-sm"
//                           : "text-muted-foreground hover:text-foreground"
//                       )}
//                     >
//                       {v}
//                     </Button>
//                   ))}
//                 </div>
//               </div>
//             </>
//           ) : (
//             <>
//               <div className="flex items-center gap-2">
//                 <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
//                   <Package className="w-4 h-4 text-primary" />
//                 </div>
//                 <Select value={filters.sku} onValueChange={(v) => setSku(v as SKU)}>
//                   <SelectTrigger className={cn(filterClass, "w-[150px]")}>
//                     <SelectValue placeholder="SKU" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     <SelectItem value="all">All SKUs</SelectItem>
//                     <SelectItem value="sku-1">WL-BOOT-001</SelectItem>
//                     <SelectItem value="sku-2">WL-JACK-002</SelectItem>
//                     <SelectItem value="sku-3">WL-BAG-003</SelectItem>
//                     <SelectItem value="sku-4">WL-BELT-004</SelectItem>
//                   </SelectContent>
//                 </Select>
//               </div>
//               <div className="flex items-center gap-2">
//                 <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
//                   <Store className="w-4 h-4 text-primary" />
//                 </div>
//                 <Select value={filters.store} onValueChange={(v) => setStore(v as StoreType)}>
//                   <SelectTrigger className={cn(filterClass, "w-[150px]")}>
//                     <SelectValue placeholder="Store" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     <SelectItem value="all">All Stores</SelectItem>
//                     <SelectItem value="store-1">NYC Flagship</SelectItem>
//                     <SelectItem value="store-2">LA Downtown</SelectItem>
//                     <SelectItem value="store-3">Chicago Main</SelectItem>
//                     <SelectItem value="store-4">Miami Beach</SelectItem>
//                     <SelectItem value="store-5">Seattle Pike</SelectItem>
//                   </SelectContent>
//                 </Select>
//               </div>
//               <div className="flex items-center gap-2">
//                 <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
//                   <Tag className="w-4 h-4 text-primary" />
//                 </div>
//                 <Select value={filters.category} onValueChange={(v) => setCategory(v as Category)}>
//                   <SelectTrigger className={cn(filterClass, "w-[150px]")}>
//                     <SelectValue placeholder="Category" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     {CATEGORY_OPTIONS.map((o) => (
//                       <SelectItem key={o.value} value={o.value}>
//                         {o.label}
//                       </SelectItem>
//                     ))}
//                   </SelectContent>
//                 </Select>
//               </div>
//               <div className="flex items-center gap-2">
//                 <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
//                   <BarChart3 className="w-4 h-4 text-primary" />
//                 </div>
//                 <div className="flex rounded-lg border border-border bg-secondary/30 p-0.5">
//                   {(["daily", "weekly", "monthly"] as ViewMode[]).map((v) => (
//                     <Button
//                       key={v}
//                       variant="ghost"
//                       size="sm"
//                       onClick={() => setView(v)}
//                       className={cn(
//                         "capitalize text-xs px-3 h-7 rounded-md transition-all",
//                         filters.view === v
//                           ? "bg-primary text-primary-foreground shadow-sm"
//                           : "text-muted-foreground hover:text-foreground"
//                       )}
//                     >
//                       {v}
//                     </Button>
//                   ))}
//                 </div>
//               </div>
//             </>
//           )}

//           <div className="flex-1" />
//         </div>
//       </div>
//     </div>
//   );
// };



























import { Calendar, Building2, Store, Package, Layers, Tag, BarChart3 } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  useFilters,
  DateRange,
  ViewMode,
  Aggregation,
} from "@/contexts/FilterContext";
import { useEffect, useState, useRef } from "react";

/* =========================
   TYPES FOR METADATA
========================= */
interface FilterMetadata {
  channels: string[];
  stores: string[];
  skus: string[];
  products: string[];
  categories: string[];
  rawMaterials: string[];
}

/* =========================
   FETCH FILTER METADATA
========================= */
async function fetchFilterMetadata(): Promise<FilterMetadata> {
  const res = await fetch("/api/filters");
  if (!res.ok) throw new Error("Failed to load filters");
  return res.json();
}

const filterClass = cn(
  "bg-background border border-border hover:border-primary/50 focus:ring-primary/20",
  "transition-all duration-200"
);

interface FilterBarProps {
  dashboard: "consumption" | "sales";
}

export const FilterBar = ({ dashboard }: FilterBarProps) => {
  const {
    filters,
    setDateRange,
    setChannel,
    setStore,
    setSku,
    setView,
    setRawMaterial,
    setProduct,
    setCategory,
  } = useFilters();

  const [metadata, setMetadata] = useState<FilterMetadata | null>(null);
  const [dynamicRawMaterials, setDynamicRawMaterials] = useState<string[]>(["all"]); // Initialize with "all"
  const [dynamicSkus, setDynamicSkus] = useState<string[]>(["all"]); // For sales dashboard: SKUs filtered by category
  const [dynamicStores, setDynamicStores] = useState<string[]>(["all"]); // For sales dashboard: Stores filtered by SKU

  useEffect(() => {
    fetchFilterMetadata()
      .then((data) => {
        setMetadata(data);
        // Initialize dynamic filters with all values from metadata
        if (data) {
          setDynamicSkus(["all", ...(data.skus ?? [])]);
          setDynamicStores(["all", ...(data.stores ?? [])]);
        }
      })
      .catch(() => setMetadata(null));
  }, []);

  // Fetch raw materials dynamically based on selected product
  useEffect(() => {
    if (!metadata) {
      // Wait for metadata to load first
      return;
    }

    if (dashboard === "consumption" && filters.product && filters.product !== "all") {
      const url = `/api/filters/rawMaterials?product=${encodeURIComponent(filters.product)}`;
      
      fetch(url)
        .then(res => res.json())
        .then(data => {
          const rawMaterials = data.rawMaterials || [];
          const rawMaterialList = ["all", ...rawMaterials];
          setDynamicRawMaterials(rawMaterialList);
        })
        .catch((err) => {
          console.error("Failed to fetch filtered raw materials:", err);
          // Fallback to all raw materials if API fails
          setDynamicRawMaterials(["all", ...(metadata?.rawMaterials ?? [])]);
        });
    } else {
      // For sales dashboard or no product filter, use all raw materials
      setDynamicRawMaterials(["all", ...(metadata?.rawMaterials ?? [])]);
    }
  }, [filters.product, metadata, dashboard]);

  // Fetch SKUs dynamically based on selected category (for sales dashboard)
  useEffect(() => {
    if (!metadata) {
      return;
    }

    if (dashboard === "sales") {
      if (filters.category && filters.category !== "all") {
        const url = `/api/filters/skus?category=${encodeURIComponent(filters.category)}`;
        
        fetch(url)
          .then(res => res.json())
          .then(data => {
            const skus = data.skus || [];
            const skuList = ["all", ...skus];
            setDynamicSkus(skuList);
          })
          .catch((err) => {
            console.error("Failed to fetch filtered SKUs:", err);
            // Fallback to all SKUs if API fails
            setDynamicSkus(["all", ...(metadata?.skus ?? [])]);
          });
      } else {
        // Category is "all" or not set, show all SKUs
        setDynamicSkus(["all", ...(metadata?.skus ?? [])]);
      }
    } else {
      // For consumption dashboard, use all SKUs
      setDynamicSkus(["all", ...(metadata?.skus ?? [])]);
    }
  }, [filters.category, metadata, dashboard]);

  // Fetch stores dynamically based on selected SKU (for sales dashboard)
  useEffect(() => {
    if (!metadata) {
      return;
    }

    if (dashboard === "sales") {
      if (filters.sku && filters.sku !== "all") {
        const url = `/api/filters/stores?sku=${encodeURIComponent(filters.sku)}`;
        
        fetch(url)
          .then(res => res.json())
          .then(data => {
            const stores = data.stores || [];
            const storeList = ["all", ...stores];
            setDynamicStores(storeList);
          })
          .catch((err) => {
            console.error("Failed to fetch filtered stores:", err);
            // Fallback to all stores if API fails
            setDynamicStores(["all", ...(metadata?.stores ?? [])]);
          });
      } else {
        // SKU is "all" or not set, show all stores
        setDynamicStores(["all", ...(metadata?.stores ?? [])]);
      }
    } else {
      // For consumption dashboard, use all stores
      setDynamicStores(["all", ...(metadata?.stores ?? [])]);
    }
  }, [filters.sku, metadata, dashboard]);

  // Reset raw material ONLY when product changes (not when raw material is manually selected)
  const prevProductRef = useRef<string | undefined>(undefined);
  
  useEffect(() => {
    // Skip on initial mount
    if (prevProductRef.current === undefined) {
      prevProductRef.current = filters.product;
      return;
    }
    
    // Only reset if product actually changed AND raw material is not valid for new product
    if (dashboard === "consumption" && 
        filters.product && 
        filters.product !== "all" && 
        filters.rawMaterial !== "all" &&
        dynamicRawMaterials.length > 1 &&
        prevProductRef.current !== filters.product &&
        prevProductRef.current !== undefined) {
      // Check if current raw material is in the filtered list (excluding "all")
      const validRawMaterials = dynamicRawMaterials.slice(1); // Remove "all"
      if (!validRawMaterials.includes(filters.rawMaterial)) {
        console.log("[FilterBar] Product changed from", prevProductRef.current, "to", filters.product);
        console.log("[FilterBar] Current raw material", filters.rawMaterial, "not in valid raw materials:", validRawMaterials);
        console.log("[FilterBar] Resetting raw material to 'all'");
        setRawMaterial("all");
      } else {
        console.log("[FilterBar] Product changed but raw material", filters.rawMaterial, "is still valid - keeping it");
      }
    }
    prevProductRef.current = filters.product;
  }, [filters.product, dynamicRawMaterials, dashboard, setRawMaterial, filters.rawMaterial]);

  // Reset SKU when category changes (for sales dashboard)
  const prevCategoryRef = useRef<string | undefined>(undefined);
  
  useEffect(() => {
    // Skip on initial mount
    if (prevCategoryRef.current === undefined) {
      prevCategoryRef.current = filters.category;
      return;
    }
    
    // Only reset if category actually changed AND SKU is not valid for new category
    if (dashboard === "sales" && 
        filters.category && 
        filters.category !== "all" && 
        filters.sku !== "all" &&
        dynamicSkus.length > 1 &&
        prevCategoryRef.current !== filters.category &&
        prevCategoryRef.current !== undefined) {
      // Check if current SKU is in the filtered list (excluding "all")
      const validSkus = dynamicSkus.slice(1); // Remove "all"
      if (!validSkus.includes(filters.sku)) {
        console.log("[FilterBar] Category changed from", prevCategoryRef.current, "to", filters.category);
        console.log("[FilterBar] Current SKU", filters.sku, "not in valid SKUs:", validSkus);
        console.log("[FilterBar] Resetting SKU to 'all'");
        setSku("all");
      } else {
        console.log("[FilterBar] Category changed but SKU", filters.sku, "is still valid - keeping it");
      }
    }
    prevCategoryRef.current = filters.category;
  }, [filters.category, dynamicSkus, dashboard, setSku, filters.sku]);

  // Reset Store when SKU changes (for sales dashboard)
  const prevSkuRef = useRef<string | undefined>(undefined);
  
  useEffect(() => {
    // Skip on initial mount
    if (prevSkuRef.current === undefined) {
      prevSkuRef.current = filters.sku;
      return;
    }
    
    // Only reset if SKU actually changed AND store is not valid for new SKU
    if (dashboard === "sales" && 
        filters.sku && 
        filters.sku !== "all" && 
        filters.store !== "all" &&
        dynamicStores.length > 1 &&
        prevSkuRef.current !== filters.sku &&
        prevSkuRef.current !== undefined) {
      // Check if current store is in the filtered list (excluding "all")
      const validStores = dynamicStores.slice(1); // Remove "all"
      if (!validStores.includes(filters.store)) {
        console.log("[FilterBar] SKU changed from", prevSkuRef.current, "to", filters.sku);
        console.log("[FilterBar] Current store", filters.store, "not in valid stores:", validStores);
        console.log("[FilterBar] Resetting store to 'all'");
        setStore("all");
      } else {
        console.log("[FilterBar] SKU changed but store", filters.store, "is still valid - keeping it");
      }
    }
    prevSkuRef.current = filters.sku;
  }, [filters.sku, dynamicStores, dashboard, setStore, filters.store]);

  const isConsumption = dashboard === "consumption";

  /* =========================
     NORMALIZED OPTIONS (KEY FIX)
  ========================= */
  const channels = ["all", ...(metadata?.channels ?? [])];
  // Use all products from metadata (no dynamic filtering based on raw material anymore)
  const products = metadata?.products 
    ? ["all", ...metadata.products]
    : ["all"];
  // Use dynamic raw materials if available, otherwise fall back to metadata raw materials
  // If neither is available, show at least "all" option
  const rawMaterials = dynamicRawMaterials.length > 1 
    ? dynamicRawMaterials 
    : metadata?.rawMaterials 
      ? ["all", ...metadata.rawMaterials]
      : ["all"];
  // For sales dashboard: use dynamic stores and SKUs based on cascading filters
  // For consumption dashboard: use all stores and SKUs from metadata
  const stores = dashboard === "sales" && dynamicStores.length > 1 
    ? dynamicStores 
    : ["all", ...(metadata?.stores ?? [])];
  const skus = dashboard === "sales" && dynamicSkus.length > 1 
    ? dynamicSkus 
    : ["all", ...(metadata?.skus ?? [])];
  const categories = ["all", ...(metadata?.categories ?? [])];


  const disabled = !metadata;


  return (
    <div className="sticky top-[72px] z-40 bg-background/95 backdrop-blur-sm border-b border-border/50 py-4">
      <div className="px-6 max-w-[1920px] mx-auto">
        <div className="flex flex-wrap items-center gap-3">

          {/* ================= FORECAST HORIZON ================= */}
          {/* Forecast horizon: Next 7 or 30 days from cutoff date */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Calendar className="w-4 h-4 text-primary" />
            </div>
            <Select value={filters.dateRange} onValueChange={(v) => setDateRange(v as DateRange)}>
              <SelectTrigger className={cn(filterClass, "w-[180px]")}>
                <SelectValue placeholder="Forecast Horizon" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="next-7">Next 7 Days Forecast</SelectItem>
                <SelectItem value="next-30">Next 30 Days Forecast</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* ================= CHANNEL ================= */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Building2 className="w-4 h-4 text-primary" />
            </div>
            <Select value={filters.channel} onValueChange={setChannel}>
              <SelectTrigger className={cn(filterClass, "w-[150px]")}>
                <SelectValue placeholder="Channel" />
              </SelectTrigger>
              <SelectContent>
                {channels.map((c) => (
                  <SelectItem key={c} value={c}>
                    {c === "all" ? "All Channels" : c}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {isConsumption ? (
            <>
              {/* ================= PRODUCT ================= */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Package className="w-4 h-4 text-primary" />
                </div>
                <Select 
                  value={filters.product} 
                  onValueChange={(value) => {
                    // Always set the product - this will trigger raw material filtering
                    setProduct(value);
                  }}
                >
                  <SelectTrigger className={cn(filterClass, "w-[160px]")}>
                    <SelectValue placeholder="Product" />
                  </SelectTrigger>
                  <SelectContent>
                    {products.length === 0 || (products.length === 1 && products[0] === "all") ? (
                      <SelectItem value="all" disabled>Loading...</SelectItem>
                    ) : (
                      products.map((p) => (
                        <SelectItem key={p} value={p}>
                          {p === "all" ? "All Products" : p}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>

              {/* ================= RAW MATERIAL ================= */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Layers className="w-4 h-4 text-primary" />
                </div>
                <Select value={filters.rawMaterial} onValueChange={setRawMaterial}>
                  <SelectTrigger className={cn(filterClass, "w-[180px]")}>
                    <SelectValue placeholder="Raw Material" />
                  </SelectTrigger>
                  <SelectContent>
                    {rawMaterials.length === 0 || (rawMaterials.length === 1 && rawMaterials[0] === "all") ? (
                      <SelectItem value="all" disabled>Loading...</SelectItem>
                    ) : (
                      rawMaterials.map((rm) => (
                        <SelectItem key={rm} value={rm}>
                          {rm === "all" ? "All Raw Materials" : rm.replace(/_/g, " ")}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>

            </>
          ) : (
            <>
              {/* ================= CATEGORY (First) ================= */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Tag className="w-4 h-4 text-primary" />
                </div>
                <Select 
                  value={filters.category} 
                  onValueChange={(value) => {
                    setCategory(value);
                    // Category change will trigger SKU filtering via useEffect
                  }}
                >
                  <SelectTrigger className={cn(filterClass, "w-[150px]")}>
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((c) => (
                      <SelectItem key={c} value={c}>
                        {c === "all" ? "All Categories" : c}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* ================= SKU (Second - filtered by Category) ================= */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Package className="w-4 h-4 text-primary" />
                </div>
                <Select 
                  value={filters.sku} 
                  onValueChange={(value) => {
                    setSku(value);
                    // SKU change will trigger Store filtering via useEffect
                  }}
                >
                  <SelectTrigger className={cn(filterClass, "w-[150px]")}>
                    <SelectValue placeholder="SKU" />
                  </SelectTrigger>
                  <SelectContent>
                    {skus.length === 0 || (skus.length === 1 && skus[0] === "all") ? (
                      <SelectItem value="all" disabled>Loading...</SelectItem>
                    ) : (
                      skus.map((sku) => (
                        <SelectItem key={sku} value={sku}>
                          {sku === "all" ? "All SKUs" : sku}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>

              {/* ================= STORE (Third - filtered by SKU) ================= */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Store className="w-4 h-4 text-primary" />
                </div>
                <Select value={filters.store} onValueChange={setStore}>
                  <SelectTrigger className={cn(filterClass, "w-[150px]")}>
                    <SelectValue placeholder="Store" />
                  </SelectTrigger>
                  <SelectContent>
                    {stores.length === 0 || (stores.length === 1 && stores[0] === "all") ? (
                      <SelectItem value="all" disabled>Loading...</SelectItem>
                    ) : (
                      stores.map((s) => (
                        <SelectItem key={s} value={s}>
                          {s === "all" ? "All Stores" : s}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>
            </>
          )}

          <div className="flex-1" />
        </div>
      </div>
    </div>
  );
};
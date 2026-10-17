const rawBase = import.meta.env.VITE_API_BASE ?? "http://localhost:8004";

export const API_ORIGIN = rawBase.replace(/\/+$/, "");
export const API_PREFIX = "/api/v1";

export type ProductsSource = "mock" | "local" | "api";

const rawSource = import.meta.env.VITE_PRODUCTS_SOURCE;

export const PRODUCTS_SOURCE: ProductsSource =
  rawSource === "api" ? "api" : rawSource === "mock" ? "mock" : "local";

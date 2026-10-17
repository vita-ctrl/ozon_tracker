import { http } from "./client";
import type { AddProductInput, PricePoint, Product } from "../types/api";

export type ProductPatch = Partial<Pick<Product, "note" | "notificationThreshold">>;

export async function listProducts(): Promise<Product[]> {
  const { data } = await http.get<Product[]>("/products");
  return data;
}

export async function getProduct(id: string): Promise<Product> {
  const { data } = await http.get<Product>(`/products/${encodeURIComponent(id)}`);
  return data;
}

export async function addProduct(input: AddProductInput): Promise<Product> {
  const { data } = await http.post<Product>("/products", input);
  return data;
}

export async function updateProduct(id: string, patch: ProductPatch): Promise<Product> {
  const { data } = await http.patch<Product>(
    `/products/${encodeURIComponent(id)}`,
    patch,
  );
  return data;
}

export async function removeProduct(id: string): Promise<void> {
  await http.delete(`/products/${encodeURIComponent(id)}`);
}

export async function getProductHistory(id: string): Promise<PricePoint[]> {
  const { data } = await http.get<PricePoint[]>(
    `/products/${encodeURIComponent(id)}/history`,
  );
  return data;
}

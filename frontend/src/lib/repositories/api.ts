import * as productsApi from "../api/products";
import type { ProductPatch } from "../api/products";
import type { AddProductInput, Product, ProductPreview } from "../types/api";
import type { ProductRepository } from "./types";

export class ApiProductRepository implements ProductRepository {
  list(): Promise<Product[]> {
    return productsApi.listProducts();
  }

  async get(id: string): Promise<Product | null> {
    try {
      return await productsApi.getProduct(id);
    } catch {
      return null;
    }
  }

  add(input: AddProductInput): Promise<Product> {
    return productsApi.addProduct(input);
  }

  update(id: string, patch: ProductPatch): Promise<Product> {
    return productsApi.updateProduct(id, patch);
  }

  remove(id: string): Promise<void> {
    return productsApi.removeProduct(id);
  }

  async preview(url: string): Promise<ProductPreview> {
    // The preview endpoint is not implemented yet. This is the single place
    // to swap for a real request once the backend exposes it.
    return {
      title: url,
      imageUrl: null,
      price: 0,
      currency: "KZT",
      availability: "in_stock",
    };
  }
}

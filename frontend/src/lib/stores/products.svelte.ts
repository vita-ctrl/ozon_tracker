import { getErrorMessage } from "../api/client";
import { productRepository } from "../repositories";
import type { ProductPatch } from "../api/products";
import type { AddProductInput, Product } from "../types/api";

export type ProductSort = "added" | "price_asc" | "price_desc" | "changed";

export const SORT_LABELS: Record<ProductSort, string> = {
  added: "По дате",
  changed: "По изменению",
  price_asc: "Цена ↑",
  price_desc: "Цена ↓",
};

class ProductsStore {
  items = $state<Product[]>([]);
  loading = $state(false);
  error = $state<string | null>(null);
  sort = $state<ProductSort>("added");
  private loaded = false;

  sorted = $derived.by(() => {
    const list = [...this.items];
    switch (this.sort) {
      case "price_asc":
        return list.sort((a, b) => a.currentPrice - b.currentPrice);
      case "price_desc":
        return list.sort((a, b) => b.currentPrice - a.currentPrice);
      case "changed":
        return list.sort(
          (a, b) => Math.abs(b.change24hPercent ?? 0) - Math.abs(a.change24hPercent ?? 0),
        );
      default:
        return list.sort(
          (a, b) => new Date(b.addedAt).getTime() - new Date(a.addedAt).getTime(),
        );
    }
  });

  async load(force = false): Promise<void> {
    if (this.loaded && !force) return;
    this.loading = true;
    this.error = null;
    try {
      this.items = await productRepository.list();
      this.loaded = true;
    } catch (error) {
      this.error = getErrorMessage(error);
    } finally {
      this.loading = false;
    }
  }

  get(id: string): Product | undefined {
    return this.items.find((product) => product.id === id);
  }

  async add(input: AddProductInput): Promise<Product> {
    const product = await productRepository.add(input);
    this.items = [product, ...this.items];
    return product;
  }

  async update(id: string, patch: ProductPatch): Promise<void> {
    const product = await productRepository.update(id, patch);
    this.items = this.items.map((item) => (item.id === id ? product : item));
  }

  async remove(id: string): Promise<void> {
    await productRepository.remove(id);
    this.items = this.items.filter((item) => item.id !== id);
  }

  preview(url: string) {
    return productRepository.preview(url);
  }
}

export const productsStore = new ProductsStore();

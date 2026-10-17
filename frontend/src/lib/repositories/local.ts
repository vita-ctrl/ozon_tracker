import { fetchParserProduct, parserProductToPreview } from "../api/parser";
import type { ProductPatch } from "../api/products";
import type { AddProductInput, Product, ProductPreview } from "../types/api";
import type { ProductRepository } from "./types";

const STORAGE_KEY = "ozon_tracker.local_products";

function load(): Product[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw) as Product[];
    }
  } catch {
    // corrupted or unavailable storage — start empty
  }
  return [];
}

function save(products: Product[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
  } catch {
    // storage unavailable (private mode) — keep state in memory only
  }
}

function delay(ms = 250): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class LocalProductRepository implements ProductRepository {
  private products: Product[] = load();

  async list(): Promise<Product[]> {
    await delay();
    return [...this.products];
  }

  async get(id: string): Promise<Product | null> {
    await delay();
    return this.products.find((product) => product.id === id) ?? null;
  }

  async add(input: AddProductInput): Promise<Product> {
    const data = await fetchParserProduct(input.url);
    const preview = parserProductToPreview(data);
    const now = new Date().toISOString();
    const id = data.sku ? `local-${data.sku}` : `local-${Date.now()}`;

    const product: Product = {
      id,
      title: preview.title,
      url: input.url,
      imageUrl: preview.imageUrl,
      note: input.note ?? null,
      currentPrice: preview.price,
      currency: preview.currency,
      availability: preview.availability,
      change24hPercent: null,
      addedAt: now,
      notificationThreshold: input.notificationThreshold ?? null,
      priceHistory: [{ at: now, price: preview.price }],
      changes: [],
    };

    this.products = [product, ...this.products.filter((item) => item.id !== id)];
    save(this.products);
    return product;
  }

  async update(id: string, patch: ProductPatch): Promise<Product> {
    await delay();
    const index = this.products.findIndex((product) => product.id === id);
    if (index === -1) {
      throw new Error("Товар не найден");
    }
    const updated: Product = { ...this.products[index], ...patch };
    this.products = this.products.map((product, i) => (i === index ? updated : product));
    save(this.products);
    return updated;
  }

  async remove(id: string): Promise<void> {
    await delay();
    this.products = this.products.filter((product) => product.id !== id);
    save(this.products);
  }

  async preview(url: string): Promise<ProductPreview> {
    const data = await fetchParserProduct(url);
    return parserProductToPreview(data);
  }
}

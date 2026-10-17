import type {
  AddProductInput,
  Product,
  ProductPreview,
} from "../types/api";
import type { ProductPatch } from "../api/products";

export interface ProductRepository {
  list(): Promise<Product[]>;
  get(id: string): Promise<Product | null>;
  add(input: AddProductInput): Promise<Product>;
  update(id: string, patch: ProductPatch): Promise<Product>;
  remove(id: string): Promise<void>;
  preview(url: string): Promise<ProductPreview>;
}

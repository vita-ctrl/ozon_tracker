import { PRODUCTS_SOURCE } from "../config";
import { ApiProductRepository } from "./api";
import { LocalProductRepository } from "./local";
import { MockProductRepository } from "./mock";
import type { ProductRepository } from "./types";

function createRepository(): ProductRepository {
  switch (PRODUCTS_SOURCE) {
    case "api":
      return new ApiProductRepository();
    case "mock":
      return new MockProductRepository();
    default:
      return new LocalProductRepository();
  }
}

export const productRepository: ProductRepository = createRepository();

export type { ProductRepository } from "./types";
export type { ProductPatch } from "../api/products";

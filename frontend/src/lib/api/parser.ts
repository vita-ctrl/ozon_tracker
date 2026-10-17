import { http } from "./client";
import type { ParserProduct, ProductPreview } from "../types/api";

/**
 * The parser can take a while (it may need to warm up cookies / drive a real
 * browser), and nginx keeps the connection open up to 90s, so we match that.
 */
const PARSER_TIMEOUT = 90_000;

export async function fetchParserProduct(
  url: string,
  currency?: string,
): Promise<ParserProduct> {
  const { data } = await http.get<ParserProduct>("/products/", {
    params: { url, ...(currency ? { currency } : {}) },
    timeout: PARSER_TIMEOUT,
  });
  return data;
}

export function parserProductToPreview(data: ParserProduct): ProductPreview {
  const inStock = data.product_type === "in_stock";
  return {
    title: data.title?.trim() || "Товар без названия",
    imageUrl: data.main_image ?? null,
    price: inStock ? data.price : 0,
    currency: (inStock ? data.currency : null) ?? "KZT",
    availability: inStock ? "in_stock" : "out_of_stock",
    priceText: data.price_text ?? null,
  };
}

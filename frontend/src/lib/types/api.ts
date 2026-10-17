/**
 * API contract types. Shapes mirror the backend pydantic schemas
 * (core_service `schemas/user.py` → UserOut, and the planned products API).
 */

export interface User {
  id: number;
  first_name: string;
  last_name: string | null;
  username: string | null;
  language_code: string | null;
  photo_url: string | null;
  is_premium: boolean;
  allows_write_to_pm: boolean;
  added_to_attachment_menu: boolean;
  notification_threshold: number;
  check_frequency_hours: number;
  notifications_paused: boolean;
}

export type Availability = "in_stock" | "out_of_stock";

export interface PricePoint {
  at: string;
  price: number;
}

export type ChangeKind = "price_up" | "price_down" | "out_of_stock" | "back_in_stock";

export interface ProductChange {
  at: string;
  kind: ChangeKind;
  oldValue: number | null;
  newValue: number | null;
  percent: number | null;
}

export interface Product {
  id: string;
  title: string;
  url: string;
  imageUrl: string | null;
  note: string | null;
  currentPrice: number;
  currency: string;
  availability: Availability;
  change24hPercent: number | null;
  addedAt: string;
  notificationThreshold: number | null;
  priceHistory: PricePoint[];
  changes: ProductChange[];
}

export interface AddProductInput {
  url: string;
  note?: string | null;
  notificationThreshold?: number | null;
}

export interface ProductPreview {
  title: string;
  imageUrl: string | null;
  price: number;
  currency: string;
  availability: Availability;
  /** Human-readable price text from the source (used when there is no numeric price). */
  priceText?: string | null;
}

/**
 * Raw responses of the parser service (`GET /api/v1/products/?url=`).
 * Mirrors `ProductData` / `OutOfStockProductData` from the backend.
 */
export interface ParserProductData {
  product_type: "in_stock";
  title: string;
  description: string | null;
  brand: string | null;
  sku: number;
  main_image: string | null;
  price: number;
  currency: string | null;
  availability: string | null;
  url: string;
  rating: number | string | null;
  review_count: number | string | null;
  price_text: string | null;
  original_price_text: string | null;
  brand_label: string | null;
  seller_name: string | null;
}

export interface ParserOutOfStockProductData {
  product_type: "out_of_stock";
  title: string | null;
  sku: number | null;
  main_image: string | null;
  price_text: string | null;
  url: string | null;
  seller_name: string | null;
  availability: string;
  delivery_message: string | null;
}

export type ParserProduct = ParserProductData | ParserOutOfStockProductData;

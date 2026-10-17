import type {
  Availability,
  PricePoint,
  Product,
  ProductChange,
  ProductPreview,
} from "../types/api";

export const MOCK_CURRENCY = "KZT";

function isoDaysAgo(days: number, hour = 12): string {
  const date = new Date();
  date.setDate(date.getDate() - days);
  date.setHours(hour, 0, 0, 0);
  return date.toISOString();
}

function history(points: Array<[number, number]>): PricePoint[] {
  return points.map(([daysAgo, price]) => ({ at: isoDaysAgo(daysAgo), price }));
}

function changesFromHistory(points: PricePoint[]): ProductChange[] {
  const changes: ProductChange[] = [];
  for (let i = 1; i < points.length; i += 1) {
    const prev = points[i - 1];
    const next = points[i];
    if (prev.price === next.price) continue;
    const percent = ((next.price - prev.price) / prev.price) * 100;
    changes.push({
      at: next.at,
      kind: next.price > prev.price ? "price_up" : "price_down",
      oldValue: prev.price,
      newValue: next.price,
      percent: Number(percent.toFixed(1)),
    });
  }
  return changes.reverse();
}

function change24h(points: PricePoint[]): number | null {
  if (points.length < 2) return null;
  const threshold = Date.now() - 24 * 60 * 60 * 1000;
  const baseline = points.filter((point) => new Date(point.at).getTime() <= threshold).at(-1);
  if (!baseline) return null;
  const last = points.at(-1)!;
  const percent = ((last.price - baseline.price) / baseline.price) * 100;
  return Number(percent.toFixed(1));
}

function image(seed: string): string {
  return `https://picsum.photos/seed/${seed}/200/200`;
}

interface Seed {
  id: string;
  title: string;
  url: string;
  note: string | null;
  addedDaysAgo: number;
  availability: Availability;
  points: Array<[number, number]>;
}

const SEEDS: Seed[] = [
  {
    id: "p-1001",
    title: "Беспроводные наушники X5 Pro",
    url: "https://www.ozon.kz/product/x5-pro",
    note: "Конкурент — наушники",
    addedDaysAgo: 45,
    availability: "in_stock",
    points: [
      [30, 18990],
      [24, 18500],
      [18, 18990],
      [12, 17490],
      [6, 17490],
      [3, 16990],
      [0, 15990],
    ],
  },
  {
    id: "p-1002",
    title: "Умная колонка Mini Sound",
    url: "https://www.ozon.kz/product/mini-sound",
    note: null,
    addedDaysAgo: 33,
    availability: "in_stock",
    points: [
      [30, 24990],
      [21, 24990],
      [14, 23500],
      [7, 23500],
      [2, 24200],
      [0, 24200],
    ],
  },
  {
    id: "p-1003",
    title: "Робот-пылесос CleanBot S7",
    url: "https://www.ozon.kz/product/cleanbot-s7",
    note: "Следлю за наличием",
    addedDaysAgo: 60,
    availability: "out_of_stock",
    points: [
      [30, 89990],
      [20, 85990],
      [10, 85990],
      [4, 82990],
      [0, 82990],
    ],
  },
  {
    id: "p-1004",
    title: "Механическая клавиатура KeyType 87",
    url: "https://www.ozon.kz/product/keytype-87",
    note: null,
    addedDaysAgo: 20,
    availability: "in_stock",
    points: [
      [18, 21900],
      [10, 21900],
      [5, 22900],
      [0, 22900],
    ],
  },
];

function seedToProduct(seed: Seed): Product {
  const priceHistory = history(seed.points);
  const changes = changesFromHistory(priceHistory);

  if (seed.availability === "out_of_stock") {
    changes.unshift({
      at: isoDaysAgo(2, 9),
      kind: "out_of_stock",
      oldValue: priceHistory.at(-1)?.price ?? null,
      newValue: null,
      percent: null,
    });
  }

  return {
    id: seed.id,
    title: seed.title,
    url: seed.url,
    imageUrl: image(seed.id),
    note: seed.note,
    currentPrice: priceHistory.at(-1)!.price,
    currency: MOCK_CURRENCY,
    availability: seed.availability,
    change24hPercent: change24h(priceHistory),
    addedAt: isoDaysAgo(seed.addedDaysAgo),
    notificationThreshold: null,
    priceHistory,
    changes,
  };
}

export function createSeedProducts(): Product[] {
  return SEEDS.map(seedToProduct);
}

const PREVIEW_POOL: ProductPreview[] = [
  { title: "Портативный блендер TurboMix", imageUrl: image("preview-1"), price: 12990, currency: MOCK_CURRENCY, availability: "in_stock" },
  { title: "Смарт-часы FitBand 6", imageUrl: image("preview-2"), price: 21990, currency: MOCK_CURRENCY, availability: "in_stock" },
  { title: "Настольная лампа LumiGlow", imageUrl: image("preview-3"), price: 7490, currency: MOCK_CURRENCY, availability: "out_of_stock" },
  { title: "Термокружка SteelKeep 500", imageUrl: image("preview-4"), price: 5990, currency: MOCK_CURRENCY, availability: "in_stock" },
];

function hash(input: string): number {
  let value = 0;
  for (let i = 0; i < input.length; i += 1) {
    value = (value * 31 + input.charCodeAt(i)) | 0;
  }
  return Math.abs(value);
}

export function mockPreview(url: string): ProductPreview {
  const preview = PREVIEW_POOL[hash(url) % PREVIEW_POOL.length];
  return { ...preview };
}

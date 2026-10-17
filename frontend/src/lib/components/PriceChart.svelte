<script lang="ts">
  import { formatPrice } from "../format";
  import type { PricePoint } from "../types/api";

  let { points, currency }: { points: PricePoint[]; currency: string } = $props();

  const W = 320;
  const H = 140;
  const PAD = 10;

  const series = $derived(points.filter((point) => Number.isFinite(point.price)));
  const prices = $derived(series.map((point) => point.price));
  const min = $derived(prices.length ? Math.min(...prices) : 0);
  const max = $derived(prices.length ? Math.max(...prices) : 0);
  const range = $derived(max - min || 1);

  const coords = $derived(
    series.map((point, index) => {
      const x = PAD + (index / Math.max(series.length - 1, 1)) * (W - PAD * 2);
      const y = PAD + (1 - (point.price - min) / range) * (H - PAD * 2);
      return { x, y };
    }),
  );

  const linePath = $derived(
    coords
      .map((c, i) => `${i === 0 ? "M" : "L"}${c.x.toFixed(1)},${c.y.toFixed(1)}`)
      .join(" "),
  );

  const areaPath = $derived(
    coords.length > 1
      ? `${linePath} L${coords[coords.length - 1].x.toFixed(1)},${(
          H - PAD
        ).toFixed(1)} L${coords[0].x.toFixed(1)},${(H - PAD).toFixed(1)} Z`
      : "",
  );
</script>

{#if series.length < 2}
  <div
    class="grid h-[140px] place-items-center rounded-2xl bg-tg-secondary-bg text-sm text-tg-hint"
  >
    Недостаточно данных для графика
  </div>
{:else}
  <div class="rounded-2xl bg-tg-secondary-bg p-2">
    <svg
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="none"
      class="h-[140px] w-full"
      role="img"
      aria-label="График изменения цены"
    >
      <defs>
        <linearGradient id="price-area" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="var(--tg-accent)" stop-opacity="0.35" />
          <stop offset="100%" stop-color="var(--tg-accent)" stop-opacity="0" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill="url(#price-area)" />
      <path
        d={linePath}
        fill="none"
        stroke="var(--tg-accent)"
        stroke-width="2"
        stroke-linejoin="round"
        stroke-linecap="round"
        vector-effect="non-scaling-stroke"
      />
    </svg>
    <div class="flex justify-between px-1 pb-1 text-xs text-tg-hint">
      <span>{formatPrice(min, currency)}</span>
      <span>{formatPrice(max, currency)}</span>
    </div>
  </div>
{/if}

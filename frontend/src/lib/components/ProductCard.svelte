<script lang="ts">
  import { ChevronRight, ImageOff, Trash } from "@lucide/svelte";

  import { formatPrice } from "../format";
  import type { Product } from "../types/api";
  import AvailabilityBadge from "./AvailabilityBadge.svelte";
  import ChangeBadge from "./ChangeBadge.svelte";

  let {
    product,
    onOpen,
    onDelete,
  }: {
    product: Product;
    onOpen: (id: string) => void;
    onDelete: (id: string) => void;
  } = $props();
</script>

<div class="flex items-stretch gap-2 rounded-2xl bg-tg-section-bg p-3">
  <button type="button" class="flex min-w-0 flex-1 gap-3 text-left" onclick={() => onOpen(product.id)}>
    <div class="size-16 shrink-0 overflow-hidden rounded-xl bg-tg-secondary-bg">
      {#if product.imageUrl}
        <img
          src={product.imageUrl}
          alt=""
          class="size-full object-cover"
          loading="lazy"
        />
      {:else}
        <div class="grid size-full place-items-center text-tg-hint">
          <ImageOff class="size-5" />
        </div>
      {/if}
    </div>

    <div class="min-w-0 flex-1">
      <p class="line-clamp-2 text-sm font-medium">{product.title}</p>
      {#if product.note}
        <p class="mt-0.5 truncate text-xs text-tg-hint">{product.note}</p>
      {/if}
      <div class="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1">
        {#if product.currentPrice > 0}
          <span class="text-base font-semibold">
            {formatPrice(product.currentPrice, product.currency)}
          </span>
        {/if}
        <ChangeBadge value={product.change24hPercent} suffix=" за сутки" />
      </div>
      <div class="mt-1.5">
        <AvailabilityBadge availability={product.availability} />
      </div>
    </div>
  </button>

  <div class="flex flex-col items-center justify-between">
    <button
      type="button"
      aria-label="Удалить из отслеживания"
      class="grid size-8 place-items-center rounded-full text-tg-hint active:bg-tg-secondary-bg"
      onclick={() => onDelete(product.id)}
    >
      <Trash class="size-4" />
    </button>
    <ChevronRight class="size-4 text-tg-hint" />
  </div>
</div>

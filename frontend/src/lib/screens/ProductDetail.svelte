<script lang="ts">
  import { onMount } from "svelte";
  import {
    Bell,
    ExternalLink,
    ImageOff,
    PackageOpen,
    Trash,
  } from "@lucide/svelte";

  import AvailabilityBadge from "../components/AvailabilityBadge.svelte";
  import ChangeBadge from "../components/ChangeBadge.svelte";
  import EmptyState from "../components/EmptyState.svelte";
  import PriceChart from "../components/PriceChart.svelte";
  import TopBar from "../components/TopBar.svelte";
  import { formatDateTime, formatPercent, formatPrice } from "../format";
  import { productsStore } from "../stores/products.svelte";
  import { router } from "../stores/router.svelte";
  import type { ChangeKind } from "../types/api";

  let { id }: { id: string } = $props();

  const product = $derived(productsStore.get(id));

  const ranges = [
    { key: "7", label: "Неделя" },
    { key: "30", label: "Месяц" },
    { key: "90", label: "3 месяца" },
  ] as const;

  let range = $state<(typeof ranges)[number]["key"]>("30");
  let threshold = $state(5);
  let saved = $state(false);
  let initialized = false;

  const chartPoints = $derived.by(() => {
    if (!product) return [];
    const limit = Date.now() - Number(range) * 24 * 60 * 60 * 1000;
    return product.priceHistory.filter((point) => new Date(point.at).getTime() >= limit);
  });

  const changeLabels: Record<ChangeKind, string> = {
    price_up: "Цена выросла",
    price_down: "Цена снизилась",
    out_of_stock: "Пропал со склада",
    back_in_stock: "Снова в наличии",
  };

  onMount(() => {
    void productsStore.load();
  });

  $effect(() => {
    if (!initialized && product) {
      threshold = product.notificationThreshold ?? 5;
      initialized = true;
    }
  });

  async function saveThreshold(): Promise<void> {
    if (!product) return;
    await productsStore.update(product.id, { notificationThreshold: threshold });
    saved = true;
    setTimeout(() => (saved = false), 2000);
  }

  async function stopTracking(): Promise<void> {
    if (!product) return;
    await productsStore.remove(product.id);
    router.back();
  }

  function openOnOzon(): void {
    if (product) window.open(product.url, "_blank", "noopener");
  }
</script>

<TopBar title={product?.title ?? "Товар"} onBack={() => router.back()} />

{#if !product}
  <EmptyState title="Товар не найден" icon={PackageOpen} />
{:else}
  <div class="flex flex-col gap-4 p-3 pb-8">
    <div class="flex gap-3">
      <div class="size-24 shrink-0 overflow-hidden rounded-2xl bg-tg-secondary-bg">
        {#if product.imageUrl}
          <img src={product.imageUrl} alt="" class="size-full object-cover" />
        {:else}
          <div class="grid size-full place-items-center text-tg-hint">
            <ImageOff class="size-6" />
          </div>
        {/if}
      </div>
      <div class="min-w-0 flex-1">
        <p class="text-sm font-medium">{product.title}</p>
        {#if product.note}
          <p class="mt-0.5 text-xs text-tg-hint">{product.note}</p>
        {/if}
        {#if product.currentPrice > 0}
          <p class="mt-2 text-2xl font-semibold">
            {formatPrice(product.currentPrice, product.currency)}
          </p>
        {/if}
        <div class="mt-1.5 flex flex-wrap items-center gap-2">
          <AvailabilityBadge availability={product.availability} />
          <ChangeBadge value={product.change24hPercent} suffix=" за сутки" />
        </div>
      </div>
    </div>

    <div>
      <div class="mb-2 flex gap-2">
        {#each ranges as item (item.key)}
          <button
            type="button"
            class="rounded-full px-3 py-1.5 text-xs font-medium {range === item.key
              ? 'bg-tg-button text-tg-button-text'
              : 'bg-tg-secondary-bg text-tg-hint'}"
            onclick={() => (range = item.key)}
          >
            {item.label}
          </button>
        {/each}
      </div>
      <PriceChart points={chartPoints} currency={product.currency} />
    </div>

    <button
      type="button"
      class="flex items-center justify-center gap-2 rounded-xl bg-tg-secondary-bg py-2.5 text-sm font-medium text-tg-link"
      onclick={openOnOzon}
    >
      <ExternalLink class="size-4" />
      Открыть на Ozon
    </button>

    <section>
      <h2 class="mb-2 flex items-center gap-1.5 text-sm font-semibold">
        <Bell class="size-4 text-tg-hint" />
        Порог уведомлений
      </h2>
      <div class="flex items-center gap-2">
        <input
          type="number"
          min="0"
          step="1"
          class="w-24 rounded-xl bg-tg-secondary-bg px-3 py-2.5 text-sm outline-none"
          bind:value={threshold}
        />
        <span class="text-sm text-tg-hint">% изменения цены</span>
        <button
          type="button"
          class="ml-auto rounded-xl bg-tg-button px-4 py-2.5 text-sm font-medium text-tg-button-text"
          onclick={() => void saveThreshold()}
        >
          {saved ? "Сохранено" : "Сохранить"}
        </button>
      </div>
    </section>

    <section>
      <h2 class="mb-2 text-sm font-semibold">История изменений</h2>
      {#if product.changes.length === 0}
        <p class="rounded-xl bg-tg-secondary-bg px-3 py-3 text-sm text-tg-hint">
          Изменений пока не зафиксировано.
        </p>
      {:else}
        <ul class="flex flex-col gap-2">
          {#each product.changes as change (change.at)}
            <li class="rounded-xl bg-tg-secondary-bg px-3 py-2.5">
              <div class="flex items-center justify-between gap-2">
                <span class="text-sm font-medium">{changeLabels[change.kind]}</span>
                <span class="text-xs text-tg-hint">{formatDateTime(change.at)}</span>
              </div>
              {#if change.kind === "price_up" || change.kind === "price_down"}
                <div class="mt-1 flex items-center gap-2 text-sm">
                  <span class="text-tg-hint line-through">
                    {formatPrice(change.oldValue ?? 0, product.currency)}
                  </span>
                  <span>→</span>
                  <span class="font-medium">
                    {formatPrice(change.newValue ?? 0, product.currency)}
                  </span>
                  {#if change.percent !== null}
                    <span class="text-xs {change.kind === 'price_down'
                      ? 'text-tg-success'
                      : 'text-tg-danger'}">
                      {formatPercent(change.percent)}
                    </span>
                  {/if}
                </div>
              {/if}
            </li>
          {/each}
        </ul>
      {/if}
    </section>

    <button
      type="button"
      class="flex items-center justify-center gap-2 rounded-xl bg-tg-destructive/10 py-2.5 text-sm font-medium text-tg-destructive"
      onclick={() => void stopTracking()}
    >
      <Trash class="size-4" />
      Остановить отслеживание
    </button>
  </div>
{/if}

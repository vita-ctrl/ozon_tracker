<script lang="ts">
  import { onMount } from "svelte";
  import { CirclePlus, PackageOpen, RefreshCw } from "@lucide/svelte";

  import EmptyState from "../components/EmptyState.svelte";
  import ProductCard from "../components/ProductCard.svelte";
  import Spinner from "../components/Spinner.svelte";
  import TopBar from "../components/TopBar.svelte";
  import { router } from "../stores/router.svelte";
  import {
    SORT_LABELS,
    productsStore,
    type ProductSort,
  } from "../stores/products.svelte";

  const sorts = Object.keys(SORT_LABELS) as ProductSort[];

  onMount(() => {
    void productsStore.load();
  });
</script>

<TopBar title="Мои товары">
  {#snippet actions()}
    <button
      type="button"
      aria-label="Обновить"
      class="grid size-9 place-items-center rounded-full text-tg-accent active:bg-tg-secondary-bg"
      onclick={() => void productsStore.load(true)}
    >
      <RefreshCw class="size-5" />
    </button>
  {/snippet}
</TopBar>

<div class="flex gap-2 overflow-x-auto px-3 py-2">
  {#each sorts as sort (sort)}
    <button
      type="button"
      class="shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition-colors {productsStore.sort ===
      sort
        ? 'bg-tg-button text-tg-button-text'
        : 'bg-tg-secondary-bg text-tg-hint'}"
      onclick={() => (productsStore.sort = sort)}
    >
      {SORT_LABELS[sort]}
    </button>
  {/each}
</div>

{#if productsStore.loading && productsStore.items.length === 0}
  <Spinner />
{:else if productsStore.error}
  <EmptyState
    title="Не удалось загрузить товары"
    description={productsStore.error}
  />
{:else if productsStore.items.length === 0}
  <EmptyState
    title="Пока нет товаров"
    description="Добавьте ссылку на товар конкурента, чтобы отслеживать цену и наличие."
    icon={PackageOpen}
  />
{:else}
  <div class="flex flex-col gap-2 px-3 pb-24">
    {#each productsStore.sorted as product (product.id)}
      <ProductCard
        {product}
        onOpen={(id) => router.go({ name: "detail", id })}
        onDelete={(id) => void productsStore.remove(id)}
      />
    {/each}
  </div>
{/if}

<button
  type="button"
  class="fixed bottom-20 right-4 z-20 flex items-center gap-2 rounded-full bg-tg-button px-4 py-3 text-sm font-medium text-tg-button-text shadow-lg active:scale-95"
  onclick={() => router.go({ name: "add" })}
>
  <CirclePlus class="size-5" />
  Добавить товар
</button>

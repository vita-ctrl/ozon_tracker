<script lang="ts">
  import { CircleCheck, ImageOff, Search } from "@lucide/svelte";

  import { getErrorMessage } from "../api/client";
  import AvailabilityBadge from "../components/AvailabilityBadge.svelte";
  import TopBar from "../components/TopBar.svelte";
  import { formatPrice } from "../format";
  import { productsStore } from "../stores/products.svelte";
  import { router } from "../stores/router.svelte";
  import type { ProductPreview } from "../types/api";

  let url = $state("");
  let note = $state("");
  let threshold = $state(5);

  let checking = $state(false);
  let submitting = $state(false);
  let error = $state<string | null>(null);
  let preview = $state<ProductPreview | null>(null);

  const canCheck = $derived(url.trim().length > 0 && !checking);

  async function check(): Promise<void> {
    if (!canCheck) return;
    checking = true;
    error = null;
    preview = null;
    try {
      preview = await productsStore.preview(url.trim());
    } catch (err) {
      error = getErrorMessage(err);
    } finally {
      checking = false;
    }
  }

  async function submit(): Promise<void> {
    if (submitting) return;
    submitting = true;
    error = null;
    try {
      const product = await productsStore.add({
        url: url.trim(),
        note: note.trim() || null,
        notificationThreshold: threshold,
      });
      router.go({ name: "detail", id: product.id });
    } catch (err) {
      error = getErrorMessage(err);
    } finally {
      submitting = false;
    }
  }
</script>

<TopBar title="Добавить товар" onBack={() => router.back()} />

<div class="flex flex-col gap-4 p-3">
  <label class="flex flex-col gap-1.5">
    <span class="text-xs font-medium text-tg-hint">Ссылка на товар с Ozon</span>
    <input
      type="url"
      inputmode="url"
      placeholder="https://www.ozon.kz/product/..."
      class="rounded-xl bg-tg-secondary-bg px-3 py-2.5 text-sm outline-none placeholder:text-tg-hint"
      bind:value={url}
      onchange={() => {
        preview = null;
      }}
    />
  </label>

  <button
    type="button"
    disabled={!canCheck}
    class="flex items-center justify-center gap-2 rounded-xl bg-tg-secondary-bg py-2.5 text-sm font-medium disabled:opacity-50"
    onclick={() => void check()}
  >
    <Search class="size-4" />
    {checking ? "Проверяем…" : "Проверить ссылку"}
  </button>

  {#if error}
    <p class="rounded-xl bg-tg-danger/10 px-3 py-2 text-sm text-tg-danger">{error}</p>
  {/if}

  {#if preview}
    <div class="rounded-2xl bg-tg-section-bg p-3">
      <p class="mb-2 text-xs font-medium text-tg-hint">Превью</p>
      <div class="flex gap-3">
        <div class="size-16 shrink-0 overflow-hidden rounded-xl bg-tg-secondary-bg">
          {#if preview.imageUrl}
            <img src={preview.imageUrl} alt="" class="size-full object-cover" />
          {:else}
            <div class="grid size-full place-items-center text-tg-hint">
              <ImageOff class="size-5" />
            </div>
          {/if}
        </div>
        <div class="min-w-0 flex-1">
          <p class="line-clamp-2 text-sm font-medium">{preview.title}</p>
          {#if preview.price > 0}
            <p class="mt-1 text-base font-semibold">
              {formatPrice(preview.price, preview.currency)}
            </p>
          {:else if preview.priceText}
            <p class="mt-1 text-sm text-tg-hint">{preview.priceText}</p>
          {/if}
          <div class="mt-1">
            <AvailabilityBadge availability={preview.availability} />
          </div>
        </div>
      </div>

      <div class="mt-3 flex flex-col gap-3">
        <label class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-tg-hint">Пометка (необязательно)</span>
          <input
            type="text"
            placeholder="Например: конкурент — наушники"
            class="rounded-xl bg-tg-secondary-bg px-3 py-2.5 text-sm outline-none placeholder:text-tg-hint"
            bind:value={note}
          />
        </label>

        <label class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-tg-hint"
            >Порог уведомлений, % (необязательно)</span
          >
          <input
            type="number"
            min="0"
            step="1"
            class="rounded-xl bg-tg-secondary-bg px-3 py-2.5 text-sm outline-none"
            bind:value={threshold}
          />
        </label>
      </div>
    </div>

    <button
      type="button"
      disabled={submitting}
      class="flex items-center justify-center gap-2 rounded-xl bg-tg-button py-3 text-sm font-semibold text-tg-button-text disabled:opacity-50"
      onclick={() => void submit()}
    >
      <CircleCheck class="size-5" />
      {submitting ? "Добавляем…" : "Начать отслеживание"}
    </button>
  {/if}
</div>

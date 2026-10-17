<script lang="ts">
  import { ArrowLeft } from "@lucide/svelte";
  import type { Snippet } from "svelte";

  let {
    title,
    onBack,
    actions,
  }: {
    title: string;
    onBack?: () => void;
    actions?: Snippet;
  } = $props();
</script>

<header
  class="sticky top-0 z-10 flex items-center gap-2 border-b border-tg-separator bg-tg-header-bg/95 px-3 py-3 backdrop-blur"
>
  {#if onBack}
    <button
      type="button"
      aria-label="Назад"
      class="grid size-9 shrink-0 place-items-center rounded-full text-tg-accent active:bg-tg-secondary-bg"
      onclick={onBack}
    >
      <ArrowLeft class="size-5" />
    </button>
  {/if}
  <h1 class="min-w-0 flex-1 truncate text-lg font-semibold">{title}</h1>
  {#if actions}
    {@render actions()}
  {/if}
</header>

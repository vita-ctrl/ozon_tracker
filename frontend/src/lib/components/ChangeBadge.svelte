<script lang="ts">
  import { Minus, TrendingDown, TrendingUp } from "@lucide/svelte";

  import { formatPercent } from "../format";

  let { value, suffix = "" }: { value: number | null; suffix?: string } = $props();

  const up = $derived(value !== null && value > 0);
</script>

{#if value === null || value === 0}
  <span class="inline-flex items-center gap-1 text-xs text-tg-hint">
    <Minus class="size-3.5" />
    без изменений{suffix}
  </span>
{:else if up}
  <span class="inline-flex items-center gap-1 text-xs font-medium text-tg-danger">
    <TrendingUp class="size-3.5" />
    {formatPercent(value)}{suffix}
  </span>
{:else}
  <span class="inline-flex items-center gap-1 text-xs font-medium text-tg-success">
    <TrendingDown class="size-3.5" />
    {formatPercent(value)}{suffix}
  </span>
{/if}

<script lang="ts">
  import type { Availability } from "../types/api";

  let {
    availability,
    class: className = "",
  }: { availability: Availability; class?: string } = $props();
</script>

<span
  class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium {availability ===
  'in_stock'
    ? 'bg-tg-success/15 text-tg-success'
    : 'bg-tg-danger/15 text-tg-danger'} {className}"
>
  {availability === "in_stock" ? "В наличии" : "Нет в наличии"}
</span>

<script lang="ts">
  import { LoaderCircle } from "@lucide/svelte";

  let { label = "Загрузка…" }: { label?: string } = $props();
</script>

<div class="flex flex-col items-center justify-center gap-2 py-12 text-tg-hint">
  <LoaderCircle class="size-6 animate-spin" />
  <span class="text-sm">{label}</span>
</div>

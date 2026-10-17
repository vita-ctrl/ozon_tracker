<script lang="ts">
  import type { LucideIcon } from "@lucide/svelte";
  import type { Snippet } from "svelte";

  let {
    title,
    description,
    icon: Icon,
    children,
  }: {
    title: string;
    description?: string;
    icon?: LucideIcon;
    children?: Snippet;
  } = $props();
</script>

<div class="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
  {#if Icon}
    <div class="grid size-14 place-items-center rounded-full bg-tg-secondary-bg text-tg-hint">
      <Icon class="size-7" />
    </div>
  {/if}
  <div>
    <p class="font-medium">{title}</p>
    {#if description}
      <p class="mt-1 text-sm text-tg-hint">{description}</p>
    {/if}
  </div>
  {#if children}
    {@render children()}
  {/if}
</div>

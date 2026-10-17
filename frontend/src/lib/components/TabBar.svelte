<script lang="ts">
  import { Package, Settings } from "@lucide/svelte";

  import { router } from "../stores/router.svelte";

  const tabs = [
    { name: "list", label: "Товары", icon: Package },
    { name: "settings", label: "Настройки", icon: Settings },
  ] as const;

  const active = $derived(router.route.name === "settings" ? "settings" : "list");
</script>

<nav
  class="sticky bottom-0 z-10 mt-auto flex border-t border-tg-separator bg-tg-header-bg/95 backdrop-blur"
>
  {#each tabs as tab (tab.name)}
    {@const Icon = tab.icon}
    <button
      type="button"
      class="flex flex-1 flex-col items-center gap-1 py-2 text-xs transition-colors {active ===
      tab.name
        ? 'text-tg-accent'
        : 'text-tg-hint'}"
      onclick={() => router.go({ name: tab.name })}
    >
      <Icon class="size-5" />
      <span>{tab.label}</span>
    </button>
  {/each}
</nav>

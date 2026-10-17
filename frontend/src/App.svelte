<script lang="ts">
  import { onMount } from "svelte";
  import { Send } from "@lucide/svelte";

  import EmptyState from "./lib/components/EmptyState.svelte";
  import Spinner from "./lib/components/Spinner.svelte";
  import TabBar from "./lib/components/TabBar.svelte";
  import AddProduct from "./lib/screens/AddProduct.svelte";
  import ProductDetail from "./lib/screens/ProductDetail.svelte";
  import ProductList from "./lib/screens/ProductList.svelte";
  import Settings from "./lib/screens/Settings.svelte";
  import { router } from "./lib/stores/router.svelte";
  import { userStore } from "./lib/stores/user.svelte";

  const route = $derived(router.route);
  const showTabs = $derived(route.name === "list" || route.name === "settings");

  onMount(() => {
    void userStore.load();
  });
</script>

<div class="mx-auto flex min-h-dvh w-full max-w-md flex-col">
  {#if userStore.loading}
    <div class="grid flex-1 place-items-center">
      <Spinner label="Подключаемся к Telegram…" />
    </div>
  {:else if userStore.unauthorized}
    <EmptyState
      title="Откройте через Telegram"
      description="Приложение работает только как Telegram Mini App. Запустите его из чата с ботом."
      icon={Send}
    />
  {:else if userStore.error}
    <EmptyState title="Ошибка подключения" description={userStore.error} />
  {:else}
    {#if route.name === "list"}
      <ProductList />
    {:else if route.name === "add"}
      <AddProduct />
    {:else if route.name === "detail"}
      <ProductDetail id={route.id} />
    {:else}
      <Settings />
    {/if}

    {#if showTabs}
      <TabBar />
    {/if}
  {/if}
</div>

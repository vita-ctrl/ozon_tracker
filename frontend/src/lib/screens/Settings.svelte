<script lang="ts">
  import { Bell, Clock, Info, Pause, Play } from "@lucide/svelte";

  import TopBar from "../components/TopBar.svelte";
  import { displayName } from "../format";
  import { userStore } from "../stores/user.svelte";

  const user = $derived(userStore.user);

  let threshold = $state(userStore.user?.notification_threshold ?? 5);
  let frequency = $state(userStore.user?.check_frequency_hours ?? 6);
  let paused = $state(userStore.user?.notifications_paused ?? false);
  let saved = $state(false);

  const frequencies = [3, 6, 12, 24];

  function save(): void {
    userStore.applySettings({
      notification_threshold: threshold,
      check_frequency_hours: frequency,
      notifications_paused: paused,
    });
    saved = true;
    setTimeout(() => (saved = false), 2000);
  }
</script>

<TopBar title="Настройки" />

<div class="flex flex-col gap-4 p-3 pb-8">
  {#if user}
    <div class="flex items-center gap-3 rounded-2xl bg-tg-section-bg p-3">
      {#if user.photo_url}
        <img src={user.photo_url} alt="" class="size-12 rounded-full object-cover" />
      {:else}
        <div
          class="grid size-12 place-items-center rounded-full bg-tg-secondary-bg text-lg font-semibold"
        >
          {user.first_name.charAt(0)}
        </div>
      {/if}
      <div class="min-w-0">
        <p class="truncate font-medium">{displayName(user)}</p>
        {#if user.username}
          <p class="truncate text-sm text-tg-hint">@{user.username}</p>
        {/if}
      </div>
    </div>
  {/if}

  <section class="flex flex-col gap-3 rounded-2xl bg-tg-section-bg p-3">
    <h2 class="flex items-center gap-1.5 text-sm font-semibold">
      <Bell class="size-4 text-tg-hint" />
      Уведомления
    </h2>

    <label class="flex items-center justify-between gap-3">
      <span class="text-sm">Порог по умолчанию</span>
      <div class="flex items-center gap-2">
        <input
          type="number"
          min="0"
          step="1"
          class="w-20 rounded-xl bg-tg-secondary-bg px-3 py-2 text-sm outline-none"
          bind:value={threshold}
        />
        <span class="text-sm text-tg-hint">%</span>
      </div>
    </label>

    <label class="flex items-center justify-between gap-3">
      <span class="flex items-center gap-1.5 text-sm">
        <Clock class="size-4 text-tg-hint" />
        Частота проверки
      </span>
      <select
        class="rounded-xl bg-tg-secondary-bg px-3 py-2 text-sm outline-none"
        bind:value={frequency}
      >
        {#each frequencies as hours (hours)}
          <option value={hours}>раз в {hours} ч</option>
        {/each}
      </select>
    </label>

    <button
      type="button"
      class="flex items-center justify-between gap-3"
      onclick={() => (paused = !paused)}
    >
      <span class="flex items-center gap-1.5 text-sm">
        {#if paused}
          <Play class="size-4 text-tg-hint" />
          Возобновить уведомления
        {:else}
          <Pause class="size-4 text-tg-hint" />
          Поставить на паузу
        {/if}
      </span>
      <span
        class="relative h-6 w-11 rounded-full transition-colors {paused
          ? 'bg-tg-button'
          : 'bg-tg-secondary-bg'}"
      >
        <span
          class="absolute top-0.5 size-5 rounded-full bg-tg-bg shadow transition-all {paused
            ? 'left-5.5'
            : 'left-0.5'}"
        ></span>
      </span>
    </button>
  </section>

  <button
    type="button"
    class="rounded-xl bg-tg-button py-3 text-sm font-semibold text-tg-button-text"
    onclick={save}
  >
    {saved ? "Сохранено" : "Сохранить"}
  </button>

  <p class="flex items-start gap-1.5 px-1 text-xs text-tg-hint">
    <Info class="mt-0.5 size-3.5 shrink-0" />
    Настройки сохраняются локально. Синхронизация с сервером появится после
    добавления эндпоинта обновления профиля.
  </p>
</div>

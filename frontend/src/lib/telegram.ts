import SDK from "@twa-dev/sdk";
import type { WebApp as TelegramWebApp } from "@twa-dev/types";

declare global {
  interface Window {
    Telegram?: { WebApp: TelegramWebApp };
  }
}

const THEME_VARS: Record<string, string> = {
  bg_color: "--tg-bg",
  secondary_bg_color: "--tg-secondary-bg",
  text_color: "--tg-text",
  hint_color: "--tg-hint",
  link_color: "--tg-link",
  button_color: "--tg-button",
  button_text_color: "--tg-button-text",
  header_bg_color: "--tg-header-bg",
  accent_text_color: "--tg-accent",
  destructive_text_color: "--tg-destructive",
  section_bg_color: "--tg-section-bg",
  section_header_text_color: "--tg-section-header",
  subtitle_text_color: "--tg-subtitle",
  section_separator_color: "--tg-separator",
};

/**
 * Under Vite's CJS interop the `@twa-dev/sdk` default export can resolve to the
 * module namespace (`{ default: WebApp }`) instead of the WebApp object itself,
 * which made `WebApp.ready` a TypeError. Unwrap it when needed and fall back to
 * the global that the bundled Telegram script installs as a side effect.
 */
const sdk = SDK as unknown as TelegramWebApp & { default?: TelegramWebApp };

function getWebApp(): TelegramWebApp | undefined {
  if (sdk.default) return sdk.default;
  if (typeof sdk.ready === "function") return sdk;
  return window.Telegram?.WebApp;
}

export function applyTheme(): void {
  const app = getWebApp();
  const root = document.documentElement;
  root.classList.toggle("dark", app?.colorScheme === "dark");

  if (!app) return;

  const params = app.themeParams as unknown as Record<string, string | undefined>;
  for (const [key, cssVar] of Object.entries(THEME_VARS)) {
    const value = params[key];
    if (value) {
      root.style.setProperty(cssVar, value);
    }
  }
}

let initialized = false;

export function initTelegram(): void {
  const app = getWebApp();
  if (initialized || !app) return;
  initialized = true;

  app.ready();
  app.expand();
  applyTheme();
  app.onEvent("themeChanged", applyTheme);
}

export function getInitData(): string {
  return getWebApp()?.initData ?? "";
}

export function isInsideTelegram(): boolean {
  return Boolean(getWebApp()?.initData);
}

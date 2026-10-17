// frontend/scripts/gen-telegram-url.js
// node gen-telegram-url.js [--user ivan|alexander] [--origin http://localhost:5173]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : def;
}
const ORIGIN = arg("origin", process.env.FRONTEND_ORIGIN || "http://localhost:5173");

function botToken() {
  if (process.env.BOT_TOKEN) return process.env.BOT_TOKEN.trim();
  const p = path.resolve(__dirname, "../../core_service/src/.env");
  const m = fs.readFileSync(p, "utf8").match(/^BOT_TOKEN=(.+)$/m);
  return m ? m[1].trim() : "";
}

const THEME = {
  bg_color: "#15121a", secondary_bg_color: "#15121a", text_color: "#e8e0eb",
  hint_color: "#968d9e", link_color: "#d6baff", button_color: "#d6baff",
  button_text_color: "#430088", accent_text_color: "#d6baff",
  destructive_text_color: "#ffb4ab", header_bg_color: "#15121a",
  section_bg_color: "#15121a", section_header_text_color: "#e8e0eb",
  section_separator_color: "#968d9e", subtitle_text_color: "#968d9e",
  bottom_bar_bg_color: "#15121a",
};

const USERS = {
  ivan: {
    id: 123456, first_name: "Иван", last_name: "Петров",
    username: "ivan_petrov", language_code: "ru", is_premium: true,
  },
  alexander: {
    id: 8273260911, is_bot: false, first_name: "Александр", last_name: "Кузнецов",
    username: "aleksandr_kuznetsov", language_code: "ru", is_premium: true,
    allows_write_to_pm: true,
    photo_url: "https://t.me/i/userpic/320/4FPEE4tmP3ATHa57u6MqTDih13LTOiMoKoLDRG4PnSA.svg",
  },
};

async function main() {
  if (typeof globalThis.window === "undefined") globalThis.window = globalThis;

  const { mockTelegramEnvExtended } = await import("telegram-mock-init-data");
  const user = USERS[arg("user", "alexander")] ?? USERS.alexander;

  const launchParams = await mockTelegramEnvExtended({
    user,
    botToken: botToken(),
    themeParams: THEME,
  });

  console.log(`${ORIGIN}/#${launchParams}`);
}

main().catch((e) => { console.error(e); process.exit(1); });

import { mount } from "svelte";

import "./app.css";
import App from "./App.svelte";
import { initTelegram } from "./lib/telegram";

initTelegram();

const app = mount(App, {
  target: document.getElementById("app")!,
});

export default app;

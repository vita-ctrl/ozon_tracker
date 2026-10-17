import axios from "axios";

import { API_ORIGIN, API_PREFIX } from "../config";
import { getInitData } from "../telegram";

export const http = axios.create({
  baseURL: `${API_ORIGIN}${API_PREFIX}`,
  timeout: 15000,
});

http.interceptors.request.use((config) => {
  const initData = getInitData();
  if (initData) {
    config.headers.set("X-Telegram-Init-Data", initData);
  }
  return config;
});

export function isUnauthorized(error: unknown): boolean {
  return axios.isAxiosError(error) && error.response?.status === 401;
}

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    if (!error.response) {
      return "Сервер недоступен";
    }
    if (status === 502) {
      return "Не удалось разобрать страницу товара";
    }
    if (status === 503) {
      return "Ozon недоступен, попробуйте позже";
    }
    if (status === 504) {
      return "Ozon не ответил вовремя, попробуйте позже";
    }
    const detail: unknown = error.response.data?.detail;
    if (typeof detail === "string") return detail;
    return error.message;
  }
  return error instanceof Error ? error.message : "Неизвестная ошибка";
}

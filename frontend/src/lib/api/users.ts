import { http } from "./client";
import type { User } from "../types/api";

export async function getMe(): Promise<User> {
  const { data } = await http.get<User>("/me");
  return data;
}

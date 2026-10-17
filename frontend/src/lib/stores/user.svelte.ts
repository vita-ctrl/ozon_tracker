import { getErrorMessage, isUnauthorized } from "../api/client";
import { getMe } from "../api/users";
import type { User } from "../types/api";

export interface UserSettingsPatch {
  notification_threshold?: number;
  check_frequency_hours?: number;
  notifications_paused?: boolean;
}

class UserStore {
  user = $state<User | null>(null);
  loading = $state(true);
  error = $state<string | null>(null);
  unauthorized = $state(false);

  async load(): Promise<void> {
    this.loading = true;
    this.error = null;
    this.unauthorized = false;
    try {
      this.user = await getMe();
    } catch (error) {
      if (isUnauthorized(error)) {
        this.unauthorized = true;
      } else {
        this.error = getErrorMessage(error);
      }
    } finally {
      this.loading = false;
    }
  }

  applySettings(patch: UserSettingsPatch): void {
    if (this.user) {
      this.user = { ...this.user, ...patch };
    }
  }
}

export const userStore = new UserStore();

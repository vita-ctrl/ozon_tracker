export type Route =
  | { name: "list" }
  | { name: "add" }
  | { name: "detail"; id: string }
  | { name: "settings" };

class RouterStore {
  route = $state<Route>({ name: "list" });

  go(route: Route): void {
    this.route = route;
  }

  back(): void {
    this.route = { name: "list" };
  }
}

export const router = new RouterStore();

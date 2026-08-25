import json
import re


class WidgetStates:
    def __init__(self, widget_states: dict[str, str]):
        self._states: dict[str, dict] = {}
        for key, value in widget_states.items():
            prefix = re.split(r"[^a-zA-Z]", key)[0]
            if prefix in self._states:
                continue
            try:
                self._states[prefix] = json.loads(value)
            except json.JSONDecodeError:
                continue

    def get(self, name: str) -> dict | None:
        return self._states.get(name)

    def has(self, name: str) -> bool:
        return name in self._states

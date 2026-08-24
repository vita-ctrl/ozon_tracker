from importlib import import_module
from pathlib import Path

from aiogram import Dispatcher


routers = []

package_dir = Path(__file__).parent
for path in package_dir.rglob("*.py"):
    if path.name == "__init__.py":
        continue

    # Get path relative to the app/ directory
    # relative_path like handlers/start.py or handlers/user/create_ad.py
    relative_path = path.relative_to(package_dir.parent)
    module_parts = relative_path.with_suffix("").parts
    module_name = ".".join(module_parts)

    module = import_module(f".{module_name}", package="bot")
    router = getattr(module, "router", None)
    if router is not None:
        routers.append(router)


def setup(dp: Dispatcher) -> None:
    for router in routers:
        dp.include_router(router)

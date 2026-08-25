from importlib import import_module
from pathlib import Path

from fastapi import FastAPI

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

    module = import_module(f".{module_name}", package="api.v1")
    router = getattr(module, "router", None)
    if router is not None:
        routers.append(router)


def setup(app: FastAPI) -> None:
    for router in routers:
        app.include_router(router, prefix="/v1")

import importlib
import pkgutil


_PLUGINS = None


def get_plugins():
    global _PLUGINS
    if not _PLUGINS:
        _PLUGINS = _import_plugins()
    return _PLUGINS


def _import_plugins(name=__name__):
    """Load all plugins under '.plugins' package"""

    package = importlib.import_module(name)

    results = {}
    for _, name, _ in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + "." + name
        results[full_name] = importlib.import_module(full_name)
    return results


__all__ = ["get_plugins"]

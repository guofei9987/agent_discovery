"""agent_discovery package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("agent-discovery")
except PackageNotFoundError:
    # Package metadata is unavailable when importing directly from source.
    __version__ = "0.0.0"

__all__ = ["__version__"]

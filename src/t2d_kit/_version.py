"""Version information for t2d-kit."""

try:
    from importlib.metadata import version, PackageNotFoundError

    # Try to get the version from the installed package
    __version__ = version("t2d-kit")
except PackageNotFoundError:
    # Fallback for development or when package is not installed
    __version__ = "0.1.0"
except Exception:
    # Additional fallback for any other issues
    __version__ = "0.1.0"

# Parse version tuple from version string
def _parse_version_tuple(version_str: str) -> tuple:
    """Parse version string into tuple."""
    # Remove any pre-release or build metadata
    base_version = version_str.split("-")[0].split("+")[0]
    parts = base_version.split(".")
    return tuple(int(part) for part in parts[:3])  # Major, minor, patch only

__version_tuple__ = _parse_version_tuple(__version__)
